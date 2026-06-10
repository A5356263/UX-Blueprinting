from __future__ import annotations

import json
import shutil
from pathlib import Path

from packages.common import (
    get_project_exports_dir,
    get_project_remediation_dir,
    get_project_runtime_dir,
    get_project_source_dir,
    get_project_workspace_dir,
    sanitize_json_text,
)
from packages.provenance import append_command_if_provenance_exists


def copy_if_exists(source: Path, destination: Path) -> bool:
    if not source.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(source, destination)
    return True


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(sanitize_json_text(path.read_text(encoding="utf-8")))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def assert_archive_allowed(task_id: str) -> None:
    workspace_dir = get_project_workspace_dir(task_id)
    remediation_dir = get_project_remediation_dir(task_id)

    check_status = read_json(workspace_dir / "check_status.json")
    if not check_status:
        raise SystemExit("Archive blocked: missing workspace/check_status.json")
    if check_status.get("status") == "failed":
        raise SystemExit("Archive blocked: check_status.json.status=failed")

    issue_index = read_json(remediation_dir / "issue_index.json")
    if not issue_index:
        return

    issues = issue_index.get("issues", [])
    if not isinstance(issues, list):
        return

    open_blockers = [
        item
        for item in issues
        if isinstance(item, dict) and item.get("severity") == "blocker" and item.get("status") == "open"
    ]
    deferred_blockers = [
        item
        for item in issues
        if isinstance(item, dict) and item.get("severity") == "blocker" and item.get("status") == "deferred"
    ]
    if open_blockers:
        raise SystemExit("Archive blocked: remediation issue_index.json still contains open blocker issues")
    if deferred_blockers:
        raise SystemExit("Archive blocked: remediation issue_index.json still contains deferred blocker issues")


def run_archive_artifacts(task_id: str) -> int:
    assert_archive_allowed(task_id)
    source_dir = get_project_source_dir(task_id)
    workspace_dir = get_project_workspace_dir(task_id)
    runtime_dir = get_project_runtime_dir(task_id)
    remediation_dir = get_project_remediation_dir(task_id)
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

    for name in ["context_bundle", "gates", "snapshots", "remediation"]:
        if copy_if_exists(runtime_dir / name, context_dir / name):
            copied += 1

    if copy_if_exists(source_dir / "task_card.md", context_dir / "task_card.md"):
        copied += 1
    if copy_if_exists(runtime_dir / "uxb_route_decision.json", context_dir / "uxb_route_decision.json"):
        copied += 1
    if copy_if_exists(runtime_dir / "context_manifest.json", context_dir / "context_manifest.json"):
        copied += 1
    if copy_if_exists(runtime_dir / "knowledge_trace.json", context_dir / "knowledge_trace.json"):
        copied += 1
    if copy_if_exists(runtime_dir / "provenance.json", context_dir / "provenance.json"):
        copied += 1
    if copy_if_exists(remediation_dir / "repair_summary.md", checks_dir / "repair_summary.md"):
        copied += 1

    print(f"Artifacts archived to: {exports_dir}")
    print(f"Copied items: {copied}")
    append_command_if_provenance_exists(task_id, "archive")
    return 0
