from deepagents import SubAgent

from deep_agent_runtime import MODEL


def create_research_planner_subagent() -> SubAgent:
	return {
		"name": "research-planner",
		"description": "Owns discovery and planning tasks: use this agent for technical research, requirement analysis, implementation planning, and execution breakdowns.",
		"system_prompt": (
			"You are a research and planning specialist. "
			"Focus on clarifying requirements, evaluating options, identifying risks, and producing actionable implementation plans."
		),
		"tools": [],
		"model": MODEL,
	}