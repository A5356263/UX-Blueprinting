from __future__ import annotations

import json
from typing import Any

from .schemas import BusinessModel, ExperienceModel, FactsModel


def _render_string_list(items: list[str]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" if not item.startswith("- ") else item for item in items)


def _render_fact_list(entries: list[object]) -> str:
    if not entries:
        return "- none"
    return "\n".join(f"- {item.fact_id}: {item.text} (source: {item.source_ref})" for item in entries)


def _plain_business_term(text: str) -> str:
    replacements = {
        "独立成型能力": "单独做成一个完整功能",
        "并入既有能力结构": "放到已有功能里扩展",
        "收敛为规则 / 配置层": "不单独做页面，只做成配置项",
        "暂不下最终立场": "信息还不够，先不定方案",
        "能力归位": "这个需求应该放在哪里做",
        "治理边界": "哪些地方不能随便放开",
        "依赖边界": "做这件事前需要满足什么条件",
        "依赖条件": "做这件事前需要满足什么条件",
        "反模式": "容易踩坑的做法",
        "认知负担": "用户理解和学习成本",
        "当前输入驱动的能力调整": "根据这次需求得出的调整",
    }
    result = text
    for source, target in replacements.items():
        result = result.replace(source, target)
    return result


def _plain_dependency_line(text: str) -> str:
    cleaned = _plain_business_term(text)
    if ":" in cleaned:
        cleaned = cleaned.split(":", 1)[1].strip()
    cleaned = cleaned.replace("->", "，")
    return cleaned


def _plain_rule_line(text: str) -> str:
    cleaned = _plain_business_term(text)
    if ":" in cleaned:
        cleaned = cleaned.split(":", 1)[1].strip()
    cleaned = cleaned.replace("->", "，")
    return cleaned


def _plain_experience_term(text: str) -> str:
    replacements = {
        "任务闭环": "完整操作流程",
        "页面承载": "这个页面要承担的任务",
        "得到可解释结果": "展示成功结果和下一步",
        "进入阻断或补充链路": "告诉用户失败原因和处理办法",
        "preview 反向决定": "演示稿反向影响正式结构",
    }
    result = _plain_business_term(text)
    for source, target in replacements.items():
        result = result.replace(source, target)
    return result


def _render_interaction_nodes(nodes: list[InteractionNode], empty_text: str) -> str:
    if not nodes:
        return f"- {empty_text}"
    parts: list[str] = []
    for node in nodes:
        copy_lines = _render_string_list(node.copy_strategy or ["待补充文案策略"])
        state_lines = _render_string_list(node.state_notes or ["待补充状态说明"])
        exception_lines = _render_string_list(node.exception_notes or ["待补充异常说明"])
        parts.append(
            "\n".join(
                [
                    f"### {node.title}",
                    "",
                    "用户动作：",
                    node.user_action,
                    "",
                    "系统反馈：",
                    node.system_feedback,
                    "",
                    "下一步：",
                    node.next_step,
                    "",
                    "本节点需要前置解释：",
                    copy_lines,
                    "",
                    "状态关注：",
                    state_lines,
                    "",
                    "异常关注：",
                    exception_lines,
                ]
            )
        )
    return "\n\n".join(parts)


def _render_page_designs(sections: list[PageDesignSection]) -> str:
    if not sections:
        return "- 待补充页面 / 弹窗 / 抽屉设计"
    blocks: list[str] = []
    for section in sections:
        structure_lines = _render_string_list(section.structure)
        first_screen_lines = _render_string_list(section.first_screen)
        primary_lines = _render_string_list(section.primary_actions)
        secondary_lines = _render_string_list(section.secondary_actions)
        state_lines = _render_string_list(section.state_feedbacks)
        exception_lines = _render_string_list(section.exception_feedbacks)
        copy_lines = _render_string_list(section.concrete_copy)
        blocks.append(
            "\n".join(
                [
                    f"### 页面：{section.title}",
                    "",
                    "页面目标：",
                    section.page_goal,
                    "",
                    "进入条件：",
                    section.entry_condition,
                    "",
                    "页面结构：",
                    structure_lines,
                    "",
                    "首屏必须展示：",
                    first_screen_lines,
                    "",
                    "主要操作：",
                    primary_lines,
                    "",
                    "次要操作：",
                    secondary_lines,
                    "",
                    "状态与反馈：",
                    state_lines,
                    "",
                    "异常处理：",
                    exception_lines,
                    "",
                    "具体文案：",
                    copy_lines,
                    "",
                    "完成后去向：",
                    section.next_step,
                ]
            )
        )
    return "\n\n".join(blocks)


def _string_lines(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _extract_node_states(node: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for item in node.get("states", []) if isinstance(node.get("states"), list) else []:
        if isinstance(item, dict):
            name = str(item.get("name") or "").strip()
            meaning = str(item.get("meaning") or "").strip()
            feedback = str(item.get("feedback") or "").strip()
            line = "；".join(part for part in [name, meaning, feedback] if part)
            if line:
                lines.append(line)
        elif isinstance(item, str) and item.strip():
            lines.append(item.strip())
    lines.extend(_string_lines(node.get("state_refs")))
    return lines


def _extract_node_exceptions(node: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for item in node.get("exceptions", []) if isinstance(node.get("exceptions"), list) else []:
        if isinstance(item, dict):
            name = str(item.get("name") or "").strip()
            trigger = str(item.get("trigger") or "").strip()
            feedback = str(item.get("feedback") or "").strip()
            next_step = str(item.get("next_step") or "").strip()
            line = "；".join(part for part in [name, trigger, feedback, next_step] if part)
            if line:
                lines.append(line)
        elif isinstance(item, str) and item.strip():
            lines.append(item.strip())
    lines.extend(_string_lines(node.get("exception_refs")))
    return lines


def _extract_copy_lines(item: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for entry in item.get("concrete_copy", []) if isinstance(item.get("concrete_copy"), list) else []:
        if isinstance(entry, dict):
            copy_type = str(entry.get("type") or "").strip()
            copy_text = str(entry.get("text") or "").strip()
            if copy_type and copy_text:
                lines.append(f"{copy_type}：{copy_text}")
            elif copy_text:
                lines.append(copy_text)
        elif isinstance(entry, str) and entry.strip():
            lines.append(entry.strip())
    return lines


def _build_interaction_from_payload(
    payload: dict[str, Any],
) -> tuple[list[str], list[InteractionNode], list[InteractionNode], list[InteractionNode], list[PageDesignSection], list[str]]:
    overview = _string_lines(payload.get("overview", {}).get("summary") if isinstance(payload.get("overview"), dict) else [])
    role_flows = payload.get("role_flows") if isinstance(payload.get("role_flows"), list) else []
    main_nodes: list[InteractionNode] = []
    secondary_nodes: list[InteractionNode] = []
    exception_nodes: list[InteractionNode] = []
    state_feedbacks: list[str] = []
    for flow in role_flows:
        if not isinstance(flow, dict):
            continue
        flow_title = str(flow.get("title") or flow.get("summary") or flow.get("flow_id") or "未命名流程").strip()
        flow_type = str(flow.get("flow_type") or "secondary")
        for node in flow.get("nodes", []) if isinstance(flow.get("nodes"), list) else []:
            if not isinstance(node, dict):
                continue
            carrier = node.get("carrier") if isinstance(node.get("carrier"), dict) else {}
            carrier_name = str(carrier.get("name") or "").strip()
            title = str(node.get("title") or node.get("node_id") or "未命名节点").strip()
            if carrier_name:
                title = f"{title}（{carrier_name}）"
            state_notes = _extract_node_states(node)
            exception_notes = _extract_node_exceptions(node)
            role_node = InteractionNode(
                title=f"{flow_title} / {title}",
                user_action=str(node.get("user_action") or "待补充用户动作"),
                system_feedback=str(node.get("system_feedback") or "待补充系统反馈"),
                next_step=str(node.get("next_step") or "待补充下一步"),
                copy_strategy=_string_lines(node.get("copy_strategy")),
                state_notes=state_notes,
                exception_notes=exception_notes,
            )
            if flow_type == "main":
                main_nodes.append(role_node)
            elif flow_type == "exception":
                exception_nodes.append(role_node)
            else:
                secondary_nodes.append(role_node)
            state_feedbacks.extend(state_notes)

    page_designs: list[PageDesignSection] = []
    for page in payload.get("page_designs", []) if isinstance(payload.get("page_designs"), list) else []:
        if not isinstance(page, dict):
            continue
        page_designs.append(
            PageDesignSection(
                title=str(page.get("title") or page.get("page_id") or "未命名页面"),
                page_goal=str(page.get("purpose") or "待补充页面目标"),
                entry_condition=str(page.get("entry") or "待补充进入条件"),
                structure=_string_lines(page.get("modules")),
                first_screen=_string_lines(page.get("modules"))[:3],
                primary_actions=_string_lines(page.get("primary_actions")),
                secondary_actions=_string_lines(page.get("secondary_actions")),
                state_feedbacks=_string_lines(page.get("states")),
                exception_feedbacks=_string_lines(page.get("exceptions")),
                concrete_copy=_extract_copy_lines(page),
                next_step=str(page.get("next_step") or "待补充完成后去向"),
            )
        )
    return overview, main_nodes, secondary_nodes, exception_nodes, page_designs, state_feedbacks


def render_facts_markdown(model: FactsModel) -> str:
    references = _render_string_list(model.explicit_references)
    note_lines = _render_string_list([f"{item.note_id}: {item.title} -> {item.summary}" for item in model.knowledge_notes])
    primary_sources = _render_string_list(model.source_files[:2])
    contract_sources = _render_string_list(
        [
            f"projects/{model.project_id}/runtime/task_card_resolved.json",
            f"projects/{model.project_id}/runtime/context_manifest.json",
        ]
    )
    terminology_rows = "\n".join(
        f"| {item.term_id} | {item.term} | {item.meaning} | {item.boundary} | {item.source} |" for item in model.terminology
    )
    actor_rows = "\n".join(
        f"| {item.actor_id} | {item.name} | {item.actor_type} | {item.responsibility} | {item.source} |" for item in model.actors
    )
    object_rows = "\n".join(
        f"| {item.object_id} | {item.name} | {item.object_type} | {item.description} | {item.source} |" for item in model.objects
    )
    rule_rows = "\n".join(
        f"| {item.rule_id} | {item.name} | {item.trigger} | {item.subject} | {item.precondition} | {item.result} | {item.failure} | {item.source_ref} |"
        for item in model.rules
    )
    state_rows = "\n".join(
        f"| {item.state_id} | {item.name} | {item.enter_condition} | {item.exit_condition} | {item.blocking_condition} | {item.description} | {item.source_ref} |"
        for item in model.states
    )
    flow_rows = "\n".join(
        f"| {item.flow_id} | {item.actor} | {item.action} | {item.precondition} | {item.result} | {item.note} | {item.source_ref} |"
        for item in model.flows
    )
    exception_rows = "\n".join(
        f"| {item.exception_id} | {item.scenario} | {item.trigger} | {item.outcome} | {item.impacted} | {item.source_ref} |"
        for item in model.exceptions
    )
    dependency_rows = "\n".join(
        f"| {item.dependency_id} | {item.name} | {item.dependency_type} | {item.role} | {item.confidence} | {item.source_ref} |"
        for item in model.dependencies
    )
    trace_rows = "\n".join(
        f"| {item.trace_id} | {item.trace_type} | {item.source_location} | {item.source_file} | {item.note} |"
        for item in model.trace_links
    )
    return f"""# Facts

## 任务意图

- 任务目标：{model.task_goal}
- 任务边界：{model.task_boundary}
- 输出用途：{model.output_purpose}

## 事实来源说明

- 主输入：
{primary_sources}
- 任务合同：
{contract_sources}
- 显式引用：
{references}
- 知识校准命中：
{note_lines}
- 使用边界：
  - facts 的业务事实只从 requirement.md / background.md 抽取
  - task_card_resolved.json / context_manifest.json 仅用于任务意图、任务边界与执行约束说明
  - wiki 只做术语与边界校准，不替代当前任务事实

## 术语与对象边界

| term_id | 术语 | 当前任务中的含义 | 边界说明 | 来源 |
| --- | --- | --- | --- | --- |
{terminology_rows}

## 角色与对象清单

### 角色清单

| actor_id | 角色 | 角色类型 | 当前职责 / 影响 | 来源 |
| --- | --- | --- | --- | --- |
{actor_rows}

### 对象清单

| object_id | 对象 | 对象类型 | 当前任务中的说明 | 来源 |
| --- | --- | --- | --- | --- |
{object_rows}

## 原子事实清单

### Actor Facts
{_render_fact_list(model.actor_facts)}

### Object Facts
{_render_fact_list(model.object_facts)}

### State Facts
{_render_fact_list(model.state_facts)}

### Action Facts
{_render_fact_list(model.action_facts)}

### Rule Facts
{_render_fact_list(model.rule_facts)}

### Exception Facts
{_render_fact_list(model.exception_facts)}

### Dependency Facts
{_render_fact_list(model.dependency_facts)}

### Scope Facts
{_render_fact_list(model.scope_facts)}

## 规则矩阵

| rule_id | 规则名称 | trigger（触发条件） | subject（作用对象） | precondition（前置条件） | result（结果） | failure / block（失败或拦截） | source_ref |
| --- | --- | --- | --- | --- | --- | --- | --- |
{rule_rows}

## 状态模型

| state_id | 状态 | 进入条件 | 退出条件 | 阻断条件 | 说明 | source_ref |
| --- | --- | --- | --- | --- | --- | --- |
{state_rows}

## 动作与流程事实

| flow_id | 发起角色 | 动作 | 前置条件 | 后续动作 / 结果 | 备注 | source_ref |
| --- | --- | --- | --- | --- | --- | --- |
{flow_rows}

## 异常与拦截清单

| exception_id | 场景 | 触发条件 | 系统结果 / 提示 | 影响对象 | source_ref |
| --- | --- | --- | --- | --- | --- |
{exception_rows}

## 依赖清单

| dependency_id | 依赖项 | 类型 | 当前作用 | 当前确认度 | source_ref |
| --- | --- | --- | --- | --- | --- |
{dependency_rows}

## 范围与非范围

### 本次明确范围
{_render_string_list(model.in_scope)}

### 本次明确非范围 / 暂不展开
{_render_string_list(model.out_of_scope)}

## 已知约束
{_render_string_list(model.constraints)}

## 开放问题与缺口

### Open Questions
{_render_string_list(model.open_questions)}

### Gaps
{_render_string_list(model.gaps)}

## 追踪映射

| fact_or_unit_id | 类型 | 对应原文位置 | 主要来源文件 | 备注 |
| --- | --- | --- | --- | --- |
{trace_rows}
"""


def render_business_markdown(model: BusinessModel) -> str:
    baseline_rows = "\n".join(
        f"| {item.baseline_id} | {item.text} | {', '.join(item.source_refs)} |"
        for item in model.baselines
    )
    judgment_core_lines = _render_string_list([f"{item.title}：{_plain_business_term(item.conclusion)}" for item in model.judgments])
    option_summary_lines = _render_string_list(
        [
            f"{_plain_business_term(item.option)}：{_plain_business_term(item.conclusion)}（适用条件：{_plain_business_term(item.fit_condition)}）"
            for item in model.placement_options
        ]
    )
    option_rows = "\n".join(
        f"| {item.option_id} | {item.option} | {item.conclusion} | {item.fit_condition} | {item.benefit} | {item.tradeoff} | {item.why_not_final} |"
        for item in model.placement_options
    )
    risk_rows = "\n".join(
        f"| {item.risk_id} | {item.name} | {item.manifestation} | {item.consequence} | {item.level} | {item.mitigation} |" for item in model.risks
    )
    risk_core_lines = _render_string_list(
        [
            f"风险：{_plain_business_term(item.name)}；影响：{_plain_business_term(item.consequence)}；建议：{_plain_business_term(item.mitigation)}"
            for item in model.risks
        ]
    )
    trace_rows = "\n".join(
        f"| {item.judgment_id} | {item.section} | {item.conclusion} | {item.facts_basis} | {item.baseline_basis} | {item.comparison} | {item.remaining_gap} |"
        for item in model.trace_links
    )
    knowledge_lines = _render_string_list(model.knowledge_hits)
    final_position_reason = _render_string_list([_plain_business_term(item) for item in model.final_position_reason])
    fact_lines = _render_string_list(model.fact_links)
    adopted_rules = _render_string_list([_plain_rule_line(item) for item in model.adopted_rules])
    adopted_dependencies = _render_string_list([_plain_dependency_line(item) for item in model.adopted_dependencies])
    raw_dependencies = _render_string_list(model.adopted_dependencies)
    open_gaps = _render_string_list(model.open_questions + model.gaps)
    self_check_lines = _render_string_list(
        [
            f"judgment_count={len(model.judgments)}",
            f"fact_ref_count={len(model.fact_links)}",
            f"baseline_count={len(model.baselines)}",
            f"option_count={len(model.placement_options)}",
            f"risk_count={len(model.risks)}",
            f"trace_count={len(model.trace_links)}",
        ]
    )
    return f"""# Business Blueprint

## 1. 一句话结论

- 结论：{_plain_business_term(model.final_position)}
- 建议方向：{_plain_business_term(model.placement_options[0].option) if model.placement_options else "待确认"}

## 2. 需求是否成立

- 问题与场景：{model.problem_statement}
- 变更意图：{model.change_intent}
- 当前判断：
{judgment_core_lines}

## 3. 值不值得做

- 收益与价值：
{_render_string_list([f"{_plain_business_term(item.option)}：{_plain_business_term(item.benefit)}" for item in model.placement_options])}
- 成本与代价：
{_render_string_list([f"{_plain_business_term(item.option)}：{_plain_business_term(item.tradeoff)}" for item in model.placement_options])}

## 4. 应该做成什么能力形态

- 当前建议形态：{_plain_business_term(model.placement_options[0].option) if model.placement_options else "待确认"}
- 备选路径比较：
{option_summary_lines}
- 立场理由：
{final_position_reason}

## 5. 推荐业务方案

- 目标与边界：{model.review_goal}
- 推荐方案骨架：
{_render_string_list(model.final_position_reason)}
- 角色与流程承接：
{_render_string_list(model.experience_constraints[:3])}

## 6. 必须守住的规则和边界

### 关键规则限制
{adopted_rules}

### 前置条件与限制
{adopted_dependencies}

## 7. 主要风险与保护策略

{risk_core_lines}

## 8. 方案承接要求

{_render_string_list(model.experience_constraints)}

## 9. 待确认问题

{_render_string_list(model.open_questions + model.gaps)}

## 附录：事实、知识与判断追踪

### 事实承接
- 评审对象：{model.review_target}
- 评审边界：{model.review_boundary}
- 变更类型：{model.change_type}
- 触发背景：{model.trigger}
- F-xx 承接列表：
{fact_lines}
- DEP-xx 原始依赖项：
{raw_dependencies}

### 命中知识与来源
- 命中知识：
{knowledge_lines}

| baseline_id | 基线结论 | source_path |
| --- | --- | --- |
{baseline_rows}

### 备选方案比较
| option_id | 方案 | 当前结论 | 适用前提 | 主要收益 | 主要代价 / 风险 | 为什么不是最终立场 |
| --- | --- | --- | --- | --- | --- | --- |
{option_rows}

### 判断追踪映射
| judgment_id | 对应判断 | 结论 | facts 依据 | 基线 / 策略依据 | 对比对象 | 剩余缺口 |
| --- | --- | --- | --- | --- | --- | --- |
{trace_rows}

### 链路自检信息
{self_check_lines}

### 开放问题与缺口（OQ / GAP）
{open_gaps}

### 风险原始追踪（RSK）
| risk_id | 风险 | 表现 | 后果 | 等级 | 缓解方向 |
| --- | --- | --- | --- | --- | --- |
{risk_rows}
"""


def render_experience_markdown(model: ExperienceModel) -> str:
    principle_rows = "\n".join(
        f"| {item.principle_id} | {item.name} | {item.reason} | {item.applied_to} |" for item in model.principles
    )
    principle_ids = ", ".join(item.principle_id for item in model.principles[:4]) or "PR-01"
    ia_rows = "\n".join(
        f"| {item.ia_node} | {item.node_type} | {item.target_user} | {item.entry} | {item.carries} | {item.relation} |"
        for item in model.ia_entries
    )
    flow_rows = "\n".join(
        f"| {item.flow_id} | {item.name} | {item.start} | {item.key_steps} | {item.key_decision} | {item.success_result} | {item.failure_result} |"
        for item in model.task_flows
    )
    page_rows = "\n".join(
        f"| {item.page_id} | {item.name} | {item.page_type} | {item.target_user} | {item.primary_task} | {item.entry} | {item.exit} | {item.relation} |"
        for item in model.pages
    )
    trace_rows = "\n".join(
        f"| {item.trace_id} | {item.object_name} | {item.business_basis} | {item.fact_basis} | {item.principle_basis} | {item.note} |"
        for item in model.trace_links
    )
    info_rows = "\n".join(
        f"| {item.info_id} | {item.purpose} | {item.priority} | {item.placement} | {item.trigger} | {item.hidden_risk} |"
        for item in model.info_contracts
    )
    state_rows = "\n".join(
        f"| {item.state_id} | {item.name} | {item.trigger} | {item.available_actions} | {item.page_feedback} | {item.copy_feedback} | {item.downstream} |"
        for item in model.state_feedbacks
    )
    copy_rows = "\n".join(
        f"| {item.copy_id} | {item.scenario} | {item.copy_type} | {item.semantic_goal} | {item.required_info} | {item.forbidden_style} | {item.direction} |"
        for item in model.copy_contracts
    )
    risk_rows = "\n".join(
        f"| {item.risk_id} | {item.name} | {item.trigger} | {item.confusion} | {item.protection} | {item.target} |"
        for item in model.risks
    )
    overview_lines = _render_string_list(
        [
            f"目标用户与角色：{model.target_users}",
            f"体验目标：{model.experience_goal}",
            f"任务边界：{model.task_boundary}",
        ]
    )
    main_flow_lines = _render_string_list(
        [f"{item.flow_id} {item.name}：{item.key_steps}" for item in model.task_flows[:4]]
    )
    secondary_flow_lines = _render_string_list(
        [f"{item.page_id} {item.name}：{item.relation}" for item in model.pages[:4]]
    )
    exception_flow_lines = _render_string_list(
        [f"{item.risk_id} {item.name}：{item.protection}" for item in model.risks[:6]]
    )
    page_design_lines = _render_string_list(
        [f"{item.page_id} {item.name}：{item.primary_task}" for item in model.pages[:10]]
    )
    state_feedback_lines = _render_string_list(
        [f"{item.state_id} {item.name}：{item.copy_feedback}" for item in model.state_feedbacks[:10]]
    )
    layout_sections = "\n\n".join(f"### {item.page_id} {item.name}\n\n```text\n{item.layout_diagram}\n```" for item in model.key_pages)
    self_check_lines = _render_string_list(
        [
            f"page_count={len(model.pages)}",
            f"flow_count={len(model.task_flows)}",
            f"key_page_count={len(model.key_pages)}",
            f"state_count={len(model.state_feedbacks)}",
            f"copy_count={len(model.copy_contracts)}",
            f"risk_count={len(model.risks)}",
            f"trace_count={len(model.trace_links)}",
        ]
    )
    return f"""# Experience Blueprint

## 1. 交互流程总览

{overview_lines}

## 2. 主交互流程

{main_flow_lines}

## 3. 次交互流程

{secondary_flow_lines}

## 4. 异常与阻断流程

{exception_flow_lines}

## 5. 页面 / 弹窗 / 抽屉设计

{page_design_lines}

## 6. 状态与反馈文案

{state_feedback_lines}

## 附录 A：上游依据

- 上游业务判断：
{_render_string_list([_plain_experience_term(item) for item in model.business_basis])}
- 上游规则限制：
{_render_string_list([_plain_experience_term(item) for item in model.rule_basis])}
- 上游风险：
{_render_string_list([_plain_experience_term(item) for item in model.risk_basis])}
- 开放问题与缺口：
{_render_string_list(model.open_questions + model.gaps)}

## 附录 B：原始信息架构与页面清单

| ia_node | 类型 | 面向角色 | 入口 | 承接对象 / 主任务 | 与其他节点关系 |
| --- | --- | --- | --- | --- | --- |
{ia_rows}

```text
{model.ia_diagram}
```

| page_id | 名称 | 类型 | 目标用户 | 主任务 | 入口 | 退出方式 | 上下游关系 |
| --- | --- | --- | --- | --- | --- | --- | --- |
{page_rows}

### 区块布局示意
{layout_sections}

### 内容与信息优先级合同
| info_item | 信息目的 | 优先级 | 推荐位置 | 触发时机 | 不展示风险 |
| --- | --- | --- | --- | --- | --- |
{info_rows}

## 附录 C：页面 / 流程追踪映射

| flow_id | 流程名称 | 起点 | 关键步骤 | 关键判断 / 阻断 | 成功结果 | 失败 / 异常结果 |
| --- | --- | --- | --- | --- | --- | --- |
{flow_rows}

| trace_id | 页面 / 流程 / 文案对象 | 承接业务判断 | 承接事实 / 规则 / 异常 | 承接原则 | 说明 |
| --- | --- | --- | --- | --- | --- |
{trace_rows}

## 附录 D：设计原则引用

- 原则引用：{principle_ids}

| principle_id | 原则名称 | 命中原因 | 作用位置 |
| --- | --- | --- | --- |
{principle_rows}

## 附录 E：原始状态 / 文案 / 风险矩阵

### coverage 与追踪摘要
{self_check_lines}

### 状态与反馈矩阵（原始）
| state_id | 状态名称 | 触发条件 | 可用动作 | 页面反馈 | 文案反馈 | 下游结果 |
| --- | --- | --- | --- | --- | --- | --- |
{state_rows}

### 文案合同（原始）
| copy_id | 场景 | 文案类型 | 语义目标 | 必含信息 | 禁止写法 | 示例方向 |
| --- | --- | --- | --- | --- | --- | --- |
{copy_rows}

### 风险追踪（RSK）
| risk_id | 风险 / 疑惑点 | 触发场景 | 用户为什么会困惑 / 出错 | 保护策略 | 对应页面 / 流程 / 文案 |
| --- | --- | --- | --- | --- | --- |
{risk_rows}
"""


def render_gap_list() -> str:
    return """# Gap List

## Blockers

- none

## Warnings

- 当前产物生成已切到真正按输入与命中知识推理的方向，但如果来源证据不足，输出会主动变“保守”而不是回退到旧模板。

## 待补信息

- 补充更具体的任务原始输入，以便 facts / business / experience 形成更稳定的动态结论。
"""


def render_check_report() -> str:
    return """# Check Report

## Summary

- status: pending
- has_blocker: false
- blocker_count: 0
- warning_count: 0
- info_count: 0

## Output Status

- facts.md: present
- business_blueprint.md: present
- experience_blueprint.md: present
- gap_list.md: present
- check_report.md: present
- check_status.json: present

## Blockers

- none

## Warnings

- 当前是 generate 阶段初始报告，仍需继续运行 gate / validate / coverage 完成正式检查。

## Infos

- generate-* 已完成正式初稿写入。

## Machine Status

- 机器可读状态文件：`workspace/check_status.json`
"""


def render_check_status(project_id: str) -> str:
    payload = {
        "task_id": project_id,
        "status": "pending",
        "has_blocker": False,
        "blocker_count": 0,
        "warning_count": 0,
        "info_count": 0,
        "completed_outputs": [
            f"projects/{project_id}/workspace/facts.md",
            f"projects/{project_id}/workspace/business_blueprint.md",
            f"projects/{project_id}/workspace/experience_blueprint.md",
            f"projects/{project_id}/workspace/gap_list.md",
            f"projects/{project_id}/workspace/check_report.md",
            f"projects/{project_id}/workspace/check_status.json",
        ],
        "missing_outputs": [],
        "generated_by": "packages.generation",
        "updated_at": "",
        "issues": {
            "blockers": [],
            "warnings": [],
            "infos": ["generate-* 已完成正式初稿写入。"],
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
