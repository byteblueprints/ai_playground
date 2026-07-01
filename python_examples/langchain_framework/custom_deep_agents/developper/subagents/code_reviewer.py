from deepagents import SubAgent


def create_code_reviewer_subagent(model: str) -> SubAgent:
	return {
		"name": "code-reviewer",
		"description": "Reviews code for bugs, regressions, edge cases, and readability risks.",
		"system_prompt": (
			"You are a code reviewer specialist. "
			"Prioritize correctness, risk detection, and actionable review feedback."
		),
		"tools": [],
		"model": model,
	}