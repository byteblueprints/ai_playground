from typing import Any


def _extract_text_delta(event: dict[str, Any]) -> str:
    if event.get("method") != "messages":
        return ""

    params = event.get("params") or {}
    namespace = params.get("namespace")
    # Coordinator messages are top-level events with empty namespace.
    if namespace:
        return ""

    data = params.get("data")
    payload = data[0] if isinstance(data, (list, tuple)) and data else None
    if not isinstance(payload, dict):
        return ""

    if payload.get("event") != "content-block-delta":
        return ""

    delta = payload.get("delta") or {}
    if not isinstance(delta, dict):
        return ""

    if delta.get("type") != "text-delta":
        return ""

    text = delta.get("text")
    return str(text) if text else ""


async def consume_coordinator_messages(stream: Any, coordinator_chunks: list[str]) -> None:
    printed_header = False
    async for event in stream:
        text_delta = _extract_text_delta(event)
        if not text_delta:
            continue

        if not printed_header:
            print("assistant: ", end="", flush=True)
            printed_header = True
        print(text_delta, end="", flush=True)
        coordinator_chunks.append(text_delta)

    if printed_header:
        print()