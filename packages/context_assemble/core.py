from __future__ import annotations

import json
import shutil
from pathlib import Path

from packages.common import get_project_runtime_dir, get_repo_root
from packages.provenance import append_command_if_provenance_exists
from packages.task_card_resolve import resolve_task_card_file


def to_repo_relative(repo_root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")


def copy_reference(repo_root: Path, target_root: Path, reference: str) -> dict[str, str]:
    source = repo_root / Path(reference.replace("/", "\\"))
    if not source.exists():
        raise FileNotFoundError(f"Reference not found: {reference}")

    destination = target_root / Path(reference.replace("/", "\\"))
    destination.parent.mkdir(parents=True, exist_ok=True)

    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
        ref_type = "directory"
    else:
        shutil.copy2(source, destination)
        ref_type = "file"

    return {
        "reference": reference,
        "type": ref_type,
        "source": to_repo_relative(repo_root, source),
        "destination": to_repo_relative(repo_root, destination),
        "is_directory_ref": "true" if ref_type == "directory" else "false",
        "suggest_narrow_to_file": "true" if ref_type == "directory" else "false",
    }


def run_context_assemble(task_id: str) -> int:
    repo_root = get_repo_root()
    runtime_dir = get_project_runtime_dir(task_id)
    context_bundle_dir = runtime_dir / "context_bundle"
    if context_bundle_dir.exists():
        shutil.rmtree(context_bundle_dir)
    context_bundle_dir.mkdir(parents=True, exist_ok=True)

    resolved, resolved_path = resolve_task_card_file(task_id, write_output=True)

    if resolved["errors"]:
        for error in resolved["errors"]:
            print(f"ERROR: {error}")
        print(f"Task card resolution failed: {resolved_path}")
        return 1

    references: list[str] = []
    consumption_map = {
        "knowledge_refs": ["facts", "business", "experience"],
        "wiki_refs": ["facts", "business", "experience"],
        "template_refs": ["facts", "business", "experience"],
        "check_refs": ["gate", "validate"],
    }
    reference_items: list[dict[str, object]] = []
    for field in ("knowledge_refs", "wiki_refs", "template_refs", "check_refs"):
        for reference in resolved[field]:
            reference_items.append(
                {
                    "reference": str(reference),
                    "group": field,
                    "consumed_by": consumption_map[field],
                }
            )
            references.append(str(reference))

    copied_map: dict[str, dict[str, str]] = {ref: copy_reference(repo_root, context_bundle_dir, ref) for ref in references}
    copied: list[dict[str, object]] = []
    for item in reference_items:
        copied_item = dict(item)
        copied_item.update(copied_map[item["reference"]])
        copied.append(copied_item)

    facts_req = resolved.get("facts_output_requirements", {})
    business_req = resolved.get("business_output_requirements", {})
    experience_req = resolved.get("experience_output_requirements", {})
    manifest = {
        "task_id": task_id,
        "resolved_from": to_repo_relative(repo_root, resolved_path),
        "reference_count": len(copied),
        "references": copied,
        "warnings": resolved["warnings"],
        "facts_extraction_boundary": facts_req.get("boundary", []),
        "business_judgment_boundary": business_req.get("boundary", []),
        "experience_translation_boundary": experience_req.get("boundary", []),
    }
    manifest_path = runtime_dir / "context_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    usage_report = {
        "task_id": task_id,
        "generated_from": to_repo_relative(repo_root, manifest_path),
        "mainline_knowledge_policy": "wiki_pages_only",
        "reference_summary": {
            "knowledge_ref_count": len(resolved.get("knowledge_refs", [])),
            "wiki_ref_count": len(resolved.get("wiki_refs", [])),
            "template_ref_count": len(resolved.get("template_refs", [])),
            "check_ref_count": len(resolved.get("check_refs", [])),
        },
        "references": [
            {
                "reference": item.get("reference"),
                "group": item.get("group"),
                "type": item.get("type"),
                "consumed_by": item.get("consumed_by"),
            }
            for item in copied
        ],
    }
    usage_report_path = runtime_dir / "knowledge_usage_report.json"
    usage_report_path.write_text(json.dumps(usage_report, ensure_ascii=False, indent=2), encoding="utf-8")

    for warning in resolved["warnings"]:
        print(f"WARNING: {warning}")
    print(f"Task card resolved: {resolved_path}")
    print(f"Context assembled: {manifest_path}")
    append_command_if_provenance_exists(task_id, "assemble")
    return 0
