import asyncio
import os
from contextlib import AsyncExitStack

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools as load_mcp_session_tools


def _mcp_startup_timeout_seconds() -> float:
    raw = os.getenv("MCP_STARTUP_TIMEOUT_SECONDS", "15").strip()
    try:
        return max(1.0, float(raw))
    except ValueError:
        return 15.0


async def load_nvim_tools(exit_stack: AsyncExitStack) -> list:
    timeout_seconds = _mcp_startup_timeout_seconds()
    server_config = {
        "transport": "stdio",
        "command": "uvx",
        "args": ["nvim-mcp"],
        "env": {"NVIM_ADDRESS": "127.0.0.1:12345"},
    }

    try:
        client = MultiServerMCPClient({"nvim": server_config})
        session = await asyncio.wait_for(
            exit_stack.enter_async_context(client.session("nvim")),
            timeout=timeout_seconds,
        )
        return await asyncio.wait_for(
            load_mcp_session_tools(session, server_name="nvim"),
            timeout=timeout_seconds,
        )
    except TimeoutError:
        print(
            f"Warning: Timed out initializing nvim MCP session after {timeout_seconds:.0f}s. "
            "Set MCP_STARTUP_TIMEOUT_SECONDS to tune startup."
        )
    except Exception as error:
        print(f"Warning: Failed to initialize nvim MCP session: {error}")

    return []
