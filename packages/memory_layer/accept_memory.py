from __future__ import annotations

from pathlib import Path
from typing import Any

from packages.common import get_memory_root_dir, get_project_memory_dir
from packages.memory_layer.memory_index import now_iso, read_json, repo_rel, upsert_memory_index_item, write_json


def _memory_directory_for(item: dict[str, Any]) -> Path:
    memory_root = get_memory_root_dir()
    kind = str(item.get("kind") or "")
    if kind == "capability_insight":
        return memory_root / "capability_insights"

    if kind == "failure_mode":
        category_dir = memory_root / "failure_modes"
    else:
        category_dir = memory_root / "patterns"

    domain_tags = [str(value) for value in item.get("domain_tags", []) if str(value).strip()]
    if str(item.get("scope") or "") == "domain" and domain_tags:
        return category_dir / domain_tags[0]
    return category_dir / "generic"


def _merge_unique(existing: list[Any], incoming: list[Any]) -> list[Any]:
    merged: list[Any] = []
    for value in [*existing, *incoming]:
        if value in merged:
            continue
        merged.append(value)
    return merged


def _merge_item(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    merged.update(incoming)
    for key in ["domain_tags", "task_type_tags", "classification_basis", "source_tasks", "source_artifacts", "source_issue_ids"]:
        merged[key] = _merge_unique(
            [value for value in existing.get(key, []) if value],
            [value for value in incoming.get(key, []) if value],
        )
    merged["status"] = "accepted"
    merged["accepted_at"] = now_iso()
    return merged


def _load_candidates(project_id: str) -> list[dict[str, Any]]:
    payload = read_json(get_project_memory_dir(project_id) / "extracted_memory_candidates.json")
    values = payload.get("candidates", [])
    return [item for item in values if isinstance(item, dict)]


def _write_trace_updates(project_id: str, accepted_ids: list[str]) -> None:
    trace_path = get_project_memory_dir(project_id) / "memory_trace.json"
    trace_payload = read_json(trace_path)
    trace_payload["accepted_memory_ids"] = accepted_ids
    trace_payload["updated_at"] = now_iso()
    write_json(trace_path, trace_payload)


def run_memory_accept(project_id: str) -> int:
    runtime_memory_dir = get_project_memory_dir(project_id)
    runtime_memory_dir.mkdir(parents=True, exist_ok=True)

    accepted_items: list[dict[str, Any]] = []
    accepted_ids: list[str] = []

    for item in _load_candidates(project_id):
        kind = str(item.get("kind") or "")
        if kind not in {"pattern", "failure_mode", "capability_insight"}:
            continue

        directory = _memory_directory_for(item)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{item['memory_id']}.json"
        existing = read_json(path)
        accepted_item = _merge_item(existing, item)
        write_json(path, accepted_item)
        upsert_memory_index_item(accepted_item, path)
        accepted_items.append(accepted_item | {"path": repo_rel(path)})
        accepted_ids.append(str(item.get("memory_id") or ""))

    accepted_payload = {
        "project_id": project_id,
        "generated_at": now_iso(),
        "accepted_count": len(accepted_items),
        "items": accepted_items,
    }
    write_json(runtime_memory_dir / "accepted_memory_items.json", accepted_payload)
    _write_trace_updates(project_id, accepted_ids)

    print(f"Accepted memory items: {runtime_memory_dir / 'accepted_memory_items.json'}")
    print(f"Updated long-term memory index: {get_memory_root_dir() / 'index.json'}")
    return 0
