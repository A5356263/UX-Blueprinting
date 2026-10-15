#!/usr/bin/env python3
"""Evidence Archive 3.0 deterministic authorization, snapshot and Store tool."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import stat
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

try:
    import fcntl
except ImportError:  # pragma: no cover - the suite currently targets POSIX workspaces.
    fcntl = None


WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
SKILL_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = WORKSPACE_ROOT / "shared-workflow/data-analysis/artifact-registry.json"
REQUEST_SCHEMA_PATH = SKILL_ROOT / "schemas/archive_request.schema.json"
RECORD_SCHEMA_PATH = SKILL_ROOT / "schemas/archive_record.schema.json"
SUMMARY_SCHEMA_PATH = SKILL_ROOT / "schemas/archive_summary.schema.json"
BASELINE_SCHEMA_PATH = (
    WORKSPACE_ROOT / "shared-workflow/data-analysis/schemas/baseline_item.schema.json"
)
RUNTIME_DIR = WORKSPACE_ROOT / "shared-workflow/data-analysis/runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))
import contract_runtime

ARCHIVE_VERSION = "3.0.0"
PROJECTION_BY_KIND = {
    "evidence": "canonical_evidence_item",
    "context_factor": "governed_context_assessment",
    "root_cause": "root_cause_minimum",
    "outcome": "outcome_minimum",
    "business_decision_snapshot": "business_decision_minimum",
    "baseline": "shared_baseline_item",
}
PRODUCER_BY_KIND = {
    "evidence": "evidence-govern",
    "context_factor": "evidence-govern",
    "root_cause": "root-cause-synthesis",
    "outcome": "outcome-validation-recheck",
    "business_decision_snapshot": "business-impact",
    "baseline": "objective-data-analysis",
}
ROOT_CAUSE_FIELDS = {
    "candidate_id",
    "status",
    "lifecycle_status",
    "is_primary",
    "issue_scope",
    "observed_symptoms",
    "evidence_facts",
    "evidence_chain",
    "counter_evidence",
    "alternative_explanations",
    "causal_confidence",
    "business_rule_basis_refs",
    "review_status",
    "required_next_evidence",
    "caveats",
}
CONTEXT_FIELDS = {
    "factor_id",
    "factor_type",
    "source_refs",
    "time_window",
    "affected_scope",
    "related_evidence_refs",
    "time_overlap",
    "scope_overlap",
    "possible_effect_direction",
    "disposition",
    "assessment_confidence",
    "rationale",
}


class ArchiveError(ValueError):
    """Raised when an archive operation would violate a locked contract."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_object(path: Path | str) -> dict[str, Any]:
    try:
        if str(path) == "-":
            value = json.load(sys.stdin)
        else:
            value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ArchiveError(f"无法读取 JSON：{path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ArchiveError("输入顶层必须是 object")
    return value


def _load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    registry = _load_object(path)
    if not isinstance(registry.get("artifacts"), list) or not isinstance(
        registry.get("stores"), list
    ):
        raise ArchiveError("Artifact Registry 缺少 artifacts 或 stores")
    return registry


def _registry_entry(
    registry: dict[str, Any], artifact_id: str, collection: str
) -> dict[str, Any]:
    matches = [
        item
        for item in registry.get(collection, [])
        if item.get("artifact_id") == artifact_id
    ]
    if len(matches) != 1:
        raise ArchiveError(f"Registry 中无法唯一解析 {collection}:{artifact_id}")
    return matches[0]


def _registry_path(root: Path, entry: dict[str, Any]) -> Path:
    path_value = entry.get("path")
    if not isinstance(path_value, str) or not path_value:
        raise ArchiveError(f"Registry 项缺少 path：{entry.get('artifact_id')}")
    candidate = (root / path_value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ArchiveError(f"Registry 路径越出工作区：{path_value}") from exc
    return candidate


def _load_source_artifact(
    root: Path, registry: dict[str, Any], instance_ref: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(instance_ref, dict):
        raise ArchiveError("来源必须提供 Artifact Instance Ref")
    try:
        source, _ = contract_runtime.validate_instance_ref(
            instance_ref,
            workspace_root=root,
            registry=registry,
        )
    except contract_runtime.ContractRuntimeError as exc:
        raise ArchiveError(str(exc)) from exc
    entry = _registry_entry(
        registry, str(instance_ref.get("artifact_id")), "artifacts"
    )
    return source, entry


def _resolve_selector(source: dict[str, Any], selector: dict[str, Any]) -> Any:
    path = selector.get("path")
    if not isinstance(path, str) or not path:
        raise ArchiveError("source_selector.path 不能为空")
    current: Any = source
    for token in path.split("."):
        if token.isdigit():
            raise ArchiveError("禁止使用数组下标定位长期归档对象")
        if not isinstance(current, dict) or token not in current:
            raise ArchiveError(f"来源路径不存在：{path}")
        current = current[token]
    id_field, id_value = selector.get("id_field"), selector.get("id_value")
    if isinstance(current, list):
        if not id_field or not id_value:
            raise ArchiveError(f"数组来源必须使用稳定 ID 选择：{path}")
        matches = [
            item
            for item in current
            if isinstance(item, dict) and str(item.get(id_field)) == str(id_value)
        ]
        if len(matches) != 1:
            raise ArchiveError(
                f"来源路径 {path} 无法按 {id_field}={id_value} 唯一定位"
            )
        current = matches[0]
    elif id_field:
        if not isinstance(current, dict) or str(current.get(id_field)) != str(id_value):
            raise ArchiveError(
                f"来源对象 {path} 不匹配 {id_field}={id_value}"
            )
    if not isinstance(current, dict):
        raise ArchiveError(f"来源目标必须是 object：{path}")
    return copy.deepcopy(current)


def _resolve_json_pointer(source: Any, pointer: str) -> Any:
    if pointer == "#":
        return source
    if not isinstance(pointer, str) or not pointer.startswith("#/"):
        raise ArchiveError(f"Payload Ref 不是绝对 JSON Pointer：{pointer}")
    current = source
    for raw_token in pointer[2:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            try:
                current = current[int(token)]
            except (ValueError, IndexError) as exc:
                raise ArchiveError(f"Payload Ref 无法解析：{pointer}") from exc
        elif isinstance(current, dict) and token in current:
            current = current[token]
        else:
            raise ArchiveError(f"Payload Ref 无法解析：{pointer}")
    return current


def _source_material(
    kind: str,
    source: dict[str, Any],
    selected: dict[str, Any],
    authorized_fields: list[str],
) -> dict[str, Any]:
    if kind in {"evidence", "context_factor", "root_cause", "baseline"}:
        return copy.deepcopy(selected)
    if kind == "outcome":
        return {
            "analysis_contract": copy.deepcopy(source.get("analysis_contract", {})),
            "validation_assessment": copy.deepcopy(selected),
            "limitations": copy.deepcopy(source.get("limitations", [])),
            "outcome_evidence_patch_refs": [
                str(item.get("request_id"))
                for item in source.get("analysis_results", {}).get(
                    "outcome_evidence_patch_requests", []
                )
                if isinstance(item, dict) and item.get("request_id")
            ],
        }
    if kind == "business_decision_snapshot":
        run = source.get("run", {})
        material = {
            "run": {
                key: run.get(key)
                for key in ("run_id", "project_name", "valuation_state", "generated_at")
            },
            "portfolio_summary": copy.deepcopy(selected),
        }
        if "limitations" in authorized_fields:
            material["limitations"] = copy.deepcopy(source.get("limitations", []))
        return material
    raise ArchiveError(f"不支持的 record_kind：{kind}")


def _find_item(
    source: dict[str, Any], collection: str, id_field: str, ref: str | None
) -> dict[str, Any] | None:
    if not ref:
        return None
    for item in source.get(collection, []):
        if isinstance(item, dict) and str(item.get(id_field)) == str(ref):
            return item
    return None


def _governance_material(
    source: dict[str, Any],
    governance: dict[str, Any],
    review_decisions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    patch_ref = governance.get("patch_ref")
    patch = _find_item(source, "evidence_patches", "patch_id", patch_ref)
    if patch is None:
        patch = _find_item(source, "baseline_patches", "patch_id", patch_ref)
    handoff = _find_item(
        source, "downstream_handoffs", "handoff_id", governance.get("handoff_ref")
    )
    decisions = []
    requested = set(governance.get("review_decision_refs", []))
    available_decisions = [
        *source.get("review_decisions", []),
        *(review_decisions or []),
    ]
    seen_review_ids: set[str] = set()
    for decision in available_decisions:
        if isinstance(decision, dict) and decision.get("review_id") in requested:
            review_id = str(decision["review_id"])
            if review_id in seen_review_ids:
                continue
            seen_review_ids.add(review_id)
            decisions.append(decision)
    return {
        "run": copy.deepcopy(source.get("run", {})),
        "patch": copy.deepcopy(patch),
        "handoff": copy.deepcopy(handoff),
        "review_decisions": copy.deepcopy(decisions),
    }


def prepare_request(
    draft: dict[str, Any],
    *,
    root: Path = WORKSPACE_ROOT,
    registry_path: Path = REGISTRY_PATH,
) -> dict[str, Any]:
    """Resolve sources and return a pinned, schema-ready Archive Request."""
    request = copy.deepcopy(draft)
    request.setdefault("artifact_type", "evidence_archive_request")
    request.setdefault("artifact_version", ARCHIVE_VERSION)
    request.setdefault("review_decisions", [])
    registry = _load_registry(registry_path)
    targets = request.get("targets")
    if not isinstance(targets, list):
        raise ArchiveError("targets 必须是数组")
    for target in targets:
        if not isinstance(target, dict):
            raise ArchiveError("每个 target 必须是 object")
        source, entry = _load_source_artifact(
            root, registry, target.get("source_artifact_instance_ref")
        )
        selected = _resolve_selector(source, target.get("source_selector", {}))
        run = source["run"]
        target["source_artifact_version"] = entry["current_version"]
        target["source_run_id"] = run["run_id"]
        material = _source_material(
            str(target.get("record_kind")),
            source,
            selected,
            list(target.get("authorized_field_paths", [])),
        )
        target["source_content_digest"] = _sha256(material)
        governance = target.setdefault("governance", {})
        for key, default in {
            "artifact_id": None,
            "artifact_instance_ref": None,
            "source_run_id": None,
            "content_digest": None,
            "handoff_ref": None,
            "patch_ref": None,
            "review_decision_refs": [],
        }.items():
            governance.setdefault(key, copy.deepcopy(default))
        if governance.get("artifact_id"):
            governed, _ = _load_source_artifact(
                root, registry, governance.get("artifact_instance_ref")
            )
            governance["source_run_id"] = governed["run"]["run_id"]
            governance["content_digest"] = _sha256(
                _governance_material(
                    governed,
                    governance,
                    request.get("review_decisions", []),
                )
            )
    validate_request(request, root=root, registry_path=registry_path)
    return request


def _require_keys(
    value: dict[str, Any], required: set[str], label: str, errors: list[str]
) -> None:
    missing = sorted(required - value.keys())
    if missing:
        errors.append(f"{label} 缺少字段：{', '.join(missing)}")


def _validate_json_schema(
    value: dict[str, Any], schema_path: Path
) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return []
    schema = _load_object(schema_path)
    try:
        resolver = jsonschema.RefResolver(
            base_uri=schema_path.resolve().as_uri(), referrer=schema
        )
        jsonschema.Draft202012Validator(schema, resolver=resolver).validate(value)
    except Exception as exc:
        return [f"JSON Schema 校验失败：{exc}"]
    return []


def _request_errors(request: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    request_fields = {
        "artifact_type",
        "artifact_version",
        "project_name",
        "authorization",
        "review_decisions",
        "invocation_context",
        "analysis_purpose",
        "requested_analyses",
        "input_bindings",
        "requested_deliverables",
        "publication_policy",
        "retention_policy",
        "targets",
    }
    unknown = sorted(set(request) - request_fields)
    if unknown:
        errors.append(f"request 包含未知字段：{', '.join(unknown)}")
    _require_keys(
        request,
        {
            "artifact_type",
            "artifact_version",
            "project_name",
            "authorization",
            "invocation_context",
            "analysis_purpose",
            "requested_analyses",
            "input_bindings",
            "requested_deliverables",
            "publication_policy",
            "retention_policy",
            "targets",
        },
        "request",
        errors,
    )
    if request.get("artifact_type") != "evidence_archive_request":
        errors.append("artifact_type 必须是 evidence_archive_request")
    if request.get("artifact_version") != ARCHIVE_VERSION:
        errors.append(f"artifact_version 必须是 {ARCHIVE_VERSION}")
    if not isinstance(request.get("review_decisions", []), list):
        errors.append("review_decisions 必须是数组")
    authorization = request.get("authorization")
    if not isinstance(authorization, dict):
        errors.append("authorization 必须是 object")
        return errors
    _require_keys(
        authorization,
        {
            "mode",
            "authorization_ref",
            "authorized_target_refs",
            "authorized_field_paths",
            "approved_actions",
            "review_decision_refs",
        },
        "authorization",
        errors,
    )
    authorization_fields = {
        "mode",
        "authorization_ref",
        "confirmed_at",
        "authorized_target_refs",
        "authorized_field_paths",
        "approved_actions",
        "review_decision_refs",
    }
    unknown = sorted(set(authorization) - authorization_fields)
    if unknown:
        errors.append(f"authorization 包含未知字段：{', '.join(unknown)}")
    if authorization.get("mode") not in {
        "explicit_user_request",
        "approved_handoff",
    }:
        errors.append("authorization.mode 不受支持")
    if "persist_in_archive" not in authorization.get("approved_actions", []):
        errors.append("authorization 缺少 persist_in_archive")
    authorized_targets = set(authorization.get("authorized_target_refs", []))
    authorized_fields = set(authorization.get("authorized_field_paths", []))
    targets = request.get("targets")
    if not isinstance(targets, list) or not targets:
        errors.append("targets 至少包含一项")
        return errors
    seen: set[str] = set()
    for index, target in enumerate(targets):
        label = f"targets[{index}]"
        if not isinstance(target, dict):
            errors.append(f"{label} 必须是 object")
            continue
        _require_keys(
            target,
            {
                "target_ref",
                "record_kind",
                "projection",
                "logical_object_ref",
                "source_artifact_id",
                "source_artifact_instance_ref",
                "source_artifact_version",
                "source_run_id",
                "source_selector",
                "source_content_digest",
                "authorized_field_paths",
                "record_action",
                "supersedes_ref",
                "sensitivity",
                "redaction_state",
                "allowed_uses",
                "forbidden_uses",
                "governance",
            },
            label,
            errors,
        )
        target_fields = {
            "target_ref",
            "record_kind",
            "projection",
            "logical_object_ref",
            "source_artifact_id",
            "source_artifact_instance_ref",
            "source_artifact_version",
            "source_run_id",
            "source_selector",
            "source_content_digest",
            "authorized_field_paths",
            "record_action",
            "supersedes_ref",
            "sensitivity",
            "redaction_state",
            "allowed_uses",
            "forbidden_uses",
            "governance",
        }
        unknown = sorted(set(target) - target_fields)
        if unknown:
            errors.append(f"{label} 包含未知字段：{', '.join(unknown)}")
        target_ref = target.get("target_ref")
        if target_ref in seen:
            errors.append(f"重复 target_ref：{target_ref}")
        seen.add(str(target_ref))
        if target_ref not in authorized_targets:
            errors.append(f"{label} 未被 authorization 授权：{target_ref}")
        fields = target.get("authorized_field_paths")
        if not isinstance(fields, list) or not fields:
            errors.append(f"{label}.authorized_field_paths 不能为空")
        elif not set(fields).issubset(authorized_fields):
            errors.append(f"{label} 请求字段超出 authorization")
        kind = target.get("record_kind")
        if target.get("projection") != PROJECTION_BY_KIND.get(str(kind)):
            errors.append(f"{label} projection 与 record_kind 不匹配")
        if target.get("sensitivity") == "restricted":
            errors.append(f"{label} restricted Payload 不得进入当前明文 Store")
        if target.get("sensitivity") == "confidential" and target.get(
            "redaction_state"
        ) not in {"upstream_redacted", "archive_safe_projection"}:
            errors.append(f"{label} confidential Payload 缺少归档安全快照")
        if target.get("record_action") == "new" and target.get("supersedes_ref"):
            errors.append(f"{label} new 记录不得包含 supersedes_ref")
        if target.get("record_action") == "superseding" and not target.get(
            "supersedes_ref"
        ):
            errors.append(f"{label} superseding 记录必须包含 supersedes_ref")
        digest = target.get("source_content_digest")
        if not isinstance(digest, str) or len(digest) != 64:
            errors.append(f"{label} source_content_digest 非 64 位 SHA-256")
        governance = target.get("governance")
        if not isinstance(governance, dict):
            errors.append(f"{label}.governance 必须是 object")
        else:
            governance_fields = {
                "artifact_id",
                "artifact_instance_ref",
                "source_run_id",
                "content_digest",
                "handoff_ref",
                "patch_ref",
                "review_decision_refs",
            }
            unknown = sorted(set(governance) - governance_fields)
            if unknown:
                errors.append(
                    f"{label}.governance 包含未知字段：{', '.join(unknown)}"
                )
            if authorization.get("mode") == "approved_handoff" and not governance.get(
                "handoff_ref"
            ):
                errors.append(f"{label} approved_handoff 缺少 handoff_ref")
        selector = target.get("source_selector")
        if not isinstance(selector, dict):
            errors.append(f"{label}.source_selector 必须是 object")
        else:
            unknown = sorted(set(selector) - {"path", "id_field", "id_value"})
            if unknown:
                errors.append(
                    f"{label}.source_selector 包含未知字段：{', '.join(unknown)}"
                )
        if kind == "business_decision_snapshot":
            if (
                "approve_archive_decision_snapshot"
                not in authorization.get("approved_actions", [])
            ):
                errors.append(f"{label} 缺少 approve_archive_decision_snapshot")
            if authorization.get("mode") != "explicit_user_request":
                errors.append(f"{label} Business Impact 快照必须由用户明确批准")
    return errors


def validate_request(
    request: dict[str, Any],
    *,
    root: Path = WORKSPACE_ROOT,
    registry_path: Path = REGISTRY_PATH,
) -> None:
    errors = _request_errors(request)
    errors.extend(_validate_json_schema(request, REQUEST_SCHEMA_PATH))
    if errors:
        raise ArchiveError("；".join(errors))
    registry = _load_registry(registry_path)
    authorization = request["authorization"]
    for target in request["targets"]:
        source, entry = _load_source_artifact(
            root, registry, target["source_artifact_instance_ref"]
        )
        if target["source_artifact_id"] != target["source_artifact_instance_ref"]["artifact_id"]:
            raise ArchiveError(f"{target['target_ref']} 来源 Artifact ID 不一致")
        if entry["producer_skill"] != PRODUCER_BY_KIND[target["record_kind"]]:
            raise ArchiveError(
                f"{target['record_kind']} 不接受来源 {entry['producer_skill']}"
            )
        if target["source_artifact_version"] != entry["current_version"]:
            raise ArchiveError(f"{target['target_ref']} 来源版本已变化")
        if target["source_run_id"] != source["run"]["run_id"]:
            raise ArchiveError(f"{target['target_ref']} 来源 run 已变化")
        selected = _resolve_selector(source, target["source_selector"])
        material = _source_material(
            target["record_kind"],
            source,
            selected,
            target["authorized_field_paths"],
        )
        if _sha256(material) != target["source_content_digest"]:
            raise ArchiveError(f"{target['target_ref']} 来源内容已变化，需要重新确认")
        _validate_governance(
            target,
            selected,
            authorization,
            request.get("review_decisions", []),
            root=root,
            registry=registry,
        )


def _approved_review_ids(source: dict[str, Any]) -> set[str]:
    return {
        str(item.get("review_id"))
        for item in source.get("review_decisions", [])
        if isinstance(item, dict) and item.get("decision") == "approved"
    }


def _validate_governance(
    target: dict[str, Any],
    selected: dict[str, Any],
    authorization: dict[str, Any],
    review_decisions: list[dict[str, Any]],
    *,
    root: Path,
    registry: dict[str, Any],
) -> None:
    governance = target["governance"]
    artifact_id = governance.get("artifact_id")
    if target["record_kind"] in {"evidence", "baseline"} and not artifact_id:
        raise ArchiveError(f"{target['target_ref']} 缺少 Evidence Govern Patch")
    if not artifact_id:
        return
    source, _ = _load_source_artifact(
        root, registry, governance.get("artifact_instance_ref")
    )
    if governance.get("source_run_id") != source["run"]["run_id"]:
        raise ArchiveError(f"{target['target_ref']} 治理 run 已变化")
    material = _governance_material(source, governance, review_decisions)
    if _sha256(material) != governance.get("content_digest"):
        raise ArchiveError(f"{target['target_ref']} 治理内容已变化，需要重新确认")
    approved_reviews = _approved_review_ids(source) | {
        str(item.get("review_request_id"))
        for item in review_decisions
        if isinstance(item, dict)
        and item.get("decision") == "approved"
        and item.get("source_artifact_instance_ref")
        == governance.get("artifact_instance_ref")
        and "persist_in_archive" in item.get("approved_actions", [])
    }
    for review_ref in governance.get("review_decision_refs", []):
        if review_ref not in approved_reviews:
            raise ArchiveError(f"审核决定尚未批准：{review_ref}")
    patch_ref = governance.get("patch_ref")
    patch = _find_item(source, "evidence_patches", "patch_id", patch_ref)
    patch_kind = "evidence"
    if patch is None:
        patch = _find_item(source, "baseline_patches", "patch_id", patch_ref)
        patch_kind = "baseline"
    if target["record_kind"] in {"evidence", "baseline"}:
        if patch is None or patch_kind != target["record_kind"]:
            raise ArchiveError(f"{target['target_ref']} 无法解析对应 Patch")
        if patch.get("can_persist") is not True or patch.get(
            "decision_status"
        ) not in {"not_required", "approved"}:
            raise ArchiveError(f"{patch_ref} 未获准持久化")
        selected_id = (
            selected.get("evidence_id")
            if target["record_kind"] == "evidence"
            else selected.get("baseline_id")
        )
        patch_target = (
            patch.get("target_ref")
            if target["record_kind"] == "evidence"
            else patch.get("baseline_ref")
        )
        if str(patch_target) != str(selected_id):
            raise ArchiveError(f"{patch_ref} 与归档目标不匹配")
    handoff_ref = governance.get("handoff_ref")
    if handoff_ref:
        handoff = _find_item(
            source, "downstream_handoffs", "handoff_id", handoff_ref
        )
        if handoff is None:
            raise ArchiveError(f"无法解析 Archive Handoff：{handoff_ref}")
        if handoff.get("target_skill") != "evidence-archive":
            raise ArchiveError(f"{handoff_ref} 不是面向 Evidence Archive")
        if handoff.get("handoff_status") not in {"ready", "ready_with_caveats"}:
            raise ArchiveError(f"{handoff_ref} 尚未 ready")
        if "persist_in_archive" not in handoff.get("allowed_uses", []):
            raise ArchiveError(f"{handoff_ref} 未允许 persist_in_archive")
        referenced_values = [
            _resolve_json_pointer(source, str(value))
            for value in handoff.get("payload_refs", [])
        ]
        selected_id = (
            selected.get("evidence_id")
            or selected.get("baseline_id")
            or target["source_selector"].get("id_value")
        )
        references_target = any(
            value == patch
            or (
                isinstance(value, dict)
                and selected_id
                and selected_id
                in {
                    value.get("evidence_id"),
                    value.get("baseline_id"),
                    value.get("target_ref"),
                    value.get("baseline_ref"),
                }
            )
            for value in referenced_values
        )
        if not references_target:
            raise ArchiveError(f"{handoff_ref} 未引用本次归档对象")
        for review_id in handoff.get("required_review_request_ids", []):
            if review_id not in approved_reviews:
                raise ArchiveError(f"{handoff_ref} 所需审核未批准：{review_id}")
            external_decision = next(
                (
                    item
                    for item in review_decisions
                    if isinstance(item, dict)
                    and item.get("review_request_id") == review_id
                ),
                None,
            )
            if external_decision:
                if external_decision.get("handoff_id") != handoff_ref:
                    raise ArchiveError(f"{review_id} 未绑定当前 Handoff")
                approved_payloads = set(external_decision.get("payload_refs", []))
                if not set(handoff.get("payload_refs", [])).issubset(
                    approved_payloads
                ):
                    raise ArchiveError(f"{review_id} 未覆盖当前 Handoff payload")
    elif authorization.get("mode") == "approved_handoff":
        raise ArchiveError(f"{target['target_ref']} 缺少已批准 Handoff")


def _apply_patch(
    kind: str, snapshot: dict[str, Any], governed: dict[str, Any] | None, patch_ref: str | None
) -> dict[str, Any]:
    if not governed or not patch_ref:
        return snapshot
    collection = "evidence_patches" if kind == "evidence" else "baseline_patches"
    patch = _find_item(governed, collection, "patch_id", patch_ref)
    if not patch:
        raise ArchiveError(f"Patch 在写入前消失：{patch_ref}")
    result = copy.deepcopy(snapshot)
    result["lifecycle_status"] = patch["to_status"]
    if kind == "baseline":
        result["review_status"] = patch["decision_status"]
    return result


def _project_snapshot(
    target: dict[str, Any],
    source: dict[str, Any],
    selected: dict[str, Any],
    governed: dict[str, Any] | None,
) -> dict[str, Any]:
    kind = target["record_kind"]
    if kind == "evidence":
        snapshot = _apply_patch(
            kind, copy.deepcopy(selected), governed, target["governance"].get("patch_ref")
        )
    elif kind == "context_factor":
        snapshot = {
            key: copy.deepcopy(value)
            for key, value in selected.items()
            if key in CONTEXT_FIELDS
        }
    elif kind == "root_cause":
        snapshot = {
            key: copy.deepcopy(value)
            for key, value in selected.items()
            if key in ROOT_CAUSE_FIELDS
        }
    elif kind == "outcome":
        snapshot = _source_material(
            kind, source, selected, target["authorized_field_paths"]
        )
    elif kind == "business_decision_snapshot":
        allowed = {"run", "portfolio_summary", "limitations"}
        if not set(target["authorized_field_paths"]).issubset(allowed):
            raise ArchiveError("Business Impact 归档字段超出最小决策快照")
        snapshot = _source_material(
            kind, source, selected, target["authorized_field_paths"]
        )
    elif kind == "baseline":
        snapshot = _apply_patch(
            kind, copy.deepcopy(selected), governed, target["governance"].get("patch_ref")
        )
    else:  # pragma: no cover
        raise ArchiveError(f"未知 record_kind：{kind}")
    if not isinstance(snapshot, dict):
        raise ArchiveError("归档快照必须是 object")
    return snapshot


def _event_material(record: dict[str, Any]) -> dict[str, Any]:
    record_meta = record["record"]
    return {
        "record_kind": record_meta["record_kind"],
        "record_action": record_meta["record_action"],
        "logical_object_ref": record_meta["logical_object_ref"],
        "payload_fingerprint": record_meta["payload_fingerprint"],
        "supersedes_ref": record_meta["supersedes_ref"],
        "source": record["source"],
        "authorization": record["authorization"],
        "governance": record["governance"],
        "policy": record["policy"],
    }


def _record_id(record: dict[str, Any]) -> str:
    return f"ar_{_sha256(_event_material(record))[:24]}"


def _build_archive_record(
    target: dict[str, Any],
    authorization: dict[str, Any],
    source: dict[str, Any],
    source_entry: dict[str, Any],
    selected: dict[str, Any],
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    payload_fingerprint = _sha256(snapshot)
    lineage = selected.get("lineage")
    lineage_fingerprint = (
        lineage.get("lineage_fingerprint")
        if isinstance(lineage, dict)
        else None
    )
    if not isinstance(lineage_fingerprint, str) or len(lineage_fingerprint) != 64:
        lineage_fingerprint = target["source_content_digest"]
    governance = target["governance"]
    record = {
        "record": {
            "archive_record_id": "ar_" + "0" * 24,
            "schema_version": ARCHIVE_VERSION,
            "record_kind": target["record_kind"],
            "record_action": target["record_action"],
            "logical_object_ref": target["logical_object_ref"],
            "archived_at": _utc_now(),
            "payload_fingerprint": payload_fingerprint,
            "lineage_fingerprint": lineage_fingerprint,
            "evidence_id": (
                snapshot.get("evidence_id")
                if target["record_kind"] == "evidence"
                else None
            ),
            "comparison_key": (
                snapshot.get("comparison_key")
                if target["record_kind"] == "evidence"
                else None
            ),
            "supersedes_ref": target["supersedes_ref"],
        },
        "source": {
            "artifact_id": target["source_artifact_id"],
            "artifact_type": source_entry["artifact_type"],
            "artifact_version": source_entry["current_version"],
            "producer_skill": source_entry["producer_skill"],
            "source_run_id": target["source_run_id"],
            "source_item_ref": str(
                target["source_selector"].get("id_value")
                or target["source_selector"]["path"]
            ),
            "source_content_digest": target["source_content_digest"],
            "original_lineage": copy.deepcopy(lineage),
        },
        "authorization": {
            "mode": authorization["mode"],
            "authorization_ref": authorization["authorization_ref"],
            "authorized_field_paths": copy.deepcopy(
                target["authorized_field_paths"]
            ),
            "approved_actions": copy.deepcopy(authorization["approved_actions"]),
        },
        "governance": {
            "artifact_ref": (
                f"{governance['artifact_id']}#run_id={governance['source_run_id']}"
                if governance.get("artifact_id")
                else None
            ),
            "handoff_ref": governance.get("handoff_ref"),
            "patch_ref": governance.get("patch_ref"),
            "review_decision_refs": copy.deepcopy(
                governance.get("review_decision_refs", [])
            ),
            "persistence_applied": True,
        },
        "policy": {
            "sensitivity": target["sensitivity"],
            "redaction_state": target["redaction_state"],
            "allowed_uses": copy.deepcopy(target["allowed_uses"]),
            "forbidden_uses": copy.deepcopy(target["forbidden_uses"]),
        },
        "payload_snapshot": snapshot,
    }
    record["record"]["archive_record_id"] = _record_id(record)
    return record


def _baseline_payload_fingerprint(item: dict[str, Any]) -> str:
    value = copy.deepcopy(item)
    lineage = value.get("lineage")
    if isinstance(lineage, dict):
        lineage.pop("archive_payload_fingerprint", None)
    return _sha256(value)


def _build_baseline_item(
    target: dict[str, Any],
    authorization: dict[str, Any],
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    baseline = copy.deepcopy(snapshot)
    lineage = baseline.setdefault("lineage", {})
    if not isinstance(lineage, dict):
        raise ArchiveError("Baseline lineage 必须是 object")
    lineage.update(
        {
            "archive_authorization_ref": authorization["authorization_ref"],
            "archive_patch_ref": target["governance"].get("patch_ref"),
            "source_artifact_ref": target["source_artifact_id"],
            "source_run_id": target["source_run_id"],
        }
    )
    lineage["archive_payload_fingerprint"] = _baseline_payload_fingerprint(baseline)
    return baseline


def _validate_archive_record(record: dict[str, Any]) -> None:
    required = {
        "record",
        "source",
        "authorization",
        "governance",
        "policy",
        "payload_snapshot",
    }
    if set(record) != required:
        raise ArchiveError("Archive Record 顶层字段不符合 3.0 合同")
    meta = record.get("record")
    if not isinstance(meta, dict):
        raise ArchiveError("record 必须是 object")
    meta_fields = {
        "archive_record_id",
        "schema_version",
        "record_kind",
        "record_action",
        "logical_object_ref",
        "archived_at",
        "payload_fingerprint",
        "lineage_fingerprint",
        "evidence_id",
        "comparison_key",
        "supersedes_ref",
    }
    if set(meta) != meta_fields:
        raise ArchiveError("record 元数据字段不符合 3.0 合同")
    if meta.get("schema_version") != ARCHIVE_VERSION:
        raise ArchiveError("Archive Record 版本错误")
    if meta.get("record_kind") not in set(PROJECTION_BY_KIND) - {"baseline"}:
        raise ArchiveError("Archive Record 类型错误")
    if meta.get("record_action") == "new" and meta.get("supersedes_ref"):
        raise ArchiveError("new 记录不得 supersede")
    if meta.get("record_action") == "superseding" and not meta.get(
        "supersedes_ref"
    ):
        raise ArchiveError("superseding 记录缺少 supersedes_ref")
    if _sha256(record["payload_snapshot"]) != meta.get("payload_fingerprint"):
        raise ArchiveError("Payload 指纹不匹配")
    if _record_id(record) != meta.get("archive_record_id"):
        raise ArchiveError("archive_record_id 不符合确定性身份")
    source = record.get("source")
    if not isinstance(source, dict) or set(source) != {
        "artifact_id",
        "artifact_type",
        "artifact_version",
        "producer_skill",
        "source_run_id",
        "source_item_ref",
        "source_content_digest",
        "original_lineage",
    }:
        raise ArchiveError("source 字段不符合 3.0 合同")
    if not isinstance(source.get("source_content_digest"), str) or len(
        source["source_content_digest"]
    ) != 64:
        raise ArchiveError("source_content_digest 非 64 位 SHA-256")
    authorization = record.get("authorization")
    if not isinstance(authorization, dict) or set(authorization) != {
        "mode",
        "authorization_ref",
        "authorized_field_paths",
        "approved_actions",
    }:
        raise ArchiveError("authorization 字段不符合 3.0 合同")
    if "persist_in_archive" not in authorization.get("approved_actions", []):
        raise ArchiveError("Archive Record 缺少 persist_in_archive 授权")
    governance = record.get("governance")
    if not isinstance(governance, dict) or set(governance) != {
        "artifact_ref",
        "handoff_ref",
        "patch_ref",
        "review_decision_refs",
        "persistence_applied",
    }:
        raise ArchiveError("governance 字段不符合 3.0 合同")
    if governance.get("persistence_applied") is not True:
        raise ArchiveError("Archive Record 未标记 persistence_applied")
    policy = record.get("policy")
    if not isinstance(policy, dict) or set(policy) != {
        "sensitivity",
        "redaction_state",
        "allowed_uses",
        "forbidden_uses",
    }:
        raise ArchiveError("policy 字段不符合 3.0 合同")
    if policy.get("sensitivity") == "restricted":
        raise ArchiveError("restricted Payload 不得进入当前 Store")
    if policy.get("sensitivity") not in {"internal", "confidential"}:
        raise ArchiveError("Archive Record sensitivity 不受支持")
    if policy.get("sensitivity") == "confidential" and policy.get(
        "redaction_state"
    ) not in {"upstream_redacted", "archive_safe_projection"}:
        raise ArchiveError("confidential Payload 缺少归档安全状态")
    if not isinstance(policy.get("allowed_uses"), list) or not policy["allowed_uses"]:
        raise ArchiveError("allowed_uses 不能为空")
    if not isinstance(policy.get("forbidden_uses"), list) or not policy[
        "forbidden_uses"
    ]:
        raise ArchiveError("forbidden_uses 不能为空")
    item = record["payload_snapshot"]
    if not isinstance(item, dict):
        raise ArchiveError("payload_snapshot 必须是 object")
    kind = meta.get("record_kind")
    if kind == "evidence":
        required_evidence = {
            "evidence_id",
            "evidence_type",
            "claim_type",
            "claim_summary",
            "scope",
            "time_window",
            "comparison_key",
            "lineage",
            "evidence_strength",
            "lifecycle_status",
            "privacy_status",
            "manual_review_required",
            "allowed_uses",
            "forbidden_uses",
            "business_rule_basis_refs",
            "limitations",
        }
        if not required_evidence.issubset(item) or set(item) - (
            required_evidence | {"scene_descriptor"}
        ):
            raise ArchiveError("Evidence Snapshot 不符合 Canonical Evidence Item")
        if not item.get("evidence_id"):
            raise ArchiveError("Evidence Snapshot 缺少 evidence_id")
    elif kind == "context_factor":
        if set(item) != CONTEXT_FIELDS:
            raise ArchiveError("Context Factor Snapshot 字段不完整")
    elif kind == "root_cause":
        required_root = {
            "candidate_id",
            "status",
            "lifecycle_status",
            "is_primary",
            "issue_scope",
            "observed_symptoms",
            "evidence_facts",
            "evidence_chain",
            "counter_evidence",
            "alternative_explanations",
            "causal_confidence",
            "business_rule_basis_refs",
            "review_status",
            "required_next_evidence",
            "caveats",
        }
        if not required_root.issubset(item) or set(item) - ROOT_CAUSE_FIELDS:
            raise ArchiveError("Root Cause Snapshot 字段不符合白名单")
    elif kind == "outcome":
        if not {
            "analysis_contract",
            "validation_assessment",
            "limitations",
        }.issubset(item) or set(item) - {
            "analysis_contract",
            "validation_assessment",
            "limitations",
            "outcome_evidence_patch_refs",
        }:
            raise ArchiveError("Outcome Snapshot 字段不符合白名单")
    elif kind == "business_decision_snapshot":
        if not {"run", "portfolio_summary"}.issubset(item) or set(item) - {
            "run",
            "portfolio_summary",
            "limitations",
        }:
            raise ArchiveError("Business Decision Snapshot 字段不符合白名单")
    errors = _validate_json_schema(record, RECORD_SCHEMA_PATH)
    if errors:
        raise ArchiveError("；".join(errors))


def _validate_baseline(item: dict[str, Any]) -> None:
    required = {
        "baseline_id",
        "baseline_version",
        "metric_contract_ref",
        "scenario_key",
        "grain",
        "baseline_window",
        "period_granularity",
        "calculation_method",
        "baseline_values",
        "comparability_contract",
        "comparison_fingerprint",
        "confidence",
        "lifecycle_status",
        "review_status",
        "lineage",
        "supersedes_ref",
    }
    if set(item) - (
        required | {"segment_definition_ref"}
    ):
        raise ArchiveError("Baseline 包含 Shared Baseline Item 之外的字段")
    missing = required - item.keys()
    if missing:
        raise ArchiveError(f"Baseline 缺少字段：{', '.join(sorted(missing))}")
    if item.get("lifecycle_status") == "proposed":
        raise ArchiveError("proposed Baseline 不得写入 Store")
    if item.get("review_status") not in {"not_required", "approved"}:
        raise ArchiveError("Baseline 尚未获准持久化")
    lineage = item.get("lineage")
    if not isinstance(lineage, dict):
        raise ArchiveError("Baseline lineage 必须是 object")
    expected = lineage.get("archive_payload_fingerprint")
    if expected != _baseline_payload_fingerprint(item):
        raise ArchiveError("Baseline Archive Payload 指纹不匹配")
    errors = _validate_json_schema(item, BASELINE_SCHEMA_PATH)
    if errors:
        raise ArchiveError("；".join(errors))


def _check_store_file(path: Path) -> None:
    if not path.exists():
        return
    details = path.stat()
    if not stat.S_ISREG(details.st_mode):
        raise ArchiveError(f"Store 不是普通文件：{path}")
    if stat.S_IMODE(details.st_mode) & 0o077:
        raise ArchiveError(f"Store 权限过宽，必须为 0600：{path}")


def _read_jsonl(
    path: Path, validator: Callable[[dict[str, Any]], None]
) -> list[dict[str, Any]]:
    _check_store_file(path)
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ArchiveError(
                    f"Store 第 {line_number} 行不是合法 JSON：{exc}"
                ) from exc
            if not isinstance(value, dict):
                raise ArchiveError(f"Store 第 {line_number} 行不是 object")
            validator(value)
            records.append(value)
    return records


@contextmanager
def _store_lock(root: Path, store_artifact_id: str) -> Iterator[None]:
    if fcntl is None:
        raise ArchiveError("当前平台不支持 POSIX 文件锁")
    lock_id = _sha256({"root": str(root.resolve()), "store": store_artifact_id})[:20]
    lock_path = Path(tempfile.gettempdir()) / f"evidence-archive-{lock_id}.lock"
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _atomic_jsonl_replace(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            for record in records:
                handle.write(_canonical_json(record) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def _record_ref(record: dict[str, Any]) -> str:
    return (
        "archived-evidence-store#archive_record_id="
        + record["record"]["archive_record_id"]
    )


def _baseline_ref(item: dict[str, Any]) -> str:
    return (
        f"baseline-store#baseline_id={item['baseline_id']}"
        f"&baseline_version={item['baseline_version']}"
    )


def _parse_supersedes_record_ref(value: str) -> str:
    prefix = "archived-evidence-store#archive_record_id="
    if not value.startswith(prefix):
        raise ArchiveError("supersedes_ref 不是标准 Archive Record Ref")
    return value[len(prefix) :]


def _parse_supersedes_baseline_ref(value: str) -> tuple[str, str]:
    prefix = "baseline-store#baseline_id="
    if not value.startswith(prefix) or "&baseline_version=" not in value:
        raise ArchiveError("supersedes_ref 不是标准 Baseline Ref")
    identity, version = value[len(prefix) :].split("&baseline_version=", 1)
    return identity, version


def _validate_record_chains(records: list[dict[str, Any]]) -> None:
    by_id: dict[str, dict[str, Any]] = {}
    successor_by_ref: dict[str, str] = {}
    for record in records:
        record_id = record["record"]["archive_record_id"]
        if record_id in by_id:
            raise ArchiveError(f"Store 存在重复 archive_record_id：{record_id}")
        action = record["record"]["record_action"]
        supersedes = record["record"].get("supersedes_ref")
        if action == "superseding":
            previous_id = _parse_supersedes_record_ref(str(supersedes))
            previous = by_id.get(previous_id)
            if previous is None:
                raise ArchiveError(f"supersedes_ref 指向不存在或未来记录：{supersedes}")
            if previous["record"]["record_kind"] != record["record"]["record_kind"]:
                raise ArchiveError("superseding 不得跨 record_kind")
            if (
                previous["record"]["logical_object_ref"]
                != record["record"]["logical_object_ref"]
            ):
                raise ArchiveError("superseding 不得跨 logical_object_ref")
            if supersedes in successor_by_ref:
                raise ArchiveError(f"superseding 链出现分叉：{supersedes}")
            successor_by_ref[str(supersedes)] = record_id
        elif supersedes:
            raise ArchiveError("new 记录不得包含 supersedes_ref")
        by_id[record_id] = record


def _validate_baseline_chains(records: list[dict[str, Any]]) -> None:
    by_key: dict[tuple[str, str], dict[str, Any]] = {}
    successor_by_ref: set[str] = set()
    for item in records:
        key = (str(item["baseline_id"]), str(item["baseline_version"]))
        if key in by_key:
            raise ArchiveError(f"Store 存在重复 Baseline：{key[0]}@{key[1]}")
        supersedes = item.get("supersedes_ref")
        if supersedes:
            previous_key = _parse_supersedes_baseline_ref(str(supersedes))
            if previous_key not in by_key:
                raise ArchiveError(f"Baseline supersedes_ref 不存在：{supersedes}")
            if previous_key[0] != key[0]:
                raise ArchiveError("Baseline superseding 不得跨 baseline_id")
            if str(supersedes) in successor_by_ref:
                raise ArchiveError(f"Baseline 链出现分叉：{supersedes}")
            successor_by_ref.add(str(supersedes))
        elif any(existing[0] == key[0] for existing in by_key):
            raise ArchiveError("同一 baseline_id 的新版本必须声明 supersedes_ref")
        by_key[key] = item


def _commit_batch(
    root: Path,
    registry: dict[str, Any],
    store_artifact_id: str,
    candidates: list[dict[str, Any]],
) -> tuple[list[tuple[str, str]], dict[str, Any]]:
    entry = _registry_entry(registry, store_artifact_id, "stores")
    if entry.get("current_version") != ARCHIVE_VERSION:
        raise ArchiveError(f"{store_artifact_id} Registry 版本不是 {ARCHIVE_VERSION}")
    if "append_only" not in str(entry.get("write_policy")):
        raise ArchiveError(f"{store_artifact_id} 不允许 append-only 写入")
    path = _registry_path(root, entry)
    validator = (
        _validate_archive_record
        if store_artifact_id == "archived-evidence-store"
        else _validate_baseline
    )
    chain_validator = (
        _validate_record_chains
        if store_artifact_id == "archived-evidence-store"
        else _validate_baseline_chains
    )
    with _store_lock(root, store_artifact_id):
        existing = _read_jsonl(path, validator)
        chain_validator(existing)
        before = len(existing)
        results: list[tuple[str, str]] = []
        accepted: list[dict[str, Any]] = []
        if store_artifact_id == "archived-evidence-store":
            by_id = {
                item["record"]["archive_record_id"]: item for item in existing
            }
            for item in candidates:
                validator(item)
                identity = item["record"]["archive_record_id"]
                if identity in by_id:
                    results.append(("duplicate", _record_ref(by_id[identity])))
                else:
                    accepted.append(item)
                    by_id[identity] = item
                    results.append(("archived", _record_ref(item)))
        else:
            by_key = {
                (str(item["baseline_id"]), str(item["baseline_version"])): item
                for item in existing
            }
            for item in candidates:
                validator(item)
                key = (str(item["baseline_id"]), str(item["baseline_version"]))
                if key in by_key:
                    if _baseline_payload_fingerprint(by_key[key]) != _baseline_payload_fingerprint(item):
                        raise ArchiveError(
                            f"Baseline {key[0]}@{key[1]} 内容冲突"
                        )
                    results.append(("duplicate", _baseline_ref(by_key[key])))
                else:
                    accepted.append(item)
                    by_key[key] = item
                    results.append(("archived", _baseline_ref(item)))
        combined = existing + accepted
        chain_validator(combined)
        if accepted:
            _atomic_jsonl_replace(path, combined)
            reread = _read_jsonl(path, validator)
            chain_validator(reread)
            if len(reread) != len(combined):
                raise ArchiveError("Store 原子提交后记录数不一致")
        update = {
            "store_artifact_id": store_artifact_id,
            "store_ref": entry["path"],
            "before_count": before,
            "after_count": len(combined),
            "appended_count": len(accepted),
        }
        return results, update


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def _governance_refs(target: dict[str, Any]) -> list[str]:
    values = [
        target["governance"].get("handoff_ref"),
        target["governance"].get("patch_ref"),
        *target["governance"].get("review_decision_refs", []),
    ]
    return [str(value) for value in values if value]


def archive_request(
    request: dict[str, Any],
    *,
    root: Path = WORKSPACE_ROOT,
    registry_path: Path = REGISTRY_PATH,
    summary_writer: Callable[[Path, dict[str, Any]], None] = _atomic_write_json,
) -> dict[str, Any]:
    """Validate, project and atomically archive all authorized targets."""
    validate_request(request, root=root, registry_path=registry_path)
    registry = _load_registry(registry_path)
    prepared: list[dict[str, Any]] = []
    for target in request["targets"]:
        source, entry = _load_source_artifact(
            root, registry, target["source_artifact_instance_ref"]
        )
        selected = _resolve_selector(source, target["source_selector"])
        governed = None
        if target["governance"].get("artifact_id"):
            governed, _ = _load_source_artifact(
                root, registry, target["governance"]["artifact_instance_ref"]
            )
        snapshot = _project_snapshot(target, source, selected, governed)
        if target["record_kind"] == "baseline":
            payload = _build_baseline_item(
                target, request["authorization"], snapshot
            )
            _validate_baseline(payload)
            fingerprint = payload["lineage"]["archive_payload_fingerprint"]
            store_id = "baseline-store"
        else:
            payload = _build_archive_record(
                target,
                request["authorization"],
                source,
                entry,
                selected,
                snapshot,
            )
            _validate_archive_record(payload)
            fingerprint = payload["record"]["payload_fingerprint"]
            store_id = "archived-evidence-store"
        prepared.append(
            {
                "target": target,
                "payload": payload,
                "store_id": store_id,
                "payload_fingerprint": fingerprint,
            }
        )

    result_by_target: dict[str, tuple[str, str | None, str | None]] = {}
    store_updates: list[dict[str, Any]] = []
    for store_id in ("archived-evidence-store", "baseline-store"):
        group = [item for item in prepared if item["store_id"] == store_id]
        if not group:
            continue
        try:
            committed, update = _commit_batch(
                root,
                registry,
                store_id,
                [item["payload"] for item in group],
            )
            store_updates.append(update)
            for item, (status, record_ref) in zip(group, committed):
                result_by_target[item["target"]["target_ref"]] = (
                    status,
                    record_ref,
                    None,
                )
        except ArchiveError as exc:
            for item in group:
                result_by_target[item["target"]["target_ref"]] = (
                    "failed",
                    None,
                    str(exc),
                )

    archive_results = []
    for item in prepared:
        target = item["target"]
        result, record_ref, reason = result_by_target[target["target_ref"]]
        archive_results.append(
            {
                "target_ref": target["target_ref"],
                "record_kind": target["record_kind"],
                "result": result,
                "archive_record_ref": record_ref,
                "payload_fingerprint": item["payload_fingerprint"],
                "authorization_ref": request["authorization"]["authorization_ref"],
                "governance_or_review_refs": _governance_refs(target),
                "sensitivity": target["sensitivity"],
                "reason": reason,
            }
        )
    successful = [
        item
        for item in archive_results
        if item["result"] in {"archived", "duplicate"}
    ]
    if not successful:
        raise ArchiveError(
            "本次没有记录成功归档；"
            + "；".join(item["reason"] or "unknown" for item in archive_results)
        )
    write_status = (
        "partial"
        if any(item["result"] in {"failed", "skipped"} for item in archive_results)
        else "written"
    )
    generated_at = _utc_now()
    summary = {
        "run": {
            "artifact_type": "evidence_archive_summary",
            "artifact_version": ARCHIVE_VERSION,
            "producer_skill": "evidence-archive",
            "run_id": f"ea_{_sha256({'at': generated_at, 'targets': request['targets'], 'results': archive_results})[:16]}",
            "project_name": request["project_name"],
            "generated_at": generated_at,
            "source_mode": request["authorization"]["mode"],
            "sources": sorted(
                {item["source_artifact_id"] for item in request["targets"]}
            ),
            "write_status": write_status,
            "invocation_context": request["invocation_context"],
            "analysis_purpose": request["analysis_purpose"],
            "status": (
                "completed_with_caveats"
                if write_status == "partial"
                else "completed"
            ),
        },
        "data_quality": {
            "source_contract_valid": True,
            "authorization_valid": True,
            "snapshot_valid": True,
            "store_integrity": (
                "valid_with_caveats" if write_status == "partial" else "valid"
            ),
        },
        "authorization": {
            "mode": request["authorization"]["mode"],
            "authorization_ref": request["authorization"]["authorization_ref"],
            "approved_actions": request["authorization"]["approved_actions"],
            "review_decision_refs": request["authorization"][
                "review_decision_refs"
            ],
        },
        "archive_target_refs": [
            item["target_ref"] for item in request["targets"]
        ],
        "archive_results": archive_results,
        "store_updates": store_updates,
        "limitations": (
            ["部分 Store 写入失败；已成功写入的记录不会回滚"]
            if write_status == "partial"
            else []
        ),
        "handoff": {
            "input_gate_status": (
                "partial" if write_status == "partial" else "ready"
            ),
            "handoff_status": "terminal",
            "allowed_uses": [
                "exact_archive_record_lookup",
                "historical_trace",
            ],
            "forbidden_uses": [
                "treat_all_archive_records_as_evidence",
                "automatic_knowledge_publication",
                "current_context_inference",
            ],
            "blocked_reasons": [],
        },
    }
    summary = contract_runtime.apply_request_envelope(summary, request)
    schema_errors = _validate_json_schema(summary, SUMMARY_SCHEMA_PATH)
    if schema_errors:
        raise ArchiveError("；".join(schema_errors))
    summary_entry = _registry_entry(registry, "archive-summary", "artifacts")
    if summary_entry.get("current_version") != ARCHIVE_VERSION:
        raise ArchiveError("archive-summary Registry 版本不是 3.0.0")
    candidate_dir = root / "spark-output/.candidates"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    candidate_path = candidate_dir / f"{summary['run']['run_id']}.json"
    summary_writer(candidate_path, summary)
    try:
        reference = contract_runtime.publish_result(
            workspace_root=root,
            registry_path=registry_path,
            artifact_id="archive-summary",
            candidate_path=candidate_path,
            purpose_key=request["analysis_purpose"]["purpose_key"],
            purpose_label=request["analysis_purpose"]["purpose_label"],
            deliverables=request["requested_deliverables"],
        )
        return _load_object(root / reference["artifact_path"])
    finally:
        try:
            candidate_path.unlink()
        except FileNotFoundError:
            pass


def get_record(
    kind: str,
    *,
    archive_record_id: str | None = None,
    baseline_id: str | None = None,
    baseline_version: str | None = None,
    root: Path = WORKSPACE_ROOT,
    registry_path: Path = REGISTRY_PATH,
) -> dict[str, Any]:
    registry = _load_registry(registry_path)
    if kind == "evidence":
        entry = _registry_entry(registry, "archived-evidence-store", "stores")
        path = _registry_path(root, entry)
        if not archive_record_id:
            raise ArchiveError("必须提供 archive_record_id")
        records = _read_jsonl(path, _validate_archive_record)
        _validate_record_chains(records)
        matches = [
            item
            for item in records
            if item["record"]["archive_record_id"] == archive_record_id
        ]
    elif kind == "baseline":
        entry = _registry_entry(registry, "baseline-store", "stores")
        path = _registry_path(root, entry)
        if not baseline_id or baseline_version is None:
            raise ArchiveError("必须同时提供 baseline_id 和 baseline_version")
        records = _read_jsonl(path, _validate_baseline)
        _validate_baseline_chains(records)
        matches = [
            item
            for item in records
            if str(item["baseline_id"]) == str(baseline_id)
            and str(item["baseline_version"]) == str(baseline_version)
        ]
    else:
        raise ArchiveError("get 只支持 evidence 或 baseline")
    if len(matches) != 1:
        raise ArchiveError(f"精确引用匹配到 {len(matches)} 条记录")
    return matches[0]


def verify_store(
    kind: str,
    *,
    root: Path = WORKSPACE_ROOT,
    registry_path: Path = REGISTRY_PATH,
) -> dict[str, Any]:
    registry = _load_registry(registry_path)
    store_id = (
        "archived-evidence-store" if kind == "evidence" else "baseline-store"
    )
    entry = _registry_entry(registry, store_id, "stores")
    path = _registry_path(root, entry)
    validator = _validate_archive_record if kind == "evidence" else _validate_baseline
    records = _read_jsonl(path, validator)
    (
        _validate_record_chains(records)
        if kind == "evidence"
        else _validate_baseline_chains(records)
    )
    return {
        "store_artifact_id": store_id,
        "status": "valid",
        "record_count": len(records),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "path": entry["path"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evidence Archive 3.0")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("prepare", "validate", "archive"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--request", required=True)
    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("--kind", choices=["evidence", "baseline"], required=True)
    get_parser.add_argument("--archive-record-id")
    get_parser.add_argument("--baseline-id")
    get_parser.add_argument("--baseline-version")
    verify_parser = subparsers.add_parser("verify-store")
    verify_parser.add_argument(
        "--kind", choices=["evidence", "baseline"], required=True
    )
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            result = prepare_request(_load_object(args.request))
        elif args.command == "validate":
            request = _load_object(args.request)
            validate_request(request)
            result = {"result": "valid"}
        elif args.command == "archive":
            result = archive_request(_load_object(args.request))
        elif args.command == "get":
            result = get_record(
                args.kind,
                archive_record_id=args.archive_record_id,
                baseline_id=args.baseline_id,
                baseline_version=args.baseline_version,
            )
        else:
            result = verify_store(args.kind)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except ArchiveError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
