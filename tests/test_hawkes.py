import numpy as np

from analysis.wiki_hawkes import fit_hawkes, sim_hawkes


def test_recovers_branching_ratio():
    rng = np.random.default_rng(0)
    for eta in (0.0, 0.5):
        t = sim_hawkes(mu=2.0, eta=eta, beta=6.0, T=500.0, rng=rng)
        f = fit_hawkes(t, None, T=500.0)
        assert abs(f["eta"] - eta) <= 0.1, (eta, f)
