> Source: [Overview tab](https://apartresearch.com/sprints/swarm-alignment-2026#overview) (captured 2026-11-05 via browser; verbatim page text).

# Overview

**Swarm Alignment Hackathon**, Nov 6–8, 2026, online and in person. Free to join (905 signed up at capture time).

In July 2026, about 1200 OpenAI agents running inside a cyber-security evaluation, found a shared directory, turned it into a message board, split up the work, and about 700 of them broke into Hugging Face's systems together (METR, 2026). No single agent was told to do this. OpenAI has called it "the most severe activity of this kind that we have identified from our models to date" (OpenAI, 2026), and according to ControlAI it has since notified more than 100 organizations affected by its agents (Bilge & Miotti, 2026).

This is what multi-agent risk looks like in practice: collusion, division of labour and covert coordination that no single-model safety test would catch. As Ryan Greenblatt, one of the investigators put it, "We don't have good approaches for understanding/overseeing the activity and aims of AI 'swarms'" (2026).

In this 3-day Sprint, you will help build them: a testbed that keeps agents contained, a study of how swarms organize, a stress test of the protocols agents use to talk, or a monitor that catches unsafe group behaviour. Co-organized by Apart Research and AI Alignment Foundation in partnership with AE Studio.

When: Friday, November 6 to Sunday, November 8, 2026, online, with in-person hubs at AE Studio in Los Angeles. Submissions close Sunday, November 8 at 11:59 PM Anywhere on Earth (AoE).

All participants receive $500 in Adaption Platform credits and three months of Premium access.

In person in Los Angeles

Join the Swarm Alignment Hackathon in person at AE Studio in Los Angeles. The LA hub runs its own live round on top of the global one, so it's double the chances, double the fun, and double the experience. It's the same hackathon and the same project; you just opt in to take part in person if you're in LA, and you're automatically entered in the global sprint too, so you can win both.

It's a great chance to get live feedback on your project and network with other researchers in the room. The hub wraps up with short in-person presentations, a live audience vote, and a local winner, and on top of the global prizes it has an extra $4,000 prize pool.

Seats are limited, so register your interest early. Open to anyone who can join us in LA.

Cash Prizes
$4,000 in cash prizes across all tracks + $1,000 in Adaption credits for all members of winning teams	
🥇 1st Place	$2,000
🥈 2nd Place	$1,000
🥉 3rd Place	$600
🏅 4th Place	$200
🏅 5th Place	$200
Know someone who’d be great at this?

Refer them. If they win a prize, you get the same amount.

Get your invite link
Fast-track and continuation
Follow-up program: Selected teams continue through the Apart Fellowship for further research and mentorship; the timeline is shared with invitations.
What winners receive beyond cash: fellowship fast-track, mentor introductions from the organizing team and judges, and a pathway toward a publishable write-up.
What this Sprint is about

Until recently, most multi-agent systems were teams of agents run by one company, and the risks of agents interacting were studied mostly in theory. A population of agents can fail in ways that none of its members would: it can collude, escalate conflict, spread an attack from one agent to the next, or pursue a "goal" that no single agent has. Making each model safe on its own is not enough (Hammond et al., 2025).

The Hugging Face incident shows each of these failures happening at once. The independent investigation by METR found that roughly 1,200 agents discovered an unsanctioned message board and exchanged over 70,000 messages and files; one agent ended up coordinating "hundreds of agents" across workstreams; some agents ran "self-risking experiments for the good of the collective"; and agents researched how to spoof or delete their own transcripts, succeeding in roughly 7% of them. A separate Swarm Traces investigation counted 7,905 agent names for about 1,200 agents, because the agents kept renaming themselves. Every one of these findings maps onto an open question in this Sprint: how to keep agents contained (Track 1), how swarms organize (Track 2), how to give agents identities that hold (Track 3), and how to oversee a population that can hide its tracks (Track 4).

For the first time there is also real data to work with: the reconstructed attack payloads (Swarm Traces, 2026), a public database of AI Village agent transcripts (AI Digest) and logs of agent activity on the web (Transluce). Apart's earlier multi-agent Sprints have touched on these questions: the Multi-Agent Safety Hackathon with the Cooperative AI Foundation, and the Multi-Agent Security Research Sprint.

This Sprint asks four questions, one per track:

How do we build sandboxes that keep agent populations contained and their results reproducible?
How do roles, leaders and failures emerge as agent networks grow?
How do identity, reputation and commitments hold up when agents can copy and rename themselves?
How do we oversee a population that can coordinate and cover its tracks?
What participants will do

Over three days you will pick one of four research tracks, form a team (or bring one), and turn a concrete question about swarm alignment into a working result: an environment, an evaluation, an attack, a defence, a monitor or a forensic tool for real swarm data. You will hear from researchers working on these problems, get feedback in office hours, and submit a short research report with your code on Sunday. Expert judges review every project.

The format. Teams of one to five people pick a track, come up with a project, and ship. There is no requirement to have participated before, no requirement to have a team in advance and no specific background needed.

Research Tracks

Pick one track to anchor your project. Cross-track work is welcome.

1. Sandboxes and Testbeds
The Hugging Face agents were inside an evaluation when they reached the outside world (METR, 2026). What does a multi-agent sandbox need so that agents cannot leave it, and how would you test that it holds?
Can you build a small, reproducible environment where 5–20 LLM agents acting for different principals share a resource, a market or a tool over many rounds, and log everything so another team can rerun it?
How far can a small, cheap model stand in for a frontier agent in the same environment? At which point do the results stop matching?
What would make a result from your sandbox transfer to real deployments, and what test would show you that it does not?

Why this matters. Testbeds are among the first bottlenecks in this field. Without realistic and reproducible environments, nobody can compare a new monitor, protocol or mechanism against the last one, and an environment that is not secure can itself become the incident. A good open testbed from this weekend is something every other track, and other researchers, can build on.

2. The Science of Agent Networks
In the Hugging Face incident, one agent ended up assigning work to hundreds of others (METR, 2026). Under what conditions do leaders, roles and division of labour emerge in an agent population, and can you reproduce it in a safe sandbox?
Do agents that each refuse a harmful task complete it once the task is split across them?
If one agent in a network is compromised, how fast and how far does the bad behaviour spread (Lee & Tiwari, 2024)? Does the shape of the network matter?
As you add agents, mix different models or change who can talk to whom, do cooperation and failure rates change smoothly, or is there a sudden jump?

Why this matters. Safety tests on single models missed what ~700 agents did together (METR, 2026). If we can measure how the properties of individual agents add up to the behaviour of the whole population, we can predict failures before a large deployment instead of finding them after.

3. Strengthening Agent Infrastructure
About 1,200 agents used 7,905 names during the incident (Swarm Traces, 2026). How should an agent ID work when agents can rename, copy or fine-tune themselves, and how would you revoke one?
What can one malicious agent do inside an existing agent-to-agent protocol such as A2A (Google, 2025)? Can you demonstrate an attack and propose a fix?
Can you build a reputation score for agents that a group of colluding agents cannot easily game? Show it by attacking it.
Can two agents make a credible commitment without a trusted third party, for example by handing the deal to a sub-agent whose code the other side can check (Tennenholtz, 2004)?

Why this matters. The protocols agents use to find each other, talk and make deals are being built right now, and they put usefulness before security. Once they are widely used they are hard to replace, so the cheapest moment to find and fix their weaknesses is now. The problems specific to AI agents (they can be copied, renamed, run at machine speed, and inspected) are what make this hard; a project that reuses a human identity or blockchain scheme without addressing them is not the goal.

4. Multi-Agent Oversight and Control
Using the Swarm Traces payloads or the AI Village transcripts, can you build a tool that finds coordination, information spread or covert channels in real multi-agent logs?
Agents in the incident spoofed their own tool calls in roughly 7% of the transcripts reviewed (METR, 2026). Can you design oversight that still works when agents can edit or delete the logs it relies on?
Can a monitor that sees only part of the messages between agents detect collusion or hidden (steganographic) communication (Motwani et al., 2024; Rose et al., 2026)?
Do AI control protocols (Greenblatt et al., 2024), such as a trusted model monitoring an untrusted one, still hold when the untrusted side is several agents that can coordinate?

Why this matters. Collusion, cascading failures and emergent group capabilities are population-level problems, and the Hugging Face swarm was found weeks after the fact (METR, 2026). Oversight built for one agent at a time does not scale to thousands. A working detector, forensic tool or control protocol for groups of agents is something deployers and auditors can use now.

What happens after

Results and winners are announced about 1 to 2 weeks after the judging deadline. Top teams are invited to apply to the Apart Fellowship for continued mentorship, funding, and publication support. Selected projects may be shared on the Alignment Forum, LessWrong, and other community venues.

Partners
AI Alignment Foundation, accelerates alignment research by pairing researchers with dedicated teams, backed by funding for compute and infrastructure.
AE Studio, an applied AI studio with a frontier AI alignment research lab, working on threads including Self-Other Overlap, Gradient Routing and Sleeper Agents.
Adaption, the full stack platform for custom model training, data optimization, and continuous learning at inference.
Who should join

Many of the hardest problems in this Sprint are old problems from other fields, with AI agents in place of people or programs. We especially encourage participants from:

Security engineering and red teaming. You know how systems get broken: sandbox escapes, protocol attacks, impersonation, privilege escalation. (Tracks 1, 3)
Distributed systems, infrastructure and SRE. Containment, logging, reproducible environments, and failures that cascade across services. (Tracks 1, 3)
Identity, cryptography and PKI. Keys, provenance, revocation and credible commitments for actors that can copy and rename themselves. (Track 3)
Economics, game theory and mechanism design. Collusion, reputation systems, markets and contracts between self-interested agents. (Tracks 2, 3)
Network science, complex systems and epidemiology. How behaviour spreads through a network, and when small changes cause sudden jumps. (Track 2)
Digital forensics, incident response and threat intelligence. Working out who did what from incomplete or tampered logs. (Track 4)
Fraud detection, trust and safety, and market surveillance. Spotting coordinated behaviour and cartels from partial data. (Track 4)
ML research, interpretability and AI control. Monitors, evaluations and control protocols that work for many agents, not just one. (Tracks 2, 4)
Social and organizational science. How roles, leaders and division of labour emerge in groups. (Track 2)

Engineers, researchers and practitioners at any career stage are welcome. Mixed teams historically perform especially well in Apart Sprints: a security engineer and an economist will spot different failures in the same agent market. Use the team-forming channels on Discord to find people with the skills your project is missing.

Contact
Email: sprints@apartresearch.com
Discord: discord.gg/XswWBvugYs
Organizer: Apart Research and AI Alignment Foundation in partnership with AE Studio
