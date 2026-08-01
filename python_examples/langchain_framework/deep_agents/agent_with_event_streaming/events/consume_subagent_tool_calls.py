from typing import Any

from .consume_single_tool_call import consume_single_tool_call


async def consume_subagent_tool_calls(subagent: Any) -> None:
    async for call in subagent.tool_calls:
        await consume_single_tool_call(
            call,
            label=f"[subagent:{subagent.name}] tool: {call.tool_name}",
        )