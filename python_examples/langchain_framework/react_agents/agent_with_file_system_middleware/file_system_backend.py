import os
from pathlib import Path

from deepagents.backends import FilesystemBackend
from deepagents.middleware import FilesystemMiddleware
from dotenv import load_dotenv
from langchain.agents import create_agent

load_dotenv()

model = "openai:gpt-4.1"
APP_DESCRIPTION = "Chat agent with filesystem backend."

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


def create_backend():
	root_name = os.getenv("FILESYSTEM_BACKEND_ROOT", "file_system_backend_root")
	file_system_root = Path(__file__).resolve().parent / root_name
	file_system_root.mkdir(parents=True, exist_ok=True)
	return FilesystemBackend(root_dir=file_system_root, virtual_mode=True)


agent_with_file_system_backend = create_agent(
	model=model,
	middleware=[FilesystemMiddleware(backend=create_backend())],
	system_prompt=(
		"""You are a helpful assistant.
	"""
	),
	tools=[],
)


def ask_agent_with_file_system_backend(user_input: str) -> dict:
	return agent_with_file_system_backend.invoke(
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

			agent_response = ask_agent_with_file_system_backend(user_input)
			print(f"{RED}Agent{RESET}: {format_agent_response(agent_response)}")
			print()
	except KeyboardInterrupt:
		print("\nExiting...")


if __name__ == "__main__":
	run_application()
