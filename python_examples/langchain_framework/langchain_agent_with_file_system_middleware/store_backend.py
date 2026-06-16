import uuid

from deepagents.backends import StoreBackend
from deepagents.middleware import FilesystemMiddleware
from dotenv import load_dotenv
from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore

load_dotenv()

model = "openai:gpt-4.1"
APP_DESCRIPTION = "Chat agent with store backend memory."
memory_store = InMemoryStore()

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


agent_with_store_backend = create_agent(
	model=model,
	middleware=[FilesystemMiddleware(backend=StoreBackend())],
	system_prompt=(
		"""You are a helpful assistant.
	"""
	),
	store=memory_store,
	tools=[],
)


def ask_agent_with_store_backend(user_input: str, thread_id: str) -> dict:
	history_item = memory_store.get(("conversation",), thread_id)
	conversation_history = history_item.value if history_item else []

	conversation_history.append({"role": "user", "content": user_input})

	response = agent_with_store_backend.invoke(
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
	return content if content else str(last_message)


def run_application() -> None:
	thread_id = str(uuid.uuid4())
	print(f"Session thread ID: {thread_id}")
	print("Chat started. Press Ctrl+C to exit.\n")

	try:
		while True:
			user_input = input(f"{GREEN}You{RESET}: ").strip()
			if not user_input:
				continue

			agent_response = ask_agent_with_store_backend(user_input, thread_id)
			print(f"{RED}Agent{RESET}: {format_agent_response(agent_response)}")
			print()
	except KeyboardInterrupt:
		print("\nExiting...")


if __name__ == "__main__":
	run_application()
