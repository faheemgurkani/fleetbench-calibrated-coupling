"""Degradation operators on the monitors' action view (RQ 4.2 tampered logs, RQ 4.3 partial view).

drop(acts, k, seed)        keep each record with probability 1-k (partial observation)
rename(acts, seed)         a fresh random ID per agent (bijection); returns (acts, mapping)
churn(acts, period, seed)  agents take a new ID every `period` ticks (as in the incident: 7,905 names
                           for ~1,200 agents); returns (acts, mapping new_id -> true agent)
spoof(acts, rate, seed)    the agent-side log: ~rate of an agent's disruption records (503/help/alt) are
                           rewritten as a fake successful lookup (cf. ~7% spoofed transcripts, METR 2026)
reconcile(agent_log, witness_log)  compare the agent-side log with the gateway witness log; return the
                           witness record wherever they disagree, and the number of mismatches
"""
from __future__ import annotations

import random

DISRUPTIVE = ("error503", "help", "alt")


def drop(acts: list[dict], k: float, seed: int) -> list[dict]:
    rng = random.Random(seed)
    return [r for r in acts if rng.random() >= k]


def rename(acts: list[dict], seed: int):
    agents = sorted({r["agent"] for r in acts})
    rng = random.Random(seed)
    ids = [f"X{rng.randrange(10**6):06d}" for _ in agents]
    while len(set(ids)) < len(ids):
        ids = [f"X{rng.randrange(10**6):06d}" for _ in agents]
    m = dict(zip(agents, ids))
    return [{**r, "agent": m[r["agent"]]} for r in acts], m


def churn(acts: list[dict], period: int, seed: int):
    rng = random.Random(seed)
    m, out = {}, []
    for r in acts:
        key = (r["agent"], r["tick"] // period)
        if key not in m:
            m[key] = f"X{rng.randrange(10**8):08d}"
        out.append({**r, "agent": m[key]})
    return out, {v: k[0] for k, v in m.items()}


def spoof(acts: list[dict], rate: float, seed: int) -> list[dict]:
    rng = random.Random(seed)
    out = []
    for r in acts:
        if r["kind"] in DISRUPTIVE and rng.random() < rate:
            out.append({"agent": r["agent"], "tick": r["tick"], "kind": "lookup", "spoofed": True})
        else:
            out.append(dict(r))
    return out


def reconcile(agent_log: list[dict], witness_log: list[dict]):
    key = lambda r: (r["agent"], r["tick"])  # noqa: E731  one action per agent per tick
    w = {key(r): r for r in witness_log}
    out, mism = [], 0
    for r in agent_log:
        wr = w.get(key(r))
        if wr is not None and (wr["kind"] != r["kind"] or wr.get("variant") != r.get("variant")):
            mism += 1
            out.append(dict(wr))
        else:
            out.append({k: v for k, v in r.items() if k != "spoofed"})
    return out, mism
