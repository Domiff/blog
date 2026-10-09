from typing import Any


def truncate(limit: int = 80):
    def formatter(model: Any, attribute: str) -> str:
        text = getattr(model, attribute) or ""
        if len(text) <= limit:
            return text
        return f"{text[:limit].rstrip()}..."
    return formatter
