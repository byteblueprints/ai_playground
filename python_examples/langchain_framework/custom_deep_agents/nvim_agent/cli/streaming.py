import asyncio
from typing import Any, Awaitable, Callable

from .formatting import (
    extract_assistant_text_from_output,
    extract_text_from_chunk,
    format_value,
    truncate,
)
from .styles import BLUE, CYAN, DIM, RED, RESET, TURN_SEP

CreateAgentStreamFn = Callable[[Any, str, str], Awaitable[tuple[Any, list]]]
SaveAssistantResponseFn = Callable[[str, list, str], None]


async def display_agent_stream(
    agent: Any,
    user_input: str,
    thread_id: str,
    create_agent_stream: CreateAgentStreamFn,
    save_assistant_response: SaveAssistantResponseFn,
) -> None:
    print(TURN_SEP)
    print(f"{DIM}  processing...{RESET}", flush=True)

    stream_obj, conversation_history = await create_agent_stream(agent, user_input, thread_id)

    assistant_chunks: list[str] = []
    assistant_header_printed = False
    fallback_assistant_text = ""

    def print_assistant_chunk(text: str) -> None:
        nonlocal assistant_header_printed
        if not text:
            return
        if not assistant_header_printed:
            print(f"\n{RED}Agent{RESET}: ", end="", flush=True)
            assistant_header_printed = True
        print(f"{CYAN}{text}{RESET}", end="", flush=True)
        assistant_chunks.append(text)

    async def consume_deep_stream(stream: Any) -> None:
        async def consume_messages() -> None:
            async for message in stream.messages:
                chunk = await message.text
                if chunk:
                    print_assistant_chunk(chunk)

        async def consume_tool_calls() -> None:
            async for call in stream.tool_calls:
                print(f"\n{BLUE}Tool{RESET}: {call.tool_name}")
                print(f"{DIM}  input : {truncate(format_value(call.input))}{RESET}")

                raw_chunks: list[str] = []
                async for delta in call.output_deltas:
                    raw_chunks.append(str(delta))

                if raw_chunks:
                    print(f"{DIM}  output: {truncate(''.join(raw_chunks))}{RESET}")
                else:
                    final_output = getattr(call, "output", None)
                    if final_output not in (None, ""):
                        print(f"{DIM}  output: {truncate(format_value(final_output))}{RESET}")

                if getattr(call, "error", None):
                    print(f"{RED}  error : {call.error}{RESET}")

        await asyncio.gather(consume_messages(), consume_tool_calls())

    async def consume_raw_event_stream(event_stream: Any) -> None:
        nonlocal fallback_assistant_text

        async for event in event_stream:
            if not isinstance(event, dict):
                continue

            event_name = event.get("event", "")
            data = event.get("data", {}) or {}

            if event_name == "on_chat_model_stream":
                text = extract_text_from_chunk(data.get("chunk"))
                if text:
                    print_assistant_chunk(text)

            elif event_name == "on_tool_start":
                tool_name = event.get("name", "tool")
                tool_input = data.get("input", data)
                print(f"\n{BLUE}Tool{RESET}: {tool_name}")
                print(f"{DIM}  input : {truncate(format_value(tool_input))}{RESET}")

            elif event_name == "on_tool_end":
                tool_output = data.get("output", data)
                print(f"{DIM}  output: {truncate(format_value(tool_output))}{RESET}")

            elif event_name == "on_chain_end":
                output = data.get("output")
                if output is not None:
                    extracted = extract_assistant_text_from_output(output)
                    if extracted:
                        fallback_assistant_text = extracted

    if hasattr(stream_obj, "messages") and hasattr(stream_obj, "tool_calls"):
        await consume_deep_stream(stream_obj)
    elif hasattr(stream_obj, "__aiter__"):
        await consume_raw_event_stream(stream_obj)
    else:
        raise RuntimeError("Unsupported stream object returned by create_agent_stream")

    if assistant_header_printed:
        print()

    assistant_text = "".join(assistant_chunks).strip() or fallback_assistant_text.strip()
    save_assistant_response(thread_id, conversation_history, assistant_text)

    print(TURN_SEP)
