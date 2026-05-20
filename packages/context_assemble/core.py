from __future__ import annotations

import json
import os
import shutil
import stat
from pathlib import Path

from packages.common import get_project_runtime_dir, get_repo_root
from packages.knowledge_consumption import build_knowledge_consumption_plan
from packages.provenance import append_command_if_provenance_exists
from packages.task_card_resolve import resolve_task_card_file


def to_repo_relative(repo_root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")


def _on_rmtree_error(func, path, exc_info) -> None:
    os.chmod(path, stat.S_IWRITE)
    func(path)


def copy_path(repo_root: Path, target_root: Path, source_path: Path, reference_label: str, ref_type: str) -> dict[str, str]:
    destination = target_root / Path(reference_label.replace("/", "\\"))
    destination.parent.mkdir(parents=True, exist_ok=True)

    if source_path.is_dir():
        shutil.copytree(source_path, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(source_path, destination)

    return {
        "reference": reference_label,
        "type": ref_type,
        "source": to_repo_relative(repo_root, source_path),
        "destination": to_repo_relative(repo_root, destination),
    }


def find_candidate_index(repo_root: Path, directory_ref: str, primary_entries: list[str]) -> str | None:
    normalized_ref = directory_ref.replace("\\", "/").rstrip("/")
    directory_path = repo_root / Path(normalized_ref.replace("/", "\\"))
    if not directory_path.exists() or not directory_path.is_dir():
        return None

    for entry in primary_entries:
        normalized_entry = entry.replace("\\", "/")
        if not normalized_entry.startswith(f"{normalized_ref}/"):
            continue
        entry_path = repo_root / Path(normalized_entry.replace("/", "\\"))
        if entry_path.exists() and entry_path.is_file():
            return normalized_entry

    candidates = [
        directory_path / "README.md",
        directory_path / "index.md",
        directory_path / f"{directory_path.name}-index.md",
        directory_path / f"{directory_path.name}-domain-index.md",
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return to_repo_relative(repo_root, candidate)
    return None


def resolve_reference_for_copy(
    repo_root: Path,
    reference: str,
    primary_entries: list[str],
    strict: bool,
    warnings: list[str],
    narrowing_actions: list[dict[str, str]],
) -> tuple[str, str]:
    normalized_ref = reference.replace("\\", "/").strip()
    source = repo_root / Path(normalized_ref.replace("/", "\\"))
    if not source.exists():
        raise FileNotFoundError(f"Reference not found: {normalized_ref}")
    if "*" in normalized_ref or "?" in normalized_ref:
        raise ValueError(f"Wildcard reference cannot be copied directly: {normalized_ref}")
    if source.is_file():
        return normalized_ref, "file"

    resolved_index = find_candidate_index(repo_root, normalized_ref, primary_entries)
    if resolved_index:
        narrowing_actions.append(
            {
                "reference": normalized_ref,
                "resolved_to": resolved_index,
                "action": "directory_to_index",
            }
        )
        return resolved_index, "index"

    if strict:
        raise ValueError(f"Unresolved directory reference in strict mode: {normalized_ref}")

    warnings.append(f"Directory reference copied as fallback because no stable index entry was found: {normalized_ref}")
    narrowing_actions.append(
        {
            "reference": normalized_ref,
            "resolved_to": normalized_ref,
            "action": "directory_fallback_copy",
        }
    )
    return normalized_ref, "directory"


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


def _selected_reference_items(selection_plan: dict[str, object]) -> list[dict[str, object]]:
    selected_refs = selection_plan.get("selected_refs")
    if not isinstance(selected_refs, dict):
        return []

    consumed_by_map = {
        "business_refs": ["business", "experience"],
        "guideline_refs": ["experience"],
        "complexity_refs": ["facts", "business", "experience"],
    }
    reason_by_ref = _selection_reason_by_ref(selection_plan)
    items: list[dict[str, object]] = []

    for group, consumed_by in consumed_by_map.items():
        refs = selected_refs.get(group, [])
        if not isinstance(refs, list):
            continue
        for ref in refs:
            normalized_ref = str(ref).replace("\\", "/").strip()
            if not normalized_ref:
                continue
            items.append(
                {
                    "reference": normalized_ref,
                    "group": group,
                    "consumed_by": list(consumed_by),
                    "selected_by": "uxb_ai",
                    "selection_reason": reason_by_ref.get(normalized_ref, ""),
                }
            )
    return items


def _dedupe_reference_items(items: list[dict[str, object]]) -> list[dict[str, object]]:
    deduped: dict[tuple[str, str], dict[str, object]] = {}
    for item in items:
        key = (str(item.get("group", "")), str(item.get("reference", "")))
        existing = deduped.get(key)
        if existing is None:
            deduped[key] = {
                "reference": str(item.get("reference", "")),
                "group": str(item.get("group", "")),
                "consumed_by": list(item.get("consumed_by", [])),
                "selected_by": str(item.get("selected_by", "")),
                "selection_reason": str(item.get("selection_reason", "")),
            }
            continue

        existing["consumed_by"] = sorted(set(existing.get("consumed_by", []) + list(item.get("consumed_by", []))))
        if not existing.get("selected_by") and item.get("selected_by"):
            existing["selected_by"] = str(item.get("selected_by", ""))
        if not existing.get("selection_reason") and item.get("selection_reason"):
            existing["selection_reason"] = str(item.get("selection_reason", ""))
    return list(deduped.values())


def run_context_assemble(task_id: str, strict: bool = False) -> int:
    repo_root = get_repo_root()
    runtime_dir = get_project_runtime_dir(task_id)
    context_bundle_dir = runtime_dir / "context_bundle"
    if context_bundle_dir.exists():
        shutil.rmtree(context_bundle_dir, onexc=_on_rmtree_error)
    context_bundle_dir.mkdir(parents=True, exist_ok=True)

    resolved, resolved_path = resolve_task_card_file(task_id, write_output=True)
    if resolved["errors"]:
        for error in resolved["errors"]:
            print(f"ERROR: {error}")
        print(f"Task card resolution failed: {resolved_path}")
        return 1

    warnings = list(resolved.get("warnings", []))
    primary_entries = [str(item) for item in resolved.get("primary_knowledge_entries", [])]
    selection_plan = build_knowledge_consumption_plan(task_id)

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
                }
            )

    reference_items_raw.extend(_selected_reference_items(selection_plan))
    reference_items = _dedupe_reference_items(reference_items_raw)

    copied: list[dict[str, object]] = []
    directory_refs_detected: list[str] = []
    directory_refs_resolved_to_index: list[dict[str, str]] = []
    directory_refs_fallback_copied: list[str] = []
    narrowed_references: list[dict[str, str]] = []
    primary_entries_used: list[str] = []
    broad_reference_warnings: list[str] = []

    try:
        for item in reference_items:
            reference = str(item["reference"])
            resolved_reference, resolved_type = resolve_reference_for_copy(
                repo_root,
                reference,
                primary_entries,
                strict,
                warnings,
                narrowed_references,
            )
            source_path = repo_root / Path(resolved_reference.replace("/", "\\"))
            copied_item = dict(item)
            copied_item.update(copy_path(repo_root, context_bundle_dir, source_path, resolved_reference, resolved_type))
            copied_item["requested_reference"] = reference
            copied_item["exists"] = True
            copied_item["copied"] = True
            copied.append(copied_item)

            original_source = repo_root / Path(reference.replace("/", "\\"))
            if original_source.exists() and original_source.is_dir():
                directory_refs_detected.append(reference)
                if resolved_reference != reference:
                    directory_refs_resolved_to_index.append(
                        {
                            "reference": reference,
                            "resolved_to": resolved_reference,
                        }
                    )
                elif resolved_type == "directory":
                    directory_refs_fallback_copied.append(reference)
                    broad_reference_warnings.append(f"Directory reference copied without narrowing: {reference}")

            if resolved_reference in primary_entries and resolved_reference not in primary_entries_used:
                primary_entries_used.append(resolved_reference)
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
    }

    manifest = {
        "task_id": task_id,
        "resolved_from": to_repo_relative(repo_root, resolved_path),
        "selection_source": str(selection_plan.get("selection_source", "")),
        "reference_count": len(copied),
        "task_contract": task_contract,
        "references": copied,
        "warnings": warnings,
        "strict_mode": strict,
        "directory_refs_detected": sorted(set(directory_refs_detected)),
        "directory_refs_resolved_to_index": directory_refs_resolved_to_index,
        "directory_refs_fallback_copied": sorted(set(directory_refs_fallback_copied)),
        "narrowed_references": narrowed_references,
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

    selected_refs = selection_plan.get("selected_refs", {})
    usage_report = {
        "task_id": task_id,
        "selection_source": str(selection_plan.get("selection_source", "")),
        "selected_refs": {
            "business_refs": list(selected_refs.get("business_refs", [])) if isinstance(selected_refs, dict) else [],
            "guideline_refs": list(selected_refs.get("guideline_refs", [])) if isinstance(selected_refs, dict) else [],
            "complexity_refs": list(selected_refs.get("complexity_refs", [])) if isinstance(selected_refs, dict) else [],
        },
        "assembled_refs": [str(item.get("reference", "")) for item in copied if str(item.get("reference", "")).strip()],
        "missing_refs": [],
        "notes": [
            "本报告只记录 UXB AI 指定资料的装配情况，不代表代码做了知识选择。",
        ],
        "reference_summary": {
            "template_ref_count": len(resolved.get("template_refs", [])),
            "check_ref_count": len(resolved.get("check_refs", [])),
            "selected_ref_count": len([item for item in copied if str(item.get("selected_by", "")) == "uxb_ai"]),
            "assembled_ref_count": len(copied),
        },
        "references": [
            {
                "reference": item.get("reference"),
                "requested_reference": item.get("requested_reference"),
                "group": item.get("group"),
                "type": item.get("type"),
                "consumed_by": item.get("consumed_by"),
                "selected_by": item.get("selected_by"),
                "selection_reason": item.get("selection_reason"),
            }
            for item in copied
        ],
        "assembly_details": {
            "generated_from": to_repo_relative(repo_root, manifest_path),
            "primary_entries_used": sorted(set(primary_entries_used)),
            "narrowing_actions": narrowed_references,
            "broad_reference_warnings": broad_reference_warnings,
        },
    }
    usage_report_path = runtime_dir / "knowledge_usage_report.json"
    usage_report_path.write_text(json.dumps(usage_report, ensure_ascii=False, indent=2), encoding="utf-8")

    for warning in warnings:
        print(f"WARNING: {warning}")
    print(f"Task card resolved: {resolved_path}")
    print(f"Context assembled: {manifest_path}")
    append_command_if_provenance_exists(task_id, "assemble")
    return 0
