from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from packages.common import get_project_runtime_dir


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


def _clean_reason_items(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    cleaned: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in value:
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
        cleaned.append({"ref": ref, "reason": reason})
    return cleaned


def _uxb_route_decision_path(project_id: str) -> Path:
    return get_project_runtime_dir(project_id) / "uxb_route_decision.json"


def _infer_execution_mode(required_outputs: list[str]) -> tuple[str, list[str]]:
    errors: list[str] = []
    normalized_outputs = {item.strip() for item in required_outputs if item.strip()}
    selected_business_outputs = [name for name in BUSINESS_OUTPUTS if name in normalized_outputs]

    if len(selected_business_outputs) != 1:
        errors.append(
            "execution.required_outputs must include exactly one business output: "
            "business_note.md / business_blueprint_lite.md / business_blueprint.md"
        )
        return "", errors

    missing_core_outputs = sorted(REQUIRED_CORE_OUTPUTS - normalized_outputs)
    if missing_core_outputs:
        errors.append(
            "execution.required_outputs is missing required core outputs: "
            + ", ".join(missing_core_outputs)
        )

    return BUSINESS_OUTPUTS[selected_business_outputs[0]], errors


def load_uxb_execution_decision(project_id: str) -> dict[str, Any]:
    path = _uxb_route_decision_path(project_id)
    payload = _read_json(path)
    validation_errors: list[str] = []

    if not payload:
        validation_errors.append("Missing runtime/uxb_route_decision.json")
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
            "uxb_route_decision.schema_version is unsupported. Supported values: "
            + ", ".join(sorted(SUPPORTED_UXB_SCHEMA_VERSIONS))
        )
    if created_by != "uxb_ai":
        validation_errors.append("uxb_route_decision.created_by must be uxb_ai")
    if not confirmed_by_user:
        validation_errors.append("uxb_route_decision.confirmed_by_user must be true")
    if not can_execute_mainline:
        validation_errors.append("uxb_route_decision.can_execute_mainline must be true")

    judgment = payload.get("judgment")
    if not isinstance(judgment, dict):
        judgment = {}
        validation_errors.append("uxb_route_decision.judgment must be an object")

    complexity_judgment = payload.get("complexity_judgment")
    if not isinstance(complexity_judgment, dict):
        complexity_judgment = {}

    execution = payload.get("execution")
    if not isinstance(execution, dict):
        execution = {}
        validation_errors.append("uxb_route_decision.execution must be an object")

    required_outputs = _clean_string_list(execution.get("required_outputs"))
    if not required_outputs:
        validation_errors.append("uxb_route_decision.execution.required_outputs cannot be empty")

    knowledge_selection = payload.get("knowledge_selection")
    if not isinstance(knowledge_selection, dict):
        knowledge_selection = {}
        validation_errors.append("uxb_route_decision.knowledge_selection must be an object")

    normalized_knowledge_selection = {
        "business_refs": _clean_string_list(knowledge_selection.get("business_refs")),
        "guideline_refs": _clean_string_list(knowledge_selection.get("guideline_refs")),
        "complexity_refs": _clean_string_list(knowledge_selection.get("complexity_refs")),
        "selection_reasons": _clean_reason_items(knowledge_selection.get("selection_reasons")),
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


def run_route_decision(project_id: str) -> int:
    decision = load_uxb_execution_decision(project_id)
    source_path = str(decision.get("source_path") or f"projects/{project_id}/runtime/uxb_route_decision.json")

    if decision.get("status") == "confirmed":
        print(f"UXB execution decision confirmed: {source_path}")
        return 0

    print("Current execution decision requires UXB AI re-judgment. Please update runtime/uxb_route_decision.json first.")
    for item in _clean_string_list(decision.get("validation_errors")):
        print(f"- {item}")
    return 1
