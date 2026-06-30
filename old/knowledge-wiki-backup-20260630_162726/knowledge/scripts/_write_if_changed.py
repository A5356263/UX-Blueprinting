from __future__ import annotations

from pathlib import Path


def read_text_if_exists(path: Path, encoding: str = "utf-8") -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding=encoding)


def write_text_if_changed(path: Path, content: str, encoding: str = "utf-8") -> bool:
    existing = read_text_if_exists(path, encoding=encoding)
    if existing == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding=encoding)
    return True


def parse_metadata_value(text: str, field_name: str) -> str | None:
    prefix = f"- {field_name}:"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return None


def replace_metadata_value(text: str, field_name: str, value: str) -> str:
    prefix = f"- {field_name}:"
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = f"{prefix} {value}"
            return "\n".join(lines)
    return text
