from __future__ import annotations

import json
import shutil
from pathlib import Path

from packages.common import get_project_runtime_dir, get_repo_root
from packages.task_card_resolve import resolve_task_card_file


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
        "source": str(source),
        "destination": str(destination),
    }


def run_context_assemble(task_id: str) -> int:
    repo_root = get_repo_root()
    runtime_dir = get_project_runtime_dir(task_id)
    context_bundle_dir = runtime_dir / "context_bundle"
    context_bundle_dir.mkdir(parents=True, exist_ok=True)

    resolved, resolved_path = resolve_task_card_file(task_id, write_output=True)

    if resolved["errors"]:
        for error in resolved["errors"]:
            print(f"ERROR: {error}")
        print(f"Task card resolution failed: {resolved_path}")
        return 1

    references: list[str] = []
    for field in ("knowledge_refs", "wiki_refs", "template_refs", "check_refs"):
        references.extend(str(reference) for reference in resolved[field])

    copied = [copy_reference(repo_root, context_bundle_dir, reference) for reference in references]
    manifest = {
        "task_id": task_id,
        "resolved_from": str(resolved_path),
        "reference_count": len(copied),
        "references": copied,
        "warnings": resolved["warnings"],
    }
    manifest_path = runtime_dir / "context_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    for warning in resolved["warnings"]:
        print(f"WARNING: {warning}")
    print(f"Task card resolved: {resolved_path}")
    print(f"Context assembled: {manifest_path}")
    return 0
