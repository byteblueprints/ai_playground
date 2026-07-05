import os

from langchain_core.tools import tool


def make_execute_tool(backend):
    """Create a Windows shell tool bound to a sandbox-capable backend instance."""

    def _windows_shell_guidance(command: str) -> str | None:
        """Return guidance when Linux shell syntax is used on Windows hosts."""
        if os.name != "nt":
            return None

        lower = command.lower()
        linux_markers = (
            "python3 ",
            "/tmp/",
            ">/tmp/",
            "bash -c",
            "sh -c",
            "cd /workspace",
            "$!",
            "nohup ",
            " 2>&1 &",
            " /usr/bin/",
            " /var/",
            " /etc/",
        )
        if not any(marker in lower for marker in linux_markers):
            return None

        return (
            "Error: Detected Linux/bash-style command syntax on a Windows host.\n"
            "Use Windows PowerShell syntax instead.\n"
            "Guidelines:\n"
            "- Use Windows executables and commands (for example, `python` instead of `python3`).\n"
            "- Use Windows-friendly paths and avoid Linux roots like `/tmp`, `/usr/bin`, `/var`, `/etc`.\n"
            "- For background processes, use PowerShell `Start-Process` (or `Start-Job`) instead of `nohup`, `&`, and `$!`.\n"
            "- Keep commands relative to the workspace root when possible.\n"
            "Example background pattern:\n"
            "powershell -NoProfile -Command \""
            "Start-Process -FilePath <exe> -ArgumentList <args> -WorkingDirectory '.' -WindowStyle Hidden"
            "\""
        )

    @tool
    def run_windows_shell(command: str, timeout: int | None = None) -> str:
        """Run a Windows shell command in the workspace backend.

        Commands execute with the backend root as the working directory.
        This tool is intended for Windows hosts and accepts Windows shell
        commands (PowerShell syntax recommended).

        Prefer relative paths (for example, `python main.py`) because virtual
        filesystem paths like `/workspace/...` are not host shell paths.

        Args:
            command: Windows shell command to execute.
            timeout: Optional timeout in seconds for this command.

        Returns:
            Command output and execution status.
        """
        if timeout is not None and timeout < 0:
            return f"Error: timeout must be non-negative, got {timeout}."

        windows_hint = _windows_shell_guidance(command)
        if windows_hint is not None:
            return windows_hint

        try:
            result = backend.execute(command, timeout=timeout) if timeout is not None else backend.execute(command)
        except NotImplementedError as exc:
            return f"Error: Execution not available. {exc}"
        except ValueError as exc:
            return f"Error: Invalid parameter. {exc}"

        parts = [result.output]
        if result.exit_code is not None:
            command_status = "succeeded" if result.exit_code == 0 else "failed"
            parts.append(f"\n[Command {command_status} with exit code {result.exit_code}]")
        if result.truncated:
            parts.append("\n[Output was truncated due to size limits]")
        return "".join(parts)

    return run_windows_shell

def make_delete_file_tool(backend, path_prefix: str | None = None):
    """Create a delete tool bound to the provided backend instance."""

    normalized_prefix = None
    if path_prefix:
        normalized_prefix = path_prefix.rstrip("/") + "/"

    def _normalize_path(file_path: str) -> str:
        if not normalized_prefix:
            return file_path

        if file_path == normalized_prefix.rstrip("/"):
            return "/"

        if file_path.startswith(normalized_prefix):
            return "/" + file_path[len(normalized_prefix):].lstrip("/")

        return file_path

    @tool
    def delete_file(file_path: str) -> str:
        """Delete a file or directory. Directories are removed recursively.
        Symlinks are removed as links without following them.

        Args:
            file_path: Virtual path to the file or directory to delete.

        Returns:
            Confirmation message or error description.
        """
        backend_path = _normalize_path(file_path)
        result = backend.delete(backend_path)
        if result.error:
            return f"Error: {result.error}"
        return f"Deleted: {file_path}"

    return delete_file
