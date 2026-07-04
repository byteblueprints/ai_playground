from contextlib import AsyncExitStack

from deepagents import SubAgent

try:
	from ..mcp_tools import load_playwright_tools
except ImportError:
	from mcp_tools import load_playwright_tools


async def create_dev_tester_subagent(model: str, exit_stack: AsyncExitStack) -> SubAgent:
	tools = await load_playwright_tools(exit_stack)

	return {
		"name": "dev-tester",
		"description": "Owns all application testing: unit, integration, end-to-end, API, UI/browser automation, regression, performance, security, and test planning/validation. Playwright tool is available for browser automation.",
		"system_prompt": (
			"You are the primary testing specialist for all application testing tasks. "
			"Handle test strategy, test design, test implementation guidance, and behavior validation across unit, integration, API, UI, and end-to-end scopes. "
			"For browser-based testing, use available browser tools for navigation, interactions, form/file flows, network checks, console checks, and screenshots."
		),
		"tools": tools,
		"model": model,
	}