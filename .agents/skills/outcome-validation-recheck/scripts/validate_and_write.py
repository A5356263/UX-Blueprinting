#!/usr/bin/env python3
"""Validate and publish Outcome Validation Recheck 4.0 immutable results."""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = SKILL_ROOT.parents[2]
INPUT_SCHEMA = SKILL_ROOT / "schemas/input.schema.json"
OUTPUT_SCHEMA = SKILL_ROOT / "schemas/output.schema.json"
REGISTRY = PROJECT_ROOT / "shared-workflow/data-analysis/artifact-registry.json"
RUNTIME_DIR = PROJECT_ROOT / "shared-workflow/data-analysis/runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))
import contract_runtime

MODE_STAGES = {
    "readiness_validation": {"pre_launch", "demo"},
    "effectiveness_validation": {"pilot", "post_launch"},
    "durability_monitoring": {"long_term", "regression_monitoring"},
}
FORBIDDEN_FIELDS = {
    "validation_runs",
    "validation_readiness",
    "validation_results",
    "deviation_diagnoses",
    "pattern_learning_signals",
    "lifecycle_feedback",
    "regression_monitoring_requests",
    "patch_requests",
}


class ContractError(ValueError):
    pass


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _fragment(document: Any, pointer: str) -> Any:
    current = document
    if not pointer:
        return current
    if not pointer.startswith("/"):
        raise ContractError(f"Unsupported JSON Schema fragment: #{pointer}")
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or token not in current:
            raise ContractError(f"Unresolvable JSON Schema fragment: #{pointer}")
        current = current[token]
    return current


def _type_matches(value: Any, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected, True)


def _schema_matches(
    value: Any,
    schema: Any,
    document: dict[str, Any],
    document_path: Path,
    location: str,
) -> bool:
    try:
        _validate_schema(value, schema, document, document_path, location)
        return True
    except ContractError:
        return False


def _validate_schema(
    value: Any,
    schema: Any,
    document: dict[str, Any],
    document_path: Path,
    location: str,
) -> None:
    if schema is True:
        return
    if schema is False:
        raise ContractError(f"{location}: disallowed by schema")
    if not isinstance(schema, dict):
        raise ContractError(f"{location}: invalid schema node")

    reference = schema.get("$ref")
    if reference:
        file_part, _, fragment = reference.partition("#")
        if file_part:
            target_path = (document_path.parent / file_part).resolve()
            target_document = load_json(target_path)
        else:
            target_path = document_path
            target_document = document
        target_schema = _fragment(target_document, fragment)
        _validate_schema(
            value, target_schema, target_document, target_path, location
        )

    for item in schema.get("allOf", []):
        _validate_schema(value, item, document, document_path, location)
    if "anyOf" in schema and not any(
        _schema_matches(value, item, document, document_path, location)
        for item in schema["anyOf"]
    ):
        raise ContractError(f"{location}: does not match any allowed schema")
    if "oneOf" in schema:
        matches = sum(
            _schema_matches(value, item, document, document_path, location)
            for item in schema["oneOf"]
        )
        if matches != 1:
            raise ContractError(f"{location}: must match exactly one schema")
    if "if" in schema and _schema_matches(
        value, schema["if"], document, document_path, location
    ):
        if "then" in schema:
            _validate_schema(
                value, schema["then"], document, document_path, location
            )

    expected = schema.get("type")
    if expected:
        types = expected if isinstance(expected, list) else [expected]
        if not any(_type_matches(value, item) for item in types):
            raise ContractError(f"{location}: expected type {types}")
    if "const" in schema and value != schema["const"]:
        raise ContractError(f"{location}: expected constant {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        raise ContractError(f"{location}: value is outside enum")

    if isinstance(value, dict):
        missing = [key for key in schema.get("required", []) if key not in value]
        if missing:
            raise ContractError(f"{location}: missing required fields {missing}")
        properties = schema.get("properties", {})
        for key, child_schema in properties.items():
            if key in value:
                _validate_schema(
                    value[key],
                    child_schema,
                    document,
                    document_path,
                    f"{location}/{key}",
                )
        if schema.get("additionalProperties") is False:
            unknown = sorted(set(value) - set(properties))
            if unknown:
                raise ContractError(f"{location}: unknown fields {unknown}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            raise ContractError(f"{location}: too few items")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, ensure_ascii=False, sort_keys=True) for item in value]
            if len(encoded) != len(set(encoded)):
                raise ContractError(f"{location}: duplicate items are not allowed")
        if "items" in schema:
            for index, item in enumerate(value):
                _validate_schema(
                    item,
                    schema["items"],
                    document,
                    document_path,
                    f"{location}/{index}",
                )
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise ContractError(f"{location}: string is too short")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            raise ContractError(f"{location}: string does not match pattern")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            raise ContractError(f"{location}: number is below minimum")


def schema_validate(instance: Any, schema_path: Path) -> None:
    schema = load_json(schema_path)
    _validate_schema(instance, schema, schema, schema_path.resolve(), "$")


def _validate_handoff_release(
    handoff: dict[str, Any],
    instance_ref: dict[str, Any],
    decisions: list[dict[str, Any]],
    required_action: str,
) -> None:
    status = handoff.get("handoff_status")
    if status not in {"ready", "ready_with_caveats", "pending_review"}:
        raise ContractError("Handoff is not ready")
    required = set(handoff.get("required_review_request_ids", []))
    decision_by_id = {
        item.get("review_request_id"): item for item in decisions if isinstance(item, dict)
    }
    if status == "pending_review" and not required:
        raise ContractError("pending_review Handoff does not declare required reviews")
    for review_id in required:
        decision = decision_by_id.get(review_id)
        if not decision or decision.get("decision") != "approved":
            raise ContractError(f"Required review is not approved: {review_id}")
        if decision.get("source_artifact_instance_ref") != instance_ref:
            raise ContractError(
                f"Review Artifact Instance does not match Handoff: {review_id}"
            )
        if decision.get("handoff_id") != handoff.get("handoff_id"):
            raise ContractError(f"Review handoff_id does not match: {review_id}")
        if not set(handoff.get("payload_refs", [])).issubset(
            set(decision.get("payload_refs", []))
        ):
            raise ContractError(f"Review does not cover Handoff Payload: {review_id}")
        if required_action not in decision.get("approved_actions", []):
            raise ContractError(
                f"Review does not approve {required_action}: {review_id}"
            )


def validate_input(payload: dict[str, Any]) -> None:
    schema_validate(payload, INPUT_SCHEMA)
    run = payload["run"]
    mode = run["validation_mode"]
    stage = run["validation_stage"]
    if stage not in MODE_STAGES[mode]:
        raise ContractError(f"{mode} cannot run at {stage}")

    root = payload["root_cause_handoff"]
    root_ref = payload["root_artifact_instance_ref"]
    if root_ref.get("producer_skill") != "root-cause-synthesis":
        raise ContractError("Outcome requires a Root Cause handoff")
    if root.get("target_skill") != "outcome-validation-recheck":
        raise ContractError("Root Cause handoff is not addressed to Outcome")
    if root_ref.get("artifact_id") != "root-cause":
        raise ContractError("Root Cause handoff must reference the root-cause Artifact")
    if root.get("handoff_type") != "root_cause_hypothesis_for_outcome":
        raise ContractError("Root Cause handoff type is not allowed for Outcome")
    if "outcome_validation" not in root.get("allowed_uses", []):
        raise ContractError("Root Cause handoff does not allow outcome_validation")
    _validate_handoff_release(
        root, root_ref, payload.get("review_decisions", []), "outcome_validation"
    )

    intervention = payload["intervention_contract"]
    if intervention["validation_stage"] != stage:
        raise ContractError("Intervention Contract stage does not match the requested stage")
    if intervention["approval_status"] not in {"approved", "approved_with_caveats"}:
        raise ContractError("Intervention Contract is not approved for validation")

    govern = payload.get("govern_handoff")
    evidence = payload["governed_validation_evidence"]
    if mode != "readiness_validation":
        if not govern:
            raise ContractError("Effectiveness and durability require a Govern handoff")
        govern_ref = payload.get("govern_artifact_instance_ref") or {}
        if govern_ref.get("producer_skill") != "evidence-govern":
            raise ContractError("Validation evidence must come through Evidence Govern")
        if govern.get("target_skill") != "outcome-validation-recheck":
            raise ContractError("Govern handoff is not addressed to Outcome")
        if govern_ref.get("artifact_id") != "governed":
            raise ContractError("Govern handoff must reference the governed Artifact")
        if govern.get("handoff_type") != "governed_evidence_for_outcome":
            raise ContractError("Govern handoff type is not allowed for Outcome")
        if "outcome_validation" not in govern.get("allowed_uses", []):
            raise ContractError("Govern handoff does not allow outcome_validation")
        _validate_handoff_release(
            govern, govern_ref, payload.get("review_decisions", []), "outcome_validation"
        )
        if not evidence["evidence_refs"]:
            raise ContractError("Effectiveness and durability require governed evidence refs")
        if not evidence["core_metric_refs"]:
            raise ContractError("Effectiveness and durability require core metric refs")


def validate_registered_inputs(payload: dict[str, Any]) -> None:
    """Resolve every formal upstream instance and its exact registered Handoff."""
    registry = load_json(REGISTRY)
    project_name = payload["run"]["project_name"]
    checks = [(
        payload["root_artifact_instance_ref"],
        payload["root_cause_handoff"],
        "root-cause",
        "root-cause-synthesis",
    )]
    if payload.get("govern_artifact_instance_ref") is not None:
        checks.append((
            payload["govern_artifact_instance_ref"],
            payload["govern_handoff"],
            "governed",
            "evidence-govern",
        ))
    for instance_ref, handoff, artifact_id, producer in checks:
        if (
            instance_ref.get("artifact_id") != artifact_id
            or instance_ref.get("producer_skill") != producer
        ):
            raise ContractError(f"{artifact_id} Artifact Instance identity mismatch")
        try:
            source, _ = contract_runtime.validate_instance_ref(
                instance_ref,
                workspace_root=PROJECT_ROOT,
                registry=registry,
            )
            registered = {
                item.get("handoff_id"): item
                for item in source.get("downstream_handoffs", [])
            }
            if registered.get(handoff.get("handoff_id")) != handoff:
                raise ContractError(f"{artifact_id} Handoff is not exactly registered")
            contract_runtime.validate_handoff(
                handoff,
                source_reference=instance_ref,
                target_skill="outcome-validation-recheck",
                required_use="outcome_validation",
                source_payload=source,
                reviews=payload.get("review_decisions", []),
            )
        except contract_runtime.ContractRuntimeError as exc:
            raise ContractError(str(exc)) from exc
        if source.get("run", {}).get("project_name") != project_name:
            raise ContractError(f"{artifact_id} project_name mismatch")


def _all_not_ready(assessment: dict[str, Any]) -> bool:
    readiness = assessment["readiness"]
    return any(
        readiness[key] in {"not_ready", "unknown"}
        for key in ("baseline", "observation_window", "exposure", "implementation_fidelity", "measurement")
    )


def validate_output(
    payload: dict[str, Any], source_input: dict[str, Any] | None = None
) -> None:
    schema_payload = copy.deepcopy(payload)
    schema_payload.setdefault("publication", {
        "status": "candidate",
        "analysis_purpose_key": "outcome-validation",
        "analysis_purpose_label": "效果验证与回检",
        "update_current_for_purpose": False,
    })
    schema_payload.setdefault("delivery", {
        "status": "not_requested", "requested": [], "files": []
    })
    schema_payload["run"].setdefault("invocation_context", "chain_context")
    schema_payload["run"].setdefault(
        "analysis_purpose",
        {"purpose_key": "outcome-validation", "purpose_label": "效果验证与回检"},
    )
    schema_payload["run"].setdefault("status", "completed")
    schema_validate(schema_payload, OUTPUT_SCHEMA)
    run = payload["run"]
    contract = payload["analysis_contract"]
    results = payload["analysis_results"]
    assessment = results["validation_assessment"]

    if run["artifact_version"] != "4.0.0":
        raise ContractError("Outcome write contract must be 4.0.0")
    old = FORBIDDEN_FIELDS.intersection(set(payload).union(set(results)))
    if old:
        raise ContractError(f"Removed fields present: {sorted(old)}")
    mode = contract["validation_mode"]
    stage = contract["validation_stage"]
    if stage not in MODE_STAGES[mode]:
        raise ContractError(f"{mode} cannot run at {stage}")
    if assessment["validation_mode"] != mode or assessment["validation_stage"] != stage:
        raise ContractError("Assessment mode/stage differs from analysis_contract")
    if source_input:
        source_run = source_input["run"]
        if (mode, stage) != (
            source_run["validation_mode"],
            source_run["validation_stage"],
        ):
            raise ContractError("Input and output mode/stage differ")

    effect = assessment["intervention_effectiveness"]
    attribution = assessment["attribution"]
    readiness = assessment["readiness"]
    if stage in {"pre_launch", "demo"}:
        if effect != "not_applicable":
            raise ContractError("Pre-launch and demo cannot conclude intervention effect")
        if attribution["strength"] != "not_applicable":
            raise ContractError("Pre-launch and demo cannot attribute intervention effect")
    else:
        if _all_not_ready(assessment) and effect != "not_evaluable":
            raise ContractError("Missing readiness dimensions require not_evaluable effect")
        if (
            readiness["exposure"] != "ready"
            or readiness["implementation_fidelity"] != "ready"
        ) and effect in {
            "effective",
            "partially_effective",
            "ineffective",
            "mixed",
            "harmful",
        }:
            raise ContractError("Effect requires ready exposure and implementation fidelity")

    critical_harm = any(
        item["critical"] and item["result_status"] == "worsened"
        for item in assessment["guardrail_outcomes"] + assessment["segment_outcomes"]
    )
    if critical_harm and effect not in {"mixed", "harmful"}:
        raise ContractError("Critical guardrail or segment harm must yield mixed or harmful")
    if attribution["confounding_risk"] == "high" and attribution["strength"] not in {
        "associational_only",
        "unknown",
    }:
        raise ContractError("High confounding risk cannot support causal attribution")
    if attribution["strength"] == "causal_supported" and attribution["confounding_risk"] != "low":
        raise ContractError("causal_supported requires low confounding risk")

    attribution_rank = {
        "not_applicable": 0,
        "unknown": 1,
        "associational_only": 2,
        "causal_suggestive": 3,
        "causal_supported": 4,
    }
    measurements = results["effect_measurements"]
    measurement_ids: set[str] = set()
    measurement_keys: set[str] = set()
    if stage in {"pre_launch", "demo"} and measurements:
        raise ContractError("Pre-launch and demo cannot emit observed effect measurements")
    for measurement in measurements:
        measurement_id = measurement["measurement_id"]
        if measurement_id in measurement_ids:
            raise ContractError(f"Duplicate effect measurement_id: {measurement_id}")
        measurement_ids.add(measurement_id)
        scope = measurement["measurement_scope"]
        scope_key = json.dumps(
            [measurement["metric_ref"], scope],
            ensure_ascii=False,
            sort_keys=True,
        )
        if scope_key in measurement_keys:
            raise ContractError(
                "Duplicate metric_ref and measurement_scope in effect measurements"
            )
        measurement_keys.add(scope_key)
        metric_type = measurement["metric_type"]
        grain = scope["grain"]
        if metric_type == "nps" and grain != "survey_response":
            raise ContractError("NPS effect measurement must use survey_response grain")
        if metric_type == "enterprise_state_transition" and grain not in {
            "enterprise",
            "enterprise_x_business_board",
        }:
            raise ContractError(
                "Enterprise transition effect must use enterprise grain"
            )
        baseline = measurement["baseline_value"]
        comparison = measurement["comparison_value"]
        change = measurement["absolute_change"]
        if measurement["result_status"] == "not_evaluable":
            if any(value is not None for value in (baseline, comparison, change)):
                raise ContractError(
                    "not_evaluable effect measurement cannot carry numeric change"
                )
        else:
            if any(value is None for value in (baseline, comparison, change)):
                raise ContractError(
                    "evaluable effect measurement requires baseline, comparison and change"
                )
            if abs(float(comparison) - float(baseline) - float(change)) > 1e-9:
                raise ContractError(
                    "effect measurement absolute_change does not reconcile"
                )
        if attribution_rank[measurement["attribution_strength"]] > attribution_rank[
            attribution["strength"]
        ]:
            raise ContractError(
                "effect measurement attribution exceeds assessment attribution"
            )

    for relationship in results["outcome_relationships"]:
        if stage in {"pre_launch", "demo"} and relationship["relation_type"] not in {
            "hypothetical",
            "supporting",
            "validation_needed",
        }:
            raise ContractError("Pre-launch/demo relationships cannot claim observed effects")
        if relationship["relation_type"] == "validated_effect" and relationship[
            "effect_attribution_confidence"
        ] != "causal_supported":
            raise ContractError("validated_effect requires causal_supported attribution")

    for reroute in results["reroute_decisions"]:
        if reroute["full_chain_rerun"] is not False:
            raise ContractError("Outcome cannot request an automatic full-chain rerun")
    for request in results["outcome_evidence_patch_requests"]:
        if request["target_processor"] != "evidence-govern":
            raise ContractError("Evidence change requests must return to Evidence Govern")
        if request["can_auto_apply"] is not False:
            raise ContractError("Outcome cannot apply Evidence patches")
    for signal in results["root_cause_feedback_signals"]:
        if signal["govern_absorption_required"] is not True:
            raise ContractError("Root Cause feedback must first be absorbed by Evidence Govern")
    for signal in results["pattern_observation_signals"]:
        if signal["can_form_pattern"] is not False:
            raise ContractError("Outcome emits observations, not reusable patterns")

    for requirement in results["monitoring_requirements"]:
        policy_refs = [
            requirement["threshold_policy_ref"],
            requirement["cadence_policy_ref"],
            requirement["notification_policy_ref"],
        ]
        if requirement["can_schedule"] is not False:
            raise ContractError("Outcome cannot create schedules")
        if requirement["status"] == "ready_for_automation_controller" and not all(policy_refs):
            raise ContractError("Automation-ready monitoring requires all approved policy refs")
        if not all(policy_refs) and requirement["status"] == "ready_for_automation_controller":
            raise ContractError("Missing policies must remain proposal or blocked")

    review_ids = {item["review_id"] for item in payload["manual_review_requests"]}
    for handoff in payload["downstream_handoffs"]:
        if not set(handoff.get("required_review_request_ids", [])).issubset(review_ids):
            raise ContractError("Handoff references an unknown manual review")
        target = handoff["target_skill"]
        if target == "business-impact" and (
            stage in {"pre_launch", "demo"} or effect == "not_evaluable"
        ):
            raise ContractError("Business Impact cannot consume an unmeasured effect")
        if target == "evidence-archive":
            if "persist_in_archive" not in handoff.get("allowed_uses", []):
                raise ContractError("Archive handoff requires persist_in_archive")
            if not handoff.get("required_review_request_ids"):
                raise ContractError("Archive handoff requires explicit authorization review")

    if any(value is not False for value in payload["write_safety"].values()):
        raise ContractError("Outcome write safety flags must all be false")


def atomic_write(payload: dict[str, Any], output: Path) -> Path:
    payload = json.loads(json.dumps(payload))
    payload["run"]["write_status"] = "written"
    validate_output(payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    fd, temp_name = tempfile.mkstemp(prefix=".outcome-", suffix=".tmp", dir=output.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, output)
        return output
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def render_markdown(payload: dict[str, Any]) -> str:
    labels = {
        "mixed": "结果有改善也有风险",
        "improved": "已改善",
        "stable": "保持稳定",
        "worsened": "出现恶化",
        "not_evaluable": "当前条件不足以判断",
        "causal_suggestive": "存在因果支持，但仍需保留限制",
        "associational_only": "仅支持相关关系",
        "low": "低",
        "medium": "中",
        "high": "高",
        "unknown": "未知",
    }
    run = payload["run"]
    assessment = payload["analysis_results"]["validation_assessment"]
    decision = assessment.get("decision", {})
    if not isinstance(decision, dict):
        decision = {"status": decision}
    attribution = assessment.get("attribution", {})
    lines = [
        f"# {run['project_name']} · 效果验证报告",
        "",
        "## 验证判断",
        "",
        f"- 阶段：{payload['analysis_contract'].get('validation_stage')}",
        f"- 判断：{labels.get(decision.get('status'), decision.get('status')) or assessment.get('status') or '未形成'}",
        f"- 判断理由：{decision.get('reason', '未说明')}",
        f"- 下一步：{decision.get('next_action', '未说明')}",
        f"- 归因强度：{labels.get(attribution.get('strength', 'unknown'), attribution.get('strength', 'unknown'))}",
        f"- 混杂风险：{labels.get(attribution.get('confounding_risk', 'unknown'), attribution.get('confounding_risk', 'unknown'))}",
        f"- 混杂因素：{'；'.join(attribution.get('confounding_factors', [])) or '未发现'}",
        "",
        "## 关键结果",
        "",
    ]
    for label, key in (
        ("主要指标", "primary_outcomes"),
        ("护栏指标", "guardrail_outcomes"),
        ("分群结果", "segment_outcomes"),
    ):
        for item in assessment.get(key, []):
            reference = (
                item.get("metric_ref")
                or item.get("segment_ref")
                or item.get("outcome_ref")
                or "未命名结果"
            )
            status = item.get("result_status", "未评估")
            lines.append(f"- {label} · {reference}：{labels.get(status, status)}")
    if not any(
        assessment.get(key)
        for key in ("primary_outcomes", "guardrail_outcomes", "segment_outcomes")
    ):
        lines.append("- 暂无可评估结果")
    lines += ["", "## 限制", ""]
    for item in payload.get("limitations", []):
        if isinstance(item, dict):
            lines.append(
                f"- {item.get('affected_scope', '当前结论')}："
                f"{item.get('conclusion_impact', item.get('description', '存在限制'))}；"
                f"建议：{item.get('required_action', '补充验证')}"
            )
        else:
            lines.append(f"- {item}")
    if not payload.get("limitations"):
        lines.append("- 无额外限制")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "write", "publish"):
        command = sub.add_parser(name)
        command.add_argument("--input", required=True, type=Path)
        command.add_argument("--candidate", required=True, type=Path)
        if name == "write":
            command.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    source_input = load_json(args.input)
    candidate = load_json(args.candidate)
    validate_input(source_input)
    validate_registered_inputs(source_input)
    validate_output(candidate, source_input)
    if args.command == "write":
        path = atomic_write(candidate, args.output)
        print(f"candidate written: {path}")
    elif args.command == "publish":
        prepared = contract_runtime.apply_request_envelope(candidate, source_input)
        validate_output(prepared, source_input)
        with tempfile.TemporaryDirectory() as directory:
            candidate_path = Path(directory) / "candidate.json"
            report_path = Path(directory) / "report.md"
            atomic_write(prepared, candidate_path)
            report_path.write_text(render_markdown(prepared), encoding="utf-8")
            deliverables = []
            for item in source_input["requested_deliverables"]:
                value = dict(item)
                if value["format"] == "markdown":
                    value["source_path"] = str(report_path)
                deliverables.append(value)
            reference = contract_runtime.publish_result(
                workspace_root=PROJECT_ROOT,
                registry_path=REGISTRY,
                artifact_id="outcome",
                candidate_path=candidate_path,
                purpose_key=source_input["analysis_purpose"]["purpose_key"],
                purpose_label=source_input["analysis_purpose"]["purpose_label"],
                deliverables=deliverables,
            )
        print(json.dumps(reference, ensure_ascii=False, indent=2))
    else:
        print("valid: Outcome Validation Recheck 3.0 input and output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
