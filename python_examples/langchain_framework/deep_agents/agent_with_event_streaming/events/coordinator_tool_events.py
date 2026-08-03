from typing import Any

from utils.colors import colorize

from .turn_context import TurnEventContext


def handle_coordinator_tool_started(
    data: dict[str, Any], context: TurnEventContext
) -> None:
    tool_name = str(data.get("tool_name"))
    tool_input = data.get("input") or {}

    if tool_name == "task":
        subagent_type = tool_input.get("subagent_type", "subagent")
        description = tool_input.get("description", "")
        context.top_stack.append(("task", subagent_type))
        context.ensure_header()
        status = colorize("Subagent Started", "subagent_status", bold=True)
        details = colorize(f"[subagent:{subagent_type}]", "subagent", bold=True)
        print(f"\n{status} {details}", flush=True)
        if description:
            print(colorize(str(description), "subagent_input"), flush=True)
    else:
        context.top_stack.append(("tool", tool_name))
        context.ensure_header()
        tool_input_display = {
            key: value for key, value in tool_input.items() if value not in (None, "")
        }
        status = colorize("Tool Started", "tool_status", bold=True)
        details = colorize(f"[tool:{tool_name}]", "tool")
        print(f"\n{status} {details}", flush=True)
        if tool_input_display:
            print(colorize(str(tool_input_display), "tool"), flush=True)


def handle_coordinator_tool_finished(context: TurnEventContext) -> None:
    if not context.top_stack:
        return

    entry_kind, name = context.top_stack.pop()
    context.ensure_header()
    if entry_kind == "task":
        status = colorize("Subagent Completed", "subagent_status", bold=True)
        details = colorize(f"[subagent:{name}]", "subagent", bold=True)
        print(f"\n{status} {details}", flush=True)
    else:
        status = colorize("Tool Completed", "tool_status", bold=True)
        details = colorize(f"[tool:{name}]", "tool")
        print(f"{status} {details}", flush=True)


def handle_coordinator_tool_error(
    data: dict[str, Any], context: TurnEventContext
) -> None:
    error = data.get("error")
    context.ensure_header()
    print(colorize(f"[tool] error: {error}", "error", bold=True), flush=True)
