import os
from contextlib import AsyncExitStack

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langgraph.store.memory import InMemoryStore

try:
	from .backend import create_backend
	from .subagents import create_subagents
except ImportError:
	from backend import create_backend
	from subagents import create_subagents

load_dotenv()

model = os.getenv("MODEL", "openai:gpt-5.4")
APP_DESCRIPTION = "Developer-focused Deep Agent scaffold with pluggable subagents."
memory_store = InMemoryStore()
backend = create_backend()


async def create_deep_agent_with_persistent_playwright_tools(
	exit_stack: AsyncExitStack,
):
	subagents = await create_subagents(model=model, exit_stack=exit_stack)

	return create_deep_agent(
		model=model,
		backend=backend,
		subagents=subagents,
		store=memory_store,
		tools=[],
	)


async def ask_agent(agent, user_input: str, thread_id: str) -> dict:
	history_item = memory_store.get(("conversation",), thread_id)
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
			memory_store.put(("conversation",), thread_id, conversation_history)

	return response


def format_agent_response(agent_response: dict) -> str:
	messages = agent_response.get("messages", []) if isinstance(agent_response, dict) else []
	if not messages:
		return str(agent_response)

	last_message = messages[-1]
	content = getattr(last_message, "content", "")
	if isinstance(content, str):
		return content if content else str(last_message)

	if isinstance(content, list):
		text_chunks: list[str] = []
		for block in content:
			if isinstance(block, str):
				text_chunks.append(block)
				continue

			if isinstance(block, dict):
				if block.get("type") == "text" and isinstance(block.get("text"), str):
					text_chunks.append(block["text"])
				continue

			block_type = getattr(block, "type", None)
			block_text = getattr(block, "text", None)
			if block_type == "text" and isinstance(block_text, str):
				text_chunks.append(block_text)

		formatted_text = "\n".join(chunk.strip() for chunk in text_chunks if chunk and chunk.strip())
		if formatted_text:
			return formatted_text

	return str(content) if content else str(last_message)