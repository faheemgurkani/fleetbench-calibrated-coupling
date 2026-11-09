"""Tier B: scale the frozen monitors to N = 1,200 agents by resampling Tier A agent trajectories.

A synthetic cohort ("episode") of N agents is built from N real agent trajectories (token arrays over
{error503, help, alt:<endpoint>}) drawn from *different* Tier A episodes of one condition, so marginals
and the shock response match Tier A exactly and no real coupling exists between them (a fleet).
Coupling of strength c is planted on top: a fraction d of agents are leaders whose shared-endpoint
uses are replaced by a private endpoint (drawn per cohort from a pool of 32); n_leaders = max(2, round(0.2 x
min(N, 50))), i.e. a few discoverers as in Tier A, at most 10; each other
agent independently, with probability c, adopts one random leader and uses its endpoint at a lag of
1-3 ticks after each of the leader's uses.

Monitors (same definitions as the frozen src/fleetbench/monitors.py, vectorised over sampled pairs):
  M2  Jaccard of (token, tick) events matched within +-1 tick, threshold from independent calibration
  M3  raw lag statistic, 200 time-shuffle surrogates, p threshold from independent calibration
  M4  weighted lag statistic (IDF over replicate cohorts), null = sampled cross-cohort pseudo-partners
Outputs results/tierb/tierb.json: per (N, c, wave): FPR on unlinked pairs, TPR on adoption pairs,
expected false alerts = FPR x N(N-1)/2.

Usage: .venv/bin/python src/sim/tierb.py --phase main
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT, RUNS  # noqa: E402
from fleetbench.views import load_phase  # noqa: E402

LAGS = (1, 2, 3)
ALPHA = 0.05
N_PRIVATE = 32
SHARED = 2  # token index of the shared endpoint; 0 = error503, 1 = help; private endpoints: 3..3+15


# ------------------------------------------------------------------ trajectory pool from Tier A
def pool_from_phase(phase: str, condition: str) -> np.ndarray:
    """[n_agents, T, 3 + N_PRIVATE] token arrays; any alt use maps to the shared token (index 2)."""
    out = []
    for e in load_phase(RUNS, phase, [condition]):
        x = np.zeros((len(e.agents), e.ticks, 3 + N_PRIVATE), dtype=np.float32)
        ai = {a: i for i, a in enumerate(e.agents)}
        for r in e.actions:
            k = {"error503": 0, "help": 1, "alt": SHARED}.get(r["kind"])
            if k is not None:
                x[ai[r["agent"]], r["tick"], k] = 1
        out.append(x)
    return np.concatenate(out)


def make_cohort(pool: np.ndarray, n: int, c: float, rng, d: float = 0.2):
    """One cohort: n resampled trajectories + planted coupling. Returns X [n,T,K] and adoption edges."""
    idx = rng.choice(len(pool), size=n, replace=len(pool) < n)
    x = pool[idx].copy()
    T = x.shape[1]
    edges = set()
    if c > 0:
        n_lead = max(2, int(round(d * min(n, 50))))
        leaders = rng.choice(n, size=n_lead, replace=False)
        priv = rng.choice(N_PRIVATE, size=n_lead, replace=True) + 3
        for L, k in zip(leaders, priv):
            x[L, :, k] = x[L, :, SHARED]
            x[L, :, SHARED] = 0
        lead_set = set(leaders.tolist())
        for f in range(n):
            if f in lead_set or rng.random() >= c:
                continue
            j = rng.integers(n_lead)
            L, k = leaders[j], priv[j]
            ts = np.nonzero(x[L, :, k])[0]
            lag = rng.integers(1, 4, size=len(ts))
            tt = ts + lag
            tt = tt[tt < T]
            if len(tt):
                x[f, tt, k] = 1
                edges.add((int(L), int(f)))
    return x, edges


def independent_cohort(pool: np.ndarray, n: int, rng) -> np.ndarray:
    """Independent calibration agents: Tier A independent trajectories, each with its own private endpoint."""
    idx = rng.choice(len(pool), size=n, replace=len(pool) < n)
    x = pool[idx].copy()
    for i in range(n):
        k = rng.integers(N_PRIVATE) + 3
        x[i, :, k] = x[i, :, SHARED]
        x[i, :, SHARED] = 0
    return x


# ------------------------------------------------------------------ vectorised statistics on pairs
def lag_s(xa: np.ndarray, xb: np.ndarray, w: np.ndarray | None = None) -> np.ndarray:
    """Directed S(a->b) for aligned arrays of pairs: xa, xb [P, T, K] -> [P]."""
    if w is not None:
        xa = xa * w
    s = np.zeros(xa.shape[0])
    for l in LAGS:
        s += np.einsum("ptk,ptk->p", xa[:, :-l], xb[:, l:])
    return s


def pair_s(xa, xb, w=None):
    return np.maximum(lag_s(xa, xb, w), lag_s(xb, xa, w))


def jaccard_pm1(xa: np.ndarray, xb: np.ndarray) -> np.ndarray:
    """Vectorised M2 for pairs: events (k, t) matched within +-1 tick."""
    def near(x):
        y = x.copy()
        y[:, 1:] = np.maximum(y[:, 1:], x[:, :-1])
        y[:, :-1] = np.maximum(y[:, :-1], x[:, 1:])
        return y
    ma = (xa * near(xb)).sum((1, 2))
    mb = (xb * near(xa)).sum((1, 2))
    na, nb = xa.sum((1, 2)), xb.sum((1, 2))
    den = na + nb - 0.5 * (ma + mb)
    return np.where(den > 0, 0.5 * (ma + mb) / np.maximum(den, 1e-9), 0.0)


def shuffle_p(xa, xb, rng, n_null=200):
    obs = pair_s(xa, xb)
    T = xa.shape[1]
    ge = np.zeros(len(obs))
    eq = np.ones(len(obs))
    for _ in range(n_null):
        perm = rng.permutation(T)
        nb = pair_s(xa, xb[:, perm])
        ge += nb > obs
        eq += nb == obs
    return (ge + rng.random(len(obs)) * eq) / (n_null + 1)


def idf(X_all: np.ndarray) -> np.ndarray:
    m = (X_all.sum(1) > 0).sum(0)
    return np.log((X_all.shape[0] + 1) / (m + 1)).astype(np.float32)


def m4_p(cohorts, ci, ia, ib, w, rng, n_partners=1000):
    """M4 randomized p for pairs (ia[p], ib[p]) of cohort ci, null = sampled agents from other cohorts."""
    others = np.concatenate([c for j, c in enumerate(cohorts) if j != ci])
    x = cohorts[ci]
    obs = pair_s(x[ia], x[ib], w)
    ge = np.zeros(len(obs))
    eq = np.ones(len(obs))
    nn = 0
    for side in (ia, ib):
        part = others[rng.integers(len(others), size=n_partners)]
        for q in range(n_partners):
            xp = np.broadcast_to(part[q], x[side].shape)
            nb = pair_s(x[side], xp, w)
            ge += nb > obs
            eq += nb == obs
            nn += 1
    return (ge + rng.random(len(obs)) * eq) / (nn + 1)


# ------------------------------------------------------------------ sweep
def run(phase: str, Ns, cs, n_rep: int, n_pairs: int, seed: int, waves=(False, True)):
    rng = np.random.default_rng(seed)
    pools = {"fleet": pool_from_phase(phase, "fleet"), "wave": pool_from_phase(phase, "wave"),
             "independent": pool_from_phase(phase, "independent")}
    # calibration on independent agents (as for the Tier A monitors): N = 10 cohorts
    cal = [independent_cohort(pools["independent"], 10, rng) for _ in range(30)]
    ia, ib = np.triu_indices(10, 1)
    cal_m2 = np.concatenate([jaccard_pm1(c[ia], c[ib]) for c in cal])
    cal_p3 = np.concatenate([shuffle_p(c[ia], c[ib], rng) for c in cal])
    thr_m2, thr_m3 = float(np.quantile(cal_m2, 1 - ALPHA)), float(np.quantile(cal_p3, ALPHA))
    res = {"phase": phase, "thr_m2": thr_m2, "thr_m3": thr_m3, "pool_sizes": {k: len(v) for k, v in pools.items()},
           "n_rep": n_rep, "n_pairs_sampled": n_pairs, "rows": []}
    for wave in waves:
        pool = pools["wave" if wave else "fleet"]
        for N in Ns:
            for c in cs:
                cohorts, edges = zip(*[make_cohort(pool, N, c, rng) for _ in range(n_rep)])
                w = idf(np.concatenate(cohorts))
                fl = {"M2": [], "M3": [], "M4": []}
                tp = {"M2": [], "M3": [], "M4": []}
                for ci, (x, ed) in enumerate(zip(cohorts, edges)):
                    # sample unlinked pairs (no adoption edge, no shared leader) + all adoption pairs (capped)
                    lead_of = {f: L for L, f in ed}
                    a = rng.integers(N, size=n_pairs // n_rep * 2)
                    b = rng.integers(N, size=len(a))
                    keep = (a != b)
                    a, b = a[keep], b[keep]
                    linked = np.array([(x_, y_) in ed or (y_, x_) in ed or
                                       (x_ in lead_of and (lead_of.get(y_) == lead_of[x_] or y_ == lead_of[x_])) or
                                       (y_ in lead_of and x_ == lead_of[y_]) for x_, y_ in zip(a.tolist(), b.tolist())], dtype=bool)
                    a, b = a[~linked][: max(1, n_pairs // n_rep)], b[~linked][: max(1, n_pairs // n_rep)]
                    pos = list(ed)[:200]
                    for tag, (pa, pb) in (("neg", (a, b)),
                                          ("pos", (np.array([p[0] for p in pos], dtype=int), np.array([p[1] for p in pos], dtype=int)))):
                        if len(pa) == 0:
                            continue
                        f2 = jaccard_pm1(x[pa], x[pb]) > thr_m2
                        f3 = shuffle_p(x[pa], x[pb], rng, n_null=100) <= thr_m3
                        f4 = m4_p(list(cohorts), ci, pa, pb, w, rng, n_partners=200) <= ALPHA
                        dst = fl if tag == "neg" else tp
                        dst["M2"] += f2.tolist()
                        dst["M3"] += f3.tolist()
                        dst["M4"] += f4.tolist()
                n_all = N * (N - 1) / 2
                row = {"wave": wave, "N": N, "c": c, "n_adopt_pairs": int(sum(len(e) for e in edges))}
                for m in fl:
                    f = float(np.mean(fl[m])) if fl[m] else float("nan")
                    row[m] = {"fpr": f, "n_neg": len(fl[m]), "expected_false_alerts": f * n_all,
                              "tpr": float(np.mean(tp[m])) if tp[m] else float("nan"), "n_pos": len(tp[m])}
                res["rows"].append(row)
                print(json.dumps({k: (v if not isinstance(v, dict) else {kk: round(vv, 3) if isinstance(vv, float) else vv
                                                                         for kk, vv in v.items() if kk in ("fpr", "tpr")})
                                  for k, v in row.items()}), flush=True)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="main")
    ap.add_argument("--Ns", nargs="+", type=int, default=[10, 30, 100, 300, 1200])
    ap.add_argument("--cs", nargs="+", type=float, default=[0.0, 0.05, 0.1, 0.2, 0.4])
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--pairs", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20261108)
    ap.add_argument("--out", default="tierb")
    a = ap.parse_args()
    r = run(a.phase, a.Ns, a.cs, a.reps, a.pairs, a.seed)
    od = ROOT / "results" / a.out
    od.mkdir(parents=True, exist_ok=True)
    json.dump(r, open(od / "tierb.json", "w"), indent=1)
