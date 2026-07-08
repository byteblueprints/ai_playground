from contextlib import AsyncExitStack

from deepagents import SubAgent
from deepagents.middleware.filesystem import FilesystemPermission

from .code_reviewer import create_code_reviewer_subagent
from .code_writer import create_code_writer_subagent
from .dev_tester import create_dev_tester_subagent


SUBAGENT_PERMISSIONS = [
	FilesystemPermission(operations=["write"], paths=["/**"], mode="allow"),
]


def _with_subagent_permissions(subagent: SubAgent) -> SubAgent:
	return {**subagent, "permissions": SUBAGENT_PERMISSIONS}


async def create_subagents(exit_stack: AsyncExitStack) -> list[SubAgent]:
	return [
		_with_subagent_permissions(create_code_writer_subagent()),
		_with_subagent_permissions(create_code_reviewer_subagent()),
		_with_subagent_permissions(await create_dev_tester_subagent(exit_stack)),
	]
