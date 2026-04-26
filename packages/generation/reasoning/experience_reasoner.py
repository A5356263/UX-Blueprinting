from __future__ import annotations

from .knowledge_loader import load_knowledge_notes
from .schemas import (
    BusinessModel,
    CopyEntry,
    ExperienceModel,
    ExperienceRiskEntry,
    ExperienceTraceEntry,
    FactsModel,
    IaEntry,
    InfoContractEntry,
    PageBlueprint,
    PageEntry,
    PrincipleEntry,
    StateFeedbackEntry,
    TaskFlowEntry,
)


def _state_kind(name: str) -> str:
    lowered = name.lower()
    if "失败" in name or "阻断" in name:
        return "blocker"
    if "成功" in name or "完成" in name:
        return "success"
    if "处理" in name or "待" in name:
        return "processing"
    if "启用" in name or "打开" in name:
        return "active"
    return "default"


def _build_principles(project_id: str, business_model: BusinessModel) -> list[PrincipleEntry]:
    notes = load_knowledge_notes(project_id, stage="experience")
    principles: list[PrincipleEntry] = []
    for note in notes:
        if note.kind != "guideline":
            continue
        signals = note.signals[:2] or [note.summary]
        for signal in signals:
            principles.append(
                PrincipleEntry(
                    principle_id=f"PR-{len(principles) + 1:02d}",
                    name=note.title,
                    reason=signal,
                    applied_to="页面承载、信息优先级、状态解释或文案职责",
                )
            )
            if len(principles) >= 6:
                return principles
    if not principles:
        for line in business_model.experience_constraints[:3]:
            principles.append(
                PrincipleEntry(
                    principle_id=f"PR-{len(principles) + 1:02d}",
                    name="业务约束转体验承载",
                    reason=line,
                    applied_to="页面承载与解释责任",
                )
            )
    return principles


def _build_task_flows(facts_model: FactsModel) -> list[TaskFlowEntry]:
    flows: list[TaskFlowEntry] = []
    if facts_model.flows:
        for flow in facts_model.flows:
            success_name = next((state.name for state in facts_model.states if _state_kind(state.name) == "success"), "得到可解释结果")
            failure_name = next((state.name for state in facts_model.states if _state_kind(state.name) == "blocker"), "进入阻断或补充链路")
            flows.append(
                TaskFlowEntry(
                    flow_id=f"TF-{len(flows) + 1:02d}",
                    name=flow.action,
                    start=flow.actor,
                    key_steps=f"{flow.precondition} -> {flow.action} -> {flow.result}",
                    key_decision=flow.note,
                    success_result=success_name,
                    failure_result=failure_name,
                )
            )
    else:
        flows.append(
            TaskFlowEntry(
                flow_id="TF-01",
                name="当前任务主闭环",
                start="从 source 输入进入",
                key_steps="理解任务目标 -> 组织判断 -> 产出正式蓝图",
                key_decision="当前没有足够的动作证据，只能按保守主闭环展开。",
                success_result="形成当前阶段正式产物",
                failure_result="进入 gap 与待确认链路",
            )
        )
    return flows


def _build_pages(flows: list[TaskFlowEntry], facts_model: FactsModel) -> list[PageEntry]:
    pages: list[PageEntry] = []
    for flow in flows:
        pages.append(
            PageEntry(
                page_id=f"P-{len(pages) + 1:02d}",
                name=f"{flow.name}承载页",
                page_type="页面",
                target_user=flow.start,
                primary_task=flow.name,
                entry=f"从 {flow.start} 进入该闭环",
                exit=f"进入 {flow.success_result} 或 {flow.failure_result}",
                relation=f"承接 {flow.flow_id} 的主任务节点",
            )
        )
        if facts_model.states or facts_model.exceptions:
            pages.append(
                PageEntry(
                    page_id=f"P-{len(pages) + 1:02d}",
                    name=f"{flow.name}反馈页",
                    page_type="结果页 / 详情页",
                    target_user=flow.start,
                    primary_task="理解结果、状态与下一步",
                    entry=f"{flow.name} 执行后进入",
                    exit="返回上一步或进入下一闭环",
                    relation=f"承接 {flow.flow_id} 的结果解释节点",
                )
            )
    if facts_model.dependencies or facts_model.gaps:
        pages.append(
            PageEntry(
                page_id=f"P-{len(pages) + 1:02d}",
                name="帮助与追踪页",
                page_type="抽屉 / 内嵌支持模块",
                target_user="所有需要解释边界的角色",
                primary_task="查看规则、来源、依赖与 gaps",
                entry="从主页面或反馈页进入",
                exit="关闭后回到原上下文",
                relation="作为辅助承载，解释为什么当前结构要这样展开",
            )
        )
    return pages


def _layout_for_page(page: PageEntry, facts_model: FactsModel) -> str:
    focus = facts_model.task_goal or page.primary_task
    return "\n".join(
        [
            f"[Header: {page.name} + 当前状态 + 帮助入口]",
            f"[Intro: {focus}]",
            f"[Main: {page.primary_task}]",
            "[Support: 规则说明 / 来源追踪 / 风险解释]",
            f"[Footer: {page.exit}]",
        ]
    )


def _build_key_pages(pages: list[PageEntry], facts_model: FactsModel) -> list[PageBlueprint]:
    blueprints: list[PageBlueprint] = []
    shared_states = [state.name for state in facts_model.states[:4]] or ["当前闭环状态"]
    shared_risks = [exception.scenario for exception in facts_model.exceptions[:3]] or facts_model.gaps[:2] or ["输入不足时要显式解释不确定性"]
    for page in pages[:6]:
        primary_action = page.primary_task
        secondary = "查看来源、规则或补充解释" if "帮助" not in page.name else "帮助当前角色回链判断依据"
        blueprints.append(
            PageBlueprint(
                page_id=page.page_id,
                name=page.name,
                goal=f"让用户在当前节点完成“{page.primary_task}”，同时知道为什么要在这里承载。",
                target_user=page.target_user,
                entry_condition=page.entry,
                primary_task=primary_action,
                secondary_task=secondary,
                first_screen_focus=f"先看到当前节点目标、关键边界、是否可继续以及当前状态。",
                key_information=f"这里要优先解释与 {page.primary_task} 直接相关的事实、规则、状态和结果。",
                reading_order="先看任务目标与边界，再看主任务内容，再看状态反馈，最后看帮助与追踪入口。",
                key_actions=[primary_action, "查看状态解释", "查看规则或来源"],
                key_states=shared_states,
                risks=shared_risks,
                copy_responsibility="页面文案要负责解释边界、状态变化和下一步，而不是只提示操作。",
                relation=page.relation,
                layout_diagram=_layout_for_page(page, facts_model),
            )
        )
    return blueprints


def _build_info_contracts(key_pages: list[PageBlueprint]) -> list[InfoContractEntry]:
    contracts: list[InfoContractEntry] = []
    for page in key_pages:
        contracts.append(
            InfoContractEntry(
                info_id=f"INFO-{len(contracts) + 1:02d}",
                purpose=f"解释 {page.name} 的节点目标与边界",
                priority="高",
                placement=f"{page.page_id} 首屏",
                trigger="进入页面时",
                hidden_risk="如果不前置解释，用户会把页面承载误解成固定模板页面。",
            )
        )
        contracts.append(
            InfoContractEntry(
                info_id=f"INFO-{len(contracts) + 1:02d}",
                purpose=f"解释 {page.name} 的状态与下一步",
                priority="高",
                placement=f"{page.page_id} 主区或结果区",
                trigger="操作前后",
                hidden_risk="如果不解释状态，用户会不知道当前闭环是否完成。",
            )
        )
        if len(contracts) >= 8:
            break
    return contracts


def _build_state_feedbacks(facts_model: FactsModel, pages: list[PageEntry]) -> list[StateFeedbackEntry]:
    page_name = pages[0].name if pages else "当前承载页"
    feedbacks: list[StateFeedbackEntry] = []
    for state in facts_model.states[:6]:
        kind = _state_kind(state.name)
        feedbacks.append(
            StateFeedbackEntry(
                state_id=state.state_id,
                name=state.name,
                trigger=state.enter_condition,
                available_actions="继续当前任务 / 查看解释 / 返回上一步" if kind != "success" else "查看结果 / 进入下一步",
                page_feedback=f"{page_name} 需要显式显示“{state.name}”与其上下文含义。",
                copy_feedback=state.description,
                downstream=state.exit_condition,
            )
        )
    if not feedbacks:
        feedbacks.append(
            StateFeedbackEntry(
                state_id="ST-01",
                name="待补充",
                trigger="当前没有稳定状态证据",
                available_actions="补充输入 / 保守输出",
                page_feedback="页面需要明确告诉用户当前状态证据不足。",
                copy_feedback="文案必须把不确定性写出来。",
                downstream="回到 gap 链路",
            )
        )
    return feedbacks


def _build_copy_contracts(key_pages: list[PageBlueprint], state_feedbacks: list[StateFeedbackEntry]) -> list[CopyEntry]:
    contracts: list[CopyEntry] = []
    for page in key_pages[:4]:
        contracts.append(
            CopyEntry(
                copy_id=f"COPY-{len(contracts) + 1:02d}",
                scenario=page.name,
                copy_type="说明文案",
                semantic_goal="解释为什么当前闭环要在这里承载，以及用户现在要做什么。",
                required_info="页面目标、关键边界、主要动作、是否存在阻断条件。",
                forbidden_style="不要只说“请操作”或“更方便”。",
                direction=page.copy_responsibility,
            )
        )
    for state in state_feedbacks[:3]:
        contracts.append(
            CopyEntry(
                copy_id=f"COPY-{len(contracts) + 1:02d}",
                scenario=state.name,
                copy_type="状态 / 反馈文案",
                semantic_goal="解释当前状态意味着什么，以及用户下一步可以做什么。",
                required_info="状态含义、原因、下一步。",
                forbidden_style="不能把处理中写成已完成，也不能把阻断写成黑盒失败。",
                direction=state.copy_feedback,
            )
        )
    return contracts


def _build_risks(facts_model: FactsModel, pages: list[PageEntry]) -> list[ExperienceRiskEntry]:
    risks: list[ExperienceRiskEntry] = []
    targets = " / ".join(page.page_id for page in pages[:3]) or "当前主页面"
    for exception in facts_model.exceptions[:3]:
        risks.append(
            ExperienceRiskEntry(
                risk_id=f"RSK-{len(risks) + 1:02d}",
                name=exception.scenario,
                trigger=exception.trigger,
                confusion=f"如果不解释 {exception.scenario}，用户会不知道当前是治理阻断还是系统异常。",
                protection=f"在 {targets} 中显式提供阻断解释、处理方向与来源追踪入口。",
                target=targets,
            )
        )
    for gap in facts_model.gaps[:2]:
        risks.append(
            ExperienceRiskEntry(
                risk_id=f"RSK-{len(risks) + 1:02d}",
                name="输入不足会影响页面承载判断",
                trigger=gap,
                confusion="用户可能会把当前页面结构误解为固定答案，而不是保守推导结果。",
                protection="在帮助与追踪承载里显式展示当前 gap 及其影响范围。",
                target=targets,
            )
        )
    return risks


def build_experience_model(project_id: str, facts_model: FactsModel, business_model: BusinessModel) -> ExperienceModel:
    principles = _build_principles(project_id, business_model)
    task_flows = _build_task_flows(facts_model)
    pages = _build_pages(task_flows, facts_model)
    key_pages = _build_key_pages(pages, facts_model)
    info_contracts = _build_info_contracts(key_pages)
    state_feedbacks = _build_state_feedbacks(facts_model, pages)
    copy_contracts = _build_copy_contracts(key_pages, state_feedbacks)
    risks = _build_risks(facts_model, pages)

    ia_entries: list[IaEntry] = []
    for index, page in enumerate(pages, start=1):
        ia_entries.append(
            IaEntry(
                ia_node=f"IA-{index:02d}",
                node_type=page.page_type,
                target_user=page.target_user,
                entry=page.entry,
                carries=page.primary_task,
                relation=page.relation,
            )
        )

    ia_diagram = "\n".join(
        [pages[0].name]
        + [f"└── {page.name}" for page in pages[1:]]
    ) if pages else "当前任务没有形成稳定页面集合，只能保守输出体验闭环。"

    flow_overview_diagram = "\n".join(
        [f"{flow.start} -> {flow.name} -> {flow.success_result} / {flow.failure_result}" for flow in task_flows]
    )

    trace_links: list[ExperienceTraceEntry] = []
    business_basis = [judgment.judgment_id for judgment in business_model.judgments[:4]] or ["POS-01"]
    fact_basis = [fact.fact_id for fact in (facts_model.action_facts + facts_model.state_facts + facts_model.rule_facts)[:6]]
    principle_basis = [principle.principle_id for principle in principles[:3]]
    for page in pages[:6]:
        trace_links.append(
            ExperienceTraceEntry(
                trace_id=f"TR-{len(trace_links) + 1:02d}",
                object_name=page.name,
                business_basis=", ".join(business_basis[:2]),
                fact_basis=", ".join(fact_basis[:3]),
                principle_basis=", ".join(principle_basis),
                note=f"{page.name} 的承载方式来自当前任务闭环，而不是预设页面骨架。",
            )
        )

    return ExperienceModel(
        project_id=project_id,
        target_users="当前任务链路中涉及的主要角色，以及需要共同评审该蓝图的设计 / 产品 / 业务角色。",
        experience_goal="把 business 的当前动态结论翻译成可读的任务闭环、页面承载、状态反馈与文案职责。",
        task_boundary="围绕当前输入推导出的主闭环、节点、页面、状态与解释责任展开，不预设固定页面集合。",
        excluded_scope="不输出高保真视觉、不直接给出前端实现、不让 preview 反向决定正式产物结构。",
        ui_boundary="当前蓝图足以支持页面承载、信息优先级、状态反馈和文案职责讨论。",
        business_basis=[business_model.final_position] + business_model.final_position_reason[:2],
        rule_basis=business_model.adopted_rules[:],
        risk_basis=[risk.name for risk in business_model.risks[:3]],
        principles=principles,
        ia_entries=ia_entries,
        ia_diagram=ia_diagram,
        task_flows=task_flows,
        flow_overview_diagram=flow_overview_diagram,
        pages=pages,
        key_pages=key_pages,
        info_contracts=info_contracts,
        state_feedbacks=state_feedbacks,
        copy_contracts=copy_contracts,
        risks=risks,
        open_questions=business_model.open_questions[:],
        gaps=business_model.gaps[:],
        trace_links=trace_links,
    )
