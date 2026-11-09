"""Recompute the Tier A (10-agent) numbers from the raw logs, read Tier B and wiki numbers from their saved outputs, and diff against results/<phase>/report_numbers.json.

Steps: (1) check the frozen files' SHA-256 against plan/FREEZE.sha256; (2) re-run score_tierA (M1 judge
answers are read from the cache, no new LLM calls) into a scratch copy; (3) rebuild report_numbers from
the scratch results plus results/tierb and results/wiki; (4) print any difference. Exit code 1 on any
mismatch.

Usage: .venv/bin/python src/analysis/verify.py --phase main
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT  # noqa: E402


def check_freeze() -> list[str]:
    bad = []
    for line in open(ROOT / "plan/FREEZE.sha256"):
        h, f = line.split(maxsplit=1)
        f = f.strip()
        if hashlib.sha256((ROOT / f).read_bytes()).hexdigest() != h:
            bad.append(f)
    return bad


def diff(a, b, path=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            out += diff(a.get(k), b.get(k), f"{path}.{k}")
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, f"{path}[{i}]")
    elif a != b and not (isinstance(a, float) and isinstance(b, float) and (a != a and b != b)):
        out.append(f"{path}: stored {a!r} vs recomputed {b!r}")
    return out


def main(phase: str, tierb: str = "tierb") -> int:
    bad = check_freeze()
    print("freeze hashes:", "OK" if not bad else f"CHANGED {bad}")
    from analysis import figures, score_tierA
    stored = json.load(open(ROOT / "results" / phase / "report_numbers.json"))
    # score_tierA (frozen) writes to <ROOT>/results/<phase>; redirect its ROOT to a scratch tree
    sroot = ROOT / "results" / f"_verify_{phase}"
    sd = sroot / "results" / phase
    sd.mkdir(parents=True, exist_ok=True)
    cache = ROOT / "results" / phase / "judge_cache.jsonl"
    judge = cache.exists()
    if judge:
        shutil.copy(cache, sd / "judge_cache.jsonl")
    orig = score_tierA.ROOT
    score_tierA.ROOT = sroot
    try:
        conds = sorted({json.loads(l)["ep"].split("/")[1] for l in open(cache)}) if judge else None
        res = score_tierA.main(phase, judge, True, conds)
    finally:
        score_tierA.ROOT = orig
    r_tb = ROOT / "results" / tierb / "tierb.json"
    r_hk = ROOT / "results/wiki/hawkes.json"
    nums = figures.numbers(res, json.load(open(r_tb)) if r_tb.exists() else None,
                           json.load(open(r_hk)) if r_hk.exists() else None)
    nums["gates"] = figures.gates(phase)
    nums.update(figures.extras(phase, sroot))
    nums = json.loads(json.dumps(nums, sort_keys=True, default=float))
    d = diff(stored, nums)
    shutil.rmtree(sroot, ignore_errors=True)
    print("report numbers:", "identical" if not d else f"{len(d)} differences")
    for x in d[:40]:
        print("  ", x)
    return 1 if (d or bad) else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="main")
    ap.add_argument("--tierb", default="tierb")
    a = ap.parse_args()
    sys.exit(main(a.phase, a.tierb))
