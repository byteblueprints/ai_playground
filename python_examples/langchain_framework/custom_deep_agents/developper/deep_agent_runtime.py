import os
import warnings

from dotenv import load_dotenv
from langchain_core._api import LangChainBetaWarning
from langchain_openai import ChatOpenAI
from langgraph.store.memory import InMemoryStore

from backends.backend import WORKSPACE_ROUTE, create_backend_pair
from tools import make_delete_file_tool, make_execute_tool

warnings.filterwarnings("ignore", category=LangChainBetaWarning)

load_dotenv()


SUPPORTED_MERCURY_MODELS = {
	"mercury",
	"mercury-2",
	"mercury-coder",
	"mercury-coder-small",
	"mercury-small",
}


def _build_model() -> str | ChatOpenAI:
	provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
	if provider not in {"mercury", "inception"}:
		return os.getenv("MODEL", "openai:gpt-5.4")

	inception_api_key = os.getenv("INCEPTION_API_KEY")
	if not inception_api_key:
		raise RuntimeError("INCEPTION_API_KEY is required when LLM_PROVIDER=mercury.")

	mercury_model = os.getenv("MERCURY_MODEL", "mercury-coder").strip().lower()
	if mercury_model not in SUPPORTED_MERCURY_MODELS:
		raise RuntimeError(
			"MERCURY_MODEL must be one of: mercury, mercury-2, mercury-coder, mercury-coder-small, mercury-small"
		)
	base_url = os.getenv("MERCURY_BASE_URL", "https://api.inceptionlabs.ai/v1")

	return ChatOpenAI(
		model=mercury_model,
		base_url=base_url,
		api_key=inception_api_key,
		use_responses_api=False,
	)

MODEL = _build_model()
APP_DESCRIPTION = "Developer-focused Deep Agent scaffold with pluggable subagents."
MEMORY_STORE = InMemoryStore()
BACKEND, WORKSPACE_BACKEND = create_backend_pair()
DELETE_FILE_TOOL = make_delete_file_tool(WORKSPACE_BACKEND, path_prefix=WORKSPACE_ROUTE)
EXECUTE_TOOL = make_execute_tool(WORKSPACE_BACKEND)
