from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from packages.common import get_project_runtime_dir, get_repo_root


SUPPORTED_UXB_SCHEMA_VERSIONS = {"uxb_route_decision@4.0"}
BUSINESS_OUTPUTS = {
    "business_note.md": "fast",
    "business_blueprint_lite.md": "standard",
    "business_blueprint.md": "full",
}
REQUIRED_CORE_OUTPUTS = {"facts.md", "experience_blueprint.md"}
ALLOWED_STAGES = {"facts", "business", "experience"}


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
    seen: set[str] = set()
    for item in value:
        text = str(item).replace("\\", "/").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        cleaned.append(text)
    return cleaned


def _clean_stage_list(value: object) -> list[str]:
    values = [item for item in _clean_string_list(value) if item in ALLOWED_STAGES]
    return values


def _clean_reason_items(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    cleaned: list[dict[str, Any]] = []
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
        cleaned.append(
            {
                "ref": ref,
                "type": str(item.get("type") or "").strip(),
                "used_for_stage": _clean_stage_list(item.get("used_for_stage")),
                "reason": reason,
            }
        )
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


def _is_allowed_summary_route_ref(ref: str, group: str) -> bool:
    if group == "complexity":
        return ref.startswith(".claude/skills/uxb/references/complexity/")
    if ref.startswith("knowledge/wiki/summaries/"):
        return True
    if group == "business" and ref.startswith("knowledge/raw/业务/") and (
        ref.endswith("/README.md") or ref.endswith("/00_领域概述.md")
    ):
        return True
    return False


def _normalize_stage_refs(value: object) -> dict[str, dict[str, list[str]]]:
    stage_refs = value if isinstance(value, dict) else {}
    normalized: dict[str, dict[str, list[str]]] = {}
    for stage in sorted(ALLOWED_STAGES):
        stage_payload = stage_refs.get(stage) if isinstance(stage_refs, dict) else {}
        if not isinstance(stage_payload, dict):
            stage_payload = {}
        normalized[stage] = {
            "raw_refs": _clean_string_list(stage_payload.get("raw_refs")),
        }
    return normalized


def _normalize_raw_escalation_plan(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    plan: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            continue
        raw_ref = str(item.get("raw_ref") or "").replace("\\", "/").strip()
        if not raw_ref or raw_ref in seen:
            continue
        seen.add(raw_ref)
        plan.append(
            {
                "raw_ref": raw_ref,
                "routed_by_summary": str(item.get("routed_by_summary") or "").replace("\\", "/").strip(),
                "why_summary_not_enough": str(item.get("why_summary_not_enough") or "").strip(),
                "used_for_stage": _clean_stage_list(item.get("used_for_stage")),
                "decision_points": _clean_string_list(item.get("decision_points")),
            }
        )
    return plan


def _validate_ref_exists(repo_root: Path, ref: str, label: str, errors: list[str]) -> None:
    ref_path = repo_root / Path(ref.replace("/", "\\"))
    if not ref_path.exists():
        errors.append(f"{label} does not exist: {ref}")


def _validate_knowledge_selection(
    knowledge_selection: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    repo_root = get_repo_root()
    errors: list[str] = []

    raw_summary_refs = knowledge_selection.get("summary_refs")
    if not isinstance(raw_summary_refs, dict):
        raw_summary_refs = {}
        errors.append("uxb_route_decision.knowledge_selection.summary_refs must be an object")

    summary_refs = {
        "business": _clean_string_list(raw_summary_refs.get("business")),
        "guideline": _clean_string_list(raw_summary_refs.get("guideline")),
        "complexity": _clean_string_list(raw_summary_refs.get("complexity")),
    }

    if not summary_refs["business"]:
        errors.append("knowledge_selection.summary_refs.business cannot be empty")
    if not summary_refs["complexity"]:
        errors.append("knowledge_selection.summary_refs.complexity cannot be empty")

    for group, refs in summary_refs.items():
        for ref in refs:
            if not _is_allowed_summary_route_ref(ref, group):
                errors.append(
                    f"knowledge_selection.summary_refs.{group} contains unsupported route ref: {ref}"
                )
                continue
            if ref.startswith("knowledge/raw/") and not (ref.endswith("/README.md") or ref.endswith("/00_领域概述.md")):
                errors.append(f"raw ref cannot appear directly in summary_refs: {ref}")
            _validate_ref_exists(repo_root, ref, f"summary ref ({group})", errors)

    raw_escalation_plan = _normalize_raw_escalation_plan(knowledge_selection.get("raw_escalation_plan"))
    raw_by_ref = {item["raw_ref"]: item for item in raw_escalation_plan}
    declared_route_refs = set(summary_refs["business"] + summary_refs["guideline"])

    for item in raw_escalation_plan:
        raw_ref = str(item["raw_ref"])
        routed_by_summary = str(item["routed_by_summary"])
        why_summary_not_enough = str(item["why_summary_not_enough"])
        used_for_stage = list(item["used_for_stage"])
        decision_points = list(item["decision_points"])

        if not raw_ref.startswith("knowledge/raw/"):
            errors.append(f"raw_escalation_plan.raw_ref must start with knowledge/raw/: {raw_ref}")
        _validate_ref_exists(repo_root, raw_ref, "raw escalation ref", errors)

        if not routed_by_summary:
            errors.append(f"raw escalation entry is missing routed_by_summary: {raw_ref}")
        elif routed_by_summary not in declared_route_refs:
            errors.append(
                f"raw escalation entry routed_by_summary must be declared in summary_refs.business/guideline: {raw_ref}"
            )
        else:
            _validate_ref_exists(repo_root, routed_by_summary, "routed_by_summary", errors)

        if not why_summary_not_enough:
            errors.append(f"raw escalation entry is missing why_summary_not_enough: {raw_ref}")
        if not used_for_stage:
            errors.append(f"raw escalation entry is missing used_for_stage: {raw_ref}")
        if not decision_points:
            errors.append(f"raw escalation entry is missing decision_points: {raw_ref}")

    stage_refs = _normalize_stage_refs(knowledge_selection.get("stage_refs"))
    for stage, stage_payload in stage_refs.items():
        for raw_ref in stage_payload.get("raw_refs", []):
            if raw_ref not in raw_by_ref:
                errors.append(f"stage_refs.{stage}.raw_refs contains undeclared raw ref: {raw_ref}")
                continue
            if stage not in raw_by_ref[raw_ref]["used_for_stage"]:
                errors.append(
                    f"stage_refs.{stage}.raw_refs contains raw ref not granted for this stage: {raw_ref}"
                )

    selection_reasons = _clean_reason_items(knowledge_selection.get("selection_reasons"))
    reason_map = {str(item.get("ref") or ""): str(item.get("reason") or "").strip() for item in selection_reasons}
    required_reason_refs = set(summary_refs["business"] + summary_refs["guideline"] + summary_refs["complexity"] + list(raw_by_ref.keys()))
    for ref in sorted(required_reason_refs):
        if not reason_map.get(ref):
            errors.append(f"knowledge_selection.selection_reasons is missing reason for ref: {ref}")

    return (
        {
            "summary_refs": summary_refs,
            "raw_escalation_plan": raw_escalation_plan,
            "stage_refs": stage_refs,
            "selection_reasons": selection_reasons,
        },
        errors,
    )


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
                "summary_refs": {"business": [], "guideline": [], "complexity": []},
                "raw_escalation_plan": [],
                "stage_refs": {stage: {"raw_refs": []} for stage in sorted(ALLOWED_STAGES)},
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

    knowledge_selection_raw = payload.get("knowledge_selection")
    if not isinstance(knowledge_selection_raw, dict):
        knowledge_selection_raw = {}
        validation_errors.append("uxb_route_decision.knowledge_selection must be an object")

    normalized_knowledge_selection, knowledge_errors = _validate_knowledge_selection(knowledge_selection_raw)
    validation_errors.extend(knowledge_errors)

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
