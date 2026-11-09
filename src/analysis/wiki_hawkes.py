"""H4: how much of Lütje's Hawkes "contagion" bound on collusion.wiki can start waves explain?

Arrivals = the first revision of each previously unseen name (labels.jsonl `first_write`, empty label
excluded), as in Lütje (2026, §4.8, "names"). Model: Hawkes process with exponential kernel
alpha * beta * exp(-beta * dt) (branching ratio eta = alpha) and a piecewise-constant baseline on
blocks of width w, fitted by EM (branching-structure EM; Veen & Schoenberg 2008).

The fleet-calibrated move: shrink the baseline block width w from 6 h (Lütje's choice) toward the
start-wave timescale (~10 min). Waves are absorbed by a finer baseline; contagion at a longer reaction
time is not. Because waves and contagion at the same timescale are not identifiable from arrivals
alone (Shalizi & Thomas 2011), the curve eta(w) is calibrated on simulated processes with known truth:
  (a) pure start waves: Poisson arrivals of wave events, each releasing a burst of k containers within
      10 minutes, zero contagion;  (b) pure contagion: Hawkes with eta = 0.5, reaction time 10 min.
Everything is reported as a bound, never as proof. No request log (third-party IPs) is used.

Usage: .venv/bin/python src/analysis/wiki_hawkes.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT  # noqa: E402

WIKI = ROOT / "starter/swarm_alignment/datasets/collusion-wiki"
BLOCKS_H = (24.0, 6.0, 3.0, 1.0, 0.5, 1 / 6)  # baseline block widths in hours


def name_arrivals() -> np.ndarray:
    ts = []
    for l in open(WIKI / "labels.jsonl"):
        d = json.loads(l)
        if d.get("label") and d.get("first_write"):
            ts.append(datetime.fromisoformat(d["first_write"].replace("Z", "+00:00")).timestamp())
    t = np.sort(np.array(ts)) / 3600.0  # hours
    return t - t[0]


def fit_hawkes(t: np.ndarray, block_h: float | None, T: float | None = None, n_iter: int = 300,
               beta0: float = 6.0, window_h: float = 6.0) -> dict:
    """EM for an exponential-kernel Hawkes process with piecewise-constant baseline (block_h; None = constant).
    Kernel phi(dt) = eta * beta * exp(-beta dt); returns eta, beta (1/h), reaction time 1/beta, loglik."""
    t = np.asarray(t, dtype=float)
    n = len(t)
    T = float(T if T is not None else t[-1] + 1e-6)
    edges = np.arange(0, T + (block_h or T), block_h or T)
    if edges[-1] < T:
        edges = np.append(edges, T)
    blk = np.clip(np.searchsorted(edges, t, side="right") - 1, 0, len(edges) - 2)
    blen = np.diff(edges)
    blen[-1] = T - edges[-2]
    # candidate parent pairs within a window (kernel negligible beyond)
    I, J = [], []
    lo = 0
    for i in range(n):
        while t[i] - t[lo] > window_h:
            lo += 1
        for j in range(lo, i):
            I.append(i)
            J.append(j)
    I, J = np.array(I, dtype=int), np.array(J, dtype=int)
    dt = t[I] - t[J] if len(I) else np.zeros(0)
    mu = np.bincount(blk, minlength=len(blen)) / blen * 0.5
    eta, beta = 0.5, beta0
    for _ in range(n_iter):
        trig = eta * beta * np.exp(-beta * dt)
        base = mu[blk]
        tot = base.copy()
        np.add.at(tot, I, trig)
        p_trig = trig / tot[I]
        p_base = base / tot
        mu = np.bincount(blk, weights=p_base, minlength=len(blen)) / blen
        s_trig = p_trig.sum()
        comp = (1 - np.exp(-beta * (T - t))).sum()
        eta = s_trig / max(comp, 1e-9)
        beta = s_trig / max((p_trig * dt).sum(), 1e-9)
    trig = eta * beta * np.exp(-beta * dt)
    lam = mu[blk].copy()
    np.add.at(lam, I, trig)
    ll = float(np.log(lam).sum() - (mu * blen).sum() - eta * (1 - np.exp(-beta * (T - t))).sum())
    return {"eta": float(eta), "beta_per_h": float(beta), "reaction_min": float(60 / beta), "loglik": ll,
            "n": int(n), "blocks": int(len(blen)), "block_h": block_h}


def sim_hawkes(mu: float, eta: float, beta: float, T: float, rng) -> np.ndarray:
    """Simulate by branching: immigrants ~ Poisson(mu T), each event has Poisson(eta) children at Exp(beta) delays."""
    gen = list(rng.uniform(0, T, rng.poisson(mu * T)))
    out = []
    while gen:
        out += gen
        kids = []
        for s in gen:
            for _ in range(rng.poisson(eta)):
                c = s + rng.exponential(1 / beta)
                if c < T:
                    kids.append(c)
        gen = kids
    return np.sort(np.array(out))


def sim_waves(rate_waves: float, burst_mean: float, burst_span_h: float, T: float, rng,
              day_profile: bool = True) -> np.ndarray:
    """Pure start waves: wave times ~ (optionally diurnally modulated) Poisson; each releases
    1 + Poisson(burst_mean - 1) containers uniformly within burst_span_h. Zero contagion."""
    n_w = rng.poisson(rate_waves * T)
    w = rng.uniform(0, T, n_w)
    if day_profile:  # thin to a daytime-heavy profile, as schedules usually are
        keep = rng.random(n_w) < 0.5 * (1 + np.sin(2 * np.pi * w / 24.0))
        w = w[keep]
    ev = [wi + rng.uniform(0, burst_span_h, 1 + rng.poisson(burst_mean - 1)) for wi in w]
    return np.sort(np.concatenate(ev)) if ev else np.zeros(0)


def main():
    rng = np.random.default_rng(20261108)
    t = name_arrivals()
    T = float(t[-1] + 1e-6)
    res = {"n_arrivals": int(len(t)), "span_days": T / 24, "wiki": [], "sim_waves": [], "sim_contagion": []}
    res["wiki"].append(fit_hawkes(t, None))
    for b in BLOCKS_H:
        res["wiki"].append(fit_hawkes(t, b))
    # calibration processes matched to the wiki's size: ~n arrivals over the same span
    n = len(t)
    waves = sim_waves(rate_waves=n / T / 5.0 * 2, burst_mean=5.0, burst_span_h=1 / 6, T=T, rng=rng)
    cont = sim_hawkes(mu=n / T * 0.5, eta=0.5, beta=6.0, T=T, rng=rng)
    res["sim_waves_n"], res["sim_contagion_n"] = int(len(waves)), int(len(cont))
    for nm, s in (("sim_waves", waves), ("sim_contagion", cont)):
        res[nm].append(fit_hawkes(s, None))
        for b in BLOCKS_H:
            res[nm].append(fit_hawkes(s, b))
    od = ROOT / "results" / "wiki"
    od.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(od / "hawkes.json", "w"), indent=1)
    for k in ("wiki", "sim_waves", "sim_contagion"):
        print(k, [(r["block_h"], round(r["eta"], 3), round(r["reaction_min"], 1)) for r in res[k]])


if __name__ == "__main__":
    main()
