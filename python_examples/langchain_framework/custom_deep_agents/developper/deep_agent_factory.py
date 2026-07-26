from contextlib import AsyncExitStack
import asyncio

from deepagents import create_deep_agent
from deepagents.middleware.filesystem import FilesystemPermission
from tools import load_nvim_tools, load_powershell_tools

from subagents import create_subagents

from deep_agent_runtime import BACKEND, DELETE_FILE_TOOL, EXECUTE_TOOL, MEMORY_STORE, MODEL

SKILL_SOURCES = ["/skills/"]
COORDINATOR_PERMISSIONS = [
    FilesystemPermission(operations=["write"], paths=["/skills", "/skills/**"], mode="deny"),
]


COORDINATOR_SYSTEM_PROMPT = (
    "You are the main coordinator agent. "
    "Delegate to specialist subagents when that improves quality or speed, and work directly when appropriate. "
    "When using the PowerShell MCP start_console tool, default to reason=null so existing standby consoles are reused. "
    "Provide a non-empty reason only when the user explicitly asks for a new/separate/additional PowerShell terminal or window. "
    "File location policy: create all source-code and project files inside /workspace; create memory files only inside /memories; and keep skill files in /skills as read-only references. "
    "Do not create, edit, or delete files under /skills unless the user explicitly asks to change skills. "
    "Create temporary files inside the default backend."
)

async def create_custom_deep_agent(
    exit_stack: AsyncExitStack,
):
    subagents = await create_subagents(exit_stack=exit_stack)
    # This block loads the PowerShell and Neovim tool sets and constructs the custom deep agent.
    powershell_tools, nvim_tools = await asyncio.gather(
        load_powershell_tools(exit_stack),
        load_nvim_tools(exit_stack),
    )

    return create_deep_agent(
        model=MODEL,
        system_prompt=COORDINATOR_SYSTEM_PROMPT,
        backend=BACKEND,
        skills=SKILL_SOURCES,
        permissions=COORDINATOR_PERMISSIONS,
        subagents=subagents,
        store=MEMORY_STORE,
        tools=[DELETE_FILE_TOOL, EXECUTE_TOOL, *powershell_tools, *nvim_tools],
    )

