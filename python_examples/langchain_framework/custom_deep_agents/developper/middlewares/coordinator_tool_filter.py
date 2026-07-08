from collections.abc import Awaitable, Callable
from typing import Any

from langchain.agents.middleware.types import AgentMiddleware
from langchain_core.messages import ToolMessage


def _tool_name(tool: Any) -> str | None:
    if isinstance(tool, dict):
        name = tool.get("name")
        if isinstance(name, str):
            return name
        function = tool.get("function")
        if isinstance(function, dict):
            function_name = function.get("name")
            if isinstance(function_name, str):
                return function_name
        return None

    name = getattr(tool, "name", None)
    return name if isinstance(name, str) else None


class CoordinatorToolFilterMiddleware(AgentMiddleware[Any, Any, Any]):
    def __init__(self, *, excluded: frozenset[str]) -> None:
        self._excluded = excluded

    def _filter(self, tools: list[Any]) -> list[Any]:
        if not self._excluded:
            return tools
        return [tool for tool in tools if _tool_name(tool) not in self._excluded]

    def wrap_model_call(self, request: Any, handler: Callable[[Any], Any]) -> Any:
        return handler(request.override(tools=self._filter(request.tools)))

    async def awrap_model_call(self, request: Any, handler: Callable[[Any], Awaitable[Any]]) -> Any:
        return await handler(request.override(tools=self._filter(request.tools)))

    def wrap_tool_call(self, request: Any, handler: Callable[[Any], Any]) -> Any:
        tool_name = request.tool_call.get("name")
        if tool_name in self._excluded:
            return ToolMessage(
                content=(
                    f"Error: direct coordinator usage of '{tool_name}' is blocked by delegation policy. "
                    "Call the task tool and delegate to the most suitable available subagent now. "
                    "Do not call this blocked tool again in this turn."
                ),
                name=str(tool_name),
                tool_call_id=request.tool_call.get("id"),
                status="error",
            )
        return handler(request)

    async def awrap_tool_call(self, request: Any, handler: Callable[[Any], Awaitable[Any]]) -> Any:
        tool_name = request.tool_call.get("name")
        if tool_name in self._excluded:
            return ToolMessage(
                content=(
                    f"Error: direct coordinator usage of '{tool_name}' is blocked by delegation policy. "
                    "Call the task tool and delegate to the most suitable available subagent now. "
                    "Do not call this blocked tool again in this turn."
                ),
                name=str(tool_name),
                tool_call_id=request.tool_call.get("id"),
                status="error",
            )
        return await handler(request)
