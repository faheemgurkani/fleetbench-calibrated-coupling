"""Shared paths, model routes and the logged LLM client.

Pattern adapted from the prior sprint's `src/pipeline/common.py` (pre-existing work, AI Collusion
Research sprint, Oct 2026): every call is pinned to one OpenRouter provider (no fallbacks), carries
a fixed seed, and is appended to data/logs/calls.jsonl with tokens and cost. A hard budget cap
stops the run before spend exceeds BUDGET_CAP_USD.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LOGS = DATA / "logs"
RUNS = DATA / "runs"
for _p in (LOGS, RUNS):
    _p.mkdir(parents=True, exist_ok=True)

BUDGET_CAP_USD = float(os.environ.get("BUDGET_CAP_USD", "6.0"))

# Prices in $/M tokens (input, output), read from OpenRouter's endpoint list on 2026-11-07.
MODELS = {
    "gptoss120": {
        "model": "openai/gpt-oss-120b",
        "provider": {"order": ["PrimeIntellect"], "allow_fallbacks": False},
        "price": (0.019, 0.072),
        "extra": {"reasoning": {"effort": "low"}},
    },
    "gptoss120_deka": {
        "model": "openai/gpt-oss-120b",
        "provider": {"order": ["DekaLLM"], "allow_fallbacks": False},
        "price": (0.03, 0.18),
        "extra": {"reasoning": {"effort": "low"}},
    },
    "gemma27": {
        "model": "google/gemma-3-27b-it",
        "provider": {"order": ["DeepInfra"], "allow_fallbacks": False},
        "price": (0.08, 0.16),
        "extra": {},
    },
    "mistral24": {
        "model": "mistralai/mistral-small-3.2-24b-instruct",
        "provider": {"order": ["DeepInfra"], "allow_fallbacks": False},
        "price": (0.075, 0.20),
        "extra": {},
    },
}


def load_env() -> None:
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


load_env()
_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
_lock = threading.Lock()


class BudgetExceeded(RuntimeError):
    pass


def spent_usd() -> float:
    f = LOGS / "calls.jsonl"
    if not f.exists():
        return 0.0
    return sum(json.loads(l).get("cost_usd") or 0.0 for l in f.open())


def seed_for(*parts) -> int:
    """Deterministic 31-bit seed from any identifying parts (episode, agent, tick...)."""
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:8], 16) & 0x7FFFFFFF


def chat(route: str, messages: list[dict], *, purpose: str, meta: dict, seed: int,
         tools: list[dict] | None = None, temperature: float = 1.0, max_tokens: int = 1200,
         retries: int = 4):
    """One pinned, seeded, logged chat completion. Returns the OpenAI message object."""
    if spent_usd() > BUDGET_CAP_USD:
        raise BudgetExceeded(f"spend above cap ${BUDGET_CAP_USD}")
    spec = MODELS[route]
    body = {"provider": spec["provider"], "usage": {"include": True}, **spec["extra"]}
    kw = dict(model=spec["model"], messages=messages, temperature=temperature, seed=seed,
              max_tokens=max_tokens, extra_body=body)
    if tools:
        kw["tools"] = tools
        kw["tool_choice"] = "auto"
    err = None
    for attempt in range(retries):
        t0 = time.time()
        try:
            resp = _client.chat.completions.create(**kw)
            if not resp.choices:
                raise RuntimeError(f"empty choices: {getattr(resp, 'error', None)}")
            u = resp.usage
            pin, pout = (u.prompt_tokens or 0), (u.completion_tokens or 0)
            cost = getattr(u, "cost", None)
            if cost is None:
                cost = pin * spec["price"][0] / 1e6 + pout * spec["price"][1] / 1e6
            msg = resp.choices[0].message
            rec = {"t": time.time(), "route": route, "model": spec["model"],
                   "provider": getattr(resp, "provider", None), "purpose": purpose, **meta,
                   "seed": seed, "prompt_tokens": pin, "completion_tokens": pout,
                   "cost_usd": round(float(cost), 7), "latency_s": round(time.time() - t0, 2),
                   "finish": resp.choices[0].finish_reason}
            with _lock, open(LOGS / "calls.jsonl", "a") as f:
                f.write(json.dumps(rec) + "\n")
            return msg
        except BudgetExceeded:
            raise
        except Exception as e:  # noqa: BLE001  (network/provider errors: retry with backoff)
            err = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"chat failed after {retries} tries: {err}")
