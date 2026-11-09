"""Figures and the report-number table from results/<phase>/, results/tierb/ and results/wiki/.

Usage: .venv/bin/python src/analysis/figures.py --phase main
Writes results/<phase>/figures/*.pdf|png and results/<phase>/report_numbers.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT  # noqa: E402

NAMES = {"M0": "M0 keyword", "M1": "M1 LLM judge", "M2": "M2 co-action", "M2b": "M2b lockstep",
         "M3": "M3 lag coupling", "M4": "M4 (ours)", "M4j": "M4j jitter", "M3w": "M3w", "M4r": "M4r"}
COND = {"independent": "independent (held-out half)", "fleet": "fleet", "wave": "fleet, staggered starts",
        "fleet_drift": "fleet, docs change every run"}
# one colour per monitor across all figures; M4 is the only blue
MCOL = {"M2": "#c0392b", "M3": "#e08a1e", "M4": "#1f6fb2"}
CCOL = {"independent": "#b8bec6", "fleet": "#c0392b", "wave": "#e08a1e", "fleet_drift": "#7d5ba6"}
plt.rcParams.update({"font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
                     "legend.fontsize": 7, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "axes.grid.axis": "y", "grid.color": "#e6e6e6", "grid.linewidth": 0.6,
                     "axes.axisbelow": True, "lines.linewidth": 1.4, "lines.markersize": 3.5,
                     "pdf.fonttype": 42, "font.family": "DejaVu Sans"})
PCT = matplotlib.ticker.PercentFormatter(1.0, decimals=0)


def save(fig, d, name):
    fig.tight_layout(pad=0.4)
    fig.savefig(d / f"{name}.pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(d / f"{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def panel(ax, k):
    ax.text(-0.13, 1.04, f"({k})", transform=ax.transAxes, fontsize=9, fontweight="bold", va="bottom")


def nominal(ax, x=None, label=True):
    ax.axhline(0.05, color="#333", ls="--", lw=0.7, zorder=1)
    if label:
        ax.text(ax.get_xlim()[1] if x is None else x, 0.055, "5% target", ha="right", va="bottom", fontsize=6.5, color="#333")


def fig_trap(r, d):
    mons = [m for m in ("M0", "M1", "M2", "M2b", "M3", "M4") if m in r["flag_rate"]["fleet"]]
    conds = [c for c in ("independent", "fleet", "wave", "fleet_drift") if c in r["flag_rate"]]
    fig, ax = plt.subplots(figsize=(6.8, 2.5))
    width = 0.8 / len(conds)
    ax.axvspan(len(mons) - 1.5, len(mons) - 0.5, color="#e8f1fa", zorder=0, lw=0)
    for k, c in enumerate(conds):
        x = np.arange(len(mons)) + (k - (len(conds) - 1) / 2) * width
        v = [r["flag_rate"][c].get(m, {"rate": np.nan, "ci": [np.nan, np.nan]}) for m in mons]
        y = np.array([q["rate"] for q in v])
        lo = y - np.array([q["ci"][0] for q in v])
        hi = np.array([q["ci"][1] for q in v]) - y
        ax.bar(x, y, width * 0.92, color=CCOL[c], label=COND[c], yerr=[lo, hi], capsize=1.5,
               error_kw={"lw": 0.6, "ecolor": "#444"}, zorder=2)
        for xi, yi, h in zip(x, y, hi):
            if c == "fleet" and yi >= 0.15:
                ax.text(xi, yi + h + 0.02, f"{yi:.0%}", ha="center", fontsize=6.5, color=CCOL[c], fontweight="bold")
    for i, m in enumerate(mons):
        if all(r["flag_rate"][c].get(m, {"rate": 1})["rate"] < 0.005 for c in conds):
            ax.text(i, 0.12, "0 everywhere", ha="center", fontsize=6.5, color="#666")
    ax.set_xlim(-0.5, len(mons) - 0.5)
    nominal(ax, label=False)
    ax.text(-0.45, 0.058, "5% target", ha="left", va="bottom", fontsize=6.5, color="#333")
    ax.text(len(mons) - 1, 0.93, "ours", ha="center", fontsize=7, color=MCOL["M4"], fontweight="bold")
    ax.text((len(mons) - 2) / 2, 0.93, "current practice (calibrated on independent agents)", ha="center", fontsize=7, color="#555")
    ax.set_xticks(np.arange(len(mons)), [NAMES[m] for m in mons])
    ax.set_ylabel("pairs flagged as coordinating\n(no agent can communicate)")
    ax.yaxis.set_major_formatter(PCT)
    ax.set_ylim(0, 1)
    ax.legend(ncol=4, loc="lower center", frameon=False, bbox_to_anchor=(0.5, 1.0), handlelength=1.2, columnspacing=1.2)
    save(fig, d, "fig1_fleet_trap")


def fig_tierb(tb, d):
    from matplotlib.lines import Line2D
    rows = tb["rows"]
    nmax = max(r["N"] for r in rows)
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 2.0), gridspec_kw={"width_ratios": [1.25, 1]})
    for wave, ls in ((False, "-"), (True, ":")):
        for m in ("M2", "M3", "M4"):
            rr = sorted([x for x in rows if x["wave"] == wave and x["c"] == 0.0], key=lambda x: x["N"])
            if rr:
                axs[0].plot([x["N"] for x in rr], [max(x[m]["expected_false_alerts"], 1e-1) for x in rr], ls,
                            color=MCOL[m], marker="o" if not wave else None)
    for m, nudge in (("M2", 1.0), ("M3", 1.6), ("M4", 0.6)):
        x = [r for r in rows if not r["wave"] and r["c"] == 0.0 and r["N"] == nmax]
        if x:
            axs[0].text(nmax * 1.12, x[0][m]["expected_false_alerts"] * nudge, f"{x[0][m]['expected_false_alerts']:,.0f}",
                        color=MCOL[m], fontsize=6.5, va="center")
    axs[0].axvline(nmax, color="#999", lw=0.6)
    axs[0].text(nmax * 0.9, 0.5, f"size of the HF swarm\n({nmax:,} agents)", fontsize=6.5, ha="right", va="bottom", color="#555")
    axs[0].set(xscale="log", yscale="log", xlabel="agents in the fleet (N)", ylabel="false alerts on a fleet\nwith zero communication",
               ylim=(0.3, 3e7), xlim=(8, nmax * 2.6))
    axs[0].grid(True, which="major", axis="both", color="#eee")
    h = [Line2D([], [], color=MCOL[m], marker="o", label=NAMES[m]) for m in ("M2", "M3", "M4")]
    h += [Line2D([], [], color="#555", ls="-", label="one start wave"), Line2D([], [], color="#555", ls=":", label="staggered starts")]
    axs[0].legend(handles=h, frameon=False, loc="upper left", ncol=2, fontsize=6.5, handlelength=1.6)
    for m in ("M2", "M3", "M4"):
        rr = sorted([x for x in rows if not x["wave"] and x["N"] == nmax and x["c"] > 0], key=lambda x: x["c"])
        if rr:
            axs[1].plot([x["c"] for x in rr], [x[m]["tpr"] for x in rr], color=MCOL[m], marker="o", label=NAMES[m])
    axs[1].set(xlabel="planted coupling c (share of agents that copy)", ylabel=f"recall on transmission pairs\n(N = {nmax:,})", ylim=(0, 1.08))
    axs[1].yaxis.set_major_formatter(PCT)
    axs[1].legend(frameon=False, loc="center right", bbox_to_anchor=(1.0, 0.68))
    panel(axs[0], "a"); panel(axs[1], "b")
    save(fig, d, "fig2_scale")


def fig_degrade(r, d):
    from matplotlib.lines import Line2D
    h = r.get("H3")
    if not h:
        return
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 2.0), gridspec_kw={"width_ratios": [1, 1.15]})
    xs = sorted(h["drop"], key=float, reverse=True)
    dropped = [1 - float(x) for x in xs]
    for m in ("M2", "M3", "M4"):
        axs[0].plot(dropped, [h["drop"][x][m]["tpr"] for x in xs], color=MCOL[m], marker="o")
        axs[0].plot(dropped, [h["drop"][x][m]["fleet_fpr"] for x in xs], color=MCOL[m], ls=":", marker="x", ms=3)
    nominal(axs[0], label=False)
    axs[0].set(xlabel="log records dropped at random", ylabel="rate", ylim=(0, 1.38), yticks=np.linspace(0, 1, 6))
    axs[0].xaxis.set_major_formatter(PCT); axs[0].yaxis.set_major_formatter(PCT)
    hd = [Line2D([], [], color=MCOL[m], lw=2, label=NAMES[m]) for m in ("M2", "M3", "M4")]
    hd += [Line2D([], [], color="#555", marker="o", label="recall (transmission pairs)"),
           Line2D([], [], color="#555", ls=":", marker="x", ms=3, label="false alarms (fleet pairs)")]
    axs[0].legend(handles=hd, frameon=False, loc="upper right", fontsize=6, handlelength=1.6, ncol=2, columnspacing=0.8)
    labels = ["full log", "new ID /\n10 ticks", "new ID /\n5 ticks", "7% records\nspoofed", "spoofed +\nreconciled"]
    vals = [h["drop"]["1.0"], h["churn"]["period_10"], h["churn"]["period_5"], h["spoof"]["raw_7pct"], h["spoof"]["reconciled"]]
    x = np.arange(len(labels))
    t = [v["M4"]["tpr"] for v in vals]; f = [v["M4"]["fleet_fpr"] for v in vals]
    axs[1].bar(x - 0.2, t, 0.38, color=MCOL["M4"], label="M4 recall", zorder=2)
    axs[1].bar(x + 0.2, f, 0.38, color="#9ecae1", label="M4 fleet false alarms", zorder=2)
    for xi, a, b in zip(x, t, f):
        axs[1].text(xi - 0.2, a + 0.02, f"{a:.0%}", ha="center", fontsize=6, color=MCOL["M4"])
        axs[1].text(xi + 0.2, b + 0.02, f"{b:.0%}", ha="center", fontsize=6, color="#3d7ab0")
    axs[1].set_xlim(-0.6, len(labels) - 0.4)
    nominal(axs[1], label=False)
    axs[1].set_xticks(x, labels, fontsize=6.5)
    axs[1].yaxis.set_major_formatter(PCT)
    axs[1].set_ylim(0, 1.18)
    axs[1].legend(frameon=False, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.04))
    panel(axs[0], "a"); panel(axs[1], "b")
    save(fig, d, "fig3_degrade")


def fig_hawkes(hk, d):
    fig, ax = plt.subplots(figsize=(3.4, 2.5))
    order = [1 / 6, 0.5, 1.0, 3.0, 6.0, 24.0, None]
    ticks = ["10 min", "30 min", "1 h", "3 h", "6 h", "24 h", "const."]
    pos = {b: i for i, b in enumerate(order)}
    ax.axvspan(pos[6.0] - 0.35, pos[6.0] + 0.35, color="#f2f2f2", zorder=0, lw=0)
    for k, col, mk, lab in (("wiki", "k", "o", "collusion.wiki (real)"), ("sim_waves", "#e08a1e", "s", "simulated: start waves,\nzero contagion"),
                            ("sim_contagion", MCOL["M4"], "^", "simulated: contagion\n(true η = 0.5)")):
        rr = sorted(hk[k], key=lambda x: pos[min(order[:-1], key=lambda b: abs(b - x["block_h"])) if x["block_h"] else None])
        ax.plot([pos[min(order[:-1], key=lambda b: abs(b - x["block_h"])) if x["block_h"] else None] for x in rr],
                [x["eta"] for x in rr], color=col, marker=mk, ms=3.5, label=lab)
    ax.scatter([pos[6.0]], [0.87], marker="*", s=40, color="#c0392b", zorder=5, label="Lütje's published η (6 h)")
    ax.set_xticks(range(len(order)), ticks, fontsize=6.8)
    ax.set(xlabel="how finely the baseline may vary", ylabel="fitted branching ratio η", ylim=(-0.03, 1.1))
    ax.legend(frameon=False, loc="upper left", fontsize=6, handlelength=1.5, labelspacing=0.3)
    save(fig, d, "fig4_hawkes")


def fig_lag(r, d):
    lp = r.get("lag_profile")
    if not lp:
        return
    fig, ax = plt.subplots(figsize=(3.4, 2.2))
    for k, col, lab in (("fleet_all_pairs", CCOL["fleet"], "fleet, all pairs"), ("swarm_adopt_pairs", MCOL["M4"], "swarm, transmission pairs")):
        v = np.array(lp[k][0])
        ax.plot(lp["lags"], v / max(v.max(), 1e-9), color=col, marker="o", label=f"{lab} (n = {lp[k][1]:,})")
    ax.axvline(0, color="#999", lw=0.6)
    ax.set(xlabel="lag ℓ (ticks): b acts ℓ ticks after a", ylabel="co-occurrence\n(share of maximum)")
    ax.yaxis.set_major_formatter(PCT)
    ax.legend(frameon=False, fontsize=6.3, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=1)
    save(fig, d, "fig5_lag")


def numbers(r, tb, hk):
    fr = r["flag_rate"]
    n = {"n_episodes": r["n_episodes"], "m2_threshold": r["m2_threshold"],
         "flag_rate": {c: {m: [round(v["rate"], 4)] + [round(x, 4) for x in v["ci"]] for m, v in d.items()} for c, d in fr.items()},
         "swarm": r["swarm"],
         "H2": {m: ({"tpr": round(v["tpr_nominal"]["rate"], 4), "tpr_ci": [round(x, 4) for x in v["tpr_nominal"]["ci"]],
                     "tpr_at_5pct_fleet": round(v["tpr_at_5pct_fleet_fpr"], 4),
                     "swarm_unlinked": round(v["flag_rate_swarm_no_link_pairs"]["rate"], 4)} if "tpr_nominal" in v else
                    {k: (round(x, 4) if isinstance(x, float) else x) for k, x in v.items()})
                for m, v in r["H2"].items()},
         "H5": r["H5"]}
    existing = [m for m in ("M0", "M1", "M2", "M2b", "M3") if m in fr.get("fleet", {})]
    n["H1_monitors_ge_015"] = [m for m in existing if fr["fleet"][m]["rate"] >= 0.15]
    n["H1_all_ci_include_005"] = all(fr["fleet"][m]["ci"][0] <= 0.05 <= fr["fleet"][m]["ci"][1] for m in existing)
    if tb:
        n["tierb"] = [{"wave": x["wave"], "N": x["N"], "c": x["c"],
                       **{m: {"fpr": round(x[m]["fpr"], 4), "tpr": round(x[m]["tpr"], 4) if x[m]["tpr"] == x[m]["tpr"] else None,
                              "false_alerts": round(x[m]["expected_false_alerts"], 1)} for m in ("M2", "M3", "M4")}}
                      for x in tb["rows"]]
    if hk:
        n["hawkes"] = {k: [(x["block_h"], round(x["eta"], 3), round(x["reaction_min"], 1)) for x in hk[k]]
                       for k in ("wiki", "sim_waves", "sim_contagion")}
        n["hawkes_n"] = hk["n_arrivals"]
    if r.get("H3"):
        n["H3"] = json.loads(json.dumps(r["H3"]), parse_float=lambda s: round(float(s), 4))
    return n


def extras(phase, root=ROOT):
    """Post-freeze, exploratory additions (reviewer requests): the rare-endpoint rule baseline and the
    distribution of the M1 judge's answers. Recomputed by verify.py like every other number."""
    from analysis import rare_endpoint_baseline as R
    rb = R.summary(phase, root)
    rnd = lambda v: {"rate": round(v["rate"], 4), "ci": [round(x, 4) for x in v["ci"]]}  # noqa: E731
    out = {"rare_endpoint": {q: {"flag_rate": {c: rnd(v) for c, v in o["flag_rate"].items()},
                                 "tpr": rnd(o["swarm_transmission_tpr"]), "unlinked": rnd(o["swarm_unlinked"])}
                             for q, o in rb.items()}}
    j = [json.loads(l) for l in open(ROOT / "results" / phase / "judge_cache.jsonl")]
    out["judge"] = {"n": len(j), "suspicion_values": sorted({x["suspicion"] for x in j}),
                    "with_pairs": sum(bool(x["pairs"]) for x in j)}
    return out


def gates(phase):
    """Manipulation checks and data checks (same definitions as src/analysis/pilot_gates.py)."""
    from analysis import pilot_gates as G
    from common import LOGS, RUNS
    rows = {}
    for d in sorted((RUNS / phase).glob("*/ep*")):
        if not (d / "meta.json").exists():
            continue
        ev, meta = G.load(d)
        c = meta["condition"]
        r = {"same_action": G.same_action(ev, meta), "alt_share": G.alt_share(ev, meta),
             "agent_error": sum(1 for e in ev if e.get("kind") == "agent_error"),
             "no_action": sum(1 for e in ev if e.get("kind") == "no_action"), "turns": len(ev),
             "foreign": sum(1 for e in ev if e.get("kind") == "alt" and not e.get("own_variant"))}
        if c in ("swarm", "uninstructed"):
            r.update(G.swarm_stats(ev, meta))
        rows.setdefault(c, []).append(r)
    mean = lambda c, k: float(np.mean([r[k] for r in rows.get(c, [])]))  # noqa: E731
    out = {"G1_frac_swarm_eps_with_adoption": float(np.mean([r["canary_adoptions"] >= 1 for r in rows["swarm"]])),
           "G1_adoptions_total": int(sum(r["canary_adoptions"] for r in rows["swarm"])),
           "G2_same_action": {"fleet": round(mean("fleet", "same_action"), 4), "independent": round(mean("independent", "same_action"), 4)},
           "G3_pseudo_pairs": round(G.pseudo_pair_same_action(phase, "independent"), 4),
           "G4_alt_share": {"fleet": round(mean("fleet", "alt_share"), 4), "swarm": round(mean("swarm", "alt_share"), 4)},
           "agent_error_rate": {c: round(sum(r["agent_error"] for r in v) / sum(r["turns"] for r in v), 4) for c, v in rows.items()},
           "no_action_rate": {c: round(sum(r["no_action"] for r in v) / sum(r["turns"] for r in v), 4) for c, v in rows.items()},
           "foreign_without_board": {c: int(sum(r["foreign"] for r in rows[c])) for c in rows if c not in ("swarm", "uninstructed")},
           "uninstructed": {"frac_write": round(mean("uninstructed", "frac_write"), 4),
                            "frac_read_peer": round(mean("uninstructed", "frac_read_peer"), 4),
                            "adoptions": int(sum(r["canary_adoptions"] for r in rows.get("uninstructed", [])))},
           "swarm_nondisc_read": round(mean("swarm", "frac_nondisc_read_peer"), 4)}
    calls = [json.loads(l) for l in open(LOGS / "calls.jsonl") if f'"ep": "{phase}/' in l]
    out["calls"] = {"agent_calls": sum(1 for c in calls if c["purpose"] == "agent"),
                    "judge_calls": sum(1 for c in calls if c["purpose"] == "judge"),
                    "providers": sorted({str(c["provider"]) for c in calls if c["purpose"] == "agent"}),
                    "cost_usd": round(sum(c["cost_usd"] for c in calls), 2)}
    return out


def main(phase, tierb_dir="tierb"):
    rd = ROOT / "results" / phase
    d = rd / "figures"
    d.mkdir(parents=True, exist_ok=True)
    r = json.load(open(rd / "results.json"))
    tbf, hkf = ROOT / "results" / tierb_dir / "tierb.json", ROOT / "results/wiki/hawkes.json"
    tb = json.load(open(tbf)) if tbf.exists() else None
    hk = json.load(open(hkf)) if hkf.exists() else None
    fig_trap(r, d)
    fig_degrade(r, d)
    fig_lag(r, d)
    if tb:
        fig_tierb(tb, d)
    if hk:
        fig_hawkes(hk, d)
    nums = numbers(r, tb, hk)
    nums["gates"] = gates(phase)
    nums.update(extras(phase))
    json.dump(nums, open(rd / "report_numbers.json", "w"), indent=1, sort_keys=True)
    return nums


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="main")
    ap.add_argument("--tierb", default="tierb")
    a = ap.parse_args()
    main(a.phase, a.tierb)
    print("ok")
