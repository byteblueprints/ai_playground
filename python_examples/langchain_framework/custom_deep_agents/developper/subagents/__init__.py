from contextlib import AsyncExitStack

from deepagents import SubAgent

from .code_reviewer import create_code_reviewer_subagent
from .code_writer import create_code_writer_subagent
from .dev_tester import create_dev_tester_subagent


async def create_subagents(model: str, exit_stack: AsyncExitStack) -> list[SubAgent]:
	return [
		create_code_writer_subagent(model),
		create_code_reviewer_subagent(model),
		await create_dev_tester_subagent(model, exit_stack),
	]