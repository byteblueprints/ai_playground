import os
from pathlib import Path

from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

from .filesystem import CustomLocalShellBackend


WORKSPACE_ROUTE = "/workspace/"
SKILLS_ROUTE = "/skills/"
MEMORIES_ROUTE = "/memories/"


def _resolve_workspace_root() -> Path:
	workspace_root = os.getenv("WORKSPACE_ROOT") or os.getenv("DEEP_AGENT_WORKSPACE_ROOT")
	if workspace_root:
		return Path(workspace_root).expanduser().resolve()

	# Default to a dedicated home folder under local file_system_root/workspace.
	return (Path(__file__).resolve().parent.parent / "file_system_root" / "workspace" / "home").resolve()


def _resolve_skills_root(workspace_root: Path) -> Path:
	skills_root = os.getenv("SKILLS_ROOT") or os.getenv("DEEP_AGENT_SKILLS_ROOT")
	if skills_root:
		return Path(skills_root).expanduser().resolve()

	# Keep skills and workspace under the same file_system_root when possible.
	if workspace_root.name.lower() == "home" and workspace_root.parent.name.lower() == "workspace":
		return (workspace_root.parent.parent / "skills").resolve()

	if workspace_root.name.lower() == "workspace":
		return (workspace_root.parent / "skills").resolve()

	return (workspace_root / "skills").resolve()


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


def create_skills_backend(workspace_root: Path) -> CustomLocalShellBackend:
	skills_root = _resolve_skills_root(workspace_root)
	skills_root.mkdir(parents=True, exist_ok=True)

	return CustomLocalShellBackend(
		root_dir=skills_root,
		virtual_mode=True,
		inherit_env=False,
	)


def create_backend_pair() -> tuple[CompositeBackend, CustomLocalShellBackend]:
	workspace_backend = create_workspace_backend()
	skills_backend = create_skills_backend(_resolve_workspace_root())
	backend = CompositeBackend(
		default=StateBackend(),
		routes={
			WORKSPACE_ROUTE: workspace_backend,
			SKILLS_ROUTE: skills_backend,
			MEMORIES_ROUTE: StoreBackend(namespace=lambda _rt: ("memories",)),
		},
	)
	return backend, workspace_backend
