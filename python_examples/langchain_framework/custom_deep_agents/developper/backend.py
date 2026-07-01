import os
from pathlib import Path

from deepagents.backends import FilesystemBackend


def create_backend() -> FilesystemBackend:
	root_name = os.getenv("FILESYSTEM_BACKEND_ROOT", "file_system_root")
	file_system_root = Path(__file__).resolve().parent / root_name
	file_system_root.mkdir(parents=True, exist_ok=True)
	return FilesystemBackend(root_dir=file_system_root, virtual_mode=True)