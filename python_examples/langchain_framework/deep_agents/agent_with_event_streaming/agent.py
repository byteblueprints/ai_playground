import asyncio
import inspect
import os
import uuid
import warnings
from typing import Any

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_core._api import LangChainBetaWarning
from langgraph.store.memory import InMemoryStore

from events.consume_turn_streams import consume_turn_streams


load_dotenv()
warnings.filterwarnings("ignore", category=LangChainBetaWarning)


model = os.getenv("MODEL", "openai:gpt-4.1-mini")
system_prompt = (
    "You are a helpful deep agent for local experimentation. "
    "Use tools when useful and explain your reasoning clearly."
)


async def create_stream(agent: Any, messages: list[dict[str, str]], thread_id: str):
    stream_candidate = agent.astream_events(
        {"messages": messages},
        version="v3",
        config={"configurable": {"thread_id": thread_id}},
    )
    if inspect.isawaitable(stream_candidate):
        return await stream_candidate
    return stream_candidate


def save_assistant_response(
    memory_store: InMemoryStore,
    thread_id: str,
    conversation_history: list[dict[str, str]],
    coordinator_chunks: list[str],
) -> None:
    assistant_text = "".join(coordinator_chunks).strip()
    if assistant_text:
        conversation_history.append({"role": "assistant", "content": assistant_text})
    memory_store.put(("conversation",), thread_id, conversation_history)


async def run_turn(agent: Any, memory_store: InMemoryStore, thread_id: str, user_text: str) -> None:
    history_item = memory_store.get(("conversation",), thread_id)
    conversation_history = history_item.value if history_item else []
    conversation_history.append({"role": "user", "content": user_text})

    stream = await create_stream(agent, conversation_history, thread_id)
    coordinator_chunks: list[str] = []

    await consume_turn_streams(stream, coordinator_chunks)

    save_assistant_response(memory_store, thread_id, conversation_history, coordinator_chunks)


async def run_chat() -> None:
    if not os.getenv("OPENAI_API_KEY") and model.startswith("openai:"):
        raise RuntimeError("OPENAI_API_KEY is required for openai:* models.")

    agent = create_deep_agent(
        model=model,
        system_prompt=system_prompt,
    )
    memory_store = InMemoryStore()
    thread_id = str(uuid.uuid4())

    print(f"session thread_id: {thread_id}")
    print("type /exit to quit")

    while True:
        user_text = (await asyncio.to_thread(input, "you: ")).strip()
        if not user_text:
            continue
        if user_text.lower() in {"/exit", "exit", "quit"}:
            break
        try:
            await run_turn(agent, memory_store, thread_id, user_text)
        except Exception as exc:
            print(f"error: {exc}")


def main() -> None:
    asyncio.run(run_chat())


if __name__ == "__main__":
    main()