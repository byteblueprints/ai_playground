import sys

from utils.colors import colorize

from .turn_context import TurnEventContext


def handle_subagent_reasoning_delta(
    text: str, namespace: tuple[str, ...], context: TurnEventContext
) -> None:
    if context.reasoning_active and context.reasoning_namespace != namespace:
        context.end_reasoning()
    if not context.reasoning_active:
        prefix = "\n" if (context.reasoning_started or context.answer_started) else ""
        status = context.reasoning_status("Reasoning Started", namespace)
        sys.stdout.write(f"{prefix}{status}\n")
        context.reasoning_active = True
        context.reasoning_namespace = namespace
        context.reasoning_started = True
    sys.stdout.write(colorize(text, "reasoning"))
    sys.stdout.flush()


def handle_subagent_text_delta(text: str, context: TurnEventContext) -> None:
    context.end_reasoning()
    sys.stdout.write(colorize(text, "subagent_output"))
    sys.stdout.flush()
