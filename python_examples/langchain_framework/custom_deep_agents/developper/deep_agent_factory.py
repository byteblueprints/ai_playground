from contextlib import AsyncExitStack
import asyncio

from deepagents import create_deep_agent
from deepagents.middleware.filesystem import FilesystemPermission
from middlewares import CoordinatorToolFilterMiddleware
from tools import load_nvim_tools, load_powershell_tools

from subagents import create_subagents

from deep_agent_runtime import BACKEND, DELETE_FILE_TOOL, EXECUTE_TOOL, MEMORY_STORE, MODEL


COORDINATOR_SYSTEM_PROMPT = (
    "You are the main coordinator agent. "
    "Delegation policy is strict: for coding, file changes, code review, and testing requests, call the task tool first and delegate to the best available specialist subagent. "
    "Select subagents by their current descriptions and capabilities, not by hardcoded names, so the policy automatically applies to future subagents. "
    "When using the PowerShell MCP start_console tool, default to reason=null so existing standby consoles are reused. "
    "Provide a non-empty reason only when the user explicitly asks for a new/separate/additional PowerShell terminal or window. "
    "Do not use direct coordinator implementation tools (such as write_file, edit_file, grep, or execute) for those requests unless delegation is not possible. "
    "Direct work is allowed only when no available subagent can reasonably handle the task, or a delegation attempt fails because of missing capability. "
    "If direct work is used after fallback, briefly explain why delegation was not possible. "
    "File location policy: create source code files and other non-temporary files inside the workspace path; create memory files inside /memories; and create temporary files inside the default backend."
)

COORDINATOR_PERMISSIONS = [
    FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
]

COORDINATOR_EXCLUDED_TOOLS = frozenset({"write_file", "edit_file"})

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
        middleware=[CoordinatorToolFilterMiddleware(excluded=COORDINATOR_EXCLUDED_TOOLS)],
        permissions=COORDINATOR_PERMISSIONS,
        subagents=subagents,
        store=MEMORY_STORE,
        tools=[DELETE_FILE_TOOL, EXECUTE_TOOL, *powershell_tools, *nvim_tools],
    )

