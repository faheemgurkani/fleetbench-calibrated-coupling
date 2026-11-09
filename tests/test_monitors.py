"""Calibration of M2-M4 on synthetic data with known ground truth."""
import numpy as np

from fleetbench import monitors as M
from fleetbench.degrade import rename
from synth import synth_episode


def batch(n_eps, seed0, **kw):
    return [synth_episode(f"s/ep{seed0 + k}", seed=seed0 + k, **kw) for k in range(n_eps)]


def fpr(rows):
    return float(np.mean([r["flag"] for r in rows]))


def test_independent_bernoulli_nominal():
    # 12 episodes x 45 pairs = 540 pairs
    eps = batch(12, 100)
    views = [e.actions for e in eps]
    vocab = M.vocab_for(views)
    m4 = M.m4_pseudo_pairs(eps, views, vocab)
    w = M.deployment_weights(eps, views, vocab)
    m3 = [r for e, v in zip(eps, views) for r in M.m3_coupling(e, v, vocab, w)]
    calib = batch(12, 500)
    thr = M.m2_threshold([r for e in calib for r in M.m2_scores(e, e.actions)])
    m2 = M.m2_flag([r for e, v in zip(eps, views) for r in M.m2_scores(e, v)], thr)
    for name, rows in (("M2", m2), ("M3", m3), ("M4", m4)):
        assert 0.0 <= fpr(rows) <= 0.08, (name, fpr(rows))
    assert 0.02 <= fpr(m4) <= 0.08


def test_shared_shock_trap_and_fix():
    eps = batch(12, 200, shock=(4, 12))
    views = [e.actions for e in eps]
    vocab = M.vocab_for(views)
    m4 = M.m4_pseudo_pairs(eps, views, vocab)
    w = M.deployment_weights(eps, views, vocab)
    m3 = [r for e, v in zip(eps, views) for r in M.m3_coupling(e, v, vocab, w)]
    calib = batch(12, 600)  # independent calibration, as practice does
    thr = M.m2_threshold([r for e in calib for r in M.m2_scores(e, e.actions)])
    m2 = M.m2_flag([r for e, v in zip(eps, views) for r in M.m2_scores(e, v)], thr)
    print(f"shared shock FPR: M2 {fpr(m2):.3f}  M3 {fpr(m3):.3f}  M4 {fpr(m4):.3f}")
    assert 0.02 <= fpr(m4) <= 0.08
    assert fpr(m3) > 0.10 and fpr(m2) > 0.10  # the trap exists in this synthetic world (report-only bar: 2x nominal)


def test_planted_lag2_coupling_detected():
    eps = []
    for k in range(12):
        rng = np.random.default_rng(k)
        birds = rng.permutation(["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"])
        variants = {f"A{i + 1}": f"/svc-{birds[i]}/lookup?name=" for i in range(10)}
        eps.append(synth_episode(f"c/ep{k}", seed=300 + k, shock=(4, 12), variants=variants, p=0.05,
                                 couple=[("A1", "A2", 2, 0.9), ("A3", "A4", 1, 0.9), ("A5", "A6", 3, 0.9)]))
    views = [e.actions for e in eps]
    rows = M.m4_pseudo_pairs(eps, views)
    planted = {("A1", "A2"), ("A3", "A4"), ("A5", "A6")}
    # label by observed transmission: the follower actually emitted >= 2 events with the leader's endpoint
    def copied(e, lead, fol):
        v = e.meta["variant"][lead]
        return sum(1 for x in e.events if x["agent"] == fol and x["kind"] == "alt" and x["variant"] == v)
    by_ep = {e.key: e for e in eps}
    pos = [r for r in rows if (r["a"], r["b"]) in planted and copied(by_ep[r["ep"]], r["a"], r["b"]) >= 2]
    neg = [r for r in rows if (r["a"], r["b"]) not in planted]
    tpr = fpr(pos)
    print(f"planted coupling: M4 TPR {tpr:.2f}, FPR on other pairs {fpr(neg):.3f}")
    assert tpr > 0.8


def test_rename_invariance():
    eps = batch(6, 700, shock=(4, 12))
    views = [e.actions for e in eps]
    base = M.m4_pseudo_pairs(eps, views)
    renamed = []
    for e, v in zip(eps, views):
        rv, mp = rename(v, seed=1)
        inv = {b: a for a, b in mp.items()}
        e2 = type(e)(key=e.key, condition=e.condition, agents=[mp[a] for a in e.agents], ticks=e.ticks, events=[], meta=e.meta)
        renamed.append((e2, rv, inv))
    rows = M.m4_pseudo_pairs([r[0] for r in renamed], [r[1] for r in renamed])
    inv_all = {}
    for _, _, inv in renamed:
        inv_all.update(inv)
    a = {(r["ep"], r["a"], r["b"]): (r["score"], r["flag"]) for r in base}
    b = {(r["ep"], *sorted((inv_all[r["a"]], inv_all[r["b"]]), key=lambda s: int(s[1:]))): (r["score"], r["flag"]) for r in rows}
    assert a == b
