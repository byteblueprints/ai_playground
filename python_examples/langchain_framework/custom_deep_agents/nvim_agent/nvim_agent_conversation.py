import inspect

from runtime import MEMORY_STORE


async def create_agent_stream(agent, user_input: str, thread_id: str):
    history_item = MEMORY_STORE.get(("conversation",), thread_id)
    conversation_history = history_item.value if history_item else []

    conversation_history.append({"role": "user", "content": user_input})

    stream_candidate = agent.astream_events(
        {"messages": conversation_history},
        version="v3",
        config={"configurable": {"thread_id": thread_id}},
    )

    if inspect.isawaitable(stream_candidate):
        return await stream_candidate, conversation_history
    return stream_candidate, conversation_history


def save_assistant_response(thread_id: str, conversation_history: list, assistant_text: str) -> None:
    if assistant_text.strip():
        conversation_history.append({"role": "assistant", "content": assistant_text})
        MEMORY_STORE.put(("conversation",), thread_id, conversation_history)
