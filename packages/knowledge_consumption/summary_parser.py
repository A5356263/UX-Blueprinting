from __future__ import annotations

import re
from pathlib import Path


META_LINE_RE = re.compile(r"^\s*-\s*([a-zA-Z0-9_]+)\s*:\s*(.*?)\s*$")
LIST_ITEM_RE = re.compile(r"^\s*-\s+(.+?)\s*$")


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


def _parse_inline_list(value: str) -> list[str]:
    text = value.strip()
    if not (text.startswith("[") and text.endswith("]")):
        return []
    inner = text[1:-1].strip()
    if not inner:
        return []
    items: list[str] = []
    for part in inner.split(","):
        cleaned = part.strip().strip("'\"")
        if cleaned:
            items.append(cleaned)
    return items


def normalize_source_group(value: object) -> str:
    text = str(value or "").strip().lower()
    if text in {"business", "业务"}:
        return "business"
    if text in {"guideline", "guidelines", "设计准则"}:
        return "guideline"
    if text in {"inbox", "收件箱"}:
        return "inbox"
    return text


def normalize_stage_hint(value: object) -> str:
    text = str(value or "").strip().lower()
    if text in {"facts", "business", "experience"}:
        return text
    return text


def parse_summary_metadata(text: str) -> dict[str, object]:
    source_path = ""
    source_refs: list[str] = []
    related_summaries: list[str] = []
    page_type = ""
    source_group = ""
    confidence = ""
    summary_role = ""
    domain = ""
    stage_hint = ""
    current_multiline_key = ""

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        meta_match = META_LINE_RE.match(line)
        if meta_match:
            key = meta_match.group(1).strip()
            value = meta_match.group(2).strip()
            current_multiline_key = ""
            if key == "source_path":
                normalized = _normalize_repo_path(value)
                if normalized:
                    source_path = normalized
            elif key == "source_refs":
                inline_refs = _parse_inline_list(value)
                for ref in inline_refs:
                    normalized = _normalize_repo_path(ref)
                    if normalized and normalized not in source_refs:
                        source_refs.append(normalized)
                if value in {"[]", ""}:
                    current_multiline_key = "source_refs"
            elif key == "related_summaries":
                inline_related = _parse_inline_list(value)
                for ref in inline_related:
                    normalized = _normalize_repo_path(ref)
                    if normalized and normalized not in related_summaries:
                        related_summaries.append(normalized)
                if value in {"[]", ""}:
                    current_multiline_key = "related_summaries"
            elif key == "page_type":
                page_type = value
            elif key == "source_group":
                source_group = normalize_source_group(value)
            elif key == "confidence":
                confidence = value
            elif key == "summary_role":
                summary_role = value
            elif key == "domain":
                domain = value
            elif key == "stage_hint":
                stage_hint = normalize_stage_hint(value)
            continue

        if current_multiline_key:
            item_match = LIST_ITEM_RE.match(line)
            if not item_match:
                current_multiline_key = ""
                continue
            candidate = item_match.group(1).strip()
            normalized = _normalize_repo_path(candidate)
            if not normalized:
                continue
            if current_multiline_key == "source_refs" and normalized not in source_refs:
                source_refs.append(normalized)
            if current_multiline_key == "related_summaries" and normalized not in related_summaries:
                related_summaries.append(normalized)

    if source_path and source_path not in source_refs:
        source_refs.insert(0, source_path)

    return {
        "source_path": source_path,
        "source_refs": source_refs,
        "related_summaries": related_summaries,
        "page_type": page_type,
        "source_group": source_group,
        "confidence": confidence,
        "summary_role": summary_role,
        "domain": domain,
        "stage_hint": stage_hint,
    }
