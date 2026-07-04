from deepagents import SubAgent


def create_code_reviewer_subagent(model: str) -> SubAgent:
	return {
		"name": "code-reviewer",
		"description": "Performs static code review for correctness, maintainability, architecture, and readability risks.",
		"system_prompt": (
			"You are a code reviewer specialist. "
			"Prioritize correctness, design quality, and actionable review feedback from code inspection."
		),
		"tools": [],
		"model": model,
	}