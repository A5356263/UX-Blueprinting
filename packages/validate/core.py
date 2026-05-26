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
from packages.route_decision import load_uxb_execution_decision


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
        "## 0. 本次关键设计判断",
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
        "## 0. 本次关键设计判断",
        "## 1. 旅程图",
        "## 2. 交互流程总览",
        "## 3. 主交互流程",
        "## 4. 次交互流程",
        "## 5. 异常与阻断流程",
        "## 6. 页面 / 弹窗 / 抽屉设计",
        "## 7. 状态与反馈文案",
        "## 8. 待确认问题",
    ],
    "gap_list.md": ["## Blockers", "## Warnings", "## 待补信息"],
    "business_note.md": [
        "## 0. 路线说明",
        "## 1. 业务依据",
        "## 2. 核心业务规则影响",
        "## 3. 体验可承接内容",
        "## 4. 升级信号",
        "## 5. 待确认问题",
    ],
    "business_blueprint_lite.md": [
        "## 0. 路线说明",
        "## 1. 一句话结论",
        "## 2. 关键业务规则",
        "## 3. 边界与风险",
        "## 4. 体验承接要求",
        "## 5. 升级信号",
        "## 6. 待确认问题",
    ],
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
    "business_note.md": [
        "页面区块布局",
        "高保真视觉",
        "组件开发实现",
        "前端技术栈",
        "SQL",
        "数据库表",
    ],
    "business_blueprint_lite.md": [
        "页面区块布局",
        "高保真视觉",
        "组件开发实现",
        "前端技术栈",
        "SQL",
        "数据库表",
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
    "experience_blueprint.md": {"2. 交互流程总览", "3. 主交互流程", "附录：设计指南消费说明"},
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
    "experience_blueprint.md": {"2. 交互流程总览", "3. 主交互流程", "附录：设计指南消费说明"},
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
    "1. 旅程图",
    "2. 交互流程总览",
    "3. 主交互流程",
    "4. 次交互流程",
    "5. 异常与阻断流程",
    "6. 页面 / 弹窗 / 抽屉设计",
    "7. 状态与反馈文案",
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

HANDOFF_CATEGORY_LABELS = {
    "roles": "必须覆盖的角色",
    "flows": "必须闭环的主流程",
    "exceptions": "必须处理的异常",
    "states": "必须解释的状态",
    "risks": "必须保护的风险",
}

HANDOFF_GENERIC_PHRASES = {
    "roles": ["角色", "配置方", "申请方", "审批方"],
    "flows": ["主流程", "流程", "路径", "闭环"],
    "exceptions": ["异常", "阻断", "拦截", "失败"],
    "states": ["状态", "反馈", "结果"],
    "risks": ["风险", "保护", "治理"],
}

HANDOFF_PHRASE_STOPWORDS = {
    "必须覆盖的角色",
    "必须闭环的主流程",
    "必须处理的异常",
    "必须解释的状态",
    "必须保护的风险",
    "experience阶段必须承接以下内容",
    "后续experience阶段必须承接的内容",
    "后续experience阶段必须承接的内容：",
    "可作为设计建议的内容",
    "角色",
    "流程",
    "异常",
    "状态",
    "风险",
    "配置方",
    "申请方",
    "审批方",
}

HANDOFF_SIGNAL_KEYWORDS = [
    "互斥",
    "冲突",
    "关闭",
    "审批",
    "审批人",
    "权限",
    "员工",
    "管理员",
    "范围",
    "申请",
    "超时",
    "失败",
    "拒绝",
    "通过",
    "未完成",
    "校验",
    "配置",
    "通知",
    "结果",
    "生效",
    "来源",
    "查询",
    "导出",
    "敏感",
    "时效",
    "离职",
    "兜底",
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
    manifest_path = runtime_dir / "context_manifest.json"

    if not manifest_path.exists():
        add_issue(issues, "blocker", "缺少 runtime/context_manifest.json")
        return

    manifest = read_json(manifest_path)
    if not manifest:
        add_issue(issues, "blocker", "runtime/context_manifest.json 不可读取或不是有效 JSON")
        return

    task_card_source = str(manifest.get("task_card_source") or "").strip()
    if not task_card_source:
        add_issue(issues, "blocker", "context_manifest.json 缺少 task_card_source")

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


def check_knowledge_consumption_plan(project_id: str, issues: list[tuple[str, str]]) -> None:
    runtime_dir = get_project_runtime_dir(project_id)
    manifest = read_json(runtime_dir / "context_manifest.json")

    selection_source = str(manifest.get("selection_source") or "").strip()
    if not selection_source:
        add_issue(issues, "blocker", "context_manifest.json 缺少 selection_source")
        return

    references = manifest.get("references")
    if not isinstance(references, list):
        add_issue(issues, "blocker", "context_manifest.json 缺少 references")
        return

    repo_root = get_repo_root()
    for item in references:
        if not isinstance(item, dict):
            continue
        reference = str(item.get("reference") or "").replace("\\", "/").strip()
        if not reference:
            continue
        ref_path = repo_root / Path(reference.replace("/", "\\"))
        if not ref_path.exists():
            add_issue(issues, "blocker", f"context_manifest.json 引用了不存在的 ref：{reference}")

    if not isinstance(manifest.get("selected_refs"), dict):
        add_issue(issues, "warning", "context_manifest.json 缺少 selected_refs")
    if not isinstance(manifest.get("assembled_refs"), list):
        add_issue(issues, "warning", "context_manifest.json 缺少 assembled_refs")
    if not isinstance(manifest.get("missing_refs"), list):
        add_issue(issues, "warning", "context_manifest.json 缺少 missing_refs")


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


def get_section_by_title(sections: dict[str, str], title: str) -> str:
    return sections.get(title, "")


def extract_first_markdown_table(text: str) -> tuple[list[str], list[list[str]]]:
    lines = text.splitlines()
    pipe_lines = [line for line in lines if line.strip().startswith("|")]
    if not pipe_lines:
        return [], []

    header_cells: list[str] = []
    body_rows: list[list[str]] = []
    found_header = False
    for i in range(len(lines) - 1):
        if lines[i].strip().startswith("|") and TABLE_SEPARATOR_PATTERN.match(lines[i + 1].strip()):
            header_cells = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
            found_header = True
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                body_rows.append([cell.strip() for cell in lines[j].strip().strip("|").split("|")])
                j += 1
            break
    return (header_cells, body_rows) if found_header else ([], [])


def journey_cell_contains_gap_marker(text: str) -> bool:
    normalized = normalize_handoff_line(strip_markdown_inline(text))
    if not normalized:
        return False

    lower_text = normalized.lower()
    if "journey gap" in lower_text or "[gap]" in lower_text:
        return True
    if normalized.startswith("旅程缺口"):
        return True

    explicit_prefixes = (
        "gap:",
        "gap：",
        "缺口:",
        "缺口：",
        "缺失:",
        "缺失：",
        "待补:",
        "待补：",
        "待确认:",
        "待确认：",
        "缺少",
        "尚缺",
        "未覆盖",
        "无法判断",
        "依据不足",
    )
    return normalized.startswith(explicit_prefixes)


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


def find_first_section_by_keyword(sections: dict[str, str], keyword: str) -> str:
    for title, section_text in sections.items():
        if keyword in title:
            return section_text
    return ""


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


def strip_markdown_inline(text: str) -> str:
    cleaned = text.replace("**", "").replace("`", "").strip()
    return re.sub(r"^#+\s*", "", cleaned).strip()


def normalize_handoff_line(text: str) -> str:
    cleaned = strip_markdown_inline(text)
    return re.sub(r"^\s*(?:[-*]|\d+\.)\s*", "", cleaned).strip()


def normalize_handoff_phrase(text: str) -> str:
    return re.sub(r"[^\w\u4e00-\u9fff]", "", strip_markdown_inline(text))


def is_meaningful_handoff_phrase(text: str) -> bool:
    normalized = normalize_handoff_phrase(text)
    if len(normalized) < 2:
        return False
    return normalized not in {normalize_handoff_phrase(item) for item in HANDOFF_PHRASE_STOPWORDS}


def extract_handoff_requirements(section_text: str) -> dict[str, list[str]]:
    items = {key: [] for key in HANDOFF_CATEGORY_LABELS}
    current_category: str | None = None

    for raw_line in section_text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        normalized = normalize_handoff_line(stripped)
        matched_category = next(
            (key for key, label in HANDOFF_CATEGORY_LABELS.items() if label in normalized),
            None,
        )
        if matched_category:
            current_category = matched_category
            continue
        if "可作为设计建议的内容" in normalized:
            current_category = None
            continue
        if current_category is None:
            continue

        is_item_line = bool(re.match(r"^\s*(?:[-*]|\d+\.)\s+", raw_line)) or stripped.startswith("**") or stripped.startswith("###")
        if not is_item_line:
            continue

        item_text = normalize_handoff_line(stripped)
        if not item_text or item_text in HANDOFF_CATEGORY_LABELS.values():
            continue
        items[current_category].append(item_text)

    return {key: dedupe_keep_order(value) for key, value in items.items()}


def extract_handoff_match_phrases(item_text: str, category: str) -> list[str]:
    candidates: list[str] = [item_text]
    split_queue = [item_text]

    if "：" in item_text:
        head, tail = item_text.split("：", 1)
        split_queue.extend([head, tail])
    elif ":" in item_text:
        head, tail = item_text.split(":", 1)
        split_queue.extend([head, tail])

    for segment in split_queue:
        candidates.extend(re.split(r"[→/、，,；;（）()+]", segment))
        if category in {"flows", "exceptions", "states", "risks"}:
            candidates.extend(re.split(r"(?:并|或|与|和|及)", segment))

    cleaned_candidates: list[str] = []
    for candidate in candidates:
        cleaned = normalize_handoff_line(candidate)
        cleaned = re.sub(r"^(?:配置方|申请方|审批方)\s*[:：]?\s*", "", cleaned)
        cleaned = cleaned.strip(" -:：")
        if not is_meaningful_handoff_phrase(cleaned):
            continue
        cleaned_candidates.append(cleaned)
        if category == "roles" and cleaned.endswith("管理员") and len(cleaned) > 3:
            cleaned_candidates.append("管理员")
        if category in {"exceptions", "states", "risks"}:
            for suffix in ["风险", "状态", "流程", "模式", "能力", "结果", "机制", "策略"]:
                if cleaned.endswith(suffix) and len(cleaned) > len(suffix) + 1:
                    trimmed = cleaned[: -len(suffix)]
                    if is_meaningful_handoff_phrase(trimmed):
                        cleaned_candidates.append(trimmed)
            for keyword in HANDOFF_SIGNAL_KEYWORDS:
                if keyword in cleaned:
                    cleaned_candidates.append(keyword)
        if category == "states":
            if "管理模式" in cleaned:
                cleaned_candidates.extend(["管理模式", "管理模式-已开启", "管理模式-未开启", "已开启", "未开启"])
            if "可见性" in cleaned:
                cleaned_candidates.extend(["适用对象", "可见"])
            if "可操作性" in cleaned:
                cleaned_candidates.extend(["用户可操作", "可操作"])
            if "下一步" in cleaned:
                cleaned_candidates.extend(["统一反馈口径", "下一步", "处理动作"])

    return dedupe_keep_order(cleaned_candidates)


def handoff_item_match_count(item_text: str, target_text: str, category: str) -> tuple[int, list[str]]:
    phrases = extract_handoff_match_phrases(item_text, category)
    hit_count = sum(1 for phrase in phrases if contains_phrase(target_text, phrase))
    return hit_count, phrases


def handoff_item_is_covered(item_text: str, target_text: str, category: str) -> tuple[bool, list[str]]:
    hit_count, phrases = handoff_item_match_count(item_text, target_text, category)
    required_hits = 1
    if category in {"flows", "exceptions", "states", "risks"} and len(phrases) >= 3:
        required_hits = 2
    return hit_count >= required_hits, phrases


def summarize_handoff_item(item_text: str, limit: int = 24) -> str:
    normalized = normalize_handoff_line(item_text)
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[:limit]}..."


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


def resolve_required_output_path(project_id: str, normalized_path: str) -> Path:
    workspace_prefix = f"projects/{project_id}/workspace/"
    runtime_prefix = f"projects/{project_id}/runtime/"
    source_prefix = f"projects/{project_id}/source/"
    if normalized_path.startswith(workspace_prefix):
        return get_project_workspace_dir(project_id) / normalized_path[len(workspace_prefix) :]
    if normalized_path.startswith(runtime_prefix):
        return get_project_runtime_dir(project_id) / normalized_path[len(runtime_prefix) :]
    if normalized_path.startswith(source_prefix):
        return get_project_source_dir(project_id) / normalized_path[len(source_prefix) :]
    return get_repo_root() / normalized_path


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
    journey_section = get_section_by_title(sections, "1. 旅程图")
    main_flow_section = get_section_by_title(sections, "3. 主交互流程")
    secondary_flow_section = get_section_by_title(sections, "4. 次交互流程")
    exception_flow_section = get_section_by_title(sections, "5. 异常与阻断流程")
    page_design_section = get_section_by_title(sections, "6. 页面 / 弹窗 / 抽屉设计")
    state_copy_section = get_section_by_title(sections, "7. 状态与反馈文案")
    pending_section = get_section_by_title(sections, "8. 待确认问题")
    appendix_section = sections.get("附录：设计指南消费说明", "")
    core_text = get_experience_core_text(sections)
    core_non_tabular_text = "\n".join([main_flow_section, secondary_flow_section, exception_flow_section, page_design_section])

    flow_section = "\n".join([main_flow_section, secondary_flow_section])
    journey_item_count = max(count_real_table_rows(journey_section), count_real_list_items(journey_section))
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

    if journey_item_count == 0:
        add_issue(issues, "warning", "experience_blueprint.md 缺少正式旅程图，或旅程图还没有形成可解析结构")

    if page_inventory_item_count == 0:
        add_issue(issues, "warning", "experience_blueprint.md 页面设计检测不到结构化内容，请确认已用自然语言写清各页面")

    if state_feedback_pair_count == 0:
        add_issue(issues, "blocker", "experience_blueprint.md 缺少状态与异常处理信息")

    if count_real_list_items(pending_section) == 0:
        add_issue(issues, "warning", "experience_blueprint.md 待确认问题为空，建议显式标注不确定项")

    if appendix_item_count == 0:
        add_issue(issues, "warning", "experience_blueprint.md 附录内容偏少，建议补充设计指南与业务知识消费说明")

    if not has_exception_coverage:
        add_issue(issues, "blocker", "experience_blueprint.md 仅覆盖 happy path，未显式覆盖异常态 / 阻断态")

    for pattern, message in EXPERIENCE_MACHINE_LINE_PATTERNS:
        if pattern.search(core_text):
            add_issue(issues, "warning", f"experience_blueprint.md {message}")

    core_table_count = count_real_table_rows(core_non_tabular_text)
    if core_table_count > 0:
        add_issue(issues, "warning", "experience_blueprint.md 主流程、异常或页面设计核心区包含表格，建议优先使用节点化 Markdown 层级表达")

    repeated_page_names = find_repeated_page_names_in_core(page_design_section)
    if repeated_page_names:
        add_issue(issues, "warning", "experience_blueprint.md 核心区页面名重复较多，建议继续语义去重")

    table_headers, table_rows = extract_first_markdown_table(journey_section)
    if table_headers and table_rows:
        for row in table_rows:
            for cell in row[1:]:
                stripped = strip_markdown_inline(cell).replace("<br>", "").replace("<br/>", "").replace("<br />", "")
                if "依据" in stripped or "规则" in stripped:
                    add_issue(issues, "warning", "experience_blueprint.md 旅程图单元格应只保留短节点，不应混入依据或规则说明")
                    break
                if journey_cell_contains_gap_marker(stripped):
                    add_issue(issues, "warning", "experience_blueprint.md 旅程缺口应单独放在旅程图下方，不应混入旅程表格单元格")
                    break
            else:
                continue
            break

    metrics = {
        "journey_item_count": journey_item_count,
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
    context_manifest: dict[str, object] | None = None,
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
            experience_sections.get("1. 旅程图", ""),
            experience_sections.get("2. 交互流程总览", ""),
            experience_sections.get("3. 主交互流程", ""),
            experience_sections.get("4. 次交互流程", ""),
            experience_sections.get("5. 异常与阻断流程", ""),
            experience_sections.get("6. 页面 / 弹窗 / 抽屉设计", ""),
            experience_sections.get("7. 状态与反馈文案", ""),
        ]
    )
    handoff_requirements = extract_handoff_requirements(handover_section)

    role_items = handoff_requirements.get("roles", [])
    if not role_items:
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
    else:
        covered_role_count = 0
        for item_text in role_items:
            covered, _phrases = handoff_item_is_covered(item_text, experience_signal_text, "roles")
            if covered:
                covered_role_count += 1
                continue
            add_issue(
                issues,
                "warning",
                f"承接检查：business_blueprint.md 已点名角色要求“{summarize_handoff_item(item_text)}”，但 experience_blueprint.md 还没有给出对应的清晰路径、页面或职责承接。",
            )
        coverage_lines.append(f"角色路径覆盖：{covered_role_count}/{len(role_items)}")
        required_role_count = len(role_items)

    flow_items = handoff_requirements.get("flows", [])
    covered_flow_count = 0
    for item_text in flow_items:
        covered, _phrases = handoff_item_is_covered(item_text, experience_signal_text, "flows")
        if covered:
            covered_flow_count += 1
            continue
        add_issue(
            issues,
            "warning",
            f"承接检查：business_blueprint.md 明确要求主流程闭环包含“{summarize_handoff_item(item_text)}”，但 experience_blueprint.md 还没有把这一段转成清晰的用户流程、系统反馈或结果去向。",
        )
    coverage_lines.append(f"主流程闭环覆盖：{covered_flow_count}/{len(flow_items)}")

    exception_items = handoff_requirements.get("exceptions", [])
    covered_exception_count = 0
    for item_text in exception_items:
        covered, _phrases = handoff_item_is_covered(item_text, experience_signal_text, "exceptions")
        if covered:
            covered_exception_count += 1
            continue
        add_issue(
            issues,
            "warning",
            f"承接检查：business_blueprint.md 已把“{summarize_handoff_item(item_text)}”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。",
        )
    coverage_lines.append(f"异常与阻断覆盖：{covered_exception_count}/{len(exception_items)}")

    state_items = handoff_requirements.get("states", [])
    covered_state_count = 0
    for item_text in state_items:
        covered, _phrases = handoff_item_is_covered(item_text, experience_sections.get("7. 状态与反馈文案", ""), "states")
        if covered:
            covered_state_count += 1
            continue
        add_issue(
            issues,
            "warning",
            f"承接检查：business_blueprint.md 要求解释“{summarize_handoff_item(item_text)}”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。",
        )
    coverage_lines.append(f"状态与反馈覆盖：{covered_state_count}/{len(state_items)}")

    risk_items = handoff_requirements.get("risks", [])
    if not risk_items and contains_any(business_signal_text, HANDOFF_GENERIC_PHRASES["risks"]):
        risk_items = [line.strip() for line in risk_section.splitlines() if LIST_ITEM_PATTERN.match(line)]
    covered_risk_count = 0
    for item_text in risk_items:
        covered, _phrases = handoff_item_is_covered(item_text, experience_signal_text, "risks")
        if covered:
            covered_risk_count += 1
            continue
        add_issue(
            issues,
            "warning",
            f"承接检查：business_blueprint.md 已把“{summarize_handoff_item(item_text)}”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。",
        )
    coverage_lines.append(f"风险保护承接：{covered_risk_count}/{len(risk_items)}")

    guideline_refs_used: list[str] = []
    if context_manifest:
        selected_refs = context_manifest.get("selected_refs")
        if isinstance(selected_refs, dict):
            guideline_refs_used = _string_list(selected_refs.get("guideline_refs"))

    has_guideline_appendix = "设计指南消费说明" in experience_text
    claims_guideline_consumed = has_guideline_appendix and any(marker in experience_text for marker in ("已消费", "消费的设计指南", "消费指南"))
    if claims_guideline_consumed and not guideline_refs_used:
        add_issue(issues, "blocker", "设计指南消费检查：experience_blueprint.md 声称已消费设计指南，但 context_manifest.json 没有对应记录。")
    coverage_lines.append(f"设计指南装配：{len(guideline_refs_used)} 条")

    metrics = {
        "required_role_count": required_role_count,
        "covered_role_count": covered_role_count,
        "required_flow_step_count": len(flow_items),
        "covered_flow_step_count": covered_flow_count,
        "required_exception_count": len(exception_items),
        "covered_exception_count": covered_exception_count,
        "required_state_count": len(state_items),
        "covered_state_count": covered_state_count,
        "required_risk_count": len(risk_items),
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

    context_manifest = read_json(runtime_dir / "context_manifest.json")
    required_outputs = required_output_paths(project_id, {})
    checked_files.extend(
        [
            f"projects/{project_id}/runtime/context_manifest.json",
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
        output_path = resolve_required_output_path(project_id, normalized)
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
            context_manifest,
        )
        extend_issues(issues, handoff_issues)

    resolved = context_manifest.get("resolved", {})
    has_directory_ref = bool(resolved.get("has_directory_ref"))
    requires_narrowing = bool(resolved.get("requires_narrowing"))
    narrowed_references = context_manifest.get("narrowed_references", [])
    fallback_copied = context_manifest.get("directory_refs_fallback_copied", [])
    strict_mode = bool(context_manifest.get("strict_mode"))
    usage_report = context_manifest.get("usage_report", {})
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
    context_manifest = read_json(get_project_runtime_dir(project_id) / "context_manifest.json")
    handoff_metrics, handoff_issues, coverage_lines = analyze_natural_language_handoff(
        business_text,
        experience_text,
        context_manifest,
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
    context_manifest_path = runtime_dir / "context_manifest.json"

    issues: list[tuple[str, str]] = []
    add_provenance_issues(issues, project_id, required_commands=["generate-facts"])
    checked_files = [
        f"projects/{project_id}/source/task_card.md",
        f"projects/{project_id}/source/requirement.md",
        f"projects/{project_id}/source/background.md",
        f"projects/{project_id}/runtime/context_manifest.json",
        f"projects/{project_id}/runtime/provenance.json",
        f"projects/{project_id}/workspace/facts.md",
    ]
    check_required_files(
        [
            source_dir / "task_card.md",
            source_dir / "requirement.md",
            source_dir / "background.md",
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
    warnings = context_manifest.get("warnings", [])
    if isinstance(warnings, list):
        for item in warnings:
            warning_text = str(item)
            if "directory-only" in warning_text or "directory" in warning_text:
                add_issue(issues, "warning", f"context_manifest 警告：{warning_text}")

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


def _section_text(content: str, heading: str) -> str:
    lines = content.splitlines()
    collecting = False
    collected: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == heading:
            collecting = True
            continue
        if collecting and stripped.startswith("## "):
            break
        if collecting:
            collected.append(line)
    return "\n".join(collected).strip()


def _read_execution_decision(project_id: str) -> dict[str, object]:
    return load_uxb_execution_decision(project_id)


def _add_execution_mode_info(project_id: str, issues: list[tuple[str, str]], expected_modes: set[str]) -> None:
    decision = _read_execution_decision(project_id)
    mode = str(decision.get("execution_mode") or "")
    if str(decision.get("status") or "") != "confirmed":
        details = "; ".join(str(item) for item in decision.get("validation_errors", []) if str(item).strip())
        add_issue(issues, "warning", f"当前 UXB 执行判断未确认：{details or '请先检查 runtime/uxb_route_decision.json'}")
        return
    if mode not in expected_modes:
        add_issue(issues, "warning", f"当前执行模式为 {mode or 'unknown'}，与本次 gate 预期 {', '.join(sorted(expected_modes))} 不一致")
    else:
        add_issue(issues, "info", f"执行模式：{mode}")


def run_business_note_gate(project_id: str) -> int:
    workspace_dir = get_workspace_dir(project_id)
    issues: list[tuple[str, str]] = []
    add_provenance_issues(issues, project_id, required_commands=["generate-facts", "generate-business-note"])
    checked_files = [
        f"projects/{project_id}/workspace/facts.md",
        f"projects/{project_id}/workspace/business_note.md",
        f"projects/{project_id}/runtime/uxb_route_decision.json",
        f"projects/{project_id}/runtime/provenance.json",
    ]
    _add_execution_mode_info(project_id, issues, {"fast"})

    facts_text = read_text(workspace_dir / "facts.md")
    note_text = read_text(workspace_dir / "business_note.md")
    if not facts_text:
        add_issue(issues, "blocker", "缺少 facts.md")
    if not note_text:
        add_issue(issues, "blocker", "缺少 business_note.md")

    if note_text:
        check_required_headings("business_note.md", note_text, issues)
        check_forbidden_terms("business_note.md", note_text, issues)
        check_placeholders("business_note.md", note_text, issues)
        check_runtime_leakage_guard("business_note.md", note_text, issues)
        impact_text = _section_text(note_text, "## 2. 核心业务规则影响")
        for dimension in ["权限", "数据范围", "审批", "状态机", "业务对象关系"]:
            if dimension not in impact_text:
                add_issue(issues, "blocker", f"business_note.md 未说明核心业务规则影响维度：{dimension}")
        if "体验可承接" not in note_text and not _section_text(note_text, "## 3. 体验可承接内容"):
            add_issue(issues, "blocker", "business_note.md 缺少 experience 可承接内容")

    blockers, warnings, infos, _ = summarize_issues(issues)
    metrics = {"artifact": "business_note.md"}
    report_path, status_path, status = write_gate_artifacts(
        project_id,
        "business_note",
        "experience",
        blockers,
        warnings,
        infos,
        checked_files,
        metrics,
    )
    print(f"Business note gate finished: {report_path}")
    print(f"Business note gate status: {status_path}")
    append_command_if_provenance_exists(project_id, "gate-business-note")
    if status == "failed":
        _print_repair_guidance(project_id)
    return 0 if status != "failed" else 1


def run_business_lite_gate(project_id: str) -> int:
    workspace_dir = get_workspace_dir(project_id)
    issues: list[tuple[str, str]] = []
    add_provenance_issues(issues, project_id, required_commands=["generate-facts", "generate-business-lite"])
    checked_files = [
        f"projects/{project_id}/workspace/facts.md",
        f"projects/{project_id}/workspace/business_blueprint_lite.md",
        f"projects/{project_id}/runtime/uxb_route_decision.json",
        f"projects/{project_id}/runtime/provenance.json",
    ]
    _add_execution_mode_info(project_id, issues, {"standard"})

    facts_text = read_text(workspace_dir / "facts.md")
    business_lite_text = read_text(workspace_dir / "business_blueprint_lite.md")
    if not facts_text:
        add_issue(issues, "blocker", "缺少 facts.md")
    if not business_lite_text:
        add_issue(issues, "blocker", "缺少 business_blueprint_lite.md")

    if business_lite_text:
        check_required_headings("business_blueprint_lite.md", business_lite_text, issues)
        check_forbidden_terms("business_blueprint_lite.md", business_lite_text, issues)
        check_placeholders("business_blueprint_lite.md", business_lite_text, issues)
        check_runtime_leakage_guard("business_blueprint_lite.md", business_lite_text, issues)
        for heading in ["## 2. 关键业务规则", "## 3. 边界与风险", "## 4. 体验承接要求"]:
            if len(_section_text(business_lite_text, heading)) < 20:
                add_issue(issues, "blocker", f"business_blueprint_lite.md 内容不足：{heading}")

    blockers, warnings, infos, _ = summarize_issues(issues)
    metrics = {"artifact": "business_blueprint_lite.md"}
    report_path, status_path, status = write_gate_artifacts(
        project_id,
        "business_lite",
        "experience",
        blockers,
        warnings,
        infos,
        checked_files,
        metrics,
    )
    print(f"Business lite gate finished: {report_path}")
    print(f"Business lite gate status: {status_path}")
    append_command_if_provenance_exists(project_id, "gate-business-lite")
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


def run_experience_lite_gate(project_id: str) -> int:
    workspace_dir = get_workspace_dir(project_id)
    issues: list[tuple[str, str]] = []
    checked_files = [
        f"projects/{project_id}/workspace/facts.md",
        f"projects/{project_id}/workspace/business_note.md",
        f"projects/{project_id}/workspace/business_blueprint_lite.md",
        f"projects/{project_id}/workspace/experience_blueprint.md",
        f"projects/{project_id}/runtime/provenance.json",
    ]
    add_provenance_issues(issues, project_id, required_commands=["generate-facts", "generate-experience"])

    facts_text = read_text(workspace_dir / "facts.md")
    business_note_text = read_text(workspace_dir / "business_note.md")
    business_lite_text = read_text(workspace_dir / "business_blueprint_lite.md")
    business_context = business_lite_text or business_note_text
    experience_text = read_text(workspace_dir / "experience_blueprint.md")

    if not facts_text:
        add_issue(issues, "blocker", "缺少 facts.md")
    if not business_context:
        add_issue(issues, "blocker", "缺少 business_note.md 或 business_blueprint_lite.md")
    if not experience_text:
        add_issue(issues, "blocker", "缺少 experience_blueprint.md")

    if business_note_text and not business_lite_text:
        business_note_gate = read_gate_status(project_id, "business_note")
        if not business_note_gate:
            add_issue(issues, "blocker", "缺少 business_note gate 状态，请先运行 gate-business-note")
        elif business_note_gate.get("status") == "failed":
            add_issue(issues, "blocker", "business_note 阶段未通过，不能进入体验蓝图阶段")
    if business_lite_text:
        business_lite_gate = read_gate_status(project_id, "business_lite")
        if not business_lite_gate:
            add_issue(issues, "blocker", "缺少 business_lite gate 状态，请先运行 gate-business-lite")
        elif business_lite_gate.get("status") == "failed":
            add_issue(issues, "blocker", "business_lite 阶段未通过，不能进入体验蓝图阶段")

    if experience_text:
        check_required_headings("experience_blueprint.md", experience_text, issues)
        check_forbidden_terms("experience_blueprint.md", experience_text, issues)
        check_placeholders("experience_blueprint.md", experience_text, issues)
        check_runtime_leakage_guard("experience_blueprint.md", experience_text, issues)
        if business_context:
            metrics, experience_depth_issues = analyze_experience_blueprint(facts_text, business_context, experience_text)
            extend_issues(issues, experience_depth_issues)
        else:
            metrics = {}
    else:
        metrics = {}

    blockers, warnings, infos, _ = summarize_issues(issues)
    report_path, status_path, status = write_gate_artifacts(
        project_id,
        "experience_lite",
        "final-validate",
        blockers,
        warnings,
        infos,
        checked_files,
        metrics,
    )
    print(f"Experience lite gate finished: {report_path}")
    print(f"Experience lite gate status: {status_path}")
    append_command_if_provenance_exists(project_id, "gate-experience-lite")
    if status == "failed":
        _print_repair_guidance(project_id)
    return 0 if status != "failed" else 1


def run_validate_lite(project_id: str) -> int:
    workspace_dir = get_workspace_dir(project_id)
    runtime_dir = get_project_runtime_dir(project_id)
    report_path = workspace_dir / "check_report.md"
    status_path = workspace_dir / "check_status.json"
    issues: list[tuple[str, str]] = []
    checked_files = [
        f"projects/{project_id}/runtime/uxb_route_decision.json",
        f"projects/{project_id}/workspace/facts.md",
        f"projects/{project_id}/workspace/business_note.md",
        f"projects/{project_id}/workspace/business_blueprint_lite.md",
        f"projects/{project_id}/workspace/experience_blueprint.md",
    ]

    decision = _read_execution_decision(project_id)
    execution_mode = str(decision.get("execution_mode") or "")
    if str(decision.get("status") or "") != "confirmed":
        details = "; ".join(str(item) for item in decision.get("validation_errors", []) if str(item).strip())
        add_issue(issues, "blocker", f"UXB 执行判断未确认：{details or '请先检查 runtime/uxb_route_decision.json'}")

    facts_text = read_text(workspace_dir / "facts.md")
    business_note_text = read_text(workspace_dir / "business_note.md")
    business_lite_text = read_text(workspace_dir / "business_blueprint_lite.md")
    experience_text = read_text(workspace_dir / "experience_blueprint.md")

    if not facts_text:
        add_issue(issues, "blocker", "缺少 facts.md")
    if execution_mode == "fast" and not business_note_text:
        add_issue(issues, "blocker", "当前执行要求 business_note.md，但文件缺失")
    if execution_mode == "standard" and not business_lite_text:
        add_issue(issues, "blocker", "当前执行要求 business_blueprint_lite.md，但文件缺失")
    if not experience_text:
        add_issue(issues, "blocker", "缺少 experience_blueprint.md")

    for file_name, content in [
        ("business_note.md", business_note_text),
        ("business_blueprint_lite.md", business_lite_text),
        ("experience_blueprint.md", experience_text),
    ]:
        if not content:
            continue
        check_required_headings(file_name, content, issues)
        check_forbidden_terms(file_name, content, issues)
        check_placeholders(file_name, content, issues)
        check_runtime_leakage_guard(file_name, content, issues)

    if execution_mode == "fast":
        gate_stage = "business_note"
    elif execution_mode == "standard":
        gate_stage = "business_lite"
    else:
        gate_stage = "business_note" if business_note_text else "business_lite" if business_lite_text else ""
    for stage in [gate_stage, "experience_lite"]:
        if not stage:
            continue
        gate_status = read_gate_status(project_id, stage)
        checked_files.append(f"projects/{project_id}/runtime/gates/{stage}_gate_status.json")
        if not gate_status:
            add_issue(issues, "blocker", f"缺少 {stage} gate 状态文件")
        elif gate_status.get("status") == "failed":
            add_issue(issues, "blocker", f"{stage} gate 状态为 failed")
        elif gate_status.get("status") == "warning":
            add_issue(issues, "warning", f"{stage} gate 状态为 warning")
        else:
            add_issue(issues, "info", f"{stage} gate 状态：{gate_status.get('status')}")

    blockers, warnings, infos, status = summarize_issues(issues)
    output_status_lines = [
        f"projects/{project_id}/workspace/facts.md: {'present' if facts_text else 'missing'}",
        f"projects/{project_id}/workspace/business_note.md: {'present' if business_note_text else 'missing'}",
        f"projects/{project_id}/workspace/business_blueprint_lite.md: {'present' if business_lite_text else 'missing'}",
        f"projects/{project_id}/workspace/experience_blueprint.md: {'present' if experience_text else 'missing'}",
    ]
    report_path.write_text(render_final_report(project_id, status, blockers, warnings, infos, output_status_lines, ["validate-lite"]), encoding="utf-8")
    completed_outputs = [line.split(": ", 1)[0] for line in output_status_lines if line.endswith("present")]
    missing_outputs = [line.split(": ", 1)[0] for line in output_status_lines if line.endswith("missing")]
    payload = build_final_payload(
        project_id,
        blockers,
        warnings,
        infos,
        completed_outputs,
        missing_outputs,
        checked_files,
        {"execution_mode": execution_mode, "validation_mode": "lite"},
    )
    status_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Validate lite finished: {report_path}")
    print(f"Machine status written: {status_path}")
    append_command_if_provenance_exists(project_id, "validate-lite")
    if status == "failed":
        _print_repair_guidance(project_id)
    return 0 if status != "failed" else 1


def run_coverage_lite(project_id: str) -> int:
    workspace_dir = get_workspace_dir(project_id)
    report_path = workspace_dir / "check_report.md"
    status_path = workspace_dir / "check_status.json"

    status_data = read_json(status_path)
    if not status_data:
        raise SystemExit(f"Missing machine status: {status_path}")

    business_text = read_text(workspace_dir / "business_blueprint_lite.md") or read_text(workspace_dir / "business_note.md")
    experience_text = read_text(workspace_dir / "experience_blueprint.md")
    blockers = list(status_data.get("issues", {}).get("blockers", []))
    warnings = list(status_data.get("issues", {}).get("warnings", []))
    infos = list(status_data.get("issues", {}).get("infos", []))
    coverage_lines: list[str] = []

    if not business_text:
        blockers.append("coverage-lite: 缺少轻量业务产物")
    if not experience_text:
        blockers.append("coverage-lite: 缺少 experience_blueprint.md")
    if business_text and experience_text:
        required_signals = ["规则", "边界", "风险", "状态", "异常", "文案"]
        covered = [item for item in required_signals if item in business_text and item in experience_text]
        missing = [item for item in required_signals if item in business_text and item not in experience_text]
        coverage_lines.append(f"covered_signals={len(covered)} missing_signals={len(missing)}")
        for item in missing:
            warnings.append(f"coverage-lite: experience 未明显承接轻量业务产物中的维度：{item}")

    blockers = sorted(set(str(item) for item in blockers))
    warnings = sorted(set(str(item) for item in warnings))
    infos = sorted(set(str(item) for item in infos + [f"轻量承接检查：{line}" for line in coverage_lines]))
    status = "passed"
    if blockers:
        status = "failed"
    elif warnings:
        status = "warning"

    output_status_lines = [line[2:] if line.startswith("- ") else line for line in re.findall(r"^- .+: (?:present|missing)$", read_text(report_path), flags=re.MULTILINE)]
    report_path.write_text(render_final_report(project_id, status, blockers, warnings, infos, output_status_lines, coverage_lines), encoding="utf-8")
    status_data["status"] = status
    status_data["has_blocker"] = bool(blockers)
    status_data["blocker_count"] = len(blockers)
    status_data["warning_count"] = len(warnings)
    status_data["info_count"] = len(infos)
    status_data.setdefault("issues", {})
    status_data["issues"]["blockers"] = blockers
    status_data["issues"]["warnings"] = warnings
    status_data["issues"]["infos"] = infos
    status_data["generated_by"] = "packages.validate"
    status_data["updated_at"] = now_iso()
    status_data["metrics"] = status_data.get("metrics", {})
    status_data["metrics"]["coverage_lite"] = {"lines": coverage_lines}
    checked_files = [str(item) for item in status_data.get("checked_files", []) if isinstance(item, str)]
    status_data["issue_details"] = build_issue_details(project_id, "final", blockers, warnings, infos, checked_files, status_data["metrics"])
    status_path.write_text(json.dumps(status_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Coverage lite finished: {report_path}")
    print(f"Machine status updated: {status_path}")
    append_command_if_provenance_exists(project_id, "coverage-lite")
    if status == "failed":
        _print_repair_guidance(project_id)
    return 0 if status != "failed" else 1
