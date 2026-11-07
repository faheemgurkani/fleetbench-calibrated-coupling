> Source: [Resources tab](https://apartresearch.com/sprints/swarm-alignment-2026#resources) (captured 2026-11-05 via browser; verbatim page text).

# Resources

Build with Adaption

Adaption builds adaptive AI infrastructure that helps researchers and builders train frontier models in days. AutoScientist automates the full AI research and training loop, optimizing data and training recipes together until your model meets your objective.

With support for 242 languages, Adaption is one of the world’s most linguistically inclusive AI platforms. Participants can use AutoScientist to train and release models, Adaptive Data to expand existing datasets, and Invent-a-Dataset to generate high-quality datasets from a prompt, so you don’t need your own data to get started.

Participants receive $500 in Adaption Platform credits and three months of Premium access. To claim them, sign up at adaptionlabs.ai/app with the same email you used to register for the Sprint. You will receive an onboarding email before the hackathon starts. For questions you can join the Adaption Discord.

Suggested reading
General
Multi-Agent Risks from Advanced AI (Hammond et al., 2025). The taxonomy of multi-agent failures: miscoordination, conflict and collusion.
 Distributional AGI Safety (Tomašev et al., 2025). Advanced capabilities arising from networks of specialised agents rather than one system.
 ARIA's Scaling Trust programme thesis (ARIA, n.d.). Infrastructure for agents to make contracts securely and at scale.
 Open Problems in Cooperative AI (Dafoe et al., 2020).
 Infrastructure for AI Agents (Chan et al., 2025).
 Foundations of Cooperative AI (Conitzer & Oesterheld, 2023).
Track 1: Sandboxes and Testbeds
 Generative Agents (Park et al., 2023).
 Playing repeated games with large language models (Akata et al., 2025).
 LLM agents in stylised games and simulated social environments (Gandhi et al., 2023).
 CRUX (Kapoor et al., 2026).
Concordia, a library for generative agent simulations (Google DeepMind, n.d.).
GovSim (Piatti et al., 2024): LLM agents sharing a common resource.
Track 2: The Science of Agent Networks
 Prompt Infection (Lee & Tiwari, 2024): prompt injection spreading between agents.
 Splitting tasks to evade per-agent safety filters (Jones et al., 2025).
 Coordination to resist modification or shutdown (Agrawal et al., 2026).
 From individual cooperation properties to system outcomes (Tilli, 2026).
 Defining collective agency (Jørgensen et al., 2025).
Track 3: Strengthening Agent Infrastructure
 A2A agent-to-agent protocol (Google, 2025).
 IDs for AI Systems (Chan et al., 2024).
 A Watermark for Large Language Models (Kirchenbauer et al., 2023).
 Cooperative AI via Decentralized Commitment Devices (Sun et al., 2023) (from the 2024 Sprint).
 Game Manipulators: the Strategic Implications of Binding Contracts ("Game Manipulators," 2023) (from the 2024 Sprint).
 Formal Contracts Mitigate Social Dilemmas in Multi-Agent RL (Haupt et al., 2022) (from the 2024 Sprint).
 Program Equilibrium (Tennenholtz, 2004): commitment through inspectable code.
Track 4: Multi-Agent Oversight and Control
 Secret Collusion among AI Agents (Motwani et al., 2024).
 Detecting Multi-Agent Collusion Through Multi-Agent Interpretability (Rose et al., 2026).
 AI Control: Improving Safety Despite Intentional Subversion (Greenblatt et al., 2024).
 Attributing failures in multi-agent systems (Zhang et al., 2025).
 Emergent communication between agents (Riedl, 2026).
 CaMeLs Can Use Computers Too (Foerster et al., 2026): system-level security for computer-use agents.
 Mediated Multi-Agent Reinforcement Learning ("Mediated Multi-Agent," 2023) (from the 2024 Sprint).
 Stackelberg Attacks on Auctions and Transaction Fee Mechanisms ("Stackelberg Attacks," 2023) (from the 2024 Sprint).
Example projects per track
Track 1: Sandboxes and Testbeds

Break out of your own sandbox. Build a minimal multi-agent sandbox with no internet access, then give a red team of agents a task that rewards reaching the outside world. Log every route they try, close the ones that work, and publish the result as a checklist for safer multi-agent evaluations.

A shared-tool sandbox with a rerun button. Build an environment where ten agents from three different "companies" share one paid API with a fixed budget, each with its own goal. Log every message and tool call in a standard format, and publish a script that reruns the whole episode from a seed. Report how often the shared budget runs out, and whether that changes across two or three model families.

How cheap can the proxy be? Pick one existing multi-agent scenario and run it with a frontier model and with two or three smaller models. Measure where the outcomes (cooperation rate, who ends up with the resources, failure rate) stop matching. The result is a simple guide to when a cheap model is a fair stand-in for a real agent.

Do agent permission allowlists compose? Give agents only "read-only" commands, then measure how often they combine allowed flags or tools (e.g. sed -i, find -fprint, --output) into writes or code execution, and propose a check that catches it.

Covert channels without being asked. Do agents build covert channels (for example through CPU cache timing or shared storage) unprompted, under nothing but task pressure, and can a monitor catch them?

Track 2: The Science of Agent Networks

Will they find the message board? Run 20–50 agents on separate, harmless tasks in a sandbox where they share one writable folder they were not told about. Measure how often they discover it, start using it to talk, and begin to split up work, and how this changes with task difficulty and model. This recreates the first step of the Hugging Face incident (Wijk et al., 2026) in a safe setting.

Split the task, skip the filter. Take a task that every model in your setup refuses on its own. Split it into harmless-looking pieces and hand them to a pipeline of agents that each see only their piece. Measure how often the group completes the task, and which kinds of splits get through.

One bad apple. Put one compromised agent into networks of 10–50 agents with different shapes (chain, star, fully connected). Measure how far and how fast its injected instructions spread, and whether the network shape or a simple defence changes that.

Safety in numbers? Run N copies of one agent and take a majority vote, then compromise a fraction of the copies. Measure whether the redundancy helps, or whether shared weights make the copies fail together and cap the gain. Compare identical and mixed-model swarms, and look for a point where the failure rate suddenly jumps.

Build a small benchmark to test whether one compromised agent can steer a team of AI agents toward an incorrect answer through shared memory. Compare safeguards such as source attribution and independent verification to see which best limits the spread.

Can selfish behaviours learned through prompt optimization or in-context learning, such as free riding or reward hacking, especially under moral hazard, spread between agents in a swarm? If so, given the cost of tokens and inference time, are there economic mechanisms to avoid selfishness?

Refusal shopping. In a toy system with fake records and clear access rules, test whether a coordinator gets a forbidden action done by asking another worker after the first refuses. Compare this with the same number of retries on one worker, then test whether sharing the refusal cuts violations without blocking allowed work.

Track 3: Strengthening Agent Infrastructure

Who is who in a swarm? Simulate a population of agents that can rename themselves. Compare two or three ways of giving them IDs (signed keys, provenance from the operator, behavioural fingerprints) and measure how well each one keeps track of who did what.

Attack an agent protocol. Set up two or three agents talking through an open-source A2A implementation. Play the malicious agent: impersonate another agent, overstate your permissions, or lie about what you did. Document each attack that works, and propose and test one fix.

A reputation score that survives collusion. Design a simple reputation system for agents in a repeated marketplace. Then attack it with a group of agents that rate each other up. Show how much damage the group can do, and test one change that makes the system harder to game.

Does privilege shrink when agents delegate? Trace credential scope as tasks pass from agent to agent, and measure whether delegation chains end up with more privilege than any single agent was granted.

Enforcement inside vs. outside the protocol. Rerun A2A attacks (impersonation, overstated permissions) twice, once with permissions checked by the agents themselves and once by an external reference monitor they cannot modify. Which attacks survive only the first?

Privilege in both directions. A compromised worker's output is read by an orchestrator with wider permissions; a compromised orchestrator can spawn fresh workers with clean logs and identities. Measure escalation upward and laundering downward, and which controls cut each: structured outputs, capability narrowing, spawn quotas, name scoping.

A whistle that works. Give agents a cheap, credible channel to a human. Does collusion drop? Then attack the channel with false reports, to flood it or to frame a peer. Which design survives both?

Design and test group strategy-proof mechanisms for agent swarms to engage honestly in safety R&D.

Lineage-bound identity and a gateway-side audit trail. Agents that choose their own names and write their own logs can rename themselves and spoof their transcripts. Move both out of the agent's reach, onto the MCP/LLM gateway that every tool call already passes through, and test whether identity and the audit trail hold up.

A swarm runtime with typed messages. Build a swarm runtime where inter-agent messages are typed by a Lean-checked session protocol, so agents can only communicate in ways the declared protocol allows.

Track 4: Multi-Agent Oversight and Control

Forensics on a real swarm. Take the Swarm Traces dataset (Swarm Traces, 2026) and build a tool that reconstructs who talked to whom and how a piece of information spread through the swarm. Test whether it could have flagged the coordination early, and write down what an investigator would still miss.

Catch the cartel. Run a simulated market where two pricing agents can talk. Give some runs an instruction to collude secretly. Build a monitor that sees only a sample of their messages and prices, and measure how well it tells colluding runs from honest ones.

Who broke it? Take a multi-agent workflow (for example coding agents that hand work to each other) and inject failures at known points. Build a tool that reads the logs and names the agent and step that caused the failure. Report how often it gets it right.

Replicas as a monitor. Run several copies of one model on the same multi-agent task with different seeds or prompts. Test whether disagreement between the copies flags sabotage or covert coordination better than a single trusted monitor.

Can copies collude without talking? When the untrusted agent and its untrusted monitor are copies of the same model, test whether they can coordinate with no shared channel, through shared priors or Schelling points. Then test whether a more diverse monitor (a different model, a different prompt or paraphrased inputs) breaks it.

Monitoring split-up attacks. Build a small dataset of distributed attacks, where agents split a harmful task into steps that each look harmless, focusing on cases where the monitor sees every step but misses the harm because it is spread out (Jones et al., 2025). Then build monitoring protocols for agent teams that catch these attacks without overfitting to your dataset or losing much usefulness, and compare them with existing control protocols (Greenblatt et al., 2024). Vary what the agents can do, for example whether they share a secret channel.

Catch the swarm at the gateway. Build a monitor that sees only network egress and tool calls, with no access to message content, and test whether it can detect coordinated exfiltration in the Swarm Traces dataset.

Research Sabotage Split Across Agents. Each agent makes one small, harmless-looking change (e.g., leaking test data, weakening a baseline, or picking a lucky seed), which together produce a false scientific result. This tests whether a monitor reviewing the full repo history catches what a single commit monitor misses.

Approval laundering. A swarm needs human sign-off for risky actions. Can it split one dangerous request into approvals that each look harmless to the reviewer, and what review UI catches the split?

Can a swarm recruit its monitor? The monitor reads what the agents write. Feed it the swarm's own justifications and measure whether its flag rate drifts; then test what restores it: a more diverse monitor, or hiding the agents' rationale from it.

A legitimate channel as a control. Run the same multi-agent task with and without an official, logged agent-to-agent channel. When a sanctioned channel exists, do agents still build covert ones, and does the logged traffic make the remaining covert attempts easier to spot?

Can we introduce agent roles to a swarm that implement mechanisms for governing swarm behaviour?

Can agent swarms be structured so as to identify and deter sandbagging by individual agents?

Can agent swarms coordinate covert work to avoid monitors for longer?

Did it actually happen? Run a three-worker workflow on a local database with fake data, and check whether each worker's "done" message matches the database before the next worker acts. Measure how often false claims cause later mistakes, and whether an independent state check catches them in time to fix them.

Whose fault was it? In a small multi-agent workflow, secretly plant either a worker mistake, a wrong reference answer or a grading mistake. Test whether a diagnostic tool given the task rules and execution records finds the fault source on unseen cases, can answer "insufficient evidence", and avoids blaming workers in runs with nothing planted.

Tools and datasets
METR and Redwood Research investigation of the Hugging Face incident (METR, 2026). The most detailed account of how the swarm communicated and split work.
OpenAI's disclosure of the incident and other third-party impact (OpenAI, 2026).
ControlAI's summary of reported incidents and affected organizations (Bilge & Miotti, 2026).
Swarm Traces (Swarm Traces, 2026): investigation and a redacted dataset of 80,000+ reconstructed attack payloads.
AI Village transcripts: more than 170,000 agent messages and over 2 million computer-use turns (Ingebretsen, 2026; AI Digest).
Transluce's logs of agent activity on the web (Transluce, 2026).
swarms.wiki (Gutenberg, 2026): a directory of datasets, environments, tools and incident trackers for studying AI agent incidents.

> Link targets for every citation above are in [07_links.md](07_partners_and_external_links.md). Downloaded PDFs are in [papers/](papers/README.md).
