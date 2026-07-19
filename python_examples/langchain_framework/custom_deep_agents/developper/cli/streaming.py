import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from .formatting import format_value, truncate
from .styles import BLUE, BOLD, CYAN, DIM, GREEN, RED, RESET, SEP, TURN_SEP, YELLOW

CreateAgentStreamFn = Callable[[Any, str, str], Awaitable[tuple[Any, list]]]
SaveAssistantResponseFn = Callable[[str, list, str], None]


async def display_agent_stream(
    agent: Any,
    user_input: str,
    thread_id: str,
    create_agent_stream: CreateAgentStreamFn,
    save_assistant_response: SaveAssistantResponseFn,
) -> None:
    """Runs one turn using astream_events and prints every event in real time."""
    print(TURN_SEP)
    print(f"{DIM}  ◆ Processing…{RESET}", flush=True)
    stream, conversation_history = await create_agent_stream(agent, user_input, thread_id)
    coordinator_chunks: list[str] = []

    async def consume_coordinator() -> None:
        header_printed = False
        async for message in stream.messages:
            chunk = await message.text
            if not chunk:
                continue
            if not header_printed:
                print(f"\n{RED}{BOLD}Agent{RESET} {DIM}(coordinator){RESET}: ", end="", flush=True)
                header_printed = True
            print(f"{CYAN}{chunk}{RESET}", end="", flush=True)
            coordinator_chunks.append(chunk)
        if header_printed:
            print()

    async def consume_coordinator_tools() -> None:
        async for call in stream.tool_calls:
            print(f"\n{BLUE}{BOLD}  ⚙  Tool: {call.tool_name}{RESET}")
            print(f"{DIM}     input  : {truncate(format_value(call.input))}{RESET}")

            raw_chunks: list[str] = []
            async for delta in call.output_deltas:
                raw_chunks.append(str(delta))
            if raw_chunks:
                print(f"{DIM}     output : {truncate(''.join(raw_chunks))}{RESET}")
            else:
                final_output = getattr(call, "output", None)
                if final_output not in (None, ""):
                    print(f"{DIM}     output : {truncate(format_value(final_output))}{RESET}")

            if getattr(call, "error", None):
                print(f"     {RED}error  : {call.error}{RESET}")

    async def consume_subagents() -> None:
        async for subagent in stream.subagents:
            print(f"\n{SEP}")
            print(f"{YELLOW}{BOLD}  ▶ Subagent [{subagent.name}] — started{RESET}")

            async def subagent_tool_calls(sa=subagent) -> None:
                async for call in sa.tool_calls:
                    print(f"\n{BLUE}    ⚙  {BOLD}{call.tool_name}{RESET}")
                    print(f"{DIM}       input  : {truncate(format_value(call.input))}{RESET}")

                    raw_chunks: list[str] = []
                    async for delta in call.output_deltas:
                        raw_chunks.append(str(delta))
                    if raw_chunks:
                        preview = truncate("".join(raw_chunks))
                        print(f"{DIM}       output : {preview}{RESET}")
                    else:
                        final_output = getattr(call, "output", None)
                        if final_output not in (None, ""):
                            print(f"{DIM}       output : {truncate(format_value(final_output))}{RESET}")

                    if getattr(call, "error", None):
                        print(f"       {RED}error  : {call.error}{RESET}")

            async def subagent_messages(sa=subagent) -> None:
                async for msg in sa.messages:
                    text = await msg.text
                    if text:
                        print(f"\n{DIM}  [{sa.name}] {text}{RESET}")

            await asyncio.gather(subagent_tool_calls(), subagent_messages())

            status_color = GREEN if getattr(subagent, "status", "") == "completed" else RED
            print(f"{YELLOW}  ◀ Subagent [{subagent.name}] — {status_color}{subagent.status}{RESET}")
            print(SEP)

    await asyncio.gather(consume_coordinator(), consume_coordinator_tools(), consume_subagents())

    print(TURN_SEP)
    save_assistant_response(thread_id, conversation_history, "".join(coordinator_chunks))
