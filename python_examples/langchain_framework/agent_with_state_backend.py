from pathlib import Path

from deepagents.backends import FilesystemBackend
from deepagents.middleware import FilesystemMiddleware
from dotenv import load_dotenv
from langchain.agents import create_agent

load_dotenv()

model = "openai:gpt-4.1"


def create_backend():
    file_system_root = Path(__file__).resolve().parent / "file_system_root"
    file_system_root.mkdir(parents=True, exist_ok=True)
    return FilesystemBackend(root_dir=file_system_root, virtual_mode=True)


agent = create_agent(
    model=model,
    middleware=[FilesystemMiddleware(backend=create_backend())],
    system_prompt=(
        """You are a helpful assistant.
    """
    ),
    tools=[],
)

def ask_agent(user_input: str) -> str:
    return agent.invoke({"messages": [{"role": "user", "content": user_input}]})