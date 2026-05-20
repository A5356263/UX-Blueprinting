from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from packages.common import get_project_runtime_dir
from packages.provenance import append_command_if_provenance_exists


MIRROR_VERSION = "route-decision@3.0"
SUPPORTED_UXB_SCHEMA_VERSIONS = {"uxb_route_decision@3.0"}
BUSINESS_OUTPUTS = {
    "business_note.md": "fast",
    "business_blueprint_lite.md": "standard",
    "business_blueprint.md": "full",
}
REQUIRED_CORE_OUTPUTS = {"facts.md", "experience_blueprint.md"}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _clean_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    cleaned: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            cleaned.append(text)
    return cleaned


def _uxb_route_decision_path(project_id: str) -> Path:
    return get_project_runtime_dir(project_id) / "uxb_route_decision.json"


def _infer_execution_mode(required_outputs: list[str]) -> tuple[str, list[str]]:
    errors: list[str] = []
    normalized_outputs = {item.strip() for item in required_outputs if item.strip()}
    selected_business_outputs = [name for name in BUSINESS_OUTPUTS if name in normalized_outputs]

    if len(selected_business_outputs) != 1:
        errors.append(
            "execution.required_outputs 必须且只能明确指定一个业务产物："
            "business_note.md / business_blueprint_lite.md / business_blueprint.md"
        )
        return "", errors

    missing_core_outputs = sorted(REQUIRED_CORE_OUTPUTS - normalized_outputs)
    if missing_core_outputs:
        errors.append(
            "execution.required_outputs 缺少主链路基础产物："
            + ", ".join(missing_core_outputs)
        )

    return BUSINESS_OUTPUTS[selected_business_outputs[0]], errors


def load_uxb_execution_decision(project_id: str) -> dict[str, Any]:
    path = _uxb_route_decision_path(project_id)
    payload = _read_json(path)
    validation_errors: list[str] = []

    if not payload:
        validation_errors.append("缺少 runtime/uxb_route_decision.json")
        return {
            "project_id": project_id,
            "status": "needs_rejudgment",
            "source_path": f"projects/{project_id}/runtime/uxb_route_decision.json",
            "required_outputs": [],
            "execution_mode": "",
            "knowledge_selection": {
                "business_refs": [],
                "guideline_refs": [],
                "complexity_refs": [],
                "selection_reasons": [],
            },
            "validation_errors": validation_errors,
        }

    schema_version = str(payload.get("schema_version") or "").strip()
    created_by = str(payload.get("created_by") or "").strip()
    confirmed_by_user = bool(payload.get("confirmed_by_user"))
    can_execute_mainline = bool(payload.get("can_execute_mainline"))

    if schema_version not in SUPPORTED_UXB_SCHEMA_VERSIONS:
        validation_errors.append(
            "uxb_route_decision.schema_version 不受支持，当前只支持 "
            + ", ".join(sorted(SUPPORTED_UXB_SCHEMA_VERSIONS))
        )
    if created_by != "uxb_ai":
        validation_errors.append("uxb_route_decision.created_by 必须为 uxb_ai")
    if not confirmed_by_user:
        validation_errors.append("uxb_route_decision.confirmed_by_user 必须为 true")
    if not can_execute_mainline:
        validation_errors.append("uxb_route_decision.can_execute_mainline 必须为 true")

    judgment = payload.get("judgment")
    if not isinstance(judgment, dict):
        judgment = {}
        validation_errors.append("uxb_route_decision.judgment 必须存在且为对象")

    complexity_judgment = payload.get("complexity_judgment")
    if not isinstance(complexity_judgment, dict):
        complexity_judgment = {}

    execution = payload.get("execution")
    if not isinstance(execution, dict):
        execution = {}
        validation_errors.append("uxb_route_decision.execution 必须存在且为对象")

    required_outputs = _clean_string_list(execution.get("required_outputs"))
    if not required_outputs:
        validation_errors.append("uxb_route_decision.execution.required_outputs 不能为空")

    knowledge_selection = payload.get("knowledge_selection")
    if not isinstance(knowledge_selection, dict):
        knowledge_selection = {}
        validation_errors.append("uxb_route_decision.knowledge_selection 必须存在且为对象")

    normalized_knowledge_selection = {
        "business_refs": _clean_string_list(knowledge_selection.get("business_refs")),
        "guideline_refs": _clean_string_list(knowledge_selection.get("guideline_refs")),
        "complexity_refs": _clean_string_list(knowledge_selection.get("complexity_refs")),
        "selection_reasons": _clean_string_list(knowledge_selection.get("selection_reasons")),
    }

    execution_mode, mode_errors = _infer_execution_mode(required_outputs)
    validation_errors.extend(mode_errors)

    status = "confirmed" if not validation_errors else "needs_rejudgment"
    return {
        "project_id": project_id,
        "status": status,
        "source_path": f"projects/{project_id}/runtime/uxb_route_decision.json",
        "schema_version": schema_version,
        "created_by": created_by,
        "confirmed_by_user": confirmed_by_user,
        "can_execute_mainline": can_execute_mainline,
        "judgment": judgment,
        "complexity_judgment": complexity_judgment,
        "knowledge_selection": normalized_knowledge_selection,
        "required_outputs": required_outputs,
        "execution_notes": _clean_string_list(execution.get("notes")),
        "execution_mode": execution_mode,
        "validation_errors": validation_errors,
    }


def build_route_decision(project_id: str) -> dict[str, Any]:
    decision = load_uxb_execution_decision(project_id)
    return {
        "version": MIRROR_VERSION,
        "project_id": project_id,
        "status": decision["status"],
        "source": decision["source_path"],
        "can_execute_mainline": decision.get("status") == "confirmed",
        "required_outputs": decision.get("required_outputs", []),
        "execution_mode": decision.get("execution_mode", ""),
        "validation_errors": decision.get("validation_errors", []),
        "note": "Temporary execution mirror. No semantic judgment.",
    }


def run_route_decision(project_id: str) -> int:
    runtime_dir = get_project_runtime_dir(project_id)
    runtime_dir.mkdir(parents=True, exist_ok=True)

    mirror = build_route_decision(project_id)
    json_path = runtime_dir / "route_decision.json"
    json_path.write_text(json.dumps(mirror, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if mirror.get("status") == "confirmed":
        append_command_if_provenance_exists(project_id, "route-decision")
        print(f"route_decision.json 已同步: {json_path}")
        return 0

    print(f"route_decision.json 已同步: {json_path}")
    print("当前执行判断需要 UXB AI 重新确认，请先更新 runtime/uxb_route_decision.json。")
    for item in _clean_string_list(mirror.get("validation_errors")):
        print(f"- {item}")
    return 1
