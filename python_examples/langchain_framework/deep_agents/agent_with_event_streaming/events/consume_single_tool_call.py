from typing import Any


async def consume_single_tool_call(call: Any, label: str, indent: str = "  ") -> None:
    print(f"\n{label}")
    print(f"{indent}input: {call.input}")

    output_deltas: list[str] = []
    async for delta in call.output_deltas:
        output_deltas.append(str(delta))

    if output_deltas:
        print(f"{indent}output: {''.join(output_deltas)}")
    else:
        final_output = getattr(call, "output", None)
        if final_output not in (None, ""):
            print(f"{indent}output: {final_output}")

    if getattr(call, "error", None):
        print(f"{indent}error: {call.error}")