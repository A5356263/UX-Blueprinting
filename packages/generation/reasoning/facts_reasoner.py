from __future__ import annotations

import json
import re
from pathlib import Path

from packages.common import get_project_runtime_dir, get_project_source_dir

from .knowledge_loader import load_knowledge_notes
from .schemas import (
    ActorEntry,
    DependencyEntry,
    EvidenceUnit,
    ExceptionEntry,
    FactEntry,
    FactsModel,
    FlowEntry,
    KnowledgeNote,
    ObjectEntry,
    RuleEntry,
    StateEntry,
    TerminologyEntry,
    TraceEntry,
)


HEADING_RE = re.compile(r"^(#+)\s+(.+?)\s*$")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s+(.*)$")
ROLE_PATTERN = re.compile(r"[A-Za-z0-9_\-\u4e00-\u9fff]{1,20}(?:用户|人员|成员|管理员|审批人|负责人|团队|角色|系统|设计师|产品经理|运营|开发|评审方|管理方|协作方)")
OBJECT_PATTERN = re.compile(r"[A-Za-z0-9_\-\u4e00-\u9fff]{1,24}(?:页面|能力|流程|规则|状态|任务|模板|蓝图|文档|配置|结果|记录|权限|模块|知识库|索引|摘要|产物|窗口)")
RULE_WORDS = ("必须", "不能", "禁止", "不得", "需要", "应", "校验", "约束", "限制", "应当")
STATE_WORDS = ("状态", "成功", "失败", "处理中", "待", "完成", "启用", "禁用", "关闭", "打开", "阻断")
ACTION_WORDS = ("生成", "创建", "提交", "查看", "配置", "编辑", "选择", "调整", "触发", "运行", "同步", "输出", "引用", "读取", "装配")
EXCEPTION_WORDS = ("失败", "异常", "阻断", "冲突", "报错", "警告", "中断", "缺失")
DEPENDENCY_WORDS = ("依赖", "基于", "读取", "引用", "使用", "命中", "需要", "装配", "上下文", "知识库", "wiki", "guideline")
SCOPE_IN_WORDS = ("本次", "覆盖", "包含", "聚焦", "范围")
SCOPE_OUT_WORDS = ("不覆盖", "不包含", "暂不", "非范围", "不展开")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _normalize_line(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip(" -\t")


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _runtime_contract_paths(project_id: str) -> dict[str, Path]:
    runtime_dir = get_project_runtime_dir(project_id)
    return {
        "resolved": runtime_dir / "task_card_resolved.json",
        "manifest": runtime_dir / "context_manifest.json",
    }


def _fallback_task_card_path(project_id: str) -> Path:
    return get_project_source_dir(project_id) / "task_card.md"


def _source_paths(project_id: str) -> list[Path]:
    source_dir = get_project_source_dir(project_id)
    return [
        source_dir / "requirement.md",
        source_dir / "background.md",
    ]


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_normalize_line(item) for item in value if isinstance(item, str) and _normalize_line(item)]


def _prefer_string_list(*values: object) -> list[str]:
    for value in values:
        items = _string_list(value)
        if items:
            return items
    return []


def _classify_line(text: str) -> list[str]:
    categories: list[str] = []
    if any(word in text for word in RULE_WORDS):
        categories.append("rule")
    if any(word in text for word in STATE_WORDS):
        categories.append("state")
    if any(word in text for word in ACTION_WORDS):
        categories.append("action")
    if any(word in text for word in EXCEPTION_WORDS):
        categories.append("exception")
    if any(word in text for word in DEPENDENCY_WORDS):
        categories.append("dependency")
    if any(word in text for word in SCOPE_IN_WORDS + SCOPE_OUT_WORDS):
        categories.append("scope")
    if ROLE_PATTERN.search(text):
        categories.append("actor")
    if OBJECT_PATTERN.search(text):
        categories.append("object")
    return sorted(set(categories))


def _extract_candidates(pattern: re.Pattern[str], text: str) -> list[str]:
    seen: set[str] = set()
    results: list[str] = []
    for match in pattern.findall(text):
        normalized = str(match).strip("，。；：、 ")
        if len(normalized) < 2 or normalized in seen:
            continue
        seen.add(normalized)
        results.append(normalized)
    return results


def _parse_task_card_sections(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    sections: dict[str, list[str]] = {}
    current_heading = ""
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.rstrip()
        heading_match = HEADING_RE.match(stripped.strip())
        if heading_match and len(heading_match.group(1)) == 2:
            current_heading = heading_match.group(2).strip()
            sections.setdefault(current_heading, [])
            continue
        list_match = LIST_ITEM_RE.match(stripped)
        if not current_heading or not list_match:
            continue
        text = _normalize_line(list_match.group(1))
        if text:
            sections.setdefault(current_heading, []).append(text)
    return sections


def _load_runtime_contract_context(project_id: str) -> dict[str, object]:
    contract_paths = _runtime_contract_paths(project_id)
    resolved = _read_json(contract_paths["resolved"])
    manifest = _read_json(contract_paths["manifest"])
    task_contract = manifest.get("task_contract")
    manifest_contract = task_contract if isinstance(task_contract, dict) else {}
    fallback_path = _fallback_task_card_path(project_id)
    fallback_sections = _parse_task_card_sections(fallback_path)
    contract_sources = [
        str(path).replace("\\", "/")
        for path in (contract_paths["resolved"], contract_paths["manifest"])
        if path.exists()
    ]
    return {
        "task_goal": _prefer_string_list(
            resolved.get("task_goal"),
            manifest_contract.get("task_goal"),
            fallback_sections.get("Task Goal"),
        ),
        "task_scenario": _prefer_string_list(
            resolved.get("task_scenario"),
            manifest_contract.get("task_scenario"),
            fallback_sections.get("Task Scenario"),
        ),
        "execution_constraints": _prefer_string_list(
            resolved.get("execution_constraints"),
            manifest_contract.get("execution_constraints"),
            fallback_sections.get("Constraints"),
        ),
        "read_order": _prefer_string_list(
            resolved.get("read_order"),
            manifest_contract.get("read_order"),
            fallback_sections.get("Read Order"),
        ),
        "notes": _prefer_string_list(
            resolved.get("notes"),
            manifest_contract.get("notes"),
            fallback_sections.get("Notes"),
        ),
        "contract_sources": contract_sources,
        "fallback_task_card": str(fallback_path).replace("\\", "/") if fallback_path.exists() else "",
    }


def _build_business_evidence_units(project_id: str) -> list[EvidenceUnit]:
    units: list[EvidenceUnit] = []
    counter = 1
    source_paths = list(_source_paths(project_id))
    for path in source_paths:
        if not path.exists():
            continue
        heading_stack: list[str] = []
        for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = raw_line.rstrip()
            heading_match = HEADING_RE.match(stripped.strip())
            if heading_match:
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()
                heading_stack = heading_stack[: level - 1]
                heading_stack.append(heading_text)
                continue
            text = _normalize_line(stripped)
            if len(text) < 8:
                continue
            units.append(
                EvidenceUnit(
                    evidence_id=f"EV-{counter:03d}",
                    text=text,
                    source_file=str(path).replace("\\", "/"),
                    heading=" / ".join(heading_stack),
                    line_no=line_no,
                    categories=_classify_line(text),
                    actor_candidates=_extract_candidates(ROLE_PATTERN, text),
                    object_candidates=_extract_candidates(OBJECT_PATTERN, text),
                )
            )
            counter += 1
    return units


def _build_evidence_units(project_id: str) -> list[EvidenceUnit]:
    return _build_business_evidence_units(project_id)


def _find_first_line(units: list[EvidenceUnit], keywords: tuple[str, ...], fallback: str) -> str:
    for unit in units:
        if any(keyword in unit.text for keyword in keywords):
            return unit.text
    return fallback


def _first_nonempty(values: list[str]) -> str:
    for value in values:
        text = _normalize_line(value)
        if text:
            return text
    return ""


def _pick_units(units: list[EvidenceUnit], category: str, limit: int) -> list[EvidenceUnit]:
    return [unit for unit in units if category in unit.categories][:limit]


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


def _derive_task_goal(contract_context: dict[str, object], business_units: list[EvidenceUnit]) -> str:
    goal = _first_nonempty(contract_context.get("task_goal", []))
    if goal:
        return goal
    return _find_first_line(
        business_units,
        ("目标", "解决", "优化", "提升", "改成", "推理"),
        "当前任务需要先澄清真实需求，再为后续业务判断与体验转译提供可追溯事实。",
    )


def _derive_task_scenario(contract_context: dict[str, object], business_units: list[EvidenceUnit]) -> str:
    scenario = _first_nonempty(contract_context.get("task_scenario", []))
    if scenario:
        return scenario
    return _find_first_line(
        business_units,
        ("场景", "背景", "当前", "流程"),
        "当前任务属于基于 requirement/background 进行事实抽取与边界澄清的场景。",
    )


def _derive_task_boundary(contract_context: dict[str, object], business_units: list[EvidenceUnit]) -> str:
    for candidate in list(contract_context.get("execution_constraints", [])) + list(contract_context.get("notes", [])):
        text = _normalize_line(candidate)
        if text:
            return text
    return _find_first_line(
        business_units,
        ("边界", "范围", "仅", "不覆盖", "不包含"),
        "facts 只抽取 requirement.md 与 background.md 中的真实业务事实，任务合同仅用于说明边界。",
    )


def _build_constraints(contract_context: dict[str, object]) -> list[str]:
    constraints = [f"C-{index:02d}: {item}" for index, item in enumerate(list(contract_context.get("execution_constraints", []))[:6], start=1)]
    if constraints:
        return constraints
    return [
        "C-01: facts 以 requirement.md 与 background.md 为业务事实主来源。",
        "C-02: wiki 只做术语与边界校准，不替代当前任务事实。",
    ]


def _build_actors(units: list[EvidenceUnit]) -> list[ActorEntry]:
    candidates = _dedupe_strings([item for unit in units for item in unit.actor_candidates])
    actors: list[ActorEntry] = []
    for index, name in enumerate(candidates[:6], start=1):
        source_unit = next(unit for unit in units if name in unit.actor_candidates)
        actors.append(
            ActorEntry(
                actor_id=f"A-{index:02d}",
                name=name,
                actor_type="任务相关角色",
                responsibility=source_unit.text,
                source=source_unit.source_file,
            )
        )
    if not actors:
        actors.append(
            ActorEntry(
                actor_id="A-01",
                name="当前任务评审角色",
                actor_type="任务相关角色",
                responsibility="当前输入没有提取到稳定角色，因此需要由任务相关角色共同评审和补充边界。",
                source=f"projects/{units[0].source_file.split('projects/', 1)[-1]}" if units else "source",
            )
        )
    return actors


def _build_objects(units: list[EvidenceUnit]) -> list[ObjectEntry]:
    candidates = _dedupe_strings([item for unit in units for item in unit.object_candidates])
    objects: list[ObjectEntry] = []
    for index, name in enumerate(candidates[:8], start=1):
        source_unit = next(unit for unit in units if name in unit.object_candidates)
        objects.append(
            ObjectEntry(
                object_id=f"O-{index:02d}",
                name=name,
                object_type="任务相关对象",
                description=source_unit.text,
                source=source_unit.source_file,
            )
        )
    if not objects:
        objects.append(
            ObjectEntry(
                object_id="O-01",
                name="当前任务对象",
                object_type="任务相关对象",
                description="当前输入没有提取到稳定对象，因此先以当前任务对象作为保守建模承接点。",
                source=units[0].source_file if units else "source",
            )
        )
    return objects


def _build_terminology(objects: list[ObjectEntry], knowledge_notes: list[KnowledgeNote]) -> list[TerminologyEntry]:
    entries: list[TerminologyEntry] = []
    for index, obj in enumerate(objects[:4], start=1):
        entries.append(
            TerminologyEntry(
                term_id=f"T-{index:02d}",
                term=obj.name,
                meaning=obj.description,
                boundary="当前任务中的直接承接对象，需要与其上下游关系分开理解。",
                source=obj.source,
            )
        )
    for note in knowledge_notes[:2]:
        entries.append(
            TerminologyEntry(
                term_id=f"T-{len(entries) + 1:02d}",
                term=note.title,
                meaning=note.summary,
                boundary="来自命中知识，只用于校准当前任务的术语边界。",
                source=note.path,
            )
        )
    return entries


def _build_fact_entries(units: list[EvidenceUnit], category: str, prefix: str, limit: int) -> list[FactEntry]:
    entries: list[FactEntry] = []
    for index, unit in enumerate(_pick_units(units, category, limit), start=1):
        entries.append(FactEntry(f"{prefix}{index:02d}", unit.text, unit.evidence_id))
    return entries


def _state_name_from_text(text: str, fallback: str) -> str:
    for candidate in ("处理中", "成功", "失败", "阻断", "启用", "禁用", "完成", "待处理", "关闭", "打开", "待补充"):
        if candidate in text:
            return candidate
    return fallback


def _build_rules(rule_units: list[EvidenceUnit], objects: list[ObjectEntry], exception_units: list[EvidenceUnit]) -> list[RuleEntry]:
    rules: list[RuleEntry] = []
    for index, unit in enumerate(rule_units[:6], start=1):
        related_object = unit.object_candidates[0] if unit.object_candidates else objects[0].name
        failure = exception_units[index - 1].text if index - 1 < len(exception_units) else "命中限制条件时进入阻断或补充说明链路。"
        name_source = unit.heading.split("/")[-1].strip() if unit.heading else unit.text[:10]
        rules.append(
            RuleEntry(
                rule_id=f"R-{index:02d}",
                name=f"{name_source}规则",
                trigger=unit.heading or "命中当前输入中的限制条件",
                subject=related_object,
                precondition="当前证据中涉及的前置条件成立后才可继续执行。",
                result=unit.text,
                failure=failure,
                source_ref=unit.evidence_id,
            )
        )
    return rules


def _build_states(state_units: list[EvidenceUnit]) -> list[StateEntry]:
    states: list[StateEntry] = []
    seen_names: set[str] = set()
    for unit in state_units[:6]:
        name = _state_name_from_text(unit.text, f"状态{len(states) + 1}")
        if name in seen_names:
            continue
        seen_names.add(name)
        states.append(
            StateEntry(
                state_id=f"S-{len(states) + 1:02d}",
                name=name,
                enter_condition=unit.heading or "进入当前链路时",
                exit_condition="完成当前状态对应的动作或进入下一个结果态。",
                blocking_condition="命中当前证据中的限制、异常或依赖缺失时进入阻断。",
                description=unit.text,
                source_ref=unit.evidence_id,
            )
        )
    return states


def _action_phrase(text: str) -> str:
    for word in ACTION_WORDS:
        if word in text:
            return word
    return "处理"


def _build_flows(action_units: list[EvidenceUnit], actors: list[ActorEntry], objects: list[ObjectEntry]) -> list[FlowEntry]:
    flows: list[FlowEntry] = []
    for unit in action_units[:6]:
        actor = unit.actor_candidates[0] if unit.actor_candidates else actors[0].name
        obj = unit.object_candidates[0] if unit.object_candidates else objects[0].name
        flows.append(
            FlowEntry(
                flow_id=f"FL-{len(flows) + 1:02d}",
                actor=actor,
                action=f"{_action_phrase(unit.text)} {obj}",
                precondition=unit.heading or "具备当前输入中描述的前置条件。",
                result=unit.text,
                note=f"从当前输入直接抽取，未做模板补全：{unit.evidence_id}",
                source_ref=unit.evidence_id,
            )
        )
    return flows


def _build_exceptions(exception_units: list[EvidenceUnit], actors: list[ActorEntry]) -> list[ExceptionEntry]:
    exceptions: list[ExceptionEntry] = []
    impacted_default = actors[0].name
    for unit in exception_units[:6]:
        exceptions.append(
            ExceptionEntry(
                exception_id=f"EX-{len(exceptions) + 1:02d}",
                scenario=_state_name_from_text(unit.text, f"异常场景{len(exceptions) + 1}"),
                trigger=unit.heading or "命中失败、异常、冲突或阻断条件",
                outcome=unit.text,
                impacted=unit.actor_candidates[0] if unit.actor_candidates else impacted_default,
                source_ref=unit.evidence_id,
            )
        )
    return exceptions


def _build_dependencies(dep_units: list[EvidenceUnit]) -> list[DependencyEntry]:
    dependencies: list[DependencyEntry] = []
    for unit in dep_units[:6]:
        name = unit.object_candidates[0] if unit.object_candidates else unit.text[:20]
        dep_type = "知识 / 上下文 / 外部依赖" if ("知识" in unit.text or "wiki" in unit.text.lower()) else "任务依赖"
        dependencies.append(
            DependencyEntry(
                dependency_id=f"DEP-{len(dependencies) + 1:02d}",
                name=name,
                dependency_type=dep_type,
                role=unit.text,
                confidence="显式提及" if ("依赖" in unit.text or "引用" in unit.text) else "推断",
                source_ref=unit.evidence_id,
            )
        )
    return dependencies


def _scope_lists(scope_units: list[EvidenceUnit]) -> tuple[list[str], list[str]]:
    in_scope: list[str] = []
    out_scope: list[str] = []
    for unit in scope_units:
        if any(token in unit.text for token in SCOPE_OUT_WORDS):
            out_scope.append(f"OUT-{len(out_scope) + 1:02d}: {unit.text}")
        else:
            in_scope.append(f"IN-{len(in_scope) + 1:02d}: {unit.text}")
    return in_scope[:6], out_scope[:6]


def _build_trace_links(units: list[EvidenceUnit], fact_entries: list[FactEntry]) -> list[TraceEntry]:
    unit_map = {unit.evidence_id: unit for unit in units}
    traces: list[TraceEntry] = []
    for entry in fact_entries[:16]:
        unit = unit_map.get(entry.source_ref)
        if unit is None:
            continue
        traces.append(
            TraceEntry(
                trace_id=entry.fact_id,
                trace_type="fact",
                source_location=f"{unit.heading or '正文'}:{unit.line_no}",
                source_file=unit.source_file,
                note=unit.text,
            )
        )
    return traces


def build_facts_model(project_id: str) -> FactsModel:
    evidence_units = _build_evidence_units(project_id)
    knowledge_notes = load_knowledge_notes(project_id, stage="facts")
    contract_context = _load_runtime_contract_context(project_id)

    task_goal = _derive_task_goal(contract_context, evidence_units)
    task_boundary = _derive_task_boundary(contract_context, evidence_units)
    task_scenario = _derive_task_scenario(contract_context, evidence_units)

    actors = _build_actors(evidence_units)
    objects = _build_objects(evidence_units)
    terminology = _build_terminology(objects, knowledge_notes)

    actor_facts = _build_fact_entries(evidence_units, "actor", "F-A", 8)
    object_facts = _build_fact_entries(evidence_units, "object", "F-O", 8)
    state_facts = _build_fact_entries(evidence_units, "state", "F-S", 8)
    action_facts = _build_fact_entries(evidence_units, "action", "F-AC", 8)
    rule_facts = _build_fact_entries(evidence_units, "rule", "F-R", 8)
    exception_facts = _build_fact_entries(evidence_units, "exception", "F-E", 8)
    dependency_facts = _build_fact_entries(evidence_units, "dependency", "F-D", 8)
    scope_facts = _build_fact_entries(evidence_units, "scope", "F-SC", 8)

    rules = _build_rules(_pick_units(evidence_units, "rule", 8), objects, _pick_units(evidence_units, "exception", 8))
    states = _build_states(_pick_units(evidence_units, "state", 8))
    flows = _build_flows(_pick_units(evidence_units, "action", 8), actors, objects)
    exceptions = _build_exceptions(_pick_units(evidence_units, "exception", 8), actors)
    dependencies = _build_dependencies(_pick_units(evidence_units, "dependency", 8))
    in_scope, out_of_scope = _scope_lists(_pick_units(evidence_units, "scope", 12))

    open_questions: list[str] = []
    gaps: list[str] = []
    for unit in evidence_units:
        if any(token in unit.text for token in ("待确认", "仍待", "尚未明确", "还需确认")):
            open_questions.append(f"OQ-{len(open_questions) + 1:02d}: {unit.text}")
        if any(token in unit.text for token in ("GAP", "缺口", "不足", "缺失", "未覆盖")):
            gaps.append(f"GAP-{len(gaps) + 1:02d}: {unit.text}")

    if not knowledge_notes:
        gaps.append(f"GAP-{len(gaps) + 1:02d}: 当前没有读取到可用的显式知识引用，当前只能依赖 source 输入做保守推断。")
    if not contract_context.get("contract_sources"):
        fallback_task_card = str(contract_context.get("fallback_task_card", ""))
        if fallback_task_card:
            gaps.append(f"GAP-{len(gaps) + 1:02d}: Runtime 合同缺失，当前仅用 task_card.md 回填任务说明，业务事实仍只来自 requirement/background。")
        else:
            gaps.append(f"GAP-{len(gaps) + 1:02d}: Runtime 合同缺失，当前任务意图与边界只能基于已有输入做保守整理。")

    constraints = _build_constraints(contract_context)

    all_fact_entries = actor_facts + object_facts + state_facts + action_facts + rule_facts + exception_facts + dependency_facts + scope_facts
    trace_links = _build_trace_links(evidence_units, all_fact_entries)

    source_files = [str(path).replace("\\", "/") for path in _source_paths(project_id)]
    if len(source_files) < 2:
        source_files = [
            f"projects/{project_id}/source/requirement.md",
            f"projects/{project_id}/source/background.md",
        ]

    return FactsModel(
        project_id=project_id,
        task_goal=task_goal,
        task_boundary=task_boundary,
        task_scenario=task_scenario,
        output_purpose="为 business judgment 与 experience translation 提供可追踪、可回链的当前任务事实。",
        source_files=source_files,
        explicit_references=[note.path for note in knowledge_notes],
        evidence_units=evidence_units,
        knowledge_notes=knowledge_notes,
        terminology=terminology,
        actors=actors,
        objects=objects,
        actor_facts=actor_facts,
        object_facts=object_facts,
        state_facts=state_facts,
        action_facts=action_facts,
        rule_facts=rule_facts,
        exception_facts=exception_facts,
        dependency_facts=dependency_facts,
        scope_facts=scope_facts,
        rules=rules,
        states=states,
        flows=flows,
        exceptions=exceptions,
        dependencies=dependencies,
        in_scope=in_scope or ["IN-01: 当前输入主要聚焦正式产物生成过程及其边界说明。"],
        out_of_scope=out_of_scope or ["OUT-01: 当前输入没有要求进入高保真视觉设计与实现细节。"],
        constraints=constraints,
        open_questions=_dedupe_strings(open_questions)[:8],
        gaps=_dedupe_strings(gaps)[:8],
        trace_links=trace_links,
    )
