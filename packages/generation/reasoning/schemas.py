from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class TerminologyEntry:
    term_id: str
    term: str
    meaning: str
    boundary: str
    source: str


@dataclass(slots=True)
class ActorEntry:
    actor_id: str
    name: str
    actor_type: str
    responsibility: str
    source: str


@dataclass(slots=True)
class ObjectEntry:
    object_id: str
    name: str
    object_type: str
    description: str
    source: str


@dataclass(slots=True)
class FactEntry:
    fact_id: str
    text: str


@dataclass(slots=True)
class RuleEntry:
    rule_id: str
    name: str
    trigger: str
    subject: str
    precondition: str
    result: str
    failure: str
    source_ref: str


@dataclass(slots=True)
class StateEntry:
    state_id: str
    name: str
    enter_condition: str
    exit_condition: str
    blocking_condition: str
    description: str
    source_ref: str


@dataclass(slots=True)
class FlowEntry:
    flow_id: str
    actor: str
    action: str
    precondition: str
    result: str
    note: str
    source_ref: str


@dataclass(slots=True)
class ExceptionEntry:
    exception_id: str
    scenario: str
    trigger: str
    outcome: str
    impacted: str
    source_ref: str


@dataclass(slots=True)
class DependencyEntry:
    dependency_id: str
    name: str
    dependency_type: str
    role: str
    confidence: str
    source_ref: str


@dataclass(slots=True)
class TraceEntry:
    trace_id: str
    trace_type: str
    source_location: str
    source_file: str
    note: str


@dataclass(slots=True)
class FactsModel:
    project_id: str
    task_goal: str
    task_boundary: str
    output_purpose: str
    source_files: list[str]
    explicit_references: list[str]
    terminology: list[TerminologyEntry] = field(default_factory=list)
    actors: list[ActorEntry] = field(default_factory=list)
    objects: list[ObjectEntry] = field(default_factory=list)
    actor_facts: list[FactEntry] = field(default_factory=list)
    object_facts: list[FactEntry] = field(default_factory=list)
    state_facts: list[FactEntry] = field(default_factory=list)
    action_facts: list[FactEntry] = field(default_factory=list)
    rule_facts: list[FactEntry] = field(default_factory=list)
    exception_facts: list[FactEntry] = field(default_factory=list)
    dependency_facts: list[FactEntry] = field(default_factory=list)
    scope_facts: list[FactEntry] = field(default_factory=list)
    rules: list[RuleEntry] = field(default_factory=list)
    states: list[StateEntry] = field(default_factory=list)
    flows: list[FlowEntry] = field(default_factory=list)
    exceptions: list[ExceptionEntry] = field(default_factory=list)
    dependencies: list[DependencyEntry] = field(default_factory=list)
    in_scope: list[str] = field(default_factory=list)
    out_of_scope: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    trace_links: list[TraceEntry] = field(default_factory=list)


@dataclass(slots=True)
class JudgmentEntry:
    judgment_id: str
    title: str
    conclusion: str
    evidence: str
    comparison: str
    gap: str


@dataclass(slots=True)
class BaselineEntry:
    baseline_id: str
    text: str


@dataclass(slots=True)
class PlacementOption:
    option_id: str
    option: str
    conclusion: str
    fit_condition: str
    benefit: str
    tradeoff: str
    why_not_final: str


@dataclass(slots=True)
class RiskEntry:
    risk_id: str
    name: str
    manifestation: str
    consequence: str
    level: str
    mitigation: str


@dataclass(slots=True)
class BusinessTraceEntry:
    judgment_id: str
    section: str
    conclusion: str
    facts_basis: str
    baseline_basis: str
    comparison: str
    remaining_gap: str


@dataclass(slots=True)
class BusinessModel:
    project_id: str
    review_target: str
    review_boundary: str
    review_goal: str
    fact_links: list[str]
    change_intent: str
    change_type: str
    trigger: str
    baselines: list[BaselineEntry] = field(default_factory=list)
    judgments: list[JudgmentEntry] = field(default_factory=list)
    logic_checks: list[JudgmentEntry] = field(default_factory=list)
    strategy_checks: list[JudgmentEntry] = field(default_factory=list)
    placement_options: list[PlacementOption] = field(default_factory=list)
    final_position: str = ""
    final_position_reason: list[str] = field(default_factory=list)
    experience_constraints: list[str] = field(default_factory=list)
    adopted_rules: list[str] = field(default_factory=list)
    adopted_dependencies: list[str] = field(default_factory=list)
    value_cost_assessment: list[JudgmentEntry] = field(default_factory=list)
    risks: list[RiskEntry] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    trace_links: list[BusinessTraceEntry] = field(default_factory=list)


@dataclass(slots=True)
class PrincipleEntry:
    principle_id: str
    name: str
    reason: str
    applied_to: str


@dataclass(slots=True)
class IaEntry:
    ia_node: str
    node_type: str
    target_user: str
    entry: str
    carries: str
    relation: str


@dataclass(slots=True)
class TaskFlowEntry:
    flow_id: str
    name: str
    start: str
    key_steps: str
    key_decision: str
    success_result: str
    failure_result: str


@dataclass(slots=True)
class PageEntry:
    page_id: str
    name: str
    page_type: str
    target_user: str
    primary_task: str
    entry: str
    exit: str
    relation: str


@dataclass(slots=True)
class PageBlueprint:
    page_id: str
    name: str
    goal: str
    target_user: str
    entry_condition: str
    primary_task: str
    secondary_task: str
    first_screen_focus: str
    key_information: str
    key_actions: list[str]
    key_states: list[str]
    risks: list[str]
    relation: str
    layout_diagram: str


@dataclass(slots=True)
class InfoContractEntry:
    info_id: str
    purpose: str
    priority: str
    placement: str
    trigger: str
    hidden_risk: str


@dataclass(slots=True)
class StateFeedbackEntry:
    state_id: str
    name: str
    trigger: str
    available_actions: str
    page_feedback: str
    copy_feedback: str
    downstream: str


@dataclass(slots=True)
class CopyEntry:
    copy_id: str
    scenario: str
    copy_type: str
    semantic_goal: str
    required_info: str
    forbidden_style: str
    direction: str


@dataclass(slots=True)
class ExperienceRiskEntry:
    risk_id: str
    name: str
    trigger: str
    confusion: str
    protection: str
    target: str


@dataclass(slots=True)
class ExperienceTraceEntry:
    trace_id: str
    object_name: str
    business_basis: str
    fact_basis: str
    principle_basis: str
    note: str


@dataclass(slots=True)
class ExperienceModel:
    project_id: str
    target_users: str
    experience_goal: str
    task_boundary: str
    excluded_scope: str
    ui_boundary: str
    business_basis: list[str] = field(default_factory=list)
    rule_basis: list[str] = field(default_factory=list)
    risk_basis: list[str] = field(default_factory=list)
    principles: list[PrincipleEntry] = field(default_factory=list)
    ia_entries: list[IaEntry] = field(default_factory=list)
    ia_diagram: str = ""
    task_flows: list[TaskFlowEntry] = field(default_factory=list)
    flow_overview_diagram: str = ""
    pages: list[PageEntry] = field(default_factory=list)
    key_pages: list[PageBlueprint] = field(default_factory=list)
    info_contracts: list[InfoContractEntry] = field(default_factory=list)
    state_feedbacks: list[StateFeedbackEntry] = field(default_factory=list)
    copy_contracts: list[CopyEntry] = field(default_factory=list)
    risks: list[ExperienceRiskEntry] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    trace_links: list[ExperienceTraceEntry] = field(default_factory=list)
