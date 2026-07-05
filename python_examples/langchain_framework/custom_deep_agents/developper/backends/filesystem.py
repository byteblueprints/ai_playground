"""Filesystem backends with `delete` support (backport from deepagents main)."""

import shutil
from dataclasses import dataclass
from pathlib import Path

from deepagents.backends import FilesystemBackend, LocalShellBackend


@dataclass
class DeleteResult:
    """Result of a delete operation."""

    path: str | None = None
    error: str | None = None


class CustomFilesystemBackend(FilesystemBackend):
    """FilesystemBackend extended with a `delete` method.

    Backports `delete` from the deepagents main branch until it ships on PyPI.
    All other behaviour is identical to `FilesystemBackend`.
    """

    def delete(self, file_path: str) -> DeleteResult:
        """Delete a file or directory from the filesystem.

        Files are unlinked. Directories are removed recursively along with all
        of their contents. Symlinks are removed as links and never followed into
        their target (so deleting a symlink to a directory removes only the link).

        Args:
            file_path: Path to the file or directory to delete.

        Returns:
            `DeleteResult` with the deleted path on success, or an error if the
                path does not exist or removal fails.
        """
        try:
            resolved_path = self._resolve_path(file_path)
        except (OSError, RuntimeError) as e:
            return DeleteResult(error=f"Error deleting '{file_path}': {e}")

        try:
            if not resolved_path.exists() and not resolved_path.is_symlink():
                return DeleteResult(error=f"Error: '{file_path}' not found")

            if resolved_path.is_symlink():
                resolved_path.unlink()
            elif resolved_path.is_dir():
                shutil.rmtree(resolved_path)
            else:
                resolved_path.unlink()

            return DeleteResult(path=file_path)
        except OSError as e:
            return DeleteResult(error=f"Error deleting '{file_path}': {e}")


class CustomLocalShellBackend(LocalShellBackend):
    """LocalShellBackend extended with a `delete` method."""

    def delete(self, file_path: str) -> DeleteResult:
        """Delete a file or directory from the filesystem.

        Files are unlinked. Directories are removed recursively along with all
        of their contents. Symlinks are removed as links and never followed into
        their target (so deleting a symlink to a directory removes only the link).
        """
        try:
            resolved_path = self._resolve_path(file_path)
        except (OSError, RuntimeError) as e:
            return DeleteResult(error=f"Error deleting '{file_path}': {e}")

        try:
            if not resolved_path.exists() and not resolved_path.is_symlink():
                return DeleteResult(error=f"Error: '{file_path}' not found")

            if resolved_path.is_symlink():
                resolved_path.unlink()
            elif resolved_path.is_dir():
                shutil.rmtree(resolved_path)
            else:
                resolved_path.unlink()

            return DeleteResult(path=file_path)
        except OSError as e:
            return DeleteResult(error=f"Error deleting '{file_path}': {e}")
