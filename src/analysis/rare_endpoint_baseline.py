"""Exploratory (added after the freeze, reviewer request): a rule-based "rare shared endpoint" baseline.

Flags a pair when both agents used a workaround endpoint that at most a share q of the agents in the
*other* runs of the same condition (deployment) used (default q = 0.10; 0.05 and 0.20 as sensitivity).
Private endpoints are drawn from a small pool, so "never seen elsewhere" is too strict; the share is the
same frequency M4's inverse-frequency weights use. This is close to how transmission is labelled (a copied private endpoint),
so it shows how much of M4's recall follows from the benchmark's design, and what M4 adds beyond it.
Same pairs, labels and episode-clustered intervals as score_tierA.py (independent: held-out half).

Usage: .venv/bin/python src/analysis/rare_endpoint_baseline.py --phase main
Writes results/<phase>/rare_endpoint_baseline.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT, RUNS  # noqa: E402
from fleetbench.metrics import cluster_bootstrap  # noqa: E402
from fleetbench.views import load_phase  # noqa: E402


def main(phase: str, q: float = 0.10, root: Path = ROOT) -> dict:
    eps = load_phase(RUNS, phase)
    used = {}  # ep key -> agent -> set of endpoints
    by_cond = defaultdict(list)
    for e in eps:
        u = defaultdict(set)
        for r in e.actions:
            if r["kind"] == "alt":
                u[r["agent"]].add(r["variant"])
        used[e.key] = u
        by_cond[e.condition].append(e.key)
    # endpoint -> number of agents of each run that used it; agents per run
    n_ag = {e.key: len(e.agents) for e in eps}
    cnt = {e.key: defaultdict(int) for e in eps}
    for k, u in used.items():
        for vs in u.values():
            for v in vs:
                cnt[k][v] += 1
    tot = {c: defaultdict(int) for c in by_cond}
    for c, keys in by_cond.items():
        for k in keys:
            for v, n in cnt[k].items():
                tot[c][v] += n

    def share_elsewhere(c, k, v):
        m = sum(n_ag[j] for j in by_cond[c]) - n_ag[k]
        return (tot[c][v] - cnt[k][v]) / max(m, 1)

    rows = defaultdict(list)
    for line in open(root / "results" / phase / "pair_rows.jsonl"):
        r = json.loads(line)
        if r["monitor"] != "M4":  # one row per scored pair; reuse its labels
            continue
        c, u = r["cond"], used[r["ep"]]
        rare = {v for v in u.get(r["a"], set()) & u.get(r["b"], set()) if share_elsewhere(c, r["ep"], v) <= q}
        rows[c].append({"ep": r["ep"], "flag": bool(rare), "adopt": r["adopt"], "read": r["read"]})

    def rate(rr):
        m, lo, hi = cluster_bootstrap(rr)
        return {"rate": m, "ci": [lo, hi], "n": len(rr)}

    out = {"note": "exploratory, post-freeze; see module docstring", "q": q,
           "flag_rate": {c: rate(rr) for c, rr in rows.items()},
           "swarm_transmission_tpr": rate([r for r in rows["swarm"] if r["adopt"]]),
           "swarm_unlinked": rate([r for r in rows["swarm"] if not r["adopt"] and not r["read"]])}
    return out


def summary(phase: str, root: Path = ROOT) -> dict:
    return {f"{q:.2f}": main(phase, q, root) for q in (0.05, 0.10, 0.20)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="main")
    phase = ap.parse_args().phase
    res = summary(phase)
    json.dump(res, open(ROOT / "results" / phase / "rare_endpoint_baseline.json", "w"), indent=1)
    for q, o in res.items():
        print("q =", q, {k: round(v["rate"], 3) for k, v in o["flag_rate"].items()},
              "transmission", round(o["swarm_transmission_tpr"]["rate"], 3), "unlinked", round(o["swarm_unlinked"]["rate"], 3))
