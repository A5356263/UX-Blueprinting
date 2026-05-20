from __future__ import annotations

import json
from pathlib import Path

from packages.common import get_project_runtime_dir


def _dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        normalized = value.replace("\\", "/").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


def _selection_source(task_id: str) -> str:
    return f"projects/{task_id}/runtime/uxb_route_decision.json"


def _read_uxb_route_decision(task_id: str) -> dict[str, object]:
    route_path = get_project_runtime_dir(task_id) / "uxb_route_decision.json"
    if not route_path.exists() or not route_path.is_file():
        return {}
    try:
        payload = json.loads(route_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _normalize_reason_items(raw_items: object) -> list[dict[str, str]]:
    if not isinstance(raw_items, list):
        return []

    normalized_items: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        ref = str(item.get("ref") or "").replace("\\", "/").strip()
        reason = str(item.get("reason") or "").strip()
        if not ref:
            continue
        key = (ref, reason)
        if key in seen:
            continue
        seen.add(key)
        normalized_items.append({"ref": ref, "reason": reason})
    return normalized_items


def _normalize_ref_list(raw_values: object) -> list[str]:
    if not isinstance(raw_values, list):
        return []
    return _dedupe_keep_order([str(item) for item in raw_values if isinstance(item, str)])


def build_knowledge_consumption_plan(task_id: str) -> dict[str, object]:
    payload = _read_uxb_route_decision(task_id)
    knowledge_selection = payload.get("knowledge_selection")
    if not isinstance(knowledge_selection, dict):
        knowledge_selection = {}

    return {
        "selection_source": _selection_source(task_id),
        "selected_refs": {
            "business_refs": _normalize_ref_list(knowledge_selection.get("business_refs")),
            "guideline_refs": _normalize_ref_list(knowledge_selection.get("guideline_refs")),
            "complexity_refs": _normalize_ref_list(knowledge_selection.get("complexity_refs")),
        },
        "selection_reasons": _normalize_reason_items(knowledge_selection.get("selection_reasons")),
    }
