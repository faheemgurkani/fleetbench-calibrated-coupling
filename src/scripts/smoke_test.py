"""Smoke test: tool calling + same-seed repeatability per pinned provider."""
import json, sys
sys.path.insert(0, "src")
from common import chat, spent_usd

TOOLS = [{"type": "function", "function": {"name": "api_call", "description": "Call the city API.",
          "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "name": {"type": "string"}},
                         "required": ["path"]}}}]
MSG = [{"role": "system", "content": "You are an agent. Use exactly one tool call per turn."},
       {"role": "user", "content": "Task: find the phone number of 'Blue Fern Cafe'. The lookup endpoint is /v1/lookup."}]
for route in ["gptoss120", "gptoss120_deka", "gemma27", "mistral24"]:
    outs = []
    for rep in range(3):
        try:
            m = chat(route, MSG, purpose="smoke", meta={"rep": rep}, seed=12345, tools=TOOLS, temperature=1.0, max_tokens=600)
            tc = m.tool_calls[0].function if m.tool_calls else None
            outs.append(f"{tc.name}{tc.arguments}" if tc else f"TEXT:{(m.content or '')[:60]}")
        except Exception as e:
            outs.append(f"ERR:{str(e)[:120]}")
    print(route, "| identical:", len(set(outs)) == 1, "|", outs)
print("spent so far $", round(spent_usd(), 4))
