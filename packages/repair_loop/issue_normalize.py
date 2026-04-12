from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from packages.common import get_project_runtime_dir, get_project_workspace_dir
from packages.repair_loop.issue_collect import read_text, repo_rel


EXPECTED_HEADINGS = {
    "facts": [
        "任务意图",
        "事实来源说明",
        "术语与对象边界",
        "角色与对象清单",
        "原子事实清单",
        "规则矩阵",
        "状态模型",
        "动作与流程事实",
        "异常与拦截清单",
        "依赖清单",
        "范围与非范围",
        "开放问题与缺口",
        "追踪映射",
    ],
    "business": [
        "评审对象与任务边界",
        "领域基线",
        "方案意图与变更类型",
        "合理性判断",
        "底层逻辑一致性判断",
        "管理策略一致性判断",
        "能力归位判断",
        "价值、成本与认知负担评估",
        "备选路径比较",
        "最终业务立场",
        "关键规则与依赖影响",
        "风险与反模式",
        "开放问题与缺口",
        "判断追踪映射",
    ],
    "experience": [
        "体验目标与任务边界",
        "体验推导依据",
        "信息架构总览",
        "任务流蓝图",
        "页面 / 窗口清单",
        "关键页面蓝图",
        "区块布局示意",
        "内容与信息优先级合同",
        "状态与反馈矩阵",
        "文案合同",
        "风险、疑惑点与保护策略",
        "开放问题与缺口",
        "体验追踪映射",
    ],
}

PLACEHOLDER_PATTERN = re.compile(r"{{[^}]+}}|<project-id>|<[^>]+>")


def _stage_artifact_path(project_id: str, stage: str) -> Path | None:
    workspace_dir = get_project_workspace_dir(project_id)
    runtime_dir = get_project_runtime_dir(project_id)
    mapping = {
        "facts": workspace_dir / "facts.md",
        "business": workspace_dir / "business_blueprint.md",
        "experience": workspace_dir / "experience_blueprint.md",
        "final": workspace_dir / "check_status.json",
        "runtime": runtime_dir / "gate_metrics.json",
    }
    return mapping.get(stage)


def _artifact_inspection(project_id: str, stage: str) -> dict[str, Any]:
    artifact_path = _stage_artifact_path(project_id, stage)
    if artifact_path is None:
        return {"path": None, "missing_file": False, "missing_headings": [], "has_placeholder": False}
    if not artifact_path.exists():
        return {"path": artifact_path, "missing_file": True, "missing_headings": [], "has_placeholder": False}
    if artifact_path.suffix != ".md":
        return {"path": artifact_path, "missing_file": False, "missing_headings": [], "has_placeholder": False}

    content = read_text(artifact_path)
    missing_headings = [
        heading for heading in EXPECTED_HEADINGS.get(stage, []) if f"## {heading}" not in content
    ]
    has_placeholder = bool(PLACEHOLDER_PATTERN.search(content))
    return {
        "path": artifact_path,
        "missing_file": False,
        "missing_headings": missing_headings,
        "has_placeholder": has_placeholder,
    }


def _infer_stage(raw_issue: dict[str, Any]) -> str:
    message = raw_issue["message"]
    lowered = message.lower()
    if "experience_blueprint.md" in lowered or raw_issue["source"] == "experience_gate":
        return "experience"
    if "business_blueprint.md" in lowered or raw_issue["source"] == "business_gate":
        return "business"
    if "facts.md" in lowered or raw_issue["source"] == "facts_gate":
        return "facts"
    if raw_issue["source"] in {"validate", "coverage"}:
        return "final"
    return raw_issue["stage"]


def _infer_target_artifacts(project_id: str, stage: str, source: str, message: str) -> list[str]:
    workspace_dir = get_project_workspace_dir(project_id)
    runtime_dir = get_project_runtime_dir(project_id)
    targets: list[Path] = []
    lowered = message.lower()

    if "facts.md" in lowered:
        targets.append(workspace_dir / "facts.md")
    if "business_blueprint.md" in lowered:
        targets.append(workspace_dir / "business_blueprint.md")
    if "experience_blueprint.md" in lowered:
        targets.append(workspace_dir / "experience_blueprint.md")
    if "check_status.json" in lowered:
        targets.append(workspace_dir / "check_status.json")
    if "check_report.md" in lowered:
        targets.append(workspace_dir / "check_report.md")
    if "trace_index.json" in lowered:
        targets.append(runtime_dir / "trace_index.json")
    if "gate_metrics.json" in lowered:
        targets.append(runtime_dir / "gate_metrics.json")
    if "context_manifest.json" in lowered:
        targets.append(runtime_dir / "context_manifest.json")
    if "task_card_resolved.json" in lowered:
        targets.append(runtime_dir / "task_card_resolved.json")

    if source == "coverage":
        if "judgment" in lowered:
            targets.extend([workspace_dir / "business_blueprint.md", workspace_dir / "experience_blueprint.md"])
        elif "page" in lowered:
            targets.append(workspace_dir / "experience_blueprint.md")
        else:
            targets.extend(
                [
                    workspace_dir / "facts.md",
                    workspace_dir / "business_blueprint.md",
                    workspace_dir / "experience_blueprint.md",
                ]
            )

    if not targets:
        fallback = _stage_artifact_path(project_id, stage)
        if fallback is not None:
            targets.append(fallback)

    unique: list[str] = []
    for path in targets:
        rel = repo_rel(path)
        if rel not in unique:
            unique.append(rel)
    return unique


def _infer_category(raw_issue: dict[str, Any], project_id: str, stage: str) -> tuple[str, dict[str, Any]]:
    message = raw_issue["message"]
    lowered = message.lower()
    inspection = _artifact_inspection(project_id, stage)

    if inspection["missing_file"]:
        return "structure_missing", inspection
    if inspection["missing_headings"]:
        return "structure_missing", inspection
    if inspection["has_placeholder"]:
        return "placeholder_residue", inspection
    if raw_issue["source"] == "coverage":
        return "coverage_gap", inspection
    if "trace" in lowered or "追踪" in message or "追溯" in message:
        return "trace_missing", inspection
    if "state" in lowered or "状态" in message or "exception" in lowered or "happy path" in lowered:
        return "state_model_gap", inspection
    if "copy" in lowered or "文案合同" in message:
        return "copy_contract_gap", inspection
    if "placeholder" in lowered:
        return "placeholder_residue", inspection
    if "conflict" in lowered or "不一致" in message or "冲突" in message:
        return "consistency_conflict", inspection
    if "sql" in lowered or "react" in lowered or "前端" in message or "高保真" in message:
        return "boundary_violation", inspection
    if "coverage" in lowered or "orphan_" in lowered or "未被" in message:
        return "coverage_gap", inspection
    if "missing" in lowered or "缺少" in message or "文件" in message:
        return "structure_missing", inspection
    if stage in {"business", "experience"} and raw_issue["severity"] in {"blocker", "warning"}:
        return "depth_insufficient", inspection
    if stage == "runtime":
        return "runtime_staleness", inspection
    return "structure_missing", inspection


def _infer_upstream_backtrack_required(raw_issue: dict[str, Any], stage: str) -> bool:
    message = raw_issue["message"].lower()
    if stage == "business" and ("facts gate" in message or "facts stage" in message):
        return True
    if stage == "experience" and ("business gate" in message or "business stage" in message):
        return True
    if stage == "final" and ("facts gate" in message or "business gate" in message or "experience gate" in message):
        return True
    return False


def _infer_repair_mode(category: str, stage: str, severity: str, inspection: dict[str, Any], upstream_backtrack_required: bool) -> str:
    if upstream_backtrack_required:
        return "backtrack_upstream_stage"
    if category == "placeholder_residue":
        return "patch_current_section"
    if category == "runtime_staleness":
        return "rerun_checks_only"
    if inspection.get("missing_file"):
        return "regenerate_current_stage" if stage in {"facts", "business", "experience"} else "rerun_checks_only"
    if severity == "info":
        return "defer"
    if stage == "final":
        return "rerun_checks_only"
    return "patch_current_artifact"


def _issue_prefix(stage: str) -> str:
    return {
        "facts": "FACT",
        "business": "BIZ",
        "experience": "EXP",
        "final": "CHK",
        "runtime": "RUN",
    }.get(stage, "ISSUE")


def _build_issue_id(stage: str, source: str, category: str, targets: list[str], description: str) -> str:
    digest = hashlib.sha1(
        "|".join([stage, source, category, ",".join(targets), description]).encode("utf-8")
    ).hexdigest()[:8].upper()
    return f"{_issue_prefix(stage)}-{digest}"


def _violated_contract_refs(stage: str, source: str) -> list[str]:
    refs = ["specs/11_repair_loop_contract.md"]
    if stage == "facts":
        refs.append("specs/08_fact_extraction_contract.md")
    elif stage == "business":
        refs.append("specs/09_business_blueprint_contract.md")
    elif stage == "experience":
        refs.append("specs/10_experience_blueprint_contract.md")
    else:
        refs.append("specs/06_check_contract.md")
    if source in {"validate", "coverage"} and "specs/06_check_contract.md" not in refs:
        refs.append("specs/06_check_contract.md")
    return refs


def _build_description(stage: str, category: str, raw_issue: dict[str, Any], inspection: dict[str, Any], targets: list[str]) -> str:
    if inspection.get("missing_file"):
        return f"缺少正式产物文件：{targets[0]}"
    if inspection.get("missing_headings"):
        headings = ", ".join(f"## {item}" for item in inspection["missing_headings"][:4])
        return f"{Path(targets[0]).name} 缺少必需章节：{headings}"
    if inspection.get("has_placeholder"):
        return f"{Path(targets[0]).name} 存在占位内容残留，需要补齐正式内容后再重跑检查"
    if category == "coverage_gap" and raw_issue["source"] == "coverage":
        return f"coverage 检查发现覆盖缺口：{raw_issue['message']}"
    return f"{stage} 阶段发现 {category} 问题：{raw_issue['message']}"


def _build_evidence(raw_issue: dict[str, Any], inspection: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = [
        {"type": "message", "value": raw_issue["message"]},
        {"type": "status_path", "value": raw_issue["status_path"]},
        {"type": "report_path", "value": raw_issue["report_path"]},
    ]
    if inspection.get("missing_headings"):
        evidence.append({"type": "missing_headings", "value": inspection["missing_headings"]})
    if inspection.get("path") is not None:
        evidence.append({"type": "artifact_name", "value": str(inspection["path"].name)})
    if raw_issue.get("checked_files"):
        evidence.append({"type": "checked_files", "value": raw_issue["checked_files"][:8]})
    return evidence


def _suggested_actions(category: str, targets: list[str], inspection: dict[str, Any]) -> list[str]:
    target_name = Path(targets[0]).name if targets else "当前产物"
    actions = ["不要整稿重写，优先做局部补修"]
    if inspection.get("missing_headings"):
        headings = ", ".join(f"## {item}" for item in inspection["missing_headings"][:4])
        actions.append(f"补齐 {target_name} 的必需章节：{headings}")
    elif category == "placeholder_residue":
        actions.append(f"替换 {target_name} 中的占位内容，确保不再残留模板变量")
    elif category == "coverage_gap":
        actions.append(f"补齐 {target_name} 与上下游产物之间的覆盖与追踪关系")
    elif category == "state_model_gap":
        actions.append(f"补齐 {target_name} 的失败态、阻断态或处理中状态")
    elif category == "copy_contract_gap":
        actions.append(f"补齐 {target_name} 的文案合同或文案边界说明")
    elif category == "boundary_violation":
        actions.append(f"删除 {target_name} 中越出当前阶段边界的内容")
    elif category == "runtime_staleness":
        actions.append("刷新 runtime 产物后重新运行相关检查")
    else:
        actions.append(f"修复 {target_name} 中当前阶段未达标的内容")
    return actions


def _retry_scope_hint(stage: str, source: str, upstream_backtrack_required: bool) -> list[str]:
    if upstream_backtrack_required or stage == "facts":
        return ["gate-facts", "gate-business", "gate-experience", "validate", "coverage"]
    if stage == "business":
        return ["gate-business", "gate-experience", "validate", "coverage"]
    if stage == "experience":
        return ["gate-experience", "validate", "coverage"]
    if source == "runtime":
        return ["validate", "coverage"]
    return ["validate", "coverage"]


def normalize_issue_index(project_id: str, collected: dict[str, Any]) -> dict[str, Any]:
    issue_map: dict[str, dict[str, Any]] = {}

    for raw_issue in collected.get("raw_issues", []):
        stage = _infer_stage(raw_issue)
        targets = _infer_target_artifacts(project_id, stage, raw_issue["source"], raw_issue["message"])
        category, inspection = _infer_category(raw_issue, project_id, stage)
        upstream_backtrack_required = _infer_upstream_backtrack_required(raw_issue, stage)
        description = _build_description(stage, category, raw_issue, inspection, targets)
        issue_id = _build_issue_id(stage, raw_issue["source"], category, targets, description)

        existing = issue_map.get(issue_id)
        if existing:
            existing_sources = existing.setdefault("related_sources", [])
            if raw_issue["source"] not in existing_sources:
                existing_sources.append(raw_issue["source"])
            for evidence_item in _build_evidence(raw_issue, inspection):
                if evidence_item not in existing["evidence"]:
                    existing["evidence"].append(evidence_item)
            continue

        issue_map[issue_id] = {
            "issue_id": issue_id,
            "source": raw_issue["source"],
            "stage": stage,
            "severity": raw_issue["severity"],
            "category": category,
            "title": f"{stage} 阶段存在 {category} 问题",
            "description": description,
            "evidence": _build_evidence(raw_issue, inspection),
            "violated_contract_refs": _violated_contract_refs(stage, raw_issue["source"]),
            "target_artifacts": targets,
            "repair_mode": _infer_repair_mode(category, stage, raw_issue["severity"], inspection, upstream_backtrack_required),
            "suggested_actions": _suggested_actions(category, targets, inspection),
            "upstream_backtrack_required": upstream_backtrack_required,
            "retry_scope_hint": _retry_scope_hint(stage, raw_issue["source"], upstream_backtrack_required),
            "related_sources": [raw_issue["source"]],
            "status": "open",
        }

    issues = list(issue_map.values())
    issues.sort(key=lambda item: ({"blocker": 0, "warning": 1, "info": 2}.get(item["severity"], 9), item["stage"], item["issue_id"]))
    blocker_count = sum(1 for item in issues if item["severity"] == "blocker" and item["status"] == "open")
    warning_count = sum(1 for item in issues if item["severity"] == "warning" and item["status"] == "open")
    info_count = sum(1 for item in issues if item["severity"] == "info" and item["status"] == "open")

    return {
        "project_id": project_id,
        "generated_at": collected.get("generated_at"),
        "issue_count": len(issues),
        "open_issue_count": sum(1 for item in issues if item["status"] == "open"),
        "blocker_count": blocker_count,
        "warning_count": warning_count,
        "info_count": info_count,
        "repair_loop_status": "blocked" if blocker_count else ("planned" if issues else "idle"),
        "source_artifacts": collected.get("source_artifacts", []),
        "issues": issues,
    }
