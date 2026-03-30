from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def copy_if_exists(source: Path, destination: Path) -> bool:
    if not source.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(source, destination)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    task_dir = repo_root / "tasks" / "active" / args.task_id
    workspace_dir = task_dir / "workspace"
    task_artifacts_dir = task_dir / "artifacts"
    archive_dir = repo_root / "artifacts" / args.task_id

    final_dir = archive_dir / "final"
    checks_dir = archive_dir / "checks"
    context_dir = archive_dir / "context_snapshot"

    copied = 0
    for name in ["facts.md", "business_blueprint.md", "experience_blueprint.md", "gap_list.md"]:
        if copy_if_exists(workspace_dir / name, final_dir / name):
            copied += 1

    if copy_if_exists(workspace_dir / "check_report.md", checks_dir / "check_report.md"):
        copied += 1

    for name in ["context_bundle", "snapshots"]:
        if copy_if_exists(task_artifacts_dir / name, context_dir / name):
            copied += 1

    if copy_if_exists(task_dir / "task_card.md", context_dir / "task_card.md"):
        copied += 1

    print(f"Artifacts archived to: {archive_dir}")
    print(f"Copied items: {copied}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
