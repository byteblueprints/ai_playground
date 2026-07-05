import json


def format_value(value) -> str:
    """Compact single-line representation of a tool input/output value."""
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def truncate(text: str, limit: int = 300) -> str:
    return text[:limit] + "…" if len(text) > limit else text
