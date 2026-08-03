import asyncio
import os
import sys
import uuid
import warnings
from typing import Any

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core._api import LangChainBetaWarning
from langchain_core.language_models import BaseChatModel
from langgraph.store.memory import InMemoryStore

from events.consume_turn_events import consume_turn_events
from utils.colors import ENTITY_COLORS, RESET, colorize


load_dotenv()
warnings.filterwarnings("ignore", category=LangChainBetaWarning)

# Set up the model spec and reasoning effort from environment variables, with defaults.
model_spec = os.getenv("MODEL", "openai:gpt-5-mini")
reasoning_effort = os.getenv("REASONING_EFFORT", "medium")
system_prompt = (
    "You are a helpful deep agent for local experimentation. "
    "Use tools when useful and explain your reasoning clearly."
)


def build_model(spec: str, reasoning_effort: str | None) -> str | BaseChatModel:
    if not reasoning_effort:
        return spec

    return init_chat_model(
        spec,
        use_responses_api=True,
        reasoning={"effort": reasoning_effort, "summary": "auto"},
        output_version="responses/v1",
    )


def create_stream(agent: Any, messages: list[dict[str, str]], thread_id: str):
    return agent.stream_events(
        {"messages": messages},
        version="v3",
        config={"configurable": {"thread_id": thread_id}},
    )


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

    stream = create_stream(agent, conversation_history, thread_id)
    coordinator_chunks: list[str] = []

    consume_turn_events(stream, coordinator_chunks)

    save_assistant_response(memory_store, thread_id, conversation_history, coordinator_chunks)


async def run_chat() -> None:
    # Check for the OPENAI_API_KEY environment variable if using an OpenAI model
    if not os.getenv("OPENAI_API_KEY") and model_spec.startswith("openai:"):
        raise RuntimeError("OPENAI_API_KEY is required for openai:* models.")

    agent = create_deep_agent(
        model=build_model(model_spec, reasoning_effort),
        system_prompt=system_prompt,
    )
    
    # Initialize an in-memory store for conversation history and generate a unique thread ID for the session.
    memory_store = InMemoryStore()
    thread_id = str(uuid.uuid4())

    print(colorize(f"Session thread_id: {thread_id}", "neutral"))
    print(colorize("Type /exit to quit", "neutral"))

    while True:
        you_prompt = colorize("You:", "user", bold=True) + " " + ENTITY_COLORS["user"]
        user_text = (await asyncio.to_thread(input, you_prompt)).strip()
        sys.stdout.write(RESET)
        sys.stdout.flush()
        if not user_text:
            continue
        if user_text.lower() in {"/exit", "exit", "quit"}:
            break
        try:
            await run_turn(agent, memory_store, thread_id, user_text)
        except Exception as exc:
            print(colorize(f"Error: {exc}", "error", bold=True))


def main() -> None:
    asyncio.run(run_chat())


if __name__ == "__main__":
    main()