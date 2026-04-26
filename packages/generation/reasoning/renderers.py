from __future__ import annotations

import json

from .schemas import BusinessModel, ExperienceModel, FactsModel


def _render_string_list(items: list[str]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" if not item.startswith("- ") else item for item in items)


def _render_fact_list(entries: list[object]) -> str:
    if not entries:
        return "- none"
    return "\n".join(f"- {item.fact_id}: {item.text} (source: {item.source_ref})" for item in entries)


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
    judgment_core_lines = _render_string_list(
        [f"{item.judgment_id} {item.title}：{item.conclusion}" for item in model.judgments]
    )
    option_summary_lines = _render_string_list(
        [f"{item.option_id} {item.option}：{item.conclusion}（前提：{item.fit_condition}）" for item in model.placement_options]
    )
    option_rows = "\n".join(
        f"| {item.option_id} | {item.option} | {item.conclusion} | {item.fit_condition} | {item.benefit} | {item.tradeoff} | {item.why_not_final} |"
        for item in model.placement_options
    )
    risk_rows = "\n".join(
        f"| {item.risk_id} | {item.name} | {item.manifestation} | {item.consequence} | {item.level} | {item.mitigation} |"
        for item in model.risks
    )
    trace_rows = "\n".join(
        f"| {item.judgment_id} | {item.section} | {item.conclusion} | {item.facts_basis} | {item.baseline_basis} | {item.comparison} | {item.remaining_gap} |"
        for item in model.trace_links
    )
    knowledge_lines = _render_string_list(model.knowledge_hits)
    final_position_reason = _render_string_list(model.final_position_reason)
    fact_lines = _render_string_list(model.fact_links)
    adopted_rules = _render_string_list(model.adopted_rules)
    adopted_dependencies = _render_string_list(model.adopted_dependencies)
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

- 结论：{model.final_position}
- 建议方向：{model.placement_options[0].option if model.placement_options else "待确认"}

## 2. 为什么要做

- 业务问题：{model.problem_statement}
- 变更意图：{model.change_intent}
- 目标与边界：{model.review_goal}

## 3. 值不值得做

- 收益与价值：
{_render_string_list([f"{item.option_id} {item.option} -> {item.benefit}" for item in model.placement_options])}
- 成本与代价：
{_render_string_list([f"{item.option_id} {item.option} -> {item.tradeoff}" for item in model.placement_options])}

## 4. 怎么做更合理

- 当前建议：{model.placement_options[0].option if model.placement_options else "待确认"}
- 可对照方案：
{option_summary_lines}
- 关键判断：
{judgment_core_lines}

## 5. 哪些不能随便做

### 关键规则边界
{adopted_rules}

### 关键依赖边界
{adopted_dependencies}

## 6. 主要风险

| risk_id | 风险 | 表现 | 后果 | 等级 | 缓解方向 |
| --- | --- | --- | --- | --- | --- |
{risk_rows}

## 7. 体验设计要注意什么

- 体验层承接要求：
{_render_string_list(model.experience_constraints)}
- 立场理由：
{final_position_reason}

## 附录 A：事实承接

- 评审对象：{model.review_target}
- 评审边界：{model.review_boundary}
- 变更类型：{model.change_type}
- 触发背景：{model.trigger}
- F-xx 承接列表：
{fact_lines}

## 附录 B：命中知识与来源

- 命中知识：
{knowledge_lines}

| baseline_id | 基线结论 | source_path |
| --- | --- | --- |
{baseline_rows}

## 附录 C：备选方案比较

| option_id | 方案 | 当前结论 | 适用前提 | 主要收益 | 主要代价 / 风险 | 为什么不是最终立场 |
| --- | --- | --- | --- | --- | --- | --- |
{option_rows}

## 附录 D：判断追踪映射

| judgment_id | 对应判断 | 结论 | facts 依据 | 基线 / 策略依据 | 对比对象 | 剩余缺口 |
| --- | --- | --- | --- | --- | --- | --- |
{trace_rows}

## 附录 E：链路自检信息

### coverage 与追踪摘要
{self_check_lines}

### 开放问题与缺口（OQ / GAP）
{open_gaps}
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
    key_page_sections = "\n\n".join(
        f"""### {item.page_id} {item.name}

#### 页面目标
- 页面目标：{item.goal}
- 用户为什么来这里：{item.entry_condition}
- 首屏先看什么：{item.first_screen_focus}
- 主任务 / 次任务：{item.primary_task} / {item.secondary_task}

#### 页面信息结构
- 关键信息：{item.key_information}
- 页面状态：{', '.join(item.key_states)}
- 阅读顺序：{item.reading_order}
- 风险点：{', '.join(item.risks)}
- 文案责任：{item.copy_responsibility}
- 承接原则：{principle_ids}

#### 关键动作与关系
- 关键动作：{', '.join(item.key_actions)}
- 上下游关系：{item.relation}
"""
        for item in model.key_pages
    )
    layout_sections = "\n\n".join(f"### {item.page_id} {item.name}\n\n```text\n{item.layout_diagram}\n```" for item in model.key_pages)
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
    trace_rows = "\n".join(
        f"| {item.trace_id} | {item.object_name} | {item.business_basis} | {item.fact_basis} | {item.principle_basis} | {item.note} |"
        for item in model.trace_links
    )
    return f"""# Experience Blueprint

## 体验目标与任务边界

- 目标用户与角色：{model.target_users}
- 体验目标：{model.experience_goal}
- 任务边界：{model.task_boundary}
- 不覆盖范围：{model.excluded_scope}
- UI 讨论边界：{model.ui_boundary}

## 体验推导依据

### 上游业务立场与关键规则
{_render_string_list(model.business_basis + model.rule_basis + model.risk_basis)}

### 已命中的设计原则

- 原则引用：{principle_ids}

| principle_id | 原则名称 | 命中原因 | 作用位置 |
| --- | --- | --- | --- |
{principle_rows}

## 信息架构总览

| ia_node | 类型 | 面向角色 | 入口 | 承接对象 / 主任务 | 与其他节点关系 |
| --- | --- | --- | --- | --- | --- |
{ia_rows}

```text
{model.ia_diagram}
```

## 任务流蓝图

### 任务闭环总览
```text
{model.flow_overview_diagram}
```

### 各闭环节点
| flow_id | 流程名称 | 起点 | 关键步骤 | 关键判断 / 阻断 | 成功结果 | 失败 / 异常结果 |
| --- | --- | --- | --- | --- | --- | --- |
{flow_rows}

## 页面 / 窗口清单

| page_id | 名称 | 类型 | 目标用户 | 主任务 | 入口 | 退出方式 | 上下游关系 |
| --- | --- | --- | --- | --- | --- | --- | --- |
{page_rows}

## 关键页面蓝图
{key_page_sections}

## 区块布局示意
{layout_sections}

## 内容与信息优先级合同

| info_item | 信息目的 | 优先级 | 推荐位置 | 触发时机 | 不展示风险 |
| --- | --- | --- | --- | --- | --- |
{info_rows}

## 状态与反馈矩阵

| state_id | 状态名称 | 触发条件 | 可用动作 | 页面反馈 | 文案反馈 | 下游结果 |
| --- | --- | --- | --- | --- | --- | --- |
{state_rows}

## 文案合同

| copy_id | 场景 | 文案类型 | 语义目标 | 必含信息 | 禁止写法 | 示例方向 |
| --- | --- | --- | --- | --- | --- | --- |
{copy_rows}

## 风险、疑惑点与保护策略

| risk_id | 风险 / 疑惑点 | 触发场景 | 用户为什么会困惑 / 出错 | 保护策略 | 对应页面 / 流程 / 文案 |
| --- | --- | --- | --- | --- | --- |
{risk_rows}

## 开放问题与缺口
{_render_string_list(model.open_questions + model.gaps)}

## 体验追踪映射

| trace_id | 页面 / 流程 / 文案对象 | 承接业务判断 | 承接事实 / 规则 / 异常 | 承接原则 | 说明 |
| --- | --- | --- | --- | --- | --- |
{trace_rows}
"""


def render_gap_list() -> str:
    return """# Gap List

## Blockers

- none

## Warnings

- 当前产物生成已切到真正按输入与命中知识推理的方向，但如果来源证据不足，输出会主动变“保守”而不是回退到旧模板。

## 待补信息

- 补充更具体的任务 source 输入，以便 facts / business / experience 形成更稳定的动态结论。
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
