import sys
from dataclasses import dataclass, field

from utils.colors import colorize
from utils.thinking import ThinkingIndicator


@dataclass
class TurnEventContext:
    coordinator_chunks: list[str]
    printed_header: bool = False
    reasoning_active: bool = False
    reasoning_namespace: tuple[str, ...] | None = None
    reasoning_started: bool = False
    answer_started: bool = False
    thinking: ThinkingIndicator = field(
        default_factory=lambda: ThinkingIndicator(label="Assistant")
    )
    top_stack: list[tuple[str, str]] = field(default_factory=list)
    inner_tool_stacks: dict[tuple[str, ...], list[str]] = field(default_factory=dict)
    agent_names: dict[tuple[str, ...], str] = field(
        default_factory=lambda: {(): "coordinator"}
    )

    def start(self) -> None:
        self.thinking.start()

    def ensure_header(self) -> None:
        if not self.printed_header:
            self.thinking.stop(final_message="")
            self.printed_header = True

    def agent_name(self, namespace: tuple[str, ...]) -> str:
        if namespace in self.agent_names:
            return self.agent_names[namespace]
        if namespace:
            return namespace[-1].partition(":")[0]
        return "coordinator"

    def reasoning_status(self, label: str, namespace: tuple[str, ...]) -> str:
        name = self.agent_name(namespace)
        entity = "coordinator" if not namespace else "subagent"
        status = colorize(label, "reasoning_status", bold=True)
        identity = colorize(f"[agent:{name}]", entity, bold=True)
        return f"{status} {identity}"

    def end_reasoning(self) -> None:
        if self.reasoning_active and self.reasoning_namespace is not None:
            sys.stdout.write("\n")
            print(
                self.reasoning_status(
                    "Reasoning Completed", self.reasoning_namespace
                ),
                flush=True,
            )
            self.reasoning_active = False
            self.reasoning_namespace = None

    def finish(self, *, paused: bool = False) -> None:
        if self.printed_header:
            self.end_reasoning()
            self.thinking.stop(final_message="")
            sys.stdout.write("\n")
            sys.stdout.flush()
        elif paused:
            # Nothing was rendered yet and we're pausing for HITL review -
            # stay silent so the upcoming "Human review required" banner
            # isn't preceded by a misleading "done".
            self.thinking.stop(final_message="")
        else:
            self.thinking.stop(final_message="done")