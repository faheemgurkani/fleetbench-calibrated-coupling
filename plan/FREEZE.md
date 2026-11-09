# Freeze record (v1)

**Frozen at:** 2026-11-07T21:55:57Z (UTC), **before any main-phase episode exists** (`data/runs/main/` does not exist at this time). Dev data (`data/runs/dev/`) was used to fix the design; it is not part of the confirmatory analysis.

Any edit to a file below after this time must be recorded in [deviations.md](deviations.md) with a version bump (v2, …), and the affected analyses labelled exploratory.

| File | SHA-256 |
|---|---|
| `plan/methodology.md` | `e9e5e8598f7c5f24f7599a229aa1bf3213c170608b6c09665f037f051071469c` |
| `plan/frozen/judge_prompt_v1.md` | `eb01da6131cbdd113efb1334fe1ff8ff60c75b5e585986052e2e4c6864090823` |
| `plan/frozen/keyword_list_v1.md` | `6c12831c3f437b53354c0ed3cd166d851d4362bb9fcc48b1e5dc2c41b1f18414` |
| `src/sandbox/world.py` | `d9b01ab2f1ff9bce3f75a2a8cee68d48320dea4c35a93cac59828318f40f5788` |
| `src/sandbox/run_episode.py` | `f3dde564c458734a3f75b7fd7585038d5f05cbeee6b49dfaabcf9cdb0bd667f0` |
| `src/fleetbench/views.py` | `780b404114849a386a64212befcb06d7a456ed1bebcbb43b4b4a0c7d34839203` |
| `src/fleetbench/monitors.py` | `ca2f040d29f563e72a3eb213ee915149b021f2fe89a6f793019fc3aa37b8a89e` |
| `src/fleetbench/judge.py` | `5eb4a62086e9531df38f53234a71d53875114775e1698194199bab3c7e5b8a6a` |
| `src/fleetbench/degrade.py` | `ab4fac7700d3e309e53bcf024c2fb357990529b63f797297345b158796abfa73` |
| `src/fleetbench/metrics.py` | `d758da92f38ff28bad8e47383c3c94a487b0ba6026f231df8c0d9dedb4181007` |
| `src/analysis/score_tierA.py` | `38fe2896e1ab2dd006aae6df4b5dd7072284a5a9933e537ebebbcac62a9ff8bc` |
| `src/common.py` | `3750d0c6dd5fb49e49ff6beab031ac08ae2e2bdaec14f236c3961320348323f3` |

Verify (from the project root): `shasum -a 256 -c plan/FREEZE.sha256`
