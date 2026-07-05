import os
from pathlib import Path

from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

from .filesystem import CustomLocalShellBackend


WORKSPACE_ROUTE = "/workspace/"
MEMORIES_ROUTE = "/memories/"


def _resolve_workspace_root() -> Path:
	workspace_root = os.getenv("WORKSPACE_ROOT") or os.getenv("DEEP_AGENT_WORKSPACE_ROOT")
	if workspace_root:
		return Path(workspace_root).expanduser().resolve()

	# Default to the local file_system_root when no env var is provided.
	return (Path(__file__).resolve().parent.parent / "file_system_root").resolve()


def create_workspace_backend() -> CustomLocalShellBackend:
	workspace_root = _resolve_workspace_root()
	workspace_root.mkdir(parents=True, exist_ok=True)

	# Inherit host env so shell commands can resolve executables on Windows/macOS/Linux.
	path_override = os.getenv("LOCAL_SHELL_PATH")
	shell_env = {"PATH": path_override} if path_override else None

	return CustomLocalShellBackend(
		root_dir=workspace_root,
		virtual_mode=True,
		env=shell_env,
		inherit_env=True,
	)


def create_backend_pair() -> tuple[CompositeBackend, CustomLocalShellBackend]:
	workspace_backend = create_workspace_backend()
	backend = CompositeBackend(
		default=StateBackend(),
		routes={
			WORKSPACE_ROUTE: workspace_backend,
			MEMORIES_ROUTE: StoreBackend(namespace=lambda _rt: ("memories",)),
		},
	)
	return backend, workspace_backend
