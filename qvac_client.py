"""Local QVAC client: Qwen3 4B with a small tool-calling loop.

Verified against this SDK version with qvac_probe.py:
- tools use the flat format {name, description, parameters}
- load_model(model_src=..., model_config={"ctx_size": ..., "tools": True})
- tool calls arrive as events with type "toolCall": event.call.name / event.call.arguments.root
"""
import asyncio
import json
import re

from tetherto.qvac_sdk import Client, completion, load_model, unload_model
from tetherto.qvac_sdk.models import QWEN3_4B_INST_Q4_K_M

MODEL = QWEN3_4B_INST_Q4_K_M
MODEL_CONFIG = {"ctx_size": 4096, "tools": True}
MAX_ROUNDS = 5


def _clean(text: str) -> str:
    """Remove Qwen3's <think>...</think> reasoning block."""
    text = text or ""
    if "</think>" in text:
        text = text.split("</think>")[-1]
    text = re.sub(r"<think>.*", "", text, flags=re.DOTALL)
    return text.strip()


async def _round(transport, model_id, history, tools):
    kwargs = {"model_id": model_id, "history": history}
    if tools:
        kwargs["tools"] = tools
    run = completion(transport, **kwargs)
    text, calls = "", []
    async for event in run.events:
        if event.type == "contentDelta":
            text += event.text
        elif event.type == "toolCall":
            args = event.call.arguments
            args = getattr(args, "root", args)
            calls.append({
                "name": event.call.name,
                "arguments": dict(args or {}),
                "raw": getattr(event.call, "raw", "") or "",
            })
    return text, calls


async def _agent(system: str, question: str, tools: list, execute):
    trace = []
    async with Client() as client:
        t = client.transport
        model_id = await load_model(t, model_src=MODEL, model_config=MODEL_CONFIG)
        try:
            history = [
                {"role": "system", "content": system},
                {"role": "user", "content": question},
            ]
            for _ in range(MAX_ROUNDS):
                text, calls = await _round(t, model_id, history, tools)
                if not calls:
                    return _clean(text), trace

                history.append({
                    "role": "assistant",
                    "content": "\n".join(
                        c["raw"] or json.dumps({"name": c["name"], "arguments": c["arguments"]})
                        for c in calls
                    ),
                })
                lines = []
                for c in calls:
                    try:
                        result = execute(c["name"], c["arguments"])
                    except Exception as error:  # report the problem to the model
                        result = {"error": str(error)}
                    trace.append({"name": c["name"], "arguments": c["arguments"], "result": result})
                    lines.append(f"{c['name']}({json.dumps(c['arguments'])}) returned: {json.dumps(result)}")
                history.append({
                    "role": "user",
                    "content": "Tool results:\n" + "\n".join(lines)
                    + "\nNow answer the student's original question using these results.",
                })

            # Too many tool rounds: force a final answer without tools.
            text, _ = await _round(t, model_id, history, None)
            return _clean(text), trace
        finally:
            await unload_model(t, model_id)


def run_agent(system: str, question: str, tools: list, execute):
    """Run the model with tools. Returns (answer_text, tool_trace)."""
    return asyncio.run(_agent(system, question, tools, execute))


async def _ask_qvac(prompt: str) -> str:
    text, _ = await _agent_plain(prompt)
    return text


async def _agent_plain(prompt: str):
    async with Client() as client:
        t = client.transport
        model_id = await load_model(t, model_src=MODEL, model_config=MODEL_CONFIG)
        try:
            text, _ = await _round(t, model_id, [{"role": "user", "content": prompt}], None)
            return _clean(text), []
        finally:
            await unload_model(t, model_id)


def get_qvac_recommendation(prompt: str) -> str:
    """Single prompt, no tools (used by the legacy purchase explanation)."""
    return asyncio.run(_ask_qvac(prompt))