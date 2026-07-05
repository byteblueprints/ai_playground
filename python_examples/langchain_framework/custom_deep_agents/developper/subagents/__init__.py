from contextlib import AsyncExitStack

from deepagents import SubAgent

from .code_reviewer import create_code_reviewer_subagent
from .code_writer import create_code_writer_subagent
from .dev_tester import create_dev_tester_subagent


async def create_subagents(exit_stack: AsyncExitStack) -> list[SubAgent]:
	return [
		create_code_writer_subagent(),
		create_code_reviewer_subagent(),
		await create_dev_tester_subagent(exit_stack),
	]