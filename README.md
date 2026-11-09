# Swarm or Fleet? FleetBench and a fleet-calibrated coordination test

Built during the [Apart Research Swarm Alignment Hackathon](https://apartresearch.com/sprints/swarm-alignment-2026) (6–8 November 2026), Track 4 (Multi-Agent Oversight and Control), and not submitted to it. Author: Muhammad Faheem (Team Penstronus, independent researcher).

**Status:** a working report. A fuller paper that combines these results with the author's earlier AI Collusion Research sprint, with broader testing and evaluation, is in preparation.

**Report:** [`report/latex/report.pdf`](report/latex/report.pdf)

## The question
Agents in one deployment share a model, a task queue and the same outages, so their logs correlate even when no agent ever reads another's output (a **fleet**). A **swarm** is the same plus a channel that is actually used. Coordination monitors are validated against *independent* agents, so how often do they call a fleet a swarm (**the fleet trap**)? And does a null built from replicate runs of the same deployment fix it?

## What is here
| Path | Contents |
|---|---|
| `src/sandbox/` | FleetBench Tier A: fake city API, task queues, shared outage, notes board, witness log (`world.py`); episode runner (`run_episode.py`) |
| `src/fleetbench/` | Views and ground truth (`views.py`), monitors M0–M4 (`monitors.py`, `judge.py`), degradation operators (`degrade.py`), statistics (`metrics.py`) |
| `src/sim/tierb.py` | Tier B: resamples Tier A trajectories into fleets of up to 1,200 agents |
| `src/analysis/` | Gates (`pilot_gates.py`), scoring (`score_tierA.py`), collusion.wiki Hawkes refit (`wiki_hawkes.py`), figures and report numbers (`figures.py`, `tex_numbers.py`), end-to-end check (`verify.py`) |
| `plan/` | Execution plan, methodology, **freeze record with SHA-256 hashes** (`FREEZE.md`, `FREEZE.sha256`), every pre-freeze change with reasons (`deviations.md`), frozen judge prompt and keyword list |
| `data/runs/main/` | All 300 main episodes: witness log (`events.jsonl`), agent transcripts, metadata |
| `data/runs/dev/`, `data/runs/_discarded/` | Dev set and superseded pilots (used to fix the design before the freeze) |
| `data/logs/calls.jsonl` | Every LLM call: model, pinned provider, seed, tokens, cost |
| `results/` | Scores, Tier B sweep, Hawkes fits, figures, `report_numbers.json` |
| `tests/` | Unit and synthetic-calibration tests (world, monitors, degradation, metrics, Tier B, Hawkes) |

## Reproduce
Python 3.11; `pip install openai numpy scipy matplotlib pytest`.
```bash
python -m pytest -q tests                                  # unit + synthetic calibration tests
shasum -a 256 -c plan/FREEZE.sha256                        # frozen files unchanged
# analysis from the logged episodes (no LLM calls; M1 judge answers are cached)
python src/analysis/score_tierA.py --phase main --judge
python src/sim/tierb.py --phase main
python src/analysis/wiki_hawkes.py                         # needs the public collusion.wiki export
python src/analysis/figures.py --phase main
python src/analysis/verify.py --phase main                 # re-scores Tier A from raw logs, diffs the report numbers
```
Re-running the agents needs an OpenRouter key in `.env` (`OPENROUTER_API_KEY=...`):
`python src/sandbox/run_episode.py --phase main --conditions independent fleet swarm uninstructed tacit wave fleet_drift --episodes 30` (then `--conditions independent fleet swarm --episodes 60`). Total spend for all 300 episodes plus judging was about $2.

## Prior work and pre-existing code
The logged LLM-client pattern (`src/common.py`) and the auditor prompt adapted for M1 come from the author's previous Apart sprint (AI Collusion Research, October 2026). Everything else was written during this sprint (6–8 November 2026). The collusion.wiki export and the incident reports are third-party sources and are not redistributed here.

## Dual use
A timing- and provenance-based detector tells a coordinating swarm what to hide. We publish the benchmark, the test and its failure modes, not evasion strategies. The sandbox runs harmless lookups against a fake local API; no agent had internet access.
