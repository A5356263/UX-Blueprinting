#!/usr/bin/env python3
"""Validate, normalize, write, and render Experience Heuristic Analysis 4.0.0."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit


VERSION = "4.0.0"
SKILL_DIR = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
INPUT_SCHEMA = SKILL_DIR / "schemas/input.schema.json"
OUTPUT_SCHEMA = SKILL_DIR / "schemas/output.schema.json"
DEFAULT_REPORT = WORKSPACE_ROOT / "spark-output/experience-heuristic-analysis/experience-heuristic-report.md"
VOCABULARY = WORKSPACE_ROOT / "shared-workflow/data-analysis/presentation-vocabulary.json"
REGISTRY = WORKSPACE_ROOT / "shared-workflow/data-analysis/artifact-registry.json"
RUNTIME_DIR = WORKSPACE_ROOT / "shared-workflow/data-analysis/runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))
import contract_runtime

TOP_LEVEL = {
    "run", "analysis_contract", "data_quality", "analysis_results", "findings",
    "evidence_items", "business_rule_basis", "validation_requests",
    "limitations", "handoff",
}
FINAL_TOP_LEVEL = TOP_LEVEL | {"publication", "delivery"}
CATEGORIES = {
    "flow-continuity", "ia", "components", "visual-hierarchy", "edge-states",
    "copy", "responsive", "feedback", "accessibility", "brief-consistency",
}
SEVERITIES = {"blocker", "major", "minor", "note"}
PRIVACY = {"safe", "restricted", "needs_review", "blocked"}
EVIDENCE_CLAIMS = {"heuristic_observation", "risk_hypothesis"}
EVIDENCE_ALLOWED_USES = {
    "evidence_governance", "supporting_evidence",
    "preliminary_problem_signal", "explicit_visualization",
}
REQUIRED_FORBIDDEN_USES = {
    "user_behavior_fact", "prevalence_claim", "causal_claim",
    "final_root_cause", "business_impact_scale", "intervention_effectiveness",
}
SOURCE_TYPES = {
    "screenshot", "prototype", "figma_export", "frontend_code", "dom", "a11y",
    "runtime", "flow", "blueprint", "brief", "stories", "design_guideline",
    "design_system", "business_rule", "description",
}
EVIDENCE_SOURCE_TYPES = {
    "screenshot", "prototype", "figma_export", "frontend_code", "dom", "a11y",
    "runtime", "flow", "blueprint",
}
CONTEXT_SOURCE_TYPES = {
    "brief", "stories", "design_guideline", "design_system", "business_rule",
}
CAPABILITIES = {
    "screenshot": {"visible_layout", "visual_hierarchy", "visible_copy", "static_state", "visible_accessibility_risk", "responsive_snapshot"},
    "prototype": {"visible_layout", "visual_hierarchy", "visible_copy", "static_state", "interaction_flow", "state_transition", "responsive_spec"},
    "figma_export": {"visible_layout", "visual_hierarchy", "visible_copy", "static_state", "design_token_usage", "responsive_spec"},
    "frontend_code": {"code_structure", "semantic_markup", "state_implementation", "design_token_usage"},
    "dom": {"dom_structure", "semantic_markup", "state_attributes"},
    "a11y": {"accessibility_tree", "accessible_name", "semantic_role", "state_attributes"},
    "runtime": {"runtime_interaction", "state_transition", "feedback_behavior", "error_state"},
    "flow": {"interaction_flow", "state_transition", "branching"},
    "blueprint": {"interaction_flow", "state_transition", "expected_behavior", "brief_consistency"},
    "brief": {"expected_behavior", "brief_consistency"},
    "stories": {"expected_behavior", "brief_consistency"},
    "design_guideline": {"design_rule"},
    "design_system": {"design_rule", "design_token_usage"},
    "business_rule": {"business_rule"},
    "description": {"reported_interface_description"},
}
GAP_TYPES = {
    "additional_interface_material", "manual_interface_review",
    "business_rule_confirmation", "objective_behavior_confirmation",
    "subjective_feedback_confirmation", "accessibility_specialist_review",
    "device_or_browser_verification", "design_rule_conflict_confirmation",
    "privacy_review",
}
BANNED_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"用户一定(会|不会|能|不能|看到|看不到)", r"真实眼动", r"模拟眼动",
        r"已验证根因", r"最终根因", r"真实发生率", r"方案(已经)?有效",
        r"validated[_ ]evidence", r"verified root cause",
    )
]
SECRET_QUERY = re.compile(r"(token|secret|signature|sig|key|credential|auth)=", re.I)


class PackageError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PackageError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PackageError(f"invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise PackageError("root must be an object")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PackageError(message)


def require_keys(value: Any, required: set[str], label: str, allowed: set[str] | None = None) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    missing = required - set(value)
    require(not missing, f"{label} missing required fields: {', '.join(sorted(missing))}")
    if allowed is not None:
        extra = set(value) - allowed
        require(not extra, f"{label} contains unsupported fields: {', '.join(sorted(extra))}")
    return value


def unique_ids(values: Any, key: str, label: str) -> set[str]:
    require(isinstance(values, list), f"{label} must be a list")
    identifiers: list[str] = []
    for index, item in enumerate(values):
        require(isinstance(item, dict), f"{label}[{index}] must be an object")
        identifier = item.get(key)
        require(isinstance(identifier, str) and bool(identifier), f"{label}[{index}].{key} is required")
        identifiers.append(identifier)
    require(len(identifiers) == len(set(identifiers)), f"{label} contains duplicate {key}")
    return set(identifiers)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def input_fingerprint(request: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(request).encode("utf-8")).hexdigest()


def finding_key(project_name: str, finding: dict[str, Any]) -> str:
    identity = {
        "project": project_name,
        "page_or_flow": finding.get("page_or_flow"),
        "location": finding.get("location"),
        "state": finding.get("state"),
        "category": finding.get("category"),
        "risk_tags": sorted(str(value) for value in finding.get("risk_tags", [])),
    }
    return f"ehk_{hashlib.sha256(canonical_json(identity).encode()).hexdigest()[:16]}"


def is_safe_source_ref(value: str) -> bool:
    if not value or Path(value).is_absolute() or value.startswith(("file://", "vscode://")):
        return False
    parsed = urlsplit(value)
    if parsed.query and SECRET_QUERY.search(parsed.query):
        return False
    return True


def validate_locator(locator: Any, label: str, *, comparison: bool = False) -> None:
    require(isinstance(locator, dict), f"{label} must be an object")
    if comparison:
        ref_type = locator.get("ref_type")
        require(ref_type in {"artifact", "source"}, f"{label}.ref_type is invalid")
        if ref_type == "artifact":
            require(set(locator) == {"ref_type", "artifact_instance_ref", "payload_ref"}, f"{label} artifact locator fields are invalid")
            require(str(locator["payload_ref"]).startswith("#/"), f"{label}.payload_ref must be an absolute JSON Pointer")
        else:
            require(set(locator) == {"ref_type", "source_id", "fingerprint"}, f"{label} source locator fields are invalid")
            require(bool(locator["source_id"]) and bool(locator["fingerprint"]), f"{label} source locator is incomplete")
    else:
        require(set(locator) == {"artifact_instance_ref", "payload_ref"}, f"{label} fields are invalid")
        require(str(locator["payload_ref"]).startswith("#/"), f"{label}.payload_ref must be an absolute JSON Pointer")


def _optional_jsonschema(instance: dict[str, Any], schema_path: Path) -> None:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return
    schema = load_json(schema_path)
    try:
        resolver = jsonschema.RefResolver(
            base_uri=schema_path.resolve().as_uri(),
            referrer=schema,
        )
        jsonschema.Draft202012Validator(schema, resolver=resolver).validate(instance)
    except Exception as exc:
        raise PackageError(f"Draft 2020-12 schema validation failed: {exc}") from exc


def validate_input(request: dict[str, Any]) -> None:
    allowed = {
        "artifact_type", "artifact_version", "project_name", "source_mode",
        "analysis_mode", "sources", "analysis_scope", "focus_areas",
        "focus_source_refs", "explicit_upstream_refs", "baseline_ref",
        "current_ref", "business_rule_inputs", "project_rule_source_refs",
        "invocation_context", "analysis_purpose", "input_bindings",
        "requested_analyses", "requested_deliverables", "publication_policy", "retention_policy",
    }
    required = {
        "artifact_type", "artifact_version", "source_mode", "analysis_mode",
        "sources", "analysis_scope", "invocation_context", "analysis_purpose",
        "requested_analyses", "input_bindings", "requested_deliverables", "publication_policy",
        "retention_policy",
    }
    require_keys(request, required, "input", allowed)
    require(request["artifact_type"] == "heuristic_analysis_request", "unsupported input artifact_type")
    require(request["artifact_version"] == VERSION, f"input artifact_version must be {VERSION}")
    require(request["source_mode"] in {"independent", "chain_context"}, "unsupported source_mode")
    require(request["analysis_mode"] in {"discovery", "intervention_recheck"}, "unsupported analysis_mode")
    source_ids = unique_ids(request["sources"], "source_id", "input.sources")
    require(bool(source_ids), "input.sources requires at least one source")
    for index, source in enumerate(request["sources"]):
        label = f"input.sources[{index}]"
        require_keys(source, {"source_id", "source_type", "source_ref", "acquisition"}, label, {"source_id", "source_type", "source_ref", "acquisition", "description", "upstream_locator"})
        require(source["source_type"] in SOURCE_TYPES, f"{label}.source_type is invalid")
        require(source["acquisition"] in {"user_provided", "tool_collected", "explicit_upstream"}, f"{label}.acquisition is invalid")
        require(is_safe_source_ref(source["source_ref"]), f"{label}.source_ref is unsafe; use a relative or opaque reference")
        if source["acquisition"] == "explicit_upstream":
            validate_locator(source.get("upstream_locator"), f"{label}.upstream_locator")
        else:
            require(source.get("upstream_locator") is None, f"{label} cannot carry upstream_locator")
    upstream = request.get("explicit_upstream_refs", [])
    require(isinstance(upstream, list), "explicit_upstream_refs must be a list")
    for index, locator in enumerate(upstream):
        validate_locator(locator, f"explicit_upstream_refs[{index}]")
    if request["source_mode"] == "independent":
        require(not upstream, "independent mode cannot carry explicit_upstream_refs")
        require(all(item["acquisition"] != "explicit_upstream" for item in request["sources"]), "independent mode cannot use explicit_upstream sources")
    else:
        locators = [
            item["upstream_locator"]
            for item in request["sources"]
            if item["acquisition"] == "explicit_upstream"
        ] + list(upstream)
        for locator in (request.get("baseline_ref"), request.get("current_ref")):
            if isinstance(locator, dict) and locator.get("ref_type") == "artifact":
                locators.append(locator)
        bindings = [
            item.get("binding_ref")
            for item in request["input_bindings"]
            if item.get("binding_type") == "artifact_instance"
        ]
        registry = load_json(REGISTRY)
        for locator in locators:
            instance_ref = locator["artifact_instance_ref"]
            require(
                bindings.count(instance_ref) == 1,
                "every upstream Artifact Instance must have exactly one input binding",
            )
            try:
                payload, _ = contract_runtime.validate_instance_ref(
                    instance_ref,
                    workspace_root=WORKSPACE_ROOT,
                    registry=registry,
                )
                contract_runtime.resolve_pointer(payload, locator["payload_ref"])
            except contract_runtime.ContractRuntimeError as exc:
                raise PackageError(str(exc)) from exc
    scope = require_keys(request["analysis_scope"], {"scope_type", "included", "excluded", "scope_reason", "review_areas"}, "analysis_scope", {"scope_type", "included", "excluded", "scope_reason", "review_areas"})
    require(scope["scope_type"] in {"full_review", "scoped_review", "diff_driven_review"}, "invalid scope_type")
    review_areas = scope["review_areas"]
    require(isinstance(review_areas, list) and bool(review_areas) and set(review_areas) <= CATEGORIES, "review_areas is invalid")
    require(len(review_areas) == len(set(review_areas)), "review_areas contains duplicates")
    if scope["scope_type"] == "full_review":
        require(set(review_areas) == CATEGORIES, "full_review must include all ten review areas")
    if request["analysis_mode"] == "intervention_recheck":
        validate_locator(request.get("baseline_ref"), "baseline_ref", comparison=True)
        validate_locator(request.get("current_ref"), "current_ref", comparison=True)
        require(request["baseline_ref"] != request["current_ref"], "baseline_ref and current_ref must differ")
    else:
        require(request.get("baseline_ref") is None, "discovery cannot carry baseline_ref")
        require(request.get("current_ref") is None, "discovery cannot carry current_ref")
    require(set(request.get("focus_source_refs", [])) <= source_ids, "focus_source_refs contains unknown source")
    require(set(request.get("project_rule_source_refs", [])) <= source_ids, "project_rule_source_refs contains unknown source")
    _optional_jsonschema(request, INPUT_SCHEMA)


def derive_summary(package: dict[str, Any]) -> dict[str, Any]:
    severity = Counter(item.get("severity") for item in package.get("findings", []))
    coverage = Counter(item.get("status") for item in package.get("analysis_results", {}).get("coverage", []))
    return {
        "blocker": severity["blocker"], "major": severity["major"],
        "minor": severity["minor"], "note": severity["note"],
        "total_findings": sum(severity[item] for item in SEVERITIES),
        "promoted_evidence_count": len(package.get("evidence_items", [])),
        "coverage_status_counts": dict(sorted(coverage.items())),
        "summary_derivation": "programmatically_derived",
    }


def derive_privacy_summary(package: dict[str, Any]) -> dict[str, int]:
    counts = Counter(item.get("privacy_status") for item in package.get("run", {}).get("sources", []))
    return {key: counts[key] for key in ("safe", "restricted", "needs_review", "blocked")}


def normalize_package(request: dict[str, Any], package: dict[str, Any]) -> dict[str, Any]:
    package["run"]["combined_input_fingerprint"] = input_fingerprint(request)
    by_id: dict[str, dict[str, Any]] = {}
    for item in package.get("findings", []):
        item["finding_key"] = finding_key(package["run"].get("project_name", ""), item)
        by_id[item["finding_id"]] = item
    for evidence in package.get("evidence_items", []):
        finding = by_id.get(evidence.get("finding_ref"))
        if finding:
            evidence["finding_key"] = finding["finding_key"]
    package.setdefault("analysis_results", {})["summary"] = derive_summary(package)
    package.setdefault("data_quality", {})["privacy_summary"] = derive_privacy_summary(package)
    return package


def validate_run_and_binding(request: dict[str, Any], package: dict[str, Any]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    run_required = {
        "run_id", "artifact_type", "artifact_version", "producer_skill",
        "project_name", "generated_at", "source_mode", "analysis_mode", "status",
        "sources", "upstream_refs", "combined_input_fingerprint", "legacy_contract",
    }
    run_allowed = run_required | {"invocation_context", "analysis_purpose"}
    run = require_keys(package["run"], run_required, "run", run_allowed)
    require(str(run["run_id"]).startswith("eha_"), "run.run_id must start with eha_")
    require(run["artifact_type"] == "heuristic_evidence_package", "unsupported artifact_type")
    require(run["artifact_version"] == VERSION, f"artifact_version must be {VERSION}")
    require(run["producer_skill"] == "experience-heuristic-analysis", "unsupported producer_skill")
    require(run["source_mode"] == request["source_mode"], "run.source_mode does not match input")
    require(run["analysis_mode"] == request["analysis_mode"], "run.analysis_mode does not match input")
    if request.get("project_name"):
        require(run["project_name"] == request["project_name"], "run.project_name does not match input")
    require(run["status"] in {"completed", "completed_with_caveats", "not_evaluable"}, "unsupported run.status")
    require(run["legacy_contract"] is False, "legacy_contract must be false")
    require(run["combined_input_fingerprint"] == input_fingerprint(request), "combined_input_fingerprint does not match input request")
    output_ids = unique_ids(run["sources"], "source_id", "run.sources")
    input_by_id = {item["source_id"]: item for item in request["sources"]}
    require(output_ids == set(input_by_id), "run.sources must exactly match input sources")
    output_by_id: dict[str, dict[str, Any]] = {}
    source_allowed = {
        "source_id", "source_type", "source_ref", "acquisition", "upstream_locator",
        "status", "observable_capabilities", "limitations", "fingerprint",
        "sensitivity", "privacy_status", "redaction_applied", "disclosure_limitations",
    }
    for source in run["sources"]:
        source_id = source["source_id"]
        output_by_id[source_id] = source
        require_keys(source, source_allowed - {"upstream_locator"}, f"source {source_id}", source_allowed)
        original = input_by_id[source_id]
        for field in ("source_type", "source_ref", "acquisition"):
            require(source[field] == original[field], f"source {source_id} {field} does not match input")
        require(source["source_type"] in SOURCE_TYPES, f"source {source_id} has invalid source_type")
        require(source["status"] in {"loaded", "partially_loaded", "unreadable"}, f"source {source_id} has invalid status")
        capabilities = source["observable_capabilities"]
        require(isinstance(capabilities, list) and len(capabilities) == len(set(capabilities)), f"source {source_id} capabilities are invalid")
        require(set(capabilities) <= CAPABILITIES[source["source_type"]], f"source {source_id} claims unsupported observable capabilities")
        if source["status"] == "unreadable":
            require(not capabilities, f"unreadable source {source_id} cannot claim capabilities")
        if source["status"] in {"loaded", "partially_loaded"}:
            require(bool(source["fingerprint"]), f"readable source {source_id} requires a fingerprint")
        require(source["privacy_status"] in PRIVACY, f"source {source_id} has invalid privacy_status")
        require(source["sensitivity"] in {"public", "internal", "confidential", "restricted", "unknown"}, f"source {source_id} has invalid sensitivity")
        require(isinstance(source["redaction_applied"], bool), f"source {source_id}.redaction_applied must be boolean")
        require(is_safe_source_ref(source["source_ref"]), f"source {source_id} has unsafe source_ref")
        if source["acquisition"] == "explicit_upstream":
            require(source.get("upstream_locator") == original.get("upstream_locator"), f"source {source_id} upstream_locator mismatch")
            validate_locator(source.get("upstream_locator"), f"source {source_id}.upstream_locator")
        else:
            require(source.get("upstream_locator") is None, f"source {source_id} cannot carry upstream_locator")
    require(run["upstream_refs"] == request.get("explicit_upstream_refs", []), "run.upstream_refs does not match input")
    if run["source_mode"] == "independent":
        require(not run["upstream_refs"], "independent mode cannot claim upstream refs")
    return run, output_by_id


def validate_rules(package: dict[str, Any], sources: dict[str, dict[str, Any]]) -> set[str]:
    basis_ids = unique_ids(package["business_rule_basis"], "basis_id", "business_rule_basis")
    allowed_sources = {
        "user_confirmed", "formal_upstream", "knowledge_wiki",
        "explicit_project_rule", "provided_material", "evidence_inferred", "unknown",
    }
    for basis in package["business_rule_basis"]:
        basis_allowed = {
            "basis_id", "source_type", "source_ref", "source_version",
            "rule_type", "description", "applicable_scope", "confidence",
            "confirmation_status", "allowed_uses", "forbidden_uses",
        }
        require_keys(basis, basis_allowed, f"business rule {basis['basis_id']}", basis_allowed)
        require("source_detail" not in basis, f"business rule {basis['basis_id']} must not use source_detail")
        source_type = basis.get("source_type")
        confirmation = basis.get("confirmation_status")
        require(source_type in allowed_sources, f"business rule {basis['basis_id']} has invalid source_type")
        if source_type == "evidence_inferred":
            require(confirmation in {"candidate", "inferred"}, f"business rule {basis['basis_id']} cannot be confirmed from inferred evidence")
        if source_type == "unknown":
            require(confirmation == "unknown", f"business rule {basis['basis_id']} unknown source must remain unknown")
        if source_type == "provided_material":
            require(confirmation in {"confirmed_for_current_run", "candidate", "unknown"}, f"business rule {basis['basis_id']} provided material has invalid confirmation")
        if source_type in {"formal_upstream", "knowledge_wiki", "explicit_project_rule"} and confirmation == "confirmed":
            require(bool(basis.get("source_ref")) and bool(basis.get("source_version")) and bool(basis.get("applicable_scope")), f"business rule {basis['basis_id']} confirmed source requires ref, version, and scope")
        require(not (set(basis.get("allowed_uses", [])) & set(basis.get("forbidden_uses", []))), f"business rule {basis['basis_id']} has conflicting uses")
    contract = require_keys(package["analysis_contract"], {"analysis_scope", "focus_areas", "focus_source_refs", "applied_project_rule_refs", "rule_conflicts"}, "analysis_contract", {"analysis_scope", "focus_areas", "focus_source_refs", "applied_project_rule_refs", "rule_conflicts"})
    require(contract["analysis_scope"] == package["_request_scope"], "analysis_contract.analysis_scope does not match input")
    require(contract["focus_areas"] == package["_request_focus_areas"], "analysis_contract.focus_areas does not match input")
    require(set(contract["focus_source_refs"]) == set(package["_request_focus_source_refs"]), "analysis_contract.focus_source_refs does not match input")
    require(set(contract["applied_project_rule_refs"]) == set(package["_request_project_rule_source_refs"]), "analysis_contract.applied_project_rule_refs does not match input")
    require(set(contract["applied_project_rule_refs"]) <= set(sources), "applied_project_rule_refs contains unknown source")
    for ref in contract["applied_project_rule_refs"]:
        require(sources[ref]["source_type"] in {"design_guideline", "design_system", "business_rule"}, f"project rule source {ref} has unsupported type")
    conflict_allowed = {
        "conflict_id", "rule_refs", "target_finding_refs", "status",
        "applied_rule_ref", "excluded_rule_refs", "reason",
    }
    for conflict in contract["rule_conflicts"]:
        require_keys(
            conflict,
            {"conflict_id", "rule_refs", "target_finding_refs", "status", "reason"},
            f"rule conflict {conflict.get('conflict_id')}",
            conflict_allowed,
        )
    return basis_ids


def validate_requests(package: dict[str, Any]) -> tuple[set[str], set[str]]:
    request_ids = unique_ids(package["validation_requests"], "request_id", "validation_requests")
    finding_ids = {item.get("finding_id") for item in package["findings"]}
    blocking: set[str] = set()
    for request in package["validation_requests"]:
        request_allowed = {
            "request_id", "target_finding_refs", "gap_type", "required_input",
            "reason", "blocks_evidence_promotion", "recommended_owner_or_skill",
        }
        require_keys(
            request,
            request_allowed,
            f"validation request {request['request_id']}",
            request_allowed,
        )
        require(request.get("gap_type") in GAP_TYPES, f"validation request {request['request_id']} has invalid gap_type")
        refs = set(request.get("target_finding_refs", []))
        require(bool(refs) and refs <= finding_ids, f"validation request {request['request_id']} has invalid finding refs")
        if request.get("blocks_evidence_promotion") is True:
            blocking.update(refs)
    return request_ids, blocking


def validate_findings(
    package: dict[str, Any],
    sources: dict[str, dict[str, Any]],
    basis_ids: set[str],
    request_ids: set[str],
    blocking: set[str],
) -> dict[str, dict[str, Any]]:
    unique_ids(package["findings"], "finding_id", "findings")
    finding_keys = [item.get("finding_key") for item in package["findings"]]
    require(len(finding_keys) == len(set(finding_keys)), "findings contains duplicate finding_key")
    by_id: dict[str, dict[str, Any]] = {}
    allowed_finding_uses = EVIDENCE_ALLOWED_USES | {"human_review"}
    finding_required = {
        "finding_id", "finding_key", "category", "heuristic_lenses", "risk_tags",
        "page_or_flow", "location", "state", "source_refs", "observation",
        "risk_hypothesis", "severity", "confidence", "design_attention",
        "rule_source", "business_rule_basis_refs", "project_rule_refs",
        "heuristic_rule_ref", "privacy_status", "allowed_uses", "forbidden_uses",
        "evidence_status", "not_promoted_reasons", "validation_request_refs",
    }
    finding_allowed = finding_required | {"location_ref"}
    for finding in package["findings"]:
        finding_id = finding["finding_id"]
        require_keys(finding, finding_required, finding_id, finding_allowed)
        by_id[finding_id] = finding
        require(finding.get("finding_key") == finding_key(package["run"]["project_name"], finding), f"{finding_id} finding_key is not deterministic")
        require(finding.get("category") in CATEGORIES, f"{finding_id} has invalid category")
        require(finding.get("severity") in SEVERITIES, f"{finding_id} has invalid severity")
        require(finding.get("confidence") in {"high", "medium", "low"}, f"{finding_id} has invalid confidence")
        refs = set(finding.get("source_refs", []))
        require(bool(refs) and refs <= set(sources), f"{finding_id} references unknown source")
        usable = [sources[ref] for ref in refs if sources[ref]["source_type"] in EVIDENCE_SOURCE_TYPES and sources[ref]["status"] in {"loaded", "partially_loaded"} and sources[ref]["observable_capabilities"]]
        require(bool(usable), f"{finding_id} lacks an evidence-bearing observable source")
        require(all(sources[ref]["source_type"] != "description" for ref in refs) or bool(usable), f"{finding_id} cannot rely on description alone")
        require(set(finding.get("business_rule_basis_refs", [])) <= basis_ids, f"{finding_id} references unknown business rule")
        require(set(finding.get("project_rule_refs", [])) <= set(sources), f"{finding_id} references unknown project rule")
        require(set(finding.get("validation_request_refs", [])) <= request_ids, f"{finding_id} references unknown validation request")
        if finding.get("rule_source") in {"business_rule", "mixed"}:
            require(bool(finding.get("business_rule_basis_refs")), f"{finding_id} requires business_rule_basis_refs")
        if finding.get("rule_source") in {"project_rule", "mixed"}:
            require(bool(finding.get("project_rule_refs")), f"{finding_id} requires project_rule_refs")
        if finding.get("rule_source") == "general_heuristic":
            require(bool(finding.get("heuristic_rule_ref")), f"{finding_id} requires heuristic_rule_ref")
        require(finding.get("privacy_status") in PRIVACY, f"{finding_id} has invalid privacy_status")
        allowed = set(finding.get("allowed_uses", []))
        forbidden = set(finding.get("forbidden_uses", []))
        require(allowed <= allowed_finding_uses, f"{finding_id} has unsupported allowed uses")
        require(not (allowed & forbidden), f"{finding_id} has conflicting allowed and forbidden uses")
        status = finding.get("evidence_status")
        require(status in {"promoted", "not_promoted"}, f"{finding_id} has invalid evidence_status")
        if finding_id in blocking or finding.get("privacy_status") == "blocked":
            require(status == "not_promoted", f"{finding_id} is blocked and cannot be promoted")
        if status == "promoted":
            require(not finding.get("not_promoted_reasons"), f"promoted finding {finding_id} cannot have not_promoted_reasons")
        else:
            require(bool(finding.get("not_promoted_reasons")), f"not-promoted finding {finding_id} requires reasons")
    for conflict in package["analysis_contract"]["rule_conflicts"]:
        refs = set(conflict.get("target_finding_refs", []))
        require(refs <= set(by_id), f"rule conflict {conflict.get('conflict_id')} references unknown finding")
        if conflict.get("status") == "needs_confirmation":
            require(not conflict.get("applied_rule_ref"), f"unresolved rule conflict {conflict.get('conflict_id')} cannot select a rule")
            require(all(by_id[ref]["evidence_status"] == "not_promoted" for ref in refs), f"unresolved rule conflict {conflict.get('conflict_id')} must block promotion")
            require(any(item.get("gap_type") == "design_rule_conflict_confirmation" and refs & set(item.get("target_finding_refs", [])) for item in package["validation_requests"]), f"unresolved rule conflict {conflict.get('conflict_id')} requires a confirmation request")
    return by_id


def identifiable_group(value: Any) -> bool:
    return isinstance(value, dict) and any(str(item).strip().lower() not in {"", "unknown", "none", "null"} for item in value.values())


def validate_evidence(package: dict[str, Any], sources: dict[str, dict[str, Any]], basis_ids: set[str], findings: dict[str, dict[str, Any]]) -> set[str]:
    evidence_ids = unique_ids(package["evidence_items"], "evidence_id", "evidence_items")
    seen: set[str] = set()
    evidence_required = {
        "evidence_id", "finding_ref", "finding_key", "claim_type", "category",
        "observation", "risk_hypothesis", "design_attention", "source_refs",
        "confidence", "scene_descriptor", "business_rule_basis_refs",
        "project_rule_refs", "privacy_status", "can_be_used_as_strong_evidence",
        "manual_review_required", "causal_claim_allowed", "allowed_uses",
        "forbidden_uses", "lineage",
    }
    for evidence in package["evidence_items"]:
        evidence_id = evidence["evidence_id"]
        require_keys(evidence, evidence_required, evidence_id, evidence_required)
        ref = evidence.get("finding_ref")
        require(ref in findings and ref not in seen, f"{evidence_id} has invalid or duplicate finding_ref")
        seen.add(str(ref))
        finding = findings[str(ref)]
        require(finding["evidence_status"] == "promoted", f"{evidence_id} must reference a promoted finding")
        for field in ("finding_key", "category", "observation", "risk_hypothesis", "design_attention", "confidence", "privacy_status"):
            require(evidence.get(field) == finding.get(field), f"{evidence_id} {field} does not match its finding")
        for field in ("source_refs", "business_rule_basis_refs", "project_rule_refs", "allowed_uses", "forbidden_uses"):
            require(set(evidence.get(field, [])) == set(finding.get(field, [])), f"{evidence_id} {field} does not match its finding")
        require(evidence.get("claim_type") in EVIDENCE_CLAIMS, f"{evidence_id} has invalid claim_type")
        require(evidence.get("can_be_used_as_strong_evidence") is False, f"{evidence_id} cannot be strong evidence")
        require(evidence.get("manual_review_required") is True, f"{evidence_id} must require manual review")
        require(evidence.get("causal_claim_allowed") is False, f"{evidence_id} cannot allow causal claims")
        allowed = set(evidence.get("allowed_uses", []))
        forbidden = set(evidence.get("forbidden_uses", []))
        require(allowed <= EVIDENCE_ALLOWED_USES, f"{evidence_id} has unsupported allowed uses")
        require(REQUIRED_FORBIDDEN_USES <= forbidden, f"{evidence_id} is missing required forbidden uses")
        require(not (allowed & forbidden), f"{evidence_id} has conflicting uses")
        require(evidence["privacy_status"] != "blocked", f"{evidence_id} cannot promote blocked content")
        scene_fields = {"where", "what", "operation", "source_attribution", "evidence_form", "matching_policy"}
        scene = require_keys(evidence.get("scene_descriptor"), scene_fields, f"{evidence_id}.scene_descriptor", scene_fields)
        scene_refs = set(scene.get("source_attribution", {}).get("source_refs", []))
        require(bool(scene_refs) and scene_refs <= set(sources), f"{evidence_id} has invalid scene source refs")
        if scene.get("matching_policy") == "automatic_candidate":
            require(sum(identifiable_group(scene.get(group)) for group in ("where", "what", "operation")) >= 2, f"{evidence_id} needs two identifiable scene groups for automatic matching")
        lineage_fields = {"run_id", "source_refs", "finding_ref", "transformation_steps"}
        lineage = require_keys(evidence.get("lineage"), lineage_fields, f"{evidence_id}.lineage", lineage_fields)
        require(lineage["run_id"] == package["run"]["run_id"], f"{evidence_id} lineage run mismatch")
        require(lineage["finding_ref"] == ref, f"{evidence_id} lineage finding mismatch")
        require(set(lineage["source_refs"]) == set(evidence["source_refs"]), f"{evidence_id} lineage source mismatch")
    promoted = {item["finding_id"] for item in package["findings"] if item["evidence_status"] == "promoted"}
    require(seen == promoted, "promoted findings and evidence_items must match exactly")
    return evidence_ids


def validate_coverage_and_comparison(request: dict[str, Any], package: dict[str, Any]) -> None:
    results = require_keys(package["analysis_results"], {"coverage", "comparison", "summary"}, "analysis_results", {"coverage", "comparison", "summary"})
    coverage = results["coverage"]
    areas = [item.get("area") for item in coverage]
    require(len(areas) == len(set(areas)), "coverage contains duplicate area")
    require(set(areas) == set(request["analysis_scope"]["review_areas"]), "coverage must exactly match input review_areas")
    source_ids = {item["source_id"] for item in package["run"]["sources"]}
    statuses = {}
    for item in coverage:
        coverage_fields = {"area", "status", "source_refs", "limitations"}
        require_keys(item, coverage_fields, f"coverage {item.get('area')}", coverage_fields)
        require(item.get("area") in CATEGORIES, "coverage contains invalid area")
        require(item.get("status") in {"evaluated_with_findings", "evaluated_no_finding", "not_evaluable", "not_in_scope"}, f"coverage {item.get('area')} has invalid status")
        require(set(item.get("source_refs", [])) <= source_ids, f"coverage {item.get('area')} references unknown source")
        statuses[item["area"]] = item["status"]
    for category in {item["category"] for item in package["findings"]}:
        require(statuses.get(category) == "evaluated_with_findings", f"coverage for {category} must be evaluated_with_findings")
    comparison = results.get("comparison")
    if package["run"]["analysis_mode"] == "discovery":
        require(comparison is None, "discovery must not emit comparison")
    else:
        require(isinstance(comparison, dict), "intervention_recheck requires comparison")
        require(comparison.get("baseline_ref") == request["baseline_ref"], "comparison baseline_ref mismatch")
        require(comparison.get("current_ref") == request["current_ref"], "comparison current_ref mismatch")
        require(comparison.get("effect_claim") == "not_claimed", "comparison effect_claim must be not_claimed")
        resolved = set(comparison.get("resolved_finding_keys", []))
        persisted = set(comparison.get("persisted_finding_keys", []))
        new = set(comparison.get("new_finding_keys", []))
        require(not (resolved & persisted or resolved & new or persisted & new), "comparison finding key sets must be disjoint")
        current_keys = {item["finding_key"] for item in package["findings"]}
        require((persisted | new) <= current_keys, "persisted/new finding keys must exist in current findings")
        for change in comparison.get("severity_changes", []):
            require(change.get("finding_key") in persisted, "severity change must reference a persisted finding")
            require(change.get("before") in SEVERITIES and change.get("after") in SEVERITIES and change["before"] != change["after"], "severity change must contain different valid values")
        if comparison.get("scope_consistency") == "not_comparable":
            require(not resolved and not persisted and not new and not comparison.get("severity_changes"), "not-comparable comparison cannot classify finding changes")
    require(results["summary"] == derive_summary(package), "analysis_results.summary is not programmatically derived")


def validate_handoff(package: dict[str, Any], evidence_ids: set[str]) -> None:
    handoff_fields = {"input_gate_status", "analysis_status", "handoff_status", "evidence_refs", "blocked_reasons", "evidence_govern", "visualization", "allowed_uses", "forbidden_uses"}
    handoff = require_keys(package["handoff"], handoff_fields, "handoff", handoff_fields)
    require(set(handoff["evidence_refs"]) == evidence_ids, "handoff.evidence_refs must exactly match evidence_items")
    govern_fields = {"target_skill", "status", "payload_refs", "allowed_uses", "forbidden_uses"}
    govern = require_keys(handoff["evidence_govern"], govern_fields, "handoff.evidence_govern", govern_fields)
    require(govern["target_skill"] == "evidence-govern", "formal handoff target must be evidence-govern")
    expected_pointers = {f"#/evidence_items/{index}" for index in range(len(package["evidence_items"]))}
    require(set(govern["payload_refs"]) == expected_pointers, "formal handoff must point exactly to promoted evidence_items")
    if evidence_ids:
        require(handoff["handoff_status"] in {"ready", "ready_with_caveats"}, "package with evidence must be ready")
        require(govern["status"] == "ready", "evidence-govern status must be ready")
    else:
        require(handoff["handoff_status"] == "blocked", "package without evidence must block handoff")
        require(govern["status"] == "blocked" and not govern["payload_refs"], "blocked handoff must have empty payload_refs")
    visualization = handoff["visualization"]
    require(visualization.get("target_skill") == "data-visualization", "visualization handoff target must be data-visualization")
    require("visualization" in visualization.get("allowed_uses", []), "visualization handoff must allow visualization")
    require("recalculate_analysis" in visualization.get("forbidden_uses", []), "visualization handoff must forbid recalculation")


def validate_language(package: dict[str, Any]) -> None:
    def values(value: Any) -> Iterable[str]:
        if isinstance(value, str):
            yield value
        elif isinstance(value, list):
            for item in value:
                yield from values(item)
        elif isinstance(value, dict):
            for item in value.values():
                yield from values(item)
    for text in values(package["findings"] + package["evidence_items"] + [package["analysis_results"].get("comparison")]):
        for pattern in BANNED_PATTERNS:
            require(not pattern.search(text), f"prohibited claim language: {text}")


def validate_package(request: dict[str, Any], package: dict[str, Any]) -> None:
    validate_input(request)
    fields = frozenset(package)
    require(
        fields in {frozenset(TOP_LEVEL), frozenset(FINAL_TOP_LEVEL)},
        "package top-level fields must exactly match base or published contract",
    )
    final = fields == FINAL_TOP_LEVEL
    package["_request_scope"] = request["analysis_scope"]
    package["_request_focus_areas"] = request.get("focus_areas", [])
    package["_request_focus_source_refs"] = request.get("focus_source_refs", [])
    package["_request_project_rule_source_refs"] = request.get("project_rule_source_refs", [])
    try:
        run, sources = validate_run_and_binding(request, package)
        basis_ids = validate_rules(package, sources)
        request_ids, blocking = validate_requests(package)
        findings = validate_findings(package, sources, basis_ids, request_ids, blocking)
        evidence_ids = validate_evidence(package, sources, basis_ids, findings)
        validate_coverage_and_comparison(request, package)
        validate_handoff(package, evidence_ids)
        validate_language(package)
        data_quality_fields = {
            "status", "source_gaps", "quality_risks", "material_boundary",
            "privacy_summary",
        }
        require_keys(
            package["data_quality"],
            data_quality_fields,
            "data_quality",
            data_quality_fields,
        )
        require(package["data_quality"]["privacy_summary"] == derive_privacy_summary(package), "privacy_summary is not programmatically derived")
        if run["status"] == "not_evaluable":
            require(not package["findings"] and not package["evidence_items"], "not_evaluable run cannot emit findings or evidence")
            require(package["handoff"]["handoff_status"] == "blocked", "not_evaluable run must block handoff")
        if run["status"] == "completed":
            require(package["data_quality"]["status"] == "ready", "completed run requires ready data quality")
        if run["status"] == "completed_with_caveats":
            require(package["data_quality"]["status"] in {"ready_with_caveats", "partial"}, "completed_with_caveats requires caveated data quality")
    finally:
        package.pop("_request_scope", None)
        package.pop("_request_focus_areas", None)
        package.pop("_request_focus_source_refs", None)
        package.pop("_request_project_rule_source_refs", None)
    if final:
        _optional_jsonschema(package, OUTPUT_SCHEMA)


def atomic_write(value: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        try:
            Path(temp_name).unlink()
        except FileNotFoundError:
            pass


def render_report(package: dict[str, Any]) -> str:
    vocabulary: dict[str, Any] = {}
    try:
        vocabulary = load_json(VOCABULARY)
    except PackageError:
        vocabulary = {}
    heuristic_vocabulary = vocabulary.get("heuristic", {})
    severity_fallback = {
        "blocker": "主任务阻断风险", "major": "显著体验风险",
        "minor": "一般体验风险", "note": "观察项",
    }
    severity_labels = {
        code: heuristic_vocabulary.get(code, {}).get("label", fallback)
        for code, fallback in severity_fallback.items()
    }
    privacy_fallback = {
        "safe": "可按允许用途使用", "restricted": "内容受限",
        "needs_review": "需要隐私复核", "blocked": "禁止使用",
    }
    privacy_labels = {
        code: heuristic_vocabulary.get(code, {}).get("label", fallback)
        for code, fallback in privacy_fallback.items()
    }
    mode_labels = {
        "discovery": "现状风险检查",
        "intervention_recheck": "改版前后风险回检",
    }
    source_type_labels = {
        "screenshot": "截图", "prototype": "交互原型", "figma_export": "Figma 导出",
        "frontend_code": "前端代码", "dom": "页面结构", "a11y": "无障碍结构",
        "runtime": "运行结果", "flow": "流程材料", "blueprint": "体验蓝图",
        "brief": "需求说明", "stories": "用户故事", "design_guideline": "设计规范",
        "design_system": "设计系统", "business_rule": "业务规则",
        "description": "用户描述",
    }
    source_status_labels = {
        "loaded": "已读取", "partially_loaded": "已读取部分内容",
        "unreadable": "当前无法读取",
    }
    capability_labels = {
        "visible_layout": "可见布局", "visual_hierarchy": "视觉层级",
        "visible_copy": "可见文案", "static_state": "静态状态",
        "visible_accessibility_risk": "可见的无障碍风险",
        "responsive_snapshot": "当前视口表现", "interaction_flow": "交互路径",
        "state_transition": "状态变化", "responsive_spec": "响应式要求",
        "design_token_usage": "设计变量使用", "code_structure": "代码结构",
        "semantic_markup": "语义结构", "state_implementation": "状态实现",
        "dom_structure": "页面节点结构", "state_attributes": "状态属性",
        "accessibility_tree": "无障碍树", "accessible_name": "可访问名称",
        "semantic_role": "语义角色", "runtime_interaction": "实际交互",
        "feedback_behavior": "反馈表现", "error_state": "错误状态",
        "branching": "流程分支", "expected_behavior": "预期行为",
        "brief_consistency": "与需求的一致性", "design_rule": "设计规则",
        "business_rule": "业务规则", "reported_interface_description": "界面描述",
    }
    category_labels = {
        "flow-continuity": "流程连续性", "ia": "信息架构",
        "components": "组件一致性", "visual-hierarchy": "视觉层级",
        "edge-states": "边缘与异常状态", "copy": "文案",
        "responsive": "响应式", "feedback": "操作反馈",
        "accessibility": "基础可访问性", "brief-consistency": "与需求的一致性",
    }
    confidence_labels = {
        "high": "材料可直接支持这项观察",
        "medium": "材料基本支持，但仍有缺口",
        "low": "当前主要是待复核线索",
    }
    coverage_labels = {
        "evaluated_with_findings": "已检查，发现风险",
        "evaluated_no_finding": "已检查，现有材料下未发现明显风险",
        "not_evaluable": "材料不足，暂时无法判断",
        "not_in_scope": "本次未检查",
    }
    lines = [
        f"# {package['run']['project_name']} · 体验启发式分析",
        "",
        "## §0 核心判断",
        "",
        f"- 共识别 {len(package['findings'])} 个去重后的体验风险，其中 {len(package['evidence_items'])} 个具备进入证据治理候选的条件。",
        "- 风险等级只表示设计风险，不代表发生人数、业务价值或实施优先级。",
        "",
        "## §1 分析范围与材料",
        "",
        f"- 模式：{mode_labels[package['run']['analysis_mode']]}",
        f"- 范围：{'、'.join(package['analysis_contract']['analysis_scope']['included']) or '未具体命名'}",
    ]
    for source in package["run"]["sources"]:
        lines.append(
            f"- {source_type_labels[source['source_type']]}："
            f"{source_status_labels[source['status']]}；"
            f"隐私状态：{privacy_labels[source['privacy_status']]}；"
            "可检查："
            f"{'、'.join(capability_labels.get(value, value) for value in source['observable_capabilities']) or '无'}"
        )
    lines += ["", "## §2 材料质量与判断边界", "", f"- {package['data_quality']['material_boundary']}"]
    for limitation in package["limitations"]:
        lines.append(f"- {limitation}")
    lines += ["", "## §3 关键体验风险", ""]
    if not package["findings"]:
        lines.append("- 当前没有可报告的 Finding；这不代表完整审计通过。")
    for finding in package["findings"]:
        restricted = finding["privacy_status"] != "safe"
        observation = "内容受限，需完成隐私复核后查看。" if restricted else finding["observation"]
        risk = "暂不在可读报告中披露。" if restricted else finding["risk_hypothesis"]
        attention = "先完成隐私复核与必要脱敏。" if restricted else finding["design_attention"]
        lines += [
            f"### {finding['page_or_flow']} · {finding['location']}",
            "",
            f"- 风险等级：{severity_labels[finding['severity']]}",
            f"- 观察：{observation}",
            f"- 风险假设：{risk}",
            f"- 后续需要解决：{attention}",
            f"- 观察可靠性：{confidence_labels[finding['confidence']]}",
            "",
        ]
    lines += ["## §4 按检查领域整理", ""]
    for item in package["analysis_results"]["coverage"]:
        suffix = "；不代表完整审计通过" if item["status"] == "evaluated_no_finding" else ""
        lines.append(
            f"- {category_labels[item['area']]}："
            f"{coverage_labels[item['status']]}{suffix}"
        )
    lines += ["", "## §5 需要补证与人工复核", ""]
    if not package["validation_requests"]:
        lines.append("- 无新增补证请求。")
    for request in package["validation_requests"]:
        impact = "会阻止对应证据继续流转" if request["blocks_evidence_promotion"] else "不阻止当前观察进入人工复核"
        lines.append(f"- 还需要：{request['required_input']}。原因：{request['reason']}；{impact}。")
    lines += ["", "## §6 启发式回检差异", ""]
    comparison = package["analysis_results"].get("comparison")
    if comparison is None:
        lines.append("- 本次不是改版前后回检。")
    else:
        lines.append(f"- 可比性：{comparison['scope_consistency']}；仅描述风险变化，不声明方案效果。")
        lines.append(f"- 已消失 {len(comparison['resolved_finding_keys'])}，仍存在 {len(comparison['persisted_finding_keys'])}，新增 {len(comparison['new_finding_keys'])}。")
    lines += ["", "## §7 下游交接与禁止用途", ""]
    if package["handoff"]["handoff_status"] == "blocked":
        lines.append("- 当前没有通过门禁、可交给证据治理的启发式证据。")
    else:
        lines.append("- 已通过门禁的启发式证据可按明确引用交给证据治理；不会自动执行下一技能。")
    lines.append("- 不得据此声明用户真实行为、发生率、根因、业务规模、方案效果、投入或 ROI。")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("validate-input")
    p.add_argument("input", type=Path)
    for command in ("normalize", "validate", "write", "render", "publish"):
        p = sub.add_parser(command)
        p.add_argument("--input", required=True, type=Path)
        p.add_argument("package", type=Path)
        if command in {"normalize", "render"}:
            p.add_argument("--output", "-o", type=Path)
        if command == "write":
            p.add_argument("--output", type=Path, required=True)
            p.add_argument("--report-output", type=Path)
        if command == "publish":
            p.add_argument("--workspace-root", type=Path, default=WORKSPACE_ROOT)
            p.add_argument(
                "--registry",
                type=Path,
                default=WORKSPACE_ROOT / "shared-workflow/data-analysis/artifact-registry.json",
            )
    args = parser.parse_args(argv)
    try:
        if args.command == "validate-input":
            validate_input(load_json(args.input))
            print("OK: heuristic input 4.0.0 is valid")
            return 0
        request = load_json(args.input)
        package = load_json(args.package)
        if args.command == "normalize":
            normalize_package(request, package)
            validate_package(request, package)
            output = json.dumps(package, ensure_ascii=False, indent=2) + "\n"
            if args.output:
                atomic_write(output, args.output)
            else:
                print(output, end="")
        elif args.command == "validate":
            validate_package(request, package)
            print("OK: heuristic evidence package 4.0.0 is valid")
        elif args.command == "render":
            validate_package(request, package)
            output = render_report(package)
            if args.output:
                atomic_write(output, args.output)
            else:
                print(output, end="")
        elif args.command == "write":
            validate_package(request, package)
            require(package["run"]["status"] in {"completed", "completed_with_caveats"}, "only completed packages may be written")
            atomic_write(json.dumps(package, ensure_ascii=False, indent=2) + "\n", args.output)
            if args.report_output:
                atomic_write(render_report(package), args.report_output)
            print(f"OK: heuristic candidate written to {args.output}")
        elif args.command == "publish":
            require(
                package["run"]["status"] in {"completed", "completed_with_caveats"},
                "only completed packages may be published",
            )
            prepared = contract_runtime.apply_request_envelope(package, request)
            validate_package(request, prepared)
            with tempfile.TemporaryDirectory() as directory:
                temporary = Path(directory)
                candidate = temporary / "candidate.json"
                atomic_write(
                    json.dumps(prepared, ensure_ascii=False, indent=2) + "\n",
                    candidate,
                )
                deliverables = []
                for item in request["requested_deliverables"]:
                    bound = dict(item)
                    if item["format"] == "markdown":
                        report = temporary / "experience-heuristic-report.md"
                        atomic_write(render_report(prepared), report)
                        bound["source_path"] = str(report)
                    deliverables.append(bound)
                reference = contract_runtime.publish_result(
                    workspace_root=args.workspace_root,
                    registry_path=args.registry,
                    artifact_id="heuristic",
                    candidate_path=candidate,
                    purpose_key=request["analysis_purpose"]["purpose_key"],
                    purpose_label=request["analysis_purpose"]["purpose_label"],
                    deliverables=deliverables,
                )
            print(json.dumps(reference, ensure_ascii=False, indent=2))
    except PackageError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
