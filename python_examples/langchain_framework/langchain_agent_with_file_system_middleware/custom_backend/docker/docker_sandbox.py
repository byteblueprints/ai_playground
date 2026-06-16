import atexit
import os
import shlex
import shutil
import subprocess
import tempfile

from deepagents.backends.protocol import (
	FILE_NOT_FOUND,
	INVALID_PATH,
	IS_DIRECTORY,
	PERMISSION_DENIED,
	ExecuteResponse,
	FileDownloadResponse,
	FileUploadResponse,
)
from deepagents.backends.sandbox import BaseSandbox


class DockerSandboxBackend(BaseSandbox):
	"""Docker-only sandbox backend using `docker exec` and `docker cp`."""

	def __init__(
		self,
		container_id: str,
		*,
		root_dir: str = "/",
		timeout: int = 120,
		max_output_bytes: int = 100_000,
		image_name: str | None = None,
		auto_start: bool = False,
		remove_on_exit: bool = False,
	) -> None:
		self.container_id = container_id
		self.root_dir = root_dir
		self._docker_style_id = f"docker-{container_id}"
		self._default_timeout = timeout
		self._max_output_bytes = max_output_bytes
		self._image_name = image_name
		self._auto_start = auto_start
		self._remove_on_exit = remove_on_exit
		self._created_by_backend = False

		if self._auto_start:
			self._ensure_container_started()

		if self._remove_on_exit:
			atexit.register(self.cleanup)

	def _run_docker(self, args: list[str], timeout: int | None = None) -> subprocess.CompletedProcess[str]:
		return subprocess.run(
			["docker", *args],
			check=False,
			capture_output=True,
			text=True,
			timeout=timeout,
		)

	def _container_exists(self) -> bool:
		result = self._run_docker(["ps", "-a", "--filter", f"name=^{self.container_id}$", "--format", "{{.Names}}"])
		return result.returncode == 0 and result.stdout.strip() == self.container_id

	def _container_running(self) -> bool:
		result = self._run_docker(["ps", "--filter", f"name=^{self.container_id}$", "--format", "{{.Names}}"])
		return result.returncode == 0 and result.stdout.strip() == self.container_id

	def _ensure_container_started(self) -> None:
		if shutil.which("docker") is None:
			raise RuntimeError("Docker CLI not found. Install Docker and ensure 'docker' is on PATH.")

		if self._container_exists():
			if not self._container_running():
				start_result = self._run_docker(["start", self.container_id])
				if start_result.returncode != 0:
					detail = (start_result.stderr or start_result.stdout or "Failed to start container").strip()
					raise RuntimeError(detail)
			return

		if not self._image_name:
			raise RuntimeError(
				"Container does not exist. Set image_name when auto_start=True so DockerSandboxBackend can create it."
			)

		run_result = self._run_docker(["run", "-d", "--name", self.container_id, self._image_name])
		if run_result.returncode != 0:
			detail = (run_result.stderr or run_result.stdout or "Failed to create container").strip()
			raise RuntimeError(detail)

		self._created_by_backend = True

	def cleanup(self) -> None:
		if not self._remove_on_exit:
			return
		if not self._created_by_backend:
			return
		try:
			self._run_docker(["rm", "-f", self.container_id])
		except Exception:
			pass

	@property
	def id(self) -> str:
		return self._docker_style_id

	def execute(self, command: str, *, timeout: int | None = None) -> ExecuteResponse:
		if not command or not isinstance(command, str):
			return ExecuteResponse(
				output="Error: Command must be a non-empty string.",
				exit_code=1,
				truncated=False,
			)

		effective_timeout = timeout if timeout is not None else self._default_timeout
		if effective_timeout <= 0:
			raise ValueError(f"timeout must be positive, got {effective_timeout}")

		shell_command = command
		if self.root_dir and self.root_dir != "/":
			shell_command = f"cd {shlex.quote(self.root_dir)} && {command}"

		try:
			result = self._run_docker(["exec", self.container_id, "sh", "-lc", shell_command], timeout=effective_timeout)

			output = result.stdout or ""
			if result.stderr:
				output += "".join(f"[stderr] {line}\n" for line in result.stderr.splitlines())

			truncated = False
			output_bytes = output.encode("utf-8")
			if len(output_bytes) > self._max_output_bytes:
				output = output_bytes[: self._max_output_bytes].decode("utf-8", errors="ignore")
				truncated = True

			return ExecuteResponse(
				output=output,
				exit_code=result.returncode,
				truncated=truncated,
			)
		except subprocess.TimeoutExpired:
			return ExecuteResponse(
				output=f"Error: Command timed out after {effective_timeout}s.",
				exit_code=124,
				truncated=False,
			)
		except FileNotFoundError:
			return ExecuteResponse(
				output="Error: Docker CLI not found. Install Docker and ensure 'docker' is on PATH.",
				exit_code=127,
				truncated=False,
			)

	def upload_files(self, files: list[tuple[str, bytes]]) -> list[FileUploadResponse]:
		responses: list[FileUploadResponse] = []
		for path, content in files:
			if not path or not path.startswith("/"):
				responses.append(FileUploadResponse(path=path, error=INVALID_PATH))
				continue

			tmp_path: str | None = None
			try:
				parent = os.path.dirname(path) or "/"
				mkdir_result = self._run_docker(["exec", self.container_id, "sh", "-lc", f"mkdir -p {shlex.quote(parent)}"])
				if mkdir_result.returncode != 0:
					err = (mkdir_result.stderr or mkdir_result.stdout or "").lower()
					if "permission denied" in err:
						responses.append(FileUploadResponse(path=path, error=PERMISSION_DENIED))
					else:
						responses.append(FileUploadResponse(path=path, error=(mkdir_result.stderr or mkdir_result.stdout or "mkdir failed").strip()))
					continue

				with tempfile.NamedTemporaryFile(delete=False) as tmp:
					tmp.write(content)
					tmp_path = tmp.name

				cp_result = self._run_docker(["cp", tmp_path, f"{self.container_id}:{path}"])
				if cp_result.returncode != 0:
					err = (cp_result.stderr or cp_result.stdout or "").lower()
					if "permission denied" in err:
						responses.append(FileUploadResponse(path=path, error=PERMISSION_DENIED))
					else:
						responses.append(FileUploadResponse(path=path, error=(cp_result.stderr or cp_result.stdout or "upload failed").strip()))
				else:
					responses.append(FileUploadResponse(path=path))
			except FileNotFoundError:
				responses.append(FileUploadResponse(path=path, error="docker cli not found"))
			except Exception as e:
				responses.append(FileUploadResponse(path=path, error=str(e)))
			finally:
				if tmp_path and os.path.exists(tmp_path):
					os.remove(tmp_path)

		return responses

	def download_files(self, paths: list[str]) -> list[FileDownloadResponse]:
		responses: list[FileDownloadResponse] = []
		for path in paths:
			if not path or not path.startswith("/"):
				responses.append(FileDownloadResponse(path=path, error=INVALID_PATH))
				continue

			tmp_path: str | None = None
			try:
				with tempfile.NamedTemporaryFile(delete=False) as tmp:
					tmp_path = tmp.name

				cp_result = self._run_docker(["cp", f"{self.container_id}:{path}", tmp_path])
				if cp_result.returncode != 0:
					err = (cp_result.stderr or cp_result.stdout or "").lower()
					if "no such file" in err or "not found" in err:
						responses.append(FileDownloadResponse(path=path, error=FILE_NOT_FOUND))
					elif "is a directory" in err:
						responses.append(FileDownloadResponse(path=path, error=IS_DIRECTORY))
					elif "permission denied" in err:
						responses.append(FileDownloadResponse(path=path, error=PERMISSION_DENIED))
					else:
						responses.append(FileDownloadResponse(path=path, error=(cp_result.stderr or cp_result.stdout or "download failed").strip()))
					continue

				with open(tmp_path, "rb") as f:
					responses.append(FileDownloadResponse(path=path, content=f.read()))
			except FileNotFoundError:
				responses.append(FileDownloadResponse(path=path, error="docker cli not found"))
			except Exception as e:
				responses.append(FileDownloadResponse(path=path, error=str(e)))
			finally:
				if tmp_path and os.path.exists(tmp_path):
					os.remove(tmp_path)

		return responses
