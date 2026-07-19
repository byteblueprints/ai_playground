import asyncio
import os
import threading
import time
import uuid
from contextlib import AsyncExitStack

from nvim_agent import APP_DESCRIPTION, create_agent_stream, create_nvim_agent, save_assistant_response

from .streaming import display_agent_stream
from .styles import DIM, GREEN, RESET


def _wait_for_ctrl_x_windows(stop_event: threading.Event) -> bool:
    import msvcrt

    while not stop_event.is_set():
        if msvcrt.kbhit():
            key = msvcrt.getwch()
            if key == "\x18":
                return True
            if key in ("\x00", "\xe0") and msvcrt.kbhit():
                msvcrt.getwch()
        time.sleep(0.05)
    return False


async def _watch_for_cancel_shortcut(stop_event: threading.Event) -> bool:
    if os.name != "nt":
        return False
    return await asyncio.to_thread(_wait_for_ctrl_x_windows, stop_event)


async def run_application() -> None:
    thread_id = str(uuid.uuid4())
    print(APP_DESCRIPTION)
    print(f"Session thread ID: {thread_id}")
    print("Chat started. Press Ctrl+C to exit.")
    print("Press Ctrl+X during a turn to cancel the current interaction.\n")

    try:
        async with AsyncExitStack() as exit_stack:
            agent = await create_nvim_agent(exit_stack)
            while True:
                user_input = (await asyncio.to_thread(input, f"{GREEN}You{RESET}: ")).strip()
                if not user_input:
                    continue

                turn_task = asyncio.create_task(
                    display_agent_stream(
                        agent,
                        user_input,
                        thread_id,
                        create_agent_stream=create_agent_stream,
                        save_assistant_response=save_assistant_response,
                    )
                )
                cancel_stop_event = threading.Event()
                cancel_task = asyncio.create_task(_watch_for_cancel_shortcut(cancel_stop_event))

                done, _ = await asyncio.wait(
                    {turn_task, cancel_task},
                    return_when=asyncio.FIRST_COMPLETED,
                )

                if cancel_task in done and cancel_task.result() and not turn_task.done():
                    turn_task.cancel()
                    try:
                        await turn_task
                    except asyncio.CancelledError:
                        pass
                    print(f"{DIM}  interaction canceled (Ctrl+X){RESET}")
                else:
                    await turn_task

                cancel_stop_event.set()
                if not cancel_task.done():
                    cancel_task.cancel()
                try:
                    await cancel_task
                except asyncio.CancelledError:
                    pass

                print()
    except KeyboardInterrupt:
        print("\nExiting...")


def main() -> None:
    asyncio.run(run_application())
