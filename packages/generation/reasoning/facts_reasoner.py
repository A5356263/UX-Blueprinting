from __future__ import annotations

import re
from pathlib import Path

from packages.common import get_project_source_dir

from .schemas import (
    ActorEntry,
    DependencyEntry,
    ExceptionEntry,
    FactEntry,
    FactsModel,
    FlowEntry,
    ObjectEntry,
    RuleEntry,
    StateEntry,
    TerminologyEntry,
    TraceEntry,
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _normalize_source_text(text: str) -> str:
    text = text.replace("<br/>", "\n").replace("<br />", "\n")
    text = re.sub(r"`{3}[\s\S]*?`{3}", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _extract_source_lines(project_id: str) -> list[str]:
    source_dir = get_project_source_dir(project_id)
    texts = [
        _normalize_source_text(_read_text(source_dir / "requirement.md")),
        _normalize_source_text(_read_text(source_dir / "background.md")),
        _normalize_source_text(_read_text(source_dir / "task_card.md")),
    ]
    lines: list[str] = []
    for text in texts:
        for raw_line in text.splitlines():
            line = raw_line.strip(" -\t")
            if len(line) < 6 or line.startswith("#"):
                continue
            lines.append(line)
    return lines


def _pick_line(lines: list[str], keywords: list[str], fallback: str) -> str:
    for line in lines:
        if any(keyword in line for keyword in keywords):
            return line
    return fallback


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _extract_references(project_id: str) -> list[str]:
    task_card_path = get_project_source_dir(project_id) / "task_card.md"
    if not task_card_path.exists():
        return []
    refs: list[str] = []
    for raw_line in task_card_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if "/" not in line:
            continue
        if "knowledge/" in line or "specs/" in line or "docs/" in line:
            refs.append(line.lstrip("- ").strip())
    return refs[:8]


def _extract_roles(lines: list[str]) -> list[str]:
    joined = "\n".join(lines)
    role_map = [
        ("管理员", "管理员"),
        ("超级管理员", "超级管理员"),
        ("运营", "运营"),
        ("审批", "审批人"),
        ("员工", "员工"),
        ("用户", "用户"),
        ("系统", "系统"),
    ]
    result = [label for keyword, label in role_map if keyword in joined]
    return result or ["业务发起人", "管理者", "系统"]


def _extract_objects(lines: list[str]) -> list[str]:
    joined = "\n".join(lines)
    object_map = [
        ("权限", "权限"),
        ("角色", "角色"),
        ("申请", "申请单"),
        ("审批", "审批流"),
        ("记录", "结果记录"),
        ("页面", "页面入口"),
        ("配置", "配置项"),
    ]
    result = [label for keyword, label in object_map if keyword in joined]
    return result or ["核心对象", "关键配置", "结果记录"]


def _build_terminology(objects: list[str]) -> list[TerminologyEntry]:
    entries = [
        TerminologyEntry(
            term_id="T-01",
            term="核心能力",
            meaning="当前任务希望被稳定交付的一条业务能力链路。",
            boundary="它不是视觉方案，也不是研发实现细节。",
            source="requirement.md",
        ),
        TerminologyEntry(
            term_id="T-02",
            term="治理约束",
            meaning="限制能力开启、执行和结果生效的规则与边界。",
            boundary="它不同于系统异常，也不等于页面提示文案本身。",
            source="requirement.md",
        ),
        TerminologyEntry(
            term_id="T-03",
            term=objects[0],
            meaning="当前需求直接操作或解释的核心对象。",
            boundary="它需要和配置对象、结果对象分开识别。",
            source="requirement.md",
        ),
    ]
    return entries


def _build_fact_entries(lines: list[str], roles: list[str], objects: list[str]) -> tuple[
    list[FactEntry],
    list[FactEntry],
    list[FactEntry],
    list[FactEntry],
    list[FactEntry],
    list[FactEntry],
    list[FactEntry],
    list[FactEntry],
]:
    state_line = _pick_line(lines, ["状态", "结果", "生效", "处理中"], "需求中存在状态切换、结果反馈和阻断结果。")
    rule_line = _pick_line(lines, ["不能", "禁止", "校验", "限制"], "命中治理约束时需要阻断继续执行，并说明原因。")
    exception_line = _pick_line(lines, ["失败", "异常", "阻断", "冲突"], "需求里存在失败、阻断或异常处理场景。")
    dependency_line = _pick_line(lines, ["审批", "帮助", "依赖", "组织"], "当前能力依赖外部审批、帮助说明或组织配置协同完成。")
    actor_facts = [
        FactEntry("F-01", f"当前需求至少涉及 {roles[0]}、{roles[1] if len(roles) > 1 else '用户'} 与系统反馈三类角色。"),
        FactEntry("F-02", "管理侧负责定义边界、放行条件或解释规则冲突。"),
    ]
    object_facts = [
        FactEntry("F-03", f"本轮任务围绕 {objects[0]} 展开，并存在明确的配置边界。"),
        FactEntry("F-04", f"{objects[2] if len(objects) > 2 else '结果记录'} 需要承接结果、追踪和解释。"),
    ]
    state_facts = [
        FactEntry("F-05", state_line),
        FactEntry("F-06", "成功态与失败态都需要有可理解的状态反馈。"),
    ]
    action_facts = [
        FactEntry("F-07", "当前能力不是纯查询，至少包含进入、配置、提交、确认或查看结果等动作。"),
        FactEntry("F-08", "用户动作的可执行性受到前置条件、范围限制或规则校验影响。"),
    ]
    rule_facts = [
        FactEntry("F-09", rule_line),
        FactEntry("F-10", "命中规则后不仅要拦截，还要解释原因和下一步动作。"),
    ]
    exception_facts = [
        FactEntry("F-11", exception_line),
        FactEntry("F-12", "需要区分治理阻断与系统异常，避免用户误解。"),
    ]
    dependency_facts = [
        FactEntry("F-13", dependency_line),
        FactEntry("F-14", "正式产物仍应由当前项目独立生成，不能复制外部样例结论。"),
    ]
    scope_facts = [
        FactEntry("F-15", "当前阶段聚焦业务事实、业务判断与体验翻译，不展开实现细节。"),
        FactEntry("F-16", "正式产物必须写入 workspace，并能被后续 gate 与 validate 追踪。"),
    ]
    return (
        actor_facts,
        object_facts,
        state_facts,
        action_facts,
        rule_facts,
        exception_facts,
        dependency_facts,
        scope_facts,
    )


def build_facts_model(project_id: str) -> FactsModel:
    lines = _extract_source_lines(project_id)
    roles = _extract_roles(lines)
    objects = _extract_objects(lines)
    task_goal = _pick_line(
        lines,
        ["目标", "希望", "优化", "提升", "解决"],
        "当前需求希望补齐一条可执行、可校验、可追踪的业务能力链路。",
    )
    task_boundary = _pick_line(
        lines,
        ["范围", "边界", "本次", "仅"],
        "本次只覆盖核心能力、关键规则、状态、流程与异常，不展开实现细节。",
    )
    (
        actor_facts,
        object_facts,
        state_facts,
        action_facts,
        rule_facts,
        exception_facts,
        dependency_facts,
        scope_facts,
    ) = _build_fact_entries(lines, roles, objects)

    actors = [
        ActorEntry("A-01", roles[0], "配置方 / 管理方", "负责配置、放行或治理当前能力。", "requirement.md"),
        ActorEntry(
            "A-02",
            roles[1] if len(roles) > 1 else "用户",
            "申请方 / 使用方",
            "负责发起动作、查看结果或承接反馈。",
            "requirement.md",
        ),
        ActorEntry(
            "A-03",
            roles[2] if len(roles) > 2 else "系统",
            "审核方 / 协作方",
            "负责审核、回写状态或提供系统反馈。",
            "requirement.md",
        ),
    ]
    objects_list = [
        ObjectEntry("O-01", objects[0], "核心对象", "是本次主任务直接操作或查询的对象。", "requirement.md"),
        ObjectEntry("O-02", objects[1] if len(objects) > 1 else "关键配置", "配置对象", "决定用户能否执行以及如何执行。", "requirement.md"),
        ObjectEntry("O-03", objects[2] if len(objects) > 2 else "结果记录", "结果对象", "承接结果、追踪与解释。", "requirement.md"),
    ]
    rules = [
        RuleEntry(
            "R-01",
            "前置校验规则",
            "用户进入关键动作前",
            f"{objects[0]} 与 {objects[1] if len(objects) > 1 else '关键配置'}",
            "配置、范围与依赖可用",
            "允许继续执行",
            "命中冲突或缺依赖时阻断并解释",
            "F-09",
        ),
        RuleEntry(
            "R-02",
            "结果解释规则",
            "动作提交或状态更新后",
            objects[2] if len(objects) > 2 else "结果记录",
            "状态发生变化",
            "展示结果与下一步",
            "只给黑盒结果视为不合格",
            "F-06",
        ),
    ]
    states = [
        StateEntry(
            "S-01",
            "配置中 / 处理中",
            "进入主任务并开始执行",
            "成功提交或主动退出",
            "缺前置条件或命中规则冲突",
            "主任务尚未完成，需要继续理解和操作。",
            "F-05",
        ),
        StateEntry(
            "S-02",
            "成功完成",
            "关键动作通过校验并执行成功",
            "进入下一链路或离开页面",
            "无",
            "成功态必须明确告知结果与后续动作。",
            "F-06",
        ),
        StateEntry(
            "S-03",
            "失败 / 阻断",
            "命中规则冲突、范围限制或依赖异常",
            "处理原因后重试",
            "关键依赖仍不可用",
            "失败态必须解释原因，不能只提示失败。",
            "F-11",
        ),
    ]
    flows = [
        FlowEntry(
            "FL-01",
            roles[0],
            f"配置或启用 {objects[0]}",
            "进入主任务并具备管理权限",
            "形成可被执行侧使用的能力边界",
            "承接配置与治理责任。",
            "F-07",
        ),
        FlowEntry(
            "FL-02",
            roles[1] if len(roles) > 1 else "用户",
            "发起关键动作并等待结果",
            "能力已开放、范围允许、依赖可用",
            "进入成功结果或失败解释链路",
            "必须提供清晰反馈。",
            "F-08",
        ),
    ]
    exceptions = [
        ExceptionEntry(
            "EX-01",
            "前置规则冲突",
            "命中互斥规则、范围外限制或治理冲突",
            "阻断继续执行并给出原因与处理方向",
            "使用方 / 管理方",
            "F-09",
        ),
        ExceptionEntry(
            "EX-02",
            "依赖未就绪或结果失败",
            "外部依赖未完成、审批未完成或处理失败",
            "保留当前状态并提示如何补救",
            "使用方",
            "F-11",
        ),
    ]
    dependencies = [
        DependencyEntry(
            "DEP-01",
            "审批或协作流程",
            "流程引擎 / 审核链路",
            "决定动作是否放行以及结果如何回写",
            "部分确认",
            "F-13",
        ),
        DependencyEntry(
            "DEP-02",
            "帮助说明或结果解释机制",
            "帮助文档 / 解释能力",
            "帮助用户理解规则、失败和下一步",
            "部分确认",
            "F-14",
        ),
    ]
    joined = "\n".join(lines)
    open_questions = [
        "OQ-01: 依赖能力的最终配置方式、维护责任和边界说明仍待进一步确认。",
        "OQ-02: 当前任务中的细化异常分类与外部协作口径仍待补充。",
    ]
    if not lines:
        open_questions.append("OQ-03: 当前 source 输入为空，后续需要补充 requirement 与 background。")
    gaps = [
        "GAP-01: 原始输入对部分依赖与边界说明不足，会影响业务判断深度。",
        "GAP-02: 原始输入未完整提供所有结果说明文案，会影响后续体验层细化。",
    ]
    if not _contains_any(joined, ["审批", "依赖", "帮助", "配置"]):
        gaps.append("GAP-03: 输入中对依赖链路描述较弱，依赖识别目前以保守推断为主。")
    trace_links = [
        TraceEntry("F-01", "actor fact", "角色与职责相关段落", f"projects/{project_id}/source/requirement.md", "仅使用当前输入，不引入外部项目产物。"),
        TraceEntry("R-01", "rule", "规则、校验或限制相关段落", f"projects/{project_id}/source/requirement.md", "用于后续业务立场判断。"),
        TraceEntry("EX-01", "exception", "失败、阻断、异常相关段落", f"projects/{project_id}/source/requirement.md", "用于体验层异常态设计。"),
    ]
    return FactsModel(
        project_id=project_id,
        task_goal=task_goal,
        task_boundary=task_boundary,
        output_purpose="为 business judgment 和 experience translation 提供可追踪输入。",
        source_files=[
            f"projects/{project_id}/source/requirement.md",
            f"projects/{project_id}/source/background.md",
        ],
        explicit_references=_extract_references(project_id),
        terminology=_build_terminology(objects),
        actors=actors,
        objects=objects_list,
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
        in_scope=[
            "IN-01: 分析主任务链路、规则、状态、异常、依赖和结果反馈。",
            "IN-02: 为 business blueprint 和 experience blueprint 提供结构化事实输入。",
        ],
        out_of_scope=[
            "OUT-01: 不输出研发实现、数据库表、接口字段或高保真视觉稿。",
            "OUT-02: 不把外部样例正式产物直接复制为当前项目事实结论。",
        ],
        constraints=[
            "C-01: 当前正式产物必须来源于当前项目 source 输入，并写入 workspace。",
            "C-02: 信息不足处必须显式保留开放问题与缺口，不得编造确认结论。",
        ],
        open_questions=open_questions,
        gaps=gaps,
        trace_links=trace_links,
    )
