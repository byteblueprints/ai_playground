from deepagents import SubAgent

from .code_reviewer import create_code_reviewer_subagent
from .code_writer import create_code_writer_subagent
from .dev_tester import create_dev_tester_subagent


def create_subagents(model: str, dev_tester_tools: list | None = None) -> list[SubAgent]:
	return [
		create_code_writer_subagent(model),
		create_code_reviewer_subagent(model),
		create_dev_tester_subagent(model, tools=dev_tester_tools),
	]