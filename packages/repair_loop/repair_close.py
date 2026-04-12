from __future__ import annotations

from pathlib import Path
from typing import Any

from packages.common import get_project_gates_dir, get_project_remediation_dir, get_project_workspace_dir
from packages.repair_loop.issue_collect import (
    append_jsonl,
    collect_issue_sources,
    now_iso,
    parse_iso,
    read_json,
    write_json,
    write_text,
)
from packages.repair_loop.issue_normalize import normalize_issue_index
from packages.repair_loop.plan_build import build_remediation_plan
from packages.repair_loop.retry_scope import build_retry_scope
from packages.repair_loop.summary_render import render_repair_summary


def _command_output_paths(project_id: str, command: str) -> list[Path]:
    workspace_dir = get_project_workspace_dir(project_id)
    gates_dir = get_project_gates_dir(project_id)
    if "gate-facts" in command:
        return [gates_dir / "facts_gate_status.json"]
    if "gate-business" in command:
        return [gates_dir / "business_gate_status.json"]
    if "gate-experience" in command:
        return [gates_dir / "experience_gate_status.json"]
    if "validate" in command or "coverage" in command:
        return [workspace_dir / "check_status.json"]
    return []


def _rerun_observed(project_id: str, retry_scope: dict[str, Any], generated_at: str | None) -> bool:
    baseline = parse_iso(generated_at)
    if baseline is None:
        return True
    observed = False
    for command in retry_scope.get("recommended_commands", []):
        for path in _command_output_paths(project_id, str(command)):
            if not path.exists():
                continue
            modified = parse_iso(str(read_json(path).get("updated_at"))) if path.suffix == ".json" else None
            if modified and modified > baseline:
                observed = True
                break
            if not modified and path.stat().st_mtime > baseline.timestamp():
                observed = True
                break
        if observed:
            break
    return observed or not retry_scope.get("recommended_commands")


def _merge_issue_statuses(previous_index: dict[str, Any], current_index: dict[str, Any]) -> dict[str, Any]:
    previous_by_id = {str(issue["issue_id"]): issue for issue in previous_index.get("issues", [])}
    current_by_id = {str(issue["issue_id"]): issue for issue in current_index.get("issues", [])}

    merged: list[dict[str, Any]] = []
    for issue_id, issue in current_by_id.items():
        previous = previous_by_id.get(issue_id, {})
        previous_status = str(previous.get("status", "open"))
        new_issue = dict(issue)
        if previous_status == "accepted" and issue.get("severity") != "blocker":
            new_issue["status"] = "accepted"
        elif previous_status == "deferred":
            new_issue["status"] = "deferred"
        else:
            new_issue["status"] = "open"
        merged.append(new_issue)

    for issue_id, issue in previous_by_id.items():
        if issue_id in current_by_id:
            continue
        resolved_issue = dict(issue)
        if str(issue.get("status")) == "invalid":
            resolved_issue["status"] = "invalid"
        else:
            resolved_issue["status"] = "resolved"
        merged.append(resolved_issue)

    merged.sort(key=lambda item: ({"blocker": 0, "warning": 1, "info": 2}.get(item["severity"], 9), item["stage"], item["issue_id"]))
    current_index["issues"] = merged
    current_index["issue_count"] = len(merged)
    current_index["open_issue_count"] = sum(1 for item in merged if item.get("status") == "open")
    current_index["blocker_count"] = sum(
        1 for item in merged if item.get("status") == "open" and item.get("severity") == "blocker"
    )
    current_index["warning_count"] = sum(
        1 for item in merged if item.get("status") == "open" and item.get("severity") == "warning"
    )
    current_index["info_count"] = sum(
        1 for item in merged if item.get("status") == "open" and item.get("severity") == "info"
    )
    current_index["repair_loop_status"] = "blocked" if current_index["blocker_count"] else "closed"
    current_index["updated_at"] = now_iso()
    return current_index


def run_repair_status(project_id: str) -> int:
    remediation_dir = get_project_remediation_dir(project_id)
    issue_index = read_json(remediation_dir / "issue_index.json")
    retry_scope = read_json(remediation_dir / "retry_scope.json")
    if not issue_index:
        raise SystemExit(f"Missing remediation issue index: {remediation_dir / 'issue_index.json'}")

    open_blockers = [
        issue for issue in issue_index.get("issues", []) if issue.get("status") == "open" and issue.get("severity") == "blocker"
    ]
    deferred_blockers = [
        issue for issue in issue_index.get("issues", []) if issue.get("status") == "deferred" and issue.get("severity") == "blocker"
    ]

    print(f"repair_loop_status: {issue_index.get('repair_loop_status', 'idle')}")
    print(f"open_issue_count: {issue_index.get('open_issue_count', 0)}")
    print(f"open_blocker_count: {len(open_blockers)}")
    print(f"deferred_blocker_count: {len(deferred_blockers)}")
    if retry_scope.get("recommended_commands"):
        print("recommended_commands:")
        for command in retry_scope["recommended_commands"]:
            print(f"  - {command}")
    return 1 if open_blockers or deferred_blockers else 0


def run_repair_close(project_id: str) -> int:
    remediation_dir = get_project_remediation_dir(project_id)
    issue_index_path = remediation_dir / "issue_index.json"
    retry_scope_path = remediation_dir / "retry_scope.json"
    log_path = remediation_dir / "repair_run_log.jsonl"

    previous_index = read_json(issue_index_path)
    retry_scope = read_json(retry_scope_path)
    if not previous_index:
        raise SystemExit(f"Missing remediation issue index: {issue_index_path}")
    if not retry_scope:
        raise SystemExit(f"Missing retry scope: {retry_scope_path}")

    if not _rerun_observed(project_id, retry_scope, str(previous_index.get("generated_at"))):
        raise SystemExit("Repair close blocked: scoped rerun artifacts do not appear to have been refreshed after repair-plan.")

    collected = collect_issue_sources(project_id)
    current_index = normalize_issue_index(project_id, collected)
    merged_index = _merge_issue_statuses(previous_index, current_index)
    remediation_plan = build_remediation_plan(project_id, merged_index)
    next_retry_scope = build_retry_scope(project_id, merged_index)
    summary = render_repair_summary(merged_index, remediation_plan, next_retry_scope)

    write_json(issue_index_path, merged_index)
    write_json(remediation_dir / "remediation_plan.json", remediation_plan)
    write_json(retry_scope_path, next_retry_scope)
    write_text(remediation_dir / "repair_summary.md", summary)

    cycle_id = now_iso()
    append_jsonl(
        log_path,
        {
            "ts": now_iso(),
            "cycle_id": cycle_id,
            "event": "rerun_finished",
            "actor": "packages.repair_loop",
            "issue_ids": [],
            "result": {"status": merged_index.get("repair_loop_status")},
        },
    )
    for issue in merged_index.get("issues", []):
        if issue.get("status") == "resolved":
            append_jsonl(
                log_path,
                {
                    "ts": now_iso(),
                    "cycle_id": cycle_id,
                    "event": "issue_resolved",
                    "actor": "packages.repair_loop",
                    "issue_ids": [issue["issue_id"]],
                    "result": {"status": "resolved"},
                },
            )
        elif issue.get("status") == "accepted":
            append_jsonl(
                log_path,
                {
                    "ts": now_iso(),
                    "cycle_id": cycle_id,
                    "event": "issue_accepted",
                    "actor": "packages.repair_loop",
                    "issue_ids": [issue["issue_id"]],
                    "result": {"status": "accepted"},
                },
            )
        elif issue.get("status") == "deferred":
            append_jsonl(
                log_path,
                {
                    "ts": now_iso(),
                    "cycle_id": cycle_id,
                    "event": "issue_deferred",
                    "actor": "packages.repair_loop",
                    "issue_ids": [issue["issue_id"]],
                    "result": {"status": "deferred"},
                },
            )

    append_jsonl(
        log_path,
        {
            "ts": now_iso(),
            "cycle_id": cycle_id,
            "event": "repair_closed",
            "actor": "packages.repair_loop",
            "issue_ids": [issue["issue_id"] for issue in merged_index.get("issues", []) if issue.get("status") == "open"],
            "result": {
                "repair_loop_status": merged_index.get("repair_loop_status"),
                "open_issue_count": merged_index.get("open_issue_count", 0),
            },
        },
    )

    print(f"Repair close finished: {remediation_dir / 'repair_summary.md'}")
    return 0 if merged_index.get("repair_loop_status") != "blocked" else 1
