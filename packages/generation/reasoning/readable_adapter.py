from __future__ import annotations

import re
from dataclasses import dataclass, field

from .schemas import ExperienceModel, ExperienceRiskEntry, PageBlueprint, PageEntry, StateFeedbackEntry, TaskFlowEntry

_ID_PATTERN = re.compile(r"\b(?:EV|P|TF|TR|PR|J|POS|F)-\d+\b", re.IGNORECASE)
_PLACEHOLDER_PATTERN = re.compile(r"^(?:状态\d+|异常场景\d+|待补充|失败)$")
_SOURCE_PATH_PATTERN = re.compile(r"(?:source[_ ]?path|[^\s]{0,20}文档\s*/\s*\d+(?:\.\d+)*(?:\s*/\s*EV-\d+)?)", re.IGNORECASE)


@dataclass(slots=True)
class ReadableExperienceSections:
    users_and_tasks: list[str] = field(default_factory=list)
    page_groups: list[str] = field(default_factory=list)
    flow_summary: list[str] = field(default_factory=list)
    key_page_summaries: list[str] = field(default_factory=list)
    state_summaries: list[str] = field(default_factory=list)
    copy_summaries: list[str] = field(default_factory=list)
    risk_summaries: list[str] = field(default_factory=list)


def clean_machine_trace(text: str) -> str:
    if not text:
        return ""
    cleaned = _ID_PATTERN.sub("", text)
    cleaned = _SOURCE_PATH_PATTERN.sub("", cleaned)
    cleaned = cleaned.replace("从当前输入直接抽取", "")
    cleaned = cleaned.replace("未做模板补全", "")
    cleaned = cleaned.replace("承接 TF-", "承接流程")
    cleaned = re.sub(r"\s*/\s*\d+(?:\.\d+)*(?:\s*/\s*[^,\n;；]+)?", "", cleaned)
    cleaned = re.sub(r"状态\d+", "未命名状态", cleaned)
    cleaned = re.sub(r"异常场景\d+", "未命名异常场景", cleaned)
    cleaned = cleaned.replace("如果不解释 失败", "如果不解释当前失败原因")
    cleaned = cleaned.replace("如果不解释 未命名异常场景", "如果不解释当前异常场景")
    cleaned = cleaned.replace("权限需求文档", "")
    cleaned = cleaned.replace("产品方案说明", "")
    cleaned = cleaned.replace("需求结构化说明", "")
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" ，,;；:：")
    return cleaned or "待补充说明"


def is_placeholder_text(text: str) -> bool:
    normalized = clean_machine_trace(text)
    if not normalized:
        return True
    if _PLACEHOLDER_PATTERN.match(normalized):
        return True
    return normalized in {"状态", "异常", "结果", "处理中", "失败"}


def _semantic_key(text: str) -> str:
    normalized = clean_machine_trace(text)
    normalized = re.sub(r"[^\w\u4e00-\u9fff]", "", normalized.lower())
    return normalized


def dedupe_by_semantic_key(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        key = _semantic_key(item)
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def build_task_group_label(text: str) -> str:
    content = clean_machine_trace(text)
    if "配置" in content or "设置" in content:
        return "配置与规则设定"
    if "申请" in content or "提交" in content:
        return "提交与发起"
    if "审批" in content or "处理" in content:
        return "处理与审批"
    if "查询" in content or "查看" in content or "结果" in content:
        return "查询与结果理解"
    if "帮助" in content or "说明" in content:
        return "解释与帮助"
    return "主任务执行"


def build_readable_page_name(page: PageEntry) -> str:
    user = clean_machine_trace(page.target_user) or "用户"
    if len(user) > 16:
        user = user[:16].rstrip("，,。") + "等角色"
    task = clean_machine_trace(page.primary_task) or clean_machine_trace(page.name)
    page_type = "页面"
    for token, mapped in [("设置", "设置页"), ("申请", "申请页"), ("结果", "结果页"), ("详情", "详情页"), ("帮助", "说明区")]:
        if token in task or token in page.name:
            page_type = mapped
            break
    return f"{user}的{task}{page_type}"


def _clean_flow_steps(raw_steps: str) -> str:
    parts = [part.strip() for part in raw_steps.split("->")]
    kept: list[str] = []
    for part in parts:
        cleaned = clean_machine_trace(part)
        if not cleaned or "文档" in part:
            continue
        if cleaned in {"需求概述", "调研", "竞品分析"}:
            continue
        kept.append(cleaned)
    return " -> ".join(kept[:4]) or "进入主流程并执行关键步骤"


def build_readable_flow_sentence(flow: TaskFlowEntry) -> str:
    actor = clean_machine_trace(flow.start) or "用户"
    action = clean_machine_trace(flow.name) or "执行主任务"
    key_steps = _clean_flow_steps(flow.key_steps)
    success = clean_machine_trace(flow.success_result) or "看到成功结果和下一步"
    failure = clean_machine_trace(flow.failure_result) or "看到失败原因和处理方式"
    return f"{actor}发起“{action}”，系统按“{key_steps}”推进；成功后{success}，失败时{failure}。"


def build_readable_state_sentence(state: StateFeedbackEntry) -> str:
    state_name = clean_machine_trace(state.name)
    if is_placeholder_text(state_name):
        state_name = "未命名状态（需要补充说明）"
    trigger = clean_machine_trace(state.trigger) or "触发条件待补充"
    actions = clean_machine_trace(state.available_actions) or "可执行动作待补充"
    feedback = clean_machine_trace(state.page_feedback) or clean_machine_trace(state.copy_feedback) or "反馈说明待补充"
    downstream = clean_machine_trace(state.downstream) or "下一步待补充"
    return f"当进入“{state_name}”时（触发：{trigger}），用户可执行{actions}；系统需要说明{feedback}，并明确下一步是{downstream}。"


def build_readable_risk_sentence(risk: ExperienceRiskEntry) -> str:
    name = clean_machine_trace(risk.name)
    if is_placeholder_text(name):
        name = "关键异常风险"
    trigger = clean_machine_trace(risk.trigger)
    confusion = clean_machine_trace(risk.confusion)
    protection = clean_machine_trace(risk.protection)
    if is_placeholder_text(confusion):
        confusion = "用户无法判断当前状态和可操作动作"
    if not protection or protection.replace("/", "").strip() in {"中显式提供阻断解释处理方向与来源追踪入口", "在中显式提供阻断解释处理方向与来源追踪入口"}:
        protection = "关键页面中显式提供阻断解释、处理方向与来源追踪入口"
    return f"风险“{name}”常在“{trigger}”出现，用户会因为“{confusion}”产生疑惑；系统需通过“{protection}”做保护。"


def _build_key_page_summary(page: PageBlueprint) -> str:
    title = clean_machine_trace(page.name)
    if is_placeholder_text(title):
        title = "关键页面（需补充命名）"
    task = clean_machine_trace(page.primary_task)
    entry = clean_machine_trace(page.entry_condition)
    focus = clean_machine_trace(page.first_screen_focus)
    action_text = "、".join(clean_machine_trace(item) for item in page.key_actions if clean_machine_trace(item))
    risk_parts: list[str] = []
    for item in page.risks:
        cleaned = clean_machine_trace(item)
        if not cleaned:
            continue
        if is_placeholder_text(cleaned):
            cleaned = "关键异常风险（需补充命名）"
        risk_parts.append(cleaned)
    risk_text = "、".join(dedupe_by_semantic_key(risk_parts))
    return (
        f"### {title}\n"
        f"- 页面任务：{task}\n"
        f"- 进入条件：{entry}\n"
        f"- 首屏重点：{focus}\n"
        f"- 关键动作：{action_text or '待补充'}\n"
        f"- 需解释的风险：{risk_text or '待补充'}"
    )


def build_experience_readable_sections(model: ExperienceModel) -> ReadableExperienceSections:
    users_and_tasks = dedupe_by_semantic_key(
        [
            f"目标用户：{clean_machine_trace(model.target_users)}",
            f"核心目标：{clean_machine_trace(model.experience_goal)}",
            f"任务边界：{clean_machine_trace(model.task_boundary)}",
            f"本轮不展开：{clean_machine_trace(model.excluded_scope)}",
        ]
    )

    page_groups = dedupe_by_semantic_key(
        [
            f"{build_task_group_label(page.primary_task)}：{build_readable_page_name(page)}（入口：{clean_machine_trace(page.entry)}）"
            for page in model.pages[:8]
        ]
    )

    flow_summary = dedupe_by_semantic_key([build_readable_flow_sentence(flow) for flow in model.task_flows[:8]])
    key_page_summaries = [_build_key_page_summary(page) for page in model.key_pages[:6]]
    state_summaries = dedupe_by_semantic_key([build_readable_state_sentence(state) for state in model.state_feedbacks[:8]])

    copy_summaries = dedupe_by_semantic_key(
        [
            (
                f"在“{clean_machine_trace(copy.scenario)}”场景，文案要解释"
                f"“{clean_machine_trace(copy.semantic_goal)}”，并包含“{clean_machine_trace(copy.required_info)}”。"
            )
            for copy in model.copy_contracts[:8]
        ]
    )

    risk_summaries = dedupe_by_semantic_key([build_readable_risk_sentence(risk) for risk in model.risks[:8]])

    return ReadableExperienceSections(
        users_and_tasks=users_and_tasks,
        page_groups=page_groups,
        flow_summary=flow_summary,
        key_page_summaries=key_page_summaries,
        state_summaries=state_summaries,
        copy_summaries=copy_summaries,
        risk_summaries=risk_summaries,
    )
