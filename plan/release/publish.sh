#!/usr/bin/env bash
# Lift the pre-deadline whitelist and publish code, data, results and report. Run from the project root
# only when the author decides to go public (after submitting, ideally after the deadline: Mon 9 Nov 16:59 PKT).
set -euo pipefail
shasum -a 256 -c plan/FREEZE.sha256 >/dev/null && echo "freeze hashes OK"
.venv/bin/python -m pytest -q tests
.venv/bin/python src/analysis/verify.py --phase main
cp plan/release/gitignore.postdeadline .gitignore
cp plan/release/README_final.md README.md
git add -A
echo "--- staged (check before pushing) ---"; git status --short | wc -l
git status --short | grep -E "\.env|CLAUDE\.md|docs/notes|research_notes|reports/" && { echo "private file staged, aborting"; exit 1; } || true
git commit -m "Release FleetBench: sandbox, monitors, frozen plan, 300 episodes, results and report"
git push origin main
