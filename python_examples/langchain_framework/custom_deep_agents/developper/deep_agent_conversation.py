from deep_agent_runtime import MEMORY_STORE


async def ask_agent(agent, user_input: str, thread_id: str) -> dict:
    history_item = MEMORY_STORE.get(("conversation",), thread_id)
    conversation_history = history_item.value if history_item else []

    conversation_history.append({"role": "user", "content": user_input})

    response = await agent.ainvoke(
        {"messages": conversation_history},
        config={"configurable": {"thread_id": thread_id}},
    )

    messages = response.get("messages", [])
    if messages:
        last_message = messages[-1]
        assistant_content = getattr(last_message, "content", "")
        if assistant_content:
            conversation_history.append({"role": "assistant", "content": assistant_content})
            MEMORY_STORE.put(("conversation",), thread_id, conversation_history)

    return response


async def create_agent_stream(agent, user_input: str, thread_id: str):
    """Prepares conversation history, starts an astream_events stream, and returns (stream, history)."""
    history_item = MEMORY_STORE.get(("conversation",), thread_id)
    conversation_history = history_item.value if history_item else []
    conversation_history.append({"role": "user", "content": user_input})

    stream = await agent.astream_events(
        {"messages": conversation_history},
        version="v3",
        config={"configurable": {"thread_id": thread_id}},
    )
    return stream, conversation_history


def save_assistant_response(thread_id: str, conversation_history: list, assistant_text: str) -> None:
    """Persists the final assistant response into the in-memory conversation store."""
    if assistant_text.strip():
        conversation_history.append({"role": "assistant", "content": assistant_text})
        MEMORY_STORE.put(("conversation",), thread_id, conversation_history)
