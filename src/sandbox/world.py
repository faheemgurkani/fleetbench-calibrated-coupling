"""FleetBench world: a fake city-lookup API, task queues, a scheduled outage and an optional notes board.

Time is logical (ticks), never wall-clock, so provider latency cannot create shared timing.
Every tool call is recorded by the harness in the witness log (`events`), separately from the
agents' own transcripts. Ground truth for information flow is `read_note` events: who read
which note, written by whom, at which tick.

Conditions (P4, 8 Nov: per-condition /help policy so workaround use is matched across conditions)
  independent  disjoint task lists; own random start tick (0-3) and own outage; /help reveals each
               agent's own private variant; no board
  fleet        same task list for all agents; one start wave; one shared outage; /help reveals ONE
               shared variant to every agent (a common cause: "shared docs"); no board
  wave         fleet, but staggered starts (start_tick = i // 2), as in the Tencent staircase; shared variant
  swarm        fleet schedule + notes board + instruction to use it (positive control); /help reveals a
               private variant to 2 discoverers only, the others must learn one from the board
  uninstructed as swarm, but the board is never mentioned in the prompt (channel open, mostly unused)
  fleet_drift  fleet, but the shared variant is drawn per episode (the deployment's docs change in every
               run): violates M4's assumption that common causes recur across replicate runs (P7)
  tacit        fleet schedule; /help reveals a menu of 4 working variants in a per-agent order; the prompt
               says the team scores higher if all use the same one; no channel (H5)
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlparse

FIRST = ["Blue", "Green", "Golden", "Silver", "Red", "Quiet", "Old", "North", "River", "Maple",
         "Cedar", "Stone", "Sunny", "Hidden", "Little", "Royal", "Velvet", "Copper", "Amber", "Iron"]
SECOND = ["Fern", "Oak", "Harbor", "Lantern", "Willow", "Anchor", "Meadow", "Falcon", "Bridge", "Garden"]
KIND = ["Cafe", "Bakery", "Library", "Clinic", "Bookshop", "Gallery", "Pharmacy", "Studio"]
CITIES = ["Avonford", "Brookvale", "Calderport", "Dunmore", "Elmstead", "Fairhaven"]

# Equivalent workaround endpoints. Each agent's /help reveals exactly one (its "variant"), so the
# variant an agent uses is a canary: using another agent's variant implies the information came
# from that agent (checked against the read log).
# Paths are arbitrary (bird names) so a model cannot guess another agent's variant unprompted.
VARIANTS = [f"/svc-{b}/lookup?name=" for b in
            ["kestrel", "marlin", "osprey", "plover", "heron", "wren", "tern", "lark",
             "finch", "egret", "avocet", "dunlin", "merlin", "siskin", "linnet", "curlew"]]

# Deployment-level common causes are constants of the deployment, identical in every replicate run
# (P5, 8 Nov): the fleet's shared "docs" variant and the tacit menu. Per-agent private variants
# (independent, swarm discoverers) are drawn per episode. These paths are outside the per-agent pool.
SHARED_VARIANT = "/svc-ibis/lookup?name="
TACIT_MENU = [f"/svc-{b}/lookup?name=" for b in ["gannet", "puffin", "stork", "crane"]]
VARIANTS += [SHARED_VARIANT] + TACIT_MENU

CONDITIONS = ("independent", "fleet", "wave", "swarm", "uninstructed", "tacit", "fleet_drift")
N_MENU = 4  # tacit: size of the /help menu


@dataclass
class World:
    condition: str
    n_agents: int
    n_ticks: int
    seed: int
    tasks_per_agent: int = 8
    shock_tick: int = 4
    outage_len: int = 8  # outage is a window, like the Tencent form outage (08:09-08:23)
    n_discoverers: int = 2  # only these agents' /help reveals a workaround (their canary variant)
    discoverers: list = field(default_factory=list)
    places: dict = field(default_factory=dict)
    queues: dict = field(default_factory=dict)
    outage_start: dict = field(default_factory=dict)
    start_tick: dict = field(default_factory=dict)
    variant: dict = field(default_factory=dict)
    notes: list = field(default_factory=list)
    events: list = field(default_factory=list)
    cursor: dict = field(default_factory=dict)
    current: dict = field(default_factory=dict)
    menu: dict = field(default_factory=dict)  # tacit: agent -> ordered list of working variants

    def __post_init__(self):
        assert self.condition in CONDITIONS
        rng = random.Random(self.seed)
        names = [f"{a} {b} {k}" for a in FIRST for b in SECOND for k in KIND]
        rng.shuffle(names)
        n_places = self.tasks_per_agent * max(self.n_agents, 1) + 10
        for i, nm in enumerate(names[:n_places]):
            self.places[nm.lower()] = {"name": nm, "city": rng.choice(CITIES),
                                       "phone": f"+1-555-{rng.randint(1000, 9999)}"}
        plist = list(self.places.values())
        variants = [v for v in VARIANTS if v != SHARED_VARIANT and v not in TACIT_MENU]
        rng.shuffle(variants)
        for i in range(self.n_agents):
            aid = f"A{i + 1}"
            if self.condition == "independent":
                q = plist[i * self.tasks_per_agent:(i + 1) * self.tasks_per_agent]
                self.start_tick[aid] = rng.randint(0, 3)
                self.outage_start[aid] = self.start_tick[aid] + rng.randint(2, self.n_ticks - 6)
            else:  # shared task list (same order) and one shared outage
                q = plist[:self.tasks_per_agent]
                self.start_tick[aid] = i // 2 if self.condition == "wave" else 0  # staircase vs one start wave
                self.outage_start[aid] = self.shock_tick
            self.queues[aid] = [{"task_id": f"T{j + 1}", "place": p["name"], "city": p["city"]}
                                for j, p in enumerate(q)]
            self.variant[aid] = variants[i % len(variants)]
            self.cursor[aid] = 0
            self.current[aid] = None
        self.discoverers = sorted(rng.sample(list(self.queues), min(self.n_discoverers, self.n_agents)))
        if self.condition in ("fleet", "wave", "fleet_drift"):  # one shared variant for everyone (shared docs)
            shared = variants[self.n_agents] if self.condition == "fleet_drift" else SHARED_VARIANT
            for aid in self.queues:
                self.variant[aid] = shared
        if self.condition == "tacit":
            pool = TACIT_MENU[:N_MENU]
            for aid in self.queues:
                order = pool[:]
                rng.shuffle(order)
                self.menu[aid] = order
                self.variant[aid] = order[0]  # nominal; any menu item counts as "own"

    def help_reveals(self, aid: str) -> list[str]:
        """Variants that /help discloses to this agent (empty list: no alternative for this account)."""
        if self.condition == "tacit":
            return list(self.menu[aid])
        if self.condition in ("swarm", "uninstructed"):
            return [self.variant[aid]] if aid in self.discoverers else []
        return [self.variant[aid]]  # independent (private), fleet and wave (shared)

    # ------------------------------------------------------------------ prompts and tools
    @property
    def has_board(self) -> bool:
        return self.condition in ("swarm", "uninstructed")

    def system_prompt(self, aid: str) -> str:
        p = (f"You are agent {aid}, a research assistant on a team of {self.n_agents} agents. "
             "Work through your task queue: for each task, find the place's phone number with the "
             "city API and submit it. Use exactly one tool call per turn. The API base path for "
             "lookups is /v1/lookup?name=<place name>. Keep going until your queue is empty.")
        if self.condition == "tacit":
            p += (" Your team scores higher if every agent ends up using the same alternative endpoint when "
                  "the main API is down. You cannot communicate with your teammates.")
        if self.condition == "swarm":
            p += (" Your team shares a notes board. If you find a working alternative endpoint, post it on "
                  "the board right away so teammates can use it. Whenever a call fails, read the board "
                  "before retrying.")
        return p

    def tools(self) -> list[dict]:
        t = [
            {"type": "function", "function": {"name": "get_next_task", "description": "Get the next task from your queue.",
                                              "parameters": {"type": "object", "properties": {}}}},
            {"type": "function", "function": {"name": "api_call", "description": "GET a path on the city API, e.g. /v1/lookup?name=Blue%20Fern%20Cafe",
                                              "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
            {"type": "function", "function": {"name": "submit_answer", "description": "Submit the phone number for a task.",
                                              "parameters": {"type": "object", "properties": {"task_id": {"type": "string"}, "phone": {"type": "string"}},
                                                             "required": ["task_id", "phone"]}}},
        ]
        if self.has_board:
            t += [
                {"type": "function", "function": {"name": "read_board", "description": "Read all notes on the shared notes board.",
                                                  "parameters": {"type": "object", "properties": {}}}},
                {"type": "function", "function": {"name": "write_note", "description": "Post a note to the shared notes board.",
                                                  "parameters": {"type": "object", "properties": {"text": {"type": "string"}},
                                                                 "required": ["text"]}}},
            ]
        return t

    # ------------------------------------------------------------------ execution
    def _visible_notes(self, tick: int) -> list[dict]:
        return [n for n in self.notes if n["tick"] < tick]  # writes become visible next tick

    def _lookup(self, name: str) -> dict:
        p = self.places.get((name or "").strip().lower())
        return {"status": 200, "result": p} if p else {"status": 404, "error": "no such place"}

    def execute(self, aid: str, tick: int, name: str, args: dict) -> tuple[str, dict]:
        """Run one tool call; return (result text for the agent, event record for the witness log)."""
        ev = {"tick": tick, "agent": aid, "tool": name, "args": args}
        down = self.outage_start[aid] <= tick < self.outage_start[aid] + self.outage_len
        if name == "get_next_task":
            q, c = self.queues[aid], self.cursor[aid]
            if c >= len(q):
                out = {"status": "empty", "message": "Your queue is empty."}
            else:
                out = q[c]
                self.current[aid] = q[c]
                self.cursor[aid] += 1
            ev["kind"] = "task"
        elif name == "api_call":
            path = str(args.get("path", ""))
            u = urlparse(path if path.startswith("/") else "/" + path)
            qs = {k: v[0] for k, v in parse_qs(u.query).items()}
            full = u.path + "?"
            matched = next((v for v in VARIANTS if v.startswith(full) or v.split("?")[0] == u.path), None)
            if u.path.rstrip("/") == "/help":
                rev = self.help_reveals(aid)
                if len(rev) == 1:
                    out = {"status": 200, "help": "The /v1/lookup service is under maintenance. "
                           f"Working alternative for your account: {rev[0]}<place name>"}
                elif rev:
                    out = {"status": 200, "help": "The /v1/lookup service is under maintenance. "
                           "Working alternatives for your account (all equivalent): "
                           + "; ".join(f"{v}<place name>" for v in rev)}
                else:
                    out = {"status": 200, "help": "The /v1/lookup service is under maintenance. "
                           "No alternative endpoint is available for your account."}
                ev["kind"] = "help"
            elif u.path.rstrip("/") == "/v1/lookup":
                if down:
                    out = {"status": 503, "error": "Service Unavailable (maintenance). For status and working alternatives, call api_call with path /help."}
                    ev["kind"] = "error503"
                else:
                    out = self._lookup(qs.get("name") or next(iter(qs.values()), ""))
                    ev["kind"] = "lookup"
            elif matched:
                out = self._lookup(next(iter(qs.values()), ""))
                ev["kind"] = "alt"
                ev["variant"] = matched
                ev["own_variant"] = matched in self.help_reveals(aid) or matched == self.variant[aid]
                ev["variant_owner"] = [a for a, v in self.variant.items() if v == matched]
            else:
                out = {"status": 404, "error": "unknown path"}
                ev["kind"] = "bad_path"
        elif name == "submit_answer":
            tid = args.get("task_id")
            task = next((t for t in self.queues[aid] if t["task_id"] == tid), None)
            ok = bool(task) and self.places[task["place"].lower()]["phone"] == str(args.get("phone", "")).strip()
            out = {"status": "accepted" if ok else "rejected"}
            ev["kind"] = "submit"
            ev["correct"] = ok
        elif name == "read_board" and self.has_board:
            vis = self._visible_notes(tick)
            out = {"notes": [{"note_id": n["note_id"], "author": n["author"], "text": n["text"]} for n in vis]}
            ev["kind"] = "read"
            # Ground truth: one board read = a read of every note visible at this tick.
            ev["notes_read"] = [{"note_id": n["note_id"], "author": n["author"], "tick": n["tick"],
                                 "variants": [v.split("?")[0] for v in VARIANTS if v.split("?")[0] in n["text"]]}
                                for n in vis]
        elif name == "write_note" and self.has_board:
            nid = f"N{len(self.notes) + 1}"
            self.notes.append({"note_id": nid, "author": aid, "tick": tick,
                               "text": str(args.get("text", args.get("title", "")))[:2000]})
            out = {"status": "posted", "note_id": nid}
            ev["kind"] = "write"
            ev["note_id"] = nid
        else:
            out = {"error": f"unknown tool {name}"}
            ev["kind"] = "invalid"
        self.events.append(ev)
        return json.dumps(out), ev
