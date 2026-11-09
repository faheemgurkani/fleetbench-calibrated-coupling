import math

from fleetbench.degrade import churn, drop, reconcile, rename, spoof
from fleetbench.metrics import cluster_bootstrap, hoeffding_n, wilson
from synth import synth_episode


def acts():
    return synth_episode("d/ep0", n=20, T=40, p=0.5, seed=1).actions


def test_drop_fraction():
    a = acts()
    for k in (0.2, 0.5, 0.8):
        kept = len(drop(a, k, seed=3)) / len(a)
        assert abs(kept - (1 - k)) < 0.05


def test_rename_bijection_and_churn():
    a = acts()
    r, m = rename(a, seed=2)
    assert len(set(m.values())) == len(m) and len(r) == len(a)
    c, back = churn(a, period=5, seed=2)
    assert all(back[x["agent"]] == y["agent"] for x, y in zip(c, a))
    assert len(back) > len(m)


def test_spoof_rate_and_reconcile():
    a = acts()
    s = spoof(a, rate=0.07, seed=5)
    dis = [r for r in a if r["kind"] in ("error503", "help", "alt")]
    frac = sum(1 for r in s if r.get("spoofed")) / len(dis)
    assert abs(frac - 0.07) < 0.02
    fixed, mism = reconcile(s, a)
    assert fixed == a and mism == sum(1 for r in s if r.get("spoofed"))


def test_metrics():
    lo, hi = wilson(5, 100)
    assert math.isclose(lo, 0.02154, abs_tol=1e-4) and math.isclose(hi, 0.11175, abs_tol=1e-4)
    assert hoeffding_n(0.1, 0.05) == 185
    rows = [{"ep": i // 10, "flag": (i % 7 == 0)} for i in range(200)]
    assert cluster_bootstrap(rows, seed=4) == cluster_bootstrap(rows, seed=4)
