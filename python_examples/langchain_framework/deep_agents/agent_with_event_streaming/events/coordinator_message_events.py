import sys

from utils.colors import colorize

from .turn_context import TurnEventContext

# The coordinator's own reasoning/text always runs at the empty namespace.
_COORDINATOR_NAMESPACE: tuple[str, ...] = ()


def handle_coordinator_reasoning_delta(text: str, context: TurnEventContext) -> None:
    if context.reasoning_active and context.reasoning_namespace != _COORDINATOR_NAMESPACE:
        context.end_reasoning()
    if not context.reasoning_active:
        prefix = "\n" if (context.reasoning_started or context.answer_started) else ""
        status = context.reasoning_status("Reasoning Started", _COORDINATOR_NAMESPACE)
        sys.stdout.write(f"{prefix}{status}\n")
        context.reasoning_active = True
        context.reasoning_namespace = _COORDINATOR_NAMESPACE
        context.reasoning_started = True
    sys.stdout.write(colorize(text, "reasoning"))
    sys.stdout.flush()


def handle_coordinator_text_delta(text: str, context: TurnEventContext) -> None:
    context.end_reasoning()
    if not context.answer_started:
        prefix = "\n" if context.reasoning_started else ""
        sys.stdout.write(colorize(f"{prefix}Assistant: ", "coordinator", bold=True))
        context.answer_started = True
    sys.stdout.write(colorize(text, "coordinator"))
    sys.stdout.flush()
    context.coordinator_chunks.append(text)
