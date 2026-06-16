import os

from deepagents.middleware import FilesystemMiddleware
from dotenv import load_dotenv
from langchain.agents import create_agent

from langchain_framework.langchain_agent_with_file_system_middleware.custom_backend.docker.docker_sandbox import (
	DockerSandboxBackend,
)

load_dotenv()

model = "openai:gpt-4.1"
APP_DESCRIPTION = "Chat agent with Docker sandbox backend."

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


def _env_flag(name: str, default: bool = False) -> bool:
	value = os.getenv(name)
	if value is None:
		return default
	return value.strip().lower() in {"1", "true", "yes", "on"}


def create_sandbox_backend():
	container_id = os.getenv("DOCKER_SANDBOX_CONTAINER_ID", "my-container")
	image_name = os.getenv("DOCKER_SANDBOX_IMAGE")
	root_dir = os.getenv("DOCKER_SANDBOX_ROOT_DIR", "/")
	auto_start = _env_flag("DOCKER_SANDBOX_AUTO_START", False)
	remove_on_exit = _env_flag("DOCKER_SANDBOX_REMOVE_ON_EXIT", False)

	timeout_raw = os.getenv("DOCKER_SANDBOX_TIMEOUT", "120")
	try:
		timeout = int(timeout_raw)
	except ValueError:
		timeout = 120

	return DockerSandboxBackend(
		container_id=container_id,
		image_name=image_name,
		root_dir=root_dir,
		timeout=timeout,
		auto_start=auto_start,
		remove_on_exit=remove_on_exit,
	)


agent_with_sandbox_backend = create_agent(
	model=model,
	middleware=[FilesystemMiddleware(backend=create_sandbox_backend())],
	system_prompt=(
		"""You are a helpful assistant with filesystem and sandboxed command execution.

You can:
- Read and write files using filesystem tools
- Execute safe Python scripts and shell commands
- Help debug and analyze code

Always prioritize safety and inform users before executing commands.
	"""
	),
	tools=[],
)


def ask_agent_with_sandbox_backend(user_input: str) -> dict:
	return agent_with_sandbox_backend.invoke(
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

			agent_response = ask_agent_with_sandbox_backend(user_input)
			print(f"{RED}Agent{RESET}: {format_agent_response(agent_response)}")
			print()
	except KeyboardInterrupt:
		print("\nExiting...")


if __name__ == "__main__":
	run_application()
