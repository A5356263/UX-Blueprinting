from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from packages.common import get_project_runtime_dir, get_project_source_dir
from packages.provenance import append_command_if_provenance_exists


ROUTE_VERSION = "route-decision@2.0"
UXB_ROUTE_VERSION = "uxb-route-decision@1.0"
ROUTE_RANK = {"fast": 1, "standard": 2, "full": 3}
BUSINESS_DEPTH_BY_ROUTE = {"fast": "note", "standard": "lite", "full": "full"}


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


def _clean_lines(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    cleaned: list[str] = []
    for item in values:
        text = str(item).strip()
        if text:
            cleaned.append(text)
    return cleaned


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
        for raw_part in re.split(r"[。！？；]", stripped):
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
        term = str(raw_term).strip()
        if not term:
            continue
        hit_sentences = [sentence for sentence in sentences if term.lower() in sentence.lower()]
        if not hit_sentences:
            continue
        if all(_is_negated_sentence(sentence, rules) for sentence in hit_sentences):
            continue
        matched.append(term)
    return matched


def _sentence_for_term(text: str, term: str) -> str:
    for sentence in _analysis_sentences(text):
        if term.lower() in sentence.lower():
            return sentence[:120]
    return term


def _source_texts(project_id: str) -> dict[str, str]:
    source_dir = get_project_source_dir(project_id)
    runtime_dir = get_project_runtime_dir(project_id)
    return {
        "source/task_card.md": _read_text(source_dir / "task_card.md"),
        "source/requirement.md": _read_text(source_dir / "requirement.md"),
        "source/background.md": _read_text(source_dir / "background.md"),
        "runtime/task_card_resolved.json": json.dumps(_read_json(runtime_dir / "task_card_resolved.json"), ensure_ascii=False),
        "runtime/context_manifest.json": json.dumps(_read_json(runtime_dir / "context_manifest.json"), ensure_ascii=False),
    }


def _combined_text(texts: dict[str, str]) -> str:
    return "\n".join(value for value in texts.values() if value.strip())


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
        if len(evidence) >= 6:
            break
    fallback = str(rules.get("fallback_evidence") or "未读取到足够明确的需求正文，请先由 UXB 做需求类型判断。")
    return evidence or [fallback]


def _matched_signals(text: str, rules: dict[str, Any]) -> list[dict[str, object]]:
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
                "signal_level": str(rule.get("signal_level") or "medium"),
            }
        )
    return hits


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
            evidence[field] = str(rule.get("miss_reason") or "未发现相关信号")
            continue
        value = str(rule.get("default_hit_level") or "medium")
        for trigger in rule.get("value_triggers", []):
            if not isinstance(trigger, dict):
                continue
            trigger_terms = [str(item) for item in trigger.get("terms", [])]
            if any(term in matched for term in trigger_terms):
                value = str(trigger.get("level") or value)
                break
        values[field] = value
        evidence[field] = f"{str(rule.get('hit_reason') or '发现相关风险提示')}：{_sentence_for_term(text, matched[0])}"
    return values, evidence, matched_terms_by_field


def _design_pressure(dimensions: dict[str, str], rules: dict[str, Any]) -> list[str]:
    labels_by_field = {str(key): str(value) for key, value in rules.get("pressure_labels", {}).items()}
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
    labels = [labels_by_field[field] for field in ranked_fields if field in labels_by_field]
    default_pressure = str(rules.get("default_design_pressure") or "")
    max_count = int(rules.get("max_design_pressure_count") or 5)
    return labels[:max_count] or ([default_pressure] if default_pressure else [])


def _experience_focus(design_pressure: list[str], rules: dict[str, Any]) -> list[str]:
    focus_map = {str(key): str(value) for key, value in rules.get("experience_focus_by_pressure", {}).items()}
    return [focus_map[label] for label in design_pressure if label in focus_map][:4]


def _guardrail_warnings(dimensions: dict[str, str], rules: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    review_fields = rules.get("guardrail_review_fields", {})
    for field, config in review_fields.items():
        if not isinstance(config, dict):
            continue
        levels = {str(item) for item in config.get("levels", [])}
        if dimensions.get(str(field)) in levels:
            message = str(config.get("message") or "").strip()
            if message:
                warnings.append(message)
    return warnings


def _uxb_route_decision_path(project_id: str) -> Path:
    return get_project_runtime_dir(project_id) / "uxb_route_decision.json"


def _normalized_business_depth(route: str, payload: dict[str, Any]) -> str:
    value = str(payload.get("business_depth") or "").strip()
    return value or BUSINESS_DEPTH_BY_ROUTE.get(route, "full")


def _validate_uxb_route_decision(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    route = str(payload.get("route") or "").strip()
    demand_type = str(payload.get("demand_type") or "").strip()
    reason = str(payload.get("reason") or "").strip()
    source = str(payload.get("source") or "").strip() or "uxb_ai_judgment"
    version = str(payload.get("version") or "").strip() or UXB_ROUTE_VERSION
    confirmed_by_user = bool(payload.get("confirmed_by_user"))
    evidence = _clean_lines(payload.get("evidence"))
    design_pressure = _clean_lines(payload.get("design_pressure"))
    experience_focus = _clean_lines(payload.get("experience_focus"))
    risk_notes = _clean_lines(payload.get("risk_notes"))

    if version != UXB_ROUTE_VERSION:
        errors.append(f"uxb_route_decision.version 必须为 `{UXB_ROUTE_VERSION}`")
    if route not in ROUTE_RANK:
        errors.append("uxb_route_decision.route 必须是 fast / standard / full")
    if not demand_type:
        errors.append("uxb_route_decision.demand_type 不能为空")
    if not reason:
        errors.append("uxb_route_decision.reason 不能为空")
    if not confirmed_by_user:
        errors.append("uxb_route_decision 还没有用户确认，不能直接驱动主链路")
    if not evidence:
        errors.append("uxb_route_decision.evidence 不能为空")

    normalized = {
        "version": version,
        "source": source,
        "confirmed_by_user": confirmed_by_user,
        "demand_type": demand_type,
        "route": route,
        "reason": reason,
        "evidence": evidence,
        "design_pressure": design_pressure,
        "business_depth": _normalized_business_depth(route, payload),
        "experience_focus": experience_focus,
        "risk_notes": risk_notes,
    }
    return normalized, errors


def _build_missing_decision(project_id: str, rules: dict[str, Any], texts: dict[str, str]) -> dict[str, Any]:
    text = _combined_text(texts)
    matched_signals = _matched_signals(text, rules)
    dimensions, dimension_evidence, matched_dimension_terms = _dimension_judgment(text, rules)
    design_pressure = _design_pressure(dimensions, rules)
    return {
        "version": ROUTE_VERSION,
        "project_id": project_id,
        "status": "needs_uxb_judgment",
        "source": "missing_uxb_route_decision",
        "confirmed_by_user": False,
        "can_execute_mainline": False,
        "should_not_control_mainline": True,
        "route": "",
        "demand_type": "不确定",
        "reason": "缺少 UXB 已确认的需求类型判断，当前只能给出风险提示，不能自动决定执行路线。",
        "evidence": _task_goal_evidence(texts, rules),
        "design_pressure": design_pressure,
        "business_depth": "",
        "experience_focus": _experience_focus(design_pressure, rules),
        "risk_notes": _guardrail_warnings(dimensions, rules),
        "validation_errors": ["缺少 runtime/uxb_route_decision.json"],
        "guardrail_hints": {
            "matched_signals": matched_signals[:6],
            "dimension_judgment": dimensions,
            "dimension_evidence": dimension_evidence,
            "matched_dimension_terms": {field: terms for field, terms in matched_dimension_terms.items() if terms},
        },
    }


def build_route_decision(project_id: str) -> dict[str, Any]:
    rules = _load_rules()
    texts = _source_texts(project_id)
    text = _combined_text(texts)
    matched_signals = _matched_signals(text, rules)
    dimensions, dimension_evidence, matched_dimension_terms = _dimension_judgment(text, rules)
    design_pressure = _design_pressure(dimensions, rules)
    guardrail_warnings = _guardrail_warnings(dimensions, rules)

    raw_uxb_decision = _read_json(_uxb_route_decision_path(project_id))
    if not raw_uxb_decision:
        return _build_missing_decision(project_id, rules, texts)

    normalized, validation_errors = _validate_uxb_route_decision(raw_uxb_decision)
    status = "confirmed" if not validation_errors else "needs_user_confirmation"
    route = normalized["route"] if status == "confirmed" else ""
    business_depth = normalized["business_depth"] if status == "confirmed" else ""

    return {
        "version": ROUTE_VERSION,
        "project_id": project_id,
        "status": status,
        "source": normalized["source"],
        "confirmed_by_user": normalized["confirmed_by_user"],
        "can_execute_mainline": status == "confirmed",
        "should_not_control_mainline": status != "confirmed",
        "route": route,
        "demand_type": normalized["demand_type"],
        "reason": normalized["reason"] if status == "confirmed" else "UXB 已形成初步判断，但还不能直接启动主链路，请先补齐并确认判断结果。",
        "evidence": normalized["evidence"] or _task_goal_evidence(texts, rules),
        "design_pressure": normalized["design_pressure"] or design_pressure,
        "business_depth": business_depth,
        "experience_focus": normalized["experience_focus"] or _experience_focus(normalized["design_pressure"] or design_pressure, rules),
        "risk_notes": normalized["risk_notes"] or guardrail_warnings,
        "validation_errors": validation_errors,
        "guardrail_hints": {
            "matched_signals": matched_signals[:6],
            "dimension_judgment": dimensions,
            "dimension_evidence": dimension_evidence,
            "matched_dimension_terms": {field: terms for field, terms in matched_dimension_terms.items() if terms},
            "guardrail_warnings": guardrail_warnings,
        },
    }


def _render_markdown(decision: dict[str, Any]) -> str:
    lines = [
        "# Route Decision",
        "",
        f"- Project: `{decision['project_id']}`",
        f"- Version: `{decision['version']}`",
        f"- Status: `{decision['status']}`",
        f"- Source: `{decision['source']}`",
        f"- Confirmed by user: `{str(bool(decision['confirmed_by_user'])).lower()}`",
        f"- Can execute mainline: `{str(bool(decision['can_execute_mainline'])).lower()}`",
        f"- Route: `{decision.get('route') or 'pending'}`",
        f"- Demand type: {decision.get('demand_type') or '不确定'}",
        f"- Business depth: `{decision.get('business_depth') or 'pending'}`",
        "",
        "## Reason",
        "",
        str(decision.get("reason") or ""),
        "",
        "## Evidence",
        "",
    ]
    lines.extend(f"- {item}" for item in decision.get("evidence", []))
    lines.extend(["", "## Design Pressure", ""])
    lines.extend(f"- {item}" for item in decision.get("design_pressure", []))

    validation_errors = _clean_lines(decision.get("validation_errors"))
    lines.extend(["", "## Validation Errors", ""])
    lines.extend(f"- {item}" for item in validation_errors or ["none"])

    risk_notes = _clean_lines(decision.get("risk_notes"))
    lines.extend(["", "## Risk Notes", ""])
    lines.extend(f"- {item}" for item in risk_notes or ["none"])

    hints = decision.get("guardrail_hints", {})
    lines.extend(["", "## Guardrail Hints", ""])
    for field, value in dict(hints.get("dimension_judgment", {})).items():
        evidence = dict(hints.get("dimension_evidence", {})).get(field, "")
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

    if decision.get("status") == "confirmed":
        append_command_if_provenance_exists(project_id, "route-decision")
        print(f"route_decision.json 已生成: {json_path}")
        print(f"route_decision.md 已生成: {md_path}")
        print(f"route={decision['route']} demand_type={decision['demand_type']}")
        return 0

    print(f"route_decision.json 已生成: {json_path}")
    print(f"route_decision.md 已生成: {md_path}")
    print("当前还不能自动决定执行路线，请先由 UXB 生成并确认 runtime/uxb_route_decision.json。")
    for item in _clean_lines(decision.get("validation_errors")):
        print(f"- {item}")
    return 1
