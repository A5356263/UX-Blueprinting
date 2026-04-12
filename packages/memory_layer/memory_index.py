from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from packages.common import get_memory_root_dir, get_repo_root


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def repo_rel(path: Path) -> str:
    try:
        return str(path.relative_to(get_repo_root())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def get_memory_index_file() -> Path:
    return get_memory_root_dir() / "index.json"


def load_memory_index() -> dict[str, Any]:
    payload = read_json(get_memory_index_file())
    if payload:
        return payload
    return {
        "index_version": "1.0",
        "updated_at": "",
        "item_count": 0,
        "items": [],
    }


def upsert_memory_index_item(item: dict[str, Any], path: Path) -> dict[str, Any]:
    index_payload = load_memory_index()
    existing_items = index_payload.get("items", [])
    items = [entry for entry in existing_items if isinstance(entry, dict) and entry.get("memory_id") != item.get("memory_id")]
    items.append(
        {
            "memory_id": item.get("memory_id"),
            "kind": item.get("kind"),
            "scope": item.get("scope"),
            "title": item.get("title"),
            "status": item.get("status"),
            "domain_tags": item.get("domain_tags", []),
            "task_type_tags": item.get("task_type_tags", []),
            "path": repo_rel(path),
            "updated_at": now_iso(),
        }
    )
    items.sort(key=lambda entry: str(entry.get("memory_id") or ""))
    index_payload["updated_at"] = now_iso()
    index_payload["item_count"] = len(items)
    index_payload["items"] = items
    write_json(get_memory_index_file(), index_payload)
    return index_payload
