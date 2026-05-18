from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from packages.common import get_project_runtime_dir, get_project_source_dir
from packages.provenance import append_command_if_provenance_exists


ROUTE_VERSION = "route-decision@1.0"


def _route_rules_path() -> Path:
    override = os.environ.get("UXB_ROUTE_DECISION_RULES")
    return Path(override).resolve() if override else Path(__file__).with_name("rules.json")


def _load_rules() -> dict[str, Any]:
    path = _route_rules_path()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing route decision rules: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid route decision rules JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"Route decision rules must be a JSON object: {path}")
    return payload


def _read_text(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _source_texts(project_id: str) -> dict[str, str]:
    source_dir = get_project_source_dir(project_id)
    runtime_dir = get_project_runtime_dir(project_id)
    task_card_resolved = _read_json(runtime_dir / "task_card_resolved.json")
    context_manifest = _read_json(runtime_dir / "context_manifest.json")
    return {
        "source/task_card.md": _read_text(source_dir / "task_card.md"),
        "source/requirement.md": _read_text(source_dir / "requirement.md"),
        "source/background.md": _read_text(source_dir / "background.md"),
        "runtime/task_card_resolved.json": json.dumps(task_card_resolved, ensure_ascii=False),
        "runtime/context_manifest.json": json.dumps(context_manifest, ensure_ascii=False),
    }


def _combined_text(texts: dict[str, str]) -> str:
    return "\n".join(value for value in texts.values() if value.strip())


def _analysis_sentences(text: str) -> list[str]:
    sentences: list[str] = []
    skip_section = False
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            skip_section = stripped.startswith("## 期望判断")
            continue
        if skip_section:
            continue
        for raw_part in re.split(r"[。！？!?；;]", stripped):
            part = raw_part.strip(" -\t")
            if part:
                sentences.append(part)
    return sentences


def _is_negated_sentence(sentence: str, rules: dict[str, Any]) -> bool:
    return any(str(marker) in sentence for marker in rules.get("negation_markers", []))


def _contains_any(text: str, terms: list[str], rules: dict[str, Any]) -> list[str]:
    sentences = _analysis_sentences(text)
    matched: list[str] = []
    for raw_term in terms:
        term = str(raw_term)
        term_lower = term.lower()
        hit_sentences = [sentence for sentence in sentences if term_lower in sentence.lower()]
        if not hit_sentences:
            continue
        if all(_is_negated_sentence(sentence, rules) for sentence in hit_sentences):
            continue
        matched.append(term)
    return matched


def _sentence_for_term(text: str, term: str) -> str:
    for part in _analysis_sentences(text):
        if term.lower() in part.lower() and part:
            return part[:120]
    return term


def _task_goal_evidence(texts: dict[str, str], rules: dict[str, Any]) -> list[str]:
    evidence_terms = [str(item) for item in rules.get("evidence_terms", [])]
    evidence: list[str] = []
    for source, text in texts.items():
        if not text.strip():
            continue
        for line in text.splitlines():
            stripped = line.strip(" -\t")
            if not stripped or stripped.startswith("#"):
                continue
            if any(term in stripped for term in evidence_terms):
                evidence.append(f"{source}: {stripped[:120]}")
                break
        if len(evidence) >= 4:
            break
    return evidence


def _demand_type_and_signals(text: str, rules: dict[str, Any]) -> tuple[str, list[dict[str, object]]]:
    hits: list[dict[str, object]] = []
    for rule in rules.get("signal_rules", []):
        if not isinstance(rule, dict):
            continue
        matched = _contains_any(text, [str(item) for item in rule.get("terms", [])], rules)
        if not matched:
            continue
        hits.append(
            {
                "demand_type": str(rule.get("demand_type") or "不确定"),
                "matched_terms": matched,
                "evidence": str(rule.get("evidence_label") or ""),
                "route_pressure": int(rule.get("route_pressure") or 0),
            }
        )
    if not hits:
        return str(rules.get("default_demand_type") or "不确定"), []
    demand_order = [str(item) for item in rules.get("demand_types", [])]

    def sort_key(item: dict[str, object]) -> tuple[int, int]:
        demand_type = str(item["demand_type"])
        order = demand_order.index(demand_type) if demand_type in demand_order else len(demand_order)
        return -int(item["route_pressure"]), order

    hits.sort(key=sort_key)
    return str(hits[0]["demand_type"]), hits


def _dimension_judgment(text: str, rules: dict[str, Any]) -> tuple[dict[str, str], dict[str, str], dict[str, list[str]]]:
    values: dict[str, str] = {}
    evidence: dict[str, str] = {}
    matched_terms_by_field: dict[str, list[str]] = {}
    for field in [str(item) for item in rules.get("dimension_fields", [])]:
        rule = rules.get("dimension_rules", {}).get(field, {})
        terms = [str(item) for item in rule.get("terms", [])]
        matched = _contains_any(text, terms, rules)
        matched_terms_by_field[field] = matched
        if not matched:
            values[field] = str(rule.get("miss_level") or "none")
            evidence[field] = str(rule.get("miss_reason") or "未发现相关压力")
            continue
        value = str(rule.get("default_hit_level") or "medium")
        for trigger in rule.get("value_triggers", []):
            if not isinstance(trigger, dict):
                continue
            trigger_terms = [str(item) for item in trigger.get("terms", [])]
            if any(term in matched for term in trigger_terms):
                value = str(trigger.get("level") or value)
                break
        sample = _sentence_for_term(text, matched[0])
        values[field] = value
        evidence[field] = f"{rule.get('hit_reason') or '发现相关压力'}：{sample}"
    return values, evidence, matched_terms_by_field


def _has_dimension_value(dimensions: dict[str, str], fields: list[str], levels: list[str]) -> bool:
    return any(dimensions.get(field) in set(levels) for field in fields)


def _route_from_rules(demand_type: str, dimensions: dict[str, str], signals: list[dict[str, object]], rules: dict[str, Any]) -> str:
    policy = rules.get("route_policy", {})
    if demand_type in set(policy.get("full_demand_types", [])):
        return "full"
    for item in policy.get("full_dimension_values", []):
        if not isinstance(item, dict):
            continue
        if dimensions.get(str(item.get("field"))) in set(str(level) for level in item.get("levels", [])):
            return "full"
    state_rule = policy.get("full_when_state_exception_high_with_demand_types", {})
    state_field = str(state_rule.get("field") or "")
    state_levels = set(str(level) for level in state_rule.get("levels", []))
    demand_types = set(str(item) for item in state_rule.get("demand_types", []))
    if state_field and dimensions.get(state_field) in state_levels and any(str(signal.get("demand_type")) in demand_types for signal in signals):
        return "full"
    if demand_type in set(policy.get("standard_demand_types", [])):
        return "standard"
    standard_dimensions = policy.get("standard_dimension_values", {})
    if _has_dimension_value(
        dimensions,
        [str(item) for item in standard_dimensions.get("fields", [])],
        [str(item) for item in standard_dimensions.get("levels", [])],
    ):
        return "standard"
    pressure_threshold = int(policy.get("standard_when_route_pressure_at_least") or 0)
    if pressure_threshold and any(int(signal.get("route_pressure") or 0) >= pressure_threshold for signal in signals):
        return "standard"
    return str(policy.get("default_route") or "fast")


def _confidence(route: str, demand_type: str, signals: list[dict[str, object]], dimensions: dict[str, str], rules: dict[str, Any]) -> str:
    confidence_rules = rules.get("confidence_policy", {})
    non_none_count = sum(1 for value in dimensions.values() if value not in {"none", "low"})
    if demand_type == rules.get("default_demand_type") or not signals:
        return str(confidence_rules.get("no_signal") or "low")
    fast_risk = confidence_rules.get("fast_with_risk", {})
    if route == "fast" and _has_dimension_value(
        dimensions,
        [str(item) for item in fast_risk.get("fields", [])],
        [str(item) for item in fast_risk.get("levels", [])],
    ):
        return str(fast_risk.get("confidence") or "medium")
    if non_none_count >= int(confidence_rules.get("high_non_none_dimension_count") or 4):
        return "high"
    return str(confidence_rules.get("default") or "medium")


def _design_pressure(dimensions: dict[str, str], rules: dict[str, Any]) -> list[str]:
    ranked_fields = [
        field
        for field in [str(item) for item in rules.get("dimension_fields", [])]
        if dimensions.get(field) not in {"none", "low"}
    ]
    if not ranked_fields:
        ranked_fields = [
            str(field)
            for field in rules.get("fallback_pressure_fields", [])
            if dimensions.get(str(field)) == "low"
        ]
    labels_by_field = {str(key): str(value) for key, value in rules.get("pressure_labels", {}).items()}
    labels = [labels_by_field[field] for field in ranked_fields if field in labels_by_field]
    default_pressure = str(rules.get("default_design_pressure") or "")
    return labels[: int(rules.get("max_design_pressure_count") or 5)] or ([default_pressure] if default_pressure else [])


def _route_text(value_by_route: dict[str, list[str]], route: str) -> list[str]:
    values = value_by_route.get(route, [])
    return [str(item) for item in values]


def _experience_focus(design_pressure: list[str], rules: dict[str, Any]) -> list[str]:
    focus_map = {str(key): str(value) for key, value in rules.get("experience_focus_by_pressure", {}).items()}
    return [focus_map[label] for label in design_pressure if label in focus_map][:4]


def _reason(route: str, demand_type: str, design_pressure: list[str], rules: dict[str, Any]) -> str:
    template = str(rules.get("reason_templates", {}).get(route) or "{demand_type}：{pressure}")
    return template.format(demand_type=demand_type, pressure="、".join(design_pressure[:3]))


def build_route_decision(project_id: str) -> dict[str, Any]:
    rules = _load_rules()
    texts = _source_texts(project_id)
    text = _combined_text(texts)
    demand_type, signals = _demand_type_and_signals(text, rules)
    dimensions, dimension_evidence, matched_terms = _dimension_judgment(text, rules)
    route = _route_from_rules(demand_type, dimensions, signals, rules)
    pressure = _design_pressure(dimensions, rules)
    evidence = _task_goal_evidence(texts, rules)
    if not evidence:
        evidence = [str(rules.get("fallback_evidence") or "未读取到足够明确的需求正文，建议补充 source 输入。")]
    decision = {
        "version": ROUTE_VERSION,
        "rules_version": str(rules.get("version") or ""),
        "project_id": project_id,
        "route": route,
        "confidence": _confidence(route, demand_type, signals, dimensions, rules),
        "demand_type": demand_type,
        "reason": _reason(route, demand_type, pressure, rules),
        "evidence": evidence[:6],
        "dimension_judgment": dimensions,
        "dimension_evidence": dimension_evidence,
        "design_pressure": pressure,
        "business_depth": str(rules.get("business_depth_by_route", {}).get(route) or "full"),
        "experience_focus": _experience_focus(pressure, rules),
        "non_focus_guidance": _route_text(rules.get("non_focus_guidance_by_route", {}), route),
        "escalation_signals": _route_text(rules.get("escalation_signals_by_route", {}), route),
        "matched_route_signals": signals[:6],
        "matched_dimension_terms": {field: terms for field, terms in matched_terms.items() if terms},
        "should_not_control_mainline": True,
    }
    return decision


def _render_markdown(decision: dict[str, Any]) -> str:
    lines = [
        "# Route Decision",
        "",
        f"- Project: `{decision['project_id']}`",
        f"- Version: `{decision['version']}`",
        f"- Rules version: `{decision.get('rules_version', '')}`",
        f"- Route: `{decision['route']}`",
        f"- Confidence: `{decision['confidence']}`",
        f"- Demand type: {decision['demand_type']}",
        f"- Business depth: `{decision['business_depth']}`",
        f"- Should control mainline: `{str(decision['should_not_control_mainline']).lower()}`",
        "",
        "## Reason",
        "",
        str(decision["reason"]),
        "",
        "## Evidence",
        "",
    ]
    lines.extend(f"- {item}" for item in decision.get("evidence", []))
    lines.extend(["", "## Design Pressure", ""])
    lines.extend(f"- {item}" for item in decision.get("design_pressure", []))
    lines.extend(["", "## Escalation Signals", ""])
    lines.extend(f"- {item}" for item in decision.get("escalation_signals", []))
    lines.extend(["", "## Dimension Judgment", ""])
    for field, value in decision.get("dimension_judgment", {}).items():
        evidence = decision.get("dimension_evidence", {}).get(field, "")
        lines.append(f"- `{field}`: `{value}` - {evidence}")
    return "\n".join(lines) + "\n"


def run_route_decision(project_id: str) -> int:
    source_dir = get_project_source_dir(project_id)
    if not source_dir.exists():
        print(f"ERROR: Project source directory not found: {source_dir}")
        return 1
    decision = build_route_decision(project_id)
    runtime_dir = get_project_runtime_dir(project_id)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    json_path = runtime_dir / "route_decision.json"
    md_path = runtime_dir / "route_decision.md"
    json_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_render_markdown(decision), encoding="utf-8")
    append_command_if_provenance_exists(project_id, "route-decision")
    print(f"route_decision.json 已生成: {json_path}")
    print(f"route_decision.md 已生成: {md_path}")
    print(f"route={decision['route']} confidence={decision['confidence']} demand_type={decision['demand_type']}")
    print("should_not_control_mainline=true")
    return 0
