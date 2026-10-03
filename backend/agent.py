"""Campus Customs shop agent: PydanticAI + gpt-5.6-luna through Portkey.

Loads its system prompt from prompts/prompt.md and has three tools (tools.py)
for looking up real catalogue/inventory data. Its structured output type
(ChatReply, models.py) always includes a text reply and, when relevant, a
list of product cards for the frontend to render.

Defaults to gpt-5.6-luna per the course's model policy (cheap/fast default;
upgrade to gpt-5.6-terra only where a task actually needs the extra power).
A single-turn shop Q&A agent like this doesn't need that extra power, so
Luna is used unconditionally here rather than switched per-request.

ChatDeps carries per-request context (who's chatting, what page they're on)
into the agent via PydanticAI's dependency-injection mechanism: it's passed
to run_sync(..., deps=...) and read by @agent.system_prompt functions below
via RunContext.deps. This keeps that context out of the conversation text
entirely — the model can't mistake it for something the customer typed, and
it can't "forget" to look it up the way it might forget to call a tool.
"""

import json
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from dotenv import load_dotenv  # noqa: E402
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.usage import UsageLimits

from db import fetch_product
from models import ChatReply, CustomerContext
from tools import check_size_stock, get_product_details, search_products

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROMPT_PATH = HERE / "prompts" / "prompt.md"
AUDIT_PATH = ROOT / "output" / "audit_trail.json"

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5.6-luna")
PORTKEY_BASE_URL = os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1").rstrip("/")

# One request per tool call in a chain (e.g. search_products, then
# get_product_details, then check_size_stock for a specific size), plus the
# final structured-output call — 8 leaves headroom without allowing a
# runaway loop.
RUN_USAGE_LIMITS = UsageLimits(request_limit=8)

MAX_AUDIT_FIELD_CHARS = 200  # keep args/result/message entries short and scannable

load_dotenv(ROOT / ".env")
load_dotenv(ROOT.parent / ".env")

_audit_lock = threading.Lock()


@dataclass
class ChatDeps:
    """Per-request context, not conversation text. See module docstring."""

    customer: Optional[CustomerContext]  # None for a guest (not logged in)
    current_product_id: Optional[str]  # product id if the customer is on a product detail page


_agent: Agent[ChatDeps, ChatReply] | None = None


def _build_agent() -> Agent[ChatDeps, ChatReply]:
    api_key = os.getenv("PORTKEY_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("PORTKEY_API_KEY is not set (put it in a .env file).")

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=PORTKEY_BASE_URL,
        default_headers={"x-portkey-api-key": api_key},
    )
    model = OpenAIChatModel(MODEL_NAME, provider=OpenAIProvider(openai_client=client))
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    agent: Agent[ChatDeps, ChatReply] = Agent(
        model,
        deps_type=ChatDeps,
        system_prompt=system_prompt,
        tools=[search_products, get_product_details, check_size_stock],
        output_type=ChatReply,
    )

    @agent.system_prompt
    def customer_context(ctx: RunContext[ChatDeps]) -> str:
        customer = ctx.deps.customer
        if customer is None:
            return "The current visitor is browsing as a guest (not logged in)."
        return (
            f"You are chatting with a logged-in customer: {customer.name} "
            f"(email: {customer.email}). You may use their first name naturally; "
            "don't recite their email back to them unprompted."
        )

    @agent.system_prompt
    def page_context(ctx: RunContext[ChatDeps]) -> str:
        product_id = ctx.deps.current_product_id
        if not product_id:
            return "The customer is not currently viewing a specific product page."
        product = fetch_product(product_id)
        if product is None:
            return "The customer is on a product page, but that product could not be loaded."
        return (
            f"The customer is RIGHT NOW looking at this exact product page: '{product['name']}' "
            f"(id: {product['product_id']}, a {product['garment_type']}, ${product['price']}). "
            "This current page is what 'this'/'it' refers to by default — it takes priority over "
            "whatever product came up earlier in the conversation, since that's the literal item "
            "in front of them right now. Only use an earlier-discussed product instead if the "
            "customer's message clearly names it or clearly continues that earlier topic."
        )

    return agent


def _get_agent() -> Agent[ChatDeps, ChatReply]:
    global _agent
    if _agent is None:
        _agent = _build_agent()
    return _agent


def _history_to_messages(history: list[dict]) -> list[ModelMessage]:
    """Convert stored chat_messages rows into PydanticAI message history.

    Only the text is replayed (not old product cards) — the point is
    conversational continuity ("what about in blue?" still makes sense),
    not re-attaching stale product data to a new reply.
    """
    messages: list[ModelMessage] = []
    for row in history:
        if row["role"] == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=row["content"])]))
        elif row["role"] == "assistant":
            messages.append(ModelResponse(parts=[TextPart(content=row["content"])]))
    return messages


def _build_prompt(message: str, deps: ChatDeps) -> str:
    """Prepend a page-context reminder directly onto the user's turn.

    The page_context system prompt alone wasn't enough in testing: when a
    logged-in customer had an older product discussed earlier in their
    replayed history, the model tended to keep answering about *that*
    product even on a different product's page, because system-prompt
    instructions are easily outweighed by what looks like an ongoing
    back-and-forth in the conversation itself. Restating the current page
    right next to the new message (the part of the prompt a model attends
    to most) fixes that, without polluting the stored message text — only
    the original `message` is ever saved to chat_messages.
    """
    if not deps.current_product_id:
        return message
    product = fetch_product(deps.current_product_id)
    if product is None:
        return message
    return (
        f"[Customer is currently on the page for: {product['name']} ({product['product_id']})]\n"
        f"{message}"
    )


def _truncate(value: object, limit: int = MAX_AUDIT_FIELD_CHARS) -> str:
    text = value if isinstance(value, str) else str(value)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _summarize_tool_result(value: object) -> str:
    """Turn a tool's return value into one short, readable line for the audit trail."""
    if value is None:
        return "not found"
    if isinstance(value, list):
        if not value:
            return "0 results"
        names = [getattr(item, "name", str(item)) for item in value[:3]]
        more = f", +{len(value) - 3} more" if len(value) > 3 else ""
        return _truncate(f"{len(value)} result(s): {', '.join(names)}{more}")
    # StockCheck/ChatReply-style models already carry a ready-made short message.
    message = getattr(value, "message", None)
    if isinstance(message, str):
        return _truncate(message)
    name = getattr(value, "name", None)
    if isinstance(name, str):
        return _truncate(f"found: {name}")
    return _truncate(value)


def _extract_tool_calls(result) -> list[dict]:
    """Pull every real tool call (name, short args, short result) out of this run.

    Excludes PydanticAI's internal 'final_result' pseudo-tool, which is just
    the mechanism for returning structured output, not a tool the agent chose
    to use.
    """
    pending: dict[str, tuple[str, str]] = {}
    calls: list[dict] = []
    for message in result.new_messages():
        for part in message.parts:
            if isinstance(part, ToolCallPart) and part.tool_name != "final_result":
                pending[part.tool_call_id] = (part.tool_name, _truncate(part.args))
            elif isinstance(part, ToolReturnPart) and part.tool_name != "final_result":
                name, args = pending.get(part.tool_call_id, (part.tool_name, ""))
                calls.append({"tool": name, "args": args, "result": _summarize_tool_result(part.content)})
    return calls


def _append_audit_entry(entry: dict) -> None:
    """Append one run's record to output/audit_trail.json — never truncated or
    overwritten between runs, so the file is a running history of every agent
    call. Writes to a temp file then renames, so a crash mid-write can't
    corrupt previously-recorded history; if the file is ever found corrupt
    anyway, it's backed up (not discarded) before starting a fresh list.
    """
    with _audit_lock:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        rows: list = []
        if AUDIT_PATH.exists() and AUDIT_PATH.stat().st_size > 0:
            try:
                loaded = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
                rows = loaded if isinstance(loaded, list) else [loaded]
            except json.JSONDecodeError:
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                AUDIT_PATH.replace(AUDIT_PATH.with_name(f"audit_trail.corrupt-{stamp}.json"))
        rows.append(entry)
        tmp_path = AUDIT_PATH.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp_path.replace(AUDIT_PATH)


def run_agent(
    message: str,
    deps: ChatDeps,
    history: list[dict] | None = None,
) -> ChatReply:
    """Run one turn of the shop chatbot and return its structured reply.

    `history` (prior chat_messages rows for a logged-in customer, oldest
    first) is replayed as message_history so the agent has real
    conversational memory across visits — not just a visual log the
    frontend redisplays. Guests always pass history=None.

    Every run appends one entry to output/audit_trail.json: time, who was
    chatting, the message, every tool call made (name, short args, short
    result), and how the run ended — regardless of whether it succeeded.
    """
    message_history = _history_to_messages(history) if history else None
    prompt = _build_prompt(message, deps)
    customer_label = f"{deps.customer.name} <{deps.customer.email}>" if deps.customer else "guest"
    entry = {
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "customer": customer_label,
        "message": _truncate(message),
        "tool_calls": [],
        "stop_reason": "",
    }
    try:
        result = _get_agent().run_sync(
            prompt,
            deps=deps,
            message_history=message_history,
            usage_limits=RUN_USAGE_LIMITS,
        )
        entry["tool_calls"] = _extract_tool_calls(result)
        entry["stop_reason"] = "completed"
        return result.output
    except Exception as exc:  # keep the chat widget alive even if the model/tool call fails
        # Logged server-side only — the raw exception can contain backend/model
        # details (e.g. which provider or model served the request) that
        # shouldn't be handed to the end user.
        detail = f"{type(exc).__name__}: {exc}"
        print(f"[agent] run_agent failed: {detail}")
        entry["stop_reason"] = _truncate(f"error: {detail}")
        return ChatReply(
            reply="Sorry, I hit an error answering that. Please try again in a moment.",
            products=[],
        )
    finally:
        _append_audit_entry(entry)
