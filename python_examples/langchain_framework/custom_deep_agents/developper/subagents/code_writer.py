from deepagents import SubAgent

from deep_agent_runtime import MODEL


def create_code_writer_subagent() -> SubAgent:
	return {
		"name": "code-writer",
		"description": "Owns all code writing tasks: use this agent for any feature implementation, refactoring, or production code changes with maintainable design.",
		"system_prompt": (
			"You are a code writer specialist. "
			"Focus on clear, correct, and maintainable implementation details for production code."
		),
		"tools": [],
		"model": MODEL,
	}