#!/usr/bin/env python3
"""Validate, orchestrate, and publish Objective 3.0 by purpose."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parents[3]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import baseline_analyzer
import enterprise_state_analyzer
import error_analyzer
import input_adapter
import journey_analyzer
import report_renderer
import task_analyzer

RUNTIME_DIR = WORKSPACE_ROOT / "shared-workflow/data-analysis/runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))
import contract_runtime


ARTIFACT_VERSION = "4.0.0"
ANALYSES = (
    "metrics",
    "funnel",
    "journey",
    "errors",
    "segments",
    "baseline",
    "feature_usage",
    "enterprise_states",
)
ALLOWED_RULE_SOURCES = {"user_confirmed", "uxb", "business_config", "upstream_requirement"}
LEGACY_ANALYSIS_NAMES = {
    "metric_analysis": "metrics", "funnel_analysis": "funnel", "journey_analysis": "journey",
    "error_analysis": "errors", "segmentation_analysis": "segments",
    "historical_baseline_analysis": "baseline", "feature_usage_analysis": "feature_usage",
}
FORBIDDEN_METRIC_KEYS = {
    "target", "target_value", "target_reference", "目标参考值", "health_value", "health_score",
    "异动指标说明", "anomaly_rule", "anomaly_rules", "legacy_anomaly_rule",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sanitize_metric_definition(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: sanitize_metric_definition(item) for key, item in value.items() if key not in FORBIDDEN_METRIC_KEYS}
    if isinstance(value, list):
        return [sanitize_metric_definition(item) for item in value]
    return value


def deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in overlay.items():
        merged[key] = deep_merge(merged[key], value) if isinstance(value, dict) and isinstance(merged.get(key), dict) else value
    return merged


def _schema_validate(instance: dict[str, Any], schema_name: str) -> None:
    try:
        from jsonschema import Draft202012Validator, RefResolver
    except ImportError:
        return
    schema_path = SCRIPT_DIR.parent / "schemas" / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    resolver = RefResolver(base_uri=schema_path.resolve().as_uri(), referrer=schema)
    Draft202012Validator(schema, resolver=resolver).validate(instance)


def validate_request(request: dict[str, Any]) -> None:
    required = ("artifact_type", "artifact_version", "project_name", "source_mode", "input_data_sources")
    missing = [key for key in required if key not in request]
    if missing:
        raise ValueError("missing required request fields: " + ", ".join(missing))
    if request["artifact_type"] != "objective_analysis_request" or request["artifact_version"] != ARTIFACT_VERSION:
        raise ValueError(f"request must use objective_analysis_request {ARTIFACT_VERSION}")
    if request["source_mode"] not in {"independent", "chain_context"}:
        raise ValueError("source_mode must be independent or chain_context")
    if request.get("analysis_intent", "comprehensive") not in {"comprehensive", "report", "focused"}:
        raise ValueError("unsupported analysis_intent")
    if not isinstance(request["input_data_sources"], list) or not request["input_data_sources"]:
        raise ValueError("input_data_sources must contain at least one source")
    if request["source_mode"] == "independent" and (request.get("upstream_context_refs") or request.get("upstream_analysis_contract")):
        raise ValueError("independent mode cannot consume upstream context or analysis contracts")
    definitions = request.get("analysis_contract", {}).get("segment_definitions", [])
    invalid_sources = {str(item.get("basis", {}).get("source") or "") for item in definitions} - ALLOWED_RULE_SOURCES
    if invalid_sources:
        raise ValueError("unsupported segment rule sources: " + ", ".join(sorted(invalid_sources)))
    resolutions = {item.get("task_field_resolution", "require_consistent") for item in definitions}
    if len(resolutions) > 1:
        raise ValueError("all segment definitions must use the same task_field_resolution")
    for source in request.get("business_rule_sources", []):
        if source.get("source") and source.get("source") not in ALLOWED_RULE_SOURCES | {"analyst_proposed"}:
            raise ValueError(f"unsupported business rule source: {source.get('source')}")
    _schema_validate(request, "input.schema.json")


def validate_formal_source_references(request: dict[str, Any]) -> None:
    """Fail closed when a formal result cannot retain a portable source reference."""
    if request.get("publication_policy", {}).get("level") != "formal":
        return
    unresolved = []
    for source in request.get("input_data_sources", []):
        raw_path = source.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            continue
        resolved = Path(raw_path).expanduser().resolve()
        try:
            resolved.relative_to(WORKSPACE_ROOT.resolve())
        except ValueError:
            unresolved.append(str(source.get("source_id") or "unidentified-source"))
    if unresolved:
        raise ValueError(
            "external_source_reference_unresolved: formal publication requires "
            "a workspace-relative source; unresolved source_id="
            + ",".join(sorted(unresolved))
            + "。请将这些数据复制到受控 workspace 后重新提交正式发布；"
            "如仅需临时分析，请改为 working 发布且不要更新 Current。"
        )


def validate_output(package: dict[str, Any], *, final: bool = False) -> None:
    expected = {"run", "scope", "effective_analysis_contract", "data_quality", "analysis_results", "findings", "evidence_items", "limitations", "handoff"}
    if final:
        expected |= {"publication", "delivery"}
    if set(package) != expected:
        raise ValueError(f"output top-level contract mismatch: expected {sorted(expected)}")
    if package.get("run", {}).get("artifact_version") != ARTIFACT_VERSION:
        raise ValueError("output artifact version mismatch")
    if set(package.get("analysis_results", {})) != set(ANALYSES):
        raise ValueError("output analysis_results contract mismatch")
    if "baseline" in package.get("handoff", {}):
        raise ValueError("handoff must reference baseline instead of copying it")
    handoff = package["handoff"]
    if any(
        not (
            ref.startswith("#/evidence_items/")
            and ref.removeprefix("#/evidence_items/").isdigit()
        )
        for ref in handoff.get("payload_refs", [])
    ):
        raise ValueError("handoff.payload_refs contains an unsupported pointer")
    if final:
        _schema_validate(package, "output.schema.json")


def combined_fingerprint(manifests: list[dict[str, Any]]) -> str:
    token = "|".join(f"{item['source_id']}:{item['fingerprint']}" for item in manifests if item.get("status") == "loaded")
    return hashlib.sha256(token.encode()).hexdigest()[:16]


def _selected_analyses(request: dict[str, Any]) -> list[str]:
    requested = request.get("requested_analyses") or request.get("requested_capabilities")
    if not requested:
        return list(ANALYSES)
    normalized = [LEGACY_ANALYSIS_NAMES.get(str(value), str(value)) for value in requested]
    return [name for name in ANALYSES if name in normalized]


def _contract(request: dict[str, Any]) -> dict[str, Any]:
    upstream = request.get("upstream_analysis_contract", {}) if request.get("source_mode") == "chain_context" else {}
    contract = deep_merge(upstream, request.get("analysis_contract", {}))
    contract["metric_framework"] = "指标-2026"
    contract["metric_definitions"] = [sanitize_metric_definition(item) for item in request.get("metric_definitions", [])]
    contract["business_thresholds"] = [sanitize_metric_definition(item) for item in request.get("business_thresholds", [])]
    contract["statistical_policy"] = {
        "default": "descriptive", "sample_reliability_required": True, "impact_scale_required": True,
        "inference": "on_demand_when_question_and_sample_support_it",
    }
    contract["rule_sources"] = request.get("business_rule_sources", [])
    return contract


def _pending_rules(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in contract.get("rule_sources", []) if item.get("confirmation_status") == "analyst_proposed_pending_confirmation"]


def _incomplete_thresholds(contract: dict[str, Any]) -> list[dict[str, Any]]:
    required = {"source", "version", "scenario_key", "time_window"}
    return [item for item in contract.get("business_thresholds", []) if not required.issubset(item) or any(item.get(key) in (None, "") for key in required)]


def _not_requested() -> dict[str, Any]:
    return {"status": "not_requested"}


def _not_evaluable(reason: str) -> dict[str, Any]:
    return {"status": "not_evaluable", "reason": reason, "reliability": {"inference_performed": False}, "limitations": [reason]}


def _infer_journey_path_delimiter(rows: list[dict[str, Any]]) -> str | None:
    """Infer only an explicit structural separator; never infer path semantics."""
    samples = [
        str(row.get("journey_path"))
        for row in rows
        if row.get("journey_path") not in (None, "")
    ][:200]
    if not samples:
        return None
    candidates = ("->", "→", "=>", "|", "＞", ">")
    scored = [
        (
            sum(value.count(candidate) for value in samples),
            sum(candidate in value for value in samples),
            len(candidate),
            candidate,
        )
        for candidate in candidates
    ]
    occurrences, covered, _, delimiter = max(scored)
    if occurrences <= 0 or covered / len(samples) < .8:
        return None
    return delimiter


def _duration_unit_from_field(field: str | None) -> str | None:
    value = str(field or "").strip().lower()
    if any(token in value for token in ("(min)", "分钟", "minute")):
        return "minutes"
    if any(token in value for token in ("(ms)", "毫秒", "millisecond")):
        return "milliseconds"
    if any(token in value for token in ("(hour)", "(hr)", "小时")):
        return "hours"
    if any(token in value for token in ("(s)", "秒", "second")):
        return "seconds"
    return None


def _infer_task_duration_unit(
    quality: dict[str, Any], source_semantics: dict[str, str]
) -> str | None:
    units = {
        unit
        for source_id, mappings in quality.get("source_field_mapping", {}).items()
        if source_semantics.get(source_id) == "task_summary"
        for unit in [
            _duration_unit_from_field(
                mappings.get("task_duration", {}).get("source_field")
            )
        ]
        if unit
    }
    return next(iter(units)) if len(units) == 1 else None


def _summary_error_analysis(rows: list[dict[str, Any]]) -> dict[str, Any]:
    values = []
    for row in rows:
        try:
            value = float(row.get("task_error_count"))
        except (TypeError, ValueError):
            continue
        if value >= 0:
            values.append((str(row.get("task_instance_id") or ""), value))
    return {
        "status": "completed",
        "observed_task_count": len(values),
        "error_event_count": int(sum(value for _, value in values)),
        "affected_task_count": sum(value > 0 for _, value in values),
        "unique_error_pattern_count": None,
        "top_error_patterns": [],
        "error_category_distribution": {},
        "error_by_step": [],
        "privacy": {"formal_output": "aggregate_task_error_count_only", "raw_error_retained": False},
        "reliability": {
            "sample_size": len(values),
            "aggregate_only": True,
            "inference_performed": False,
        },
        "limitations": ["task_summary_does_not_support_error_pattern_analysis"],
    }


def _load_store_baseline(config: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    ref = config.get("baseline_ref")
    if not ref:
        return None, None
    if not ref.get("baseline_id") or not ref.get("baseline_version"):
        return None, "baseline_ref_requires_id_and_version"
    registry = json.loads((WORKSPACE_ROOT / "shared-workflow/data-analysis/artifact-registry.json").read_text(encoding="utf-8"))
    store = next((item for item in registry.get("stores", []) if item.get("artifact_id") == "baseline-store"), None)
    if not store:
        return None, "baseline_store_not_registered"
    if store.get("current_version") != "3.0.0" or store.get("read_policy") != "explicit_baseline_ref_only":
        return None, "baseline_store_contract_incompatible"
    path = WORKSPACE_ROOT / store["path"]
    if not path.is_file():
        return None, "baseline_store_not_found"
    matches = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    matches = [item for item in matches if item.get("baseline_id") == ref["baseline_id"] and str(item.get("baseline_version")) == str(ref["baseline_version"])]
    if len(matches) != 1:
        return None, "baseline_ref_not_exactly_matched"
    item = matches[0]
    required = {"baseline_id", "baseline_version", "metric_contract_ref", "scenario_key", "grain", "comparison_fingerprint", "baseline_values"}
    if not required.issubset(item):
        return None, "baseline_store_item_contract_invalid"
    try:
        schema = json.loads((WORKSPACE_ROOT / "shared-workflow/data-analysis/schemas/baseline_item.schema.json").read_text(encoding="utf-8"))
        try:
            from jsonschema import Draft202012Validator
            Draft202012Validator(schema).validate(item)
        except ImportError:
            pass
    except (OSError, ValueError) as exc:
        return None, f"baseline_store_schema_error:{exc}"
    return item, None


def _finding(project: str, key: str, analysis: str, statement: str, refs: list[str], sample: int, impact: int, eligible: bool, forbidden: list[str] | None = None) -> dict[str, Any]:
    return {
        "finding_id": input_adapter.stable_id("finding", project, key, statement), "source_analysis": analysis,
        "claim_type": "fact", "statement": statement, "metric_refs": refs, "sample_size": sample,
        "impact_count": impact, "reliability_status": "descriptive_supported" if eligible else "limited",
        "evidence_eligible": eligible, "allowed_uses": ["objective_summary", "evidence_normalize", "business_impact_input"],
        "forbidden_uses": forbidden or ["causal_claim", "optimization_claim"],
    }


def _findings(project: str, results: dict[str, Any], eligible: dict[str, bool]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    metrics = results["metrics"]
    total = int(metrics.get("task_instance_count") or 0)
    if (
        metrics.get("status") in {"completed", "completed_with_caveats"}
        and total
        and metrics.get("completion_count") is not None
        and metrics.get("completion_rate") is not None
    ):
        findings.append(_finding(project, "completion", "metrics", f"{total} 个任务实例中有 {metrics['completion_count']} 个完成，完成率为 {metrics['completion_rate']:.1%}。", ["task_completion_rate"], total, int(metrics["completion_count"]), eligible.get("metrics", False)))
        if metrics.get("error_task_count") is not None and metrics.get("error_task_rate") is not None:
            findings.append(_finding(project, "errors", "metrics", f"报错影响 {metrics['error_task_count']} 个任务，报错任务率为 {metrics['error_task_rate']:.1%}。", ["error_task_rate"], total, int(metrics["error_task_count"]), eligible.get("errors", False)))
    largest = results["funnel"].get("largest_dropoff")
    if results["funnel"].get("status") == "completed" and largest:
        findings.append(_finding(project, "dropoff", "funnel", f"固定漏斗最大绝对掉点位于“{largest['step']}”，涉及 {largest.get('absolute_dropoff_count', 0)} 个任务。", ["funnel_dropoff"], total, int(largest.get("absolute_dropoff_count") or 0), eligible.get("funnel", False), ["problem_claim_without_threshold", "root_cause_without_triangulation"]))
    journey = results["journey"]
    if journey.get("status") == "completed" and journey.get("path_patterns"):
        item = journey["path_patterns"][0]
        findings.append(_finding(project, "top-path", "journey", f"出现次数最多的实际路径为“{' → '.join(item['path'])}”，覆盖 {item['task_count']} 个任务。", ["journey_top_path"], int(journey.get("task_instance_count") or 0), int(item["task_count"]), eligible.get("journey", False), ["problem_claim_without_rule", "causal_claim"]))
        top_five = sum(int(value.get("task_count") or 0) for value in journey["path_patterns"][:5])
        journey_total = int(journey.get("task_instance_count") or 0)
        findings.append(_finding(project, "path-concentration", "journey", f"前 5 条实际路径合计覆盖 {top_five} 个任务，占可分析旅程的 {top_five / journey_total:.1%}。", ["journey_path_concentration"], journey_total, top_five, eligible.get("journey", False), ["causal_claim", "optimization_claim"]))
        if journey.get("stage_transitions"):
            transition = journey["stage_transitions"][0]
            findings.append(_finding(project, "top-transition", "journey", f"任务覆盖最多的节点流向为“{transition['source']} → {transition['target']}”，涉及 {transition['task_count']} 个任务。", ["journey_top_transition"], journey_total, int(transition["task_count"]), eligible.get("journey", False), ["causal_claim", "optimization_claim"]))
        timed_nodes = [
            node for node in journey.get("stage_nodes", [])
            if node.get("duration_seconds", {}).get("p90") is not None
        ]
        if timed_nodes:
            slow = max(timed_nodes, key=lambda node: node["duration_seconds"]["p90"])
            findings.append(_finding(project, "high-duration-node", "journey", f"节点“{slow['label']}”的观察时长 P90 最高，为 {slow['duration_seconds']['p90']:.1f} 秒；该结果只描述耗时分布，不证明节点设计是原因。", ["journey_node_duration_p90"], journey_total, int(slow["task_count"]), eligible.get("journey", False), ["causal_claim", "optimization_claim", "problem_claim_without_threshold"]))
        if journey.get("backtrack_and_loop_paths"):
            loop_count = sum(int(value.get("task_count") or 0) for value in journey["backtrack_and_loop_paths"])
            findings.append(_finding(project, "loops", "journey", f"识别到 {loop_count} 个任务出现高频往返路径模式，需结合节点定义核查是否为必要业务分支。", ["journey_loop_pattern"], journey_total, loop_count, eligible.get("journey", False), ["causal_claim", "problem_claim_without_rule"]))
        if journey.get("blueprint_deviations"):
            deviation_count = sum(int(value.get("task_count") or 0) for value in journey["blueprint_deviations"])
            findings.append(_finding(project, "blueprint-deviation", "journey", f"在已确认蓝图覆盖范围内，记录到 {deviation_count} 次任务级偏差标记；偏差类型需分别查看，不能直接解释为问题。", ["journey_blueprint_deviation"], journey_total, deviation_count, eligible.get("journey", False) and journey.get("reliability", {}).get("journey_definition_status") == "formal_matched", ["causal_claim", "problem_claim_without_rule"]))
        cohorts = journey.get("error_cohort_paths", {})
        with_error = cohorts.get("with_error", [])
        without_error = cohorts.get("without_error", [])
        if with_error and without_error:
            findings.append(_finding(project, "error-cohort-paths", "journey", f"报错任务最常见路径为“{' → '.join(with_error[0]['path'])}”，无报错任务最常见路径为“{' → '.join(without_error[0]['path'])}”；这是同一数据窗口内的路径差异，不代表报错因果。", ["journey_error_cohort_path_comparison"], journey_total, int(with_error[0]["task_count"]), eligible.get("journey", False) and eligible.get("errors", False), ["causal_claim", "root_cause_claim", "optimization_claim"]))
    errors = results["errors"]
    if errors.get("top_error_patterns"):
        item = errors["top_error_patterns"][0]
        findings.append(_finding(project, "top-error", "errors", f"出现次数最多的安全报错模式为“{item['canonical_safe_label']}”，影响 {item['affected_task_count']} 个任务。", [item["error_signature"]], int(errors.get("error_event_count") or 0), int(item["affected_task_count"]), eligible.get("errors", False) and item.get("redaction_state") == "safe", ["raw_error_publication", "causal_claim", "problem_claim_without_threshold"]))
        if item.get("events_per_affected_task") is not None:
            findings.append(_finding(project, "top-error-density", "errors", f"该模式共出现 {item['event_count']} 次、影响 {item['affected_task_count']} 个任务，平均每个受影响任务 {item['events_per_affected_task']:.1f} 次；单任务 60 秒内最多出现 {item.get('max_events_in_60_seconds_same_task', 0)} 次。", [item["error_signature"], "error_repetition_density"], int(errors.get("error_event_count") or 0), int(item["affected_task_count"]), eligible.get("errors", False) and item.get("redaction_state") == "safe", ["instrumentation_root_cause_claim", "causal_claim", "optimization_claim"]))
        if errors.get("excluded_non_error_event_count"):
            excluded = int(errors["excluded_non_error_event_count"])
            findings.append(_finding(project, "excluded-non-errors", "errors", f"报错候选中有 {excluded} 条确认、信息或成功状态记录未进入可行动错误排行。", ["error_message_kind_distribution"], int(errors.get("candidate_error_event_count") or 0), excluded, eligible.get("errors", False), ["proof_of_no_defect", "causal_claim"]))
    elif errors.get("status") == "completed" and errors.get("error_event_count") == 0:
        observed = int(errors.get("observed_task_count") or 0)
        findings.append(_finding(project, "zero-errors", "errors", f"本次观察的 {observed} 个任务中未识别到报错事件。", ["error_event_count"], observed, 0, eligible.get("errors", False), ["proof_of_no_defect", "causal_claim"]))
    segments = results["segments"]
    if segments.get("status") == "completed" and segments.get("segments"):
        sufficient = [item for item in segments["segments"] if item.get("sample_status") == "sufficient"]
        if sufficient and segments.get("comparison_evaluable"):
            item = max(sufficient, key=lambda value: value.get("sample_size", 0))
            findings.append(_finding(project, "segment", "segments", f"样本量最大的可用业务分群为“{item['label']}”，包含 {item['sample_size']} 个任务。", ["segment_distribution"], int(segments.get("reconciliation", {}).get("task_count") or 0), int(item["sample_size"]), eligible.get("segments", False), ["problem_claim_without_threshold", "causal_claim"]))
            rates = [item for item in sufficient if item.get("completion_rate") is not None]
            if len(rates) >= 2:
                high = max(rates, key=lambda value: value["completion_rate"])
                low = min(rates, key=lambda value: value["completion_rate"])
                delta = float(high["completion_rate"]) - float(low["completion_rate"])
                findings.append(_finding(project, "segment-completion-gap", "segments", f"样本内“{high['label']}”与“{low['label']}”的完成率相差 {delta:.1%}；该差异不代表总体人群因果影响。", ["segment_completion_rate_difference"], int(segments.get("reconciliation", {}).get("task_count") or 0), int(low["sample_size"]), eligible.get("segments", False), ["population_prevalence_claim", "causal_claim", "optimization_claim"]))
        elif sufficient:
            observed = int(segments.get("reconciliation", {}).get("task_count") or 0)
            findings.append(_finding(project, "segment-single-slice", "segments", f"已完成 {observed} 个任务的分群对账，但只有一个样本充足的业务切片，本次不形成群体比较结论。", ["segment_distribution"], observed, int(sufficient[0]["sample_size"]), False, ["population_prevalence_claim", "causal_claim", "formal_evidence_upgrade"]))
        else:
            observed = int(segments.get("reconciliation", {}).get("task_count") or 0)
            findings.append(_finding(project, "segment-low-sample", "segments", f"已完成 {observed} 个任务的业务分群对账，但所有分群均低于最小样本门禁。", ["segment_distribution"], observed, observed, False, ["problem_claim", "causal_claim", "formal_evidence_upgrade"]))
    baseline = results["baseline"]
    if baseline.get("status") == "completed" and baseline.get("comparisons"):
        abnormal = [item for item in baseline["comparisons"] if item.get("anomaly_status") != "normal"]
        confidence = str((baseline.get("candidate") or {}).get("confidence") or "")
        low_confidence = confidence == "low"
        suffix = "；历史点较少，仅供观察。" if low_confidence else "。"
        findings.append(_finding(project, "baseline", "baseline", f"{len(baseline['comparisons'])} 个当前周期完成可比历史比较，其中 {len(abnormal)} 个超出正常范围{suffix}", ["baseline_comparison"], int(baseline.get("reliability", {}).get("sample_size") or 0), len(abnormal), eligible.get("baseline", False) and baseline.get("comparability", {}).get("comparable", False) and not low_confidence, ["causal_claim", "formal_evidence_upgrade"] if low_confidence else ["causal_claim"]))
    feature = results["feature_usage"]
    if feature.get("status") == "completed" and feature.get("usage_metrics"):
        item = feature["usage_metrics"][0]
        findings.append(_finding(project, "feature", "feature_usage", f"功能指标 {item['metric_id']} 的分子/分母为 {item['numerator']}/{item['denominator']}，结果为 {item.get('value') or 0:.1%}。", [item["metric_id"]], int(item["denominator"]), int(item["numerator"]), eligible.get("feature_usage", False), ["problem_claim_without_threshold", "causal_claim"]))
    return findings


def _mapping_affected_analyses(
    fields: set[str],
    contract: dict[str, Any],
    source_semantics: dict[str, str] | None = None,
) -> set[str]:
    source_semantics = source_semantics or {}
    affected: set[str] = set()
    general_dependencies = {
        "task_instance_id": {"metrics", "funnel", "journey", "errors", "segments"},
        "event_name": {"metrics", "funnel", "errors", "feature_usage"},
        "event_time": {"metrics", "funnel", "journey"},
        "journey_step": {"funnel", "journey", "errors"},
        "error_message": {"errors"}, "error_code": {"errors"},
    }
    semantic_dependencies = {
        "business_blueprint": {
            "business_scenario": {"journey"},
            "sub_business_scenario": {"journey"},
            "journey_name": {"journey"},
            "registered_node_name": {"journey"},
            "registered_node_type": {"journey"},
            "registered_node_order": {"journey"},
        },
        "aggregate_metric_summary": {},
        "error_context_detail": {
            "task_instance_id": {"errors"},
            "event_time": {"errors"},
            "journey_step": {"errors"},
            "error_message": {"errors"},
            "error_code": {"errors"},
        },
        "journey_node_detail": {
            "task_instance_id": {"funnel", "journey", "errors"},
            "event_time": {"funnel", "journey"},
            "journey_step": {"funnel", "journey", "errors"},
            "error_message": {"errors"},
            "error_code": {"errors"},
        },
        "dimension_lookup": {},
        "enterprise_state_detail": {},
    }
    canonical_fields: set[str] = set()
    for value in fields:
        source_id, separator, field = value.partition(":")
        canonical = field if separator else source_id
        canonical_fields.add(canonical)
        semantic_type = source_semantics.get(source_id) if separator else None
        dependencies = semantic_dependencies.get(
            str(semantic_type), general_dependencies
        )
        affected.update(dependencies.get(canonical, set()))
    segment_fields = {str(condition.get("field")) for item in contract.get("segment_definitions", []) for condition in item.get("conditions", [])}
    if canonical_fields & segment_fields:
        affected.add("segments")
    feature = contract.get("feature_analysis", {})
    if feature.get("subject_col") in canonical_fields or feature.get("event_col", "event_name") in canonical_fields:
        affected.add("feature_usage")
    return affected


def _evidence(findings: list[dict[str, Any]], request: dict[str, Any], run_id: str, fingerprint: str) -> list[dict[str, Any]]:
    scope = request.get("analysis_scope", {})
    return [{
        "evidence_id": input_adapter.stable_id("obj", item["finding_id"], fingerprint), "finding_ref": item["finding_id"],
        "statement": item["statement"], "claim_type": item["claim_type"], "metric_refs": item["metric_refs"],
        "sample_size": item["sample_size"], "impact_count": item["impact_count"], "reliability_status": item["reliability_status"],
        "scene_descriptor": {"project": request["project_name"], "scenario_key": scope.get("scenario_key"), "time_window": scope.get("time_window"), "where": scope.get("journey_step") or scope.get("scenario_key") or request["project_name"], "what": item["source_analysis"], "operation": "objective_measurement", "source_attribution": "objective-data-analysis", "evidence_form": "structured_metric"},
        "privacy_status": "safe", "manual_review_required": False,
        "allowed_uses": item["allowed_uses"], "forbidden_uses": item["forbidden_uses"],
        "lineage": {"run_id": run_id, "input_fingerprint": fingerprint},
    } for item in findings if item["evidence_eligible"]]


def _reconcile_metric_sources(
    calculated: dict[str, Any],
    aggregate_rows: list[dict[str, Any]],
    manifests: list[dict[str, Any]],
    tolerance: float,
) -> dict[str, Any]:
    if not aggregate_rows:
        calculated["source_reconciliation"] = {
            "status": "single_calculated_source",
            "reported_metric_candidates": [],
            "source_conflict": False,
        }
        return calculated
    aggregate = task_analyzer.analyze_aggregate_metrics(aggregate_rows)
    manifest_by_id = {str(item["source_id"]): item for item in manifests}
    candidates = []
    for item in aggregate.get("reported_metrics", []):
        manifest = manifest_by_id.get(str(item.get("source_ref")), {})
        candidates.append({
            **item,
            "metric_authority": manifest.get("metric_authority", "diagnostic"),
            "declared_scope": manifest.get("declared_scope", {}),
        })
    calculated_sources = [
        item for item in manifests
        if item.get("semantic_type") in {"task_summary", "general_event_log"}
    ]
    calculated_scope = next(
        (
            item.get("declared_scope", {}).get("scope_fingerprint")
            for item in calculated_sources
            if item.get("declared_scope", {}).get("scope_fingerprint")
        ),
        None,
    )
    conflicts = []
    for item in candidates:
        candidate_scope = item.get("declared_scope", {}).get("scope_fingerprint")
        if not calculated_scope or candidate_scope != calculated_scope:
            continue
        for metric in ("completion_rate", "one_time_completion_rate"):
            reported, detail = item.get(metric), calculated.get(metric)
            if reported is not None and detail is not None and abs(float(reported) - float(detail)) > tolerance:
                conflicts.append({
                    "metric": metric,
                    "reported_value": reported,
                    "calculated_value": detail,
                    "absolute_difference": abs(float(reported) - float(detail)),
                    "reported_source_ref": item.get("source_ref"),
                })
    official = [item for item in candidates if item.get("metric_authority") == "official"]
    matching_official = [
        item for item in official
        if calculated_scope
        and item.get("declared_scope", {}).get("scope_fingerprint") == calculated_scope
    ]
    calculated_available = any(
        calculated.get(name) is not None
        for name in ("completion_rate", "one_time_completion_rate")
    )
    calculated["source_reconciliation"] = {
        "status": "source_conflict" if conflicts else "multiple_scopes_or_sources",
        "calculated_scope_fingerprint": calculated_scope,
        "reported_metric_candidates": candidates,
        "conflicts": conflicts,
        "source_conflict": bool(conflicts),
    }
    if conflicts:
        calculated["status"] = "not_evaluable"
        calculated["reason"] = "same_scope_metric_source_conflict"
        calculated.setdefault("limitations", []).append("same-scope metric sources disagree beyond tolerance; formal metric evidence is blocked")
    elif len(matching_official) == 1 or (len(official) == 1 and not calculated_available):
        headline = matching_official[0] if matching_official else official[0]
        calculated["headline_metrics"] = {
            "source_type": "official_aggregate_metric_summary",
            "source_ref": headline["source_ref"],
            "completion_rate": headline.get("completion_rate"),
            "one_time_completion_rate": headline.get("one_time_completion_rate"),
            "task_instance_count": headline.get("task_instance_count"),
            "participant_count": headline.get("participant_count"),
            "denominator_available": headline.get("task_instance_count") is not None,
        }
        if headline.get("task_instance_count") is None:
            calculated.setdefault("limitations", []).append("official aggregate rates have no task denominator; rates are displayed but cannot form count-based evidence")
    elif len(matching_official) > 1 or (len(official) > 1 and not calculated_available):
        calculated["status"] = "not_evaluable"
        calculated["reason"] = "multiple_official_metric_rows_without_unique_scope_match"
        calculated.setdefault("limitations", []).append("multiple official aggregate metric rows could not be uniquely matched to the analysis scope")
    elif official:
        calculated.setdefault("limitations", []).append("official aggregate metrics describe a different or undeclared scope and were not used as headline metrics")
    return calculated


def build_package(request: dict[str, Any]) -> dict[str, Any]:
    validate_request(request)
    contract = _contract(request)
    selected = _selected_analyses(request)
    contract["_requested_analyses"] = selected
    rows, quality, manifests = input_adapter.preprocess(request["input_data_sources"], contract)
    contract.pop("_requested_analyses", None)
    fingerprint = combined_fingerprint(manifests)
    run_id = f"oda_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{fingerprint[:8]}"
    task_gate = quality.get("task_boundary_reliable") and "task_instance_id" not in quality.get("missing_core_mappings", [])
    source_grains = quality.get("source_data_grains", {})
    source_semantics = quality.get("source_semantic_types", {})
    aggregate_rows = [
        row for row in rows
        if source_semantics.get(str(row.get("_source_ref"))) == "aggregate_metric_summary"
    ]
    summary_rows = [
        row for row in rows
        if source_semantics.get(str(row.get("_source_ref"))) == "task_summary"
    ]
    if not contract.get("journey_path_delimiter"):
        inferred_delimiter = _infer_journey_path_delimiter(summary_rows)
        if inferred_delimiter:
            contract["journey_path_delimiter"] = inferred_delimiter
            contract["journey_path_delimiter_basis"] = "observed_structural_separator"
    if not contract.get("task_duration_unit"):
        inferred_duration_unit = _infer_task_duration_unit(quality, source_semantics)
        if inferred_duration_unit:
            contract["task_duration_unit"] = inferred_duration_unit
            contract["task_duration_unit_basis"] = "mapped_source_field_unit"
    journey_node_rows = [
        row for row in rows
        if source_semantics.get(str(row.get("_source_ref"))) == "journey_node_detail"
    ]
    general_event_rows = [
        row for row in rows
        if source_semantics.get(str(row.get("_source_ref"))) == "general_event_log"
    ]
    error_context_rows = [
        row for row in rows
        if source_semantics.get(str(row.get("_source_ref"))) == "error_context_detail"
    ]
    blueprint_rows = [
        row for row in rows
        if source_semantics.get(str(row.get("_source_ref"))) == "business_blueprint"
    ]
    enterprise_state_rows = [
        row for row in rows
        if source_semantics.get(str(row.get("_source_ref"))) == "enterprise_state_detail"
    ]
    compiled_blueprints = journey_analyzer.compile_business_blueprints(blueprint_rows)
    journey_blueprints = [
        *contract.get("journey_blueprints", []),
        *compiled_blueprints.get("formal_blueprints", []),
    ]
    duration_unit = task_analyzer._task_duration_unit(contract)
    for row in summary_rows:
        row["task_duration_seconds_normalized"] = task_analyzer._duration_seconds(
            row.get("task_duration"), duration_unit
        )
    event_rows = journey_node_rows + general_event_rows
    metric_event_rows = general_event_rows
    journey_rows = journey_node_rows or [
        row for row in general_event_rows if row.get("journey_step")
    ]
    error_rows = error_context_rows + [
        row for row in general_event_rows if row.get("event_class") == "error_event"
    ]
    error_task_ids = {
        str(row.get("task_instance_id"))
        for row in error_rows
        if row.get("task_instance_id") and row.get("event_class") == "error_event"
    }
    task_result = (
        task_analyzer.analyze_task_summaries(summary_rows, contract)
        if task_gate and summary_rows and {"metrics", "funnel", "journey"}.intersection(selected)
        else task_analyzer.analyze_tasks(metric_event_rows or rows, contract)
        if task_gate and {"metrics", "funnel"}.intersection(selected)
        else {"metrics": _not_evaluable("task_boundary_unreliable"), "funnel": _not_evaluable("task_boundary_unreliable"), "reliability": {"sample_size": 0, "inference_performed": False}}
    )
    event_task_result = (
        task_analyzer.analyze_tasks(event_rows, contract)
        if task_gate and event_rows and {"funnel", "journey"}.intersection(selected)
        else None
    )
    metrics = task_result.get("metrics", _not_requested()) if "metrics" in selected else _not_requested()
    if metrics.get("status") is None:
        metrics["status"] = task_result.get("status", "completed")
        metrics["reliability"] = task_result.get("reliability", {})
        metrics["limitations"] = []
    if "metrics" in selected:
        metrics = _reconcile_metric_sources(
            metrics,
            aggregate_rows,
            manifests,
            float(contract.get("metric_conflict_tolerance", 0.0001)),
        )
    funnel = (
        event_task_result.get("funnel", _not_evaluable("event_detail_unavailable"))
        if "funnel" in selected and event_task_result is not None
        else task_result.get("funnel", _not_requested())
        if "funnel" in selected
        else _not_requested()
    )
    baseline_config = contract.get("baseline_analysis", {})
    store_baseline, store_error = _load_store_baseline(baseline_config) if "baseline" in selected else (None, None)
    results: dict[str, Any] = {
        "metrics": metrics,
        "funnel": funnel,
        "journey": (
            journey_analyzer.analyze_rows(
                journey_rows,
                expected_steps=contract.get("expected_steps", []),
                journey_blueprints=journey_blueprints,
                error_task_ids=error_task_ids,
            )
            if "journey" in selected and task_gate and journey_rows
            else journey_analyzer.analyze_task_summaries(
                summary_rows,
                delimiter=str(contract.get("journey_path_delimiter")),
                expected_steps=contract.get("expected_steps", []),
                journey_blueprints=journey_blueprints,
                error_task_ids=error_task_ids,
            )
            if "journey" in selected and task_gate and summary_rows and contract.get("journey_path_delimiter") and any(row.get("journey_path") for row in summary_rows)
            else _not_evaluable("task_boundary_or_journey_mapping_unreliable")
            if "journey" in selected
            else _not_requested()
        ),
        "errors": (
            error_analyzer.analyze_rows(error_rows)
            if "errors" in selected and any(row.get("event_class") == "error_event" for row in error_rows)
            else _summary_error_analysis(summary_rows)
            if "errors" in selected and any(row.get("task_error_count") not in (None, "") for row in summary_rows)
            else _not_evaluable("classified_error_detail_unavailable")
            if "errors" in selected
            else _not_requested()
        ),
        "segments": task_analyzer.analyze_segments(summary_rows or metric_event_rows, contract.get("segment_definitions", []), int(contract.get("minimum_segment_sample", 30))) if "segments" in selected and task_gate else (_not_evaluable("task_boundary_unreliable") if "segments" in selected else _not_requested()),
        "baseline": baseline_analyzer.analyze_baseline(
            summary_rows or metric_event_rows,
            baseline_config,
            store_baseline,
            {
                "source_artifact_refs": [item["source_id"] for item in manifests],
                "source_item_refs": [f"{item['source_id']}#baseline-series" for item in manifests],
                "input_fingerprint": fingerprint,
                "source_run_id": run_id,
            },
        ) if "baseline" in selected and not store_error else (_not_evaluable(store_error or "baseline_unavailable") if "baseline" in selected else _not_requested()),
        "feature_usage": task_analyzer.analyze_feature_usage(general_event_rows or rows, contract.get("feature_analysis", {})) if "feature_usage" in selected else _not_requested(),
        "enterprise_states": enterprise_state_analyzer.analyze(
            enterprise_state_rows,
            contract.get("enterprise_state_analysis", {}).get("transition_rules", []),
        ) if "enterprise_states" in selected else _not_requested(),
    }
    if results["journey"].get("status") in {"completed", "completed_with_caveats"}:
        results["journey"]["business_blueprint"] = compiled_blueprints
        if compiled_blueprints.get("limitations"):
            results["journey"].setdefault("limitations", []).extend(
                compiled_blueprints["limitations"]
            )
    limitations: list[str] = []
    if quality.get("missing_core_mappings"):
        limitations.append("缺少核心字段映射：" + ", ".join(quality["missing_core_mappings"]))
    if quality.get("ambiguous_mappings"):
        limitations.append("字段存在多个候选，需要确认：" + ", ".join(quality["ambiguous_mappings"]))
    if quality.get("invalid_explicit_mappings"):
        limitations.append("显式字段映射指向不存在的列：" + ", ".join(quality["invalid_explicit_mappings"]))
    limitations.extend(f"数据源不可读：{item['source_id']}（{item.get('failure_reason')}）" for item in quality.get("source_failures", []))
    limitations.extend(
        f"维表关联 {item['lookup_source_id']} 覆盖不足，未形成正式分群比较。"
        for item in quality.get("dimension_join_results", [])
        if item.get("status") == "not_evaluable"
    )
    limitations.extend(quality.get("task_boundary_reasons", []))
    if quality.get("invalid_timestamp_count"):
        limitations.append(f"存在 {quality['invalid_timestamp_count']} 条无效时间戳，时长与顺序结果需谨慎解释。")
    pending = _pending_rules(contract)
    incomplete_thresholds = _incomplete_thresholds(contract)
    if incomplete_thresholds:
        limitations.append(f"存在 {len(incomplete_thresholds)} 条缺少来源、版本、场景或时间窗的业务阈值；不能用于异常、证据或基线候选。")
    if pending or incomplete_thresholds:
        if pending:
            limitations.append(f"存在 {len(pending)} 条待确认分析口径；仅允许探索性描述，不生成正式证据或基线候选。")
        if results["baseline"].get("candidate") is not None:
            results["baseline"]["candidate"] = None
            results["baseline"].setdefault("limitations", []).append("baseline_candidate_blocked_by_pending_rules")
    for name in selected:
        result = results[name]
        if result.get("status") == "not_evaluable":
            limitations.append(f"{name} 无法评估：{result.get('reason', 'insufficient_data')}。")
        limitations.extend(str(value) for value in result.get("limitations", []))
    mapping_affected = _mapping_affected_analyses(
        set(quality.get("ambiguous_mappings", []))
        | set(quality.get("invalid_explicit_mappings", [])),
        contract,
        source_semantics,
    )
    eligibility = {name: not pending and name not in mapping_affected for name in ANALYSES}
    for name in {"metrics", "funnel", "journey", "errors", "segments"}:
        eligibility[name] = eligibility[name] and bool(task_gate)
    if results["metrics"].get("source_reconciliation", {}).get("source_conflict"):
        eligibility["metrics"] = False
    if any(item.get("status") == "not_evaluable" for item in quality.get("dimension_join_results", [])):
        eligibility["segments"] = False
    mapped_sources = quality.get("source_field_mapping", {})
    error_signal_defined = bool(contract.get("event_mapping", {}).get("error")) or any(
        mapping.get(name, {}).get("source_field")
        for mapping in mapped_sources.values()
        for name in ("error_message", "error_code", "task_error_count")
    ) or any(row.get("event_class") == "error_event" for row in rows)
    if "errors" in selected and not error_signal_defined:
        results["errors"] = _not_evaluable("error_signal_not_defined")
        limitations.append("errors 无法评估：error_signal_not_defined。")
    eligibility["errors"] = (
        eligibility["errors"]
        and error_signal_defined
        and bool(quality.get("error_classification_reliable"))
    )
    if (
        "errors" in selected
        and error_signal_defined
        and not quality.get("error_classification_reliable")
    ):
        limitations.append(
            "报错字段存在，但缺少明确来源角色、事件映射或条件式分类规则；错误发现不得提升为正式 Evidence。"
        )
    if contract.get("feature_analysis", {}).get("subject_col") in {"task_instance_id", "session_id"}:
        eligibility["feature_usage"] = eligibility["feature_usage"] and bool(task_gate)
    findings = _findings(request["project_name"], results, eligibility)
    evidence_items = _evidence(findings, request, run_id, fingerprint)
    status = "completed_with_caveats" if limitations or quality["status"] != "ready" else "completed"
    package = {
        "run": {"run_id": run_id, "artifact_type": "objective_evidence_package", "artifact_version": ARTIFACT_VERSION, "producer_skill": "objective-data-analysis", "project_name": request["project_name"], "generated_at": utc_now(), "source_mode": request["source_mode"], "analysis_intent": request.get("analysis_intent", "comprehensive"), "status": status, "selected_analyses": selected, "sources": manifests, "combined_input_fingerprint": fingerprint},
        "scope": request.get("analysis_scope", {}), "effective_analysis_contract": contract, "data_quality": quality,
        "analysis_results": results, "findings": findings, "evidence_items": evidence_items, "limitations": list(dict.fromkeys(limitations)),
        "handoff": {"next_skill": "evidence-govern", "input_gate_status": "ready_with_caveats" if limitations else "ready", "handoff_status": ("ready_with_caveats" if limitations else "ready") if evidence_items else "blocked", "payload_refs": [f"#/evidence_items/{index}" for index in range(len(evidence_items))], "evidence_refs": [item["evidence_id"] for item in evidence_items], "analysis_result_refs": {"baseline": "#/analysis_results/baseline", "segments": "#/analysis_results/segments", "journey": "#/analysis_results/journey", "enterprise_states": "#/analysis_results/enterprise_states"}, "limitations_ref": "#/limitations", "lineage_ref": "#/run", "visualization": {"handoff_id": f"handoff-objective-visualization-{run_id}", "target_skill": "data-visualization", "handoff_type": "analysis_for_visualization", "handoff_status": "ready_with_caveats" if limitations else "ready", "payload_refs": ["#/analysis_results", "#/findings", "#/limitations"], "allowed_uses": ["visualization"], "forbidden_uses": ["recalculate_analysis", "create_metric", "upgrade_causality"], "required_review_request_ids": [], "caveats": list(limitations)}, "allowed_uses": ["evidence_governance", "problem_impact_input", "explicit_visualization"], "forbidden_uses": ["causal_claim_without_governance", "automatic_store_write", "automatic_visualization"]},
    }
    validate_output(package)
    return package


def _transactional_publish(files: dict[Path, str | None]) -> None:
    staged: dict[Path, str] = {}
    originals: dict[Path, str | None] = {}
    try:
        for path, content in files.items():
            originals[path] = path.read_text(encoding="utf-8") if path.exists() else None
            if content is not None:
                path.parent.mkdir(parents=True, exist_ok=True)
                descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
                with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                    handle.write(content); handle.flush(); os.fsync(handle.fileno())
                staged[path] = temporary
        for path, content in files.items():
            if content is None:
                if path.exists():
                    path.unlink()
            else:
                os.replace(staged.pop(path), path)
    except Exception:
        for path, content in originals.items():
            if content is None:
                if path.exists():
                    path.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.restore.", dir=path.parent)
                with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                    handle.write(content); handle.flush(); os.fsync(handle.fileno())
                os.replace(temporary, path)
        raise
    finally:
        for temporary in staged.values():
            if os.path.exists(temporary):
                os.unlink(temporary)


def run(request_path: Path, output_root: Path) -> dict[str, Any]:
    request = json.loads(request_path.read_text(encoding="utf-8"))
    shared_required = {
        "invocation_context", "analysis_purpose", "input_bindings",
        "requested_deliverables", "publication_policy", "retention_policy",
    }
    missing = sorted(shared_required - set(request))
    if missing:
        raise ValueError(
            "formal run requires shared request dimensions: " + ", ".join(missing)
        )
    validate_formal_source_references(request)
    package = build_package(request)
    prepared = contract_runtime.apply_request_envelope(package, request)
    validate_output(prepared, final=True)
    workspace_root = output_root.parent if output_root.name == "spark-output" else output_root
    registry_path = WORKSPACE_ROOT / "shared-workflow/data-analysis/artifact-registry.json"
    with tempfile.TemporaryDirectory() as directory:
        temporary = Path(directory)
        candidate = temporary / "candidate.json"
        candidate.write_text(
            json.dumps(prepared, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        deliverables: list[dict[str, Any]] = []
        for item in request["requested_deliverables"]:
            bound = dict(item)
            if item["format"] == "markdown":
                report = temporary / "objective-analysis-report.md"
                report.write_text(
                    report_renderer.render_markdown(prepared), encoding="utf-8"
                )
                bound["source_path"] = str(report)
            deliverables.append(bound)
        reference = contract_runtime.publish_result(
            workspace_root=workspace_root,
            registry_path=registry_path,
            artifact_id="objective",
            candidate_path=candidate,
            purpose_key=request["analysis_purpose"]["purpose_key"],
            purpose_label=request["analysis_purpose"]["purpose_label"],
            deliverables=deliverables,
        )
    return contract_runtime.load_json(workspace_root / reference["artifact_path"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Objective Data Analysis 4.0.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--output-root", default="spark-output")
    args = parser.parse_args()
    package = run(Path(args.request).expanduser().resolve(), Path(args.output_root).expanduser().resolve())
    print(json.dumps({
        "status": package["run"]["status"],
        "run_id": package["run"]["run_id"],
        "purpose": package["publication"]["analysis_purpose_key"],
        "publication": package["publication"]["status"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
