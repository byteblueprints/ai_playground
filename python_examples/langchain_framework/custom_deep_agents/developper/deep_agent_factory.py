from contextlib import AsyncExitStack

from deepagents import create_deep_agent

from subagents import create_subagents

from deep_agent_runtime import BACKEND, DELETE_FILE_TOOL, EXECUTE_TOOL, MEMORY_STORE, MODEL


async def create_deep_agent_with_persistent_playwright_tools(
    exit_stack: AsyncExitStack,
):
    subagents = await create_subagents(exit_stack=exit_stack)

    return create_deep_agent(
        model=MODEL,
        backend=BACKEND,
        subagents=subagents,
        store=MEMORY_STORE,
        tools=[DELETE_FILE_TOOL, EXECUTE_TOOL],
    )
