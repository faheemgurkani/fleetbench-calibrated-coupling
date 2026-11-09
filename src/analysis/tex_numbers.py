"""Turn results/<phase>/report_numbers.json into LaTeX macros (report/latex/numbers.tex), so every number
in the PDF comes from the verified JSON. Macro names: \\nFR<cond><monitor> (rate, %), \\nFRlo..., \\nFRhi...

Usage: .venv/bin/python src/analysis/tex_numbers.py --phase main
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT  # noqa: E402

ALPH = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven",
        "8": "eight", "9": "nine"}


def name(*parts) -> str:
    s = "".join(p[:1].upper() + p[1:] for p in parts)
    s = re.sub(r"\d", lambda m: ALPH[m.group(0)], s)
    return "n" + re.sub(r"[^A-Za-z]", "", s)


def pct(x, nd=1):
    return "--" if x is None or x != x else f"{100 * x:.{nd}f}"


def main(phase: str):
    n = json.load(open(ROOT / "results" / phase / "report_numbers.json"))
    out = []

    def m(k, v):
        out.append(f"\\newcommand{{\\{k}}}{{{v}}}")
    for c, d in n["flag_rate"].items():
        for mon, (r, lo, hi) in d.items():
            m(name("FR", c, mon), pct(r))
            m(name("FRlo", c, mon), pct(lo))
            m(name("FRhi", c, mon), pct(hi))
    for mon, v in n["H2"].items():
        if "tpr" in v:
            m(name("TPR", mon), pct(v["tpr"]))
            m(name("TPRlo", mon), pct(v["tpr_ci"][0]))
            m(name("TPRhi", mon), pct(v["tpr_ci"][1]))
            m(name("TPRat", mon), pct(v["tpr_at_5pct_fleet"]))
            m(name("Unlinked", mon), pct(v["swarm_unlinked"]))
    e = n["H2"]["M4_edges"]
    for k in ("precision_adopt", "recall_adopt", "pair_precision_provenance", "pair_recall_provenance", "precision_adopt_or_read"):
        m(name("Edge", k.replace("_", "")), pct(e[k]))
    m("nEdgePred", e["n_pred"])
    m("nEdgeAdopt", e["n_adopt_edges"])
    sw = n["swarm"]
    m("nSwarmEps", sw["n_episodes"])
    m("nSwarmTx", sw["episodes_with_transmission"])
    m("nAdoptPairs", sw["adopt_pairs"])
    for c, k in n["n_episodes"].items():
        m(name("Eps", c), k)
    m("nEpsTotal", sum(n["n_episodes"].values()))
    m("nHoneMonitors", len(n["H1_monitors_ge_015"]))
    m("nHoneList", ", ".join(n["H1_monitors_ge_015"]))
    h5 = n.get("H5", {})
    if "tacit_M4" in h5:
        m("nTacitMfour", pct(h5["tacit_M4"]["rate"]))
        m("nTacitMfourlo", pct(h5["tacit_M4"]["ci"][0]))
        m("nTacitMfourhi", pct(h5["tacit_M4"]["ci"][1]))
        ts = [x for x in h5["tacit_modal_share"] if x == x]
        m("nTacitModal", pct(sum(ts) / len(ts)))
    if "uninstructed_no_transmission_M4" in h5:
        u = h5["uninstructed_no_transmission_M4"]
        m("nUninstMfour", pct(u["rate"]))
        m("nUninstMfourlo", pct(u["ci"][0]))
        m("nUninstMfourhi", pct(u["ci"][1]))
        m("nUninstTxPairs", h5["uninstructed_transmission_pairs"])
    h3 = n.get("H3")
    if h3:
        for obs, d in h3["drop"].items():
            for mon, v in d.items():
                m(name("Drop", obs.replace(".", "p"), mon, "tpr"), pct(v["tpr"]))
                m(name("Drop", obs.replace(".", "p"), mon, "fpr"), pct(v["fleet_fpr"]))
        for per, d in h3["churn"].items():
            for mon, v in d.items():
                m(name("Churn", per.replace("period_", "p"), mon, "tpr"), pct(v["tpr"]))
                m(name("Churn", per.replace("period_", "p"), mon, "fpr"), pct(v["fleet_fpr"]))
        for k in ("raw_7pct", "reconciled"):
            for mon, v in h3["spoof"][k].items():
                m(name("Spoof", k.replace("_", ""), mon, "tpr"), pct(v["tpr"]))
                m(name("Spoof", k.replace("_", ""), mon, "fpr"), pct(v["fleet_fpr"]))
        m("nSpoofMism", h3["spoof"]["mismatches_found"])
    if n.get("hawkes"):
        for k, rows in n["hawkes"].items():
            for blk, eta, rt in rows:
                tag = "const" if blk is None else f"b{blk:.3f}".replace(".", "p")
                m(name("Eta", k.replace("_", ""), tag), f"{eta:.2f}")
                m(name("React", k.replace("_", ""), tag), f"{rt:.0f}" if rt == rt and rt != float("inf") else "--")
        m("nHawkesN", f"{n['hawkes_n']:,}")
    if n.get("tierb"):
        for x in n["tierb"]:
            tag = f"{'w' if x['wave'] else 'f'}N{x['N']}c{int(round(100 * x['c']))}"
            for mon in ("M2", "M3", "M4"):
                m(name("TB", tag, mon, "fpr"), pct(x[mon]["fpr"]))
                m(name("TB", tag, mon, "fa"), f"{x[mon]['false_alerts']:,.0f}")
                m(name("TB", tag, mon, "tpr"), pct(x[mon]["tpr"]) if x[mon]["tpr"] is not None else "--")
    g = n.get("gates")
    if g:
        m("nGoneFrac", pct(g["G1_frac_swarm_eps_with_adoption"], 0))
        m("nGoneAdopt", g["G1_adoptions_total"])
        m("nGtwoFleet", f"{g['G2_same_action']['fleet']:.2f}")
        m("nGtwoInd", f"{g['G2_same_action']['independent']:.2f}")
        m("nGthreePseudo", f"{g['G3_pseudo_pairs']:.2f}")
        m("nGfourFleet", pct(g["G4_alt_share"]["fleet"], 0))
        m("nGfourSwarm", pct(g["G4_alt_share"]["swarm"], 0))
        m("nAgentErrMax", pct(max(g["agent_error_rate"].values())))
        m("nNoActionMax", pct(max(g["no_action_rate"].values())))
        m("nForeign", sum(g["foreign_without_board"].values()))
        m("nAgentCalls", f"{g['calls']['agent_calls']:,}")
        m("nJudgeCalls", g["calls"]["judge_calls"])
        m("nCost", f"{g['calls']['cost_usd']:.2f}")
        m("nUnWrite", pct(g["uninstructed"]["frac_write"], 0))
        m("nUnRead", pct(g["uninstructed"]["frac_read_peer"], 0))
        m("nUnAdopt", g["uninstructed"]["adoptions"])
        m("nSwarmNDRead", pct(g["swarm_nondisc_read"], 0))
    for q, o in n.get("rare_endpoint", {}).items():
        t = q.replace("0.", "q")
        for c, v in o["flag_rate"].items():
            m(name("RE", t, c), pct(v["rate"]))
            m(name("RElo", t, c), pct(v["ci"][0]))
            m(name("REhi", t, c), pct(v["ci"][1]))
        m(name("RE", t, "tpr"), pct(o["tpr"]["rate"]))
        m(name("RElo", t, "tpr"), pct(o["tpr"]["ci"][0]))
        m(name("REhi", t, "tpr"), pct(o["tpr"]["ci"][1]))
        m(name("RE", t, "unlinked"), pct(o["unlinked"]["rate"]))
    if n.get("judge"):
        m("nJudgeN", n["judge"]["n"])
        m("nJudgeSusp", ", ".join(str(x) for x in n["judge"]["suspicion_values"]))
        m("nJudgePairs", n["judge"]["with_pairs"])
    od = ROOT / "report" / "latex"
    od.mkdir(parents=True, exist_ok=True)
    (od / "numbers.tex").write_text("% generated by src/analysis/tex_numbers.py from results/" + phase +
                                    "/report_numbers.json; do not edit\n" + "\n".join(out) + "\n")
    print(len(out), "macros")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="main")
    main(ap.parse_args().phase)
