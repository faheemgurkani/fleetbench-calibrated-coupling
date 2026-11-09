"""Rates, intervals and resampling for FleetBench scores."""
from __future__ import annotations

import math

import numpy as np


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def hoeffding_n(eps: float, delta: float) -> int:
    """Samples so that |p_hat - p| <= eps with probability >= 1 - delta (two-sided)."""
    return math.ceil(math.log(2 / delta) / (2 * eps * eps))


def rate(rows: list[dict], key: str = "flag") -> float:
    return float(np.mean([bool(r[key]) for r in rows])) if rows else float("nan")


def cluster_bootstrap(rows: list[dict], key: str = "flag", n_boot: int = 2000, seed: int = 0,
                      cluster: str = "ep") -> tuple[float, float, float]:
    """Mean of rows[key] with a 95% percentile CI, resampling whole episodes (clusters)."""
    if not rows:
        return (float("nan"),) * 3
    groups = {}
    for r in rows:
        groups.setdefault(r[cluster], []).append(float(bool(r[key])) if isinstance(r[key], (bool, np.bool_)) else float(r[key]))
    sums = np.array([sum(v) for v in groups.values()])
    cnts = np.array([len(v) for v in groups.values()])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(sums), size=(n_boot, len(sums)))
    boots = sums[idx].sum(1) / cnts[idx].sum(1)
    return (float(sums.sum() / cnts.sum()), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5)))


def edge_pr(pred: set, truth: set) -> tuple[float, float]:
    tp = len(pred & truth)
    prec = tp / len(pred) if pred else float("nan")
    rec = tp / len(truth) if truth else float("nan")
    return prec, rec


def threshold_at_fpr(neg_scores, target: float = 0.05) -> float:
    """Smallest threshold t with mean(neg > t) <= target."""
    s = np.sort(np.asarray(neg_scores, dtype=float))
    return float(np.quantile(s, 1 - target)) if len(s) else float("inf")
