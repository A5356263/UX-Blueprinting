#!/usr/bin/env python3
"""Deterministic preparation, validation, and atomic write for Evidence Govern 6.0.0."""

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


WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
REGISTRY_PATH = WORKSPACE_ROOT / "shared-workflow/data-analysis/artifact-registry.json"
OUTPUT_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas/output.schema.json"
RUNTIME_DIR = WORKSPACE_ROOT / "shared-workflow/data-analysis/runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))
import contract_runtime

CURRENT_SOURCE_VERSIONS = {
    "objective-data-analysis": "4.0.0",
    "subjective-feedback-analysis": "4.0.0",
    "experience-heuristic-analysis": "4.0.0",
}
EVIDENCE_TYPE_BY_SKILL = {
    "objective-data-analysis": "objective",
    "subjective-feedback-analysis": "subjective",
    "experience-heuristic-analysis": "heuristic",
}
CANONICALIZATION_VERSION = "6.0.0"
VERSION = "6.0.0"
ALLOWED_HANDOFF_TARGETS = {
    "root-cause-synthesis",
    "outcome-validation-recheck",
    "business-impact",
    "data-visualization",
    "evidence-archive",
    "knowledge-wiki",
}


class ContractError(ValueError):
    """Raised when a request or result violates a core contract."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"文件不存在：{path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(f"JSON 无法解析：{path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON 顶层必须是 object：{path}")
    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _evidence_id(item: dict[str, Any]) -> str:
    identity = {
        "evidence_type": item.get("evidence_type"),
        "sources": item.get("lineage", {}).get("sources", []),
        "claim_type": item.get("claim_type"),
        "claim_summary": item.get("claim_summary"),
        "scope": item.get("scope"),
        "time_window": item.get("time_window"),
    }
    return f"ev_{_sha256(identity)[:16]}"


def _comparison_key(
    evidence_type: str,
    claim_type: str,
    scope: dict[str, Any],
    scene: dict[str, Any] | None,
    source_item: dict[str, Any],
) -> str | None:
    scenario = (
        source_item.get("scenario_key")
        or source_item.get("metric_contract_ref")
        or source_item.get("metric_contract_id")
    )
    where = (scene or {}).get("where")
    operation = (scene or {}).get("operation")
    if not any([scenario, scope, where, operation]):
        return None
    comparable = {
        "evidence_type": evidence_type,
        "claim_type": claim_type,
        "scenario": scenario,
        "scope": scope,
        "where": where,
        "operation": operation,
    }
    return f"cmp_{_sha256(comparable)[:16]}"


def _registry() -> dict[str, Any]:
    return _load_json(REGISTRY_PATH)


def _artifact_entry(ref: str, registry: dict[str, Any]) -> dict[str, Any]:
    for entry in registry.get("artifacts", []):
        if ref == entry.get("artifact_id"):
            return entry
    raise ContractError(f"Artifact 未登记或不是正式分析产物：{ref}")


def _decode_pointer_token(value: str) -> str:
    return value.replace("~1", "/").replace("~0", "~")


def _resolve_pointer(payload: Any, pointer: str) -> Any:
    if not isinstance(pointer, str) or not pointer:
        raise ContractError("Payload Ref 必须是非空字符串")
    if pointer == "#":
        return payload
    if not pointer.startswith("#/"):
        raise ContractError(f"Payload Ref 不是绝对 JSON Pointer：{pointer}")
    current = payload
    for raw_token in pointer[2:].split("/"):
        token = _decode_pointer_token(raw_token)
        if isinstance(current, list):
            try:
                current = current[int(token)]
            except (ValueError, IndexError) as exc:
                raise ContractError(f"Payload Ref 无法解析：{pointer}") from exc
        elif isinstance(current, dict) and token in current:
            current = current[token]
        else:
            raise ContractError(f"Payload Ref 无法解析：{pointer}")
    return current


def _source_item_id(item: dict[str, Any], index: int) -> str:
    for key in ("evidence_id", "item_id", "finding_id", "signal_id", "id"):
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    return f"index-{index}"


def _claim_summary(item: dict[str, Any]) -> str:
    claim_type = str(item.get("claim_type") or "")
    if claim_type == "risk_hypothesis":
        value = item.get("risk_hypothesis")
        if isinstance(value, str) and value.strip():
            return value.strip()
    if claim_type in {"heuristic_observation", "metric_observation", "feedback_observation"}:
        for key in ("observation", "statement"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    for key in (
        "claim_summary",
        "summary",
        "statement",
        "description",
        "title",
        "finding_summary",
        "observation",
    ):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return _canonical_json(item)[:240]


def _business_rule_refs(item: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    direct = item.get("business_rule_basis_refs")
    if isinstance(direct, list):
        refs.extend(str(value) for value in direct if value)
    basis = item.get("business_rule_basis")
    if isinstance(basis, dict):
        for key in ("basis_id", "source_ref"):
            value = basis.get(key)
            if isinstance(value, str) and value:
                refs.append(value)
    elif isinstance(basis, list):
        for value in basis:
            if isinstance(value, dict):
                ref = value.get("basis_id") or value.get("source_ref")
                if isinstance(ref, str) and ref:
                    refs.append(ref)
    return sorted(set(refs))


def _normalize_item(
    source_item: dict[str, Any],
    index: int,
    entry: dict[str, Any],
    payload: dict[str, Any],
    payload_ref: str,
) -> dict[str, Any]:
    run = payload.get("run", {})
    producer = entry["producer_skill"]
    source_id = _source_item_id(source_item, index)
    claim_type = str(source_item.get("claim_type") or source_item.get("evidence_type") or "observation")
    summary = _claim_summary(source_item)
    scene = source_item.get("scene_descriptor") or source_item.get("scene")
    scope = source_item.get("scope") or source_item.get("applicable_scope") or {}
    if not scope and isinstance(scene, dict):
        scope = {
            "where": scene.get("where"),
            "what": scene.get("what"),
            "operation": scene.get("operation"),
        }
    if not isinstance(scope, dict):
        scope = {"declared_scope": scope}
    time_window = source_item.get("time_window")
    if time_window is None and isinstance(scene, dict):
        time_window = scene.get("time_window")
    if time_window is None:
        time_window = run.get("time_window")
    if scene is not None and not isinstance(scene, dict):
        scene = {"what": str(scene)}
    privacy_status = source_item.get("privacy_status")
    effective_privacy_status = privacy_status or "needs_review"
    limitations = list(source_item.get("limitations") or [])
    if privacy_status is None:
        limitations.append("privacy_status_missing")
    if not source_id:
        limitations.append("source_item_id_missing")
    evidence_type = EVIDENCE_TYPE_BY_SKILL[producer]
    normalized: dict[str, Any] = {
        "evidence_id": "",
        "evidence_type": evidence_type,
        "claim_type": claim_type,
        "claim_summary": summary,
        "scope": scope,
        "time_window": time_window,
        "scene_descriptor": scene,
        "comparison_key": _comparison_key(
            evidence_type, claim_type, scope, scene, source_item
        ),
        "lineage": {
            "sources": [
                {
                    "source_artifact_ref": entry["artifact_id"],
                    "source_artifact_version": str(run.get("artifact_version") or ""),
                    "source_run_id": str(run.get("run_id") or ""),
                    "payload_ref": payload_ref,
                    "source_object_id": source_id,
                }
            ],
            "canonicalization_version": CANONICALIZATION_VERSION,
            "lineage_fingerprint": _sha256(
                {
                    "source_artifact_ref": entry["artifact_id"],
                    "source_artifact_version": run.get("artifact_version"),
                    "source_run_id": run.get("run_id"),
                    "payload_ref": payload_ref,
                    "source_item": source_item,
                }
            ),
        },
        "evidence_strength": _evidence_strength(
            evidence_type, source_item, limitations
        ),
        "lifecycle_status": "restricted" if effective_privacy_status in {"restricted", "needs_review", "blocked"} else "candidate",
        "privacy_status": effective_privacy_status,
        "manual_review_required": bool(
            source_item.get("manual_review_required")
            or effective_privacy_status in {"restricted", "needs_review", "blocked"}
            or evidence_type == "heuristic"
        ),
        "allowed_uses": sorted(set(str(value) for value in source_item.get("allowed_uses", []))),
        "forbidden_uses": sorted(set(str(value) for value in source_item.get("forbidden_uses", []))),
        "business_rule_basis_refs": _business_rule_refs(source_item),
        "limitations": sorted(set(str(value) for value in limitations)),
    }
    normalized["evidence_id"] = _evidence_id(normalized)
    return normalized


def _evidence_strength(
    evidence_type: str,
    source_item: dict[str, Any],
    limitations: list[Any],
) -> str:
    """Conservative source-aware strength before cross-source linking."""
    severe = {
        "privacy_status_missing",
        "source_item_id_missing",
        "invalid_denominator",
        "untraceable_source",
    }
    limitation_values = {str(value) for value in limitations}
    if severe.intersection(limitation_values):
        return "insufficient"
    confidence = str(source_item.get("confidence") or "").lower()
    if confidence in {"low", "insufficient"}:
        return "weak"
    if limitations:
        return "weak"
    if evidence_type == "objective":
        reliability = source_item.get("sample_reliability")
        if reliability in {"reliable", "high"}:
            return "strong"
        return "medium"
    return "medium"


def _infer_mode(request: dict[str, Any]) -> str:
    requested = request.get("requested_mode")
    candidates: list[str] = []
    if request.get("upstream_artifact_refs"):
        candidates.append("evidence_governance")
    if request.get("outcome_patch_refs"):
        candidates.append("outcome_patch_absorption")
    if request.get("review_decisions"):
        candidates.append("review_decision_absorption")
    if requested:
        return str(requested)
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise ContractError("无法推断运行模式：缺少分析产物、Outcome Patch 或 Review Decision")
    raise ContractError(f"输入同时触发多个运行模式，需要显式 requested_mode：{candidates}")


def _validate_request(request: dict[str, Any], mode: str) -> None:
    shared_required = {
        "invocation_context",
        "analysis_purpose",
        "requested_analyses",
        "input_bindings",
        "requested_deliverables",
        "publication_policy",
        "retention_policy",
    }
    missing = sorted(shared_required - set(request))
    if missing:
        raise ContractError(f"请求缺少共享运行维度：{', '.join(missing)}")
    if request.get("artifact_type") != "evidence_govern_request":
        raise ContractError("artifact_type 必须是 evidence_govern_request")
    if request.get("artifact_version") != VERSION:
        raise ContractError(f"只接受 Evidence Govern Request {VERSION}")
    if request.get("source_mode") not in {"explicit_input", "chain_context"}:
        raise ContractError("source_mode 必须是 explicit_input 或 chain_context")
    if mode == "evidence_governance" and not request.get("upstream_artifact_refs"):
        raise ContractError("evidence_governance 至少需要一个上游分析产物")
    if mode == "outcome_patch_absorption":
        if not request.get("prior_govern_result_ref") or not request.get("outcome_patch_refs"):
            raise ContractError("outcome_patch_absorption 需要 prior Govern 和 Outcome Patch")
    if mode == "review_decision_absorption":
        if not request.get("prior_govern_result_ref") or not request.get("review_decisions"):
            raise ContractError("review_decision_absorption 需要 prior Govern 和 Review Decision")


def prepare(request_path: Path) -> dict[str, Any]:
    request = _load_json(request_path)
    mode = _infer_mode(request)
    _validate_request(request, mode)
    registry = _registry()
    source_refs: list[str] = []
    evidence_items: list[dict[str, Any]] = []
    project_name = request.get("project_name") or ""
    context_input_manifest = []
    for index, item in enumerate(request.get("context_inputs", [])):
        source_ref = item.get("source_ref")
        context_input_manifest.append(
            {
                "context_id": f"context_{index + 1}",
                "input_type": item.get("input_type"),
                "source_ref": source_ref,
                "content_fingerprint": _sha256(
                    {
                        "statement": item.get("statement"),
                        "source_ref": source_ref,
                        "declared_scope": item.get("declared_scope"),
                    }
                ),
                "declared_scope": item.get("declared_scope"),
                "sensitivity": item.get("sensitivity", "unknown"),
                "load_status": "declared" if item.get("statement") or source_ref else "missing_reference",
            }
        )

    if mode == "evidence_governance":
        for source_ref in request.get("upstream_artifact_refs", []):
            instance_ref = source_ref.get("artifact_instance_ref")
            if not isinstance(instance_ref, dict):
                raise ContractError("上游必须提供 artifact_instance_ref")
            artifact_ref = instance_ref.get("artifact_id")
            entry = _artifact_entry(artifact_ref, registry)
            producer = entry.get("producer_skill")
            if producer not in CURRENT_SOURCE_VERSIONS:
                raise ContractError(f"Evidence Govern 不接受该生产者作为 Phase 1 输入：{producer}")
            try:
                payload, _ = contract_runtime.validate_instance_ref(
                    instance_ref,
                    workspace_root=WORKSPACE_ROOT,
                    registry=registry,
                )
            except contract_runtime.ContractRuntimeError as exc:
                raise ContractError(str(exc)) from exc
            run = payload.get("run", {})
            if run.get("producer_skill") != producer:
                raise ContractError(f"producer_skill 不匹配：{entry['artifact_id']}")
            if run.get("artifact_version") != CURRENT_SOURCE_VERSIONS[producer]:
                raise ContractError(
                    f"{producer} 需要当前版本 {CURRENT_SOURCE_VERSIONS[producer]}，"
                    f"实际为 {run.get('artifact_version')}"
                )
            handoff_ref = source_ref.get("handoff_ref")
            handoff = _resolve_pointer(payload, handoff_ref)
            if not isinstance(handoff, dict):
                raise ContractError(f"{artifact_ref} Handoff 不是 object")
            target = handoff.get("target_skill") or handoff.get("next_skill")
            status = handoff.get("handoff_status") or handoff.get("status")
            if target != "evidence-govern":
                raise ContractError(f"{artifact_ref} Handoff 未面向 evidence-govern")
            if status not in {"ready", "ready_with_caveats"}:
                raise ContractError(f"{artifact_ref} Handoff 尚未可消费")
            if source_ref.get("allowed_use") not in handoff.get("allowed_uses", []):
                raise ContractError(f"{artifact_ref} Handoff 未允许 evidence_governance")
            if not set(source_ref.get("payload_refs", [])).issubset(
                set(handoff.get("payload_refs", []))
            ):
                raise ContractError(f"{artifact_ref} 请求 Payload 超出 Handoff")
            if not project_name:
                project_name = str(run.get("project_name") or "")
            source_refs.append(entry["artifact_id"])
            for index, payload_ref in enumerate(source_ref.get("payload_refs", [])):
                source_item = _resolve_pointer(payload, payload_ref)
                if not isinstance(source_item, dict):
                    raise ContractError(
                        f"{entry['artifact_id']} {payload_ref} 不是 Evidence object"
                    )
                evidence_items.append(
                    _normalize_item(
                        source_item, index, entry, payload, payload_ref
                    )
                )

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    request_fingerprint = _sha256(request)
    run_id = f"eg_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{request_fingerprint[:8]}"
    known_gaps = sorted(
        {
            limitation
            for item in evidence_items
            for limitation in item.get("limitations", [])
        }
    )
    result = {
        "run": {
            "artifact_type": "evidence_govern_result",
            "artifact_version": VERSION,
            "producer_skill": "evidence-govern",
            "run_id": run_id,
            "project_name": project_name,
            "generated_at": now,
            "invocation_context": request["invocation_context"],
            "analysis_purpose": request["analysis_purpose"],
            "status": "partial",
            "source_mode": request["source_mode"],
            "sources": source_refs,
            "upstream_refs": list(request.get("upstream_artifact_refs", [])),
            "write_status": "not_requested",
        },
        "analysis_contract": {
            "run_mode": mode,
            "prior_govern_result_ref": request.get("prior_govern_result_ref"),
            "archived_evidence_refs": list(request.get("archived_evidence_refs", [])),
            "baseline_refs": list(request.get("baseline_refs", [])),
            "outcome_patch_refs": list(request.get("outcome_patch_refs", [])),
            "context_input_manifest": context_input_manifest,
            "phase_status": {
                "normalization": "completed" if mode == "evidence_governance" else "not_run",
                "evidence_linking_context": "not_run",
                "governance_release": "not_run",
            },
        },
        "data_quality": {
            "source_count": len(source_refs),
            "evidence_item_count": len(evidence_items),
            "lineage_complete_count": len(evidence_items),
            "known_gaps": known_gaps,
        },
        "evidence_items": evidence_items,
        "evidence_relationships": [],
        "evidence_change_signals": [],
        "context_factor_assessments": [],
        "evidence_patches": [],
        "baseline_patches": [],
        "manual_review_queue": [
            {
                "review_id": f"egr_privacy_{item['evidence_id']}",
                "target_refs": [item["evidence_id"]],
                "risk_level": "high" if item["privacy_status"] == "blocked" else "medium",
                "reason": "该证据继承了来源的隐私限制或人工复核要求",
                "blocked_consumers": ["root-cause-synthesis", "business-impact", "data-visualization", "evidence-archive"],
                "status": "open",
            }
            for item in evidence_items
            if item["manual_review_required"]
        ],
        "review_decisions": list(request.get("review_decisions", [])),
        "downstream_handoffs": [],
        "limitations": known_gaps + ["prepare_only_semantic_phases_not_completed"],
        "handoff": {
            "input_gate_status": "ready" if evidence_items or mode != "evidence_governance" else "blocked",
            "handoff_status": "pending_review",
            "allowed_uses": [],
            "forbidden_uses": ["use_before_phase_completion"],
            "blocked_reasons": [],
            "root_cause_readiness": "blocked",
            "evidence_basis": "insufficient",
        },
    }
    return result


def _require_keys(value: dict[str, Any], keys: list[str], where: str, errors: list[str]) -> None:
    for key in keys:
        if key not in value:
            errors.append(f"{where} 缺少字段 {key}")


def _governed_use_is_eligible(
    result: dict[str, Any],
    evidence: dict[str, Any],
    use: str,
    *,
    approved_review_ids: set[str],
    required_reviews_by_target: dict[str, set[str]],
) -> tuple[bool, str | None]:
    """Return whether Evidence Govern may grant a downstream-only governed use."""
    if use != "causal_synthesis":
        return False, "该用途不是 Evidence Govern 可派生用途"
    phase_status = result.get("analysis_contract", {}).get("phase_status", {})
    if phase_status.get("governance_release") not in {"completed", "partial"}:
        return False, "governance_release 尚未完成"
    if result.get("handoff", {}).get("root_cause_readiness") == "blocked":
        return False, "Root Cause Readiness 为 blocked"
    if evidence.get("privacy_status") != "safe":
        return False, "证据隐私状态不是 safe"
    if evidence.get("lifecycle_status") != "released":
        return False, "证据生命周期不是 released"
    if evidence.get("evidence_strength") == "insufficient":
        return False, "证据强度不足"
    if use in set(evidence.get("forbidden_uses", [])):
        return False, "证据明确禁止该用途"
    if evidence.get("manual_review_required") is True:
        required_reviews = required_reviews_by_target.get(
            str(evidence.get("evidence_id")), set()
        )
        if not required_reviews:
            return False, "需要人工复核但没有 review item"
        if not required_reviews.issubset(approved_review_ids):
            return False, "所需人工复核尚未 approved"
    return True, None


def _usable_released_evidence(evidence: dict[str, Any]) -> bool:
    """Return whether an evidence item may support a released evidence basis."""
    return (
        evidence.get("lifecycle_status") == "released"
        and evidence.get("privacy_status") == "safe"
        and evidence.get("evidence_strength") != "insufficient"
    )


def _source_artifact_refs(evidence: dict[str, Any]) -> set[str]:
    """Return the declared source artifacts that establish lineage independence."""
    return {
        str(source.get("source_artifact_ref"))
        for source in evidence.get("lineage", {}).get("sources", [])
        if isinstance(source, dict) and source.get("source_artifact_ref")
    }


def _relationship_supports_cross_source_basis(
    relation: dict[str, Any],
    evidence_by_id: dict[str, dict[str, Any]],
) -> tuple[bool, list[str]]:
    """Validate the minimum lineage and time comparability for a cross-source link."""
    relationship_id = relation.get("relationship_id")
    reasons: list[str] = []
    selected = [
        evidence_by_id[ref]
        for ref in relation.get("evidence_refs", [])
        if ref in evidence_by_id
    ]
    if len(selected) != len(relation.get("evidence_refs", [])) or len(selected) < 2:
        return False, reasons
    if not all(_usable_released_evidence(item) for item in selected):
        reasons.append(f"{relationship_id} 只能使用已放行、隐私安全且强度充分的 Evidence")

    source_sets = [_source_artifact_refs(item) for item in selected]
    if any(not source_set for source_set in source_sets):
        reasons.append(f"{relationship_id} 缺少可验证的来源血缘")
    else:
        for index, source_set in enumerate(source_sets):
            if any(source_set.intersection(other) for other in source_sets[index + 1 :]):
                reasons.append(f"{relationship_id} 的 Evidence 来源血缘不独立")
                break
        if len(set().union(*source_sets)) < 2:
            reasons.append(f"{relationship_id} 未形成至少两个独立来源")

    time_windows = [item.get("time_window") for item in selected]
    if any(window is None for window in time_windows):
        reasons.append(f"{relationship_id} 缺少可比时间窗口")
    elif len({_canonical_json(window) for window in time_windows}) != 1:
        reasons.append(f"{relationship_id} 的 Evidence 时间窗口不可比")
    if "time_window" in set(relation.get("mismatched_dimensions", [])):
        reasons.append(f"{relationship_id} 已声明时间窗口不匹配")
    if relation.get("source_independence") != "independent":
        reasons.append(f"{relationship_id} 必须声明独立来源")
    return not reasons, reasons


def _validate_core(result: dict[str, Any], *, for_write: bool = False) -> list[str]:
    errors: list[str] = []
    top_keys = [
        "run",
        "analysis_contract",
        "data_quality",
        "evidence_items",
        "evidence_relationships",
        "evidence_change_signals",
        "context_factor_assessments",
        "evidence_patches",
        "baseline_patches",
        "manual_review_queue",
        "review_decisions",
        "downstream_handoffs",
        "limitations",
        "handoff",
    ]
    if "publication" in result or "delivery" in result:
        top_keys.extend(["publication", "delivery"])
    _require_keys(result, top_keys, "output", errors)
    if errors:
        return errors

    run = result.get("run", {})
    if run.get("artifact_type") != "evidence_govern_result":
        errors.append("run.artifact_type 必须是 evidence_govern_result")
    if run.get("artifact_version") != VERSION:
        errors.append(f"run.artifact_version 必须是 {VERSION}")
    if run.get("producer_skill") != "evidence-govern":
        errors.append("run.producer_skill 必须是 evidence-govern")

    evidence_items = result.get("evidence_items", [])
    evidence_ids: set[str] = set()
    for index, item in enumerate(evidence_items):
        if not isinstance(item, dict):
            errors.append(f"evidence_items[{index}] 不是 object")
            continue
        evidence_id = item.get("evidence_id")
        if evidence_id in evidence_ids:
            errors.append(f"重复 evidence_id：{evidence_id}")
        if evidence_id:
            evidence_ids.add(str(evidence_id))
        expected = _evidence_id(item)
        if evidence_id != expected:
            errors.append(f"{evidence_id} 不符合确定性 ID，期望 {expected}")
        fingerprint = item.get("lineage", {}).get("lineage_fingerprint")
        if not isinstance(fingerprint, str) or len(fingerprint) != 64:
            errors.append(f"{evidence_id} lineage_fingerprint 非 64 位 SHA-256")
        lineage = item.get("lineage", {})
        if lineage.get("canonicalization_version") != CANONICALIZATION_VERSION:
            errors.append(
                f"{evidence_id} canonicalization_version 必须是 "
                f"{CANONICALIZATION_VERSION}"
            )
        for source in lineage.get("sources", []):
            if source.get("source_artifact_ref") not in {
                "objective",
                "subjective",
                "heuristic",
                "outcome",
                "archive-summary",
            }:
                errors.append(
                    f"{evidence_id} 包含未登记的 Lineage Artifact："
                    f"{source.get('source_artifact_ref')}"
                )
            if not str(source.get("payload_ref", "")).startswith("#/"):
                errors.append(f"{evidence_id} Lineage Payload Ref 非绝对 Pointer")
        privacy_status = item.get("privacy_status")
        if privacy_status not in {"safe", "restricted", "needs_review", "blocked"}:
            errors.append(f"{evidence_id} privacy_status 无效")
        if not isinstance(item.get("manual_review_required"), bool):
            errors.append(f"{evidence_id} manual_review_required 必须是 boolean")
        if not isinstance(item.get("allowed_uses"), list) or not isinstance(item.get("forbidden_uses"), list):
            errors.append(f"{evidence_id} 用途限制必须是 array")
        elif set(item["allowed_uses"]).intersection(item["forbidden_uses"]):
            errors.append(f"{evidence_id} allowed_uses 与 forbidden_uses 冲突")
        if privacy_status in {"restricted", "needs_review", "blocked"} and item.get("lifecycle_status") not in {"restricted", "archived"}:
            errors.append(f"{evidence_id} 隐私受限时 lifecycle_status 必须受限")

    evidence_by_id = {
        str(item.get("evidence_id")): item
        for item in evidence_items
        if isinstance(item, dict) and item.get("evidence_id")
    }
    valid_corroboration = False
    valid_contradiction = False
    relationship_ids: set[str] = set()
    for relation in result.get("evidence_relationships", []):
        relationship_id = relation.get("relationship_id")
        if relationship_id in relationship_ids:
            errors.append(f"重复 relationship_id：{relationship_id}")
        relationship_ids.add(str(relationship_id))
        refs = relation.get("evidence_refs", [])
        if len(set(refs)) < 2:
            errors.append(f"{relationship_id} 至少需要两个不同 Evidence Ref")
        for ref in refs:
            if ref not in evidence_ids:
                errors.append(f"{relationship_id} 引用不存在的 Evidence：{ref}")
        relationship_type = relation.get("relationship_type")
        if relationship_type in {"corroborates", "contradicts"}:
            valid, relationship_errors = _relationship_supports_cross_source_basis(
                relation, evidence_by_id
            )
            errors.extend(relationship_errors)
            if valid and relationship_type == "corroborates":
                valid_corroboration = True
            if valid and relationship_type == "contradicts":
                valid_contradiction = True

    for signal in result.get("evidence_change_signals", []):
        for ref in signal.get("evidence_refs", []):
            if ref not in evidence_ids:
                errors.append(f"{signal.get('signal_id')} 引用不存在的 Evidence：{ref}")
        forbidden = {"lifecycle_status", "to_status", "applied"}
        if forbidden.intersection(signal):
            errors.append(f"{signal.get('signal_id')} 变化信号不得直接修改生命周期")

    patch_ids: set[str] = set()
    persistable_patch_ids: set[str] = set()
    for patch_group, target_key in (
        (result.get("evidence_patches", []), "target_ref"),
        (result.get("baseline_patches", []), "baseline_ref"),
    ):
        for patch in patch_group:
            patch_id = str(patch.get("patch_id"))
            if patch_id in patch_ids:
                errors.append(f"重复 patch_id：{patch_id}")
            patch_ids.add(patch_id)
            decision = patch.get("decision_status")
            can_persist = patch.get("can_persist")
            if decision in {"pending", "rejected"} and can_persist:
                errors.append(f"{patch_id} 未获准却 can_persist=true")
            if decision in {"not_required", "approved"} and can_persist:
                persistable_patch_ids.add(patch_id)
            if patch.get("applied") is not False:
                errors.append(f"{patch_id} Evidence Govern 不得标记 applied=true")
            if target_key == "target_ref" and patch.get(target_key) not in evidence_ids:
                errors.append(f"{patch_id} 引用不存在的 Evidence：{patch.get(target_key)}")

    review_items = {
        item.get("review_id"): item for item in result.get("manual_review_queue", [])
    }
    approved_actions: set[str] = set()
    approved_review_ids: set[str] = set()
    for decision in result.get("review_decisions", []):
        review_id = decision.get("review_id")
        if review_id not in review_items:
            errors.append(f"Review Decision 引用不存在的 review_id：{review_id}")
        if decision.get("decision") == "approved":
            approved_review_ids.add(str(review_id))
        approved_actions.update(decision.get("approved_actions", []))
    required_reviews_by_target: dict[str, set[str]] = {}
    for review_id, review in review_items.items():
        for target_ref in review.get("target_refs", []):
            required_reviews_by_target.setdefault(str(target_ref), set()).add(
                str(review_id)
            )

    for handoff in result.get("downstream_handoffs", []):
        if handoff.get("target_skill") not in ALLOWED_HANDOFF_TARGETS:
            errors.append(f"{handoff.get('handoff_id')} target_skill 不在白名单")
        for ref in handoff.get("payload_refs", []):
            if not isinstance(ref, str) or not ref.startswith("#/"):
                errors.append(f"{handoff.get('handoff_id')} Payload Ref 必须是绝对 Pointer")
                continue
            try:
                selected = _resolve_pointer(result, ref)
            except ContractError:
                errors.append(f"{handoff.get('handoff_id')} Payload Ref 无法解析：{ref}")
                continue
            if isinstance(selected, dict) and selected.get("evidence_id"):
                evidence_id = str(selected["evidence_id"])
                selected_allowed_uses = set(selected.get("allowed_uses", []))
                requested_allowed_uses = set(handoff.get("allowed_uses", []))
                undeclared_uses = requested_allowed_uses - selected_allowed_uses
                rejected_derived_uses: dict[str, str] = {}
                for use in sorted(undeclared_uses):
                    eligible, reason = _governed_use_is_eligible(
                        result,
                        selected,
                        use,
                        approved_review_ids=approved_review_ids,
                        required_reviews_by_target=required_reviews_by_target,
                    )
                    if not eligible:
                        rejected_derived_uses[use] = reason or "不满足治理派生条件"
                if rejected_derived_uses:
                    errors.append(
                        f"{handoff.get('handoff_id')} allowed_uses 包含证据未许可用途："
                        f"{rejected_derived_uses}"
                    )
                if not set(selected.get("forbidden_uses", [])).issubset(
                    set(handoff.get("forbidden_uses", []))
                ):
                    errors.append(
                        f"{handoff.get('handoff_id')} 删除了证据禁止用途"
                    )
                required_reviews = required_reviews_by_target.get(evidence_id, set())
                if selected.get("manual_review_required") is True:
                    if not required_reviews:
                        errors.append(
                            f"{handoff.get('handoff_id')} 的 {evidence_id} "
                            "需要人工复核但没有 review item"
                        )
                    elif not required_reviews.issubset(approved_review_ids):
                        errors.append(
                            f"{handoff.get('handoff_id')} 的 {evidence_id} "
                            "人工复核尚未 approved"
                        )
                if selected.get("privacy_status") == "blocked":
                    errors.append(
                        f"{handoff.get('handoff_id')} 不得交接受隐私阻断的 {evidence_id}"
                    )
        for review_id in handoff.get("required_review_request_ids", []):
            if review_id not in review_items:
                errors.append(f"{handoff.get('handoff_id')} 引用不存在的 review_id：{review_id}")
            elif review_id not in approved_review_ids:
                errors.append(f"{handoff.get('handoff_id')} 所需审核尚未 approved：{review_id}")
        if handoff.get("handoff_type") == "knowledge_candidate_review_request":
            if "approve_for_knowledge_submission" not in approved_actions:
                errors.append("Knowledge Wiki Handoff 缺少 approve_for_knowledge_submission")
        if handoff.get("target_skill") == "evidence-archive":
            if handoff.get("handoff_status") not in {"ready", "ready_with_caveats"}:
                errors.append(f"{handoff.get('handoff_id')} Archive Handoff 尚未 ready")
            if "persist_in_archive" not in handoff.get("allowed_uses", []):
                errors.append(f"{handoff.get('handoff_id')} 缺少 persist_in_archive")
            if not handoff.get("payload_refs"):
                errors.append(f"{handoff.get('handoff_id')} Archive Handoff 缺少 payload_refs")
            for ref in handoff.get("payload_refs", []):
                try:
                    selected = _resolve_pointer(result, ref)
                except ContractError:
                    continue
                if isinstance(selected, dict):
                    patch_id = selected.get("patch_id")
                    if patch_id in patch_ids and patch_id not in persistable_patch_ids:
                        errors.append(f"Archive Handoff 包含未获准 Patch：{patch_id}")

    readiness_by_basis = {
        "multi_source_corroborated": "ready",
        "single_source": "exploratory_only",
        "contested": "conflict_first",
        "insufficient": "blocked",
    }
    handoff = result.get("handoff", {})
    basis = handoff.get("evidence_basis")
    usable_released = any(
        _usable_released_evidence(item)
        for item in evidence_items
        if isinstance(item, dict)
    )
    if valid_contradiction:
        derived_basis = "contested"
    elif valid_corroboration:
        derived_basis = "multi_source_corroborated"
    elif usable_released:
        derived_basis = "single_source"
    else:
        derived_basis = "insufficient"
    if basis != derived_basis:
        errors.append(
            f"evidence_basis={basis} 缺少语义依据；根据已放行 Evidence 与有效关系应为 "
            f"{derived_basis}"
        )
    if basis in readiness_by_basis:
        expected = readiness_by_basis[basis]
        if handoff.get("root_cause_readiness") != expected:
            errors.append(
                f"evidence_basis={basis} 时 root_cause_readiness 必须是 {expected}"
            )

    if for_write and handoff.get("input_gate_status") != "blocked":
        phase_status = result.get("analysis_contract", {}).get("phase_status", {})
        if phase_status.get("governance_release") not in {"completed", "partial"}:
            errors.append("正式写入前必须完成 governance_release Phase")
        if "prepare_only_semantic_phases_not_completed" in result.get("limitations", []):
            errors.append("prepare 骨架不能直接写为正式 latest")
    return errors


def _validate_json_schema(result: dict[str, Any]) -> list[str]:
    if "publication" not in result or "delivery" not in result:
        return []
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return []
    schema = _load_json(OUTPUT_SCHEMA_PATH)
    try:
        resolver = jsonschema.RefResolver(
            base_uri=OUTPUT_SCHEMA_PATH.resolve().as_uri(),
            referrer=schema,
        )
        jsonschema.Draft202012Validator(schema, resolver=resolver).validate(result)
    except Exception as exc:  # jsonschema exposes multiple validation exception classes
        return [f"JSON Schema 校验失败：{exc}"]
    return []


def validate(result_path: Path, *, for_write: bool = False) -> list[str]:
    result = _load_json(result_path)
    errors = _validate_core(result, for_write=for_write)
    errors.extend(_validate_json_schema(result))
    return errors


def atomic_write(result_path: Path, output_path: Path) -> None:
    errors = validate(result_path, for_write=True)
    if errors:
        raise ContractError("\n".join(errors))
    result = _load_json(result_path)
    result["run"]["write_status"] = "written"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        dir=str(output_path.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        temp_path = Path(temp_name)
        reread_errors = _validate_core(_load_json(temp_path), for_write=True)
        reread_errors.extend(_validate_json_schema(_load_json(temp_path)))
        if reread_errors:
            raise ContractError("\n".join(reread_errors))
        os.replace(temp_path, output_path)
    finally:
        try:
            Path(temp_name).unlink()
        except FileNotFoundError:
            pass


def _write_json(value: dict[str, Any], output: str | None) -> None:
    rendered = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if output:
        Path(output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("request")
    prepare_parser.add_argument("--output")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("candidate")

    write_parser = subparsers.add_parser("write")
    write_parser.add_argument("candidate")
    write_parser.add_argument("--output", required=True)

    publish_parser = subparsers.add_parser("publish")
    publish_parser.add_argument("candidate")
    publish_parser.add_argument("--request", required=True)
    publish_parser.add_argument("--workspace-root", type=Path, default=WORKSPACE_ROOT)
    publish_parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)

    args = parser.parse_args()
    try:
        if args.command == "prepare":
            _write_json(prepare(Path(args.request)), args.output)
        elif args.command == "validate":
            errors = validate(Path(args.candidate))
            if errors:
                raise ContractError("\n".join(errors))
            print("Evidence Govern contract validation passed.")
        elif args.command == "write":
            atomic_write(Path(args.candidate), Path(args.output))
            print(f"Evidence Govern candidate written: {args.output}")
        elif args.command == "publish":
            candidate = _load_json(Path(args.candidate))
            request = _load_json(Path(args.request))
            errors = _validate_core(candidate, for_write=True)
            if errors:
                raise ContractError("\n".join(errors))
            prepared = contract_runtime.apply_request_envelope(candidate, request)
            schema_errors = _validate_core(prepared, for_write=True)
            schema_errors.extend(_validate_json_schema(prepared))
            if schema_errors:
                raise ContractError("\n".join(schema_errors))
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "candidate.json"
                path.write_text(
                    json.dumps(prepared, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                reference = contract_runtime.publish_result(
                    workspace_root=args.workspace_root,
                    registry_path=args.registry,
                    artifact_id="governed",
                    candidate_path=path,
                    purpose_key=request["analysis_purpose"]["purpose_key"],
                    purpose_label=request["analysis_purpose"]["purpose_label"],
                    deliverables=request["requested_deliverables"],
                )
            print(json.dumps(reference, ensure_ascii=False, indent=2))
    except ContractError as exc:
        print(f"Evidence Govern contract error:\n{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
