from deepagents import SubAgent


def create_dev_tester_subagent(model: str, tools: list | None = None) -> SubAgent:
	if tools is None:
		tools = []

	return {
		"name": "dev-tester",
		"description": "Designs and validates tests for behavior, edge cases, and regressions.",
		"system_prompt": (
			"You are a development testing specialist. "
			"Create practical test plans and verify behavior against requirements."
		),
		"tools": tools,
		"model": model,
	}