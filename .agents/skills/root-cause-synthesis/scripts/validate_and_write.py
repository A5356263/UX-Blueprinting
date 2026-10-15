#!/usr/bin/env python3
"""Validate and publish Root Cause Synthesis 3.0 immutable results."""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import tempfile
import sys
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

FORBIDDEN_FIELDS = {
    "evidence_chains",
    "counter_evidence",
    "alternative_explanations",
    "causal_confidence_assessments",
    "outcome_metric_hypotheses",
    "hypothesis_ledger_items",
    "validation_plans",
    "root_cause_relation_graph_patches",
    "regression_monitoring_requests",
}
CONCRETE_SOLUTION_PATTERN = re.compile(
    r"(按钮|弹窗|tooltip|页面布局|组件方案|客服话术|灰度比例|上线范围|"
    r"\bbutton\b|\bmodal\b|\btooltip\b|\brollout\b)",
    re.IGNORECASE,
)
NUMERIC_UPLIFT_PATTERN = re.compile(r"(提升|增长|下降|降低)\s*\d+(?:\.\d+)?\s*%")


class ContractError(ValueError):
    pass


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_pointer(document: Any, pointer: str) -> Any:
    if not pointer.startswith("#/"):
        raise ContractError(f"Invalid absolute JSON Pointer: {pointer}")
    current = document
    for raw in pointer[2:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


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


def validate_input(payload: dict[str, Any]) -> None:
    schema_validate(payload, INPUT_SCHEMA)
    run = payload.get("run", {})
    mode = run.get("run_mode")
    handoff = payload.get("govern_handoff", {})
    context = payload.get("governed_context", {})
    instance_ref = payload.get("govern_artifact_instance_ref", {})

    if instance_ref.get("artifact_id") != "governed":
        raise ContractError("Root Cause input must reference the governed Artifact ID")
    if instance_ref.get("producer_skill") != "evidence-govern":
        raise ContractError("Root Cause input must come from evidence-govern")
    if handoff.get("target_skill") != "root-cause-synthesis":
        raise ContractError("Missing Root Cause consumer-specific handoff")
    if handoff.get("handoff_status") not in {
        "ready",
        "ready_with_caveats",
        "pending_review",
    }:
        raise ContractError("Govern handoff is not released for Root Cause")
    if "causal_synthesis" not in handoff.get("allowed_uses", []):
        raise ContractError("Govern handoff does not allow causal_synthesis")
    required_reviews = set(handoff.get("required_review_request_ids", []))
    decisions = {
        item.get("review_request_id"): item
        for item in payload.get("review_decisions", [])
        if isinstance(item, dict)
    }
    for review_id in required_reviews:
        decision = decisions.get(review_id)
        if not decision or decision.get("decision") != "approved":
            raise ContractError(f"Required review is not approved: {review_id}")
        if decision.get("source_artifact_instance_ref") != instance_ref:
            raise ContractError(f"Review Artifact Instance does not match Handoff: {review_id}")
        if decision.get("handoff_id") != handoff.get("handoff_id"):
            raise ContractError(f"Review does not bind this Handoff: {review_id}")
        if not set(handoff.get("payload_refs", [])).issubset(
            set(decision.get("payload_refs", []))
        ):
            raise ContractError(f"Review does not cover Handoff Payload: {review_id}")
        if "causal_synthesis" not in decision.get("approved_actions", []):
            raise ContractError(f"Review does not approve causal_synthesis: {review_id}")
    if handoff.get("handoff_status") == "pending_review" and not required_reviews:
        raise ContractError("pending_review Handoff does not declare required reviews")
    if context.get("evidence_basis") == "insufficient":
        if context.get("root_cause_readiness") != "blocked":
            raise ContractError("insufficient evidence basis must be blocked")
    cases = context.get("reviewed_outcome_case_refs", [])
    if mode == "outcome_feedback_refresh" and len(cases) < 1:
        raise ContractError("Outcome feedback refresh requires a Govern-absorbed reviewed case")
    if mode == "pattern_candidate_learning" and len(cases) < 2:
        raise ContractError("Pattern learning requires at least two reviewed cases")


def validate_registered_govern_handoff(payload: dict[str, Any]) -> None:
    """Resolve the official chain input against Registry and the current Govern artifact."""
    registry = load_json(REGISTRY)
    entry = next(
        (
            item
            for item in registry.get("artifacts", [])
            if item.get("artifact_id") == "governed"
        ),
        None,
    )
    if not entry:
        raise ContractError("governed Artifact is not registered")
    try:
        governed, _ = contract_runtime.validate_instance_ref(
            payload["govern_artifact_instance_ref"],
            workspace_root=PROJECT_ROOT,
            registry=registry,
        )
    except contract_runtime.ContractRuntimeError as exc:
        raise ContractError(str(exc)) from exc
    run = governed.get("run", {})
    handoff = payload["govern_handoff"]
    if run.get("artifact_version") != entry.get("current_version"):
        raise ContractError("Govern artifact version is not current")
    if run.get("producer_skill") != "evidence-govern":
        raise ContractError("Govern producer does not match Registry")
    if run.get("project_name") != payload["run"].get("project_name"):
        raise ContractError("Govern project_name does not match Root Cause request")
    if run.get("run_id") != payload["govern_artifact_instance_ref"].get("run_id"):
        raise ContractError("Govern run_id does not match Artifact Instance")
    registered = {
        item.get("handoff_id"): item
        for item in governed.get("downstream_handoffs", [])
        if item.get("target_skill") == "root-cause-synthesis"
    }
    if registered.get(handoff.get("handoff_id")) != handoff:
        raise ContractError("Root Cause handoff is not the exact registered Govern handoff")
    for pointer in handoff.get("payload_refs", []):
        try:
            _resolve_pointer(governed, pointer)
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ContractError(
                f"Root Cause handoff contains an unresolvable Govern pointer: {pointer}"
            ) from exc


def confidence_ceiling(candidate: dict[str, Any], payload: dict[str, Any]) -> str:
    basis = payload["analysis_contract"]["evidence_basis"]
    forbidden = set(payload["handoff"].get("forbidden_uses", []))
    counters = candidate.get("counter_evidence", [])
    alternatives = candidate.get("alternative_explanations", [])
    if basis in {"single_source", "contested", "insufficient"}:
        return "low" if basis != "insufficient" else "insufficient"
    if "causal_claim" in forbidden:
        return "low"
    if any(
        item.get("strength") == "strong"
        and item.get("resolution_status") in {"unresolved", "partially_explained"}
        for item in counters
    ):
        return "low"
    if any(item.get("status") == "stronger_than_primary" for item in alternatives):
        return "low"
    dimensions = candidate.get("causal_confidence", {}).get("dimensions", {})
    if dimensions.get("confounding_risk") == "high":
        return "low"
    if any(
        dimensions.get(key) in {"low", "unknown"}
        for key in ("source_independence", "temporal_alignment", "journey_alignment")
    ):
        return "medium"
    return "high"


def validate_output(payload: dict[str, Any], source_input: dict[str, Any] | None = None) -> None:
    schema_payload = copy.deepcopy(payload)
    schema_payload.setdefault("publication", {
        "status": "candidate",
        "analysis_purpose_key": "root-cause",
        "analysis_purpose_label": "候选根因综合",
        "update_current_for_purpose": False,
    })
    schema_payload.setdefault("delivery", {
        "status": "not_requested", "requested": [], "files": []
    })
    schema_payload["run"].setdefault("invocation_context", "chain_context")
    schema_payload["run"].setdefault(
        "analysis_purpose",
        {"purpose_key": "root-cause", "purpose_label": "候选根因综合"},
    )
    schema_payload["run"].setdefault("status", "completed")
    schema_validate(schema_payload, OUTPUT_SCHEMA)
    run = payload.get("run", {})
    contract = payload.get("analysis_contract", {})
    results = payload.get("analysis_results", {})
    handoff = payload.get("handoff", {})

    if run.get("artifact_version") != "5.0.0":
        raise ContractError("Root Cause write contract must be 5.0.0")
    present_forbidden = FORBIDDEN_FIELDS.intersection(
        set(payload).union(set(results))
    )
    if present_forbidden:
        raise ContractError(f"Removed fields present: {sorted(present_forbidden)}")
    if source_input and contract.get("run_mode") != source_input.get("run", {}).get("run_mode"):
        raise ContractError("Input and output run_mode differ")

    candidates = results.get("root_cause_candidates", [])
    candidate_ids = {item.get("candidate_id") for item in candidates}
    if handoff.get("input_gate_status") == "blocked" and candidates:
        raise ContractError("Blocked runs cannot emit Root Cause candidates")

    rank = {"insufficient": 0, "low": 1, "medium": 2, "high": 3}
    for candidate in candidates:
        if candidate.get("status") not in {
            "candidate",
            "candidate_requires_review",
            "insufficient_evidence",
            "rejected",
        }:
            raise ContractError("Root Cause status cannot be validated or final")
        if not candidate.get("counter_evidence"):
            raise ContractError(f"{candidate.get('candidate_id')}: counter evidence check is required")
        if not candidate.get("alternative_explanations"):
            raise ContractError(f"{candidate.get('candidate_id')}: alternative explanation is required")
        level = candidate.get("causal_confidence", {}).get("level")
        ceiling = confidence_ceiling(candidate, payload)
        if rank.get(level, 99) > rank[ceiling]:
            raise ContractError(
                f"{candidate.get('candidate_id')}: causal confidence {level} exceeds {ceiling}"
            )
        if any(
            item.get("status") == "stronger_than_primary"
            for item in candidate.get("alternative_explanations", [])
        ) and candidate.get("is_primary"):
            raise ContractError("A candidate with a stronger alternative cannot remain primary")

    chains = results.get("candidate_mechanism_chains", [])
    chain_candidate_refs = {
        ref for chain in chains for ref in chain.get("root_cause_candidate_refs", [])
    }
    for candidate in candidates:
        if candidate.get("status") not in {"rejected", "insufficient_evidence"}:
            if candidate.get("candidate_id") not in chain_candidate_refs:
                raise ContractError("Every active candidate requires a mechanism chain")

    confidence_by_candidate = {
        item["candidate_id"]: item["causal_confidence"]["level"] for item in candidates
    }
    for direction in results.get("intervention_direction_candidates", []):
        objective = direction.get("objective", "")
        if CONCRETE_SOLUTION_PATTERN.search(objective):
            raise ContractError("Intervention direction contains a concrete solution")
        levels = [
            confidence_by_candidate.get(ref, "insufficient")
            for ref in direction.get("root_cause_candidate_refs", [])
        ]
        if any(level in {"low", "insufficient"} for level in levels):
            if direction.get("readiness") not in {"validation_only", "blocked"}:
                raise ContractError("Low-confidence directions must remain validation_only or blocked")

    direction_ids = {
        item.get("direction_id")
        for item in results.get("intervention_direction_candidates", [])
    }
    for hypothesis in results.get("validation_hypotheses", []):
        if not set(hypothesis.get("root_cause_candidate_refs", [])).issubset(candidate_ids):
            raise ContractError("Validation hypothesis references an unknown candidate")
        if not set(hypothesis.get("intervention_direction_refs", [])).issubset(direction_ids):
            raise ContractError("Validation hypothesis references an unknown direction")
        serialized = json.dumps(hypothesis, ensure_ascii=False)
        if NUMERIC_UPLIFT_PATTERN.search(serialized):
            raise ContractError("Root Cause validation hypotheses cannot predict numeric uplift")
        if any(term in serialized.lower() for term in ("roi", "payback", "net_benefit")):
            raise ContractError("Root Cause cannot emit business valuation")

    mode = contract.get("run_mode")
    patches = results.get("root_cause_lifecycle_patches", [])
    patterns = results.get("root_cause_pattern_candidates", [])
    if patches and mode != "outcome_feedback_refresh":
        raise ContractError("Lifecycle patches are only allowed in outcome_feedback_refresh")
    if patterns and mode != "pattern_candidate_learning":
        raise ContractError("Pattern candidates are only allowed in pattern_candidate_learning")
    for patch in patches:
        if patch.get("requires_manual_approval") is not True or patch.get("can_auto_apply") is not False:
            raise ContractError("Root Cause lifecycle patches must be manual and non-applying")
    for pattern in patterns:
        if len(set(pattern.get("reviewed_outcome_case_refs", []))) < 2:
            raise ContractError("Pattern candidates require at least two reviewed Outcome cases")
        if pattern.get("can_publish") is not False:
            raise ContractError("Pattern candidates cannot auto-publish")

    review_ids = {item.get("review_id") for item in payload.get("manual_review_requests", [])}
    for item in payload.get("downstream_handoffs", []):
        if not set(item.get("required_review_request_ids", [])).issubset(review_ids):
            raise ContractError("Handoff references an unknown manual review")
        target = item.get("target_skill")
        if target == "problem-framing":
            if "problem_framing" not in item.get("allowed_uses", []):
                raise ContractError("Problem Framing handoff requires problem_framing")
            selected = [_resolve_pointer(payload, ref) for ref in item.get("payload_refs", [])]
            candidates = [
                value
                for value in selected
                if isinstance(value, dict) and value.get("candidate_id")
            ]
            directions = [
                value
                for value in selected
                if isinstance(value, dict) and value.get("direction_id")
            ]
            if not candidates:
                raise ContractError("Problem Framing handoff requires a Root Cause candidate")
            if not directions:
                raise ContractError("Problem Framing handoff requires an intervention direction")
            if any(value.get("readiness") != "design_ready_after_review" for value in directions):
                raise ContractError("Only design_ready_after_review directions may enter Problem Framing")
            selected_candidate_ids = {value["candidate_id"] for value in candidates}
            if any(
                not set(value.get("root_cause_candidate_refs", []))
                or not set(value.get("root_cause_candidate_refs", [])).issubset(
                    selected_candidate_ids
                )
                for value in directions
            ):
                raise ContractError(
                    "Problem Framing directions must reference selected Root Cause candidates"
                )
            if any(value.get("review_status") == "pending" for value in directions) and not item.get("required_review_request_ids"):
                raise ContractError("Pending design direction requires a bound review")
        if target == "knowledge-wiki":
            if mode != "pattern_candidate_learning":
                raise ContractError("Only pattern learning may request Knowledge Wiki ingestion")
            if not item.get("required_review_request_ids"):
                raise ContractError("Knowledge Wiki handoff requires publication review")
            if "publish_knowledge" in item.get("allowed_uses", []):
                raise ContractError("Root Cause cannot authorize knowledge publication")
        if target == "evidence-archive":
            if "persist_in_archive" not in item.get("allowed_uses", []):
                raise ContractError("Archive handoff requires persist_in_archive")
            if not item.get("required_review_request_ids"):
                raise ContractError("Archive handoff requires explicit authorization review")

    safety = payload.get("write_safety", {})
    if any(safety.get(key) is not False for key in safety):
        raise ContractError("Root Cause write safety flags must all be false")


def atomic_write(payload: dict[str, Any], output: Path) -> Path:
    payload = json.loads(json.dumps(payload))
    payload["run"]["write_status"] = "written"
    validate_output(payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    fd, temp_name = tempfile.mkstemp(prefix=".root-cause-", suffix=".tmp", dir=output.parent)
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
    status_labels = {
        "candidate_requires_review": "候选机制，等待复核",
        "candidate": "候选机制",
        "needs_validation": "需要补充验证",
        "ready": "已具备下一步条件",
    }
    confidence_labels = {
        "low": "低",
        "medium": "中",
        "high": "高",
        "unknown": "未知",
    }

    def scope_text(value: Any) -> str:
        if not isinstance(value, dict):
            return str(value)
        parts = [
            value.get("journey_step"),
            value.get("segment"),
            value.get("scenario"),
        ]
        return " / ".join(str(item) for item in parts if item) or "未说明范围"

    run = payload["run"]
    results = payload["analysis_results"]
    lines = [
        f"# {run['project_name']} · 根因综合报告",
        "",
        "## 结论摘要",
        "",
    ]
    for item in results.get("root_cause_candidates", []):
        confidence = item.get("causal_confidence", {})
        confidence = (
            confidence.get("level", "unknown")
            if isinstance(confidence, dict)
            else confidence
        )
        lines += [
            f"### {scope_text(item.get('issue_scope') or item.get('candidate_id'))}",
            "",
            f"- 状态：{status_labels.get(item.get('status'), item.get('status'))}",
            f"- 因果置信度：{confidence_labels.get(confidence, confidence)}",
            f"- 观察症状：{'；'.join(item.get('observed_symptoms', [])) or '无'}",
            f"- 限制：{'；'.join(item.get('caveats', [])) or '无'}",
            "",
        ]
    lines += ["## 干预方向", ""]
    for item in results.get("intervention_direction_candidates", []):
        lines.append(
            f"- {item.get('objective') or item.get('direction_id')}；"
            f"适用范围：{scope_text(item.get('target_scope', {}))}；"
            f"前置条件：{'；'.join(item.get('preconditions', [])) or '无'}"
        )
    lines += ["", "## 全局限制", ""]
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
    validate_registered_govern_handoff(source_input)
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
                artifact_id="root-cause",
                candidate_path=candidate_path,
                purpose_key=source_input["analysis_purpose"]["purpose_key"],
                purpose_label=source_input["analysis_purpose"]["purpose_label"],
                deliverables=deliverables,
            )
        print(json.dumps(reference, ensure_ascii=False, indent=2))
    else:
        print("valid: Root Cause Synthesis 3.0 input and output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
