import numpy as np

from fleetbench import monitors as M
from sim import tierb as B
from synth import synth_episode


def test_zero_coupling_no_edges_and_resampling_preserves_marginals():
    rng = np.random.default_rng(0)
    pool = rng.random((200, 20, 3 + B.N_PRIVATE)) < 0.05
    pool = pool.astype(np.float32)
    pool[:, :, 3:] = 0
    x, e = B.make_cohort(pool, 50, 0.0, rng)
    assert e == set()
    assert abs(x.mean() - pool.mean()) < 0.01


def test_vectorised_stat_matches_frozen_monitor():
    ep = synth_episode("t/ep0", seed=3, shock=(4, 12))
    vocab = M.vocab_for([ep.actions])
    from fleetbench.views import token_array
    x = token_array(ep.actions, ep.agents, ep.ticks, vocab)
    s = M.lag_matrix(x, x)
    ia, ib = np.triu_indices(len(ep.agents), 1)
    v = B.pair_s(x[ia], x[ib])
    assert np.allclose(v, np.maximum(s, s.T)[ia, ib])
    rows = M.m2_scores(ep, ep.actions)
    j = B.jaccard_pm1(x[ia], x[ib])
    assert np.allclose(j, [r["score"] for r in rows], atol=1e-6)


def test_planted_coupling_creates_edges():
    rng = np.random.default_rng(1)
    pool = np.zeros((100, 20, 3 + B.N_PRIVATE), dtype=np.float32)
    pool[:, 6:12, B.SHARED] = 1
    x, e = B.make_cohort(pool, 30, 1.0, rng)
    assert len(e) == 30 - len({L for L, _ in e})
