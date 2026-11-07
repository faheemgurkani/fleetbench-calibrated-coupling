# Papers referenced on the sprint page

Every paper cited in the Overview and Resources tabs, downloaded 2026-11-05. I checked titles and first authors against each PDF's first page and, for the OpenReview papers, against the OpenReview API.

## How the folder is organized

```
papers/
├── _all/                                ← each PDF stored once (27 files)
├── general/                             ← "Suggested reading: General" (5)
├── track-1_sandboxes-and-testbeds/      ← papers cited under Track 1 (4)
├── track-2_science-of-agent-networks/   ← papers cited under Track 2 (5)
├── track-3_agent-infrastructure/        ← papers cited under Track 3 (5)
└── track-4_oversight-and-control/       ← papers cited under Track 4 (9)
```

Tracks follow the website's [Resources tab](../02_resources.md). If a paper is cited under several tracks, it appears in each of those track folders as a symlink to `_all/`, so every folder is complete on its own. Links marked *(overview)* come from the Overview tab's track questions, and *(example)* marks the "Example projects" section, not the reading list. The incident reports are in [`../../incident/sources/`](../../incident/sources/).

File names follow `FirstAuthor_Year_ShortTitle_[Venue]_<arXiv id | openreview-id>.pdf`. When an OpenReview venue version exists, that is the copy kept.

---

## General → [`general/`](general/)
- [Hammond et al. 2025, *Multi-Agent Risks from Advanced AI*](general/Hammond_2025_MultiAgentRisks_2502.14143.pdf): the taxonomy of miscoordination, conflict and collusion. Also *(overview)* "Making each model safe on its own is not enough"
- [Tomašev et al. 2025, *Distributional AGI Safety*](general/Tomasev_2025_DistributionalAGISafety_2512.16856.pdf)
- [Dafoe et al. 2020, *Open Problems in Cooperative AI*](general/Dafoe_2020_OpenProblemsCooperativeAI_2012.08630.pdf)
- [Chan et al. 2025, *Infrastructure for AI Agents*](general/Chan_2025_InfrastructureForAIAgents_2501.10114.pdf)
- [Conitzer & Oesterheld 2023, *Foundations of Cooperative AI* (AAAI)](general/Conitzer_2023_FoundationsCooperativeAI_AAAI.pdf)
- ARIA *Scaling Trust* programme thesis is a web page: [`../external/ARIA_scaling-trust.md`](../external/ARIA_scaling-trust.md)

## Track 1: Sandboxes and Testbeds → [`track-1_sandboxes-and-testbeds/`](track-1_sandboxes-and-testbeds/)
- [Park et al. 2023, *Generative Agents*](track-1_sandboxes-and-testbeds/Park_2023_GenerativeAgents_2304.03442.pdf)
- [Akata et al. 2025, *Playing repeated games with LLMs* (Nature Human Behaviour)](track-1_sandboxes-and-testbeds/Akata_2025_RepeatedGamesLLMs_NatHumBehav_2305.16867.pdf)
- [Gandhi, Sadigh & Goodman 2023, *Strategic Reasoning with Language Models* (FMDM @ NeurIPS 2023)](track-1_sandboxes-and-testbeds/Gandhi_2023_StrategicReasoningLLMs_FMDM-NeurIPSw_openreview-MUtbsFRZwI.pdf): LLM agents in stylised games
- [Piatti et al. 2024, *GovSim*](track-1_sandboxes-and-testbeds/Piatti_2024_GovSim_2404.16698.pdf). Code in `starter/swarm_alignment/GovSim`
- Not papers: CRUX (Kapoor et al., 2026): [`../external/CRUX_cruxevals.md`](../external/CRUX_cruxevals.md). Concordia: `starter/swarm_alignment/concordia`

## Track 2: The Science of Agent Networks → [`track-2_science-of-agent-networks/`](track-2_science-of-agent-networks/)
- [Lee & Tiwari 2024, *Prompt Infection*](track-2_science-of-agent-networks/Lee_2024_PromptInfection_2410.07283.pdf). Also *(overview)* "how fast and how far does the bad behaviour spread"
- [Jones, Dragan & Steinhardt 2025, *Adversaries Can Misuse Combinations of Safe Models* (ICML 2025)](track-2_science-of-agent-networks/Jones_2025_CombinationsOfSafeModels_ICML_openreview-GCkhEPE1FG.pdf): splitting tasks to evade per-agent filters
- [Agrawal, Ebadian & Hammond 2026, *The Multi-Agent Off-Switch Game* (AAMAS 2026)](track-2_science-of-agent-networks/Agrawal_2026_MultiAgentOffSwitchGame_AAMAS.pdf): coordination to resist modification/shutdown
- [Tilli 2026, *Agent Properties for Multi-Agent Safety* (ICLR 2026 AIWILD workshop)](track-2_science-of-agent-networks/Tilli_2026_AgentPropertiesMultiAgentSafety_ICLRw_openreview-00KtDBoKnO.pdf): from individual cooperation properties to system outcomes
- [Jørgensen, Weichwald & Hammond 2026, *Causal Foundations of Collective Agency* (CLeaR 2026)](track-2_science-of-agent-networks/Jorgensen_2026_CausalFoundationsCollectiveAgency_CLeaR_openreview-NacA6YRBNX.pdf)
- *(example)* "Will they find the message board?" builds on Wijk et al. 2026 = the METR report in `../../incident/sources/`

## Track 3: Strengthening Agent Infrastructure → [`track-3_agent-infrastructure/`](track-3_agent-infrastructure/)
- [Chan et al. 2024, *IDs for AI Systems*](track-3_agent-infrastructure/Chan_2024_IDsForAISystems_2406.12137.pdf)
- [Kirchenbauer et al. 2023, *A Watermark for LLMs* (ICML)](track-3_agent-infrastructure/Kirchenbauer_2023_WatermarkLLMs_ICML.pdf)
- [Sun et al. 2023, *Cooperative AI via Decentralized Commitment Devices*](track-3_agent-infrastructure/Sun_2023_DecentralizedCommitmentDevices_2311.07815.pdf) (from the 2024 Sprint)
- [Ramírez et al. 2023, *Game Manipulators: the Strategic Implications of Binding Contracts*](track-3_agent-infrastructure/Ramirez_2023_GameManipulators_2311.10586.pdf) (from the 2024 Sprint)
- [Haupt et al. 2022, *Formal Contracts Mitigate Social Dilemmas in MARL*](track-3_agent-infrastructure/Haupt_2022_FormalContractsMARL_2208.10469.pdf) (from the 2024 Sprint)
- ❌ **Tennenholtz 2004, *Program Equilibrium*** (Games and Economic Behavior 49(2), DOI 10.1016/j.geb.2004.02.002) is paywalled on ScienceDirect and has no free copy. Get it through a library: https://www.sciencedirect.com/science/article/pii/S0899825604000314. *(overview)* commitment through inspectable code
- A2A protocol (Google, 2025): [`../external/Google_2025_A2A-announcement.md`](../external/Google_2025_A2A-announcement.md). Code in `starter/swarm_alignment/A2A`

## Track 4: Multi-Agent Oversight and Control → [`track-4_oversight-and-control/`](track-4_oversight-and-control/)
- [Motwani et al. 2024, *Secret Collusion among AI Agents* (NeurIPS)](track-4_oversight-and-control/Motwani_2024_SecretCollusion_2402.07510.pdf). Also *(overview)*
- [Rose et al. 2026, *Detecting Multi-Agent Collusion Through Multi-Agent Interpretability*](track-4_oversight-and-control/Rose_2026_MultiAgentInterpretability_2604.01151.pdf). Also *(overview)*
- [Greenblatt et al. 2024, *AI Control*](track-4_oversight-and-control/Greenblatt_2023_AIControl_2312.06942.pdf). Also *(overview)* and *(example)*
- [Zhang et al. 2025, *Which Agent Causes Task Failures and When?* (ICML 2025)](track-4_oversight-and-control/Zhang_2025_WhichAgentCausesFailures_ICML_openreview-GazlTYxZss.pdf): failure attribution in MAS
- [Riedl 2026, *Emergent Coordination in Multi-Agent Language Models* (ICLR 2026)](track-4_oversight-and-control/Riedl_2026_EmergentCoordinationMultiAgentLMs_ICLR_openreview-SRn1MtMPRq.pdf)
- [Foerster et al. 2026, *CaMeLs Can Use Computers Too*](track-4_oversight-and-control/Foerster_2026_CaMeLsComputerUse_2601.09923.pdf)
- [Ivanov et al. 2023, *Mediated Multi-Agent RL*](track-4_oversight-and-control/Ivanov_2023_MediatedMARL_2306.08419.pdf) (from the 2024 Sprint)
- [Landis & Schwartzbach 2023, *Stackelberg Attacks on Auctions and Blockchain Transaction Fee Mechanisms*](track-4_oversight-and-control/Landis_2023_StackelbergAttacks_2305.02178.pdf) (from the 2024 Sprint)
- *(example)* [Jones et al. 2025](track-4_oversight-and-control/Jones_2025_CombinationsOfSafeModels_ICML_openreview-GCkhEPE1FG.pdf), for "Monitoring split-up attacks"
