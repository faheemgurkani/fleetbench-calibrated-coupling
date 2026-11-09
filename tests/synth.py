"""Synthetic episodes with known ground truth (no LLM)."""
import numpy as np

from fleetbench.views import Episode


def synth_episode(key, n=10, T=20, p=0.08, shock=None, shock_p=0.5, couple=None, seed=0, variants=None):
    """Each agent emits error503/help/alt tokens as Bernoulli events.
    shock=(lo, hi): shared window where every agent's rate rises to shock_p (a common cause, same ticks in
    every episode). couple=[(leader, follower, lag, prob)]: follower copies leader's alt events after `lag`.
    variants: per-agent alt endpoint (default: one shared endpoint for all, a deployment constant)."""
    rng = np.random.default_rng(seed)
    agents = [f"A{i + 1}" for i in range(n)]
    variants = variants or {a: "/svc-ibis/lookup?name=" for a in agents}
    ev = []
    for a in agents:
        for t in range(T):
            pt = shock_p if shock and shock[0] <= t < shock[1] else p
            if rng.random() < pt:
                kind = rng.choice(["error503", "help", "alt"])
                e = {"tick": t, "agent": a, "kind": str(kind)}
                if kind == "alt":
                    e["variant"] = variants[a]
                ev.append(e)
    for lead, fol, lag, prob in couple or []:
        for e in [e for e in ev if e["agent"] == lead and e["kind"] == "alt"]:
            if e["tick"] + lag < T and rng.random() < prob:
                ev.append({"tick": e["tick"] + lag, "agent": fol, "kind": "alt", "variant": e["variant"]})
    meta = {"condition": "synthetic", "episode": seed, "ticks": T, "variant": variants}
    return Episode(key=key, condition="synthetic", agents=agents, ticks=T, events=ev, meta=meta)
