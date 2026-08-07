from typing import Any

from .coordinator_tool_events import (
    handle_coordinator_tool_error,
    handle_coordinator_tool_finished,
    handle_coordinator_tool_started,
)
from .subagent_tool_events import (
    handle_subagent_tool_error,
    handle_subagent_tool_finished,
    handle_subagent_tool_started,
)
from .turn_context import TurnEventContext


def handle_tool_event(
    data: dict[str, Any],
    namespace: tuple[str, ...],
    context: TurnEventContext,
) -> None:
    """Route a single `tools` event to the coordinator or subagent handler."""
    kind = data.get("event")
    is_top_level = not namespace
    context.end_reasoning()

    if kind == "tool-started":
        if is_top_level:
            handle_coordinator_tool_started(data, context)
        else:
            handle_subagent_tool_started(data, namespace, context)
    elif kind == "tool-finished":
        if is_top_level:
            handle_coordinator_tool_finished(context)
        else:
            handle_subagent_tool_finished(namespace, context)
    elif kind == "tool-error":
        if is_top_level:
            handle_coordinator_tool_error(data, context)
        else:
            handle_subagent_tool_error(data, context)