import asyncio

try:
	from .backend import create_backend
	from .cli import run_application
	from .deep_agent import (
		APP_DESCRIPTION,
		ask_agent,
		backend,
		create_deep_agent_with_persistent_playwright_tools,
		format_agent_response,
		memory_store,
		model,
	)
	from .subagents import create_subagents
except ImportError:
	from backend import create_backend
	from cli import run_application
	from deep_agent import (
		APP_DESCRIPTION,
		ask_agent,
		backend,
		create_deep_agent_with_persistent_playwright_tools,
		format_agent_response,
		memory_store,
		model,
	)
	from subagents import create_subagents


if __name__ == "__main__":
	asyncio.run(run_application())
