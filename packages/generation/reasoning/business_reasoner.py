from __future__ import annotations

import re

from .knowledge_loader import load_knowledge_notes
from .schemas import (
    BaselineEntry,
    BusinessModel,
    BusinessTraceEntry,
    FactsModel,
    JudgmentEntry,
    PlacementOption,
    RiskEntry,
)


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    results: list[str] = []
    for value in values:
        cleaned = re.sub(r"\s+", " ", value).strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        results.append(cleaned)
    return results


def _fact_ids(facts_model: FactsModel) -> list[str]:
    entries = (
        facts_model.actor_facts
        + facts_model.object_facts
        + facts_model.state_facts
        + facts_model.action_facts
        + facts_model.rule_facts
        + facts_model.exception_facts
        + facts_model.dependency_facts
        + facts_model.scope_facts
    )
    return [item.fact_id for item in entries[:12]]


def _derive_change_type(facts_model: FactsModel) -> str:
    text = " ".join([facts_model.task_goal, facts_model.task_scenario] + [unit.text for unit in facts_model.evidence_units[:20]])
    if any(token in text for token in ("新增", "建立", "创建", "引入")):
        return "新增能力 / 引入新机制"
    if any(token in text for token in ("重构", "改造", "升级")):
        return "内部重构 / 生成机制升级"
    if any(token in text for token in ("优化", "收敛", "调整")):
        return "优化 / 收敛 / 调整"
    return "当前输入驱动的能力调整"


def _knowledge_overlap(facts_model: FactsModel, notes: list[object]) -> list[str]:
    corpus = " ".join(
        [facts_model.task_goal, facts_model.task_scenario]
        + [actor.name for actor in facts_model.actors]
        + [obj.name for obj in facts_model.objects]
        + [unit.text for unit in facts_model.evidence_units[:25]]
    )
    hits: list[str] = []
    for note in notes:
        if note.title in corpus or any(signal and signal[:8] in corpus for signal in note.signals):
            hits.append(f"{note.note_id} {note.title}")
        elif note.kind in {"wiki", "business"}:
            hits.append(f"{note.note_id} {note.title}")
    return hits[:8]


def _build_baselines(notes: list[object], facts_model: FactsModel) -> list[BaselineEntry]:
    baselines: list[BaselineEntry] = []
    for note in notes:
        if note.kind not in {"wiki", "business", "knowledge", "raw"}:
            continue
        signal = note.signals[0] if note.signals else note.summary
        baselines.append(
            BaselineEntry(
                baseline_id=f"BL-{len(baselines) + 1:02d}",
                text=f"{note.title}：{signal}",
                source_refs=[note.note_id, note.path],
            )
        )
        if len(baselines) >= 5:
            break
    if facts_model.rules:
        baselines.append(
            BaselineEntry(
                baseline_id=f"BL-{len(baselines) + 1:02d}",
                text="当前任务至少存在规则、依赖或异常证据，业务判断必须把治理边界纳入主链路。",
                source_refs=[facts_model.rules[0].source_ref],
            )
        )
    if facts_model.states:
        baselines.append(
            BaselineEntry(
                baseline_id=f"BL-{len(baselines) + 1:02d}",
                text="当前任务不是静态说明，而是包含状态变化与结果反馈的动态链路。",
                source_refs=[facts_model.states[0].source_ref],
            )
        )
    return baselines[:6]


def _build_dynamic_judgments(facts_model: FactsModel, baselines: list[BaselineEntry], knowledge_hits: list[str]) -> list[JudgmentEntry]:
    judgments: list[JudgmentEntry] = []
    if facts_model.task_goal:
        judgments.append(
            JudgmentEntry(
                judgment_id=f"J-{len(judgments) + 1:02d}",
                title="问题与意图是否足以支撑当前改造",
                conclusion="成立" if len(facts_model.gaps) <= 3 else "部分成立",
                evidence=f"task_goal={facts_model.task_goal}; facts={', '.join(_fact_ids(facts_model)[:4])}",
                comparison="若问题与意图不清晰，结论容易停留在表层描述，难以形成稳定业务判断。",
                gap=facts_model.gaps[0] if facts_model.gaps else "当前意图层证据基本可用。",
            )
        )
    if baselines:
        judgments.append(
            JudgmentEntry(
                judgment_id=f"J-{len(judgments) + 1:02d}",
                title="当前输入与命中知识是否形成稳定基线",
                conclusion="较稳定" if knowledge_hits else "偏弱",
                evidence=f"knowledge={'; '.join(knowledge_hits[:3]) or '无稳定命中'}",
                comparison="没有知识基线时，业务判断只能停留在输入表层，难以形成领域立场。",
                gap=facts_model.gaps[0] if facts_model.gaps else "知识基线可参与当前判断。",
            )
        )
    if facts_model.rules or facts_model.dependencies:
        judgments.append(
            JudgmentEntry(
                judgment_id=f"J-{len(judgments) + 1:02d}",
                title="治理与依赖是否已经进入判断链",
                conclusion="是" if facts_model.rules and facts_model.dependencies else "部分进入",
                evidence=f"rules={len(facts_model.rules)}; dependencies={len(facts_model.dependencies)}; exceptions={len(facts_model.exceptions)}",
                comparison="若只描述结果、不承接规则与依赖，后续设计难以明确哪些地方不能随便放开。",
                gap="缺少依赖或异常证据时，需要把不确定性保留到 gaps 中。",
            )
        )
    if facts_model.states or facts_model.exceptions:
        judgments.append(
            JudgmentEntry(
                judgment_id=f"J-{len(judgments) + 1:02d}",
                title="状态、结果与异常是否形成闭环",
                conclusion="形成闭环" if facts_model.states and facts_model.exceptions else "闭环偏弱",
                evidence=f"states={len(facts_model.states)}; exceptions={len(facts_model.exceptions)}",
                comparison="如果没有状态与异常闭环，方案容易停留在静态说明，无法形成完整任务流程。",
                gap=facts_model.gaps[1] if len(facts_model.gaps) > 1 else "状态与异常仍需随真实输入继续细化。",
            )
        )
    if facts_model.gaps:
        judgments.append(
            JudgmentEntry(
                judgment_id=f"J-{len(judgments) + 1:02d}",
                title="信息充分性是否足够下最终立场",
                conclusion="可下保守立场" if len(facts_model.gaps) <= 2 else "需要保守收敛",
                evidence=f"gaps={'; '.join(facts_model.gaps[:2])}",
                comparison="信息不足时允许结论更保守，但仍需保持可追溯的当前任务判断。",
                gap=facts_model.gaps[0],
            )
        )
    return judgments


def _score_options(facts_model: FactsModel, change_type: str) -> list[PlacementOption]:
    candidate_specs = [
        ("独立成型能力", "适合对象、规则、状态和输出结构都需要单独建模时", "边界清晰，便于持续迭代", "模块数量与建模成本会上升"),
        ("并入既有能力结构", "适合当前变化更像既有能力增强而不是新能力时", "沿用现有入口，使用和维护成本更低", "如果边界没写清楚，容易和现有能力混在一起"),
        ("收敛为规则 / 配置层", "适合动作较少、规则较多、更多是边界治理时", "可以降低页面与流程复杂度", "表达力可能不足，体验层承载空间变小"),
        ("暂不下最终立场", "适合信息缺口较多、知识命中较弱时", "避免过早定论", "短期无法给出强推进结论"),
    ]
    scores = {spec[0]: 0 for spec in candidate_specs}
    if "新增" in change_type:
        scores["独立成型能力"] += 2
    if "重构" in change_type or "升级" in change_type:
        scores["并入既有能力结构"] += 2
    if len(facts_model.objects) >= 3 or len(facts_model.flows) >= 2:
        scores["独立成型能力"] += 2
    if len(facts_model.rules) >= len(facts_model.action_facts) and len(facts_model.action_facts) <= 2:
        scores["收敛为规则 / 配置层"] += 2
    if len(facts_model.gaps) >= 3:
        scores["暂不下最终立场"] += 3
    if not facts_model.action_facts:
        scores["暂不下最终立场"] += 2
        scores["收敛为规则 / 配置层"] += 1
    scores["并入既有能力结构"] += 1

    ranked = sorted(candidate_specs, key=lambda item: scores[item[0]], reverse=True)
    options: list[PlacementOption] = []
    best_name = ranked[0][0]
    for index, (name, fit_condition, benefit, tradeoff) in enumerate(ranked[:4], start=1):
        options.append(
            PlacementOption(
                option_id=f"OPT-{index:02d}",
                option=name,
                conclusion="当前最优" if name == best_name else "可对照方案",
                fit_condition=fit_condition,
                benefit=benefit,
                tradeoff=tradeoff,
                why_not_final="当前证据更支持其它路径。" if name != best_name else "当前输入、知识基线和闭环结构都更支持这个方案。",
            )
        )
    return options


def _final_position_from_options(options: list[PlacementOption], facts_model: FactsModel) -> tuple[str, list[str]]:
    best = options[0]
    if best.option == "暂不下最终立场":
        return (
            "事实不足，当前只适合输出保守判断，不适合写死强立场。",
            [
                "当前 gaps 较多，强行给出肯定结论会放大误判风险。",
                "在信息补足前，应保留问题、风险和约束，避免过早定死方向。",
            ],
        )
    return (
        f"当前更适合定位为“{best.option}”。",
        [
            f"本次调整类型更接近：{_derive_change_type(facts_model)}。",
            f"现有对象数={len(facts_model.objects)}、流程数={len(facts_model.flows)}、规则数={len(facts_model.rules)}，说明这次需求需要完整方案承接。",
            "命中知识已经参与基线建立与路径比较，因此结论具备当前任务语境下的可解释性。",
        ],
    )


def _build_handover_requirements(
    facts_model: FactsModel,
    placement_options: list[PlacementOption],
    risks: list[RiskEntry],
) -> list[str]:
    role_names = _dedupe_strings([item.name for item in facts_model.actors[:6]])
    flow_lines = _dedupe_strings([f"{item.actor} -> {item.action} -> {item.result}" for item in facts_model.flows[:5]])
    secondary_flows = _dedupe_strings([f"{item.actor}：{item.action}" for item in facts_model.flows[5:8]])
    exception_lines = _dedupe_strings([item.outcome for item in facts_model.exceptions[:5]])
    state_lines = _dedupe_strings([f"{item.name}：{item.description}" for item in facts_model.states[:5]])
    pre_info = _dedupe_strings([item.name for item in facts_model.dependencies[:5]] + [item.name for item in facts_model.rules[:3]])
    record_lines = _dedupe_strings([item.name for item in facts_model.objects[:5]])
    risk_lines = _dedupe_strings([f"{item.name}（{item.level}）" for item in risks[:5]])
    suggest_lines = _dedupe_strings(
        [
            f"优先按“{placement_options[0].option}”组织承载路径，避免并行堆叠多个入口。"
            if placement_options
            else "当前能力形态未稳定，建议先按最小闭环拆解。"
        ]
    )
    pending_lines = _dedupe_strings(facts_model.open_questions[:3] + facts_model.gaps[:3])

    def _line(prefix: str, values: list[str], fallback: str) -> str:
        return f"{prefix}：{('；'.join(values[:3])) if values else fallback}"

    return [
        _line("必须覆盖的角色", role_names, "当前输入尚未明确完整角色，需先确认"),
        _line("必须闭环的主流程", flow_lines, "当前输入流程事实不足，需补齐主流程"),
        _line("必须补充的次流程", secondary_flows, "需补齐撤回、重试、查看记录等次流程"),
        _line("必须处理的异常", exception_lines, "至少覆盖失败、阻断、权限不足等异常"),
        _line("必须解释的状态", state_lines, "至少解释处理中、成功、失败等关键状态"),
        _line("必须前置的信息", pre_info, "需在入口或关键节点前置说明规则与依赖"),
        _line("必须沉淀的记录", record_lines, "需沉淀申请、审批、结果、异常处理记录"),
        _line("必须保护的风险", risk_lines, "需给出范围控制、二次确认和失败解释策略"),
        _line("可作为设计建议补齐的内容", suggest_lines, "可补充帮助入口、文案策略和解释提示"),
        _line("必须待确认的问题", pending_lines, "当前暂无显式待确认项，需在评审中再次确认"),
    ]


def build_business_model(project_id: str, facts_model: FactsModel) -> BusinessModel:
    notes = load_knowledge_notes(project_id, stage="business") or facts_model.knowledge_notes
    fact_links = _fact_ids(facts_model)
    knowledge_hits = _knowledge_overlap(facts_model, notes)
    baselines = _build_baselines(notes, facts_model)
    judgments = _build_dynamic_judgments(facts_model, baselines, knowledge_hits)
    placement_options = _score_options(facts_model, _derive_change_type(facts_model))
    final_position, final_position_reason = _final_position_from_options(placement_options, facts_model)

    adopted_rules = [f"{rule.rule_id}: {rule.name} -> {rule.result}" for rule in facts_model.rules[:4]]
    adopted_dependencies = [f"{dep.dependency_id}: {dep.name} -> {dep.role}" for dep in facts_model.dependencies[:4]]
    risks: list[RiskEntry] = []
    for gap in facts_model.gaps[:3]:
        risks.append(
            RiskEntry(
                risk_id=f"RSK-{len(risks) + 1:02d}",
                name="信息缺口会让业务结论失稳",
                manifestation=gap,
                consequence="如果信息还不够就强行定方案，后续判断容易失真并带来误判。",
                level="高" if len(facts_model.gaps) >= 3 else "中",
                mitigation="保留缺口并给出谨慎建议，先说明适用范围、限制条件和后续补齐项。",
            )
        )
    for exception in facts_model.exceptions[:2]:
        risks.append(
            RiskEntry(
                risk_id=f"RSK-{len(risks) + 1:02d}",
                name="异常或阻断未被业务层接住",
                manifestation=exception.outcome,
                consequence="体验设计可能无法清楚说明失败原因、处理方式和下一步。",
                level="中",
                mitigation="把异常条件写进业务判断，并在后续设计中明确失败提示和处理路径。",
            )
        )

    experience_constraints = _build_handover_requirements(facts_model, placement_options, risks)
    trace_links: list[BusinessTraceEntry] = []
    for judgment in judgments:
        trace_links.append(
            BusinessTraceEntry(
                judgment_id=judgment.judgment_id,
                section=judgment.title,
                conclusion=judgment.conclusion,
                facts_basis=", ".join(fact_links[:4]),
                baseline_basis=", ".join(item.baseline_id for item in baselines[:3]),
                comparison=", ".join(item.option_id for item in placement_options[:2]),
                remaining_gap=judgment.gap,
            )
        )

    return BusinessModel(
        project_id=project_id,
        review_target="当前任务要求形成的业务能力与其承载方式，不预设固定结论。",
        review_boundary="本次只评审当前输入能否支撑稳定的业务立场，以及知识如何影响这个立场。",
        review_goal="先完成业务判断，再沉淀业务蓝图，让 business blueprint 成为当前任务的可读结论与承接输入。",
        fact_links=fact_links,
        knowledge_hits=knowledge_hits,
        problem_statement=facts_model.task_scenario,
        change_intent=facts_model.task_goal,
        change_type=_derive_change_type(facts_model),
        trigger="当前任务需要同时给出可读结论和可追溯依据，并保持与输入事实一致。",
        baselines=baselines,
        judgments=judgments,
        placement_options=placement_options,
        final_position=final_position,
        final_position_reason=final_position_reason,
        experience_constraints=experience_constraints,
        adopted_rules=adopted_rules,
        adopted_dependencies=adopted_dependencies,
        risks=risks,
        open_questions=facts_model.open_questions[:],
        gaps=facts_model.gaps[:],
        trace_links=trace_links,
    )
