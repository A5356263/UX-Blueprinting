from __future__ import annotations

import json
import os
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
from packages.task_card_resolve import resolve_task_card_file


def to_repo_relative(repo_root: Path, path: Path) -> str:
    return to_repo_ref(path, repo_root)


def _on_rmtree_error(func, path, exc_info) -> None:
    del exc_info
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _selection_reason_by_ref(selection_plan: dict[str, object]) -> dict[str, str]:
    selection_reasons = selection_plan.get("selection_reasons")
    if not isinstance(selection_reasons, list):
        return {}

    normalized: dict[str, str] = {}
    for item in selection_reasons:
        if not isinstance(item, dict):
            continue
        ref = str(item.get("ref") or "").replace("\\", "/").strip()
        if not ref or ref in normalized:
            continue
        normalized[ref] = str(item.get("reason") or "").strip()
    return normalized


def _bundle_reference_label(reference: str, group: str, consumed_by: list[str]) -> str:
    normalized = normalize_repo_ref(reference)
    if group == "template_refs":
        if normalized.startswith("templates/"):
            return f"templates/{normalized[len('templates/'):]}"
        if normalized.startswith("specs/"):
            return f"specs/{normalized[len('specs/'):]}"
        return f"templates/{Path(normalized).name}"
    if group == "check_refs":
        if normalized.startswith("specs/"):
            return f"specs/{normalized[len('specs/'):]}"
        return f"checks/{Path(normalized).name}"
    if group == "summary_refs.business" and normalized.startswith("knowledge/wiki/summaries/业务/"):
        return f"summaries/business/{normalized[len('knowledge/wiki/summaries/业务/'):]}"
    if group == "summary_refs.guideline" and normalized.startswith("knowledge/wiki/summaries/设计准则/"):
        return f"summaries/guideline/{normalized[len('knowledge/wiki/summaries/设计准则/'):]}"
    if group == "summary_refs.business" and normalized.startswith("knowledge/raw/业务/"):
        return f"summaries/business/route_cards/{normalized[len('knowledge/raw/业务/'):]}"
    if group == "summary_refs.complexity":
        complexity_suffix = extract_uxb_complexity_ref_suffix(normalized)
        if complexity_suffix:
            return f"complexity/{complexity_suffix}"
    if group == "raw_refs" and normalized.startswith("knowledge/raw/"):
        stage = consumed_by[0] if consumed_by else "shared"
        return f"raw/{stage}/{normalized[len('knowledge/raw/'):]}"
    return normalized


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


def _knowledge_reference_items(selection_plan: dict[str, object]) -> list[dict[str, object]]:
    summary_refs = selection_plan.get("summary_refs")
    if not isinstance(summary_refs, dict):
        summary_refs = {}
    stage_refs = selection_plan.get("stage_refs")
    if not isinstance(stage_refs, dict):
        stage_refs = {}
    raw_escalation_plan = selection_plan.get("raw_escalation_plan")
    if not isinstance(raw_escalation_plan, list):
        raw_escalation_plan = []

    reason_by_ref = _selection_reason_by_ref(selection_plan)
    items: list[dict[str, object]] = []

    stage_summary_membership: dict[str, list[str]] = {}
    for stage, stage_payload in stage_refs.items():
        if not isinstance(stage_payload, dict):
            continue
        for reference in [str(value).replace("\\", "/").strip() for value in stage_payload.get("summary_refs", []) if str(value).strip()]:
            stage_summary_membership.setdefault(reference, [])
            if stage not in stage_summary_membership[reference]:
                stage_summary_membership[reference].append(str(stage))

    summary_group_by_ref: dict[str, str] = {}
    for category in ("business", "guideline", "complexity"):
        for ref in [str(value).replace("\\", "/").strip() for value in summary_refs.get(category, []) if str(value).strip()]:
            summary_group_by_ref[ref] = f"summary_refs.{category}"

    for ref, consumed_by in stage_summary_membership.items():
        items.append(
            {
                "reference": ref,
                "group": summary_group_by_ref.get(ref, "summary_refs.business"),
                "consumed_by": list(consumed_by),
                "selected_by": "uxb_ai",
                "selection_reason": reason_by_ref.get(ref, ""),
                "routed_by_summary": "",
                "why_summary_not_enough": "",
                "decision_points": [],
            }
        )

    for item in raw_escalation_plan:
        if not isinstance(item, dict):
            continue
        raw_ref = str(item.get("raw_ref") or "").replace("\\", "/").strip()
        if not raw_ref:
            continue
        routed_by_summary = str(item.get("routed_by_summary") or "").replace("\\", "/").strip()
        why_summary_not_enough = str(item.get("why_summary_not_enough") or "").strip()
        decision_points = [str(value).strip() for value in item.get("decision_points", []) if str(value).strip()]
        for stage in [str(value).strip() for value in item.get("used_for_stage", []) if str(value).strip()]:
            items.append(
                {
                    "reference": raw_ref,
                    "group": "raw_refs",
                    "consumed_by": [stage],
                    "selected_by": "uxb_ai",
                    "selection_reason": reason_by_ref.get(raw_ref, why_summary_not_enough),
                    "routed_by_summary": routed_by_summary,
                    "why_summary_not_enough": why_summary_not_enough,
                    "decision_points": decision_points,
                }
            )

    return items


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
    errors = [str(item) for item in selection_plan.get("errors", []) if str(item).strip()]
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    warnings.extend(str(item) for item in selection_plan.get("warnings", []) if str(item).strip())

    reference_items_raw: list[dict[str, object]] = []
    for field, consumed_by in {
        "template_refs": ["facts", "business", "experience"],
        "check_refs": ["gate", "validate"],
    }.items():
        for reference in resolved.get(field, []):
            reference_items_raw.append(
                {
                    "reference": str(reference),
                    "group": field,
                    "consumed_by": list(consumed_by),
                    "selected_by": "",
                    "selection_reason": "",
                    "routed_by_summary": "",
                    "why_summary_not_enough": "",
                    "decision_points": [],
                }
            )

    reference_items_raw.extend(_knowledge_reference_items(selection_plan))
    reference_items = _dedupe_reference_items(reference_items_raw)

    copied: list[dict[str, object]] = []
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
            copied.append(copied_item)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1

    facts_req = resolved.get("facts_output_requirements", {})
    business_req = resolved.get("business_output_requirements", {})
    experience_req = resolved.get("experience_output_requirements", {})
    task_contract = {
        "task_goal": resolved.get("task_goal", []),
        "task_scenario": resolved.get("task_scenario", []),
        "execution_constraints": resolved.get("execution_constraints", []),
        "read_order": resolved.get("read_order", []),
        "notes": resolved.get("notes", []),
        "required_inputs": resolved.get("required_inputs", []),
        "required_outputs": resolved.get("required_outputs", []),
        "domain": resolved.get("domain", ""),
    }

    summary_refs = selection_plan.get("summary_refs", {})
    if not isinstance(summary_refs, dict):
        summary_refs = {}
    knowledge_trace = {
        "summary_refs": {
            "business": list(summary_refs.get("business", [])),
            "guideline": list(summary_refs.get("guideline", [])),
            "complexity": list(summary_refs.get("complexity", [])),
        },
        "raw_escalation_plan": selection_plan.get("raw_escalation_plan", []),
        "stage_refs": selection_plan.get("stage_refs", {}),
    }
    manifest = {
        "task_id": task_id,
        "task_card_source": to_repo_relative(repo_root, task_card_path),
        "selection_source": str(selection_plan.get("selection_source", "")),
        "knowledge_trace": knowledge_trace,
        "assembled_refs": [str(item.get("reference", "")) for item in copied if str(item.get("reference", "")).strip()],
        "missing_refs": [],
        "reference_count": len(copied),
        "task_contract": task_contract,
        "references": copied,
        "warnings": warnings,
        "strict_mode": strict,
        "reference_summary": {
            "template_ref_count": len(resolved.get("template_refs", [])),
            "check_ref_count": len(resolved.get("check_refs", [])),
            "summary_ref_count": sum(len(values) for values in knowledge_trace["summary_refs"].values()),
            "raw_ref_count": len([item for item in copied if str(item.get("group", "")) == "raw_refs"]),
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
