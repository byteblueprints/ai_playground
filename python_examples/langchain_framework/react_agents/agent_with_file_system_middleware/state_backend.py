from deepagents.backends import StateBackend
from deepagents.middleware import FilesystemMiddleware
from dotenv import load_dotenv
from langchain.agents import create_agent

load_dotenv()

model = "openai:gpt-4.1"
APP_DESCRIPTION = "Chat agent with state backend."

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


agent_with_state_backend = create_agent(
	model=model,
	middleware=[FilesystemMiddleware(backend=StateBackend())],
	system_prompt=(
		"""You are a helpful assistant.
	"""
	),
	tools=[],
)


def ask_agent_with_state_backend(user_input: str) -> dict:
	return agent_with_state_backend.invoke(
		{"messages": [{"role": "user", "content": user_input}]}
	)


def format_agent_response(agent_response: dict) -> str:
	messages = agent_response.get("messages", []) if isinstance(agent_response, dict) else []
	if not messages:
		return str(agent_response)

	last_message = messages[-1]
	content = getattr(last_message, "content", "")
	return content if content else str(last_message)


def run_application() -> None:
	print("Chat started. Press Ctrl+C to exit.\n")

	try:
		while True:
			user_input = input(f"{GREEN}You{RESET}: ").strip()
			if not user_input:
				continue

			agent_response = ask_agent_with_state_backend(user_input)
			print(f"{RED}Agent{RESET}: {format_agent_response(agent_response)}")
			print()
	except KeyboardInterrupt:
		print("\nExiting...")


if __name__ == "__main__":
	run_application()
