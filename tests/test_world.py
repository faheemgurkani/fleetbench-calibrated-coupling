"""World unit tests (no LLM calls)."""
import json

import pytest

from sandbox.world import CONDITIONS, VARIANTS, World


def mk(cond, n=10, ticks=20, seed=7):
    return World(cond, n, ticks, seed=seed)


def help_text(w, aid, tick=5):
    out, ev = w.execute(aid, tick, "api_call", {"path": "/help"})
    assert ev["kind"] == "help"
    return json.loads(out)["help"]


def test_outage_window_boundaries():
    w = mk("fleet")
    a = "A1"
    s = w.outage_start[a]
    kinds = {t: w.execute(a, t, "api_call", {"path": "/v1/lookup?name=x"})[1]["kind"] for t in range(s - 1, s + w.outage_len + 1)}
    assert kinds[s - 1] == "lookup" and kinds[s] == "error503"
    assert kinds[s + w.outage_len - 1] == "error503" and kinds[s + w.outage_len] == "lookup"


def test_help_policies():
    ind, fl, wv, sw, tc = mk("independent"), mk("fleet"), mk("wave"), mk("swarm"), mk("tacit")
    # independent: every agent gets its own, distinct variant
    revs = [ind.help_reveals(a) for a in ind.queues]
    assert all(len(r) == 1 for r in revs) and len({r[0] for r in revs}) == len(revs)
    # fleet and wave: one shared variant for all
    for w in (fl, wv):
        assert len({tuple(w.help_reveals(a)) for a in w.queues}) == 1
        assert all(len(w.help_reveals(a)) == 1 for a in w.queues)
    # swarm: only the 2 discoverers learn a variant
    for a in sw.queues:
        assert (len(sw.help_reveals(a)) == 1) == (a in sw.discoverers)
    assert "No alternative" in help_text(sw, next(a for a in sw.queues if a not in sw.discoverers))
    # tacit: same menu of 4, different order per agent
    menus = [tc.help_reveals(a) for a in tc.queues]
    assert all(len(m) == 4 for m in menus) and len({frozenset(m) for m in menus}) == 1
    assert len({tuple(m) for m in menus}) > 1


def test_wave_starts_and_shared_shock():
    w = mk("wave")
    assert [w.start_tick[f"A{i + 1}"] for i in range(10)] == [i // 2 for i in range(10)]
    assert len(set(w.outage_start.values())) == 1
    f = mk("fleet")
    assert set(f.start_tick.values()) == {0}


def test_alt_use_marks_own_and_foreign():
    sw = mk("swarm")
    d, nd = sw.discoverers[0], next(a for a in sw.queues if a not in sw.discoverers)
    v = sw.variant[d]
    _, ev = sw.execute(d, 5, "api_call", {"path": v + "x"})
    assert ev["kind"] == "alt" and ev["own_variant"]
    _, ev = sw.execute(nd, 6, "api_call", {"path": v + "x"})
    assert ev["kind"] == "alt" and not ev["own_variant"] and ev["variant_owner"] == [d]
    fl = mk("fleet")
    _, ev = fl.execute("A3", 5, "api_call", {"path": fl.help_reveals("A3")[0] + "x"})
    assert ev["own_variant"]
    tc = mk("tacit")
    _, ev = tc.execute("A2", 5, "api_call", {"path": tc.help_reveals("A2")[3] + "x"})
    assert ev["own_variant"]


def test_board_visible_next_tick_and_notes_read():
    sw = mk("swarm")
    v = sw.variant[sw.discoverers[0]].split("?")[0]
    sw.execute("A1", 5, "write_note", {"text": f"use {v}?name=..."})
    _, ev = sw.execute("A2", 5, "read_board", {})
    assert ev["notes_read"] == []
    _, ev = sw.execute("A2", 6, "read_board", {})
    assert ev["notes_read"][0]["author"] == "A1" and ev["notes_read"][0]["variants"] == [v]


def test_no_board_without_channel():
    for c in ("independent", "fleet", "wave", "tacit"):
        w = mk(c)
        assert not w.has_board and {t["function"]["name"] for t in w.tools()} == {"get_next_task", "api_call", "submit_answer"}
        assert w.execute("A1", 5, "read_board", {})[1]["kind"] == "invalid"


def test_variants_unguessable():
    for v in VARIANTS:
        assert not v.startswith("/v1") and not v.startswith("/help")
    _, ev = mk("fleet").execute("A1", 5, "api_call", {"path": "/v2/lookup?name=x"})
    assert ev["kind"] == "bad_path"


@pytest.mark.parametrize("cond", CONDITIONS)
def test_same_seed_same_world(cond):
    a, b = mk(cond, seed=3), mk(cond, seed=3)
    for k in ("queues", "outage_start", "start_tick", "variant", "discoverers", "menu"):
        assert getattr(a, k) == getattr(b, k)
    assert mk(cond, seed=4).places != a.places


def test_deployment_constants_fixed_across_episodes():
    from sandbox.world import SHARED_VARIANT, TACIT_MENU
    for s in (1, 2, 3):
        assert set(mk("fleet", seed=s).variant.values()) == {SHARED_VARIANT}
        assert set(mk("tacit", seed=s).help_reveals("A1")) == set(TACIT_MENU)
        sw = mk("swarm", seed=s)
        assert SHARED_VARIANT not in sw.variant.values() and not set(TACIT_MENU) & set(sw.variant.values())
    # private variants differ across episodes
    assert mk("swarm", seed=1).variant != mk("swarm", seed=2).variant


def test_fleet_drift_varies_shared_variant():
    a, b = mk("fleet_drift", seed=1), mk("fleet_drift", seed=2)
    assert len(set(a.variant.values())) == 1 and set(a.variant.values()) != set(b.variant.values())
    assert a.help_reveals("A1") == a.help_reveals("A7") and not a.has_board
