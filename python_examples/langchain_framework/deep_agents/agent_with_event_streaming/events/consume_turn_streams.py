import asyncio
from typing import Any

from .consume_coordinator_messages import consume_coordinator_messages
from .consume_coordinator_tool_calls import consume_coordinator_tool_calls
from .consume_subagent_stream import consume_subagent_stream


async def consume_turn_streams(stream: Any, coordinator_chunks: list[str]) -> None:
    await asyncio.gather(
        consume_coordinator_messages(stream, coordinator_chunks),
        consume_coordinator_tool_calls(stream),
        consume_subagent_stream(stream),
    )