from __future__ import annotations

from typing import Any


def _stage_order(stage: str) -> int:
    return {"final": 0, "runtime": 0, "experience": 1, "business": 2, "facts": 3}.get(stage, 0)


def _required_stage(issue: dict[str, Any]) -> str:
    backtrack_stage = str(issue.get("upstream_backtrack_stage") or "").strip()
    if backtrack_stage in {"facts", "business", "experience", "final"}:
        return backtrack_stage

    stage = str(issue.get("stage", "final"))
    if stage == "runtime":
        return "final"
    return stage


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
            "rationale": ["当前没有 open issue，可直接进入 archive 判定。"],
        }

    backtrack_required = any(bool(issue.get("upstream_backtrack_required")) for issue in actionable)
    highest_issue = max(actionable, key=lambda issue: _stage_order(_required_stage(issue)))
    highest_stage = _required_stage(highest_issue)

    if highest_stage == "facts":
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
        required_stage = _required_stage(issue)
        issue_id = str(issue.get("issue_id") or "unknown-issue")
        rationale.append(
            f"{issue_id} 需要从 {required_stage} 阶段开始重跑，修复模式为 {issue['repair_mode']}。"
        )
    if backtrack_required:
        rationale.append("至少一个问题要求回退到上游阶段，因此必须按最小回退范围扩展 scoped rerun。")

    return {
        "project_id": project_id,
        "scope_version": "1.0",
        "recommended_commands": commands,
        "backtrack_required": backtrack_required,
        "highest_required_stage": highest_stage,
        "rationale": rationale,
    }
