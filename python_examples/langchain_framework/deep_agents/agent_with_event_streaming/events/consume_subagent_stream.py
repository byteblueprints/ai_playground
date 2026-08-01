from typing import Any

from .consume_single_subagent import consume_single_subagent


async def consume_subagent_stream(stream: Any) -> None:
    async for subagent in stream.subagents:
        await consume_single_subagent(subagent)