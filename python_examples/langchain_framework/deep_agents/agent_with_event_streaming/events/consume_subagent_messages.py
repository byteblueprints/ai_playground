from typing import Any


async def consume_subagent_messages(subagent: Any) -> None:
    async for msg in subagent.messages:
        text = await msg.text
        if text:
            print(f"\n[subagent:{subagent.name}] {text}")