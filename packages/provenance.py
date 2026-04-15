from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from packages.common import get_project_runtime_dir, get_project_source_dir


PROVENANCE_FILE = "provenance.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha256(path: Path) -> str:
    if not path.exists():
        return ""
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def provenance_path(project_id: str) -> Path:
    runtime_dir = get_project_runtime_dir(project_id)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    return runtime_dir / PROVENANCE_FILE


def read_provenance(project_id: str) -> dict[str, Any]:
    path = provenance_path(project_id)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def write_provenance(project_id: str, payload: dict[str, Any]) -> Path:
    path = provenance_path(project_id)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def build_generated_provenance(project_id: str, producer: str, command_name: str) -> dict[str, Any]:
    source_dir = get_project_source_dir(project_id)
    requirement_path = source_dir / "requirement.md"
    task_card_path = source_dir / "task_card.md"
    return {
        "project_id": project_id,
        "generation_mode": "generated",
        "producer": producer,
        "source_hash": _sha256(requirement_path),
        "task_card_hash": _sha256(task_card_path),
        "generated_at": now_iso(),
        "parent_project_id": "",
        "copied_from_project_id": "",
        "manual_patch_reason": "",
        "command_chain": [command_name],
    }


def upsert_generated_provenance(project_id: str, producer: str, command_name: str) -> Path:
    existing = read_provenance(project_id)
    if not existing:
        return write_provenance(project_id, build_generated_provenance(project_id, producer, command_name))

    source_dir = get_project_source_dir(project_id)
    existing["project_id"] = project_id
    existing["generation_mode"] = existing.get("generation_mode") or "generated"
    existing["producer"] = producer
    existing["source_hash"] = _sha256(source_dir / "requirement.md")
    existing["task_card_hash"] = _sha256(source_dir / "task_card.md")
    existing["generated_at"] = now_iso()
    existing["parent_project_id"] = str(existing.get("parent_project_id") or "")
    existing["copied_from_project_id"] = str(existing.get("copied_from_project_id") or "")
    existing["manual_patch_reason"] = str(existing.get("manual_patch_reason") or "")
    command_chain = [str(item) for item in existing.get("command_chain", []) if isinstance(item, str)]
    if command_name not in command_chain:
        command_chain.append(command_name)
    existing["command_chain"] = command_chain
    return write_provenance(project_id, existing)


def append_command_if_provenance_exists(project_id: str, command_name: str) -> None:
    existing = read_provenance(project_id)
    if not existing:
        return
    command_chain = [str(item) for item in existing.get("command_chain", []) if isinstance(item, str)]
    if command_name not in command_chain:
        command_chain.append(command_name)
    existing["command_chain"] = command_chain
    write_provenance(project_id, existing)


def validate_provenance(project_id: str, required_commands: list[str] | None = None) -> list[str]:
    payload = read_provenance(project_id)
    issues: list[str] = []
    if not payload:
        return ["缺少 runtime/provenance.json"]
    if str(payload.get("project_id") or "") != project_id:
        issues.append("provenance.project_id 与当前项目不一致")
    if str(payload.get("generation_mode") or "") != "generated":
        issues.append("provenance.generation_mode 不是 generated")
    if str(payload.get("copied_from_project_id") or "").strip():
        issues.append("provenance.copied_from_project_id 非空，疑似跨项目复制")
    if not str(payload.get("source_hash") or "").strip():
        issues.append("provenance.source_hash 缺失")
    if not str(payload.get("task_card_hash") or "").strip():
        issues.append("provenance.task_card_hash 缺失")
    command_chain = [str(item) for item in payload.get("command_chain", []) if isinstance(item, str)]
    if required_commands:
        missing = [item for item in required_commands if item not in command_chain]
        if missing:
            issues.append(f"provenance.command_chain 缺少：{', '.join(missing)}")
    return issues
