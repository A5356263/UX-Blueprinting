#!/usr/bin/env python3
"""Validate, safely write, render, and publish Data Visualization 5.0 packages."""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import math
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = SKILL_DIR.parents[2]
REGISTRY_PATH = PROJECT_ROOT / "shared-workflow/data-analysis/artifact-registry.json"
RUNTIME_DIR = PROJECT_ROOT / "shared-workflow/data-analysis/runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))
import contract_runtime
SOURCE_CONTRACTS_PATH = SKILL_DIR / "schemas/source-contracts.json"
VERSION = "5.0.0"
TOP_LEVEL = {
    "run",
    "data_quality",
    "limitations",
    "handoff",
    "analysis_results",
    "manual_review_requests",
    "quality",
    "write_safety",
}
FINAL_TOP_LEVEL = TOP_LEVEL | {"publication", "delivery"}
CHART_TYPES = {
    "metric_card",
    "data_table",
    "bar",
    "grouped_bar",
    "stacked_bar",
    "line",
    "distribution",
    "scatter",
    "funnel",
    "sankey",
    "relationship_flow",
    "mechanism_chain",
}
FORBIDDEN_USES = {
    "recalculate_analysis",
    "create_metric",
    "create_relationship",
    "upgrade_causality",
    "claim_validated_effect",
    "publish_knowledge",
    "auto_archive",
    "auto_trigger_downstream",
}


class ContractError(ValueError):
    """Raised when a package violates the 5.0 contract or a semantic gate."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"文件不存在：{path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(f"JSON 无法解析：{path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON 顶层必须是 object：{path}")
    return value


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _safe_relative_ref(value: str, label: str) -> None:
    if not value.strip():
        raise ContractError(f"{label} 不能为空")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or value.startswith("file://"):
        raise ContractError(f"{label} 必须是安全相对引用：{value}")
    if re.match(r"^[A-Za-z]:[\\/]", value):
        raise ContractError(f"{label} 不能包含绝对本机路径：{value}")


def _artifact_id_ref(value: str, label: str) -> None:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise ContractError(f"{label} 必须是 Artifact Registry ID：{value}")


def _source_contract_matrix() -> dict[tuple[str, str, str], dict[str, Any]]:
    payload = load_json(SOURCE_CONTRACTS_PATH)
    if payload.get("contract_version") != VERSION:
        raise ContractError("source-contracts.json 必须使用 5.0.0")
    matrix: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in payload.get("contracts", []):
        key = (
            item.get("producer_skill", ""),
            item.get("artifact_type", ""),
            item.get("artifact_version", ""),
        )
        if not all(key) or key in matrix:
            raise ContractError(f"来源契约键为空或重复：{key}")
        if item.get("handoff_path") not in item.get("allowed_paths", []):
            raise ContractError(f"{key[0]} handoff_path 未包含在 allowed_paths")
        matrix[key] = item
    return matrix


def _unique_ids(items: list[dict[str, Any]], key: str, label: str) -> set[str]:
    values = [str(item.get(key) or "") for item in items]
    if any(not value for value in values):
        raise ContractError(f"{label} 存在空 {key}")
    if len(values) != len(set(values)):
        raise ContractError(f"{label} 存在重复 {key}")
    return set(values)


def _registered_handoffs(payload: Any) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    if isinstance(payload, dict):
        if (
            payload.get("target_skill") == "data-visualization"
            and isinstance(payload.get("payload_refs"), list)
        ):
            values.append(payload)
        for item in payload.values():
            values.extend(_registered_handoffs(item))
    elif isinstance(payload, list):
        for item in payload:
            values.extend(_registered_handoffs(item))
    return values


def validate_input(request: dict[str, Any]) -> None:
    required = {
        "artifact_type",
        "schema_version",
        "source_mode",
        "project_name",
        "visualization_intent",
        "invocation_context",
        "analysis_purpose",
        "requested_analyses",
        "input_bindings",
        "requested_deliverables",
        "publication_policy",
        "retention_policy",
    }
    missing = required - set(request)
    if missing:
        raise ContractError(f"输入缺少字段：{sorted(missing)}")
    if request.get("artifact_type") != "visualization_package_input":
        raise ContractError("输入 artifact_type 必须是 visualization_package_input")
    if request.get("schema_version") != VERSION:
        raise ContractError("Data Visualization 输入只接受 5.0.0")
    mode = request.get("source_mode")
    if mode == "registered_upstream":
        sources = request.get("upstream_sources")
        if not isinstance(sources, list) or not sources:
            raise ContractError("registered_upstream 至少需要一个 upstream_sources")
        bundle = request.get("artifact_bundle")
        if not isinstance(bundle, dict):
            raise ContractError("registered_upstream 必须声明显式 artifact_bundle")
        if bundle.get("report_profile") not in {
            "objective_journey",
            "business_problem",
            "full_diagnostic",
        }:
            raise ContractError("artifact_bundle.report_profile 不受支持")
        expected_runs = sorted(
            str(item.get("artifact_instance_ref", {}).get("run_id") or "")
            for item in sources
        )
        if not all(expected_runs) or sorted(bundle.get("source_run_ids", [])) != expected_runs:
            raise ContractError("artifact_bundle.source_run_ids 必须与本次显式上游实例完全一致")
        if bundle.get("report_profile") == "objective_journey" and (
            len(sources) != 1
            or sources[0].get("producer_skill") != "objective-data-analysis"
        ):
            raise ContractError("objective_journey 报告包只能绑定一个 Objective 实例")
        matrix = _source_contract_matrix()
        registry = load_json(REGISTRY_PATH)
        for source in sources:
            key = (
                str(source.get("producer_skill")),
                str(source.get("artifact_type")),
                str(source.get("artifact_version")),
            )
            contract = matrix.get(key)
            if contract is None:
                raise ContractError(f"输入包含未登记或旧版本上游：{key}")
            requested = set(source.get("requested_paths", []))
            if not requested or not requested <= set(contract["allowed_paths"]):
                raise ContractError(f"{key[0]} requested_paths 越过来源契约")
            instance_ref = source.get("artifact_instance_ref")
            if not isinstance(instance_ref, dict):
                raise ContractError(f"{key[0]} 缺少 artifact_instance_ref")
            try:
                payload, _ = contract_runtime.validate_instance_ref(
                    instance_ref,
                    workspace_root=PROJECT_ROOT,
                    registry=registry,
                )
                contract_runtime.validate_handoff(
                    source.get("handoff", {}),
                    source_reference=instance_ref,
                    target_skill="data-visualization",
                    required_use=str(source.get("allowed_use") or ""),
                    source_payload=payload,
                    reviews=request.get("review_decisions", []),
                )
            except contract_runtime.ContractRuntimeError as exc:
                raise ContractError(str(exc)) from exc
            handoff = source.get("handoff", {})
            registered = _registered_handoffs(payload)
            if not any(item == handoff for item in registered):
                raise ContractError(
                    f"{key[0]} Handoff 不是来源 Artifact 中登记的 Data Visualization 交接"
                )
            if instance_ref.get("producer_skill") != key[0]:
                raise ContractError(f"{key[0]} Artifact Instance producer 不匹配")
            if set(source.get("requested_paths", [])) - set(
                source.get("handoff", {}).get("payload_refs", [])
            ):
                raise ContractError(f"{key[0]} requested_paths 未被 Handoff 释放")
    elif mode == "chart_ready":
        chart_ready = request.get("chart_ready_data")
        if not isinstance(chart_ready, dict) or not any(
            chart_ready.get(key) for key in ("metrics", "tables", "relationships")
        ):
            raise ContractError("chart_ready 需要已整理的指标、表格或关系")
        for metric in chart_ready.get("metrics", []):
            for key in ("metric_id", "label", "unit", "time_window", "epistemic_status"):
                if metric.get(key) in {None, ""}:
                    raise ContractError(f"chart-ready metric 缺少 {key}")
    elif mode == "visualization_brief":
        brief = request.get("visualization_brief")
        if not isinstance(brief, dict) or not brief.get("reader_goal"):
            raise ContractError("visualization_brief 需要 reader_goal")
    else:
        raise ContractError("source_mode 不受支持")
    intent = request.get("visualization_intent")
    if not isinstance(intent, dict) or not intent.get("reader_goal"):
        raise ContractError("visualization_intent.reader_goal 不能为空")


def _registered_source_key(source: dict[str, Any], *, request_side: bool) -> tuple[str, str, str, str]:
    reference = source.get("artifact_instance_ref", {}) if request_side else {}
    return (
        str(source.get("producer_skill") or ""),
        str(source.get("artifact_type") or ""),
        str(source.get("artifact_version") or ""),
        str(
            reference.get("run_id")
            if request_side
            else source.get("source_run_id")
            or ""
        ),
    )


def validate_request_package_alignment(
    package: dict[str, Any], request: dict[str, Any]
) -> None:
    """Ensure a candidate only consumes the exact registered runs and released payload."""
    if request.get("source_mode") != "registered_upstream":
        return
    requested_sources = {
        _registered_source_key(item, request_side=True): item
        for item in request.get("upstream_sources", [])
    }
    package_sources = package["analysis_results"]["visualization_package"].get(
        "source_contracts", []
    )
    package_keys = {
        _registered_source_key(item, request_side=False) for item in package_sources
    }
    if package_keys != set(requested_sources):
        raise ContractError("候选包来源与本次请求的正式 Artifact Instance 不一致")
    for source in package_sources:
        key = _registered_source_key(source, request_side=False)
        requested = requested_sources[key]
        requested_paths = set(requested.get("requested_paths", []))
        consumed_paths = set(source.get("consumed_paths", []))
        # The request carries the Handoff object as authorization metadata. Its
        # nested source pointer is inherited for traceability, not a payload read.
        producer_contract = _source_contract_matrix()[
            (key[0], key[1], key[2])
        ]
        payload_consumed = consumed_paths - {
            str(producer_contract["handoff_path"])
        }
        if not payload_consumed <= requested_paths:
            exceeded = sorted(payload_consumed - requested_paths)
            raise ContractError(f"{key[0]} 候选包消费了本次未申请的路径：{exceeded}")


def _load_objective_renderer() -> Any:
    path = SKILL_DIR / "scripts/render_objective_report.py"
    spec = importlib.util.spec_from_file_location(
        "data_visualization_objective_renderer", path
    )
    if spec is None or spec.loader is None:
        raise ContractError("无法加载 Objective 专用报告渲染器")
    module = importlib.util.module_from_spec(spec)
    scripts_dir = str(path.parent)
    sys.path.insert(0, scripts_dir)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(scripts_dir)
    return module


def _objective_payload_for_report(request: dict[str, Any]) -> dict[str, Any] | None:
    if request.get("source_mode") != "registered_upstream":
        return None
    if request.get("artifact_bundle", {}).get("report_profile") != "objective_journey":
        return None
    sources = request.get("upstream_sources", [])
    if len(sources) != 1 or sources[0].get("producer_skill") != "objective-data-analysis":
        return None
    required = {"#/analysis_results", "#/findings", "#/limitations"}
    requested = set(sources[0].get("requested_paths", []))
    if not required <= requested:
        raise ContractError(
            "Objective 完整报告必须获准消费 analysis_results、findings 和 limitations"
        )
    registry = load_json(REGISTRY_PATH)
    try:
        payload, _ = contract_runtime.validate_instance_ref(
            sources[0]["artifact_instance_ref"],
            workspace_root=PROJECT_ROOT,
            registry=registry,
        )
    except contract_runtime.ContractRuntimeError as exc:
        raise ContractError(str(exc)) from exc
    return payload


def _payloads_for_report(request: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Resolve only the exact Artifact Instances named by the explicit bundle."""
    if request.get("source_mode") != "registered_upstream":
        return {}
    registry = load_json(REGISTRY_PATH)
    payloads: dict[str, dict[str, Any]] = {}
    for source in request.get("upstream_sources", []):
        try:
            payload, _ = contract_runtime.validate_instance_ref(
                source["artifact_instance_ref"],
                workspace_root=PROJECT_ROOT,
                registry=registry,
            )
        except contract_runtime.ContractRuntimeError as exc:
            raise ContractError(str(exc)) from exc
        payloads[str(source["producer_skill"])] = payload
    return payloads


def build_bundle_package(request: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic candidate from the exact registered bundle."""
    validate_input(request)
    if request.get("source_mode") != "registered_upstream":
        raise ContractError("build-bundle 只用于 registered_upstream")
    matrix = _source_contract_matrix()
    payloads = _payloads_for_report(request)
    contracts = []
    limitations = []
    source_refs = []
    for index, source in enumerate(request["upstream_sources"], start=1):
        key = (
            str(source["producer_skill"]),
            str(source["artifact_type"]),
            str(source["artifact_version"]),
        )
        contract = matrix[key]
        reference = source["artifact_instance_ref"]
        source_id = str(reference["artifact_id"])
        source_refs.append(source_id)
        contracts.append({
            "source_id": source_id,
            "producer_skill": source["producer_skill"],
            "artifact_type": source["artifact_type"],
            "artifact_version": source["artifact_version"],
            "source_run_id": reference["run_id"],
            "artifact_ref": source_id,
            "allowed_paths": contract["allowed_paths"],
            "consumed_paths": sorted(
                set(source["requested_paths"]) | {str(contract["handoff_path"])}
            ),
            "sensitivity_status": "inherited",
            "privacy_gate_status": "safe",
            "contract_status": "valid",
        })
        for item in payloads[source["producer_skill"]].get("limitations", []):
            description = (
                str(item.get("description") or item)
                if isinstance(item, dict)
                else str(item)
            )
            limitations.append({
                "limitation_id": f"bundle-limit-{index}-{len(limitations) + 1}",
                "type": "source",
                "description": description,
                "affects_outputs": [],
            })
    bundle = request["artifact_bundle"]
    run_token = re.sub(r"[^A-Za-z0-9_-]+", "-", str(bundle["bundle_id"]))
    package = {
        "run": {
            "artifact_type": "visualization_package",
            "artifact_version": VERSION,
            "producer_skill": "data-visualization",
            "run_id": f"dv_bundle_{run_token}",
            "project_name": request["project_name"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_mode": "registered_upstream",
            "sources": source_refs,
            "write_status": "not_requested",
        },
        "data_quality": {
            "status": "ready_with_caveats" if limitations else "ready",
            "source_contract_valid": True,
            "semantic_gate_status": "degraded" if limitations else "passed",
            "notes": [
                f"显式报告包 {bundle['bundle_id']}；配置 {bundle['report_profile']}。",
                "只投影来源正式结果，不重新计算。",
            ],
        },
        "limitations": limitations,
        "handoff": {
            "input_gate_status": "ready_with_caveats" if limitations else "ready",
            "handoff_status": "terminal",
            "allowed_uses": ["presentation", "human_review", "offline_delivery"],
            "forbidden_uses": sorted(FORBIDDEN_USES),
            "blocked_reasons": [],
        },
        "analysis_results": {
            "visualization_package": {
                "source_contracts": contracts,
                "visual_outputs": [],
                "relationship_diagrams": [],
                "output_files": [],
                "recalculation_performed": False,
            }
        },
        "manual_review_requests": [],
        "quality": {
            "overall_status": "degraded" if limitations else "pass",
            "source_traceability": "pass",
            "semantic_fidelity": "pass",
            "label_clarity": "pass",
            "accessibility": "pass",
            "responsive": "pass",
            "sensitive_display": "pass",
        },
        "write_safety": {
            "output_root_checked": True,
            "relative_paths_only": True,
            "overwrite_policy": "immutable_result_with_purpose_pointer",
            "atomic_write": True,
            "sensitive_content_checked": True,
        },
    }
    validate_package(package)
    validate_request_package_alignment(package, request)
    return package


def _semantic_projection(package: dict[str, Any]) -> dict[str, Any]:
    """Return the deterministic, source-derived portion of a candidate package."""
    visualization = dict(
        package["analysis_results"]["visualization_package"]
    )
    visualization.pop("output_files", None)
    return {
        "data_quality": package.get("data_quality"),
        "limitations": package.get("limitations"),
        "handoff": package.get("handoff"),
        "visualization_package": visualization,
        "manual_review_requests": package.get("manual_review_requests"),
        "quality": package.get("quality"),
        "write_safety": package.get("write_safety"),
    }


def _authoritative_projection_for_request(request: dict[str, Any]) -> dict[str, Any]:
    """Rebuild the only projection allowed for a registered Artifact Bundle."""
    profile = request.get("artifact_bundle", {}).get("report_profile")
    if profile == "objective_journey":
        objective = _objective_payload_for_report(request)
        if objective is None:
            raise ContractError("objective_journey 缺少唯一 Objective 正式来源")
        source_ref = str(
            request["upstream_sources"][0]["artifact_instance_ref"]["artifact_id"]
        )
        return _load_objective_renderer().build_spec(objective, source_ref)
    return build_bundle_package(request)


def validate_authoritative_projection(
    package: dict[str, Any], request: dict[str, Any]
) -> None:
    """Reject registered candidates that drift from their explicit source Bundle."""
    if request.get("source_mode") != "registered_upstream":
        return
    authoritative = _authoritative_projection_for_request(request)
    if _semantic_projection(package) != _semantic_projection(authoritative):
        raise ContractError(
            "候选包语义投影与显式 Artifact Bundle 的权威确定性投影不一致；"
            "请从正式来源重新生成候选包"
        )


def _formal_output_files(
    package: dict[str, Any], request: dict[str, Any]
) -> list[dict[str, Any]]:
    registry = load_json(REGISTRY_PATH)
    entry = contract_runtime.registry_entry(registry, "visualization")
    planned = contract_runtime.result_delivery_paths(
        entry=entry,
        run=package["run"],
        purpose_key=request["analysis_purpose"]["purpose_key"],
        deliverables=request["requested_deliverables"],
    )
    source_run_ids = sorted(
        {
            item["source_run_id"]
            for item in package["analysis_results"]["visualization_package"][
                "source_contracts"
            ]
        }
    )
    profile = request.get("artifact_bundle", {}).get("report_profile")
    files = []
    for item in planned["files"]:
        fmt = item["format"]
        if fmt not in {"json", "html", "chart"}:
            continue
        files.append(
            {
                "path": item["path"],
                "format": "html" if fmt == "chart" else fmt,
                "purpose": (
                    "contract"
                    if fmt == "json"
                    else "objective_report"
                    if fmt in {"html", "chart"} and profile == "objective_journey"
                    else f"{profile}_report"
                    if fmt in {"html", "chart"} and profile
                    else "generic_visualization_page"
                ),
                "source_run_ids": source_run_ids,
                "write_status": "written",
            }
        )
    return files


def publish_package(
    package: dict[str, Any], request: dict[str, Any]
) -> dict[str, Any]:
    validate_input(request)
    validate_authoritative_projection(package, request)
    prepared = contract_runtime.apply_request_envelope(package, request)
    validate_request_package_alignment(prepared, request)
    prepared["analysis_results"]["visualization_package"][
        "output_files"
    ] = _formal_output_files(prepared, request)
    prepared["run"]["write_status"] = "written"
    validate_package(prepared)
    with tempfile.TemporaryDirectory() as directory:
        temporary = Path(directory)
        candidate = temporary / "candidate.json"
        report = temporary / "report.html"
        requested_formats = {
            item.get("format") for item in request["requested_deliverables"]
        }
        if requested_formats & {"html", "chart"}:
            objective_payload = _objective_payload_for_report(request)
            if objective_payload is not None:
                content = _load_objective_renderer().render(objective_payload)
            elif request.get("source_mode") == "registered_upstream":
                content = render_diagnostic_html(
                    prepared,
                    _payloads_for_report(request),
                    str(request.get("artifact_bundle", {}).get("report_profile")),
                )
            else:
                content = render_generic_html(prepared)
            atomic_write(report, content)
        atomic_write(candidate, json.dumps(prepared, ensure_ascii=False, indent=2) + "\n")
        deliverables = []
        for item in request["requested_deliverables"]:
            value = dict(item)
            if value["format"] in {"html", "chart"} and report.is_file():
                value["source_path"] = str(report)
            deliverables.append(value)
        return contract_runtime.publish_result(
            workspace_root=PROJECT_ROOT,
            registry_path=REGISTRY_PATH,
            artifact_id="visualization",
            candidate_path=candidate,
            purpose_key=request["analysis_purpose"]["purpose_key"],
            purpose_label=request["analysis_purpose"]["purpose_label"],
            deliverables=deliverables,
        )


def _validate_run(package: dict[str, Any]) -> None:
    run = package.get("run")
    if not isinstance(run, dict):
        raise ContractError("run 必须是 object")
    if run.get("artifact_type") != "visualization_package":
        raise ContractError("run.artifact_type 必须是 visualization_package")
    if run.get("artifact_version") != VERSION:
        raise ContractError("Data Visualization 只接受 5.0.0，不提供旧版本适配器")
    if run.get("producer_skill") != "data-visualization":
        raise ContractError("run.producer_skill 必须是 data-visualization")
    if not str(run.get("run_id", "")).startswith("dv_"):
        raise ContractError("run.run_id 必须以 dv_ 开头")
    if run.get("source_mode") not in {
        "registered_upstream",
        "chart_ready",
        "visualization_brief",
    }:
        raise ContractError("run.source_mode 不受支持")
    for source in run.get("sources", []):
        _safe_relative_ref(str(source), "run.sources")


def _validate_source_contracts(package: dict[str, Any]) -> dict[str, str]:
    mode = package["run"]["source_mode"]
    visualization = package["analysis_results"]["visualization_package"]
    sources = visualization.get("source_contracts")
    if not isinstance(sources, list):
        raise ContractError("source_contracts 必须是 array")
    if mode in {"registered_upstream", "chart_ready"} and not sources:
        raise ContractError(f"{mode} 至少需要一个来源契约")
    matrix = _source_contract_matrix()
    source_ids = _unique_ids(sources, "source_id", "source_contracts")
    source_producers: dict[str, str] = {}
    registered_count = 0
    user_count = 0
    for source in sources:
        producer = source.get("producer_skill")
        source_producers[source["source_id"]] = str(producer)
        allowed = set(source.get("allowed_paths", []))
        consumed = set(source.get("consumed_paths", []))
        if not consumed <= allowed:
            raise ContractError(f"{source['source_id']} 消费了 allowed_paths 之外的字段")
        if producer == "user":
            _safe_relative_ref(str(source.get("artifact_ref", "")), "source artifact_ref")
        else:
            _artifact_id_ref(str(source.get("artifact_ref", "")), "source artifact_ref")
        if not source.get("source_run_id"):
            raise ContractError(f"{source['source_id']} 缺少 source_run_id")
        if source.get("contract_status") != "valid":
            raise ContractError(f"{source['source_id']} 未通过来源契约门禁")
        if source.get("privacy_gate_status") not in {"safe", "approved"}:
            raise ContractError(f"{source['source_id']} 缺少可信隐私门禁或尚未获准展示")
        if producer == "user":
            user_count += 1
            if mode == "registered_upstream":
                raise ContractError("registered_upstream 不能把 user 数据伪装为登记产物")
            continue
        registered_count += 1
        key = (
            str(producer),
            str(source.get("artifact_type")),
            str(source.get("artifact_version")),
        )
        contract = matrix.get(key)
        if contract is None:
            raise ContractError(f"未登记或版本不匹配的上游来源：{key}")
        expected_allowed = set(contract.get("allowed_paths", []))
        if allowed != expected_allowed:
            raise ContractError(f"{source['source_id']} 的 allowed_paths 与权威矩阵不一致")
        if not set(contract.get("required_inherited_paths", [])) <= consumed:
            raise ContractError(f"{source['source_id']} 未继承必要限制或门禁字段")
    if mode == "registered_upstream" and registered_count == 0:
        raise ContractError("registered_upstream 必须包含正式登记的上游来源")
    if mode == "chart_ready" and user_count == 0:
        raise ContractError("chart_ready 必须标明 user 来源")
    return source_producers


def _validate_visual_outputs(
    package: dict[str, Any], source_producers: dict[str, str]
) -> None:
    mode = package["run"]["source_mode"]
    visualization = package["analysis_results"]["visualization_package"]
    outputs = visualization.get("visual_outputs")
    if not isinstance(outputs, list):
        raise ContractError("visual_outputs 必须是 array")
    _unique_ids(outputs, "visual_id", "visual_outputs")
    for output in outputs:
        chart_type = output.get("chart_type")
        status = output.get("render_status")
        if chart_type not in CHART_TYPES:
            raise ContractError(f"不支持的 chart_type：{chart_type}")
        if status in {"formal", "degraded"} and not output.get("chart_data"):
            raise ContractError(f"{output['visual_id']} 正式或降级渲染缺少 chart_data")
        if mode == "visualization_brief":
            if status not in {"spec_only", "blocked"}:
                raise ContractError("visualization_brief 只能输出 spec_only 或 blocked")
            if output.get("chart_data"):
                raise ContractError("visualization_brief 不得携带虚构 chart_data")
        elif status in {"formal", "degraded"}:
            _validate_chart_semantics(output)
        for ref in output.get("source_refs", []):
            source_id = str(ref).split("#", 1)[0]
            if source_id not in source_producers:
                raise ContractError(f"{output['visual_id']} 引用了未知来源：{ref}")
        accessibility = output.get("accessibility", {})
        if status in {"formal", "degraded"}:
            if accessibility.get("data_table_available") is not True:
                raise ContractError(f"{output['visual_id']} 缺少可访问数据表")
            if accessibility.get("color_independent") is not True:
                raise ContractError(f"{output['visual_id']} 不能只依赖颜色表达")


def _is_finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _chart_series(output: dict[str, Any]) -> list[dict[str, Any]]:
    series = output.get("chart_data", {}).get("series", [])
    return series if isinstance(series, list) else []


def _chart_points(output: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        point
        for series in _chart_series(output)
        for point in series.get("points", [])
        if isinstance(point, dict)
    ]


def _point_number(point: dict[str, Any]) -> float | None:
    for key in ("value", "y"):
        value = point.get(key)
        if _is_finite_number(value):
            return float(value)
    return None


def _point_category(point: dict[str, Any]) -> str:
    return str(point.get("category") or point.get("label") or "").strip()


def _has_nonempty_table(output: dict[str, Any]) -> bool:
    table = output.get("chart_data", {}).get("table")
    return bool(
        isinstance(table, dict)
        and isinstance(table.get("columns"), list)
        and table["columns"]
        and isinstance(table.get("rows"), list)
        and table["rows"]
    )


def _validate_ordered_x(points: list[dict[str, Any]], visual_id: str) -> None:
    values = [point.get("x") for point in points]
    if any(value in {None, ""} for value in values):
        raise ContractError(f"{visual_id} 缺少明确的 X/顺序字段")
    normalized = [str(value) for value in values]
    if len(normalized) != len(set(normalized)):
        raise ContractError(f"{visual_id} 的 X/顺序字段存在重复，无法确定展示顺序")
    if all(_is_finite_number(value) for value in values):
        numeric = [float(value) for value in values]
        if numeric != sorted(numeric) and numeric != sorted(numeric, reverse=True):
            raise ContractError(f"{visual_id} 的数值 X 必须按单调顺序提供")


def _validate_chart_semantics(output: dict[str, Any]) -> None:
    """Reject formal charts whose declared type cannot be rendered faithfully."""
    visual_id = str(output.get("visual_id") or "图表")
    chart_type = output.get("chart_type")
    status = output.get("render_status")
    if status == "degraded":
        if not _has_nonempty_table(output):
            raise ContractError(f"{visual_id} 降级交付必须提供非空数据表")
        if not output.get("caveats"):
            raise ContractError(f"{visual_id} 降级交付必须说明无法正式绘图的限制")
        return
    if status != "formal" or chart_type in {
        "sankey",
        "relationship_flow",
        "mechanism_chain",
    }:
        return

    series = _chart_series(output)
    points = _chart_points(output)
    encoding = output.get("encoding", {})
    objective_projection = str(output.get("data_ref") or "").startswith(
        "objective#/analysis_results/"
    )
    if chart_type == "data_table":
        if not _has_nonempty_table(output):
            raise ContractError(f"{visual_id} 数据表必须包含列和至少一行数据")
        return
    if not points:
        raise ContractError(f"{visual_id} 没有可绘制的数据点")

    if chart_type == "metric_card":
        if objective_projection:
            if any(_point_number(point) is None for point in points):
                raise ContractError(f"{visual_id} Objective 指标卡组存在非数值项")
            return
        if len(points) != 1 or _point_number(points[0]) is None:
            raise ContractError(f"{visual_id} 指标卡必须且只能包含一个明确数值")
        if not str(encoding.get("unit") or "").strip():
            raise ContractError(f"{visual_id} 指标卡缺少单位")
        if not str(encoding.get("time_window") or "").strip():
            raise ContractError(f"{visual_id} 指标卡缺少时间范围")
        return

    if chart_type == "bar":
        if len(series) != 1:
            raise ContractError(f"{visual_id} 普通柱状图只接受一个系列；多系列请使用 grouped_bar")
        if any(not _point_category(point) or _point_number(point) is None for point in points):
            raise ContractError(f"{visual_id} 柱状图每个数据点都必须包含类别和数值")
        if any((_point_number(point) or 0) < 0 for point in points):
            raise ContractError(
                f"{visual_id} 当前版本不支持用柱形表达正负方向；请显式使用数据表"
            )
        return

    if chart_type in {"grouped_bar", "stacked_bar"}:
        if len(series) < 2 or any(not item.get("points") for item in series):
            raise ContractError(f"{visual_id} 分组或堆叠柱状图至少需要两个非空系列")
        combinations: set[tuple[str, str]] = set()
        for item in series:
            series_key = str(item.get("series_id") or item.get("label") or "").strip()
            if not series_key:
                raise ContractError(f"{visual_id} 存在未命名系列")
            for point in item.get("points", []):
                category = _point_category(point)
                if not category or _point_number(point) is None:
                    raise ContractError(f"{visual_id} 每个系列点都必须包含类别和数值")
                if (_point_number(point) or 0) < 0:
                    raise ContractError(
                        f"{visual_id} 当前版本不支持用柱形表达正负方向；请显式使用数据表"
                    )
                key = (category, series_key)
                if key in combinations:
                    raise ContractError(f"{visual_id} 存在重复的类别—系列组合：{category} / {series_key}")
                combinations.add(key)
        if chart_type == "stacked_bar" and not str(encoding.get("unit") or "").strip():
            raise ContractError(f"{visual_id} 堆叠柱状图缺少统一单位")
        return

    if chart_type == "line":
        for item in series:
            item_points = item.get("points", [])
            if not item_points or any(_point_number(point) is None for point in item_points):
                raise ContractError(f"{visual_id} 折线图每个系列都必须包含数值点")
            _validate_ordered_x(item_points, f"{visual_id} / {item.get('label') or item.get('series_id')}")
        return

    if chart_type == "distribution":
        has_bins = all(
            _point_category(point)
            and _point_number(point) is not None
            and (_point_number(point) or 0) >= 0
            for point in points
        )
        if not has_bins:
            raise ContractError(
                f"{visual_id} 当前只有原始样本或无效分箱，缺少已登记的分箱与非负频数/比例；不能生成正式分布图"
            )
        return

    if chart_type == "scatter":
        if any(
            not _is_finite_number(point.get("x"))
            or not _is_finite_number(point.get("y"))
            for point in points
        ):
            raise ContractError(f"{visual_id} 散点图每个数据点都必须包含有限数值 X 和 Y")
        return

    if chart_type == "funnel":
        if len(series) != 1:
            raise ContractError(f"{visual_id} 漏斗只接受一个统一分母下的阶段系列")
        if any(not _point_category(point) or _point_number(point) is None for point in points):
            raise ContractError(f"{visual_id} 漏斗每个阶段都必须包含名称和数值")
        if any((_point_number(point) or 0) < 0 for point in points):
            raise ContractError(f"{visual_id} 漏斗阶段值不能为负数")
        if not objective_projection:
            _validate_ordered_x(points, visual_id)
        if not str(encoding.get("denominator") or "").strip():
            raise ContractError(f"{visual_id} 漏斗缺少统一分母口径")


def _validate_relationships(
    package: dict[str, Any], source_producers: dict[str, str]
) -> None:
    visualization = package["analysis_results"]["visualization_package"]
    diagrams = visualization.get("relationship_diagrams")
    if not isinstance(diagrams, list):
        raise ContractError("relationship_diagrams 必须是 array")
    _unique_ids(diagrams, "diagram_id", "relationship_diagrams")
    sankey_requested = any(
        item.get("chart_type") == "sankey"
        and item.get("render_status") in {"formal", "degraded"}
        for item in visualization.get("visual_outputs", [])
    )
    has_weighted_flow = False
    for diagram in diagrams:
        if diagram.get("producer") not in set(source_producers.values()):
            raise ContractError(
                f"{diagram['diagram_id']} 的 producer 未出现在来源契约中"
            )
        node_ids = _unique_ids(diagram.get("nodes", []), "node_id", diagram["diagram_id"])
        _unique_ids(diagram.get("edges", []), "edge_id", diagram["diagram_id"])
        for ref in diagram.get("source_refs", []):
            source_id = str(ref).split("#", 1)[0]
            if source_id not in source_producers:
                raise ContractError(f"{diagram['diagram_id']} 引用了未知来源：{ref}")
        all_weighted = bool(diagram.get("edges"))
        weight_units: set[str] = set()
        for edge in diagram.get("edges", []):
            if edge.get("source") not in node_ids or edge.get("target") not in node_ids:
                raise ContractError(f"{diagram['diagram_id']} 的边引用了未知节点")
            weight = edge.get("weight")
            unit = edge.get("weight_unit")
            if weight is None or not isinstance(weight, (int, float)) or weight < 0 or not unit:
                all_weighted = False
            else:
                weight_units.add(str(unit))
            if edge.get("relation_type") == "validated_effect" and edge.get("epistemic_status") != "validated":
                raise ContractError("validated_effect 只能来自 validated 上游关系")
        if all_weighted and len(weight_units) == 1:
            has_weighted_flow = True
    if sankey_requested and not has_weighted_flow:
        raise ContractError("正式 sankey 必须绑定统一单位的非负权重关系")


def _validate_files_and_quality(package: dict[str, Any]) -> None:
    visualization = package["analysis_results"]["visualization_package"]
    if visualization.get("recalculation_performed") is not False:
        raise ContractError("recalculation_performed 必须为 false")
    files = visualization.get("output_files")
    if not isinstance(files, list):
        raise ContractError("output_files 必须是 array")
    for output in files:
        _safe_relative_ref(str(output.get("path", "")), "output_files.path")
    handoff = package.get("handoff", {})
    if handoff.get("handoff_status") != "terminal":
        raise ContractError("Data Visualization 必须 terminal 交接")
    if not FORBIDDEN_USES <= set(handoff.get("forbidden_uses", [])):
        raise ContractError("handoff.forbidden_uses 缺少核心能力边界")
    blocking = [item for item in package.get("manual_review_requests", []) if item.get("blocking") is True]
    overall = package.get("quality", {}).get("overall_status")
    if blocking and overall != "blocked":
        raise ContractError("存在 blocking manual review 时 quality 必须为 blocked")
    if overall == "blocked" and package["run"].get("write_status") == "written":
        rendered = [
            item
            for item in visualization.get("visual_outputs", [])
            if item.get("render_status") in {"formal", "degraded"}
        ]
        if rendered:
            raise ContractError("quality=blocked 时不能声明正式图表已写出")
    safety = package.get("write_safety", {})
    if safety.get("relative_paths_only") is not True:
        raise ContractError("write_safety.relative_paths_only 必须为 true")


def validate_package(package: dict[str, Any]) -> None:
    if frozenset(package) not in {frozenset(TOP_LEVEL), frozenset(FINAL_TOP_LEVEL)}:
        raise ContractError(f"顶层契约不一致，应为：{sorted(TOP_LEVEL)}")
    _validate_run(package)
    source_producers = _validate_source_contracts(package)
    _validate_visual_outputs(package, source_producers)
    _validate_relationships(package, source_producers)
    _validate_files_and_quality(package)


def _esc(value: Any) -> str:
    return html.escape(str(value if value is not None else "—"))


def _table(columns: list[Any], rows: list[list[Any]]) -> str:
    header = "".join(f"<th>{_esc(item)}</th>" for item in columns)
    body = "".join(
        "<tr>" + "".join(f"<td>{_esc(item)}</td>" for item in row) + "</tr>"
        for row in rows
    )
    return (
        "<div class='table-wrap'><table><thead><tr>"
        f"{header}</tr></thead><tbody>{body}</tbody></table></div>"
    )


def _series_rows(output: dict[str, Any]) -> tuple[list[str], list[list[Any]]]:
    rows: list[list[Any]] = []
    for series in output.get("chart_data", {}).get("series", []):
        for point in series.get("points", []):
            rows.append(
                [
                    series.get("label"),
                    point.get("label"),
                    point.get("category"),
                    point.get("x"),
                    point.get("y"),
                    point.get("value"),
                    point.get("epistemic_status"),
                ]
            )
    return ["系列", "标签", "类别", "X", "Y", "值", "状态"], rows


def _numeric_points(output: dict[str, Any]) -> list[tuple[str, float]]:
    points: list[tuple[str, float]] = []
    for series in output.get("chart_data", {}).get("series", []):
        for point in series.get("points", []):
            value = point.get("value")
            if not isinstance(value, (int, float)):
                value = point.get("y")
            if isinstance(value, (int, float)) and math.isfinite(float(value)):
                points.append((str(point.get("label") or point.get("category") or ""), float(value)))
    return points


def _display_number(value: float) -> str:
    return f"{float(value):g}"


def _series_point_values(
    output: dict[str, Any],
) -> list[tuple[str, str, dict[str, Any], float]]:
    values: list[tuple[str, str, dict[str, Any], float]] = []
    for series in _chart_series(output):
        series_label = str(series.get("label") or series.get("series_id") or "")
        for point in series.get("points", []):
            value = _point_number(point)
            if value is not None:
                values.append((series_label, _point_category(point), point, value))
    return values


def _bar_visual(output: dict[str, Any]) -> str:
    points = _numeric_points(output)
    maximum = max((abs(value) for _, value in points), default=0) or 1
    rows = []
    for label, value in points:
        width = min(100, abs(value) / maximum * 100)
        rows.append(
            "<div class='bar-row'>"
            f"<span>{_esc(label)}</span><i><b style='width:{width:.2f}%'></b></i>"
            f"<strong>{_esc(value)}</strong></div>"
        )
    return "".join(rows)


def _metric_card_visual(output: dict[str, Any]) -> str:
    point = _chart_points(output)[0]
    value = _point_number(point)
    encoding = output.get("encoding", {})
    return (
        f"<div class='metric-card' role='group' aria-label='{_esc(output['accessibility']['summary'])}'>"
        f"<span class='metric-label'>{_esc(point.get('label') or output['title'])}</span>"
        f"<strong>{_esc(_display_number(value or 0))}</strong>"
        f"<span>{_esc(encoding.get('unit'))}</span>"
        f"<small>时间范围：{_esc(encoding.get('time_window'))} · "
        f"分母：{_esc(encoding.get('denominator') or '未提供')} · "
        f"状态：{_esc(point.get('epistemic_status'))}</small></div>"
    )


def _grouped_bar_visual(output: dict[str, Any]) -> str:
    values = _series_point_values(output)
    maximum = max((abs(value) for _, _, _, value in values), default=0) or 1
    categories: list[str] = []
    for _, category, _, _ in values:
        if category not in categories:
            categories.append(category)
    groups = []
    for category in categories:
        bars = []
        for series_label, point_category, _, value in values:
            if point_category != category:
                continue
            width = min(100, abs(value) / maximum * 100)
            bars.append(
                "<div class='grouped-series'>"
                f"<span>{_esc(series_label)}</span><i><b style='width:{width:.2f}%'></b></i>"
                f"<strong>{_esc(_display_number(value))}</strong></div>"
            )
        groups.append(
            f"<section class='grouped-category'><h3>{_esc(category)}</h3>{''.join(bars)}</section>"
        )
    legend = "".join(
        f"<span>{_esc(item.get('label') or item.get('series_id'))}</span>"
        for item in _chart_series(output)
    )
    series_names = "、".join(
        str(item.get("label") or item.get("series_id")) for item in _chart_series(output)
    )
    aria = f"{output['accessibility']['summary']}；系列：{series_names}"
    return (
        f"<div class='chart-legend' aria-label='系列'>{legend}</div>"
        f"<div class='grouped-chart' role='img' aria-label='{_esc(aria)}'>{''.join(groups)}</div>"
    )


def _stacked_bar_visual(output: dict[str, Any]) -> str:
    values = _series_point_values(output)
    categories: list[str] = []
    for _, category, _, _ in values:
        if category not in categories:
            categories.append(category)
    rows = []
    for category in categories:
        items = [item for item in values if item[1] == category]
        total = sum(abs(item[3]) for item in items) or 1
        segments = "".join(
            "<span class='stacked-segment' "
            f"style='width:{abs(value) / total * 100:.2f}%' "
            f"title='{_esc(series_label)}: {_esc(_display_number(value))}'>"
            f"<b>{_esc(series_label)}</b></span>"
            for series_label, _, _, value in items
        )
        details = "；".join(
            f"{series_label} {_display_number(value)}"
            for series_label, _, _, value in items
        )
        rows.append(
            "<div class='stacked-row'>"
            f"<span>{_esc(category)}</span><div class='stacked-track'>{segments}</div>"
            f"<strong>{_esc(details)}</strong></div>"
        )
    series_names = "、".join(
        str(item.get("label") or item.get("series_id")) for item in _chart_series(output)
    )
    aria = f"{output['accessibility']['summary']}；系列：{series_names}"
    return f"<div class='stacked-chart' role='img' aria-label='{_esc(aria)}'>{''.join(rows)}</div>"


def _line_visual(output: dict[str, Any]) -> str:
    series_values = []
    for series in _chart_series(output):
        values = [
            (_point_category(point), _point_number(point), point.get("x"))
            for point in series.get("points", [])
        ]
        if values:
            series_values.append((str(series.get("label") or series.get("series_id")), values))
    if not series_values:
        return ""
    all_points = [point for _, points in series_values for point in points]
    values = [float(value) for _, value, _ in all_points if value is not None]
    minimum, maximum = min(values), max(values)
    span = maximum - minimum or 1
    width, height = 760, 220
    x_values = [point[2] for point in all_points]
    numeric_x = all(_is_finite_number(value) for value in x_values)
    if numeric_x:
        x_numbers = [float(value) for value in x_values]
        x_minimum, x_maximum = min(x_numbers), max(x_numbers)
        x_span = x_maximum - x_minimum or 1
    paths = []
    for series_index, (series_label, points) in enumerate(series_values):
        coords = []
        for index, (_, value, x_value) in enumerate(points):
            x = (
                30 + (float(x_value) - x_minimum) * (width - 60) / x_span
                if numeric_x
                else 30 + index * (width - 60) / max(len(points) - 1, 1)
            )
            y = 20 + (maximum - float(value)) * (height - 50) / span
            coords.append((x, y))
        polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
        circles = "".join(
            f"<circle cx='{x:.1f}' cy='{y:.1f}' r='4'><title>{_esc(series_label)} / "
            f"{_esc(points[index][0])}: X={_esc(points[index][2])}, "
            f"Y={_esc(points[index][1])}</title></circle>"
            for index, (x, y) in enumerate(coords)
        )
        paths.append(
            f"<g class='line-series line-series-{series_index + 1}'>"
            f"<polyline points='{polyline}'></polyline>{circles}</g>"
        )
    return (
        f"<svg class='series-svg' viewBox='0 0 {width} {height}' role='img' "
        f"aria-label='{_esc(output['accessibility']['summary'])}'>"
        f"{''.join(paths)}</svg>"
    )


def _distribution_visual(output: dict[str, Any]) -> str:
    values = _series_point_values(output)
    maximum = max((abs(value) for _, _, _, value in values), default=0) or 1
    bins = "".join(
        "<div class='distribution-bin'>"
        f"<i><b style='height:{abs(value) / maximum * 100:.2f}%'></b></i>"
        f"<span>{_esc(category)}</span><strong>{_esc(_display_number(value))}</strong></div>"
        for _, category, _, value in values
    )
    return (
        f"<div class='distribution-chart' role='img' "
        f"aria-label='{_esc(output['accessibility']['summary'])}'>{bins}</div>"
    )


def _scatter_visual(output: dict[str, Any]) -> str:
    points = _chart_points(output)
    x_values = [float(point["x"]) for point in points]
    y_values = [float(point["y"]) for point in points]
    x_minimum, x_maximum = min(x_values), max(x_values)
    y_minimum, y_maximum = min(y_values), max(y_values)
    x_span = x_maximum - x_minimum or 1
    y_span = y_maximum - y_minimum or 1
    encoding = output.get("encoding", {})
    circles = []
    for point, x_value, y_value in zip(points, x_values, y_values):
        cx = 38 + (x_value - x_minimum) * 684 / x_span
        cy = 20 + (y_maximum - y_value) * 174 / y_span
        circles.append(
            "<circle class='scatter-point' "
            f"cx='{cx:.1f}' cy='{cy:.1f}' r='6' "
            f"data-x='{_display_number(x_value)}' data-y='{_display_number(y_value)}'>"
            f"<title>{_esc(_point_category(point))}: X={_esc(_display_number(x_value))}, "
            f"Y={_esc(_display_number(y_value))}</title></circle>"
        )
    return (
        "<svg class='scatter-svg' viewBox='0 0 760 230' role='img' "
        f"aria-label='{_esc(output['accessibility']['summary'])}'>"
        "<line class='axis' x1='38' y1='194' x2='722' y2='194'></line>"
        "<line class='axis' x1='38' y1='20' x2='38' y2='194'></line>"
        f"<text class='axis-label' x='380' y='222' text-anchor='middle'>{_esc(encoding.get('x'))}</text>"
        f"<text class='axis-label' x='12' y='110' text-anchor='middle' transform='rotate(-90 12 110)'>{_esc(encoding.get('y'))}</text>"
        f"<text class='axis-tick' x='38' y='211'>{_esc(_display_number(x_minimum))}</text>"
        f"<text class='axis-tick' x='722' y='211' text-anchor='end'>{_esc(_display_number(x_maximum))}</text>"
        f"<text class='axis-tick' x='31' y='194' text-anchor='end'>{_esc(_display_number(y_minimum))}</text>"
        f"<text class='axis-tick' x='31' y='26' text-anchor='end'>{_esc(_display_number(y_maximum))}</text>"
        f"{''.join(circles)}</svg>"
    )


def _funnel_visual(output: dict[str, Any]) -> str:
    values = _series_point_values(output)
    maximum = max((abs(value) for _, _, _, value in values), default=0) or 1
    stages = []
    for _, category, point, value in values:
        width = max(8, abs(value) / maximum * 100)
        stages.append(
            "<div class='funnel-stage'>"
            f"<span>{_esc(category)}</span><i style='width:{width:.2f}%'>"
            f"<b>{_esc(_display_number(value))}</b></i>"
            f"<small>顺序：{_esc(point.get('x'))}</small></div>"
        )
    denominator = output.get("encoding", {}).get("denominator")
    return (
        f"<p class='funnel-denominator'>统一分母：{_esc(denominator)}</p>"
        f"<div class='funnel-chart' role='img' aria-label='{_esc(output['accessibility']['summary'])}'>"
        f"{''.join(stages)}</div>"
    )


def _render_visual(output: dict[str, Any]) -> str:
    status = output["render_status"]
    caveats = "".join(f"<li>{_esc(item)}</li>" for item in output.get("caveats", []))
    if status in {"spec_only", "blocked"}:
        content = "<p class='spec'>当前只提供可视化规格，不生成正式数值图。</p>"
        table_html = ""
    elif status == "degraded":
        content = "<p class='spec'>当前数据语义不足，按已声明限制仅交付数据表，不绘制可能误导的图形。</p>"
        table_data = output.get("chart_data", {}).get("table")
        table_html = _table(table_data.get("columns", []), table_data.get("rows", []))
    else:
        chart_type = output["chart_type"]
        if chart_type == "metric_card":
            content = _metric_card_visual(output)
        elif chart_type == "bar":
            content = (
                f"<div class='bars' role='img' aria-label='{_esc(output['accessibility']['summary'])}'>"
                f"{_bar_visual(output)}</div>"
            )
        elif chart_type == "grouped_bar":
            content = _grouped_bar_visual(output)
        elif chart_type == "stacked_bar":
            content = _stacked_bar_visual(output)
        elif chart_type == "line":
            content = f"<div class='chart-scroll'>{_line_visual(output)}</div>"
        elif chart_type == "distribution":
            content = f"<div class='chart-scroll'>{_distribution_visual(output)}</div>"
        elif chart_type == "scatter":
            content = f"<div class='chart-scroll'>{_scatter_visual(output)}</div>"
        elif chart_type == "funnel":
            content = _funnel_visual(output)
        elif chart_type == "data_table":
            content = ""
        else:
            content = "<p class='spec'>关系图见下方对应关系区。</p>"
        table_data = output.get("chart_data", {}).get("table")
        if table_data:
            table_html = _table(table_data.get("columns", []), table_data.get("rows", []))
        else:
            columns, rows = _series_rows(output)
            table_html = _table(columns, rows) if rows else ""
    return (
        "<article class='panel'>"
        f"<div class='eyebrow'>{_esc(output['chart_type'])} · {_esc(status)} · {_esc(output['epistemic_status'])}</div>"
        f"<h2>{_esc(output['title'])}</h2><p>{_esc(output['rationale'])}</p>{content}{table_html}"
        f"<ul class='caveats'>{caveats}</ul></article>"
    )


def _render_diagram(diagram: dict[str, Any]) -> str:
    nodes = diagram.get("nodes", [])
    node_by_id = {node["node_id"]: node for node in nodes}
    positions: dict[str, tuple[float, float]] = {}
    width, height = 900, max(220, 100 + 80 * math.ceil(max(len(nodes), 1) / 5))
    for index, node in enumerate(nodes):
        positions[node["node_id"]] = (70 + (index % 5) * 175, 60 + (index // 5) * 90)
    edges = []
    for edge in diagram.get("edges", []):
        start = positions.get(edge["source"])
        end = positions.get(edge["target"])
        if not start or not end:
            continue
        weighted = _is_finite_number(edge.get("weight")) and bool(edge.get("weight_unit"))
        stroke = max(2, min(16, math.sqrt(float(edge.get("weight") or 1)))) if weighted else 2
        dash = "" if weighted else " stroke-dasharray='6 4'"
        scale_label = (
            f"{_display_number(float(edge['weight']))} {edge['weight_unit']}"
            if weighted
            else "未提供可比较规模"
        )
        edges.append(
            f"<line x1='{start[0]}' y1='{start[1]}' x2='{end[0]}' y2='{end[1]}' "
            f"stroke-width='{stroke:.1f}'{dash}><title>{_esc(edge['relation_type'])}</title></line>"
            f"<desc>{_esc(scale_label)}</desc>"
        )
    node_svg = []
    for node in nodes:
        x, y = positions[node["node_id"]]
        node_svg.append(
            f"<rect x='{x - 60}' y='{y - 22}' width='120' height='44' rx='9'></rect>"
            f"<text x='{x}' y='{y + 4}' text-anchor='middle'>{_esc(node['label'][:18])}</text>"
        )
    caveats = "".join(f"<li>{_esc(item)}</li>" for item in diagram.get("caveats", []))
    relation_types = sorted(
        {str(edge.get("relation_type") or "未标明") for edge in diagram.get("edges", [])}
    )
    comparable = bool(diagram.get("edges")) and all(
        _is_finite_number(edge.get("weight")) and edge.get("weight_unit")
        for edge in diagram.get("edges", [])
    )
    aria_summary = (
        f"{diagram['title']}，{len(nodes)} 个节点，{len(diagram.get('edges', []))} 条关系，"
        f"关系类型：{'、'.join(relation_types) or '未提供'}；"
        + ("权重具有可比较规模。" if comparable else "部分或全部关系未提供可比较规模。")
    )
    node_rows = [
        [
            node.get("label"),
            node.get("node_type"),
            node.get("epistemic_status"),
            "；".join(str(ref) for ref in node.get("source_refs", [])) or "—",
        ]
        for node in nodes
    ]
    edge_rows = []
    for edge in diagram.get("edges", []):
        weighted = _is_finite_number(edge.get("weight")) and bool(edge.get("weight_unit"))
        edge_rows.append([
            node_by_id.get(edge.get("source"), {}).get("label", edge.get("source")),
            node_by_id.get(edge.get("target"), {}).get("label", edge.get("target")),
            edge.get("relation_type"),
            _display_number(float(edge["weight"])) if weighted else "未提供可比较规模",
            edge.get("weight_unit") if weighted else "不适用",
            edge.get("epistemic_status"),
            "；".join(str(ref) for ref in edge.get("source_refs", [])) or "—",
            "；".join(str(item) for item in edge.get("caveats", [])) or "—",
        ])
    relation_tables = (
        "<details class='relationship-data' open><summary>关系数据表</summary>"
        "<h3>节点</h3>"
        + _table(["节点标签", "节点类型", "状态", "来源引用"], node_rows)
        + "<h3>关系</h3>"
        + _table(
            ["起点", "终点", "关系类型", "权重", "权重单位", "状态", "来源引用", "限制"],
            edge_rows,
        )
        + "</details>"
    )
    return (
        "<article class='panel'><div class='eyebrow'>"
        f"{_esc(diagram['producer'])} · {_esc(diagram['relation_type'])} · {_esc(diagram['confidence'])}</div>"
        f"<h2>{_esc(diagram['title'])}</h2><div class='diagram-scroll'>"
        f"<svg class='diagram' viewBox='0 0 {width} {height}' role='img' aria-label='{_esc(aria_summary)}'>"
        f"{''.join(edges)}{''.join(node_svg)}</svg></div>{relation_tables}"
        f"<ul class='caveats'>{caveats}</ul></article>"
    )


def _human_value(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "是" if value else "否"
    if isinstance(value, float):
        return f"{value * 100:.1f}%" if 0 <= value <= 1 else f"{value:.2f}"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _statement_list(payload: dict[str, Any], limit: int = 8) -> list[str]:
    values: list[str] = []
    for item in payload.get("findings", []):
        if isinstance(item, dict):
            statement = item.get("statement") or item.get("summary")
            if statement:
                values.append(str(statement))
    summary = payload.get("analysis_summary")
    if isinstance(summary, str):
        values.append(summary)
    elif isinstance(summary, dict):
        for key in ("summary", "headline", "conclusion"):
            if summary.get(key):
                values.append(str(summary[key]))
    return values[:limit]


def _business_section(
    title: str,
    payload: dict[str, Any],
    *,
    fields: list[tuple[str, str]],
    collections: list[tuple[str, str, tuple[str, ...]]],
) -> str:
    statements = _statement_list(payload)
    parts = [
        "<div class='conclusions'><strong>关键结论</strong><ul>"
        + (
            "".join(f"<li>{_esc(item)}</li>" for item in statements)
            if statements
            else "<li>上游没有发布独立结论句；以下仅展示其正式结构化结果。</li>"
        )
        + "</ul></div>"
    ]
    rows = [
        [label, _human_value(payload.get(key))]
        for key, label in fields
        if payload.get(key) not in (None, "", [], {})
    ]
    if rows:
        parts.append(_table(["内容", "正式结果"], rows))
    for key, label, item_fields in collections:
        items = payload.get(key, [])
        if not isinstance(items, list) or not items:
            continue
        collection_rows = []
        for item in items[:20]:
            if isinstance(item, dict):
                collection_rows.append(
                    [_human_value(item.get(field)) for field in item_fields]
                )
            else:
                collection_rows.append([_human_value(item)])
        parts.append(f"<h3>{_esc(label)}</h3>")
        parts.append(_table(list(item_fields), collection_rows))
    return f"<section class='panel business-section'><h2>{_esc(title)}</h2>{''.join(parts)}</section>"


def _objective_diagnostic_section(payload: dict[str, Any]) -> str:
    results = payload.get("analysis_results", {})
    metrics = results.get("metrics", {})
    journey = results.get("journey", {})
    cards = [
        ("任务数", metrics.get("task_instance_count")),
        ("完成率", metrics.get("completion_rate")),
        ("一次完成率", metrics.get("one_time_completion_rate")),
        ("报错任务率", metrics.get("error_task_rate")),
    ]
    card_html = "".join(
        f"<div class='metric'><span>{_esc(label)}</span><strong>{_esc(_human_value(value))}</strong></div>"
        for label, value in cards
        if value is not None
    )
    path_rows = [
        [
            " → ".join(str(node) for node in item.get("path", [])),
            item.get("task_count"),
            _human_value(item.get("share")),
            "/".join(
                _human_value(item.get("duration_seconds", {}).get(key))
                for key in ("p50", "p70", "p90")
            ),
        ]
        for item in journey.get("top_path_patterns", [])[:10]
    ]
    node_rows = [
        [
            item.get("label") or item.get("node_id"),
            item.get("task_count"),
            item.get("event_count"),
            item.get("error_task_count"),
            _human_value(item.get("error_task_share")),
        ]
        for item in journey.get("stage_nodes", [])[:20]
    ]
    statements = _statement_list(payload)
    return (
        "<section class='panel business-section'><h2>客观行为与旅程：发生了什么</h2>"
        "<div class='conclusions'><strong>客观分析结论</strong><ul>"
        + (
            "".join(f"<li>{_esc(item)}</li>" for item in statements)
            if statements
            else "<li>上游未发布独立结论句；请结合路径与节点事实阅读。</li>"
        )
        + "</ul></div><div class='metric-grid'>"
        + card_html
        + "</div>"
        + (
            "<h3>高频真实路径</h3>"
            + _table(["路径", "任务数", "占比", "P50/P70/P90 秒"], path_rows)
            if path_rows
            else ""
        )
        + (
            "<h3>节点覆盖、报错与退出线索</h3>"
            + _table(["节点", "任务数", "事件数", "报错任务", "报错任务占比"], node_rows)
            if node_rows
            else ""
        )
        + "<p class='spec'>完整交互式路径筛选、高亮、理想路径对比和连线详情由 objective_journey 报告配置提供；本综合报告不重算路径。</p></section>"
    )


def _nps_diagnostic_section(summary: dict[str, Any]) -> str:
    if not isinstance(summary, dict) or summary.get("status") == "not_evaluable":
        return ""
    facts = [
        item
        for item in [summary.get("overall"), *summary.get("slices", [])]
        if isinstance(item, dict)
    ]
    rows = []
    for item in facts:
        scope = item.get("measurement_scope", {})
        dimensions = scope.get("dimensions", {})
        rate = item.get("response_rate", {})
        rows.append([
            "总体" if not dimensions else " / ".join(
                f"{key}={value}" for key, value in sorted(dimensions.items())
            ),
            item.get("response_count"),
            item.get("promoter_count"),
            item.get("passive_count"),
            item.get("detractor_count"),
            item.get("nps"),
            _human_value(rate.get("value"))
            if rate.get("status") == "available"
            else "未提供邀请分母",
        ])
    if not rows:
        return ""
    return (
        "<section class='panel business-section'><h2>NPS：不同板块和企业群体的体验变化</h2>"
        + _table(
            ["范围", "答卷", "推荐者", "中立者", "贬损者", "NPS", "响应率"],
            rows,
        )
        + "<p class='spec'>NPS 保持 survey_response 粒度；本报告不把答卷比例换算为任务或企业发生率。</p></section>"
    )


def render_diagnostic_html(
    package: dict[str, Any],
    payloads: dict[str, dict[str, Any]],
    profile: str,
) -> str:
    """Render a business-problem report from an explicit, validated Artifact Bundle."""
    validate_package(package)
    if profile not in {"business_problem", "full_diagnostic"}:
        raise ContractError(f"不支持的诊断报告配置：{profile}")
    allowed_producers = {
        str(item["producer_skill"])
        for item in package["analysis_results"]["visualization_package"][
            "source_contracts"
        ]
    }
    payloads = {
        producer: payload
        for producer, payload in payloads.items()
        if producer in allowed_producers
    }
    order = [
        "objective-data-analysis",
        "subjective-feedback-analysis",
        "experience-heuristic-analysis",
        "evidence-govern",
        "root-cause-synthesis",
        "problem-framing",
        "experience-blueprint",
        "business-impact",
        "outcome-validation-recheck",
    ]
    sections: list[str] = []
    if payloads.get("objective-data-analysis"):
        sections.append(_objective_diagnostic_section(payloads["objective-data-analysis"]))
    configs = {
        "subjective-feedback-analysis": (
            "用户反馈：用户如何感受",
            [],
            [
                ("theme_clusters", "反馈主题", ("cluster_id", "label", "sample_count", "sample_share")),
            ],
        ),
        "experience-heuristic-analysis": (
            "启发式检查：界面与交互哪里可能造成障碍",
            [],
            [("findings", "启发式问题", ("finding_id", "issue", "severity", "effort"))],
        ),
        "evidence-govern": (
            "证据互证：哪些问题有多源支持",
            [],
            [
                ("evidence_relationships", "证据关系", ("relationship_id", "relationship_type", "strength", "summary")),
                ("context_factor_assessments", "混杂因素", ("factor_id", "factor_type", "assessment", "impact")),
            ],
        ),
        "root-cause-synthesis": (
            "根因候选：为什么会发生",
            [],
            [
                ("root_cause_candidates", "根因候选", ("candidate_id", "problem_statement", "mechanism", "confidence")),
                ("intervention_direction_candidates", "干预方向", ("direction_id", "direction", "rationale", "status")),
            ],
        ),
        "problem-framing": (
            "问题框定：解决谁的什么问题",
            [
                ("problem_definition", "问题定义"),
                ("target_population", "目标用户"),
                ("target_scenarios", "目标场景"),
                ("success_definition", "成功定义"),
                ("design_focus", "设计关注点"),
            ],
            [],
        ),
        "experience-blueprint": (
            "体验方案：准备如何解决",
            [("blueprint_summary", "方案摘要")],
            [
                ("solution_designs", "候选体验方案", ("solution_id", "title", "problem_ref", "value_hypothesis", "valuation_readiness")),
                ("validation_requirements", "验证要求", ("validation_id", "metric", "success_rule", "time_window")),
            ],
        ),
        "business-impact": (
            "业务价值：影响谁、价值多大、需要投入什么",
            [("portfolio_summary", "组合价值摘要")],
            [
                ("problem_impact_cases", "问题影响", ("case_id", "problem_statement", "affected_population", "business_consequence")),
                ("solution_value_cases", "方案价值", ("case_id", "solution_ref", "solution_value", "roi_assessment")),
            ],
        ),
        "outcome-validation-recheck": (
            "效果回检：方案是否真正有效",
            [],
            [
                ("effect_measurements", "效果指标", ("measurement_id", "metric_type", "baseline_value", "comparison_value", "result")),
                ("outcome_relationships", "效果关系", ("relationship_id", "relation_type", "result", "attribution")),
            ],
        ),
    }
    for producer in order[1:]:
        payload = payloads.get(producer)
        if not payload:
            continue
        title, fields, collections = configs[producer]
        if producer in {
            "subjective-feedback-analysis",
            "root-cause-synthesis",
            "outcome-validation-recheck",
        }:
            source = {
                **payload.get("analysis_results", {}),
                "findings": payload.get("findings", []),
                "analysis_summary": payload.get("analysis_summary"),
            }
        else:
            source = payload
        sections.append(
            _business_section(
                title,
                source,
                fields=fields,
                collections=collections,
            )
        )
        if producer == "subjective-feedback-analysis":
            sections.append(
                _nps_diagnostic_section(
                    payload.get("analysis_results", {}).get("nps_summary", {})
                )
            )
    included = [producer for producer in order if producer in payloads]
    missing = [producer for producer in order if producer not in payloads]
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(package['run']['project_name'])} · 完整体验诊断报告</title>
<style>
:root{{--ink:#142033;--ink-soft:#334155;--muted:#64748b;--line:#dbe3ef;--bg:#f2f6fb;--surface-elevated:#fff;--brand:#3454d1;--brand-deep:#172a67;--brand-soft:#eef2ff;--accent:#f59e0b;--shadow:0 18px 45px rgba(29,48,91,.08);--shadow-soft:0 8px 24px rgba(29,48,91,.06)}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:radial-gradient(circle at 85% 0,#e8edff 0,transparent 30rem),var(--bg);color:var(--ink);font:14px/1.68 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif;-webkit-font-smoothing:antialiased}}.skip-link{{position:fixed;z-index:20;top:12px;left:12px;transform:translateY(-160%);padding:10px 14px;border-radius:10px;background:#fff;color:var(--brand-deep);box-shadow:var(--shadow)}}.skip-link:focus{{transform:none}}main{{max-width:1240px;margin:auto;padding:32px 24px 80px}}.report-hero{{position:relative;overflow:hidden;padding:38px 40px;border-radius:26px;background:linear-gradient(135deg,#152557 0%,#2946b8 58%,#4f6be5 100%);color:#fff;box-shadow:0 24px 55px rgba(34,55,130,.22)}}.report-hero:after{{content:"";position:absolute;width:360px;height:360px;right:-130px;top:-220px;border:1px solid #ffffff28;border-radius:50%;box-shadow:0 0 0 54px #ffffff0b,0 0 0 108px #ffffff08}}.report-kicker{{position:relative;z-index:1;margin-bottom:12px;font-size:12px;font-weight:750;letter-spacing:.12em;color:#cbd5ff}}h1{{position:relative;z-index:1;margin:0 0 12px;font-size:clamp(27px,3vw,38px);line-height:1.18;letter-spacing:-.03em}}h2{{margin:0 0 15px;font-size:21px;letter-spacing:-.015em}}h3{{margin:24px 0 10px;color:var(--ink-soft)}}.meta{{position:relative;z-index:1;color:#e3e8ff}}.notice{{position:relative;z-index:1;margin-top:20px;max-width:950px;padding:12px 15px;border:1px solid #ffffff38;border-radius:12px;background:#ffffff14;color:#f8fafc;backdrop-filter:blur(8px)}}.panel{{margin-top:20px;padding:22px;background:var(--surface-elevated);border:1px solid var(--line);border-radius:18px;box-shadow:var(--shadow-soft)}}.panel>h2{{display:flex;align-items:center;gap:9px}}.panel>h2:before{{content:"";width:5px;height:20px;border-radius:8px;background:linear-gradient(var(--brand),#7890f2)}}.conclusions{{margin-bottom:16px;padding:14px 16px;background:linear-gradient(120deg,#f2f5ff,#fafbff);border:1px solid #d9e1ff;border-left:5px solid var(--brand);border-radius:12px}}.metric-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:16px}}.metric{{position:relative;min-height:102px;padding:16px;border:1px solid var(--line);border-radius:15px;background:linear-gradient(145deg,#fff,#f7f9ff);overflow:hidden}}.metric:after{{content:"";position:absolute;left:0;right:0;bottom:0;height:4px;background:linear-gradient(90deg,var(--brand),#8b9df4)}}.metric span{{display:block;color:var(--muted);font-weight:650}}.metric strong{{display:block;margin-top:8px;font-size:25px;color:var(--brand-deep);font-variant-numeric:tabular-nums}}.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:13px}}table{{width:100%;border-collapse:separate;border-spacing:0}}th,td{{padding:11px 13px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{position:sticky;top:0;color:#475569;background:#f5f7fb;font-size:12px}}tbody tr:nth-child(even){{background:#fafcff}}tbody tr:hover{{background:#f1f5ff}}tbody tr:last-child td{{border-bottom:0}}.spec{{color:var(--muted)}}:focus-visible{{outline:3px solid var(--accent);outline-offset:3px}}@media(max-width:820px){{.metric-grid{{grid-template-columns:repeat(2,1fr)}}}}@media(max-width:620px){{main{{padding:16px 12px 52px}}.report-hero{{padding:27px 22px;border-radius:20px}}.panel{{padding:16px;border-radius:15px}}.metric-grid{{grid-template-columns:1fr 1fr;gap:9px}}}}@media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}*,*:before,*:after{{animation-duration:.01ms!important;transition-duration:.01ms!important}}}}@media print{{body{{background:#fff}}main{{max-width:none;padding:0}}.skip-link{{display:none!important}}.report-hero,.panel,.metric{{box-shadow:none;break-inside:avoid}}.report-hero{{background:#fff;color:#111;border:1px solid #bbb}}.meta,.notice{{color:#333}}}}
</style></head><body><a class="skip-link" href="#report-main">跳到报告正文</a><main id="report-main" class="report-shell"><header class="report-hero"><div class="report-kicker">多来源体验诊断</div><h1>{_esc(package['run']['project_name'])}完整体验诊断报告</h1>
<div class="meta">报告包：{_esc(profile)} · Run：{_esc(package['run']['run_id'])} · Contract：5.0.0</div>
<div class="notice">本报告只投影显式 Artifact Bundle 中获准消费的正式结果，不扫描 current/latest，不重算指标、关系、根因、方案或价值。</div></header>
<section class="panel"><h2>诊断范围</h2><p><strong>已纳入：</strong>{_esc("、".join(included))}</p><p><strong>本次未纳入：</strong>{_esc("、".join(missing) if missing else "无")}</p></section>
{''.join(sections)}
</main></body></html>"""


def render_generic_html(package: dict[str, Any]) -> str:
    validate_package(package)
    visualization = package["analysis_results"]["visualization_package"]
    renderable = [
        output
        for output in visualization["visual_outputs"]
        if output["render_status"] in {"formal", "degraded"}
    ]
    if not renderable and not visualization["relationship_diagrams"]:
        raise ContractError("当前包只有 brief/blocked 规格，没有可正式渲染的数据")
    sources = _table(
        ["来源", "生产者", "类型", "版本", "运行", "状态"],
        [
            [
                source["source_id"],
                source["producer_skill"],
                source["artifact_type"],
                source["artifact_version"],
                source["source_run_id"],
                source["contract_status"],
            ]
            for source in visualization["source_contracts"]
        ],
    )
    limitations = "".join(
        f"<li><strong>{_esc(item['type'])}</strong> {_esc(item['description'])}</li>"
        for item in package["limitations"]
    )
    reviews = "".join(
        f"<li>{_esc(item['description'])} — {_esc(item['required_action'])}</li>"
        for item in package["manual_review_requests"]
    ) or "<li>无待处理人工复核项。</li>"
    body = "".join(_render_visual(output) for output in visualization["visual_outputs"])
    relationships = "".join(
        _render_diagram(diagram) for diagram in visualization["relationship_diagrams"]
    )
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(package['run']['project_name'])} · 可视化交付</title>
<style>
:root{{--ink:#142033;--ink-soft:#334155;--muted:#64748b;--line:#dbe3ef;--bg:#f2f6fb;--surface-elevated:#fff;--brand:#3454d1;--brand-deep:#172a67;--brand-soft:#eef2ff;--accent:#f59e0b;--shadow:0 18px 45px rgba(29,48,91,.08);--shadow-soft:0 8px 24px rgba(29,48,91,.06)}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:radial-gradient(circle at 85% 0,#e8edff 0,transparent 30rem),var(--bg);color:var(--ink);font:14px/1.68 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif;-webkit-font-smoothing:antialiased}}.skip-link{{position:fixed;z-index:20;top:12px;left:12px;transform:translateY(-160%);padding:10px 14px;border-radius:10px;background:#fff;color:var(--brand-deep);box-shadow:var(--shadow)}}.skip-link:focus{{transform:none}}main{{max-width:1180px;margin:auto;padding:32px 24px 80px}}.report-hero{{position:relative;overflow:hidden;padding:36px 38px;border-radius:25px;background:linear-gradient(135deg,#152557 0%,#2946b8 62%,#4f6be5 100%);color:#fff;box-shadow:0 24px 55px rgba(34,55,130,.22)}}.report-hero:after{{content:"";position:absolute;width:340px;height:340px;right:-130px;top:-210px;border:1px solid #ffffff28;border-radius:50%;box-shadow:0 0 0 54px #ffffff0b,0 0 0 108px #ffffff08}}.report-kicker{{position:relative;z-index:1;margin-bottom:10px;font-size:12px;font-weight:750;letter-spacing:.12em;color:#cbd5ff}}h1{{position:relative;z-index:1;margin:0 0 12px;font-size:clamp(27px,3vw,37px);line-height:1.18;letter-spacing:-.03em}}h2{{display:flex;align-items:center;gap:9px;margin:4px 0 13px;font-size:20px}}h2:before{{content:"";width:5px;height:20px;border-radius:8px;background:linear-gradient(var(--brand),#7890f2)}}.meta{{position:relative;z-index:1;color:#e3e8ff}}.notice{{position:relative;z-index:1;margin-top:19px;max-width:900px;padding:12px 15px;border:1px solid #ffffff38;border-radius:12px;background:#ffffff14;color:#f8fafc}}.panel{{margin-top:20px;padding:22px;background:var(--surface-elevated);border:1px solid var(--line);border-radius:18px;box-shadow:var(--shadow-soft)}}.eyebrow{{color:var(--brand);font-size:12px;font-weight:750;letter-spacing:.08em;text-transform:uppercase}}.table-wrap,.diagram-scroll,.chart-scroll{{overflow:auto;border:1px solid var(--line);border-radius:13px}}table{{width:100%;border-collapse:separate;border-spacing:0}}th,td{{padding:11px 13px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}}th{{position:sticky;top:0;background:#f5f7fb;color:#475569;font-size:12px}}tbody tr:nth-child(even){{background:#fafcff}}tbody tr:hover{{background:#f1f5ff}}tbody tr:last-child td{{border-bottom:0}}.bar-row{{display:grid;grid-template-columns:minmax(110px,190px) 1fr 96px;gap:12px;align-items:center;margin:12px 0}}.bar-row i{{height:13px;background:#e7ecf5;border-radius:9px;overflow:hidden}}.bar-row b{{display:block;height:100%;border-radius:9px;background:linear-gradient(90deg,var(--brand),#7187ec)}}.bar-row strong{{text-align:right;font-variant-numeric:tabular-nums}}.metric-card{{display:grid;grid-template-columns:auto auto;gap:4px 12px;align-items:end;max-width:440px;padding:22px;border:1px solid #cbd5ff;border-radius:16px;background:var(--brand-soft)}}.metric-card strong{{font-size:36px;line-height:1;font-variant-numeric:tabular-nums}}.metric-card small{{grid-column:1/-1;color:var(--muted)}}.chart-legend{{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}}.chart-legend span{{padding:3px 9px;border-radius:999px;background:var(--brand-soft)}}.grouped-category{{margin:16px 0}}.grouped-category h3{{margin:0 0 7px}}.grouped-series{{display:grid;grid-template-columns:minmax(100px,160px) 1fr 80px;gap:10px;align-items:center;margin:6px 0}}.grouped-series i{{height:11px;background:#edf0f7;border-radius:8px;overflow:hidden}}.grouped-series b{{display:block;height:100%;background:var(--brand)}}.stacked-row{{display:grid;grid-template-columns:130px 1fr;gap:10px;margin:14px 0}}.stacked-track{{display:flex;min-height:34px;overflow:hidden;border-radius:9px;background:#edf0f7}}.stacked-segment{{display:grid;place-items:center;min-width:1px;border-right:2px solid #fff;background:var(--brand);color:#fff;overflow:hidden}}.stacked-segment:nth-child(even){{background:#7187ec}}.stacked-row strong{{grid-column:2;font-size:12px;color:var(--muted)}}.series-svg,.scatter-svg,.distribution-svg{{width:100%;min-width:520px;height:250px}}.series-svg polyline{{fill:none;stroke:var(--brand);stroke-width:3}}.series-svg circle,.scatter-point{{fill:#fff;stroke:var(--brand);stroke-width:3}}.scatter-svg .axis,.distribution-svg line{{stroke:#94a3b8;stroke-width:1}}.distribution-chart{{display:flex;align-items:end;gap:8px;min-height:240px;overflow-x:auto;padding:14px}}.distribution-bin{{display:grid;grid-template-rows:180px auto auto;gap:4px;min-width:54px;text-align:center}}.distribution-bin i{{display:flex;align-items:end;background:#edf0f7;border-radius:8px 8px 2px 2px;overflow:hidden}}.distribution-bin b{{display:block;width:100%;background:var(--brand)}}.funnel-denominator{{color:var(--muted)}}.funnel-chart{{display:grid;gap:10px}}.funnel-stage{{display:grid;grid-template-columns:minmax(100px,170px) 1fr 90px;gap:10px;align-items:center}}.funnel-stage i{{display:grid;place-items:center;justify-self:center;min-height:36px;border-radius:8px;background:linear-gradient(90deg,var(--brand-deep),var(--brand));color:#fff;font-style:normal}}.funnel-stage small{{color:var(--muted)}}.diagram{{min-width:760px;width:100%;height:auto;background:#fbfcff}}.diagram line{{stroke:#7183c4;stroke-opacity:.7}}.diagram rect{{fill:var(--brand-soft);stroke:#8294d7}}.diagram text{{font-size:12px;fill:var(--ink)}}.relationship-data{{margin-top:14px}}.relationship-data summary{{cursor:pointer;font-weight:700;color:var(--brand-deep)}}.relationship-data .table-wrap{{margin:8px 0 16px}}.spec,.caveats{{color:var(--muted)}}:focus-visible{{outline:3px solid var(--accent);outline-offset:3px}}@media(max-width:700px){{main{{padding:16px 12px 48px}}.report-hero{{padding:27px 22px;border-radius:20px}}.panel{{padding:16px}}.bar-row{{grid-template-columns:95px 1fr}}.bar-row strong{{grid-column:2;text-align:left}}}}@media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}*,*:before,*:after{{animation-duration:.01ms!important;transition-duration:.01ms!important}}}}@media print{{body{{background:#fff}}main{{max-width:none;padding:0}}.skip-link{{display:none!important}}.report-hero,.panel{{box-shadow:none;break-inside:avoid}}.report-hero{{background:#fff;color:#111;border:1px solid #bbb}}.meta,.notice{{color:#333}}.table-wrap,.diagram-scroll,.chart-scroll{{overflow:visible}}}}
</style></head><body><a class="skip-link" href="#report-main">跳到报告正文</a><main id="report-main" class="report-shell">
<header class="report-hero"><div class="report-kicker">可信数据表达</div><h1>{_esc(package['run']['project_name'])}</h1>
<div class="meta">Run：{_esc(package['run']['run_id'])} · Contract：5.0.0 · Quality：{_esc(package['quality']['overall_status'])}</div>
<div class="notice">本页面只表达已校验的正式来源或 chart-ready 数据，不重新计算分析结论。</div></header>
<section class="panel"><h2>来源契约</h2>{sources}</section>
{body}{relationships}
<section class="panel"><h2>限制</h2><ul>{limitations}</ul><h2>人工复核</h2><ul>{reviews}</ul></section>
</main></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    input_parser = subparsers.add_parser("validate-input")
    input_parser.add_argument("--request", required=True, type=Path)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--package", required=True, type=Path)
    build_parser = subparsers.add_parser("build-bundle")
    build_parser.add_argument("--request", required=True, type=Path)
    build_parser.add_argument("--package-output", required=True, type=Path)
    publish_parser = subparsers.add_parser("publish")
    publish_parser.add_argument("--package", required=True, type=Path)
    publish_parser.add_argument("--request", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "validate-input":
        request = load_json(args.request)
        validate_input(request)
        print("data-visualization-input=valid contract=5.0.0")
        return 0
    if args.command == "build-bundle":
        request = load_json(args.request)
        package = build_bundle_package(request)
        atomic_write(
            args.package_output,
            json.dumps(package, ensure_ascii=False, indent=2) + "\n",
        )
        print(
            json.dumps(
                {
                    "status": "bundle_candidate_built",
                    "package": str(args.package_output),
                    "source_count": len(request["upstream_sources"]),
                },
                ensure_ascii=False,
            )
        )
        return 0
    package = load_json(args.package)
    validate_package(package)
    if args.command == "validate":
        print("data-visualization-package=valid contract=5.0.0")
        return 0
    if args.command == "publish":
        request = load_json(args.request)
        reference = publish_package(package, request)
        print(json.dumps(reference, ensure_ascii=False, indent=2))
        return 0
    raise ContractError(f"不支持的命令：{args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
