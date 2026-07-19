import json
from typing import Any


def truncate(text: str, limit: int = 300) -> str:
    return text[:limit] + "..." if len(text) > limit else text


def format_value(value: Any) -> str:
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=True)
    return str(value)


def extract_text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
                continue
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts)

    if isinstance(content, dict):
        text = content.get("text")
        return text if isinstance(text, str) else ""

    return ""


def extract_text_from_chunk(chunk: Any) -> str:
    if chunk is None:
        return ""

    content = getattr(chunk, "content", None)
    if content is not None:
        text = extract_text_from_content(content)
        if text:
            return text

    if isinstance(chunk, dict):
        text = extract_text_from_content(chunk.get("content"))
        if text:
            return text

    text_attr = getattr(chunk, "text", None)
    if isinstance(text_attr, str):
        return text_attr

    if isinstance(chunk, str):
        return chunk

    return ""


def extract_assistant_text_from_output(output: Any) -> str:
    if isinstance(output, dict):
        messages = output.get("messages")
        if isinstance(messages, list) and messages:
            last = messages[-1]
            if isinstance(last, dict):
                return extract_text_from_content(last.get("content"))

            content = getattr(last, "content", None)
            text = extract_text_from_content(content)
            if text:
                return text

        for key in ("output", "result", "text"):
            candidate = output.get(key)
            if isinstance(candidate, str):
                return candidate

    return ""
