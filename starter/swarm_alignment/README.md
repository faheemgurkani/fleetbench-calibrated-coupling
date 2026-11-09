# Swarm Alignment starter (assembled locally)

This sprint has **no official starter repo** (unlike the AI Collusion sprint). This folder gathers the code and datasets that the [Resources tab](../../docs/sprint/02_resources.md) points to. Shallow clones were made 2026-11-05, and their `.git` folders were removed to keep the tree small. Re-clone from upstream to update.

| Folder | Upstream | Track | What it is |
|---|---|---|---|
| `concordia/` | https://github.com/google-deepmind/concordia | 1 | Google DeepMind library for generative-agent simulations |
| `GovSim/` | https://github.com/giorgiopiatti/GovSim | 1 | LLM agents sharing a common resource (Piatti et al., 2024) |
| `A2A/` | https://github.com/a2aproject/A2A | 3 | Agent2Agent protocol spec and SDK samples (Google, 2025) |
| `datasets/swarm-traces/redacted.jsonl.gz` | https://swarmtraces.org/data/final/redacted.jsonl.gz | 4 | Redacted dataset of 80k+ reconstructed attack payloads from the HF incident (15 MB). Browse it at https://swarmtraces.org/viewer/ |
| `Agents_Failure_Attribution/` | https://github.com/mingyin1/Agents_Failure_Attribution | 4 | Code for "Which agent causes task failures and when?" (Zhang et al., 2025) |
| `datasets/who-and-when/` | https://huggingface.co/datasets/Kevin355/Who_and_When | 4 | Who&When: multi-agent failure logs labelled with the failing agent and step (9 MB) |
| `AI-GBS/` | https://github.com/riedlc/AI-GBS | 2, 4 | Code for Riedl (2026), emergent coordination. `results_compressed.tar.xz` is an LFS pointer only; the object is missing upstream |
| `control-evaluations/` | https://github.com/rgreenblatt/control-evaluations | 4 | Code for AI Control (Greenblatt et al., 2024) |
| `control-arena/` | https://github.com/UKGovernmentBEIS/control-arena | 4 | UK AISI library of AI control settings and protocols (not on the sprint page) |
| `camel-cua/`, `camel-prompt-injection/` | https://github.com/cleverhans-lab/camel-cua, https://github.com/google-research/camel-prompt-injection | 4 | Code for CaMeLs Can Use Computers Too (Foerster et al., 2026) and the original CaMeL |
| `datasets/transluce/` | https://transluce.org/data/urlquery-agent-activity-2026-09-23.zip | 4 | Transluce urlquery agent-activity dataset (4.6 MB zip, 16 files: reports, sources, classifications) |
| `datasets/collusion-wiki/` | https://collusion.wiki/explorer/download | 4, 2 | DSE wiki swarm (OpenAI agents, May–Jul 2026): 14,591 revisions with full text and timestamps, 5,217 deletions, 3,103 self-chosen names, IP /16, links, shortener logs. Not on the sprint page. Checksums in `SHA256SUMS` (verified 2026-11-06) |
| `datasets/ai-village/` | https://huggingface.co/datasets/aidigestorg/ai-village | 4 | **Gated.** Only the dataset card (`README.md`) is local; see below |

## AI Village transcripts (gated)
The full dataset is ~280 GB, or ~10 GB without screenshot tarballs. Request access on the HF page, then run:
```bash
hf auth login
hf download aidigestorg/ai-village --repo-type dataset --local-dir starter/swarm_alignment/datasets/ai-village \
  --include "*.md" "example.py" "swarm-village/*.gz" "swarm-village/*.json" "game-jam-village/*.gz" "game-jam-village/*.json"
```
Sizes (text only): `swarm-village` ~124 MB · `game-jam-village` ~23 MB · `open-chat-village` ~1.8 GB · `main-village` ~8.4 GB. Skip `*/images/` unless you need the screenshots.

## Other tools named on the sprint page (not downloadable code)
- Transluce agent-activity logs: https://transluce.org/agent-activity (see `docs/incident/sources/Transluce_2026_agent-activity.md`)
- swarms.wiki directory of environments, datasets and incident trackers: `docs/sprint/external/swarms-wiki.md`
- Adaption platform (AutoScientist, Adaptive Data, Invent-a-Dataset), with $500 credits: https://adaptionlabs.ai/app

## No public code found (checked 2026-11-06)
Prompt Infection (Lee & Tiwari, 2024), Secret Collusion (Motwani et al., 2024), Rose et al. (2026), Jones et al. (2025), Agrawal, Tilli, Jørgensen. The papers themselves are in `docs/sprint/papers/`.
