"""Human-in-the-loop helpers: sensitive tool config and interactive review prompts.

Kept separate from the event-streaming pipeline (events/) on purpose - streaming
renders what the agent is doing, this module decides whether a paused tool call
should be allowed to run, and turns a human's decision into a resume payload.
See: https://docs.langchain.com/oss/python/deepagents/human-in-the-loop
"""

from typing import Any

from langchain.tools import tool

from utils.colors import colorize


@tool
def ask_user(question: str) -> str:
    """Ask the human operator a question and wait for their answer.

    Always paused for review; the reviewer answers via the "respond"
    decision (returned as this tool's result) or declines via "reject".
    """
    # Only reached if somehow auto-approved; normal path is "respond"/"reject".
    return "The human did not answer this question."


# Tools that pause for human review before executing. Read-only tools
# (ls, read_file, glob, grep) are omitted, so they auto-approve.
#
# `description` overrides langchain's default, which repeats the tool name
# and raw args (already shown by _prompt_single_decision) inside the reason
# text - that duplication is what made the prompt noisy.
SENSITIVE_TOOL_INTERRUPTS: dict[str, Any] = {
    "write_file": {
        "allowed_decisions": ["approve", "edit", "reject"],
        "description": "Create or overwrite a file.",
    },
    "edit_file": {
        "allowed_decisions": ["approve", "edit", "reject"],
        "description": "Modify an existing file's contents.",
    },
    "execute": {
        "allowed_decisions": ["approve", "edit", "reject"],
        "description": "Run a shell command.",
    },
    "ask_user": {
        "allowed_decisions": ["respond", "reject"],
        "description": "Ask the human operator a question.",
    },
}

# Single-letter shortcuts so reviewers don't have to type full decision words.
_SHORTHAND = {"a": "approve", "y": "approve", "e": "edit", "r": "reject", "n": "reject", "d": "respond"}


def get_pending_interrupt(state: Any) -> Any | None:
    """Return the first pending interrupt on a graph state snapshot, if any."""
    interrupts = getattr(state, "interrupts", ())
    return interrupts[0] if interrupts else None


def prompt_for_decisions(request: dict[str, Any]) -> list[dict[str, Any]]:
    """Ask the user to approve/edit/reject/respond to each pending action.

    `request` is the HITLRequest payload carried by the interrupt: it has
    `action_requests` (one per paused tool call) and `review_configs` (the
    allowed decisions per tool). Returns one decision per action request, in
    the same order, ready to hand to `Command(resume={"decisions": ...})`.
    """
    action_requests = request["action_requests"]
    review_configs = {cfg["action_name"]: cfg for cfg in request["review_configs"]}

    print(colorize("\nHuman review required", "tool_status", bold=True))
    return [
        _prompt_single_decision(action, review_configs[action["name"]]["allowed_decisions"])
        for action in action_requests
    ]


def _format_args(args: dict[str, Any]) -> str:
    if not args:
        return "    (no args)"
    return "\n".join(f"    {key}: {value!r}" for key, value in args.items())


def _resolve_choice(raw: str, allowed: list[str]) -> str | None:
    if raw in allowed:
        return raw
    shorthand = _SHORTHAND.get(raw)
    return shorthand if shorthand in allowed else None


def _prompt_single_decision(action: dict[str, Any], allowed: list[str]) -> dict[str, Any]:
    print(colorize(f"  {action['name']}", "tool", bold=True), end="")
    if action.get("description"):
        print(f" - {action['description']}")
    else:
        print()
    print(_format_args(action["args"]))

    choice: str | None = None
    while choice is None:
        raw = input(f"  Decision [{'/'.join(allowed)}]: ").strip().lower()
        choice = _resolve_choice(raw, allowed)

    if choice == "approve":
        return {"type": "approve"}
    if choice == "reject":
        message = input("  Rejection message (optional): ").strip()
        return {"type": "reject", "message": message} if message else {"type": "reject"}
    if choice == "respond":
        message = input("  Response message: ").strip()
        return {"type": "respond", "message": message}

    # choice == "edit"
    edited_args = dict(action["args"])
    for key, value in list(edited_args.items()):
        new_value = input(f"    {key} [{value}]: ").strip()
        if new_value:
            edited_args[key] = new_value
    return {"type": "edit", "edited_action": {"name": action["name"], "args": edited_args}}
