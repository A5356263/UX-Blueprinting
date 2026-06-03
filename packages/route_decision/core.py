from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from packages.common import (
    extract_uxb_complexity_ref_suffix,
    get_project_runtime_dir,
    get_repo_root,
    normalize_repo_ref,
    repo_ref_to_path,
    to_repo_ref,
)

SUPPORTED_UXB_SCHEMA_VERSIONS = {"uxb_route_decision@5.0"}
BUSINESS_OUTPUTS = {
    "business_note.md": "fast",
    "business_blueprint_lite.md": "standard",
    "business_blueprint.md": "full",
}
REQUIRED_CORE_OUTPUTS = {"facts.md", "experience_blueprint.md"}
def _load_json_payload(path: Path) -> tuple[dict[str, Any], str | None]:
    if not path.exists() or not path.is_file():
        return {}, "missing"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return {}, f"invalid_json: line {error.lineno} column {error.colno} ({error.msg})"
    if not isinstance(payload, dict):
        return {}, "invalid_root_type"
    return payload, None


def _clean_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = normalize_repo_ref(str(item))
        if not text or text in seen:
            continue
        seen.add(text)
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


def _validate_ref_exists(repo_root: Path, ref: str, label: str, errors: list[str]) -> None:
    try:
        ref_path = repo_root / repo_ref_to_path(ref)
    except ValueError as exc:
        errors.append(f"{label} is invalid: {exc}")
        return
    if not ref_path.exists():
        errors.append(f"{label} does not exist: {ref}")


def _validate_knowledge_selection(
    knowledge_selection: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    repo_root = get_repo_root()
    errors: list[str] = []
    files = _clean_string_list(knowledge_selection.get("files"))
    reasoning = str(knowledge_selection.get("reasoning") or "").strip()

    if not files:
        errors.append("knowledge_selection.files cannot be empty")
    if not reasoning:
        errors.append("knowledge_selection.reasoning cannot be empty")

    for ref in files:
        if ref.startswith("knowledge/templates/"):
            errors.append(f"knowledge_selection.files cannot include knowledge templates: {ref}")
            continue
        if extract_uxb_complexity_ref_suffix(ref) is None and not ref.startswith("knowledge/"):
            errors.append(f"knowledge_selection.files contains unsupported knowledge ref: {ref}")
            continue
        _validate_ref_exists(repo_root, ref, "knowledge file", errors)

    return {"files": files, "reasoning": reasoning}, errors


def _sorted_repo_refs(paths: list[Path], repo_root: Path) -> list[str]:
    refs = [to_repo_ref(path, repo_root) for path in paths if path.exists() and path.is_file()]
    return sorted(dict.fromkeys(refs))


def _route_decision_option_refs() -> dict[str, list[str]]:
    repo_root = get_repo_root()
    complexity_root = repo_root / ".codex" / "skills" / "uxb" / "references" / "complexity"
    summaries_root = repo_root / "knowledge" / "wiki" / "summaries"
    raw_business_root = repo_root / "knowledge" / "raw" / "业务"

    complexity_refs = _sorted_repo_refs(list(complexity_root.rglob("*.md")), repo_root) if complexity_root.exists() else []

    guideline_paths: list[Path] = []
    business_summary_paths: list[Path] = []
    if summaries_root.exists():
        for path in summaries_root.rglob("*.md"):
            relative_ref = to_repo_ref(path, repo_root)
            if relative_ref.startswith("knowledge/wiki/summaries/设计准则/"):
                guideline_paths.append(path)
            else:
                business_summary_paths.append(path)

    business_entry_paths: list[Path] = []
    if raw_business_root.exists():
        for path in raw_business_root.rglob("README.md"):
            business_entry_paths.append(path)
        for path in raw_business_root.rglob("00_领域概述.md"):
            business_entry_paths.append(path)

    return {
        "complexity": complexity_refs,
        "business_summary": _sorted_repo_refs(business_summary_paths, repo_root),
        "business_entry": _sorted_repo_refs(business_entry_paths, repo_root),
        "guideline": _sorted_repo_refs(guideline_paths, repo_root),
    }


def load_uxb_execution_decision(project_id: str) -> dict[str, Any]:
    path = _uxb_route_decision_path(project_id)
    payload, load_error = _load_json_payload(path)
    validation_errors: list[str] = []

    if load_error == "missing":
        validation_errors.append("Missing runtime/uxb_route_decision.json")
    elif load_error == "invalid_root_type":
        validation_errors.append("runtime/uxb_route_decision.json must be a JSON object")
    elif load_error and load_error.startswith("invalid_json:"):
        validation_errors.append(
            "runtime/uxb_route_decision.json is invalid JSON: "
            + load_error[len("invalid_json: ") :]
            + ". Common causes: unescaped ASCII double quotes inside string values, or writing explanation prose into the JSON file."
        )

    if not payload:
        return {
            "project_id": project_id,
            "status": "needs_rejudgment",
            "source_path": f"projects/{project_id}/runtime/uxb_route_decision.json",
            "required_outputs": [],
            "execution_mode": "",
            "knowledge_selection": {"files": [], "reasoning": ""},
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


def run_route_decision_options(project_id: str) -> int:
    del project_id
    refs = _route_decision_option_refs()

    sections = [
        ("可用 complexity refs：", refs["complexity"]),
        ("可用 business summary refs：", refs["business_summary"]),
        ("可用 business entry refs：", refs["business_entry"]),
        ("可用 guideline summary refs：", refs["guideline"]),
    ]
    for title, items in sections:
        print(title)
        if not items:
            print("- <none>")
        else:
            for item in items:
                print(f"- {item}")
        print("")
    return 0
