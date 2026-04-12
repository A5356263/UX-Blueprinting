from __future__ import annotations

from packages.common import get_project_remediation_dir
from packages.repair_loop.issue_collect import append_jsonl, collect_issue_sources, now_iso, write_json, write_text
from packages.repair_loop.issue_normalize import normalize_issue_index
from packages.repair_loop.plan_build import build_remediation_plan
from packages.repair_loop.repair_close import run_repair_accept, run_repair_close, run_repair_defer, run_repair_status
from packages.repair_loop.retry_scope import build_retry_scope
from packages.repair_loop.summary_render import render_repair_summary


def run_repair_plan(project_id: str) -> int:
    remediation_dir = get_project_remediation_dir(project_id)
    remediation_dir.mkdir(parents=True, exist_ok=True)

    collected = collect_issue_sources(project_id)
    issue_index = normalize_issue_index(project_id, collected)
    remediation_plan = build_remediation_plan(project_id, issue_index)
    retry_scope = build_retry_scope(project_id, issue_index)
    summary = render_repair_summary(issue_index, remediation_plan, retry_scope)

    write_json(remediation_dir / "issue_index.json", issue_index)
    write_json(remediation_dir / "remediation_plan.json", remediation_plan)
    write_json(remediation_dir / "retry_scope.json", retry_scope)
    write_text(remediation_dir / "repair_summary.md", summary)

    append_jsonl(
        remediation_dir / "repair_run_log.jsonl",
        {
            "ts": now_iso(),
            "cycle_id": now_iso(),
            "event": "plan_generated",
            "actor": "packages.repair_loop",
            "issue_ids": [issue["issue_id"] for issue in issue_index.get("issues", [])],
            "result": {
                "repair_loop_status": issue_index.get("repair_loop_status"),
                "open_issue_count": issue_index.get("open_issue_count", 0),
            },
        },
    )

    print(f"Issue index written: {remediation_dir / 'issue_index.json'}")
    print(f"Remediation plan written: {remediation_dir / 'remediation_plan.json'}")
    print(f"Retry scope written: {remediation_dir / 'retry_scope.json'}")
    print(f"Repair summary written: {remediation_dir / 'repair_summary.md'}")
    return 0


__all__ = ["run_repair_plan", "run_repair_status", "run_repair_close", "run_repair_accept", "run_repair_defer"]
