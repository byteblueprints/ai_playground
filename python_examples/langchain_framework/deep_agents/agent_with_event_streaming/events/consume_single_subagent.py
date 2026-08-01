import asyncio
from typing import Any

from .consume_subagent_messages import consume_subagent_messages
from .consume_subagent_tool_calls import consume_subagent_tool_calls


async def consume_single_subagent(subagent: Any) -> None:
    print(f"\n[subagent:{subagent.name}] started")
    await asyncio.gather(
        consume_subagent_messages(subagent),
        consume_subagent_tool_calls(subagent),
    )
    print(f"[subagent:{subagent.name}] status: {getattr(subagent, 'status', 'unknown')}")