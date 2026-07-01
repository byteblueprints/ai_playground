from deepagents import SubAgent


def create_code_writer_subagent(model: str) -> SubAgent:
	return {
		"name": "code-writer",
		"description": "Implements features and refactors code with maintainable design.",
		"system_prompt": (
			"You are a code writer specialist. "
			"Focus on clear, correct, and maintainable implementation details."
		),
		"tools": [],
		"model": model,
	}