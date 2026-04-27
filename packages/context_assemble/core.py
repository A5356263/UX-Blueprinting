from __future__ import annotations

import json
import os
import stat
import shutil
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
    knowledge_plan, source_ref_chains = build_knowledge_consumption_plan(resolved)

    consumption_map = {
        "knowledge_refs": ["facts", "business", "experience"],
        "wiki_refs": ["facts", "business", "experience"],
        "template_refs": ["facts", "business", "experience"],
        "check_refs": ["gate", "validate"],
    }

    reference_items_raw: list[dict[str, object]] = []
    for field in ("knowledge_refs", "wiki_refs", "template_refs", "check_refs"):
        for reference in resolved.get(field, []):
            reference_items_raw.append(
                {
                    "reference": str(reference),
                    "group": field,
                    "consumed_by": consumption_map[field],
                }
            )

    def append_stage_refs(refs: list[str], group: str, stage: str) -> None:
        for ref in refs:
            reference_items_raw.append(
                {
                    "reference": ref,
                    "group": group,
                    "consumed_by": [stage],
                }
            )

    append_stage_refs(list(knowledge_plan["facts"].get("required_wiki_refs", [])), "wiki_refs", "facts")
    append_stage_refs(list(knowledge_plan["business"].get("summary_refs", [])), "wiki_refs", "business")
    append_stage_refs(list(knowledge_plan["business"].get("related_summary_refs", [])), "wiki_refs", "business")
    append_stage_refs(list(knowledge_plan["experience"].get("summary_refs", [])), "wiki_refs", "experience")
    append_stage_refs(list(knowledge_plan["experience"].get("guideline_refs", [])), "wiki_refs", "experience")
    append_stage_refs(list(knowledge_plan["experience"].get("related_summary_refs", [])), "wiki_refs", "experience")

    raw_route_by_ref: dict[str, dict[str, object]] = {}
    for chain in source_ref_chains:
        raw_ref = str(chain.get("raw", "")).strip()
        stage = str(chain.get("stage", "")).strip()
        summary = str(chain.get("summary", "")).strip()
        if not raw_ref or not stage:
            continue
        route_meta = raw_route_by_ref.setdefault(
            raw_ref,
            {
                "stages": [],
                "summary": summary,
                "reason": "source_refs",
            },
        )
        if stage not in route_meta["stages"]:
            route_meta["stages"].append(stage)
        if summary and not route_meta.get("summary"):
            route_meta["summary"] = summary

    for raw_ref, route_meta in raw_route_by_ref.items():
        reference_items_raw.append(
            {
                "reference": raw_ref,
                "group": "raw_refs",
                "consumed_by": route_meta["stages"],
                "routed_from_summary": route_meta.get("summary", ""),
                "route_reason": route_meta.get("reason", "source_refs"),
            }
        )

    deduped_reference_items: dict[tuple[str, str], dict[str, object]] = {}
    for item in reference_items_raw:
        key = (str(item["group"]), str(item["reference"]))
        existing = deduped_reference_items.get(key)
        if existing is None:
            deduped_reference_items[key] = {
                "reference": str(item["reference"]),
                "group": str(item["group"]),
                "consumed_by": list(item.get("consumed_by", [])),
                "routed_from_summary": str(item.get("routed_from_summary", "")),
                "route_reason": str(item.get("route_reason", "")),
            }
            continue
        merged_consumed_by = sorted(set(existing.get("consumed_by", []) + list(item.get("consumed_by", []))))
        existing["consumed_by"] = merged_consumed_by
        if not existing.get("routed_from_summary") and item.get("routed_from_summary"):
            existing["routed_from_summary"] = item.get("routed_from_summary")
        if not existing.get("route_reason") and item.get("route_reason"):
            existing["route_reason"] = item.get("route_reason")

    reference_items = list(deduped_reference_items.values())

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
            if str(item.get("group")) == "raw_refs" and source_path.is_dir():
                raise ValueError(f"Raw reference must be file, not directory: {resolved_reference}")
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
        "knowledge_consumption_plan": knowledge_plan,
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
        "stage_usage": {
            "facts": {
                "wiki_refs_used": list(knowledge_plan["facts"].get("required_wiki_refs", [])),
                "raw_refs_used": [],
                "raw_policy": "not_default",
            },
            "business": {
                "wiki_refs_used": list(knowledge_plan["business"].get("summary_refs", [])),
                "raw_refs_used": list(knowledge_plan["business"].get("raw_refs_from_source_refs", [])),
                "source_ref_chains": [item for item in source_ref_chains if item.get("stage") == "business"],
            },
            "experience": {
                "wiki_refs_used": list(knowledge_plan["experience"].get("summary_refs", []))
                + list(knowledge_plan["experience"].get("guideline_refs", [])),
                "raw_refs_used": list(knowledge_plan["experience"].get("raw_refs_from_source_refs", [])),
                "source_ref_chains": [item for item in source_ref_chains if item.get("stage") == "experience"],
                "guideline_refs_used": list(knowledge_plan["experience"].get("guideline_refs", [])),
                "guideline_raw_refs_used": [
                    str(item).replace("\\", "/")
                    for item in knowledge_plan["experience"].get("raw_refs_from_source_refs", [])
                    if isinstance(item, str) and "/guidelines/" in str(item).replace("\\", "/").lower()
                ],
                "guideline_selection_reason": [],
            },
        },
        "references": [
            {
                "reference": item.get("reference"),
                "requested_reference": item.get("requested_reference"),
                "group": item.get("group"),
                "type": item.get("type"),
                "consumed_by": item.get("consumed_by"),
                "routed_from_summary": item.get("routed_from_summary"),
                "route_reason": item.get("route_reason"),
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
