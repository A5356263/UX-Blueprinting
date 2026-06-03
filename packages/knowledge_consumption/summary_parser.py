from __future__ import annotations

import re
from pathlib import Path


META_LINE_RE = re.compile(r"^\s*-\s*([a-zA-Z0-9_]+)\s*:\s*(.*?)\s*$")


def _is_repo_relative_path(value: str) -> bool:
    text = value.strip().replace("\\", "/")
    if not text:
        return False
    if "://" in text:
        return False
    if text.startswith("/") or text.startswith("\\"):
        return False
    if re.match(r"^[a-zA-Z]:", text):
        return False
    if "*" in text or "?" in text:
        return False
    return "/" in text


def _normalize_repo_path(value: str, allow_directory: bool = False) -> str | None:
    text = value.strip().replace("\\", "/")
    if not _is_repo_relative_path(text):
        return None
    if not allow_directory and text.endswith("/"):
        return None
    if not allow_directory and "." not in Path(text).name:
        return None
    return text


def infer_source_group_from_source_path(value: object) -> str:
    text = str(value or "").strip().replace("\\", "/")
    if "/设计准则/" in text:
        return "guideline"
    if "/业务/" in text:
        return "business"
    if "/inbox/" in text:
        return "inbox"
    return ""


def parse_summary_metadata(text: str) -> dict[str, object]:
    source_path = ""
    summary_role = ""
    domain = ""

    for raw_line in text.splitlines():
        meta_match = META_LINE_RE.match(raw_line.rstrip())
        if not meta_match:
            continue
        key = meta_match.group(1).strip()
        value = meta_match.group(2).strip()
        if key == "source_path":
            normalized = _normalize_repo_path(value)
            if normalized:
                source_path = normalized
        elif key == "summary_role":
            summary_role = value
        elif key == "domain":
            domain = value

    return {
        "source_path": source_path,
        "source_group": infer_source_group_from_source_path(source_path),
        "summary_role": summary_role,
        "domain": domain,
    }
