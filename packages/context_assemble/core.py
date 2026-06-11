from __future__ import annotations

import json
import shutil
import stat
from pathlib import Path

from packages.common import (
    extract_uxb_complexity_ref_suffix,
    get_project_runtime_dir,
    get_repo_root,
    normalize_repo_ref,
    repo_ref_to_path,
    to_repo_ref,
)
from packages.knowledge_consumption import build_knowledge_consumption_plan
from packages.provenance import append_command_if_provenance_exists
from packages.route_decision import load_uxb_execution_decision
from packages.task_card_resolve import resolve_task_card_file


def to_repo_relative(repo_root: Path, path: Path) -> str:
    return to_repo_ref(path, repo_root)


def _on_rmtree_error(func, path, exc_info) -> None:
    del exc_info
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _bundle_reference_label(reference: str, group: str, consumed_by: list[str]) -> str:
    normalized = normalize_repo_ref(reference)
    if group == "shared_input":
        return f"shared/{Path(normalized).name}"
    if group == "template_refs":
        stage = consumed_by[0] if consumed_by else "shared"
        if normalized.startswith("templates/"):
            return f"{stage}/templates/{normalized[len('templates/'):]}"
        if normalized.startswith("specs/"):
            return f"{stage}/specs/{normalized[len('specs/'):]}"
        return f"{stage}/templates/{Path(normalized).name}"
    if group == "check_refs":
        stage = consumed_by[0] if consumed_by else "gate"
        if normalized.startswith("specs/"):
            return f"{stage}/specs/{normalized[len('specs/'):]}"
        return f"{stage}/checks/{Path(normalized).name}"
    shared_prefix = "shared" if len(consumed_by) > 1 else (consumed_by[0] if consumed_by else "shared")
    if group == "business_summary":
        return f"{shared_prefix}/summaries/business/{Path(normalized).name}"
    if group == "guideline_summary":
        return f"{shared_prefix}/summaries/guideline/{Path(normalized).name}"
    if group == "complexity_ref":
        complexity_suffix = extract_uxb_complexity_ref_suffix(normalized)
        if complexity_suffix:
            return f"{shared_prefix}/complexity/{complexity_suffix}"
    if group == "raw_ref" and normalized.startswith("knowledge/raw/"):
        return f"{shared_prefix}/raw/{normalized[len('knowledge/raw/'):]}"
    return f"{shared_prefix}/{normalized}"


def copy_path(repo_root: Path, target_root: Path, source_path: Path, reference_label: str) -> dict[str, str]:
    destination = target_root / repo_ref_to_path(reference_label)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if source_path.is_dir():
        shutil.copytree(source_path, destination, dirs_exist_ok=True)
        ref_type = "directory"
    else:
        shutil.copy2(source_path, destination)
        ref_type = "file"

    return {
        "reference": reference_label,
        "type": ref_type,
        "source": to_repo_relative(repo_root, source_path),
        "destination": to_repo_relative(repo_root, destination),
    }


def resolve_reference_for_copy(repo_root: Path, reference: str) -> str:
    normalized_ref = normalize_repo_ref(reference)
    if not normalized_ref:
        raise ValueError("Reference cannot be empty")
    source = repo_root / repo_ref_to_path(normalized_ref)
    if not source.exists():
        raise FileNotFoundError(f"Reference not found: {normalized_ref}")
    return normalized_ref


def safe_rmtree(path: Path) -> None:
    if not path.exists():
        return
    try:
        shutil.rmtree(path, onexc=_on_rmtree_error)
    except TypeError:
        shutil.rmtree(path, onerror=_on_rmtree_error)


def _knowledge_group(reference: str) -> str:
    normalized = normalize_repo_ref(reference)
    if extract_uxb_complexity_ref_suffix(normalized) is not None:
        return "complexity_ref"
    if normalized.startswith("knowledge/wiki/summaries/设计准则/"):
        return "guideline_summary"
    if normalized.startswith("knowledge/wiki/summaries/"):
        return "business_summary"
    if normalized.startswith("knowledge/raw/"):
        return "raw_ref"
    return "knowledge_ref"


def _stage_consumed_by(group: str, reference: str) -> list[str]:
    normalized = normalize_repo_ref(reference)
    if group == "template_refs":
        if normalized.endswith("gap_list.template.md") or normalized.endswith("check_report.template.md"):
            return []
        if normalized.endswith("facts.template.md") or normalized.endswith("08_fact_extraction_contract.md"):
            return ["facts"]
        if (
            normalized.endswith("business_blueprint.template.md")
            or normalized.endswith("business_blueprint_lite.template.md")
            or normalized.endswith("business_note.template.md")
            or normalized.endswith("09_business_blueprint_contract.md")
            or normalized.endswith("16_business_note_contract.md")
            or normalized.endswith("17_business_blueprint_lite_contract.md")
        ):
            return ["business"]
        if normalized.endswith("experience_blueprint.template.md") or normalized.endswith("10_experience_blueprint_contract.md"):
            return ["experience"]
        return ["facts", "business", "experience"]
    if group == "check_refs":
        return ["gate", "validate", "coverage"]
    if group == "guideline_summary":
        return ["experience"]
    if group == "complexity_ref":
        return ["business", "experience"]
    return ["facts", "business", "experience"]


def _knowledge_reference_items(selection_plan: dict[str, object]) -> list[dict[str, object]]:
    files = selection_plan.get("files")
    if not isinstance(files, list):
        files = []
    reasoning = str(selection_plan.get("reasoning") or "").strip()

    items: list[dict[str, object]] = []
    for reference in [str(value).replace("\\", "/").strip() for value in files if str(value).strip()]:
        group = _knowledge_group(reference)
        items.append(
            {
                "reference": reference,
                "group": group,
                "consumed_by": _stage_consumed_by(group, reference),
                "selected_by": "uxb_ai",
                "selection_reason": reasoning,
                "routed_by_summary": "",
                "why_summary_not_enough": "",
                "decision_points": [],
            }
        )
    return items


def _shared_input_items(task_id: str) -> list[dict[str, object]]:
    return [
        {
            "reference": f"projects/{task_id}/source/requirement.md",
            "group": "shared_input",
            "consumed_by": ["facts", "business", "experience"],
            "selected_by": "",
            "selection_reason": "",
            "routed_by_summary": "",
            "why_summary_not_enough": "",
            "decision_points": [],
        },
        {
            "reference": f"projects/{task_id}/source/background.md",
            "group": "shared_input",
            "consumed_by": ["facts", "business", "experience"],
            "selected_by": "",
            "selection_reason": "",
            "routed_by_summary": "",
            "why_summary_not_enough": "",
            "decision_points": [],
        },
    ]


def _build_stage_contexts(task_id: str, copied: list[dict[str, object]], execution_mode: str) -> dict[str, list[str]]:
    business_output = {
        "fast": f"projects/{task_id}/workspace/business_note.md",
        "standard": f"projects/{task_id}/workspace/business_blueprint_lite.md",
        "full": f"projects/{task_id}/workspace/business_blueprint.md",
    }.get(execution_mode, f"projects/{task_id}/workspace/business_blueprint.md")
    stage_contexts: dict[str, list[str]] = {
        "facts": [
            f"projects/{task_id}/source/requirement.md",
            f"projects/{task_id}/source/background.md",
        ],
        "business": [
            f"projects/{task_id}/workspace/facts.md",
            f"projects/{task_id}/source/requirement.md",
            f"projects/{task_id}/source/background.md",
        ],
        "experience": [
            f"projects/{task_id}/workspace/facts.md",
            business_output,
            f"projects/{task_id}/source/requirement.md",
            f"projects/{task_id}/source/background.md",
        ],
        "gate": [
            f"projects/{task_id}/source/requirement.md",
            f"projects/{task_id}/source/background.md",
            f"projects/{task_id}/runtime/uxb_route_decision.json",
        ],
        "validate": [
            f"projects/{task_id}/source/requirement.md",
            f"projects/{task_id}/source/background.md",
            f"projects/{task_id}/runtime/uxb_route_decision.json",
            f"projects/{task_id}/runtime/context_manifest.json",
        ],
        "coverage": [
            f"projects/{task_id}/source/requirement.md",
            f"projects/{task_id}/source/background.md",
            f"projects/{task_id}/runtime/uxb_route_decision.json",
            f"projects/{task_id}/runtime/context_manifest.json",
        ],
    }

    for item in copied:
        destination = str(item.get("destination", "")).replace("\\", "/").strip()
        if not destination:
            continue
        consumed_by = [str(value).strip() for value in item.get("consumed_by", []) if str(value).strip()]
        for stage in consumed_by:
            stage_contexts.setdefault(stage, [])
            if destination not in stage_contexts[stage]:
                stage_contexts[stage].append(destination)
    return stage_contexts


def _dedupe_reference_items(items: list[dict[str, object]]) -> list[dict[str, object]]:
    deduped: dict[tuple[str, str, str], dict[str, object]] = {}
    for item in items:
        consumed_by = list(item.get("consumed_by", []))
        stage_key = ",".join(consumed_by)
        key = (str(item.get("group", "")), str(item.get("reference", "")), stage_key)
        if key in deduped:
            continue
        deduped[key] = {
            "reference": str(item.get("reference", "")),
            "group": str(item.get("group", "")),
            "consumed_by": consumed_by,
            "selected_by": str(item.get("selected_by", "")),
            "selection_reason": str(item.get("selection_reason", "")),
            "routed_by_summary": str(item.get("routed_by_summary", "")),
            "why_summary_not_enough": str(item.get("why_summary_not_enough", "")),
            "decision_points": list(item.get("decision_points", [])),
        }
    return list(deduped.values())


def _compact_reference_item(item: dict[str, object]) -> dict[str, object]:
    compact = {
        "reference": str(item.get("reference", "")),
        "group": str(item.get("group", "")),
        "consumed_by": [str(value) for value in item.get("consumed_by", []) if str(value).strip()],
        "source": str(item.get("source", "")),
        "destination": str(item.get("destination", "")),
        "exists": bool(item.get("exists")),
        "copied": bool(item.get("copied")),
    }
    selection_reason = str(item.get("selection_reason", "")).strip()
    if selection_reason:
        compact["selection_reason"] = selection_reason
    return compact


def run_context_assemble(task_id: str, strict: bool = False) -> int:
    repo_root = get_repo_root()
    runtime_dir = get_project_runtime_dir(task_id)
    context_bundle_dir = runtime_dir / "context_bundle"
    if context_bundle_dir.exists():
        safe_rmtree(context_bundle_dir)
    context_bundle_dir.mkdir(parents=True, exist_ok=True)

    resolved, task_card_path = resolve_task_card_file(task_id)
    if resolved["errors"]:
        for error in resolved["errors"]:
            print(f"ERROR: {error}")
        print(f"Task card parse failed: {task_card_path}")
        return 1

    warnings = list(resolved.get("warnings", []))
    selection_plan = build_knowledge_consumption_plan(task_id)
    decision = load_uxb_execution_decision(task_id)
    errors = [str(item) for item in selection_plan.get("errors", []) if str(item).strip()]
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    warnings.extend(str(item) for item in selection_plan.get("warnings", []) if str(item).strip())

    reference_items_raw: list[dict[str, object]] = []
    for field in ("template_refs", "check_refs"):
        for reference in resolved.get(field, []):
            reference_items_raw.append(
                {
                    "reference": str(reference),
                    "group": field,
                    "consumed_by": _stage_consumed_by(field, str(reference)),
                    "selected_by": "",
                    "selection_reason": "",
                    "routed_by_summary": "",
                    "why_summary_not_enough": "",
                    "decision_points": [],
                }
            )

    reference_items_raw.extend(_shared_input_items(task_id))
    reference_items_raw.extend(_knowledge_reference_items(selection_plan))
    reference_items = _dedupe_reference_items(reference_items_raw)

    copied: list[dict[str, object]] = []
    excluded_refs: list[dict[str, str]] = []
    try:
        for item in reference_items:
            reference = str(item["reference"])
            resolved_reference = resolve_reference_for_copy(repo_root, reference)
            source_path = repo_root / repo_ref_to_path(resolved_reference)
            copied_item = dict(item)
            bundle_reference = _bundle_reference_label(reference, str(item.get("group", "")), list(item.get("consumed_by", [])))
            copied_item.update(copy_path(repo_root, context_bundle_dir, source_path, bundle_reference))
            copied_item["requested_reference"] = reference
            copied_item["reference"] = reference
            copied_item["exists"] = True
            copied_item["copied"] = True
            copied.append(_compact_reference_item(copied_item))
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1

    facts_req = resolved.get("facts_output_requirements", {})
    business_req = resolved.get("business_output_requirements", {})
    experience_req = resolved.get("experience_output_requirements", {})
    task_contract = {
        "execution_constraints": resolved.get("execution_constraints", []),
        "required_inputs": resolved.get("required_inputs", []),
        "required_outputs": resolved.get("required_outputs", []),
        "domain": resolved.get("domain", ""),
    }

    knowledge_trace = {
        "files": list(selection_plan.get("files", [])) if isinstance(selection_plan.get("files"), list) else [],
        "reasoning": str(selection_plan.get("reasoning") or "").strip(),
    }
    stage_contexts = _build_stage_contexts(task_id, copied, str(decision.get("execution_mode") or ""))
    manifest = {
        "task_id": task_id,
        "task_card_source": to_repo_relative(repo_root, task_card_path),
        "selection_source": str(selection_plan.get("selection_source", "")),
        "knowledge_trace": knowledge_trace,
        "assembled_refs": [str(item.get("reference", "")) for item in copied if str(item.get("reference", "")).strip()],
        "missing_refs": [],
        "excluded_refs": excluded_refs,
        "reference_count": len(copied),
        "task_contract": task_contract,
        "references": copied,
        "warnings": warnings,
        "strict_mode": strict,
        "stage_contexts": stage_contexts,
        "reference_summary": {
            "template_ref_count": len(resolved.get("template_refs", [])),
            "check_ref_count": len(resolved.get("check_refs", [])),
            "knowledge_file_count": len(knowledge_trace["files"]),
            "raw_ref_count": len([item for item in copied if str(item.get("group", "")) == "raw_ref"]),
            "assembled_ref_count": len(copied),
        },
        "stage_boundaries": {
            "facts": facts_req.get("boundary", []),
            "business": business_req.get("boundary", []),
            "experience": experience_req.get("boundary", []),
        },
        "facts_extraction_boundary": facts_req.get("boundary", []),
        "business_judgment_boundary": business_req.get("boundary", []),
        "experience_translation_boundary": experience_req.get("boundary", []),
    }
    manifest_path = runtime_dir / "context_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (runtime_dir / "knowledge_trace.json").write_text(json.dumps(knowledge_trace, ensure_ascii=False, indent=2), encoding="utf-8")

    for warning in warnings:
        print(f"WARNING: {warning}")
    print(f"Task card parsed: {task_card_path}")
    print(f"Context assembled: {manifest_path}")
    append_command_if_provenance_exists(task_id, "assemble")
    return 0
