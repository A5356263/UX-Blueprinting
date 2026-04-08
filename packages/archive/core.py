from __future__ import annotations

import shutil
from pathlib import Path

from packages.common import get_project_exports_dir, get_project_runtime_dir, get_project_source_dir, get_project_workspace_dir


def copy_if_exists(source: Path, destination: Path) -> bool:
    if not source.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(source, destination)
    return True


def run_archive_artifacts(task_id: str) -> int:
    source_dir = get_project_source_dir(task_id)
    workspace_dir = get_project_workspace_dir(task_id)
    runtime_dir = get_project_runtime_dir(task_id)
    exports_dir = get_project_exports_dir(task_id)

    final_dir = exports_dir / "final"
    checks_dir = exports_dir / "checks"
    context_dir = runtime_dir / "archive_snapshot"

    copied = 0
    for name in ["facts.md", "business_blueprint.md", "experience_blueprint.md", "gap_list.md"]:
        if copy_if_exists(workspace_dir / name, final_dir / name):
            copied += 1

    for name in ["check_report.md", "check_status.json"]:
        if copy_if_exists(workspace_dir / name, checks_dir / name):
            copied += 1

    for name in ["context_bundle", "gates", "snapshots"]:
        if copy_if_exists(runtime_dir / name, context_dir / name):
            copied += 1

    if copy_if_exists(source_dir / "task_card.md", context_dir / "task_card.md"):
        copied += 1
    if copy_if_exists(runtime_dir / "context_manifest.json", context_dir / "context_manifest.json"):
        copied += 1
    if copy_if_exists(runtime_dir / "task_card_resolved.json", context_dir / "task_card_resolved.json"):
        copied += 1

    print(f"Artifacts archived to: {exports_dir}")
    print(f"Copied items: {copied}")
    return 0
