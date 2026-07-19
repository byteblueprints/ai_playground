from contextlib import AsyncExitStack

from langchain.agents import create_agent

from mcp_tools import load_nvim_tools
from runtime import MEMORY_STORE, MODEL


SYSTEM_PROMPT = (
    "You are a basic ReAct assistant focused on Neovim workflows. "
    "Use nvim MCP tools when they are useful, and keep answers concise and practical."
)


async def create_nvim_agent(exit_stack: AsyncExitStack):
    nvim_tools = await load_nvim_tools(exit_stack)
    return create_agent(
        model=MODEL,
        system_prompt=SYSTEM_PROMPT,
        store=MEMORY_STORE,
        tools=nvim_tools,
    )
