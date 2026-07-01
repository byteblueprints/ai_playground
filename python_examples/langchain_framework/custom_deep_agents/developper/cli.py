import asyncio
import uuid
from contextlib import AsyncExitStack

try:
	from .deep_agent import (
		ask_agent,
		create_deep_agent_with_persistent_playwright_tools,
		format_agent_response,
	)
except ImportError:
	from deep_agent import ask_agent, create_deep_agent_with_persistent_playwright_tools, format_agent_response

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


async def run_application() -> None:
	thread_id = str(uuid.uuid4())
	print(f"Session thread ID: {thread_id}")
	print("Chat started. Press Ctrl+C to exit.\n")

	try:
		async with AsyncExitStack() as exit_stack:
			agent = await create_deep_agent_with_persistent_playwright_tools(exit_stack)
			while True:
				user_input = (await asyncio.to_thread(input, f"{GREEN}You{RESET}: ")).strip()
				if not user_input:
					continue

				agent_response = await ask_agent(agent, user_input, thread_id)
				print(f"{RED}Agent{RESET}: {format_agent_response(agent_response)}")
				print()
	except KeyboardInterrupt:
		print("\nExiting...")