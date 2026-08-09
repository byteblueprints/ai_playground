from typing import Any

from .lifecycle_events import handle_lifecycle_event
from .message_events import handle_message_event
from .tool_events import handle_tool_event
from .turn_context import TurnEventContext


def consume_turn_events(stream: Any, coordinator_chunks: list[str]) -> TurnEventContext:
    """Consume the raw v3 event stream for a single (possibly paused) segment.

    Renders the coordinator's own streamed text live, and clearly marks
    subagent invocations (start, live streamed text, and the final
    "reporting back" hand-off) as they occur.

    Everything here is derived directly from the raw event stream. The
    higher-level `stream.messages` / `.tool_calls` / `.subagents`
    projections are only populated while they are the ones actively
    driving iteration - once the raw stream has been drained elsewhere
    they come back empty, so we don't rely on them.

    Returns the context without finishing it: the stream can end either
    because the turn is truly done or because it paused on an interrupt,
    and only the caller knows which (via the graph state) - so it decides
    when/how to call `context.finish(paused=...)`.
    """
    context = TurnEventContext(coordinator_chunks)
    context.start()

    for event in stream:
        if not isinstance(event, dict):
            continue

        method = event.get("method")
        params = event.get("params") or {}
        namespace = params.get("namespace") or []
        data = params.get("data")
        namespace_key = tuple(namespace)

        if method == "lifecycle" and isinstance(data, dict):
            handle_lifecycle_event(data, context)
        elif method == "tools" and isinstance(data, dict):
            handle_tool_event(data, namespace_key, context)
        elif method == "messages" and isinstance(data, (list, tuple)):
            handle_message_event(data, namespace_key, context)

    return context
