from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any


def _required_inputs_for_stage(stage: str) -> list[str]:
    if stage == "facts":
        return [
            "workspace/facts.md",
            "runtime/task_card_resolved.json",
            "runtime/context_manifest.json",
        ]
    if stage == "business":
        return [
            "workspace/facts.md",
            "workspace/business_blueprint.md",
            "runtime/trace_index.json",
        ]
    if stage == "experience":
        return [
            "workspace/facts.md",
            "workspace/business_blueprint.md",
            "workspace/experience_blueprint.md",
            "runtime/trace_index.json",
        ]
    if stage == "runtime":
        return [
            "runtime/task_card_resolved.json",
            "runtime/context_manifest.json",
            "runtime/gate_metrics.json",
        ]
    return [
        "workspace/check_report.md",
        "workspace/check_status.json",
        "runtime/gate_metrics.json",
    ]


def _completion_signal(stage: str, severity: str) -> list[str]:
    if stage == "facts":
        return ["facts gate 无相关 blocker", "validate / coverage 不再报告同类问题"]
    if stage == "business":
        return ["business gate 无相关 blocker", "experience 与 final check 不再报告同类问题"]
    if stage == "experience":
        return ["experience gate 无相关 blocker", "validate / coverage 不再报告同类问题"]
    if stage == "runtime":
        return ["runtime 支撑产物补齐", "validate / coverage 可稳定完成"]
    if severity == "warning":
        return ["warning 被接受或消除", "archive 约束明确"]
    return ["final check 不再命中相关问题", "coverage 不再报告对应缺口"]


def build_remediation_plan(project_id: str, issue_index: dict[str, Any]) -> dict[str, Any]:
    open_issues = [
        issue
        for issue in issue_index.get("issues", [])
        if issue.get("status") == "open" and issue.get("severity") in {"blocker", "warning"}
    ]
    grouped: dict[tuple[str, str, str, bool], list[dict[str, Any]]] = defaultdict(list)
    for issue in open_issues:
        target = issue.get("target_artifacts", ["runtime/gate_metrics.json"])[0]
        key = (
            issue.get("stage", "final"),
            target,
            issue.get("repair_mode", "patch_current_artifact"),
            bool(issue.get("upstream_backtrack_required")),
        )
        grouped[key].append(issue)

    repair_units: list[dict[str, Any]] = []
    for index, ((stage, target, repair_mode, _), issues) in enumerate(sorted(grouped.items()), start=1):
        categories = sorted({str(item.get("category")) for item in issues})
        guidance: list[str] = []
        for issue in issues:
            for action in issue.get("suggested_actions", []):
                if action not in guidance:
                    guidance.append(str(action))

        target_name = Path(target).name
        repair_units.append(
            {
                "unit_id": f"repair-unit-{index:03d}",
                "stage": stage,
                "target_artifact": target,
                "issue_ids": [str(item["issue_id"]) for item in issues],
                "repair_mode": repair_mode,
                "repair_goal": f"修复 {target_name} 中的 {', '.join(categories)} 问题",
                "required_inputs": _required_inputs_for_stage(stage),
                "operator_guidance": guidance or ["按 issue 证据逐条修复正式产物，不要只在聊天中说明"],
                "completion_signal": _completion_signal(
                    stage, max((str(item.get("severity")) for item in issues), default="warning")
                ),
            }
        )

    return {
        "project_id": project_id,
        "plan_version": "1.0",
        "generated_at": issue_index.get("generated_at"),
        "open_issue_count": sum(1 for item in issue_index.get("issues", []) if item.get("status") == "open"),
        "blocker_count": sum(
            1
            for item in issue_index.get("issues", [])
            if item.get("status") == "open" and item.get("severity") == "blocker"
        ),
        "warning_count": sum(
            1
            for item in issue_index.get("issues", [])
            if item.get("status") == "open" and item.get("severity") == "warning"
        ),
        "repair_units": repair_units,
    }
