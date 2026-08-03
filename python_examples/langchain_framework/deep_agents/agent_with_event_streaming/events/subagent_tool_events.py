from typing import Any

from utils.colors import colorize

from .turn_context import TurnEventContext


def handle_subagent_tool_started(
    data: dict[str, Any],
    namespace: tuple[str, ...],
    context: TurnEventContext,
) -> None:
    tool_name = str(data.get("tool_name"))
    tool_input = data.get("input") or {}

    context.inner_tool_stacks.setdefault(namespace, []).append(tool_name)
    context.ensure_header()
    tool_input_display = {
        key: value for key, value in tool_input.items() if value not in (None, "")
    }
    status = colorize("Tool Started", "tool_status", bold=True)
    details = colorize(f"[tool:{tool_name}]", "subagent")
    print(f"  {status} {details}", flush=True)
    if tool_input_display:
        print(colorize(f"  {tool_input_display}", "subagent"), flush=True)


def handle_subagent_tool_finished(
    namespace: tuple[str, ...], context: TurnEventContext
) -> None:
    stack = context.inner_tool_stacks.get(namespace)
    if not stack:
        return

    tool_name = stack.pop()
    context.ensure_header()
    status = colorize("Tool Completed", "tool_status", bold=True)
    details = colorize(f"[tool:{tool_name}]", "subagent")
    print(f"  {status} {details}", flush=True)


def handle_subagent_tool_error(
    data: dict[str, Any], context: TurnEventContext
) -> None:
    error = data.get("error")
    context.ensure_header()
    print(colorize(f"  [tool] error: {error}", "error", bold=True), flush=True)
