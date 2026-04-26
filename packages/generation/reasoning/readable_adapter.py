from __future__ import annotations

import re
from dataclasses import dataclass, field

from .schemas import ExperienceModel, ExperienceRiskEntry, PageBlueprint, PageEntry, StateFeedbackEntry, TaskFlowEntry

_ID_PATTERN = re.compile(r"\b(?:EV|P|TF|TR|PR|J|POS|F)-\d+\b", re.IGNORECASE)
_PLACEHOLDER_PATTERN = re.compile(r"^(?:状态\d+|异常场景\d+|待补充|失败)$")
_SOURCE_PATH_PATTERN = re.compile(r"(?:source[_ ]?path|[^\s]{0,20}文档\s*/\s*\d+(?:\.\d+)*(?:\s*/\s*EV-\d+)?)", re.IGNORECASE)
_ROLE_KEYWORDS = [
    "子管理员",
    "管理员",
    "审批人",
    "申请人",
    "负责人",
    "运营人员",
    "财务",
    "人事",
    "用户",
    "客户",
    "成员",
    "超管",
    "员工",
]
_ACTION_VERBS = ["配置", "查看", "提交", "申请", "审批", "关闭", "确认", "发起", "处理", "编辑"]
_CORE_PLACEHOLDER_TEXT = "还有部分状态或异常未明确命名，需要后续补充具体触发条件和提示文案。"


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
    cleaned = cleaned.replace("权限需求文档", "")
    cleaned = cleaned.replace("产品方案说明", "")
    cleaned = cleaned.replace("需求结构化说明", "")
    cleaned = cleaned.replace("M4_1", "")
    cleaned = cleaned.replace("E1([开始])", "开始")
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" ，,;；:：")
    return cleaned or "待补充说明"


def is_placeholder_text(text: str) -> bool:
    normalized = clean_machine_trace(text)
    if not normalized:
        return True
    if _PLACEHOLDER_PATTERN.match(normalized):
        return True
    if re.search(r"(?:未命名状态|未命名异常场景|状态\d+|异常场景\d+)", normalized):
        return True
    return normalized in {"状态", "异常", "结果", "处理中", "失败", "待补充", "待补充说明"}


def extract_readable_role(text: str) -> str:
    content = clean_machine_trace(text)
    if not content:
        return "用户"
    scoped_matches: list[str] = []
    for keyword in _ROLE_KEYWORDS:
        for marker in ("", "由", "为"):
            pattern = rf"(?:^|[，,。；;、\s]|{marker})([\u4e00-\u9fff]{{0,4}}{keyword})"
            scoped_matches.extend(match.group(1) for match in re.finditer(pattern, content) if match.group(1))
    if scoped_matches:
        scoped_matches = sorted(set(scoped_matches), key=lambda item: (0 if "管理员" in item else 1, len(item)))
        return scoped_matches[0].strip()
    for keyword in _ROLE_KEYWORDS:
        if keyword in content:
            return keyword
    return content[:10].rstrip("，,。；;：:")


def clean_duplicate_action(text: str) -> str:
    content = clean_machine_trace(text)
    if not content:
        return ""
    for verb in _ACTION_VERBS:
        content = content.replace(f"{verb} {verb}", verb)
        content = re.sub(rf"(?:^|\s){verb}\s+{verb}(?=[\u4e00-\u9fffA-Za-z0-9])", f" {verb}", content)
    content = re.sub(r"\s{2,}", " ", content).strip()
    return content


def shorten_readable_name(text: str, max_len: int = 24) -> str:
    content = clean_machine_trace(text)
    if len(content) <= max_len:
        return content
    page_suffix = ""
    for suffix in ["失败提示弹窗", "确认弹窗", "说明区", "结果页", "详情页", "记录页", "申请页", "设置页", "页面"]:
        if content.endswith(suffix) or suffix in content:
            page_suffix = suffix
            break
    keep_len = max(6, max_len - len(page_suffix))
    shortened = content[:keep_len].rstrip("，,。；;：:")
    return f"{shortened}{page_suffix}" if page_suffix else shortened


def hide_placeholder_in_core(text: str) -> str:
    content = clean_machine_trace(text)
    if not content:
        return _CORE_PLACEHOLDER_TEXT
    if is_placeholder_text(content):
        return _CORE_PLACEHOLDER_TEXT
    if re.search(r"(?:状态\d+|异常场景\d+|未命名状态|未命名异常场景|待补充|如果不解释\s*失败)", content):
        return _CORE_PLACEHOLDER_TEXT
    return content


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
    user = extract_readable_role(page.target_user) or "用户"
    task = clean_duplicate_action(page.primary_task) or clean_duplicate_action(page.name) or "执行任务"
    task = hide_placeholder_in_core(task)
    page_type = "页面"
    for token, mapped in [("设置", "设置页"), ("配置", "设置页"), ("申请", "申请页"), ("结果", "结果页"), ("详情", "详情页"), ("帮助", "说明区")]:
        if token in task or token in page.name:
            page_type = mapped
            break
    if page.page_type and "结果" in page.page_type:
        page_type = "结果页"
    name = f"{user}{task}{page_type}"
    return shorten_readable_name(name, max_len=24)


def _clean_flow_steps(raw_steps: str) -> str:
    parts = [part.strip() for part in raw_steps.split("->")]
    kept: list[str] = []
    for part in parts:
        cleaned = clean_duplicate_action(part)
        if not cleaned or "文档" in part:
            continue
        if cleaned in {"需求概述", "调研", "竞品分析"}:
            continue
        kept.append(cleaned)
    return " -> ".join(kept[:4]) or "进入主流程并执行关键步骤"


def build_readable_flow_sentence(flow: TaskFlowEntry) -> str:
    actor = extract_readable_role(flow.start) or "用户"
    action = clean_duplicate_action(flow.name) or "执行主任务"
    key_steps = _clean_flow_steps(flow.key_steps)
    success = hide_placeholder_in_core(flow.success_result)
    failure = hide_placeholder_in_core(flow.failure_result).replace("失败", "受阻")
    return f"{actor}发起“{action}”，系统按“{key_steps}”推进；成功后{success}，失败时{failure}。"


def build_readable_state_sentence(state: StateFeedbackEntry) -> str:
    state_name = hide_placeholder_in_core(state.name)
    if state_name == _CORE_PLACEHOLDER_TEXT or is_placeholder_text(state_name):
        return _CORE_PLACEHOLDER_TEXT
    trigger = hide_placeholder_in_core(state.trigger)
    actions = clean_duplicate_action(state.available_actions) or "继续当前任务、查看解释或返回上一步"
    feedback = hide_placeholder_in_core(state.page_feedback) or hide_placeholder_in_core(state.copy_feedback)
    downstream = hide_placeholder_in_core(state.downstream)
    return f"当进入“{state_name}”时（触发：{trigger}），用户可执行{actions}；系统需要说明{feedback}，并明确下一步是{downstream}。"


def build_readable_risk_sentence(risk: ExperienceRiskEntry) -> str:
    name = hide_placeholder_in_core(risk.name)
    if name == _CORE_PLACEHOLDER_TEXT or is_placeholder_text(name):
        name = "关键异常风险"
    trigger = hide_placeholder_in_core(risk.trigger)
    confusion = hide_placeholder_in_core(risk.confusion)
    protection = hide_placeholder_in_core(risk.protection)
    if confusion == _CORE_PLACEHOLDER_TEXT or is_placeholder_text(confusion):
        confusion = "用户无法判断当前状态和可操作动作"
    if (
        not protection
        or protection == _CORE_PLACEHOLDER_TEXT
        or ("显式提供阻断解释" in protection and "页面" not in protection)
        or protection.replace("/", "").strip() in {"中显式提供阻断解释处理方向与来源追踪入口", "在中显式提供阻断解释处理方向与来源追踪入口"}
    ):
        protection = "关键页面中显式提供阻断解释、处理方向与来源追踪入口"
    return f"风险“{name}”常在“{trigger}”出现，用户会因为“{confusion}”产生疑惑；系统需通过“{protection}”做保护。"


def _build_key_page_summary(page: PageBlueprint) -> str:
    title = shorten_readable_name(build_readable_page_name(PageEntry(
        page_id=page.page_id,
        name=page.name,
        page_type="页面",
        target_user=page.target_user,
        primary_task=page.primary_task,
        entry=page.entry_condition,
        exit=page.relation,
        relation=page.relation,
    )), max_len=24)
    if is_placeholder_text(title):
        title = "关键页面（需补充命名）"
    task = clean_duplicate_action(page.primary_task) or hide_placeholder_in_core(page.primary_task)
    entry = clean_duplicate_action(hide_placeholder_in_core(page.entry_condition))
    focus = hide_placeholder_in_core(page.first_screen_focus)
    action_text = "、".join(clean_duplicate_action(item) for item in page.key_actions if clean_duplicate_action(item))
    risk_parts: list[str] = []
    for item in page.risks:
        cleaned = hide_placeholder_in_core(item)
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

    page_groups_raw = [
        (
            build_task_group_label(page.primary_task),
            build_readable_page_name(page),
            clean_duplicate_action(hide_placeholder_in_core(page.entry)),
        )
        for page in model.pages[:8]
    ]
    page_groups_seen: set[str] = set()
    page_groups: list[str] = []
    for group_label, page_name, page_entry in page_groups_raw:
        if page_name in page_groups_seen:
            continue
        page_groups_seen.add(page_name)
        page_groups.append(f"{group_label}：{page_name}（入口：{page_entry}）")
    page_groups = dedupe_by_semantic_key(page_groups)

    flow_summary = dedupe_by_semantic_key([build_readable_flow_sentence(flow) for flow in model.task_flows[:8]])
    key_page_summaries = [_build_key_page_summary(page) for page in model.key_pages[:6]]
    state_summaries = dedupe_by_semantic_key([build_readable_state_sentence(state) for state in model.state_feedbacks[:8]])

    copy_summaries = dedupe_by_semantic_key(
        [
            (
                f"在“{hide_placeholder_in_core(copy.scenario)}”场景，文案要解释"
                f"“{hide_placeholder_in_core(copy.semantic_goal)}”，并包含“{hide_placeholder_in_core(copy.required_info)}”。"
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
