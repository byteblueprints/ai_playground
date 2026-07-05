from deepagents import SubAgent

from deep_agent_runtime import MODEL


def create_code_reviewer_subagent() -> SubAgent:
	return {
		"name": "code-reviewer",
		"description": "Owns all code review tasks: use this agent for any review, audit, feedback, or inspection of code for correctness, maintainability, architecture, and readability risks.",
		"system_prompt": (
			"You are a code reviewer specialist. "
			"Prioritize correctness, design quality, and actionable review feedback from code inspection."
		),
		"tools": [],
		"model": MODEL,
	}