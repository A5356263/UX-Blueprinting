from __future__ import annotations

from typing import Any


def _stage_order(stage: str) -> int:
    return {"final": 0, "runtime": 0, "experience": 1, "business": 2, "facts": 3}.get(stage, 0)


def build_retry_scope(project_id: str, issue_index: dict[str, Any]) -> dict[str, Any]:
    actionable = [
        issue
        for issue in issue_index.get("issues", [])
        if issue.get("status") == "open" and issue.get("severity") in {"blocker", "warning"}
    ]

    if not actionable:
        return {
            "project_id": project_id,
            "scope_version": "1.0",
            "recommended_commands": [],
            "backtrack_required": False,
            "highest_required_stage": "final",
            "rationale": ["当前无 open issue，可直接进入 archive 判定"],
        }

    backtrack_required = any(bool(issue.get("upstream_backtrack_required")) for issue in actionable)
    highest_issue = max(actionable, key=lambda issue: _stage_order(str(issue.get("stage", "final"))))
    highest_stage = str(highest_issue.get("stage", "final"))

    if backtrack_required or highest_stage == "facts":
        commands = [
            f"python -m packages gate-facts {project_id}",
            f"python -m packages gate-business {project_id}",
            f"python -m packages gate-experience {project_id}",
            f"python -m packages validate {project_id}",
            f"python -m packages coverage {project_id}",
        ]
    elif highest_stage == "business":
        commands = [
            f"python -m packages gate-business {project_id}",
            f"python -m packages gate-experience {project_id}",
            f"python -m packages validate {project_id}",
            f"python -m packages coverage {project_id}",
        ]
    elif highest_stage == "experience":
        commands = [
            f"python -m packages gate-experience {project_id}",
            f"python -m packages validate {project_id}",
            f"python -m packages coverage {project_id}",
        ]
    else:
        commands = [
            f"python -m packages validate {project_id}",
            f"python -m packages coverage {project_id}",
        ]

    rationale = []
    for issue in actionable[:5]:
        rationale.append(
            f"{issue['issue_id']} 影响 {issue['stage']} 阶段，修复模式为 {issue['repair_mode']}"
        )
    if backtrack_required:
        rationale.append("至少一个问题要求回退上游阶段，因此需要扩大重跑范围")

    return {
        "project_id": project_id,
        "scope_version": "1.0",
        "recommended_commands": commands,
        "backtrack_required": backtrack_required,
        "highest_required_stage": "facts" if backtrack_required else ("final" if highest_stage == "runtime" else highest_stage),
        "rationale": rationale,
    }
