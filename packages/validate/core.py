from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from packages.common import (
    get_project_gates_dir,
    get_project_runtime_dir,
    get_project_source_dir,
    get_project_workspace_dir,
    get_repo_root,
)
from packages.provenance import append_command_if_provenance_exists, validate_provenance


STAGE_REQUIRED_HEADINGS = {
    "facts.md": [
        "## 任务意图",
        "## 事实来源说明",
        "## 术语与对象边界",
        "## 角色与对象清单",
        "## 原子事实清单",
        "## 规则矩阵",
        "## 状态模型",
        "## 动作与流程事实",
        "## 异常与拦截清单",
        "## 依赖清单",
        "## 范围与非范围",
        "## 开放问题与缺口",
        "## 追踪映射",
    ],
    "business_blueprint.md": [
        "## 1. 一句话结论",
        "## 2. 为什么要做",
        "## 3. 值不值得做",
        "## 4. 怎么做更合理",
        "## 5. 哪些不能随便做",
        "## 6. 主要风险",
        "## 7. 体验设计要注意什么",
        "## 附录 A：事实承接",
        "## 附录 B：命中知识与来源",
        "## 附录 C：备选方案比较",
        "## 附录 D：判断追踪映射",
        "## 附录 E：链路自检信息",
    ],
    "experience_blueprint.md": [
        "## 1. 交互流程总览",
        "## 2. 主交互流程",
        "## 3. 次交互流程",
        "## 4. 异常与阻断流程",
        "## 5. 页面 / 弹窗 / 抽屉设计",
        "## 6. 状态与反馈文案",
        "## 附录 A：上游依据",
        "## 附录 B：原始信息架构与页面清单",
        "## 附录 C：页面 / 流程追踪映射",
        "## 附录 D：设计原则引用",
        "## 附录 E：原始状态 / 文案 / 风险矩阵",
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
        "## 阶段定位",
        "## 体验范围与边界",
        "## 用户与场景清单",
        "## 信息架构",
        "## 核心任务流",
        "## 页面蓝图",
        "## 风险场景与体验保护",
        "## 原则引用与映射",
        "## 开放问题",
        "## 不进入本阶段的内容",
        "## 体验要求",
    ],
}
FORBIDDEN_TERM_ALLOWED_SECTIONS = {
    "facts.md": {"任务意图", "事实来源说明", "范围与非范围", "已知约束", "开放问题与缺口"},
    "business_blueprint.md": {"附录 E：链路自检信息"},
    "experience_blueprint.md": {"1. 交互流程总览", "2. 主交互流程", "附录 E：原始状态 / 文案 / 风险矩阵"},
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
    "术语与对象边界",
    "角色与对象清单",
    "原子事实清单",
    "规则矩阵",
    "状态模型",
    "动作与流程事实",
    "异常与拦截清单",
    "依赖清单",
    "追踪映射",
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

FACT_ID_PATTERN = re.compile(r"\bF-[A-Z]{0,4}\d+\b|\bF-\d+\b")
JUDGMENT_ID_PATTERN = re.compile(r"\bJ-\d+\b|\bPOS-\d+\b")
PAGE_ID_PATTERN = re.compile(r"\bP-\d+\b")
FLOW_ID_PATTERN = re.compile(r"\bTF-\d+\b")
GENERIC_ID_PATTERN = re.compile(r"\b[A-Z]{1,8}-\d+\b")
OPTION_ID_PATTERN = re.compile(r"\bOPT?-\d+\b")
RISK_ID_PATTERN = re.compile(r"\b(?:RSK|RK|AP)-\d+\b")
TRACE_ID_PATTERN = re.compile(r"\bTR-\d+\b")
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
    (re.compile(r"\b(?:P|TF|TR)-\d+\b", re.IGNORECASE), "核心区包含 P/TF/TR 编号"),
    (re.compile(r"source[_ ]?path", re.IGNORECASE), "核心区包含 source_path"),
    (re.compile(r"(?:从当前输入直接抽取|未做模板补全)"), "核心区暴露了生成过程提示语"),
    (re.compile(r"(?:状态\d+|异常场景\d+)"), "核心区包含占位词（状态2/异常场景3）"),
    (re.compile(r"(?:未命名状态|未命名异常场景)"), "核心区包含未命名占位词"),
    (re.compile(r"(?:配置\s+配置|查看\s+查看|提交\s+提交|申请\s+申请|审批\s+审批|关闭\s+关闭)"), "核心区存在重复动词表达"),
    (re.compile(r"[\u4e00-\u9fff]{20,}(?:管理员|审批人|申请人|负责人|运营人员|财务|人事|用户|客户|成员|子管理员|超管|员工)"), "核心区存在过长角色句"),
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
            "存在未被体验层消费的业务判断",
            "存在未被后续消费的事实",
            "未发现页面 ID",
        )
        if message.lower().startswith("coverage:") or any(marker in message for marker in coverage_warning_markers):
            return "coverage"
        return "validate"
    return f"{default_stage}_gate"


def infer_issue_category(stage: str, message: str) -> str:
    lowered = message.lower()
    if "缺少栏目" in message or "缺少必需章节" in message or ("缺少" in message and "## " in message):
        return "structure_missing"
    if "缺少追踪映射" in message or "不可追溯" in message or "追踪映射" in message:
        return "trace_missing"
    if "placeholder" in lowered or "占位" in message:
        return "placeholder_residue"
    if "未被" in message or lowered.startswith("coverage:") or "覆盖检查" in message:
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
    return sorted(set(FACT_ID_PATTERN.findall(text)))


def extract_judgment_ids(text: str) -> list[str]:
    return sorted(set(JUDGMENT_ID_PATTERN.findall(text)))


def has_experience_critical_signal(text: str) -> bool:
    if not text:
        return False
    return any(item in text for item in EXPERIENCE_CRITICAL_HINTS)


def find_critical_judgment_ids(business_text: str, judgment_ids: list[str]) -> list[str]:
    critical: list[str] = []
    for judgment_id in judgment_ids:
        for match in re.finditer(re.escape(judgment_id), business_text):
            start = max(0, match.start() - 160)
            end = min(len(business_text), match.end() + 160)
            snippet = business_text[start:end]
            if has_experience_critical_signal(snippet):
                critical.append(judgment_id)
                break
    return sorted(set(critical))


def extract_page_ids(text: str) -> list[str]:
    return sorted(set(PAGE_ID_PATTERN.findall(text)))


def extract_flow_ids(text: str) -> list[str]:
    return sorted(set(FLOW_ID_PATTERN.findall(text)))


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
    lines = ["# Check Report", "", *report_summary_lines(status, blockers, warnings, infos), "## Output Status", ""]
    lines.extend([f"- {item}" for item in output_status_lines] or ["- none"])
    lines.extend(["", "## Blockers", ""])
    lines.extend([f"- {item}" for item in blockers] or ["- none"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {item}" for item in warnings] or ["- none"])
    lines.extend(["", "## Infos", ""])
    lines.extend([f"- {item}" for item in infos] or ["- none"])
    lines.extend(["", "## Coverage Check", ""])
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
        "actor": ["### Actor Facts", "角色清单"],
        "object": ["### Object Facts", "对象清单"],
        "state": ["### State Facts", "## 状态模型"],
        "action": ["### Action Facts", "## 动作与流程事实"],
        "rule": ["### Rule Facts", "## 规则矩阵"],
        "exception": ["### Exception Facts", "## 异常与拦截清单"],
        "dependency": ["### Dependency Facts", "## 依赖清单"],
        "scope": ["### Scope Facts", "## 范围与非范围"],
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
    fact_ids = extract_fact_ids(facts_text)
    judgment_ids = extract_judgment_ids(business_text)
    referenced_facts = [fact_id for fact_id in fact_ids if fact_id in business_text]

    stance_section = sections.get("1. 一句话结论", "")
    value_section = sections.get("3. 值不值得做", "")
    option_section = "\n".join([sections.get("4. 怎么做更合理", ""), sections.get("附录 C：备选方案比较", "")])
    risk_section = sections.get("6. 主要风险", "")
    trace_section = sections.get("附录 D：判断追踪映射", "")
    appendix_e_section = sections.get("附录 E：链路自检信息", "")

    judgment_count = len(judgment_ids)
    option_compare_count = max(count_unique_matches(OPTION_ID_PATTERN, option_section), count_real_table_rows(option_section), count_real_list_items(option_section))
    value_assessment_item_count = max(count_real_table_rows(value_section), count_real_list_items(value_section))
    risk_item_count = max(count_unique_matches(RISK_ID_PATTERN, risk_section), count_real_table_rows(risk_section), count_real_list_items(risk_section))
    judgment_traceable_count = len(sorted(set(JUDGMENT_ID_PATTERN.findall(trace_section))))
    trace_mapping_item_count = max(judgment_traceable_count, count_real_table_rows(trace_section), count_real_list_items(trace_section))
    unresolved_gap_count = business_text.count("GAP-") + business_text.count("OQ-")
    has_appendix_e = bool(appendix_e_section.strip())

    if not judgment_ids:
        add_issue(issues, "blocker", "business_blueprint.md 未形成显式业务判断编号（J-xx / POS-xx）")
    elif judgment_count < 3:
        add_issue(issues, "warning", "business_blueprint.md 业务判断数量偏少，review 深度可能不足")

    if not fact_ids:
        add_issue(issues, "blocker", "facts.md 中没有可承接的事实 ID")
    elif not referenced_facts:
        add_issue(issues, "blocker", "business_blueprint.md 未承接任何 facts ID")
    else:
        add_issue(issues, "info", f"business_blueprint.md 已承接 {len(referenced_facts)} 条事实")
        if len(referenced_facts) < max(1, len(fact_ids) // 5):
            add_issue(issues, "warning", "business_blueprint.md 对 facts 的显式承接偏弱")

    if option_compare_count == 0:
        add_issue(issues, "blocker", "business_blueprint.md 缺少显式备选路径比较")
    elif option_compare_count < 2:
        add_issue(issues, "warning", "business_blueprint.md 备选路径比较仍偏少，建议至少保留两个以上可比方案")

    if value_assessment_item_count == 0 or count_keywords_present(value_section, ["价值", "成本", "认知"]) < 2:
        add_issue(issues, "blocker", "business_blueprint.md 缺少价值 / 成本 / 认知负担评估")

    if risk_item_count == 0:
        add_issue(issues, "blocker", "business_blueprint.md 缺少风险与反模式单列")

    if not trace_section.strip():
        add_issue(issues, "warning", "business_blueprint.md 缺少有效的判断追踪映射内容")
    elif judgment_traceable_count == 0:
        add_issue(issues, "warning", "business_blueprint.md 判断追踪映射未真正追到 J-xx / POS-xx")

    if not stance_section.strip():
        add_issue(issues, "blocker", "business_blueprint.md 缺少最终业务立场内容")

    if unresolved_gap_count == 0:
        add_issue(issues, "warning", "business_blueprint.md 未显式保留开放问题或缺口")
    if not has_appendix_e:
        add_issue(issues, "warning", "business_blueprint.md 缺少附录 E（链路自检信息）")

    metrics = {
        "judgment_count": judgment_count,
        "facts_consumed_count": len(referenced_facts),
        "judgment_traceable_count": judgment_traceable_count,
        "trace_mapping_item_count": trace_mapping_item_count,
        "option_compare_count": option_compare_count,
        "value_assessment_item_count": value_assessment_item_count,
        "risk_item_count": risk_item_count,
        "unresolved_gap_count": unresolved_gap_count,
        "has_appendix_e": has_appendix_e,
    }
    return metrics, issues


def analyze_experience_blueprint(
    facts_text: str,
    business_text: str,
    experience_text: str,
) -> tuple[dict[str, object], list[tuple[str, str]]]:
    issues: list[tuple[str, str]] = []
    sections = parse_h2_sections(experience_text)
    fact_ids = extract_fact_ids(facts_text)
    judgment_ids = extract_judgment_ids(business_text)
    page_ids = extract_page_ids(experience_text)
    flow_ids = extract_flow_ids(experience_text)

    overview_section = sections.get("1. 交互流程总览", "")
    main_flow_section = sections.get("2. 主交互流程", "")
    secondary_flow_section = sections.get("3. 次交互流程", "")
    exception_flow_section = sections.get("4. 异常与阻断流程", "")
    page_design_section = sections.get("5. 页面 / 弹窗 / 抽屉设计", "")
    state_copy_section = sections.get("6. 状态与反馈文案", "")
    appendix_b_section = sections.get("附录 B：原始信息架构与页面清单", "")
    appendix_e_section = sections.get("附录 E：原始状态 / 文案 / 风险矩阵", "")
    flow_section = "\n".join([main_flow_section, secondary_flow_section, sections.get("附录 C：页面 / 流程追踪映射", "")])
    page_inventory_section = "\n".join([page_design_section, appendix_b_section])
    key_page_section = page_design_section
    layout_section = appendix_b_section
    content_contract_section = appendix_b_section
    state_section = "\n".join([state_copy_section, appendix_e_section])
    copy_section = "\n".join([state_copy_section, appendix_e_section])
    risk_section = "\n".join([exception_flow_section, appendix_e_section])
    trace_section = sections.get("附录 C：页面 / 流程追踪映射", "")
    core_text = get_experience_core_text(sections)

    flow_count = max(len(flow_ids), count_real_table_rows(flow_section), count_real_list_items(flow_section))
    page_inventory_item_count = max(count_real_table_rows(page_inventory_section), count_real_list_items(page_inventory_section))
    expanded_page_blueprint_count = max(
        count_expanded_page_blueprints(key_page_section),
        len(re.findall(r"^###\s+", key_page_section, re.MULTILINE)),
    )
    region_map_count = count_text_diagrams(layout_section)
    content_contract_item_count = max(count_real_table_rows(content_contract_section), count_real_list_items(content_contract_section))
    state_feedback_pair_count = max(count_real_table_rows(state_section), count_real_list_items(state_section))
    copy_contract_item_count = max(count_real_table_rows(copy_section), count_real_list_items(copy_section))
    trace_mapping_item_count = max(
        count_unique_matches(TRACE_ID_PATTERN, trace_section),
        count_real_table_rows(trace_section),
        count_real_list_items(trace_section),
    )
    referenced_facts = [item for item in fact_ids if item in experience_text]
    referenced_judgments = [item for item in judgment_ids if item in experience_text]
    principle_refs = extract_principle_refs(experience_text, fact_ids, judgment_ids, page_ids, flow_ids)
    principle_ref_count = len(principle_refs)

    exception_text = "\n".join([overview_section, main_flow_section, secondary_flow_section, exception_flow_section, state_section, risk_section])
    has_exception_coverage = contains_any(
        exception_text,
        ["失败", "阻断", "拦截", "拒绝", "异常", "不可", "空态", "冲突", "审批中", "处理中", "关闭失败"],
    )
    has_success_coverage = contains_any(exception_text, ["成功", "生效", "通过", "已开启", "完成", "可启用"])

    if not referenced_facts:
        add_issue(issues, "blocker", "experience_blueprint.md 未显式承接 facts ID")
    else:
        add_issue(issues, "info", f"experience_blueprint.md 已承接 {len(referenced_facts)} 条事实")

    if not referenced_judgments:
        add_issue(issues, "warning", "experience_blueprint.md 尚未显式承接业务判断 ID（J-xx / POS-xx）")
    else:
        add_issue(issues, "info", f"experience_blueprint.md 已承接 {len(referenced_judgments)} 条业务判断")

    if principle_ref_count == 0:
        add_issue(issues, "blocker", "experience_blueprint.md 未显式引用设计原则")
    else:
        add_issue(issues, "info", f"experience_blueprint.md 已引用 {principle_ref_count} 个设计原则 ID")

    if flow_count == 0:
        add_issue(issues, "blocker", "experience_blueprint.md 缺少交互流程说明")

    if page_inventory_item_count == 0 and not page_ids:
        add_issue(issues, "blocker", "experience_blueprint.md 缺少页面 / 弹窗 / 抽屉设计信息")

    if expanded_page_blueprint_count == 0:
        add_issue(issues, "blocker", "experience_blueprint.md 缺少页面 / 弹窗 / 抽屉展开说明")

    if region_map_count == 0:
        add_issue(issues, "blocker", "experience_blueprint.md 缺少附录中的区块布局示意")

    if content_contract_item_count == 0:
        add_issue(issues, "blocker", "experience_blueprint.md 缺少信息优先级合同")

    if state_feedback_pair_count == 0:
        add_issue(issues, "blocker", "experience_blueprint.md 缺少状态与异常处理信息")

    if copy_contract_item_count == 0:
        add_issue(issues, "blocker", "experience_blueprint.md 缺少文案解释要求")

    if trace_mapping_item_count == 0:
        add_issue(issues, "blocker", "experience_blueprint.md 缺少页面 / 流程追踪映射")

    if not has_exception_coverage:
        add_issue(issues, "blocker", "experience_blueprint.md 仅覆盖 happy path，未显式覆盖异常态 / 阻断态")
    elif not has_success_coverage:
        add_issue(issues, "warning", "experience_blueprint.md 异常态覆盖存在，但成功态 / 完成态表达仍偏弱")

    for pattern, message in EXPERIENCE_MACHINE_LINE_PATTERNS:
        if pattern.search(core_text):
            add_issue(issues, "warning", f"experience_blueprint.md {message}")

    core_table_count = count_real_table_rows(core_text)
    if core_table_count > 0:
        add_issue(issues, "warning", "experience_blueprint.md 核心区包含表格，建议改为节点化 Markdown 层级表达")

    repeated_page_names = find_repeated_page_names_in_core(sections.get("5. 页面 / 弹窗 / 抽屉设计", ""))
    if repeated_page_names:
        add_issue(issues, "warning", "experience_blueprint.md 核心区页面名重复较多，建议继续语义去重")

    metrics = {
        "flow_count": len(flow_ids),
        "page_count": len(page_ids),
        "page_inventory_item_count": page_inventory_item_count,
        "expanded_page_blueprint_count": expanded_page_blueprint_count,
        "region_map_count": region_map_count,
        "content_contract_item_count": content_contract_item_count,
        "state_feedback_pair_count": state_feedback_pair_count,
        "copy_contract_item_count": copy_contract_item_count,
        "trace_mapping_item_count": trace_mapping_item_count,
        "business_judgment_consumed_count": len(referenced_judgments),
        "principle_ref_count": principle_ref_count,
        "exception_coverage": has_exception_coverage,
        "core_table_count": core_table_count,
    }
    return metrics, issues


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

    if facts_text and business_text:
        business_metrics, business_depth_issues = analyze_business_blueprint(facts_text, business_text)
        extend_issues(issues, business_depth_issues)
        if int(business_metrics.get("judgment_traceable_count", 0)) == 0:
            add_issue(issues, "blocker", "final validate：business_blueprint.md 的判断追踪映射仍不足，不能视为稳定 business review")

    if facts_text and business_text and experience_text:
        experience_metrics, experience_depth_issues = analyze_experience_blueprint(facts_text, business_text, experience_text)
        extend_issues(issues, experience_depth_issues)

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
    coverage_lines = ["not_run"]
    report_text = render_final_report(project_id, status, blockers, warnings, infos, output_status_lines, coverage_lines)
    report_path.write_text(report_text, encoding="utf-8")

    metrics = {
        "required_output_count": len(required_outputs),
        "completed_output_count": len(completed_outputs),
        "missing_output_count": len(missing_outputs),
        "business_depth": business_metrics,
        "experience_depth": experience_metrics,
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

    fact_ids = extract_fact_ids(facts_text)
    judgment_ids = extract_judgment_ids(business_text)
    page_ids = extract_page_ids(experience_text)
    experience_sections = parse_h2_sections(experience_text)
    experience_trace_section = (
        experience_sections.get("附录 C：页面 / 流程追踪映射", "")
        or experience_sections.get("页面 / 流程追踪映射", "")
        or experience_sections.get("体验追踪映射", "")
    )

    facts_in_business = [item for item in fact_ids if item in business_text]
    facts_in_experience = [item for item in fact_ids if item in experience_text]
    orphan_facts = [item for item in fact_ids if item not in business_text and item not in experience_text]
    judgments_in_experience = [item for item in judgment_ids if item in experience_text]
    orphan_judgments = [item for item in judgment_ids if item not in experience_text]
    critical_judgments = find_critical_judgment_ids(business_text, judgment_ids)
    critical_judgments_in_trace = [item for item in critical_judgments if item in experience_trace_section]

    coverage_lines: list[str] = [
        f"facts_covered_by_business: {len(facts_in_business)}",
        f"facts_covered_by_experience: {len(facts_in_experience)}",
        f"business_judgments_consumed_by_experience: {len(judgments_in_experience)}",
        f"orphan_fact_count: {len(orphan_facts)}",
        f"orphan_judgment_count: {len(orphan_judgments)}",
        f"orphan_page_count: {0 if page_ids else 1}",
    ]

    blockers = list(status_data.get("issues", {}).get("blockers", []))
    warnings = list(status_data.get("issues", {}).get("warnings", []))
    infos = list(status_data.get("issues", {}).get("infos", []))

    if not fact_ids:
        blockers.append("facts.md 未提取到事实 ID，无法完成覆盖检查")
    if orphan_facts:
        warnings.append(f"存在未被后续消费的事实：{', '.join(orphan_facts[:6])}")
    if orphan_judgments:
        warnings.append(f"存在未被体验层消费的业务判断：{', '.join(orphan_judgments[:6])}")
    if critical_judgments and not critical_judgments_in_trace:
        warnings.append("experience 追踪映射未承接任何状态/异常/治理/依赖类业务判断，建议补充关键判断的页面/流程/状态/文案落点")
    if not page_ids:
        warnings.append("experience_blueprint.md 未发现页面 ID（P-xx），页面级消费不足")

    infos.extend([f"coverage: {line}" for line in coverage_lines])
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
    status_data["metrics"]["coverage"] = {
        "facts_covered_by_business": len(facts_in_business),
        "facts_covered_by_experience": len(facts_in_experience),
        "business_judgments_consumed_by_experience": len(judgments_in_experience),
        "orphan_fact_count": len(orphan_facts),
        "orphan_judgment_count": len(orphan_judgments),
        "critical_judgment_count": len(critical_judgments),
        "critical_judgment_traced_count": len(critical_judgments_in_trace),
        "orphan_page_count": 0 if page_ids else 1,
    }
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
    write_runtime_extension_artifacts(
        project_id,
        fact_ids,
        judgment_ids,
        page_ids,
        facts_in_business,
        facts_in_experience,
        judgments_in_experience,
    )
    print(f"Coverage check finished: {report_path}")
    print(f"Machine status updated: {status_path}")
    append_command_if_provenance_exists(project_id, "coverage")
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

        fact_ids = extract_fact_ids(facts_text)
        if not fact_ids:
            add_issue(issues, "blocker", "facts.md 未提取到原子事实 ID")
        else:
            add_issue(issues, "info", f"facts.md 已提炼 {len(fact_ids)} 条事实")

        dimension = compute_dimension_coverage(facts_text)
        covered_count = sum(dimension.values())
        if covered_count < 6:
            add_issue(issues, "blocker", "facts.md 结构化维度覆盖不足，无法稳定支撑业务判断")
        elif covered_count < 8:
            add_issue(issues, "warning", "facts.md 结构化维度覆盖仍偏粗")

        source_hits, knowledge_hits = evaluate_facts_source_legality(project_id, facts_text)
        if source_hits == 0:
            add_issue(issues, "blocker", "facts.md 未显式承接 requirement/background 输入来源")
        elif source_hits < 2:
            add_issue(issues, "warning", "facts.md 输入来源引用不完整")
        if knowledge_hits and source_hits == 0:
            add_issue(issues, "blocker", "facts.md 可能将知识补写为输入事实，请补充输入来源追溯")

        if "## 追踪映射" not in facts_text:
            add_issue(issues, "blocker", "facts.md 缺少追踪映射，关键事实不可追溯")
        if ("GAP-" not in facts_text) and ("[GAP]" not in facts_text) and ("## 开放问题与缺口" not in facts_text):
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
        "fact_count": len(extract_fact_ids(facts_text)),
        "dimension_coverage": compute_dimension_coverage(facts_text),
        "traceable_fact_count": len(extract_fact_ids(facts_text)) if "## 追踪映射" in facts_text else 0,
        "gap_count": facts_text.count("GAP-") + facts_text.count("[GAP]"),
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
    return 0 if status != "failed" else 1
