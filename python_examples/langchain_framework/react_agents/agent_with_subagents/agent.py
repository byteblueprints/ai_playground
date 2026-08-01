import ast
import math
import operator
import uuid
from pathlib import Path

from deepagents.backends import FilesystemBackend
from deepagents.middleware import FilesystemMiddleware, SubAgentMiddleware
from dotenv import load_dotenv
from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore

load_dotenv()

model = "openai:gpt-4.1"
APP_DESCRIPTION = "Chat agent with subagents and preserved conversation context."
memory_store = InMemoryStore()

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


def create_backend():
	file_system_root = Path(__file__).resolve().parent / "file_system_root"
	file_system_root.mkdir(parents=True, exist_ok=True)
	return FilesystemBackend(root_dir=file_system_root, virtual_mode=True)


ALLOWED_BINARY_OPERATORS = {
	ast.Add: operator.add,
	ast.Sub: operator.sub,
	ast.Mult: operator.mul,
	ast.Div: operator.truediv,
	ast.FloorDiv: operator.floordiv,
	ast.Mod: operator.mod,
	ast.Pow: operator.pow,
}

ALLOWED_UNARY_OPERATORS = {
	ast.UAdd: operator.pos,
	ast.USub: operator.neg,
}

ALLOWED_MATH_FUNCTIONS = {
	"sqrt": math.sqrt,
	"sin": math.sin,
	"cos": math.cos,
	"tan": math.tan,
	"log": math.log,
	"log10": math.log10,
	"exp": math.exp,
	"abs": abs,
	"round": round,
}

ALLOWED_MATH_CONSTANTS = {
	"pi": math.pi,
	"e": math.e,
}


def _safe_eval(node: ast.AST) -> float:
	if isinstance(node, ast.Expression):
		return _safe_eval(node.body)

	if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
		return float(node.value)

	if isinstance(node, ast.BinOp):
		op_type = type(node.op)
		if op_type not in ALLOWED_BINARY_OPERATORS:
			raise ValueError("Unsupported operator")
		return ALLOWED_BINARY_OPERATORS[op_type](_safe_eval(node.left), _safe_eval(node.right))

	if isinstance(node, ast.UnaryOp):
		op_type = type(node.op)
		if op_type not in ALLOWED_UNARY_OPERATORS:
			raise ValueError("Unsupported unary operator")
		return ALLOWED_UNARY_OPERATORS[op_type](_safe_eval(node.operand))

	if isinstance(node, ast.Name):
		if node.id in ALLOWED_MATH_CONSTANTS:
			return ALLOWED_MATH_CONSTANTS[node.id]
		raise ValueError(f"Unsupported identifier: {node.id}")

	if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
		func_name = node.func.id
		if func_name not in ALLOWED_MATH_FUNCTIONS:
			raise ValueError(f"Unsupported function: {func_name}")
		args = [_safe_eval(arg) for arg in node.args]
		return float(ALLOWED_MATH_FUNCTIONS[func_name](*args))

	raise ValueError("Unsupported expression")


def math_solver(expression: str) -> str:
	"""Safely evaluate a math expression.

	Supports +, -, *, /, //, %, **, parentheses, basic math functions, and constants pi/e.
	"""
	try:
		parsed = ast.parse(expression, mode="eval")
		value = _safe_eval(parsed)
		return str(value)
	except Exception as error:
		return f"Could not evaluate expression: {error}"


math_subagent = {
	"name": "math-agent",
	"description": "Used to solve arithmetic and symbolic-style math tasks accurately.",
	"system_prompt": "You are a math specialist. Use the math_solver tool for calculations and explain results clearly.",
	"tools": [math_solver],
	"model": "openai:gpt-4.1",
}

subagents = [math_subagent]

backend = create_backend()

agent = create_agent(
	model=model,
	middleware=[
		FilesystemMiddleware(backend=backend),
		SubAgentMiddleware(backend=backend, subagents=subagents),
	],
	system_prompt=(
		"""You are a helpful assistant prepared for skill orchestration.
	"""
	),
	store=memory_store,
	tools=[],
)


def ask_agent(user_input: str, thread_id: str) -> dict:
	history_item = memory_store.get(("conversation",), thread_id)
	conversation_history = history_item.value if history_item else []

	conversation_history.append({"role": "user", "content": user_input})

	response = agent.invoke(
		{"messages": conversation_history},
		config={"configurable": {"thread_id": thread_id}},
	)

	messages = response.get("messages", [])
	if messages:
		last_message = messages[-1]
		assistant_content = getattr(last_message, "content", "")
		if assistant_content:
			conversation_history.append({"role": "assistant", "content": assistant_content})
			memory_store.put(("conversation",), thread_id, conversation_history)

	return response


def format_agent_response(agent_response: dict) -> str:
	messages = agent_response.get("messages", []) if isinstance(agent_response, dict) else []
	if not messages:
		return str(agent_response)

	last_message = messages[-1]
	content = getattr(last_message, "content", "")
	return content if content else str(last_message)


def run_application() -> None:
	thread_id = str(uuid.uuid4())
	print(f"Session thread ID: {thread_id}")
	print("Chat started. Press Ctrl+C to exit.\n")

	try:
		while True:
			user_input = input(f"{GREEN}You{RESET}: ").strip()
			if not user_input:
				continue

			agent_response = ask_agent(user_input, thread_id)
			print(f"{RED}Agent{RESET}: {format_agent_response(agent_response)}")
			print()
	except KeyboardInterrupt:
		print("\nExiting...")


if __name__ == "__main__":
	run_application()
