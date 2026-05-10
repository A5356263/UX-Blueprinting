from __future__ import annotations

from typing import Any


def _issue_lines(issues: list[dict[str, Any]]) -> list[str]:
    if not issues:
        return ["- none"]
    lines = []
    for issue in issues:
        related_sources = ", ".join(issue.get("related_sources", [])) or issue.get("source", "unknown")
        lines.append(
            f"- {issue['issue_id']} | {issue['severity']} | {issue['stage']} | {issue['category']} | sources={related_sources} | {issue['description']}"
        )
    return lines


def render_repair_summary(issue_index: dict[str, Any], remediation_plan: dict[str, Any], retry_scope: dict[str, Any]) -> str:
    issues = list(issue_index.get("issues", []))
    open_issues = [issue for issue in issues if issue.get("status") == "open"]
    accepted_warnings = [
        issue for issue in issues if issue.get("status") == "accepted" and issue.get("severity") == "warning"
    ]
    deferred_issues = [issue for issue in issues if issue.get("status") == "deferred"]

    lines = [
        "# Repair Summary｜人读说明版",
        "",
        "> 本文件是以下机器状态文件的人读说明版：",
        ">",
        f"> - `projects/{issue_index.get('project_id', '<project-id>')}/runtime/remediation/issue_index.json`",
        f"> - `projects/{issue_index.get('project_id', '<project-id>')}/runtime/remediation/remediation_plan.json`",
        f"> - `projects/{issue_index.get('project_id', '<project-id>')}/runtime/remediation/retry_scope.json`",
        ">",
        "> 它只用于帮助理解修复任务，不作为 repair loop 的机器判断依据。",
        "> 机器判断请以上述 JSON 文件为准。",
        "",
        "## 当前状态",
        "",
        f"- repair_loop_status: {issue_index.get('repair_loop_status', 'idle')}",
        f"- open issues: {len(open_issues)}",
        f"- blocker: {sum(1 for issue in open_issues if issue.get('severity') == 'blocker')}",
        f"- warning: {sum(1 for issue in open_issues if issue.get('severity') == 'warning')}",
        f"- info: {sum(1 for issue in open_issues if issue.get('severity') == 'info')}",
        "",
        "## 问题统计",
        "",
        f"- issue_count: {issue_index.get('issue_count', 0)}",
        f"- open_issue_count: {issue_index.get('open_issue_count', 0)}",
        f"- blocker_count: {issue_index.get('blocker_count', 0)}",
        f"- warning_count: {issue_index.get('warning_count', 0)}",
        f"- info_count: {issue_index.get('info_count', 0)}",
        "",
        "## 本轮修复单元",
        "",
    ]

    if remediation_plan.get("repair_units"):
        for unit in remediation_plan["repair_units"]:
            lines.extend(
                [
                    f"### {unit['unit_id']}",
                    f"- target: {unit['target_artifact']}",
                    f"- goal: {unit['repair_goal']}",
                    f"- mode: {unit['repair_mode']}",
                    f"- issue_ids: {', '.join(unit['issue_ids'])}",
                    "",
                ]
            )
    else:
        lines.append("- none")
        lines.append("")

    lines.extend(["## 推荐重跑", ""])
    if retry_scope.get("recommended_commands"):
        lines.extend(["```bash", *retry_scope["recommended_commands"], "```", ""])
    else:
        lines.extend(["- none", ""])

    lines.extend(["## 未关闭问题", ""])
    lines.extend(_issue_lines(open_issues))
    lines.extend(["", "## 已接受 warning", ""])
    lines.extend(_issue_lines(accepted_warnings))
    lines.extend(["", "## 已延期问题", ""])
    lines.extend(_issue_lines(deferred_issues))
    lines.append("")
    return "\n".join(lines)
