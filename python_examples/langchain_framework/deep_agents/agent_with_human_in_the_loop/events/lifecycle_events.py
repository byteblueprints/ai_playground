from typing import Any

from .turn_context import TurnEventContext


def handle_lifecycle_event(data: dict[str, Any], context: TurnEventContext) -> None:
    lifecycle_namespace = data.get("namespace")
    graph_name = data.get("graph_name")
    if isinstance(lifecycle_namespace, list) and isinstance(graph_name, str):
        context.agent_names[tuple(lifecycle_namespace)] = graph_name