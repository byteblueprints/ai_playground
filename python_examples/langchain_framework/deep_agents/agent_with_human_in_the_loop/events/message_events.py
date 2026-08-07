from typing import Any

from .coordinator_message_events import (
    handle_coordinator_reasoning_delta,
    handle_coordinator_text_delta,
)
from .subagent_message_events import (
    handle_subagent_reasoning_delta,
    handle_subagent_text_delta,
)
from .turn_context import TurnEventContext


def handle_message_event(
    data: list[Any] | tuple[Any, ...],
    namespace: tuple[str, ...],
    context: TurnEventContext,
) -> None:
    """Route each `messages` content-block-delta to the coordinator or subagent handler."""
    for payload in data:
        if not isinstance(payload, dict):
            continue
        if payload.get("event") != "content-block-delta":
            continue

        delta = payload.get("delta") or {}
        if not isinstance(delta, dict):
            continue

        delta_type = delta.get("type")
        if delta_type not in ("text-delta", "reasoning-delta"):
            continue

        text = (
            delta.get("reasoning")
            if delta_type == "reasoning-delta"
            else delta.get("text")
        )
        if not text:
            continue

        context.ensure_header()
        if delta_type == "reasoning-delta":
            if namespace:
                handle_subagent_reasoning_delta(str(text), namespace, context)
            else:
                handle_coordinator_reasoning_delta(str(text), context)
        elif not namespace:
            handle_coordinator_text_delta(str(text), context)
        else:
            handle_subagent_text_delta(str(text), context)