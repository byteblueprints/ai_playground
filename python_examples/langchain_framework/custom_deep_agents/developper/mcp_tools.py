from contextlib import AsyncExitStack

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools as load_mcp_session_tools


async def load_playwright_tools(exit_stack: AsyncExitStack) -> list:
	playwright_tools = []
	try:
		client = MultiServerMCPClient(
			{
				"playwright": {
					"transport": "stdio",
					"command": "npx",
					"args": ["@playwright/mcp@latest"],
				},
			}
		)
		playwright_session = await exit_stack.enter_async_context(client.session("playwright"))
		playwright_tools = await load_mcp_session_tools(
			playwright_session,
			server_name="playwright",
		)
	except Exception as error:
		print(f"Warning: Failed to initialize persistent Playwright MCP session: {error}")

	return playwright_tools