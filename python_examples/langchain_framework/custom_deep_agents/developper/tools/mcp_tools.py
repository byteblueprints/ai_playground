from contextlib import AsyncExitStack
import asyncio
import os
import shlex
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools as load_mcp_session_tools


def _split_shell_args(raw_args: str) -> list[str]:
	if not raw_args.strip():
		return []
	try:
		return shlex.split(raw_args, posix=False)
	except ValueError:
		return [raw_args]


def _mcp_startup_timeout_seconds() -> float:
	raw = os.getenv("MCP_STARTUP_TIMEOUT_SECONDS", "15").strip()
	try:
		return max(1.0, float(raw))
	except ValueError:
		return 15.0


def _version_key(version_name: str) -> tuple[int, ...]:
	chunks: list[int] = []
	for part in version_name.split("."):
		digits = "".join(ch for ch in part if ch.isdigit())
		if not digits:
			break
		chunks.append(int(digits))
	return tuple(chunks)


def _preferred_runtime_dirs() -> tuple[str, ...]:
	if os.name == "nt":
		return ("win-x64", "win-arm64")
	return ("linux-x64", "linux-arm64", "osx-arm64", "osx-x64")


def _proxy_executable_name() -> str:
	return "PowerShell.MCP.Proxy.exe" if os.name == "nt" else "PowerShell.MCP.Proxy"


def _resolve_default_powershell_proxy_path() -> str:
	user_profile = os.getenv("USERPROFILE", "").strip()
	one_drive_root = os.getenv("OneDrive", "").strip()

	doc_roots: list[Path] = []
	if user_profile:
		doc_roots.append(Path(user_profile) / "Documents")
	if one_drive_root:
		doc_roots.append(Path(one_drive_root) / "Documents")

	seen: set[Path] = set()
	proxy_name = _proxy_executable_name()

	for doc_root in doc_roots:
		if doc_root in seen:
			continue
		seen.add(doc_root)

		module_root = doc_root / "PowerShell" / "Modules" / "PowerShell.MCP"
		if not module_root.exists():
			continue

		version_dirs = [entry for entry in module_root.iterdir() if entry.is_dir()]
		version_dirs.sort(key=lambda path: _version_key(path.name), reverse=True)

		for version_dir in version_dirs:
			for runtime_dir in _preferred_runtime_dirs():
				candidate = version_dir / "bin" / runtime_dir / proxy_name
				if candidate.exists():
					return str(candidate)

	return ""


async def _load_tools_for_server(exit_stack: AsyncExitStack, *, server_name: str, server_config: dict) -> list:
	mcp_tools = []
	timeout_seconds = _mcp_startup_timeout_seconds()
	try:
		client = MultiServerMCPClient(
			{server_name: server_config}
		)
		mcp_session = await asyncio.wait_for(
			exit_stack.enter_async_context(client.session(server_name)),
			timeout=timeout_seconds,
		)
		mcp_tools = await asyncio.wait_for(
			load_mcp_session_tools(
				mcp_session,
				server_name=server_name,
			),
			timeout=timeout_seconds,
		)
	except TimeoutError:
		print(
			f"Warning: Timed out initializing {server_name} MCP session after {timeout_seconds:.0f}s. "
			"Set MCP_STARTUP_TIMEOUT_SECONDS or POWERSHELL_MCP_PROXY_PATH to tune startup."
		)
	except Exception as error:
		print(f"Warning: Failed to initialize persistent {server_name} MCP session: {error}")

	return mcp_tools


async def load_nvim_tools(exit_stack: AsyncExitStack) -> list:
	return await _load_tools_for_server(
		exit_stack,
		server_name="nvim",
		server_config={
			"transport": "stdio",
			"command": "uvx",
			"args": ["nvim-mcp"],
			"env": {"NVIM_ADDRESS": "127.0.0.1:12345"},
		},
	)


async def load_playwright_tools(exit_stack: AsyncExitStack) -> list:
	return await _load_tools_for_server(
		exit_stack,
		server_name="playwright",
		server_config={
			"transport": "stdio",
			"command": "npx",
			"args": ["@playwright/mcp@latest"],
		},
	)


async def load_powershell_tools(exit_stack: AsyncExitStack) -> list:
	proxy_path = os.getenv("POWERSHELL_MCP_PROXY_PATH", "").strip() or _resolve_default_powershell_proxy_path()
	proxy_args = _split_shell_args(os.getenv("POWERSHELL_MCP_PROXY_ARGS", "--no-profile"))

	if proxy_path:
		server_config = {
			"transport": "stdio",
			"command": proxy_path,
			"args": proxy_args,
		}
	else:
		server_config = {
			"transport": "stdio",
			"command": "pwsh",
			"args": [
				"-NoLogo",
				"-NoProfile",
				"-Command",
				"& (Get-MCPProxyPath) --no-profile",
			],
		}

	return await _load_tools_for_server(
		exit_stack,
		server_name="powershell",
		server_config=server_config,
	)
