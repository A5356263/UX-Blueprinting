from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from packages.common import (
    get_project_gates_dir,
    get_project_remediation_dir,
    get_project_runtime_dir,
    get_project_source_dir,
    get_project_workspace_dir,
    get_repo_root,
)
from packages.provenance import append_command_if_provenance_exists, validate_provenance


STAGE_REQUIRED_HEADINGS = {
    "facts.md": [
        "## 任务概述",
        "## 功能范围",
        "## 关键业务规则",
        "## 状态流转",
        "## 异常与边界",
        "## 依赖与前置条件",
        "## 开放问题与缺口",
    ],
    "business_blueprint.md": [
        "## 1. 一句话结论",
        "## 2. 需求是否成立",
        "## 3. 值不值得做",
        "## 4. 应该做成什么能力形态",
        "## 5. 推荐业务方案",
        "## 6. 必须守住的规则和边界",
        "## 7. 主要风险与保护策略",
        "## 8. 方案承接要求",
        "## 9. 待确认问题",
        "## 附录：事实、知识与判断追踪",
    ],
    "experience_blueprint.md": [
        "## 1. 交互流程总览",
        "## 2. 主交互流程",
        "## 3. 次交互流程",
        "## 4. 异常与阻断流程",
        "## 5. 页面 / 弹窗 / 抽屉设计",
        "## 6. 状态与反馈文案",
        "## 7. 待确认问题",
    ],
    "gap_list.md": ["## Blockers", "## Warnings", "## 待补信息"],
}

FORBIDDEN_TERMS = {
    "facts.md": [
        "最终业务立场",
        "能力归位判断",
        "信息架构总览",
        "任务流蓝图",
        "高保真视觉",
        "前端实现",
    ],
    "business_blueprint.md": [
        "## 7. 体验设计要注意什么",
        "页面区块布局",
        "高保真视觉",
        "组件开发实现",
        "前端技术栈",
        "SQL",
        "数据库表",
    ],
    "experience_blueprint.md": [
        "数据库表",
        "接口字段",
        "SQL",
        "React 组件实现",
        "前端实现方案",
        "Runtime Task Goal",
        "source_path",
        "EV-",
        "从当前输入直接抽取",
        "未做模板补全",
    ],
}


def _print_repair_guidance(project_id: str) -> None:
    remediation_dir = get_project_remediation_dir(project_id)
    summary_path = remediation_dir / "repair_summary.md"
    retry_scope_path = remediation_dir / "retry_scope.json"

    print(f"当前检查失败，请执行：python -m packages repair-plan {project_id}")
    if summary_path.exists() or retry_scope_path.exists():
        print("如已有 remediation 产物，请优先读取：")
        if summary_path.exists():
            print(f"- {summary_path}")
        if retry_scope_path.exists():
            print(f"- {retry_scope_path}")
FORBIDDEN_TERM_ALLOWED_SECTIONS = {
    "facts.md": {"任务意图", "事实来源说明", "范围与非范围", "已知约束", "开放问题与缺口"},
    "business_blueprint.md": {"附录 E：链路自检信息"},
    "experience_blueprint.md": {"1. 交互流程总览", "2. 主交互流程"},
}
BOUNDARY_DECLARATION_FLAGS = ["不输出", "不得输出", "不覆盖", "不包含", "不进入", "非范围", "暂不展开", "任务边界", "评审边界", "不覆盖范围"]

FACTS_RUNTIME_SOURCE_ALLOWED_SECTIONS = {
    "任务意图",
    "事实来源说明",
    "范围与非范围",
    "已知约束",
    "开放问题与缺口",
}
FACTS_RUNTIME_SOURCE_BLOCKED_SECTIONS = {
    "功能范围",
    "关键业务规则",
    "状态流转",
    "异常与边界",
    "依赖与前置条件",
}
RUNTIME_SOURCE_REF_MARKERS = [
    "task_card_resolved.json",
    "context_manifest.json",
    "task_card.md",
]
RUNTIME_LEAKAGE_TERMS = [
    "facts 阶段不得",
    "business 阶段不得",
    "experience 阶段不得",
    "不得用聊天回复替代正式文档产物",
    "不得输出 UI 方案",
    "输出 UI 方案",
    "高保真视觉稿",
    "任务执行链路",
    "当前真实需求文档承载页",
    "输出反馈页",
    "任务合同页面",
    "正式生成链路",
    "generation 结构",
]
RUNTIME_LEAKAGE_ALLOWED_SECTIONS = {
    "facts.md": {"任务意图", "事实来源说明", "范围与非范围", "已知约束", "开放问题与缺口"},
    "business_blueprint.md": {"附录 E：链路自检信息"},
    "experience_blueprint.md": {"1. 交互流程总览", "2. 主交互流程", "附录 E：原始状态 / 文案 / 风险矩阵"},
}

DEFAULT_TRACKED_OUTPUTS = [
    "projects/{project_id}/workspace/facts.md",
    "projects/{project_id}/workspace/business_blueprint.md",
    "projects/{project_id}/workspace/experience_blueprint.md",
    "projects/{project_id}/workspace/gap_list.md",
    "projects/{project_id}/workspace/check_report.md",
    "projects/{project_id}/workspace/check_status.json",
]

GENERIC_ID_PATTERN = re.compile(r"\b[A-Z]{1,8}-\d+\b")
OPTION_ID_PATTERN = re.compile(r"\bOPT?-\d+\b")
RISK_ID_PATTERN = re.compile(r"\b(?:RSK|RK|AP)-\d+\b")
SECTION_HEADING_PATTERN = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
SUBPAGE_HEADING_PATTERN = re.compile(r"^(?:###|####)\s+(P-\d+)\b", re.MULTILINE)
LIST_ITEM_PATTERN = re.compile(r"^\s*(?:[-*]|\d+\.)\s+")
TABLE_SEPARATOR_PATTERN = re.compile(r"^\s*\|(?:\s*:?-+:?\s*\|)+\s*$")
PLACEHOLDER_PATTERN = re.compile(
    r"(<填写|{{TASK_ID}}|<project-id>|<角色名称>|<页面名称>|<术语>|<页面 / 子页 / 抽屉 / 弹窗 / 内嵌模块>)"
)
EXPERIENCE_CRITICAL_HINTS = [
    "状态",
    "异常",
    "阻断",
    "治理",
    "依赖",
    "风险",
    "规则",
    "审批",
    "关闭",
    "失败",
    "成功",
    "可操作",
    "不可操作",
    "二次确认",
    "提示",
    "反馈",
    "文案",
    "帮助",
]
EXPERIENCE_CORE_SECTION_TITLES = [
    "1. 交互流程总览",
    "2. 主交互流程",
    "3. 次交互流程",
    "4. 异常与阻断流程",
    "5. 页面 / 弹窗 / 抽屉设计",
    "6. 状态与反馈文案",
]
EXPERIENCE_MACHINE_LINE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bEV-\d+\b", re.IGNORECASE), "核心区包含 EV 编号"),
    (re.compile(r"source[_ ]?path", re.IGNORECASE), "核心区包含 source_path"),
    (re.compile(r"(?:从当前输入直接抽取|未做模板补全)"), "核心区暴露了生成过程提示语"),
    (re.compile(r"(?:生成基于当前真实需求文档承载页)"), "核心区存在明显机器化表达"),
]
EXPERIENCE_NODE_PATTERN = re.compile(r"^\*\*节点\s*\d+", re.MULTILINE)
EXPERIENCE_PAGE_BLOCK_PATTERN = re.compile(r"^\*\*(?:页面|弹窗|抽屉)：", re.MULTILINE)
EXPERIENCE_STATE_BLOCK_PATTERN = re.compile(r"^-+\s*状态：", re.MULTILINE)

ROLE_ALIASES: dict[str, list[str]] = {
    "超管": ["超管", "超级管理员"],
    "员工": ["员工"],
    "审批人": ["审批人", "组织负责人"],
}

HANDOFF_FLOW_CHECKS: list[tuple[str, list[str]]] = [
    ("超管配置", ["超管", "配置", "启用"]),
    ("员工发起申请", ["员工", "申请权限", "提交"]),
    ("系统前置校验", ["校验", "拦截", "认证"]),
    ("审批人审批", ["审批人", "同意", "否决"]),
    ("自动授权或拒绝", ["自动", "授权"]),
    ("结果通知员工", ["通知", "员工"]),
]

HANDOFF_EXCEPTION_CHECKS: list[tuple[str, list[str], list[str]]] = [
    ("互斥模式冲突拦截", ["互斥", "冲突"], ["无法同时开启", "互斥"]),
    ("关闭模式时在途流程阻断", ["关闭", "在途"], ["关闭失败", "未完成审批", "在途"]),
    ("资金用户校验失败", ["资金用户", "代发付款"], ["资金用户", "代发付款", "无法申请"]),
    ("子管理员模式拦截", ["子管理员"], ["子管理员", "不可通过自助申请获得"]),
]

HANDOFF_STATE_CHECKS: list[tuple[str, list[str], list[str]]] = [
    ("模式状态", ["未启用", "已启用"], ["未启用", "已启用"]),
    ("申请单状态", ["审批中", "已通过", "已拒绝", "已撤销"], ["审批中", "已通过", "已拒绝", "已撤销"]),
    ("权限生效结果", ["生效", "通过"], ["现在可以使用", "自动生效", "权限正在生效中"]),
]

HANDOFF_RISK_CHECKS: list[tuple[str, list[str], list[str], str]] = [
    (
        "审批人信息密度不足导致盲目审批",
        ["审批人负担过重", "审批页需要展示足够的前后对比信息"],
        ["当前已有权限", "申请获取的权限", "申请后将新增"],
        "承接检查：business_blueprint.md 强调审批人侧需要看到“当前已有权限 / 申请内容 / 新增影响”的判断辅助，但 experience_blueprint.md 还缺少足够完整的审批对比信息。",
    ),
    (
        "敏感权限绕过",
        ["敏感权限绕过", "敏感应用"],
        ["敏感应用", "不可申请", "联系企业管理员"],
        "承接检查：business_blueprint.md 已把敏感权限绕过列为关键风险，但 experience_blueprint.md 还没有把敏感应用不可自助申请的保护策略转译成用户可见规则或提示。",
    ),
    (
        "互斥认知盲区",
        ["认知盲区", "互斥提示需要说明原因"],
        ["审批链路", "冲突", "互斥"],
        "承接检查：business_blueprint.md 要求互斥提示解释“为什么不能同时开启”，但 experience_blueprint.md 还没有把原因说明转成用户可理解的提示。",
    ),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_workspace_dir(project_id: str) -> Path:
    return get_project_workspace_dir(project_id)


def get_gate_paths(project_id: str, stage: str) -> tuple[Path, Path]:
    gates_dir = get_project_gates_dir(project_id)
    gates_dir.mkdir(parents=True, exist_ok=True)
    return gates_dir / f"{stage}_gate_report.md", gates_dir / f"{stage}_gate_status.json"


def to_repo_rel(path: Path) -> str:
    try:
        return str(path.relative_to(get_repo_root())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def infer_issue_stage(default_stage: str, message: str) -> str:
    lowered = message.lower()
    if "facts 阶段未通过" in message or "facts gate" in lowered:
        return "facts"
    if "business 阶段未通过" in message or "business gate" in lowered:
        return "business"
    if "experience_blueprint.md" in lowered or "experience gate" in lowered:
        return "experience"
    if "business_blueprint.md" in lowered:
        return "business"
    if "facts.md" in lowered:
        return "facts"
    if "runtime/" in lowered or "context_manifest" in lowered or "task_card_resolved" in lowered:
        return "runtime"
    if default_stage == "final" and lowered.startswith("coverage:"):
        return "final"
    return default_stage


def infer_issue_source(default_stage: str, message: str) -> str:
    if default_stage == "final":
        coverage_warning_markers = (
            "承接检查：",
            "自然语言承接检查：",
            "设计指南消费检查：",
        )
        if any(message.startswith(marker) for marker in coverage_warning_markers):
            return "coverage"
        return "validate"
    return f"{default_stage}_gate"


def infer_issue_category(stage: str, message: str) -> str:
    lowered = message.lower()
    if " gate 状态" in message or "阶段状态：" in message or "阶段状态为" in message:
        return "quality_gap"
    if "缺少栏目" in message or "缺少必需章节" in message or ("缺少" in message and "## " in message):
        return "structure_missing"
    if "placeholder" in lowered or "占位" in message:
        return "placeholder_residue"
    if "设计指南" in message or "guideline" in lowered:
        return "experience_guideline_consumption_gap"
    if ("角色" in message and "路径" in message) or ("角色" in message and "覆盖" in message):
        return "experience_role_path_gap"
    if "状态" in message or "反馈" in message:
        return "experience_state_feedback_gap"
    if "异常" in message or "阻断" in message or "拦截" in message:
        return "experience_exception_handling_gap"
    if "用户可见文案" in message or "文案" in message:
        return "experience_copy_not_user_visible"
    if "承接检查" in message or "business_blueprint.md 中强调" in message:
        return "experience_business_consumption_gap"
    if lowered.startswith("handoff:") or lowered.startswith("coverage:") or "自然语言承接检查" in message:
        return "coverage_gap"
    if "未通过" in message or "状态为 failed" in message:
        return "stage_blocked"
    if "不完整" in message or "偏弱" in message or "不足" in message:
        return "depth_insufficient"
    if "sql" in lowered or "前端实现" in message or "高保真视觉" in message:
        return "boundary_violation"
    if "冲突" in message or "不一致" in message:
        return "consistency_conflict"
    if "缺失" in message or "missing" in lowered:
        return "structure_missing"
    return "quality_gap"


def infer_target_artifacts(project_id: str, stage: str, message: str, checked_files: list[str]) -> list[str]:
    workspace_prefix = f"projects/{project_id}/workspace"
    runtime_prefix = f"projects/{project_id}/runtime"
    inferred: list[str] = []
    lowered = message.lower()

    if "facts.md" in lowered or "facts gate" in lowered:
        inferred.append(f"{workspace_prefix}/facts.md")
    if "business_blueprint.md" in lowered or "business gate" in lowered:
        inferred.append(f"{workspace_prefix}/business_blueprint.md")
    if "experience_blueprint.md" in lowered or "experience gate" in lowered:
        inferred.append(f"{workspace_prefix}/experience_blueprint.md")
    if "gap_list.md" in lowered:
        inferred.append(f"{workspace_prefix}/gap_list.md")
    if "check_status.json" in lowered:
        inferred.append(f"{workspace_prefix}/check_status.json")
    if "check_report.md" in lowered:
        inferred.append(f"{workspace_prefix}/check_report.md")
    if "trace_index.json" in lowered:
        inferred.append(f"{runtime_prefix}/trace_index.json")
    if "gate_metrics.json" in lowered:
        inferred.append(f"{runtime_prefix}/gate_metrics.json")
    if "context_manifest.json" in lowered:
        inferred.append(f"{runtime_prefix}/context_manifest.json")
    if "task_card_resolved.json" in lowered:
        inferred.append(f"{runtime_prefix}/task_card_resolved.json")

    if not inferred:
        if stage == "facts":
            inferred.append(f"{workspace_prefix}/facts.md")
        elif stage == "business":
            inferred.append(f"{workspace_prefix}/business_blueprint.md")
        elif stage == "experience":
            inferred.append(f"{workspace_prefix}/experience_blueprint.md")
        elif stage == "runtime":
            inferred.append(f"{runtime_prefix}/gate_metrics.json")
        else:
            inferred.append(f"{workspace_prefix}/check_status.json")

    for checked_file in checked_files:
        if checked_file in inferred:
            continue
        if Path(checked_file).name == Path(inferred[0]).name:
            inferred.append(checked_file)

    return dedupe_keep_order(inferred)


def infer_violated_contract_refs(stage: str, source: str) -> list[str]:
    refs = ["specs/06_check_contract.md"]
    if stage == "facts":
        refs.append("specs/08_fact_extraction_contract.md")
    elif stage == "business":
        refs.append("specs/09_business_blueprint_contract.md")
    elif stage == "experience":
        refs.append("specs/10_experience_blueprint_contract.md")
    if source in {"facts_gate", "business_gate", "experience_gate"} and "specs/11_repair_loop_contract.md" not in refs:
        refs.append("specs/11_repair_loop_contract.md")
    return refs


def build_issue_details(
    project_id: str,
    default_stage: str,
    blockers: list[str],
    warnings: list[str],
    infos: list[str],
    checked_files: list[str],
    metrics: dict[str, object],
) -> list[dict[str, Any]]:
    issue_details: list[dict[str, Any]] = []
    for severity, messages in [("blocker", blockers), ("warning", warnings), ("info", infos)]:
        for message in messages:
            issue_stage = infer_issue_stage(default_stage, message)
            issue_source = infer_issue_source(default_stage, message)
            issue_details.append(
                {
                    "source": issue_source,
                    "stage": issue_stage,
                    "severity": severity,
                    "category": infer_issue_category(issue_stage, message),
                    "message": message,
                    "target_artifacts": infer_target_artifacts(project_id, issue_stage, message, checked_files),
                    "violated_contract_refs": infer_violated_contract_refs(issue_stage, issue_source),
                    "checked_files": checked_files,
                    "evidence": [
                        {"type": "message", "value": message},
                        {"type": "checked_files", "value": checked_files[:8]},
                        {"type": "metrics", "value": metrics},
                    ],
                }
            )
    return issue_details


def add_issue(issues: list[tuple[str, str]], level: str, message: str) -> None:
    issues.append((level, message))


def extend_issues(target: list[tuple[str, str]], extra: list[tuple[str, str]]) -> None:
    target.extend(extra)


def summarize_issues(issues: list[tuple[str, str]]) -> tuple[list[str], list[str], list[str], str]:
    blockers = [message for level, message in issues if level == "blocker"]
    warnings = [message for level, message in issues if level == "warning"]
    infos = [message for level, message in issues if level == "info"]
    status = "passed"
    if blockers:
        status = "failed"
    elif warnings:
        status = "warning"
    return blockers, warnings, infos, status


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def check_runtime_contract(project_id: str, issues: list[tuple[str, str]]) -> None:
    runtime_dir = get_project_runtime_dir(project_id)
    resolved_path = runtime_dir / "task_card_resolved.json"
    manifest_path = runtime_dir / "context_manifest.json"

    resolved: dict[str, object] = {}
    manifest: dict[str, object] = {}

    if not resolved_path.exists():
        add_issue(issues, "blocker", "缺少 runtime/task_card_resolved.json")
    else:
        resolved = read_json(resolved_path)
        if not resolved:
            add_issue(issues, "blocker", "runtime/task_card_resolved.json 不可读取或不是有效 JSON")
        else:
            resolved_errors = _string_list(resolved.get("errors"))
            if resolved_errors:
                add_issue(issues, "blocker", f"task_card_resolved.json 存在解析错误：{' | '.join(resolved_errors[:3])}")
            if not _string_list(resolved.get("task_goal")):
                add_issue(issues, "blocker", "task_card_resolved.json 缺少 task_goal")
            if not _string_list(resolved.get("execution_constraints")):
                add_issue(issues, "blocker", "task_card_resolved.json 缺少 execution_constraints")
            if not _string_list(resolved.get("read_order")):
                add_issue(issues, "warning", "task_card_resolved.json 缺少 read_order")

    if not manifest_path.exists():
        add_issue(issues, "blocker", "缺少 runtime/context_manifest.json")
        return

    manifest = read_json(manifest_path)
    if not manifest:
        add_issue(issues, "blocker", "runtime/context_manifest.json 不可读取或不是有效 JSON")
        return

    task_contract = manifest.get("task_contract")
    if not isinstance(task_contract, dict):
        add_issue(issues, "blocker", "context_manifest.json 缺少 task_contract")
        return

    if not _string_list(task_contract.get("task_goal")):
        add_issue(issues, "blocker", "context_manifest.json.task_contract 缺少 task_goal")
    if not _string_list(task_contract.get("execution_constraints")):
        add_issue(issues, "blocker", "context_manifest.json.task_contract 缺少 execution_constraints")
    if not _string_list(task_contract.get("read_order")):
        add_issue(issues, "warning", "context_manifest.json.task_contract 缺少 read_order")

    if resolved:
        mismatched_fields: list[str] = []
        for field in ("task_goal", "task_scenario", "execution_constraints", "read_order", "notes"):
            if _string_list(resolved.get(field)) != _string_list(task_contract.get(field)):
                mismatched_fields.append(field)
        if mismatched_fields:
            add_issue(
                issues,
                "warning",
                f"context_manifest.json.task_contract 与 task_card_resolved.json 不一致：{', '.join(mismatched_fields)}",
            )


def check_knowledge_consumption_plan(project_id: str, issues: list[tuple[str, str]]) -> None:
    runtime_dir = get_project_runtime_dir(project_id)
    manifest = read_json(runtime_dir / "context_manifest.json")
    usage_report = read_json(runtime_dir / "knowledge_usage_report.json")

    plan = manifest.get("knowledge_consumption_plan")
    if not isinstance(plan, dict):
        add_issue(issues, "blocker", "context_manifest.json 缺少 knowledge_consumption_plan")
        return

    facts = plan.get("facts")
    business = plan.get("business")
    experience = plan.get("experience")
    if not isinstance(facts, dict) or not isinstance(business, dict) or not isinstance(experience, dict):
        add_issue(issues, "blocker", "knowledge_consumption_plan 结构不完整")
        return

    facts_required = _string_list(facts.get("required_wiki_refs"))
    facts_raw = _string_list(facts.get("raw_refs_from_source_refs"))
    business_raw = _string_list(business.get("raw_refs_from_source_refs"))
    experience_raw = _string_list(experience.get("raw_refs_from_source_refs"))

    if not facts_required:
        add_issue(issues, "warning", "knowledge_consumption_plan.facts 缺少 required_wiki_refs")
    if facts_raw:
        add_issue(issues, "warning", "knowledge_consumption_plan.facts 不应默认读取 raw_refs_from_source_refs")
    if "raw_refs_from_source_refs" not in business:
        add_issue(issues, "warning", "knowledge_consumption_plan.business 缺少 raw_refs_from_source_refs")
    if "raw_refs_from_source_refs" not in experience:
        add_issue(issues, "warning", "knowledge_consumption_plan.experience 缺少 raw_refs_from_source_refs")

    repo_root = get_repo_root()
    for raw_ref in business_raw + experience_raw:
        normalized = raw_ref.replace("\\", "/")
        raw_path = repo_root / Path(normalized.replace("/", "\\"))
        if normalized.endswith("/") or "." not in Path(normalized).name:
            add_issue(issues, "blocker", f"raw ref 必须是文件，不能是目录：{normalized}")
            continue
        if raw_path.exists() and raw_path.is_dir():
            add_issue(issues, "blocker", f"raw ref 指向目录，禁止装配：{normalized}")

    stage_usage = usage_report.get("stage_usage")
    if not isinstance(stage_usage, dict):
        add_issue(issues, "warning", "knowledge_usage_report.json 缺少 stage_usage")
        return
    business_usage = stage_usage.get("business")
    experience_usage = stage_usage.get("experience")
    if not isinstance(business_usage, dict) or "source_ref_chains" not in business_usage:
        add_issue(issues, "warning", "knowledge_usage_report.json 缺少 business.source_ref_chains")
    if not isinstance(experience_usage, dict) or "source_ref_chains" not in experience_usage:
        add_issue(issues, "warning", "knowledge_usage_report.json 缺少 experience.source_ref_chains")


def extract_fact_ids(text: str) -> list[str]:
    del text
    return []


def extract_judgment_ids(text: str) -> list[str]:
    del text
    return []


def has_experience_critical_signal(text: str) -> bool:
    if not text:
        return False
    return any(item in text for item in EXPERIENCE_CRITICAL_HINTS)


def find_critical_judgment_ids(business_text: str, judgment_ids: list[str]) -> list[str]:
    del business_text, judgment_ids
    return []


def extract_page_ids(text: str) -> list[str]:
    del text
    return []


def extract_flow_ids(text: str) -> list[str]:
    del text
    return []


def extract_generic_ids(text: str) -> list[str]:
    return sorted(set(GENERIC_ID_PATTERN.findall(text)))


def parse_h2_sections(content: str) -> dict[str, str]:
    matches = list(SECTION_HEADING_PATTERN.finditer(content))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        sections[title] = content[start:end].strip()
    return sections


def get_experience_core_text(sections: dict[str, str]) -> str:
    return "\n".join(sections.get(title, "") for title in EXPERIENCE_CORE_SECTION_TITLES)


def find_repeated_page_names_in_core(section_text: str) -> list[str]:
    candidates: list[str] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        content = stripped[2:].strip()
        if "（" in content:
            content = content.split("（", 1)[0].strip()
        if "：" in content:
            content = content.split("：", 1)[-1].strip()
        normalized = re.sub(r"[^\w\u4e00-\u9fff]", "", content)
        if len(normalized) < 6:
            continue
        candidates.append(normalized)
    if len(candidates) < 4:
        return []
    repeats = {item for item in candidates if candidates.count(item) >= 3}
    return sorted(repeats)


def get_section(content: str, heading: str) -> str:
    title = heading.replace("## ", "", 1) if heading.startswith("## ") else heading
    return parse_h2_sections(content).get(title, "")


def count_real_table_rows(text: str) -> int:
    pipe_lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    if not pipe_lines:
        return 0
    separator_count = sum(1 for line in pipe_lines if TABLE_SEPARATOR_PATTERN.match(line))
    non_separator_rows = [line for line in pipe_lines if not TABLE_SEPARATOR_PATTERN.match(line)]
    non_placeholder_rows = [line for line in non_separator_rows if not PLACEHOLDER_PATTERN.search(line)]
    header_count = min(separator_count, len(non_placeholder_rows))
    return max(0, len(non_placeholder_rows) - header_count)


def count_real_list_items(text: str) -> int:
    return sum(1 for line in text.splitlines() if LIST_ITEM_PATTERN.match(line) and not PLACEHOLDER_PATTERN.search(line))


def count_text_diagrams(text: str) -> int:
    fenced_count = text.count("```text")
    diagram_lines = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if any(char in stripped for char in ("└", "├", "┌", "┐", "┘", "┴", "│")):
            diagram_lines += 1
        elif stripped.startswith("[") and stripped.endswith("]"):
            diagram_lines += 1
        elif "->" in stripped:
            diagram_lines += 1
    return fenced_count + diagram_lines


def count_unique_matches(pattern: re.Pattern[str], text: str) -> int:
    return len(sorted(set(pattern.findall(text))))


def count_keywords_present(text: str, keywords: list[str]) -> int:
    return sum(1 for keyword in keywords if keyword in text)


def contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def normalize_for_match(text: str) -> str:
    lowered = text.lower()
    return re.sub(r"\s+", "", lowered)


def contains_phrase(text: str, phrase: str) -> bool:
    return normalize_for_match(phrase) in normalize_for_match(text)


def contains_any_phrase(text: str, phrases: list[str]) -> bool:
    return any(contains_phrase(text, phrase) for phrase in phrases)


def contains_all_phrases(text: str, phrases: list[str]) -> bool:
    return all(contains_phrase(text, phrase) for phrase in phrases)


def count_pattern_matches(pattern: re.Pattern[str], text: str) -> int:
    return len(pattern.findall(text))


def count_role_mentions(text: str, aliases: dict[str, list[str]]) -> dict[str, bool]:
    return {role: contains_any_phrase(text, role_aliases) for role, role_aliases in aliases.items()}


def extract_principle_refs(
    text: str,
    fact_ids: list[str] | None = None,
    judgment_ids: list[str] | None = None,
    page_ids: list[str] | None = None,
    flow_ids: list[str] | None = None,
) -> list[str]:
    principle_lines = [line for line in text.splitlines() if ("原则" in line or "guideline" in line.lower())]
    ids: set[str] = set()
    for line in principle_lines:
        ids.update(re.findall(GENERIC_ID_PATTERN, line))
    excluded = set(fact_ids or []) | set(judgment_ids or []) | set(page_ids or []) | set(flow_ids or [])
    return sorted(item for item in ids if item not in excluded)


def count_expanded_page_blueprints(section_text: str) -> int:
    return len({match for match in SUBPAGE_HEADING_PATTERN.findall(section_text) if match})


def check_required_headings(file_name: str, content: str, issues: list[tuple[str, str]]) -> None:
    for heading in STAGE_REQUIRED_HEADINGS.get(file_name, []):
        if heading not in content:
            add_issue(issues, "blocker", f"{file_name} 缺少栏目：{heading}")


def check_forbidden_terms(file_name: str, content: str, issues: list[tuple[str, str]]) -> None:
    sections = parse_h2_sections(content)
    allowed_sections = FORBIDDEN_TERM_ALLOWED_SECTIONS.get(file_name, set())
    for term in FORBIDDEN_TERMS.get(file_name, []):
        if term.startswith("## "):
            if re.search(rf"(?m)^{re.escape(term)}\s*$", content):
                add_issue(issues, "warning", f"{file_name} 可能仍沿用旧口径：{term}")
            continue
        flagged = False
        for section_name, section_text in sections.items():
            if term not in section_text:
                continue
            if section_name in allowed_sections:
                continue
            for line in section_text.splitlines():
                if term not in line:
                    continue
                if any(flag in line for flag in BOUNDARY_DECLARATION_FLAGS):
                    continue
                add_issue(issues, "warning", f"{file_name} 可能越过阶段边界：包含 {term}")
                flagged = True
                break
            if flagged:
                break


def check_placeholders(file_name: str, content: str, issues: list[tuple[str, str]]) -> None:
    if PLACEHOLDER_PATTERN.search(content):
        add_issue(issues, "warning", f"{file_name} 仍包含占位内容")


def check_required_files(required_paths: list[Path], issues: list[tuple[str, str]]) -> None:
    for file_path in required_paths:
        if not file_path.exists():
            add_issue(issues, "blocker", f"缺少文件：{to_repo_rel(file_path)}")


def required_output_paths(project_id: str, resolved_data: dict[str, object]) -> list[str]:
    values = resolved_data.get("required_outputs")
    if isinstance(values, list) and values:
        return [str(item).replace("\\", "/") for item in values]
    return [item.format(project_id=project_id) for item in DEFAULT_TRACKED_OUTPUTS]


def report_summary_lines(status: str, blockers: list[str], warnings: list[str], infos: list[str]) -> list[str]:
    return [
        "## Summary",
        "",
        f"- status: {status}",
        f"- has_blocker: {'true' if blockers else 'false'}",
        f"- blocker_count: {len(blockers)}",
        f"- warning_count: {len(warnings)}",
        f"- info_count: {len(infos)}",
        "",
    ]


def render_stage_gate_report(
    project_id: str,
    stage: str,
    next_stage: str,
    blockers: list[str],
    warnings: list[str],
    infos: list[str],
    status: str,
    checked_files: list[str],
) -> str:
    lines = [
        "# Stage Gate Report",
        "",
        *report_summary_lines(status, blockers, warnings, infos),
        f"- project_id: {project_id}",
        f"- stage: {stage}",
        f"- next_stage: {next_stage}",
        f"- can_proceed: {'true' if status != 'failed' else 'false'}",
        "",
        "## Checked Files",
        "",
    ]
    lines.extend([f"- {item}" for item in checked_files] or ["- none"])
    lines.extend(["", "## Blockers", ""])
    lines.extend([f"- {item}" for item in blockers] or ["- none"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {item}" for item in warnings] or ["- none"])
    lines.extend(["", "## Infos", ""])
    lines.extend([f"- {item}" for item in infos] or ["- none"])
    return "\n".join(lines) + "\n"


def render_final_report(
    project_id: str,
    status: str,
    blockers: list[str],
    warnings: list[str],
    infos: list[str],
    output_status_lines: list[str],
    coverage_lines: list[str],
) -> str:
    lines = [
        "# Check Report｜人读说明版",
        "",
        f"> 本文件是 `projects/{project_id}/workspace/check_status.json` 的人读说明版。",
        "> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。",
        "> 机器判断请以 `check_status.json` 为准。",
        "",
        *report_summary_lines(status, blockers, warnings, infos),
        "## Output Status",
        "",
    ]
    lines.extend([f"- {item}" for item in output_status_lines] or ["- none"])
    lines.extend(["", "## Blockers", ""])
    lines.extend([f"- {item}" for item in blockers] or ["- none"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {item}" for item in warnings] or ["- none"])
    lines.extend(["", "## Infos", ""])
    lines.extend([f"- {item}" for item in infos] or ["- none"])
    lines.extend(["", "## 自然语言承接检查", ""])
    lines.extend([f"- {item}" for item in coverage_lines] or ["- not_run"])
    lines.extend(["", "## Machine Status", "", f"- 机器可读状态文件：`projects/{project_id}/workspace/check_status.json`", ""])
    return "\n".join(lines)


def build_gate_payload(
    project_id: str,
    stage: str,
    next_stage: str,
    blockers: list[str],
    warnings: list[str],
    infos: list[str],
    checked_files: list[str],
    metrics: dict[str, object],
) -> dict[str, object]:
    status = "passed"
    if blockers:
        status = "failed"
    elif warnings:
        status = "warning"
    issue_details = build_issue_details(project_id, stage, blockers, warnings, infos, checked_files, metrics)
    return {
        "project_id": project_id,
        "stage": stage,
        "status": status,
        "can_proceed": status != "failed",
        "next_stage": next_stage,
        "generated_by": "packages.validate",
        "updated_at": now_iso(),
        "checked_files": checked_files,
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "info_count": len(infos),
        "issues": {"blockers": blockers, "warnings": warnings, "infos": infos},
        "issue_details_version": "1.0",
        "issue_details": issue_details,
        "metrics": metrics,
    }


def build_final_payload(
    project_id: str,
    blockers: list[str],
    warnings: list[str],
    infos: list[str],
    completed_outputs: list[str],
    missing_outputs: list[str],
    checked_files: list[str],
    metrics: dict[str, object],
) -> dict[str, object]:
    status = "passed"
    if blockers:
        status = "failed"
    elif warnings:
        status = "warning"
    issue_details = build_issue_details(project_id, "final", blockers, warnings, infos, checked_files, metrics)
    return {
        "task_id": project_id,
        "status": status,
        "has_blocker": bool(blockers),
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "info_count": len(infos),
        "completed_outputs": completed_outputs,
        "missing_outputs": missing_outputs,
        "generated_by": "packages.validate",
        "updated_at": now_iso(),
        "checked_files": checked_files,
        "issues": {"blockers": blockers, "warnings": warnings, "infos": infos},
        "issue_details_version": "1.0",
        "issue_details": issue_details,
        "metrics": metrics,
    }


def write_gate_artifacts(
    project_id: str,
    stage: str,
    next_stage: str,
    blockers: list[str],
    warnings: list[str],
    infos: list[str],
    checked_files: list[str],
    metrics: dict[str, object],
) -> tuple[Path, Path, str]:
    report_path, status_path = get_gate_paths(project_id, stage)
    payload = build_gate_payload(project_id, stage, next_stage, blockers, warnings, infos, checked_files, metrics)
    report = render_stage_gate_report(project_id, stage, next_stage, blockers, warnings, infos, str(payload["status"]), checked_files)
    report_path.write_text(report, encoding="utf-8")
    status_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return report_path, status_path, str(payload["status"])


def read_gate_status(project_id: str, stage: str) -> dict[str, object] | None:
    _, status_path = get_gate_paths(project_id, stage)
    if not status_path.exists():
        return None
    return json.loads(status_path.read_text(encoding="utf-8"))


def add_provenance_issues(issues: list[tuple[str, str]], project_id: str, required_commands: list[str]) -> None:
    for issue in validate_provenance(project_id, required_commands=required_commands):
        add_issue(issues, "blocker", f"provenance: {issue}")


def write_runtime_extension_artifacts(
    project_id: str,
    fact_ids: list[str],
    judgment_ids: list[str],
    page_ids: list[str],
    facts_in_business: list[str],
    facts_in_experience: list[str],
    judgments_in_experience: list[str],
) -> None:
    runtime_dir = get_project_runtime_dir(project_id)
    workspace_dir = get_workspace_dir(project_id)

    trace_index = {
        "task_id": project_id,
        "facts": [
            {
                "id": item,
                "in_business": item in facts_in_business,
                "in_experience": item in facts_in_experience,
            }
            for item in fact_ids
        ],
        "judgments": [
            {
                "id": item,
                "in_experience": item in judgments_in_experience,
            }
            for item in judgment_ids
        ],
        "pages": [{"id": item} for item in page_ids],
    }
    (runtime_dir / "trace_index.json").write_text(json.dumps(trace_index, ensure_ascii=False, indent=2), encoding="utf-8")

    gate_metrics = {
        "task_id": project_id,
        "facts_gate": read_gate_status(project_id, "facts") or {},
        "business_gate": read_gate_status(project_id, "business") or {},
        "experience_gate": read_gate_status(project_id, "experience") or {},
        "final_check_status": read_json(workspace_dir / "check_status.json"),
    }
    (runtime_dir / "gate_metrics.json").write_text(json.dumps(gate_metrics, ensure_ascii=False, indent=2), encoding="utf-8")


def compute_dimension_coverage(facts_text: str) -> dict[str, int]:
    keys = {
        "overview": ["## 任务概述"],
        "features": ["## 功能范围"],
        "rules": ["## 关键业务规则"],
        "states": ["## 状态流转"],
        "exceptions": ["## 异常与边界"],
        "dependencies": ["## 依赖与前置条件"],
        "gaps": ["## 开放问题与缺口"],
    }
    result: dict[str, int] = {}
    for key, patterns in keys.items():
        result[key] = 1 if any(pattern in facts_text for pattern in patterns) else 0
    return result


def evaluate_facts_source_legality(project_id: str, facts_text: str) -> tuple[int, int]:
    required_sources = [
        [f"projects/{project_id}/source/requirement.md", "/requirement.md", "\\requirement.md"],
        [f"projects/{project_id}/source/background.md", "/background.md", "\\background.md"],
    ]
    source_hits = sum(1 for markers in required_sources if any(marker in facts_text for marker in markers))
    knowledge_hits = facts_text.count("knowledge/") + facts_text.count("wiki/")
    return source_hits, knowledge_hits


def check_facts_source_guard(project_id: str, facts_text: str, issues: list[tuple[str, str]]) -> None:
    sections = parse_h2_sections(facts_text)
    for section_name in FACTS_RUNTIME_SOURCE_BLOCKED_SECTIONS:
        section_text = sections.get(section_name, "")
        if not section_text:
            continue
        hits = [marker for marker in RUNTIME_SOURCE_REF_MARKERS if marker in section_text]
        if hits:
            add_issue(
                issues,
                "warning",
                f"facts.md 的业务事实章节“{section_name}”不应引用 runtime/source task card 来源：{', '.join(hits)}",
            )


def check_runtime_leakage_guard(file_name: str, content: str, issues: list[tuple[str, str]]) -> None:
    allowed_sections = RUNTIME_LEAKAGE_ALLOWED_SECTIONS.get(file_name, set())
    for section_name, section_text in parse_h2_sections(content).items():
        if section_name in allowed_sections or not section_text:
            continue
        hits = [term for term in RUNTIME_LEAKAGE_TERMS if term in section_text]
        if hits:
            add_issue(
                issues,
                "warning",
                f"{file_name} 的“{section_name}”疑似混入执行合同语句：{', '.join(sorted(set(hits))[:4])}",
            )


def check_status_report_consistency(status_data: dict[str, object], report_text: str, issues: list[tuple[str, str]]) -> None:
    status = str(status_data.get("status", ""))
    blocker_count = int(status_data.get("blocker_count", 0))
    warning_count = int(status_data.get("warning_count", 0))
    info_count = int(status_data.get("info_count", 0))
    checks = [
        f"- status: {status}",
        f"- blocker_count: {blocker_count}",
        f"- warning_count: {warning_count}",
        f"- info_count: {info_count}",
    ]
    if not all(item in report_text for item in checks):
        add_issue(issues, "blocker", "check_report.md 与 check_status.json 的摘要字段不一致")


def analyze_business_blueprint(facts_text: str, business_text: str) -> tuple[dict[str, object], list[tuple[str, str]]]:
    issues: list[tuple[str, str]] = []
    sections = parse_h2_sections(business_text)

    stance_section = sections.get("1. 一句话结论", "")
    value_section = sections.get("3. 值不值得做", "")
    capability_section = sections.get("4. 应该做成什么能力形态", "")
    plan_section = sections.get("5. 推荐业务方案", "")
    boundary_section = sections.get("6. 必须守住的规则和边界", "")
    risk_section = sections.get("7. 主要风险与保护策略", "")
    handover_section = sections.get("8. 方案承接要求", "")
    pending_section = sections.get("9. 待确认问题", "")
    appendix_section = sections.get("附录：事实、知识与判断追踪", "")
    option_section = "\n".join([capability_section, appendix_section])

    option_compare_count = max(
        count_unique_matches(OPTION_ID_PATTERN, option_section),
        count_real_table_rows(option_section),
        count_real_list_items(option_section),
    )
    value_assessment_item_count = max(count_real_table_rows(value_section), count_real_list_items(value_section))
    risk_item_count = max(count_unique_matches(RISK_ID_PATTERN, risk_section), count_real_table_rows(risk_section), count_real_list_items(risk_section))
    appendix_item_count = max(count_real_table_rows(appendix_section), count_real_list_items(appendix_section))
    unresolved_gap_count = business_text.count("[GAP]") + business_text.count("开放问题")
    has_appendix = bool(appendix_section.strip())
    handover_keyword_count = count_keywords_present(handover_section, ["角色", "流程", "状态", "异常", "风险"])
    handover_item_count = max(count_real_table_rows(handover_section), count_real_list_items(handover_section))
    has_handover_empty_talk = contains_any(handover_section, ["后续根据实际情况设计", "按实际情况调整", "后续再细化", "待后续补齐"])
    fact_section_keywords = ["任务概述", "功能范围", "关键业务规则", "状态流转", "异常与边界", "开放问题与缺口"]
    referenced_fact_sections = [item for item in fact_section_keywords if item in facts_text and item in appendix_section]

    if not stance_section.strip():
        add_issue(issues, "blocker", "business_blueprint.md 缺少最终业务立场内容")

    if option_compare_count == 0:
        add_issue(issues, "warning", "business_blueprint.md 备选路径比较检测不到结构化内容，请确认已用自然语言表达")
    elif option_compare_count < 2:
        add_issue(issues, "warning", "business_blueprint.md 备选路径比较仍偏少，建议至少保留两个以上可比方案")

    if value_assessment_item_count == 0 or count_keywords_present(value_section, ["价值", "收益", "成本", "认知", "负担"]) < 2:
        add_issue(issues, "warning", "business_blueprint.md 价值/成本/认知负担评估检测不到结构化内容，请确认已在自然语言中覆盖")

    if risk_item_count == 0:
        add_issue(issues, "warning", "business_blueprint.md 风险与保护策略内容偏少")

    if count_real_list_items(plan_section) == 0 and count_real_table_rows(plan_section) == 0:
        add_issue(issues, "warning", "business_blueprint.md 推荐业务方案检测不到结构化内容，请确认已用自然语言表达")

    if count_real_list_items(boundary_section) == 0 and count_real_table_rows(boundary_section) == 0:
        add_issue(issues, "warning", "business_blueprint.md 规则与边界描述偏少")

    if handover_item_count == 0:
        add_issue(issues, "warning", "business_blueprint.md 方案承接要求检测不到结构化内容，请确认已用自然语言表达")
    elif handover_keyword_count < 3:
        add_issue(issues, "warning", "business_blueprint.md 方案承接要求覆盖不足，建议至少覆盖角色/流程/状态/异常/风险中的 3 类")
    if has_handover_empty_talk:
        add_issue(issues, "warning", "business_blueprint.md 方案承接要求存在空话，建议改为可执行要求")

    if not appendix_section.strip():
        add_issue(issues, "warning", "business_blueprint.md 缺少有效的判断依据说明")
    elif not referenced_fact_sections:
        add_issue(issues, "warning", "business_blueprint.md 附录没有自然说明主要依据来自 facts 的哪些章节，判断依据承接仍偏弱")

    if not pending_section.strip() and unresolved_gap_count == 0:
        add_issue(issues, "warning", "business_blueprint.md 未显式保留开放问题或缺口")
    if not has_appendix:
        add_issue(issues, "warning", "business_blueprint.md 缺少附录（事实、知识与判断追踪）")

    metrics = {
        "option_compare_count": option_compare_count,
        "value_assessment_item_count": value_assessment_item_count,
        "risk_item_count": risk_item_count,
        "unresolved_gap_count": unresolved_gap_count,
        "has_appendix": has_appendix,
        "appendix_item_count": appendix_item_count,
        "referenced_fact_section_count": len(referenced_fact_sections),
        "handover_item_count": handover_item_count,
        "handover_keyword_count": handover_keyword_count,
        "has_handover_empty_talk": has_handover_empty_talk,
    }
    return metrics, issues


def analyze_experience_blueprint(
    _facts_text: str,
    business_text: str,
    experience_text: str,
) -> tuple[dict[str, object], list[tuple[str, str]]]:
    issues: list[tuple[str, str]] = []
    sections = parse_h2_sections(experience_text)
    main_flow_section = sections.get("2. 主交互流程", "")
    secondary_flow_section = sections.get("3. 次交互流程", "")
    exception_flow_section = sections.get("4. 异常与阻断流程", "")
    page_design_section = sections.get("5. 页面 / 弹窗 / 抽屉设计", "")
    state_copy_section = sections.get("6. 状态与反馈文案", "")
    pending_section = sections.get("7. 待确认问题", "")
    appendix_section = sections.get("附录：依据与追踪", "")
    core_text = get_experience_core_text(sections)

    flow_section = "\n".join([main_flow_section, secondary_flow_section])
    flow_count = max(
        count_real_table_rows(flow_section),
        count_real_list_items(flow_section),
        count_pattern_matches(EXPERIENCE_NODE_PATTERN, flow_section),
    )
    page_inventory_item_count = max(
        count_real_table_rows(page_design_section),
        count_real_list_items(page_design_section),
        count_pattern_matches(EXPERIENCE_PAGE_BLOCK_PATTERN, page_design_section),
    )
    state_feedback_pair_count = max(
        count_real_table_rows(state_copy_section),
        count_real_list_items(state_copy_section),
        count_pattern_matches(EXPERIENCE_STATE_BLOCK_PATTERN, state_copy_section),
    )
    appendix_item_count = max(count_real_table_rows(appendix_section), count_real_list_items(appendix_section))

    exception_text = "\n".join([main_flow_section, secondary_flow_section, exception_flow_section, state_copy_section])
    has_exception_coverage = contains_any(
        exception_text,
        ["失败", "阻断", "拦截", "拒绝", "异常", "不可", "空态", "冲突", "审批中", "处理中", "关闭失败"],
    )

    if flow_count == 0:
        add_issue(issues, "warning", "experience_blueprint.md 交互流程检测不到结构化内容，请确认已用自然语言写清各节点")

    if page_inventory_item_count == 0:
        add_issue(issues, "warning", "experience_blueprint.md 页面设计检测不到结构化内容，请确认已用自然语言写清各页面")

    if state_feedback_pair_count == 0:
        add_issue(issues, "blocker", "experience_blueprint.md 缺少状态与异常处理信息")

    if count_real_list_items(pending_section) == 0:
        add_issue(issues, "warning", "experience_blueprint.md 待确认问题为空，建议显式标注不确定项")

    if appendix_item_count == 0:
        add_issue(issues, "warning", "experience_blueprint.md 附录：依据与追踪内容偏少")

    if not has_exception_coverage:
        add_issue(issues, "blocker", "experience_blueprint.md 仅覆盖 happy path，未显式覆盖异常态 / 阻断态")

    for pattern, message in EXPERIENCE_MACHINE_LINE_PATTERNS:
        if pattern.search(core_text):
            add_issue(issues, "warning", f"experience_blueprint.md {message}")

    core_table_count = count_real_table_rows(core_text)
    if core_table_count > 0:
        add_issue(issues, "warning", "experience_blueprint.md 核心区包含表格，建议改为节点化 Markdown 层级表达")

    repeated_page_names = find_repeated_page_names_in_core(sections.get("5. 页面 / 弹窗 / 抽屉设计", ""))
    if repeated_page_names:
        add_issue(issues, "warning", "experience_blueprint.md 核心区页面名重复较多，建议继续语义去重")

    if "审批人" in business_text and not contains_any_phrase(experience_text, ["审批详情页", "权限申请审批", "当前已有权限"]):
        add_issue(issues, "warning", "experience_blueprint.md 提到了审批人流程，但审批详情页还没有体现足够的判断辅助信息")

    metrics = {
        "flow_count": flow_count,
        "page_inventory_item_count": page_inventory_item_count,
        "state_feedback_pair_count": state_feedback_pair_count,
        "appendix_item_count": appendix_item_count,
        "exception_coverage": has_exception_coverage,
        "core_table_count": core_table_count,
    }
    return metrics, issues


def analyze_natural_language_handoff(
    business_text: str,
    experience_text: str,
    usage_report: dict[str, object] | None = None,
) -> tuple[dict[str, object], list[tuple[str, str]], list[str]]:
    issues: list[tuple[str, str]] = []
    coverage_lines: list[str] = []
    business_sections = parse_h2_sections(business_text)
    experience_sections = parse_h2_sections(experience_text)

    handover_section = business_sections.get("8. 方案承接要求", "")
    risk_section = business_sections.get("7. 主要风险与保护策略", "")
    business_signal_text = "\n".join([handover_section, risk_section, business_text])
    experience_signal_text = "\n".join(
        [
            experience_sections.get("1. 交互流程总览", ""),
            experience_sections.get("2. 主交互流程", ""),
            experience_sections.get("3. 次交互流程", ""),
            experience_sections.get("4. 异常与阻断流程", ""),
            experience_sections.get("5. 页面 / 弹窗 / 抽屉设计", ""),
            experience_sections.get("6. 状态与反馈文案", ""),
        ]
    )

    required_roles = {
        role: aliases
        for role, aliases in ROLE_ALIASES.items()
        if contains_any_phrase(handover_section or business_text, aliases)
    }
    role_hits = count_role_mentions(experience_signal_text, required_roles or ROLE_ALIASES)
    required_role_count = len(required_roles or ROLE_ALIASES)
    covered_role_count = sum(1 for covered in role_hits.values() if covered)
    coverage_lines.append(f"角色路径覆盖：{covered_role_count}/{required_role_count}")
    for role, covered in role_hits.items():
        if role in (required_roles or ROLE_ALIASES) and not covered:
            add_issue(
                issues,
                "warning",
                f"承接检查：business_blueprint.md 要求覆盖“{role}”角色路径，但 experience_blueprint.md 还没有给出这类角色的清晰任务路径或页面承接。",
            )

    required_flow_checks = [item for item in HANDOFF_FLOW_CHECKS if contains_any_phrase(handover_section or business_text, item[1])]
    covered_flow_count = 0
    for flow_name, required_phrases in required_flow_checks:
        if contains_any_phrase(experience_signal_text, required_phrases):
            covered_flow_count += 1
        else:
            add_issue(
                issues,
                "warning",
                f"承接检查：business_blueprint.md 明确要求主流程闭环包含“{flow_name}”，但 experience_blueprint.md 还没有把这一段转成清晰的用户流程、系统反馈或结果去向。",
            )
    coverage_lines.append(f"主流程闭环覆盖：{covered_flow_count}/{len(required_flow_checks)}")

    required_exception_count = 0
    covered_exception_count = 0
    for exception_name, business_phrases, expected_phrases in HANDOFF_EXCEPTION_CHECKS:
        if not contains_any_phrase(business_signal_text, business_phrases):
            continue
        required_exception_count += 1
        if contains_any_phrase(experience_signal_text, expected_phrases):
            covered_exception_count += 1
            continue
        add_issue(
            issues,
            "warning",
            f"承接检查：business_blueprint.md 已把“{exception_name}”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。",
        )
    coverage_lines.append(f"异常与阻断覆盖：{covered_exception_count}/{required_exception_count}")

    required_state_count = 0
    covered_state_count = 0
    for state_name, business_phrases, expected_phrases in HANDOFF_STATE_CHECKS:
        if not contains_any_phrase(business_signal_text, business_phrases):
            continue
        required_state_count += 1
        if contains_any_phrase(experience_sections.get("6. 状态与反馈文案", ""), expected_phrases):
            covered_state_count += 1
            continue
        add_issue(
            issues,
            "warning",
            f"承接检查：business_blueprint.md 要求解释“{state_name}”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。",
        )
    coverage_lines.append(f"状态与反馈覆盖：{covered_state_count}/{required_state_count}")

    required_risk_count = 0
    covered_risk_count = 0
    for _risk_name, business_phrases, expected_phrases, warning_message in HANDOFF_RISK_CHECKS:
        if not contains_any_phrase(business_signal_text, business_phrases):
            continue
        required_risk_count += 1
        if contains_any_phrase(experience_signal_text, expected_phrases):
            covered_risk_count += 1
            continue
        add_issue(issues, "warning", warning_message)
    coverage_lines.append(f"风险保护承接：{covered_risk_count}/{required_risk_count}")

    guideline_refs_used: list[str] = []
    guideline_selection_reason: list[dict[str, object]] = []
    if usage_report:
        stage_usage = usage_report.get("stage_usage")
        if isinstance(stage_usage, dict):
            experience_usage = stage_usage.get("experience")
            if isinstance(experience_usage, dict):
                guideline_refs_used = _string_list(experience_usage.get("guideline_refs_used"))
                raw_reason = experience_usage.get("guideline_selection_reason")
                if isinstance(raw_reason, list):
                    guideline_selection_reason = [item for item in raw_reason if isinstance(item, dict)]

    if not guideline_refs_used:
        add_issue(issues, "warning", "设计指南消费检查：knowledge_usage_report.json 未记录 experience 阶段实际消费的 design guideline。")
    elif not guideline_selection_reason:
        add_issue(issues, "warning", "设计指南消费检查：knowledge_usage_report.json 缺少 guideline_selection_reason，无法说明为何选择这些设计指南。")
    coverage_lines.append(f"设计指南消费：{len(guideline_refs_used)} 条")

    metrics = {
        "required_role_count": required_role_count,
        "covered_role_count": covered_role_count,
        "required_flow_step_count": len(required_flow_checks),
        "covered_flow_step_count": covered_flow_count,
        "required_exception_count": required_exception_count,
        "covered_exception_count": covered_exception_count,
        "required_state_count": required_state_count,
        "covered_state_count": covered_state_count,
        "required_risk_count": required_risk_count,
        "covered_risk_count": covered_risk_count,
        "guideline_refs_used_count": len(guideline_refs_used),
    }
    return metrics, issues, coverage_lines


def run_validate_outputs(project_id: str) -> int:
    workspace_dir = get_workspace_dir(project_id)
    runtime_dir = get_project_runtime_dir(project_id)
    report_path = workspace_dir / "check_report.md"
    status_path = workspace_dir / "check_status.json"
    issues: list[tuple[str, str]] = []
    checked_files: list[str] = []

    resolved = read_json(runtime_dir / "task_card_resolved.json")
    context_manifest = read_json(runtime_dir / "context_manifest.json")
    usage_report = read_json(runtime_dir / "knowledge_usage_report.json")
    required_outputs = required_output_paths(project_id, resolved)
    checked_files.extend(
        [
            f"projects/{project_id}/runtime/task_card_resolved.json",
            f"projects/{project_id}/runtime/context_manifest.json",
            f"projects/{project_id}/runtime/knowledge_usage_report.json",
        ]
    )
    add_provenance_issues(
        issues,
        project_id,
        required_commands=[
            "generate-facts",
            "generate-business",
            "generate-experience",
        ],
    )
    check_runtime_contract(project_id, issues)
    check_knowledge_consumption_plan(project_id, issues)
    output_status_lines: list[str] = []
    completed_outputs: list[str] = []
    missing_outputs: list[str] = []

    for output_path_str in required_outputs:
        normalized = output_path_str.replace("\\", "/")
        checked_files.append(normalized)
        output_path = get_repo_root() / normalized
        if output_path.exists():
            completed_outputs.append(normalized)
            output_status_lines.append(f"{normalized}: present")
        else:
            missing_outputs.append(normalized)
            output_status_lines.append(f"{normalized}: missing")
            add_issue(issues, "blocker", f"必需输出缺失：{normalized}")

    facts_text = read_text(workspace_dir / "facts.md")
    business_text = read_text(workspace_dir / "business_blueprint.md")
    experience_text = read_text(workspace_dir / "experience_blueprint.md")
    if f"projects/{project_id}/source/task_card.md" in facts_text:
        add_issue(issues, "warning", "facts.md 仍直接引用 source/task_card.md，可能存在双入口")

    for file_name, content in [
        ("facts.md", facts_text),
        ("business_blueprint.md", business_text),
        ("experience_blueprint.md", experience_text),
        ("gap_list.md", read_text(workspace_dir / "gap_list.md")),
    ]:
        if not content:
            continue
        check_required_headings(file_name, content, issues)
        check_forbidden_terms(file_name, content, issues)
        check_placeholders(file_name, content, issues)
        check_runtime_leakage_guard(file_name, content, issues)
        checked_files.append(f"projects/{project_id}/workspace/{file_name}")
    if facts_text:
        check_facts_source_guard(project_id, facts_text, issues)

    business_metrics: dict[str, object] = {}
    experience_metrics: dict[str, object] = {}
    handoff_metrics: dict[str, object] = {}
    coverage_lines = ["not_run"]

    if facts_text and business_text:
        business_metrics, business_depth_issues = analyze_business_blueprint(facts_text, business_text)
        extend_issues(issues, business_depth_issues)

    if facts_text and business_text and experience_text:
        experience_metrics, experience_depth_issues = analyze_experience_blueprint(facts_text, business_text, experience_text)
        extend_issues(issues, experience_depth_issues)
        handoff_metrics, handoff_issues, coverage_lines = analyze_natural_language_handoff(
            business_text,
            experience_text,
            usage_report,
        )
        extend_issues(issues, handoff_issues)

    has_directory_ref = bool(resolved.get("has_directory_ref"))
    requires_narrowing = bool(resolved.get("requires_narrowing"))
    narrowed_references = context_manifest.get("narrowed_references", [])
    fallback_copied = context_manifest.get("directory_refs_fallback_copied", [])
    strict_mode = bool(context_manifest.get("strict_mode"))
    fallback_sources_used = usage_report.get("fallback_sources_used", [])
    fallback_conditions = resolved.get("fallback_conditions", [])
    resolved_to_index = context_manifest.get("directory_refs_resolved_to_index", [])

    if has_directory_ref and fallback_copied:
        add_issue(issues, "warning", "Broad knowledge references required directory fallback copy during context assembly")
    if requires_narrowing and not narrowed_references and not fallback_copied:
        add_issue(issues, "warning", "Broad knowledge references were declared but no narrowing action was recorded")
    if fallback_sources_used and not fallback_conditions:
        add_issue(issues, "warning", "Fallback knowledge sources were used without explicit fallback conditions")
    if strict_mode and fallback_copied:
        add_issue(issues, "blocker", "Strict assembly mode still produced directory fallback copies")
    if resolved_to_index and fallback_copied:
        add_issue(issues, "warning", "Some broad references were narrowed while others still fell back to directory copies")

    for stage in ["facts", "business", "experience"]:
        gate_status = read_gate_status(project_id, stage)
        checked_files.append(f"projects/{project_id}/runtime/gates/{stage}_gate_status.json")
        if not gate_status:
            add_issue(issues, "blocker", f"缺少 {stage} gate 状态文件")
            continue
        if gate_status.get("status") == "failed":
            add_issue(issues, "blocker", f"{stage} gate 状态为 failed")
        elif gate_status.get("status") == "warning":
            add_issue(issues, "warning", f"{stage} gate 状态为 warning")
        else:
            add_issue(issues, "info", f"{stage} gate 状态：{gate_status.get('status')}")

    blockers, warnings, infos, status = summarize_issues(issues)
    report_text = render_final_report(project_id, status, blockers, warnings, infos, output_status_lines, coverage_lines)
    report_path.write_text(report_text, encoding="utf-8")

    metrics = {
        "required_output_count": len(required_outputs),
        "completed_output_count": len(completed_outputs),
        "missing_output_count": len(missing_outputs),
        "business_depth": business_metrics,
        "experience_depth": experience_metrics,
        "experience_handoff": handoff_metrics,
    }
    payload = build_final_payload(
        project_id,
        blockers,
        warnings,
        infos,
        sorted(set(completed_outputs)),
        sorted(set(missing_outputs)),
        sorted(set(checked_files)),
        metrics,
    )
    status_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Validation finished: {report_path}")
    print(f"Machine status written: {status_path}")
    append_command_if_provenance_exists(project_id, "validate")
    if status == "failed":
        _print_repair_guidance(project_id)
    return 0 if status != "failed" else 1


def run_coverage_check(project_id: str) -> int:
    workspace_dir = get_workspace_dir(project_id)
    report_path = workspace_dir / "check_report.md"
    status_path = workspace_dir / "check_status.json"

    report_text = read_text(report_path)
    if not report_text:
        raise SystemExit(f"Missing report: {report_path}")
    status_data = read_json(status_path)
    if not status_data:
        raise SystemExit(f"Missing machine status: {status_path}")

    facts_text = read_text(workspace_dir / "facts.md")
    business_text = read_text(workspace_dir / "business_blueprint.md")
    experience_text = read_text(workspace_dir / "experience_blueprint.md")
    usage_report = read_json(get_project_runtime_dir(project_id) / "knowledge_usage_report.json")
    handoff_metrics, handoff_issues, coverage_lines = analyze_natural_language_handoff(
        business_text,
        experience_text,
        usage_report,
    )

    blockers = list(status_data.get("issues", {}).get("blockers", []))
    warnings = list(status_data.get("issues", {}).get("warnings", []))
    infos = list(status_data.get("issues", {}).get("infos", []))

    for level, message in handoff_issues:
        if level == "blocker":
            blockers.append(message)
        elif level == "warning":
            warnings.append(message)
        else:
            infos.append(message)

    infos.extend([f"自然语言承接检查：{line}" for line in coverage_lines])
    blockers = sorted(set(blockers))
    warnings = sorted(set(warnings))
    infos = sorted(set(infos))

    status = "passed"
    if blockers:
        status = "failed"
    elif warnings:
        status = "warning"

    output_status_lines = [line[2:] if line.startswith("- ") else line for line in re.findall(r"^- .+: (?:present|missing)$", report_text, flags=re.MULTILINE)]
    final_report = render_final_report(project_id, status, blockers, warnings, infos, output_status_lines, coverage_lines)
    report_path.write_text(final_report, encoding="utf-8")

    status_data["status"] = status
    status_data["has_blocker"] = bool(blockers)
    status_data["blocker_count"] = len(blockers)
    status_data["warning_count"] = len(warnings)
    status_data["info_count"] = len(infos)
    status_data["generated_by"] = "packages.validate"
    status_data["updated_at"] = now_iso()
    status_data.setdefault("issues", {})
    status_data["issues"]["blockers"] = blockers
    status_data["issues"]["warnings"] = warnings
    status_data["issues"]["infos"] = infos
    status_data["metrics"] = status_data.get("metrics", {})
    status_data["metrics"]["coverage"] = handoff_metrics
    checked_files = [str(item) for item in status_data.get("checked_files", []) if isinstance(item, str)]
    status_data["issue_details_version"] = "1.0"
    status_data["issue_details"] = build_issue_details(
        project_id,
        "final",
        blockers,
        warnings,
        infos,
        checked_files,
        status_data["metrics"],
    )
    status_path.write_text(json.dumps(status_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Coverage check finished: {report_path}")
    print(f"Machine status updated: {status_path}")
    append_command_if_provenance_exists(project_id, "coverage")
    if status == "failed":
        _print_repair_guidance(project_id)
    return 0 if status != "failed" else 1


def run_facts_gate(project_id: str) -> int:
    source_dir = get_project_source_dir(project_id)
    runtime_dir = get_project_runtime_dir(project_id)
    workspace_dir = get_workspace_dir(project_id)
    facts_path = workspace_dir / "facts.md"
    task_resolved_path = runtime_dir / "task_card_resolved.json"
    context_manifest_path = runtime_dir / "context_manifest.json"

    issues: list[tuple[str, str]] = []
    add_provenance_issues(issues, project_id, required_commands=["generate-facts"])
    checked_files = [
        f"projects/{project_id}/source/task_card.md",
        f"projects/{project_id}/source/requirement.md",
        f"projects/{project_id}/source/background.md",
        f"projects/{project_id}/runtime/task_card_resolved.json",
        f"projects/{project_id}/runtime/context_manifest.json",
        f"projects/{project_id}/runtime/provenance.json",
        f"projects/{project_id}/workspace/facts.md",
    ]
    check_required_files(
        [
            source_dir / "task_card.md",
            source_dir / "requirement.md",
            source_dir / "background.md",
            task_resolved_path,
            context_manifest_path,
            facts_path,
        ],
        issues,
    )

    facts_text = read_text(facts_path)
    if facts_text:
        check_required_headings("facts.md", facts_text, issues)
        check_forbidden_terms("facts.md", facts_text, issues)
        check_placeholders("facts.md", facts_text, issues)
        check_runtime_leakage_guard("facts.md", facts_text, issues)
        check_facts_source_guard(project_id, facts_text, issues)

        dimension = compute_dimension_coverage(facts_text)
        covered_count = sum(dimension.values())
        if covered_count < 5:
            add_issue(issues, "blocker", "facts.md 章节覆盖不足，无法稳定支撑业务判断")
        elif covered_count < 7:
            add_issue(issues, "warning", "facts.md 章节覆盖仍偏粗")

        source_hits, knowledge_hits = evaluate_facts_source_legality(project_id, facts_text)
        if source_hits == 0:
            add_issue(issues, "blocker", "facts.md 未显式承接 requirement/background 输入来源")
        elif source_hits < 2:
            add_issue(issues, "warning", "facts.md 输入来源引用不完整")
        if knowledge_hits and source_hits == 0:
            add_issue(issues, "blocker", "facts.md 可能将知识补写为输入事实，请补充输入来源追溯")

        if "[GAP]" not in facts_text and "## 开放问题与缺口" not in facts_text:
            add_issue(issues, "warning", "facts.md 未显式暴露缺口")

    context_manifest = read_json(context_manifest_path)
    resolved = read_json(task_resolved_path)
    warnings = context_manifest.get("warnings", [])
    if isinstance(warnings, list):
        for item in warnings:
            warning_text = str(item)
            if "directory-only" in warning_text or "directory" in warning_text:
                add_issue(issues, "warning", f"context_manifest 警告：{warning_text}")

    if resolved.get("has_directory_ref"):
        add_issue(issues, "warning", "task_card_resolved.json reports broad knowledge references that may require narrowing")
    fallback_copied = context_manifest.get("directory_refs_fallback_copied", [])
    if isinstance(fallback_copied, list) and fallback_copied:
        joined_refs = ", ".join(str(item) for item in fallback_copied)
        add_issue(issues, "warning", f"context_manifest reports directory fallback copies: {joined_refs}")

    blockers, warnings, infos, _ = summarize_issues(issues)
    metrics = {
        "dimension_coverage": compute_dimension_coverage(facts_text),
        "gap_count": facts_text.count("[GAP]"),
        "knowledge_derived_fact_count": 0,
    }
    report_path, status_path, status = write_gate_artifacts(
        project_id,
        "facts",
        "business",
        blockers,
        warnings,
        infos,
        checked_files,
        metrics,
    )
    print(f"Facts gate finished: {report_path}")
    print(f"Facts gate status: {status_path}")
    append_command_if_provenance_exists(project_id, "gate-facts")
    if status == "failed":
        _print_repair_guidance(project_id)
    return 0 if status != "failed" else 1


def run_business_gate(project_id: str) -> int:
    workspace_dir = get_workspace_dir(project_id)
    issues: list[tuple[str, str]] = []
    add_provenance_issues(issues, project_id, required_commands=["generate-facts", "generate-business"])
    checked_files = [
        f"projects/{project_id}/workspace/facts.md",
        f"projects/{project_id}/workspace/business_blueprint.md",
        f"projects/{project_id}/runtime/provenance.json",
        f"projects/{project_id}/runtime/gates/facts_gate_status.json",
    ]

    facts_gate = read_gate_status(project_id, "facts")
    if not facts_gate:
        add_issue(issues, "blocker", "缺少 facts 阶段 gate 结果，请先运行 gate-facts")
    elif facts_gate.get("status") == "failed":
        add_issue(issues, "blocker", "facts 阶段未通过，不能进入业务蓝图阶段")
    else:
        add_issue(issues, "info", f"facts 阶段状态：{facts_gate.get('status')}")

    facts_text = read_text(workspace_dir / "facts.md")
    business_text = read_text(workspace_dir / "business_blueprint.md")
    if not facts_text:
        add_issue(issues, "blocker", "缺少 facts.md")
    if not business_text:
        add_issue(issues, "blocker", "缺少 business_blueprint.md")

    if business_text:
        check_required_headings("business_blueprint.md", business_text, issues)
        check_forbidden_terms("business_blueprint.md", business_text, issues)
        check_placeholders("business_blueprint.md", business_text, issues)
        check_runtime_leakage_guard("business_blueprint.md", business_text, issues)
        metrics, business_depth_issues = analyze_business_blueprint(facts_text, business_text)
        extend_issues(issues, business_depth_issues)
    else:
        metrics = {}

    blockers, warnings, infos, _ = summarize_issues(issues)
    report_path, status_path, status = write_gate_artifacts(
        project_id,
        "business",
        "experience",
        blockers,
        warnings,
        infos,
        checked_files,
        metrics,
    )
    print(f"Business gate finished: {report_path}")
    print(f"Business gate status: {status_path}")
    append_command_if_provenance_exists(project_id, "gate-business")
    if status == "failed":
        _print_repair_guidance(project_id)
    return 0 if status != "failed" else 1


def run_experience_gate(project_id: str) -> int:
    workspace_dir = get_workspace_dir(project_id)
    issues: list[tuple[str, str]] = []
    add_provenance_issues(
        issues,
        project_id,
        required_commands=["generate-facts", "generate-business", "generate-experience"],
    )
    checked_files = [
        f"projects/{project_id}/workspace/facts.md",
        f"projects/{project_id}/workspace/business_blueprint.md",
        f"projects/{project_id}/workspace/experience_blueprint.md",
        f"projects/{project_id}/runtime/provenance.json",
        f"projects/{project_id}/runtime/gates/business_gate_status.json",
    ]

    business_gate = read_gate_status(project_id, "business")
    if not business_gate:
        add_issue(issues, "blocker", "缺少 business 阶段 gate 结果，请先运行 gate-business")
    elif business_gate.get("status") == "failed":
        add_issue(issues, "blocker", "business 阶段未通过，不能进入体验蓝图阶段")
    else:
        add_issue(issues, "info", f"business 阶段状态：{business_gate.get('status')}")

    facts_text = read_text(workspace_dir / "facts.md")
    business_text = read_text(workspace_dir / "business_blueprint.md")
    experience_text = read_text(workspace_dir / "experience_blueprint.md")
    if not facts_text:
        add_issue(issues, "blocker", "缺少 facts.md")
    if not business_text:
        add_issue(issues, "blocker", "缺少 business_blueprint.md")
    if not experience_text:
        add_issue(issues, "blocker", "缺少 experience_blueprint.md")

    if experience_text:
        check_required_headings("experience_blueprint.md", experience_text, issues)
        check_forbidden_terms("experience_blueprint.md", experience_text, issues)
        check_placeholders("experience_blueprint.md", experience_text, issues)
        check_runtime_leakage_guard("experience_blueprint.md", experience_text, issues)
        metrics, experience_depth_issues = analyze_experience_blueprint(facts_text, business_text, experience_text)
        extend_issues(issues, experience_depth_issues)
    else:
        metrics = {}

    blockers, warnings, infos, _ = summarize_issues(issues)
    report_path, status_path, status = write_gate_artifacts(
        project_id,
        "experience",
        "final-validate",
        blockers,
        warnings,
        infos,
        checked_files,
        metrics,
    )
    print(f"Experience gate finished: {report_path}")
    print(f"Experience gate status: {status_path}")
    append_command_if_provenance_exists(project_id, "gate-experience")
    if status == "failed":
        _print_repair_guidance(project_id)
    return 0 if status != "failed" else 1
