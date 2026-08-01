from typing import Any

from .consume_single_tool_call import consume_single_tool_call


async def consume_coordinator_tool_calls(stream: Any) -> None:
    async for call in stream.tool_calls:
        await consume_single_tool_call(call, label=f"[tool] {call.tool_name}")