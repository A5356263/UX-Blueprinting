from __future__ import annotations

import json
import os
import stat
import shutil
from pathlib import Path

from packages.common import get_project_runtime_dir, get_repo_root
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
    fallback_refs = [str(item) for item in resolved.get("fallback_source_refs", [])]

    consumption_map = {
        "knowledge_refs": ["facts", "business", "experience"],
        "wiki_refs": ["facts", "business", "experience"],
        "template_refs": ["facts", "business", "experience"],
        "check_refs": ["gate", "validate"],
    }

    reference_items: list[dict[str, object]] = []
    for field in ("knowledge_refs", "wiki_refs", "template_refs", "check_refs"):
        for reference in resolved.get(field, []):
            reference_items.append(
                {
                    "reference": str(reference),
                    "group": field,
                    "consumed_by": consumption_map[field],
                }
            )

    copied: list[dict[str, object]] = []
    directory_refs_detected: list[str] = []
    directory_refs_resolved_to_index: list[dict[str, str]] = []
    directory_refs_fallback_copied: list[str] = []
    narrowed_references: list[dict[str, str]] = []
    primary_entries_used: list[str] = []
    fallback_sources_used: list[str] = []
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
            if reference in fallback_refs and reference not in fallback_sources_used:
                fallback_sources_used.append(reference)
            if resolved_reference in fallback_refs and resolved_reference not in fallback_sources_used:
                fallback_sources_used.append(resolved_reference)
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
        "reference_count": len(copied),
        "task_contract": task_contract,
        "references": copied,
        "warnings": warnings,
        "knowledge_entry_mode": "summary_first_with_raw_fallback",
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

    usage_report = {
        "task_id": task_id,
        "generated_from": to_repo_relative(repo_root, manifest_path),
        "mainline_knowledge_policy": "summary_first_with_raw_fallback",
        "reference_summary": {
            "knowledge_ref_count": len(resolved.get("knowledge_refs", [])),
            "wiki_ref_count": len(resolved.get("wiki_refs", [])),
            "template_ref_count": len(resolved.get("template_refs", [])),
            "check_ref_count": len(resolved.get("check_refs", [])),
        },
        "primary_entries_used": sorted(set(primary_entries_used)),
        "fallback_sources_used": sorted(set(fallback_sources_used)),
        "narrowing_actions": narrowed_references,
        "broad_reference_warnings": broad_reference_warnings,
        "references": [
            {
                "reference": item.get("reference"),
                "requested_reference": item.get("requested_reference"),
                "group": item.get("group"),
                "type": item.get("type"),
                "consumed_by": item.get("consumed_by"),
            }
            for item in copied
        ],
    }
    usage_report_path = runtime_dir / "knowledge_usage_report.json"
    usage_report_path.write_text(json.dumps(usage_report, ensure_ascii=False, indent=2), encoding="utf-8")

    for warning in warnings:
        print(f"WARNING: {warning}")
    print(f"Task card resolved: {resolved_path}")
    print(f"Context assembled: {manifest_path}")
    append_command_if_provenance_exists(task_id, "assemble")
    return 0
