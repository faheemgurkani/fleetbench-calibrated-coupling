"""Run FleetBench episodes: N agents act once per tick, in parallel, against one World.

Writes data/runs/<phase>/<condition>/ep<k>/ with
  events.jsonl       witness log (harness-side; ground truth)
  transcripts.json   each agent's own conversation (what an agent-side log would show)
  meta.json          condition, seeds, outage schedule, variants, model route

Usage: .venv/bin/python src/sandbox/run_episode.py --phase pilot --conditions fleet swarm --episodes 2 --n 6 --ticks 14
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import RUNS, MODELS, chat, seed_for, spent_usd  # noqa: E402
from sandbox.world import World  # noqa: E402


def agent_turn(world: World, aid: str, tick: int, hist: list[dict], route: str, ep_key: str):
    msgs = [{"role": "system", "content": world.system_prompt(aid)}] + hist
    m = chat(route, msgs, purpose="agent", meta={"ep": ep_key, "agent": aid, "tick": tick},
             seed=seed_for(ep_key, aid, tick), tools=world.tools(), temperature=1.0, max_tokens=1200)
    return m


def run(phase: str, condition: str, ep: int, n: int, ticks: int, route: str, base_seed: int):
    ep_key = f"{phase}/{condition}/ep{ep}"
    out = RUNS / phase / condition / f"ep{ep}"
    if (out / "meta.json").exists():
        print("skip (done)", ep_key)
        return
    world = World(condition, n, ticks, seed=seed_for(base_seed, condition, ep))
    agents = [f"A{i + 1}" for i in range(n)]
    hist = {a: [{"role": "user", "content": f"[tick 0] Start. Your queue has {len(world.queues[a])} tasks."}] for a in agents}
    for tick in range(ticks):
        active = [a for a in agents if tick >= world.start_tick[a]]
        with ThreadPoolExecutor(max_workers=n) as ex:
            futs = {a: ex.submit(agent_turn, world, a, tick, hist[a], route, ep_key) for a in active}
            replies = {}
            for a, f in futs.items():
                try:
                    replies[a] = f.result()
                except Exception as e:  # noqa: BLE001  a failed turn is logged, the episode goes on
                    if type(e).__name__ == "BudgetExceeded":
                        raise
                    replies[a] = None
                    world.events.append({"tick": tick, "agent": a, "tool": None, "kind": "agent_error",
                                         "text": str(e)[:300]})
        # Execute in a seeded random order; board writes only become visible next tick anyway.
        order = sorted(active, key=lambda a: seed_for(ep_key, "order", tick, a))
        for a in order:
            m = replies[a]
            if m is None:
                hist[a].append({"role": "user", "content": f"[tick {tick + 1}] Continue. Use one tool call."})
                continue
            entry = {"role": "assistant", "content": m.content or ""}
            if m.tool_calls:
                tc = m.tool_calls[0]  # one action per tick; extra calls are ignored and logged
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {"_raw": tc.function.arguments}
                res, ev = world.execute(a, tick, tc.function.name, args if isinstance(args, dict) else {})
                ev["n_tool_calls"] = len(m.tool_calls)
                # Echo sanitised JSON arguments: raw malformed arguments made the provider reject the history.
                entry["tool_calls"] = [{"id": tc.id, "type": "function",
                                        "function": {"name": tc.function.name, "arguments": json.dumps(args if isinstance(args, dict) else {})}}]
                hist[a].append(entry)
                hist[a].append({"role": "tool", "tool_call_id": tc.id, "content": res})
                hist[a].append({"role": "user", "content": f"[tick {tick + 1}] Continue."})
            else:
                world.events.append({"tick": tick, "agent": a, "tool": None, "kind": "no_action",
                                     "text": (m.content or "")[:500]})
                hist[a].append(entry)
                hist[a].append({"role": "user", "content": f"[tick {tick + 1}] Continue. Use one tool call."})
        print(f"{ep_key} tick {tick} done; spent ${spent_usd():.4f}", flush=True)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "events.jsonl", "w") as f:
        for e in world.events:
            f.write(json.dumps(e) + "\n")
    json.dump(hist, open(out / "transcripts.json", "w"), indent=1)
    json.dump({"condition": condition, "episode": ep, "n": n, "ticks": ticks, "route": route,
               "model": MODELS[route]["model"], "provider": MODELS[route]["provider"],
               "world_seed": world.seed, "outage_len": world.outage_len, "discoverers": world.discoverers, "start_tick": world.start_tick, "outage_start": world.outage_start, "variant": world.variant, "menu": world.menu, "shock_tick": world.shock_tick,
               "queues": world.queues, "notes": world.notes}, open(out / "meta.json", "w"), indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="pilot")
    ap.add_argument("--conditions", nargs="+", default=["independent", "fleet", "swarm"])
    ap.add_argument("--episodes", type=int, default=2)
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--ticks", type=int, default=20)
    ap.add_argument("--route", default="gptoss120")
    ap.add_argument("--seed", type=int, default=20261107)
    ap.add_argument("--parallel", type=int, default=2, help="episodes run concurrently")
    a = ap.parse_args()
    jobs = [(c, e) for e in range(a.episodes) for c in a.conditions]
    with ThreadPoolExecutor(max_workers=a.parallel) as ex:
        for f in [ex.submit(run, a.phase, c, e, a.n, a.ticks, a.route, a.seed) for c, e in jobs]:
            f.result()
    print("total spent $", round(spent_usd(), 4))
