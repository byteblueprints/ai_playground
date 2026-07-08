import asyncio
import os
import uuid
from contextlib import AsyncExitStack
from pathlib import Path


if "WORKSPACE_ROOT" not in os.environ and "DEEP_AGENT_WORKSPACE_ROOT" not in os.environ:
    os.environ["WORKSPACE_ROOT"] = str((Path(__file__).resolve().parents[1] / "file_system_root").resolve())

from deep_agent import (
    create_agent_stream,
    create_custom_deep_agent,
    save_assistant_response,
)

from .streaming import display_agent_stream
from .styles import GREEN, RESET


async def run_application() -> None:
    thread_id = str(uuid.uuid4())
    print(f"Session thread ID: {thread_id}")
    print("Chat started. Press Ctrl+C to exit.\n")

    try:
        async with AsyncExitStack() as exit_stack:
            agent = await create_custom_deep_agent(exit_stack)
            while True:
                user_input = (await asyncio.to_thread(input, f"{GREEN}You{RESET}: ")).strip()
                if not user_input:
                    continue

                await display_agent_stream(
                    agent,
                    user_input,
                    thread_id,
                    create_agent_stream=create_agent_stream,
                    save_assistant_response=save_assistant_response,
                )
                print()
    except KeyboardInterrupt:
        print("\nExiting...")


def main() -> None:
    asyncio.run(run_application())
