from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Literal

from packages.common import get_project_workspace_dir

FlowType = Literal["main", "secondary", "exception"]
CarrierType = Literal["page", "drawer", "modal", "toast", "inline", "external"]

_MACHINE_TRACE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bEV-\d+\b", re.IGNORECASE), "包含 EV 编号"),
    (re.compile(r"\b(?:P|TF|TR)-\d+\b", re.IGNORECASE), "包含流程/页面追踪编号"),
    (re.compile(r"source[_ ]?path", re.IGNORECASE), "包含 source_path"),
    (re.compile(r"(?:从当前输入直接抽取|未做模板补全|Runtime Task Goal)"), "包含机器提示语"),
    (re.compile(r"(?:配置\s+支持配置|提交\s+目前企业的员工权限分配均由权限)"), "包含低质量机械短语"),
]
_FORBIDDEN_SCHEMA_FIELDS = {"self_service_permission", "admin_permission_flow", "employee_permission_application"}
_NODE_REQUIRED_FIELDS = (
    "node_id",
    "title",
    "carrier",
    "user_action",
    "system_feedback",
    "next_step",
    "copy_strategy",
)


@dataclass(slots=True)
class TraceRefs:
    fact_refs: list[str] = field(default_factory=list)
    judgment_refs: list[str] = field(default_factory=list)
    principle_refs: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Carrier:
    type: CarrierType
    name: str


@dataclass(slots=True)
class InteractionException:
    name: str
    trigger: str
    feedback: str
    next_step: str


@dataclass(slots=True)
class InteractionState:
    name: str
    meaning: str
    feedback: str


@dataclass(slots=True)
class InteractionNode:
    node_id: str
    title: str
    carrier: Carrier
    user_action: str
    system_feedback: str
    next_step: str
    copy_strategy: list[str] = field(default_factory=list)
    states: list[InteractionState] = field(default_factory=list)
    exceptions: list[InteractionException] = field(default_factory=list)
    trace_refs: TraceRefs = field(default_factory=TraceRefs)


@dataclass(slots=True)
class RoleFlow:
    flow_id: str
    flow_type: FlowType
    role: str
    title: str
    summary: str
    nodes: list[InteractionNode] = field(default_factory=list)


@dataclass(slots=True)
class ConcreteCopy:
    type: str
    text: str


@dataclass(slots=True)
class PageDesign:
    page_id: str
    carrier_type: CarrierType
    title: str
    purpose: str
    entry: str
    modules: list[str] = field(default_factory=list)
    primary_actions: list[str] = field(default_factory=list)
    secondary_actions: list[str] = field(default_factory=list)
    concrete_copy: list[ConcreteCopy] = field(default_factory=list)
    states: list[str] = field(default_factory=list)
    exceptions: list[str] = field(default_factory=list)
    trace_refs: TraceRefs = field(default_factory=TraceRefs)


@dataclass(slots=True)
class InteractionMap:
    project_id: str
    version: str
    overview: dict[str, Any] = field(default_factory=dict)
    role_flows: list[RoleFlow] = field(default_factory=list)
    page_designs: list[PageDesign] = field(default_factory=list)
    quality_notes: dict[str, Any] = field(default_factory=dict)


def _as_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _contains_machine_trace(value: object) -> str | None:
    text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    for pattern, reason in _MACHINE_TRACE_PATTERNS:
        if pattern.search(text):
            return reason
    return None


def validate_interaction_map_payload(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []

    if not isinstance(payload, dict):
        return ["interaction_map 不是有效 JSON 对象"], warnings

    for forbidden_field in sorted(_FORBIDDEN_SCHEMA_FIELDS):
        if forbidden_field in payload:
            blockers.append(f"interaction_map 禁止包含字段：{forbidden_field}")

    role_flows = payload.get("role_flows")
    page_designs = payload.get("page_designs")
    if not isinstance(role_flows, list) or not role_flows:
        blockers.append("interaction_map 缺少 role_flows")
    if not isinstance(page_designs, list) or not page_designs:
        blockers.append("interaction_map 缺少 page_designs")

    main_flow_count = 0
    node_with_trace_count = 0
    for flow in role_flows if isinstance(role_flows, list) else []:
        if not isinstance(flow, dict):
            blockers.append("role_flows 中存在非对象项")
            continue
        flow_id = str(flow.get("flow_id") or "unknown")
        flow_type = str(flow.get("flow_type") or "")
        if flow_type not in {"main", "secondary", "exception"}:
            blockers.append(f"{flow_id}: flow_type 非法")
        if flow_type == "main":
            main_flow_count += 1
        if not str(flow.get("role") or "").strip():
            blockers.append(f"{flow_id}: 缺少 role")
        if not isinstance(flow.get("nodes"), list) or not flow.get("nodes"):
            blockers.append(f"{flow_id}: 缺少 nodes")
            continue

        for node in flow["nodes"]:
            if not isinstance(node, dict):
                blockers.append(f"{flow_id}: nodes 中存在非对象项")
                continue
            node_id = str(node.get("node_id") or "unknown")
            for field_name in _NODE_REQUIRED_FIELDS:
                if not node.get(field_name):
                    blockers.append(f"{flow_id}/{node_id}: 缺少 {field_name}")

            carrier = node.get("carrier")
            if not isinstance(carrier, dict):
                blockers.append(f"{flow_id}/{node_id}: carrier 必须是对象")
            else:
                carrier_type = str(carrier.get("type") or "")
                if carrier_type not in {"page", "drawer", "modal", "toast", "inline", "external"}:
                    blockers.append(f"{flow_id}/{node_id}: carrier.type 非法")
                if not str(carrier.get("name") or "").strip():
                    blockers.append(f"{flow_id}/{node_id}: carrier.name 为空")

            has_states = bool(node.get("states")) or bool(node.get("state_refs"))
            has_exceptions = bool(node.get("exceptions")) or bool(node.get("exception_refs"))
            if not has_states:
                warnings.append(f"{flow_id}/{node_id}: 缺少 states 或 state_refs")
            if not has_exceptions:
                warnings.append(f"{flow_id}/{node_id}: 缺少 exceptions 或 exception_refs")

            trace_refs = node.get("trace_refs")
            if isinstance(trace_refs, dict):
                fact_refs = _as_string_list(trace_refs.get("fact_refs"))
                judgment_refs = _as_string_list(trace_refs.get("judgment_refs"))
                principle_refs = _as_string_list(trace_refs.get("principle_refs"))
                if fact_refs or judgment_refs or principle_refs:
                    node_with_trace_count += 1
            if not node.get("source_refs") and not isinstance(trace_refs, dict):
                warnings.append(f"{flow_id}/{node_id}: 缺少 source_refs / trace_refs")

            machine_reason = _contains_machine_trace(node)
            if machine_reason:
                warnings.append(f"{flow_id}/{node_id}: {machine_reason}")

    if main_flow_count == 0:
        blockers.append("interaction_map 缺少 main flow")
    if isinstance(role_flows, list) and role_flows and node_with_trace_count == 0:
        blockers.append("interaction_map 节点全部缺少 trace_refs")

    page_with_copy_count = 0
    for page in page_designs if isinstance(page_designs, list) else []:
        if not isinstance(page, dict):
            blockers.append("page_designs 中存在非对象项")
            continue
        page_id = str(page.get("page_id") or "unknown")
        for field_name in ("page_id", "carrier_type", "title", "purpose", "entry"):
            if not page.get(field_name):
                blockers.append(f"{page_id}: 缺少 {field_name}")
        if not isinstance(page.get("modules"), list) or not page.get("modules"):
            warnings.append(f"{page_id}: modules 为空")
        concrete_copy = page.get("concrete_copy")
        if isinstance(concrete_copy, list) and concrete_copy:
            page_with_copy_count += 1
        else:
            blockers.append(f"{page_id}: 缺少 concrete_copy")
        machine_reason = _contains_machine_trace(page)
        if machine_reason:
            warnings.append(f"{page_id}: {machine_reason}")

    if isinstance(page_designs, list) and page_designs and page_with_copy_count == 0:
        blockers.append("interaction_map 页面全部缺少 concrete_copy")

    quality_notes = payload.get("quality_notes")
    if isinstance(quality_notes, dict) and quality_notes.get("fallback_used") is True:
        warnings.append("interaction_map 标记了 fallback_used=true")

    return blockers, warnings


def write_interaction_map(project_id: str, payload: dict[str, Any]) -> None:
    workspace_dir = get_project_workspace_dir(project_id)
    workspace_dir.mkdir(parents=True, exist_ok=True)
    path = workspace_dir / "interaction_map.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_interaction_map_payload(project_id: str) -> dict[str, Any] | None:
    path = get_project_workspace_dir(project_id) / "interaction_map.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def load_interaction_map(project_id: str) -> InteractionMap | None:
    payload = load_interaction_map_payload(project_id)
    if payload is None:
        return None
    blockers, _warnings = validate_interaction_map_payload(payload)
    if blockers:
        return None
    return InteractionMap(
        project_id=str(payload.get("project_id") or project_id),
        version=str(payload.get("version") or "1.0"),
        overview=payload.get("overview") if isinstance(payload.get("overview"), dict) else {},
        role_flows=[],
        page_designs=[],
        quality_notes=payload.get("quality_notes") if isinstance(payload.get("quality_notes"), dict) else {},
    )
