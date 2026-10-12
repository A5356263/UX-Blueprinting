#!/usr/bin/env python3
"""Normalize deterministic Business Impact calculations and validate package 4.0.0."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import tempfile
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[4]
REGISTRY_PATH = PROJECT_ROOT / "shared-workflow/data-analysis/artifact-registry.json"
VERSION = "4.0.0"
INPUT_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas/input.schema.json"
OUTPUT_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas/output.schema.json"
RUNTIME_DIR = PROJECT_ROOT / "shared-workflow/data-analysis/runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))
import contract_runtime

TOP_LEVEL = {
    "run",
    "analysis_contract",
    "data_quality",
    "valuation_inputs",
    "problem_impact_cases",
    "solution_value_cases",
    "portfolio_summary",
    "assumption_ledger",
    "limitations",
    "downstream_handoffs",
    "handoff",
}
FINAL_TOP_LEVEL = TOP_LEVEL | {"publication", "delivery"}

BANNED_KEYS = {
    "value_assessments",
    "effort_assessments",
    "roi_assessments",
    "candidate_problem_links",
    "candidate_multi_source",
    "optimization_value_ceiling",
    "business_value_relationship_chains",
    "break_even_analysis",
}

QUANTIFIED_SENSITIVITY = {
    "metric_change",
    "conversion_rate",
    "adoption_rate",
    "unit_value",
    "attribution_discount",
    "investment",
}


class PackageError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PackageError(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PackageError(f"cannot read JSON: {exc}") from exc
    require(isinstance(value, dict), "package root must be an object")
    return value


def resolve_pointer(document: Any, pointer: str) -> Any:
    require(pointer.startswith("#/"), f"not an absolute JSON Pointer: {pointer}")
    current = document
    for raw in pointer[2:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        try:
            current = current[int(token)] if isinstance(current, list) else current[token]
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            raise PackageError(f"unresolvable JSON Pointer: {pointer}") from exc
    return current


def optional_schema_validate(value: dict[str, Any], schema_path: Path) -> None:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return
    schema = load_json(schema_path)
    try:
        resolver = jsonschema.RefResolver(
            base_uri=schema_path.resolve().as_uri(), referrer=schema
        )
        jsonschema.Draft202012Validator(schema, resolver=resolver).validate(value)
    except Exception as exc:
        raise PackageError(f"{schema_path.name} validation failed: {exc}") from exc


def validate_input_request(request: dict[str, Any]) -> None:
    optional_schema_validate(request, INPUT_SCHEMA_PATH)
    require(request.get("context_mode") in {"independent", "chain_context"}, "invalid context_mode")
    modes = set(request.get("requested_modes", []))
    require(bool(modes), "requested_modes cannot be empty")
    sources = request.get("sources", [])
    require(bool(sources), "sources cannot be empty")
    artifact_bindings = [
        item
        for item in request.get("input_bindings", [])
        if item.get("binding_type") == "artifact_instance"
    ]
    registry = load_json(REGISTRY_PATH)
    for source in sources:
        if source.get("source_type") != "artifact":
            continue
        matches = [
            item["binding_ref"]
            for item in artifact_bindings
            if isinstance(item.get("binding_ref"), dict)
            and item["binding_ref"].get("artifact_id") == source.get("source_ref")
        ]
        require(
            len(matches) == 1,
            f"artifact source {source.get('source_ref')} requires exactly one Artifact Instance binding",
        )
        try:
            payload, _ = contract_runtime.validate_instance_ref(
                matches[0], workspace_root=PROJECT_ROOT, registry=registry
            )
        except contract_runtime.ContractRuntimeError as exc:
            raise PackageError(str(exc)) from exc
        run = payload.get("run", {})
        require(
            source.get("source_version") == matches[0]["artifact_version"]
            and source.get("run_id") == matches[0]["run_id"]
            and source.get("project_name") == matches[0]["project_name"],
            f"artifact source {source.get('source_ref')} descriptor does not match its instance",
        )
    if not modes.intersection({"solution_value", "validated_revaluation"}):
        return
    if "validated_revaluation" in modes:
        require(bool(request.get("outcome_refs")), "validated_revaluation requires outcome_refs")
        require(bool(request.get("prior_valuation_ref")), "validated_revaluation requires prior_valuation_ref")
    blueprint_sources = [
        item
        for item in sources
        if item.get("source_type") == "artifact"
        and item.get("source_ref") == "experience-blueprint"
    ]
    if not blueprint_sources:
        require(
            bool(request.get("user_solution_statement"))
            or any(item.get("source_type") == "formal_plan" for item in sources),
            "solution valuation requires a Blueprint solution, user solution statement, or formal plan",
        )
        require(
            not request.get("solution_refs"),
            "solution_refs are reserved for the formal Experience Blueprint handoff",
        )
        return
    require(
        request.get("context_mode") == "chain_context",
        "Experience Blueprint solution valuation requires explicit chain_context",
    )
    require(len(blueprint_sources) == 1, "exactly one Experience Blueprint source is allowed")
    instance_ref = request.get("blueprint_artifact_instance_ref")
    require(isinstance(instance_ref, dict), "Blueprint chain requires blueprint_artifact_instance_ref")
    require(
        instance_ref.get("artifact_id") == "experience-blueprint"
        and instance_ref.get("producer_skill") == "experience-blueprint",
        "Experience Blueprint Artifact Instance identity mismatch",
    )
    try:
        blueprint, _ = contract_runtime.validate_instance_ref(
            instance_ref,
            workspace_root=PROJECT_ROOT,
            registry=registry,
        )
    except contract_runtime.ContractRuntimeError as exc:
        raise PackageError(str(exc)) from exc
    run = blueprint.get("run", {})
    require(run.get("project_name") == request.get("project_name"), "experience-blueprint project_name mismatch")
    handoff = request.get("blueprint_handoff")
    require(isinstance(handoff, dict), "Blueprint chain requires blueprint_handoff")
    require(
        blueprint.get("handoff") == handoff,
        "Blueprint handoff is not the exact registered handoff",
    )
    require(
        handoff.get("target_skill") == "business-impact",
        "Experience Blueprint handoff binding is invalid",
    )
    require(
        handoff.get("handoff_status") in {"ready", "ready_with_caveats"}
        and "solution_value_assessment" in handoff.get("allowed_uses", []),
        "Experience Blueprint handoff is not released for solution valuation",
    )
    released_refs = set(handoff.get("payload_refs", []))
    refs = request.get("solution_refs", [])
    require(bool(refs), "solution valuation requires solution_refs")
    for ref in refs:
        artifact_id, marker, pointer = str(ref).partition("#")
        require(marker == "#" and artifact_id == "experience-blueprint", f"invalid solution_ref: {ref}")
        absolute_pointer = f"#{pointer}"
        require(absolute_pointer in released_refs, f"solution_ref is not released by the Experience Blueprint handoff: {ref}")
        solution = resolve_pointer(blueprint, absolute_pointer)
        require(isinstance(solution, dict) and solution.get("solution_id"), f"solution_ref does not select a solution: {ref}")
        require(solution.get("readiness") == "valuation_ready", f"{solution.get('solution_id')} is not valuation_ready")
        require("solution_value_input" in solution.get("allowed_uses", []), f"{solution.get('solution_id')} does not allow solution_value_input")
        require(solution.get("valuation_inputs_status") == "complete", f"{solution.get('solution_id')} has incomplete valuation inputs")
        require(not solution.get("open_questions"), f"{solution.get('solution_id')} still has blocking open questions")


def walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


def dec(value: Any, label: str) -> Decimal:
    require(not isinstance(value, bool), f"{label} must be numeric")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise PackageError(f"{label} must be numeric") from exc
    require(result.is_finite(), f"{label} must be finite")
    return result


def number(value: Decimal, precision: int) -> int | float:
    quantum = Decimal(1).scaleb(-precision)
    rounded = value.quantize(quantum, rounding=ROUND_HALF_UP)
    if rounded == rounded.to_integral():
        return int(rounded)
    return float(rounded)


def validate_range(value: Any, label: str, *, nonnegative: bool = False, rate: bool = False) -> None:
    require(isinstance(value, dict), f"{label} must be a range object")
    require(set(value) == {"low", "base", "high"}, f"{label} must contain low/base/high only")
    low, base, high = (dec(value[key], f"{label}.{key}") for key in ("low", "base", "high"))
    require(low <= base <= high, f"{label} must satisfy low <= base <= high")
    if nonnegative:
        require(low >= 0, f"{label} cannot be negative")
    if rate:
        require(low >= 0 and high <= 1, f"{label} must stay within 0..1")


def validate_measurement_scope(scope: Any, label: str) -> None:
    require(isinstance(scope, dict), f"{label} must be an object")
    require(
        set(scope) == {
            "grain",
            "dimensions",
            "time_window",
            "population_definition",
        },
        f"{label} must contain grain/dimensions/time_window/population_definition only",
    )
    require(
        scope["grain"]
        in {
            "enterprise",
            "user",
            "account",
            "task",
            "survey_response",
            "business_board",
            "enterprise_x_business_board",
            "unknown",
        },
        f"{label}.grain is invalid",
    )
    require(isinstance(scope["dimensions"], dict), f"{label}.dimensions must be an object")


def measurement_scope_key(scope: dict[str, Any]) -> str:
    return json.dumps(scope, ensure_ascii=False, sort_keys=True)


def range_sum(values: list[dict[str, Any]], precision: int) -> dict[str, Any]:
    return {
        key: number(sum((dec(item[key], key) for item in values), Decimal(0)), precision)
        for key in ("low", "base", "high")
    }


def range_product(values: list[dict[str, Any]], multiplier: Any, precision: int) -> dict[str, Any]:
    factor = dec(multiplier, "period_multiplier")
    result: dict[str, Any] = {}
    for key in ("low", "base", "high"):
        product = factor
        for item in values:
            product *= dec(item[key], key)
        result[key] = number(product, precision)
    return result


def derive_population(problem: dict[str, Any], precision: int) -> None:
    population = problem["affected_population"]
    estimated = population.get("estimated_affected_range")
    denominator = population.get("denominator_count")
    if estimated is not None and denominator is not None:
        denominator_d = dec(denominator, "denominator_count")
        require(denominator_d > 0, "denominator_count must be positive")
        population["affected_share_range"] = {
            key: number(dec(estimated[key], key) / denominator_d, precision)
            for key in ("low", "base", "high")
        }
    elif estimated is None or denominator is None:
        population["affected_share_range"] = None


def derive_solution(solution: dict[str, Any], contract: dict[str, Any], precision: int) -> None:
    links = solution["metric_value_links"]
    included: list[dict[str, Any]] = []
    benefit_components: list[dict[str, Any]] = []
    for link in links:
        metric_change = copy.deepcopy(link["metric_change"])
        if link["metric_change_unit"] == "nps_points":
            metric_change = {
                key: number(dec(value, f"{link['link_id']}.metric_change") / Decimal(100), precision)
                for key, value in metric_change.items()
            }
        link["benefit_range"] = range_product(
            [
                link["addressable_volume"],
                metric_change,
                link["conversion_rate"],
                link["adoption_rate"],
                link["attribution_discount"],
                link["unit_value"],
            ],
            link["period_multiplier"],
            precision,
        )
        if link["aggregation_policy"] == "include":
            included.append(link["benefit_range"])
            benefit_components.append(
                {
                    "component_id": f"benefit:{link['link_id']}",
                    "description": f"指标价值：{link['metric_ref']}",
                    "value_range": copy.deepcopy(link["benefit_range"]),
                    "currency": link["currency"],
                    "source_ref": link["link_id"],
                    "dedup_group": link["dedup_group"],
                }
            )
    solution["benefit_components"] = benefit_components

    if solution["valuation_level"] != "quantified_roi":
        solution["benefit_components"] = []
        solution["expected_benefit_range"] = None
        solution["effort_profile"]["total_investment_range"] = None
        solution["total_disbenefit_range"] = None
        solution["net_benefit_range"] = None
        solution["roi_range"] = None
        solution["payback_period_range"] = None
        return

    solution["expected_benefit_range"] = range_sum(included, precision) if included else {"low": 0, "base": 0, "high": 0}
    costs = [item["cost_range"] for item in solution["effort_profile"]["components"]]
    require(all(item is not None for item in costs), f"{solution['solution_value_case_id']} quantified ROI requires all cost ranges")
    investment = range_sum(costs, precision) if costs else {"low": 0, "base": 0, "high": 0}
    solution["effort_profile"]["total_investment_range"] = investment
    disbenefits = [item["value_range"] for item in solution["disbenefit_components"]]
    total_disbenefit = range_sum(disbenefits, precision) if disbenefits else {"low": 0, "base": 0, "high": 0}
    solution["total_disbenefit_range"] = total_disbenefit

    benefit = solution["expected_benefit_range"]
    net = {
        "low": number(dec(benefit["low"], "benefit.low") - dec(investment["high"], "investment.high") - dec(total_disbenefit["high"], "disbenefit.high"), precision),
        "base": number(dec(benefit["base"], "benefit.base") - dec(investment["base"], "investment.base") - dec(total_disbenefit["base"], "disbenefit.base"), precision),
        "high": number(dec(benefit["high"], "benefit.high") - dec(investment["low"], "investment.low") - dec(total_disbenefit["low"], "disbenefit.low"), precision),
    }
    solution["net_benefit_range"] = net

    if all(dec(investment[key], f"investment.{key}") > 0 for key in ("low", "base", "high")):
        solution["roi_range"] = {
            "low": number(dec(net["low"], "net.low") / dec(investment["high"], "investment.high"), precision),
            "base": number(dec(net["base"], "net.base") / dec(investment["base"], "investment.base"), precision),
            "high": number(dec(net["high"], "net.high") / dec(investment["low"], "investment.low"), precision),
        }
    else:
        solution["roi_range"] = None

    window = contract.get("valuation_window")
    period_count = dec(window["period_count"], "period_count") if window else None
    periodic = None
    if period_count:
        periodic = {
            "best": (dec(benefit["high"], "benefit.high") - dec(total_disbenefit["low"], "disbenefit.low")) / period_count,
            "base": (dec(benefit["base"], "benefit.base") - dec(total_disbenefit["base"], "disbenefit.base")) / period_count,
            "worst": (dec(benefit["low"], "benefit.low") - dec(total_disbenefit["high"], "disbenefit.high")) / period_count,
        }
    if periodic and all(value > 0 for value in periodic.values()):
        solution["payback_period_range"] = {
            "low": number(dec(investment["low"], "investment.low") / periodic["best"], precision),
            "base": number(dec(investment["base"], "investment.base") / periodic["base"], precision),
            "high": number(dec(investment["high"], "investment.high") / periodic["worst"], precision),
        }
    else:
        solution["payback_period_range"] = None


def derive_portfolio(package: dict[str, Any]) -> dict[str, Any]:
    problems = package["problem_impact_cases"]
    solutions = package["solution_value_cases"]
    problem_by_id = {item["problem_impact_case_id"]: item for item in problems}
    priority: list[dict[str, Any]] = []
    for problem in problems:
        value_status = problem["addressable_opportunity"]["status"]
        priority.append(
            {
                "case_ref": problem["problem_impact_case_id"],
                "case_type": "problem_impact",
                "value_status": value_status,
                "readiness": problem["maturity"],
                "recommendation": "进入方案设计" if problem["maturity"] == "evidence_backed" else "优先补证",
            }
        )

    chains: list[dict[str, Any]] = []
    by_problem: dict[str, list[str]] = {}
    levels = {"impact_only": len(problems), "value_vs_effort": 0, "quantified_roi": 0}
    for solution in solutions:
        levels[solution["valuation_level"]] += 1
        readiness = solution["forecast_status"] if solution["valuation_timing"] == "forecast" else "validated_revaluation"
        priority.append(
            {
                "case_ref": solution["solution_value_case_id"],
                "case_type": "solution_value",
                "value_status": "quantified" if solution["expected_benefit_range"] is not None else "qualitative",
                "readiness": readiness,
                "recommendation": solution["decision_recommendation"],
            }
        )
        by_problem.setdefault(solution["problem_impact_case_ref"], []).append(solution["solution_value_case_id"])
        problem = problem_by_id[solution["problem_impact_case_ref"]]
        unit = problem["affected_population"]["unit"]
        for link in solution["metric_value_links"]:
            chains.append(
                {
                    "chain_id": f"chain:{solution['solution_value_case_id']}:{link['link_id']}",
                    "problem_ref": problem["problem_impact_case_id"],
                    "solution_ref": solution["solution_value_case_id"],
                    "metric_link_ref": link["link_id"],
                    "nodes": [
                        f"problem:{problem['problem_impact_case_id']}",
                        f"population:{unit}",
                        f"metric:{link['metric_ref']}",
                        f"solution:{solution['solution_ref']}",
                        f"effect:{link['effect_status']}",
                        f"value:{link['currency']}",
                    ],
                    "status": solution["valuation_timing"],
                }
            )
    comparisons = [
        {"problem_ref": problem_ref, "solution_case_refs": refs}
        for problem_ref, refs in sorted(by_problem.items())
        if len(refs) > 1
    ]
    return {
        "problem_case_count": len(problems),
        "solution_case_count": len(solutions),
        "valuation_level_counts": levels,
        "business_value_priority_view": priority,
        "impact_value_chains": chains,
        "solution_comparison_view": comparisons,
    }


def validate_envelope(package: dict[str, Any]) -> None:
    require(
        frozenset(package) in {frozenset(TOP_LEVEL), frozenset(FINAL_TOP_LEVEL)},
        f"top-level fields must be exactly the base or published contract: {', '.join(sorted(TOP_LEVEL))}",
    )
    banned = sorted(set(walk_keys(package)) & BANNED_KEYS)
    require(not banned, f"package contains removed fields: {', '.join(banned)}")


def normalize_package(package: dict[str, Any]) -> dict[str, Any]:
    validate_envelope(package)
    result = copy.deepcopy(package)
    precision = int(result["analysis_contract"]["calculation_precision"])
    for problem in result["problem_impact_cases"]:
        derive_population(problem, precision)
    for solution in result["solution_value_cases"]:
        derive_solution(solution, result["analysis_contract"], precision)
    result["portfolio_summary"] = derive_portfolio(result)
    return result


def validate_references(refs: Iterable[str], known: set[str], label: str, *, allow_empty: bool = True) -> None:
    refs_list = list(refs)
    if not allow_empty:
        require(bool(refs_list), f"{label} cannot be empty")
    unknown = sorted(set(refs_list) - known)
    require(not unknown, f"{label} contains unknown valuation inputs: {', '.join(unknown)}")


def validate_package(package: dict[str, Any]) -> None:
    validate_envelope(package)
    optional_schema_validate(package, OUTPUT_SCHEMA_PATH)

    run = package["run"]
    require(run.get("artifact_type") == "business_impact_assessment", "invalid artifact_type")
    require(run.get("artifact_version") == VERSION, f"artifact_version must be {VERSION}")
    require(run.get("producer_skill") == "business-impact", "invalid producer_skill")
    require(run.get("run_modes") == package["analysis_contract"].get("requested_modes"), "run_modes must match requested_modes")
    expected_source_mode = "user_inputs_only" if run.get("context_mode") == "independent" else "explicit_chain_context"
    require(run.get("source_mode") == expected_source_mode, "source_mode must match context_mode")
    require(all(source.get("project_name") == run.get("project_name") for source in run.get("sources", [])), "all sources must use the same project_name")
    require(all(source.get("explicitly_referenced") is True for source in run.get("sources", [])), "all sources must be explicitly referenced")
    for source in run.get("sources", []):
        if source.get("source_type") == "artifact":
            source_ref = str(source.get("source_ref") or "")
            require(
                "/" not in source_ref and not source_ref.startswith("."),
                "artifact sources must use a Registry Artifact or Context ID, not a path",
            )
            require(source.get("source_version"), "artifact sources must declare source_version")
    source_ids = [source.get("source_id") for source in run.get("sources", [])]
    require(len(source_ids) == len(set(source_ids)), "run.sources contains duplicate source_id")
    known_sources = set(source_ids)

    inputs = package["valuation_inputs"]
    input_ids = [item.get("input_id") for item in inputs]
    require(len(input_ids) == len(set(input_ids)), "valuation_inputs contains duplicate input_id")
    known_inputs = set(input_ids)
    input_by_id = {item["input_id"]: item for item in inputs}
    contract_currency = package["analysis_contract"]["currency"]
    for item in inputs:
        source_root = item["source_ref"].split("#", 1)[0]
        require(source_root in known_sources, f"{item['input_id']} source_ref does not resolve to run.sources")
        validate_measurement_scope(
            item["measurement_scope"], f"{item['input_id']}.measurement_scope"
        )
        if item["time_window"] is not None:
            require(
                item["measurement_scope"]["time_window"] == item["time_window"],
                f"{item['input_id']} time_window must match measurement_scope",
            )
    classification_rank = {"internal": 0, "confidential": 1, "restricted": 2}
    max_input_rank = max((classification_rank[item["sensitivity"]] for item in inputs), default=0)
    require(classification_rank[run["data_classification"]] >= max_input_rank, "run.data_classification is lower than input sensitivity")

    problem_ids: list[str] = []
    stable_keys: list[str] = []
    for problem in package["problem_impact_cases"]:
        problem_id = problem["problem_impact_case_id"]
        problem_ids.append(problem_id)
        stable_keys.append(problem["stable_key"])
        validate_references(problem["source_input_refs"], known_inputs, f"{problem_id}.source_input_refs", allow_empty=False)
        population = problem["affected_population"]
        validate_measurement_scope(
            population["measurement_scope"],
            f"{problem_id}.affected_population.measurement_scope",
        )
        require(
            population["unit"] == population["measurement_scope"]["grain"]
            or population["unit"] == "unknown",
            f"{problem_id} population unit must match measurement_scope grain",
        )
        validate_references(population["basis_input_refs"], known_inputs, f"{problem_id}.affected_population.basis_input_refs")
        for name in ("estimated_affected_range", "affected_share_range"):
            if population[name] is not None:
                validate_range(population[name], f"{problem_id}.{name}", nonnegative=True, rate=name == "affected_share_range")
        if population["projection_status"] in {"measured", "derived"}:
            require(population["denominator_count"] is not None, f"{problem_id} projected population requires denominator_count")
            population_sources = [input_by_id[ref] for ref in population["basis_input_refs"]]
            require(any(item["semantic_role"] == "population_metric" for item in population_sources), f"{problem_id} projected population requires population_metric input")
            require(not any(item["source_skill"] in {"subjective-feedback-analysis", "experience-heuristic-analysis"} for item in population_sources), f"{problem_id} cannot project population from subjective or heuristic input")
            scoped_population_inputs = [
                item
                for item in population_sources
                if item["semantic_role"] == "population_metric"
            ]
            require(
                any(
                    measurement_scope_key(item["measurement_scope"])
                    == measurement_scope_key(population["measurement_scope"])
                    for item in scoped_population_inputs
                ),
                f"{problem_id} projected population requires a matching measurement_scope",
            )
            if population["unit"] in {"enterprise", "enterprise_x_business_board"}:
                require(
                    any(
                        item["source_skill"] == "objective-data-analysis"
                        for item in scoped_population_inputs
                    ),
                    f"{problem_id} enterprise population must come from Objective aggregates",
                )
            join = population["join_coverage"]
            validate_references(join["source_input_refs"], known_inputs, f"{problem_id}.affected_population.join_coverage.source_input_refs")
            if join["status"] == "not_required":
                require(bool(join.get("reason")), f"{problem_id} join_coverage not_required needs an explicit single-source reason")
            else:
                require(join["status"] in {"sufficient", "partial"}, f"{problem_id} projected population requires positive join coverage")
                require(
                    join.get("matched_count") is not None
                    and dec(join["matched_count"], f"{problem_id}.join_coverage.matched_count") > 0,
                    f"{problem_id} projected population requires matched_count > 0",
                )
                require(
                    any(
                        value is not None
                        and dec(value, f"{problem_id}.join_coverage.match_rate") > 0
                        for value in (join.get("left_match_rate"), join.get("right_match_rate"))
                    ),
                    f"{problem_id} projected population requires a positive match rate",
                )
        eligible = population["eligible_count"]
        observed = population["observed_sample_count"]
        affected = population["observed_affected_count"]
        if observed is not None and affected is not None:
            require(dec(affected, f"{problem_id}.observed_affected_count") <= dec(observed, f"{problem_id}.observed_sample_count"), f"{problem_id} observed affected cannot exceed observed sample")
        if eligible is not None and observed is not None:
            require(dec(observed, f"{problem_id}.observed_sample_count") <= dec(eligible, f"{problem_id}.eligible_count"), f"{problem_id} observed sample cannot exceed eligible population")
        if population["estimated_affected_range"] is not None and population["denominator_count"] is not None:
            require(dec(population["estimated_affected_range"]["high"], f"{problem_id}.estimated.high") <= dec(population["denominator_count"], f"{problem_id}.denominator"), f"{problem_id} estimated affected cannot exceed denominator")
        for segment in population["segments"]:
            validate_references(segment["source_input_refs"], known_inputs, f"{segment['segment_ref']}.source_input_refs")
            if segment["affected_range"] is not None:
                validate_range(segment["affected_range"], f"{segment['segment_ref']}.affected_range", nonnegative=True)
        if problem["maturity"] == "evidence_backed":
            require(any(input_by_id[ref]["source_type"] == "governed_artifact" for ref in problem["source_input_refs"]), f"{problem_id} evidence_backed requires governed input")
        else:
            source_skills = {
                input_by_id[ref]["source_skill"]
                for ref in problem["source_input_refs"]
                if input_by_id[ref]["semantic_role"] == "problem_evidence" and input_by_id[ref]["source_skill"]
            }
            require(len(source_skills) <= 1, f"{problem_id} preliminary case cannot merge multiple analysis skills")
        for impact in problem["impact_components"]:
            validate_references(impact["source_input_refs"], known_inputs, f"{impact['impact_id']}.source_input_refs")
            if impact["magnitude_range"] is not None:
                validate_range(impact["magnitude_range"], f"{impact['impact_id']}.magnitude_range")
        for frame_name in ("cost_of_inaction", "addressable_opportunity"):
            frame = problem[frame_name]
            validate_references(frame["basis_input_refs"], known_inputs, f"{problem_id}.{frame_name}.basis_input_refs")
            if frame["value_range"] is not None:
                validate_range(frame["value_range"], f"{problem_id}.{frame_name}.value_range", nonnegative=True)
                require(frame["currency"] is not None and frame["time_window"] is not None, f"{problem_id}.{frame_name} quantified value needs currency/window")
                require(contract_currency is None or frame["currency"] == contract_currency, f"{problem_id}.{frame_name} currency must match contract")
                require(frame["status"] == "quantified", f"{problem_id}.{frame_name} value range requires quantified status")
            else:
                require(frame["status"] != "quantified", f"{problem_id}.{frame_name} quantified status requires value range")
    require(len(problem_ids) == len(set(problem_ids)), "duplicate problem_impact_case_id")
    require(len(stable_keys) == len(set(stable_keys)), "duplicate problem stable_key")
    known_problems = set(problem_ids)

    solution_ids: list[str] = []
    for solution in package["solution_value_cases"]:
        solution_id = solution["solution_value_case_id"]
        solution_ids.append(solution_id)
        require(solution["problem_impact_case_ref"] in known_problems, f"{solution_id} references unknown problem case")
        validate_references(solution["source_input_refs"], known_inputs, f"{solution_id}.source_input_refs", allow_empty=False)
        solution_inputs = [input_by_id[ref] for ref in solution["source_input_refs"]]
        require(any(item["semantic_role"] == "solution_scope" for item in solution_inputs), f"{solution_id} requires explicit solution_scope input")
        require(not any(item["source_skill"] == "root-cause-synthesis" and item["semantic_role"] == "solution_scope" for item in solution_inputs), f"{solution_id} cannot use Root Cause direction as concrete solution")
        source_type_requirements = {
            "experience_blueprint": lambda item: item["source_skill"] == "experience-blueprint",
            "user_defined_solution": lambda item: item["source_type"] == "user_input",
            "formal_plan": lambda item: item["source_type"] == "formal_plan",
        }
        require(any(item["semantic_role"] == "solution_scope" and source_type_requirements[solution["solution_source_type"]](item) for item in solution_inputs), f"{solution_id} solution_source_type does not match solution input")
        for link in solution["qualitative_value_links"]:
            validate_references(link["source_input_refs"], known_inputs, f"{link['link_id']}.source_input_refs", allow_empty=False)
        included_groups: list[str] = []
        for link in solution["metric_value_links"]:
            validate_measurement_scope(
                link["measurement_scope"], f"{link['link_id']}.measurement_scope"
            )
            validate_range(link["addressable_volume"], f"{link['link_id']}.addressable_volume", nonnegative=True)
            validate_range(
                link["metric_change"],
                f"{link['link_id']}.metric_change",
                nonnegative=link["metric_change_unit"] in {"rate", "count"},
                rate=link["metric_change_unit"] == "rate",
            )
            if link["metric_change_unit"] == "nps_points":
                require(
                    dec(link["metric_change"]["low"], f"{link['link_id']}.metric_change.low") >= Decimal(-200)
                    and dec(link["metric_change"]["high"], f"{link['link_id']}.metric_change.high") <= Decimal(200),
                    f"{link['link_id']} NPS point change must stay within -200..200",
                )
            for field in ("conversion_rate", "adoption_rate", "attribution_discount"):
                validate_range(link[field], f"{link['link_id']}.{field}", nonnegative=True, rate=True)
            validate_range(link["unit_value"], f"{link['link_id']}.unit_value", nonnegative=True)
            validate_range(link["benefit_range"], f"{link['link_id']}.benefit_range", nonnegative=True)
            require(link["currency"] == contract_currency, f"{link['link_id']} currency must match contract")
            validate_references(link["source_input_refs"], known_inputs, f"{link['link_id']}.source_input_refs", allow_empty=False)
            require(link["baseline_input_ref"] in link["source_input_refs"], f"{link['link_id']} baseline_input_ref must be included in source_input_refs")
            require(input_by_id[link["baseline_input_ref"]]["semantic_role"] in {"population_metric", "effect_estimate"}, f"{link['link_id']} baseline_input_ref must point to metric input")
            require(
                measurement_scope_key(
                    input_by_id[link["baseline_input_ref"]]["measurement_scope"]
                )
                == measurement_scope_key(link["measurement_scope"]),
                f"{link['link_id']} baseline measurement_scope does not match link",
            )
            roles = {input_by_id[ref]["semantic_role"] for ref in link["source_input_refs"]}
            require({"population_metric", "effect_estimate", "unit_value"} <= roles, f"{link['link_id']} needs population/effect/unit-value inputs")
            if link["formula_type"] == "transition_value":
                require("business_rule" in roles, f"{link['link_id']} transition formula requires business rule")
                require(
                    link["measurement_scope"]["grain"]
                    in {"enterprise", "enterprise_x_business_board"},
                    f"{link['link_id']} transition value requires enterprise scope",
                )
            if link["formula_type"] == "nps_value":
                require(
                    link["metric_change_unit"] == "nps_points",
                    f"{link['link_id']} NPS value requires nps_points",
                )
                require(
                    link["measurement_scope"]["grain"] == "survey_response",
                    f"{link['link_id']} NPS value requires survey_response scope",
                )
                require(
                    "business_rule" in roles,
                    f"{link['link_id']} NPS value requires an explicit value rule",
                )
            if link["aggregation_policy"] == "include":
                included_groups.append(link["dedup_group"])
            if solution["valuation_timing"] == "validated_revaluation":
                require(link["effect_status"] == "validated_result", f"{link['link_id']} revaluation needs validated_result")
                require(any(input_by_id[ref]["source_type"] == "outcome_artifact" for ref in link["source_input_refs"]), f"{link['link_id']} validated result needs Outcome input")
            else:
                require(link["effect_status"] == "forecast_scenario", f"{link['link_id']} forecast cannot claim validated effect")
        require(len(included_groups) == len(set(included_groups)), f"{solution_id} has duplicate included dedup_group")

        for component in solution["effort_profile"]["components"]:
            if component["cost_range"] is not None:
                validate_range(component["cost_range"], f"{component['component_id']}.cost_range", nonnegative=True)
                require(component["source_input_ref"] in known_inputs, f"{component['component_id']} cost source is missing")
                require(input_by_id[component["source_input_ref"]]["semantic_role"] == "cost", f"{component['component_id']} must reference cost input")
                require(component["currency"] == contract_currency, f"{component['component_id']} currency must match contract")
        for component in solution["disbenefit_components"]:
            validate_range(component["value_range"], f"{component['component_id']}.value_range", nonnegative=True)
            require(component["currency"] == contract_currency, f"{component['component_id']} currency must match contract")
            require(component["source_ref"] in known_inputs, f"{component['component_id']} disbenefit source is missing")
        for impact in solution["guardrail_impacts"]:
            validate_references(impact["source_input_refs"], known_inputs, f"{impact['guardrail_ref']}.source_input_refs")
        for effect in solution["distributional_effects"]:
            validate_references(effect["source_input_refs"], known_inputs, f"{effect['segment_ref']}.source_input_refs")
        for sensitivity in solution["sensitivity_analysis"]:
            source_ref = sensitivity["source_input_ref"]
            require(source_ref is None or source_ref in known_inputs, f"{solution_id} sensitivity source is missing")
        if solution["valuation_level"] == "quantified_roi":
            require(package["analysis_contract"]["currency"] is not None, f"{solution_id} quantified ROI needs currency")
            require(package["analysis_contract"]["valuation_window"] is not None, f"{solution_id} quantified ROI needs valuation window")
            require(bool(solution["metric_value_links"]), f"{solution_id} quantified ROI needs metric_value_links")
            require(bool(solution["effort_profile"]["components"]), f"{solution_id} quantified ROI needs cost components")
            require(all(item["cost_range"] is not None for item in solution["effort_profile"]["components"]), f"{solution_id} quantified ROI needs all cost ranges")
            sensitivity = {item["parameter"] for item in solution["sensitivity_analysis"]}
            require(QUANTIFIED_SENSITIVITY <= sensitivity, f"{solution_id} quantified ROI lacks sensitivity parameters")
            for field, nonnegative in (
                ("expected_benefit_range", True),
                ("total_disbenefit_range", True),
                ("net_benefit_range", False),
                ("roi_range", False),
                ("payback_period_range", True),
            ):
                if solution[field] is not None:
                    validate_range(solution[field], f"{solution_id}.{field}", nonnegative=nonnegative)
            validate_range(solution["effort_profile"]["total_investment_range"], f"{solution_id}.total_investment_range", nonnegative=True)
            require(dec(solution["effort_profile"]["total_investment_range"]["base"], f"{solution_id}.investment.base") > 0, f"{solution_id} quantified ROI needs positive investment")
        else:
            require(bool(solution["qualitative_value_links"]), f"{solution_id} value_vs_effort needs qualitative value links")
            require(not solution["metric_value_links"], f"{solution_id} value_vs_effort cannot carry quantified metric value links")
            require(solution["benefit_components"] == [], f"{solution_id} value_vs_effort cannot emit monetary benefit components")
            require(solution["expected_benefit_range"] is None and solution["roi_range"] is None, f"{solution_id} value_vs_effort cannot emit quantified ROI")
        if solution["valuation_timing"] == "validated_revaluation":
            require(solution["prior_valuation_snapshot"] is not None, f"{solution_id} revaluation requires prior snapshot")
            require(solution["forecast_status"] == "not_applicable", f"{solution_id} revaluation forecast_status must be not_applicable")
        else:
            require(solution["prior_valuation_snapshot"] is None, f"{solution_id} forecast cannot carry prior snapshot")
            if solution["forecast_status"] == "decision_ready_forecast":
                decision_inputs = [
                    input_by_id[ref]
                    for link in solution["metric_value_links"]
                    for ref in link["source_input_refs"]
                ] + [
                    input_by_id[component["source_input_ref"]]
                    for component in solution["effort_profile"]["components"]
                    if component["source_input_ref"] in known_inputs
                ]
                require(all(item["provenance_status"] in {"formal_source", "user_confirmed"} for item in decision_inputs), f"{solution_id} decision-ready forecast cannot rely on scenario or unverified inputs")
        problem = next(item for item in package["problem_impact_cases"] if item["problem_impact_case_id"] == solution["problem_impact_case_ref"])
        opportunity = problem["addressable_opportunity"]
        if solution["expected_benefit_range"] is not None and opportunity["value_range"] is not None:
            require(opportunity["currency"] == contract_currency, f"{solution_id} opportunity currency must match contract")
            require(all(dec(solution["expected_benefit_range"][key], f"{solution_id}.benefit.{key}") <= dec(opportunity["value_range"][key], f"{solution_id}.opportunity.{key}") for key in ("low", "base", "high")), f"{solution_id} expected benefit cannot exceed addressable opportunity")
        harmed = any(item["status"] == "harmed" for item in solution["guardrail_impacts"])
        if harmed or solution["non_compensable_risks"]:
            require(solution["decision_recommendation"] == "manual_risk_review", f"{solution_id} material risk requires manual_risk_review")
    require(len(solution_ids) == len(set(solution_ids)), "duplicate solution_value_case_id")

    if "validated_revaluation" in run["run_modes"]:
        expected_state = "validated_revaluation"
    elif any(item["forecast_status"] == "provisional_forecast" for item in package["solution_value_cases"]):
        expected_state = "provisional_forecast"
    elif any(item["forecast_status"] == "decision_ready_forecast" for item in package["solution_value_cases"]):
        expected_state = "decision_ready_forecast"
    else:
        expected_state = "problem_impact_only"
    require(run["valuation_state"] == expected_state, "run.valuation_state does not match case state")

    for assumption in package["assumption_ledger"]:
        source_ref = assumption["source_input_ref"]
        require(source_ref is None or source_ref in known_inputs, f"{assumption['assumption_id']} has unknown source input")

    handoff_ids = [item["handoff_id"] for item in package["downstream_handoffs"]]
    require(len(handoff_ids) == len(set(handoff_ids)), "duplicate downstream handoff")
    for item in package["downstream_handoffs"]:
        require(
            item["target_skill"] in {
                "experience-blueprint",
                "outcome-validation-recheck",
                "data-visualization",
                "evidence-archive",
            },
            "Business Impact handoff target is outside the capability boundary",
        )
        if item["target_skill"] == "evidence-archive":
            require(
                item["handoff_status"] == "pending_review"
                and bool(item["required_review_request_ids"]),
                "Evidence Archive requires a pending explicit review request",
            )

    handoff = package["handoff"]
    if run["status"] in {"not_evaluable", "blocked"}:
        require(not package["problem_impact_cases"] and not package["solution_value_cases"], "blocked/not_evaluable package cannot emit cases")

    normalized = normalize_package(package)
    require(package["portfolio_summary"] == normalized["portfolio_summary"], "portfolio_summary is not programmatically derived")
    for original, expected in zip(package["problem_impact_cases"], normalized["problem_impact_cases"]):
        require(original["affected_population"]["affected_share_range"] == expected["affected_population"]["affected_share_range"], f"{original['problem_impact_case_id']} affected share is not derived")
    for original, expected in zip(package["solution_value_cases"], normalized["solution_value_cases"]):
        fields = [
            "metric_value_links",
            "benefit_components",
            "expected_benefit_range",
            "total_disbenefit_range",
            "net_benefit_range",
            "roi_range",
            "payback_period_range",
        ]
        require(original["effort_profile"]["total_investment_range"] == expected["effort_profile"]["total_investment_range"], f"{original['solution_value_case_id']} investment is not derived")
        for field in fields:
            require(original[field] == expected[field], f"{original['solution_value_case_id']}.{field} is not programmatically derived")


def atomic_commit(package: dict[str, Any], output_path: Path) -> None:
    normalized = normalize_package(package)
    normalized["handoff"]["write_status"] = "written"
    validate_package(normalized)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(normalized, ensure_ascii=False, indent=2) + "\n"
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_name = handle.name
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, output_path)
        temp_name = None
    finally:
        if temp_name is not None:
            try:
                Path(temp_name).unlink()
            except FileNotFoundError:
                pass


def render_markdown(package: dict[str, Any]) -> str:
    labels = {
        "quantified_roi": "已量化 ROI",
        "value_vs_effort": "价值与投入对比",
        "impact_only": "仅评估问题影响",
        "provisional_forecast": "初步预测，需验证",
        "evidence_backed": "已有证据支持",
        "forecast_scenario": "情景预测",
        "observed": "已观察",
    }
    def range_text(value: Any, *, percent: bool = False) -> str:
        if not isinstance(value, dict):
            return "未量化"
        factor = 100 if percent else 1
        suffix = "%" if percent else ""
        values = [
            value.get("low"),
            value.get("base"),
            value.get("high"),
        ]
        if any(item is None for item in values):
            return "未量化"
        rendered = [
            f"{float(item) * factor:,.1f}{suffix}" if percent else f"{float(item):,.0f}"
            for item in values
        ]
        return f"{rendered[0]} / {rendered[1]} / {rendered[2]}（低/中/高）"

    run = package["run"]
    lines = [
        f"# {run['project_name']} · 业务影响评估",
        "",
        "## 问题影响",
        "",
    ]
    for item in package.get("problem_impact_cases", []):
        population = item.get("affected_population", {})
        lines += [
            f"### {item.get('problem_statement') or item.get('problem_impact_case_id')}",
            "",
            f"- 受影响对象：{population.get('unit', '未说明')}",
            f"- 受影响数量：{range_text(population.get('estimated_affected_range'))}",
            f"- 受影响占比：{range_text(population.get('affected_share_range'), percent=True)}",
            f"- 不处理的机会损失：{range_text(item.get('cost_of_inaction', {}).get('value_range'))}",
            f"- 结论成熟度：{labels.get(item.get('maturity'), item.get('maturity', '未说明'))}",
            "",
        ]
    lines += ["", "## 方案价值", ""]
    for item in package.get("solution_value_cases", []):
        lines += [
            f"### {item.get('solution_ref') or item.get('solution_value_case_id')}",
            "",
            f"- 估算层级：{labels.get(item.get('valuation_level'), item.get('valuation_level', '未说明'))}",
            f"- 预期收益：{range_text(item.get('expected_benefit_range'))}",
            f"- 净收益：{range_text(item.get('net_benefit_range'))}",
            f"- ROI：{range_text(item.get('roi_range'), percent=True)}",
            f"- 回收期：{range_text(item.get('payback_period_range'))}",
            f"- 预测状态：{labels.get(item.get('forecast_status'), item.get('forecast_status', '未说明'))}",
            f"- 决策建议：{item.get('decision_recommendation', '未说明')}",
            "",
        ]
    summary = package.get("portfolio_summary", {})
    lines += [
        "## 组合判断",
        "",
        f"- 问题影响项：{summary.get('problem_case_count', 0)}",
        f"- 方案价值项：{summary.get('solution_case_count', 0)}",
    ]
    for item in summary.get("business_value_priority_view", []):
        lines.append(
            f"- {item.get('case_ref')}：{item.get('recommendation')} "
            f"（{item.get('readiness')}）"
        )
    lines += ["", "## 限制", ""]
    lines += [f"- {item}" for item in package.get("limitations", [])] or ["- 无额外限制"]
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("path", type=Path)
    validate_input_parser = subparsers.add_parser("validate-input")
    validate_input_parser.add_argument("path", type=Path)
    normalize_parser = subparsers.add_parser("normalize")
    normalize_parser.add_argument("path", type=Path)
    normalize_parser.add_argument("--output", "-o", type=Path)
    commit_parser = subparsers.add_parser("commit")
    commit_parser.add_argument("path", type=Path)
    commit_parser.add_argument("--output", "-o", type=Path, required=True)
    publish_parser = subparsers.add_parser("publish")
    publish_parser.add_argument("path", type=Path)
    publish_parser.add_argument("--request", required=True, type=Path)
    args = parser.parse_args(argv)

    try:
        package = load_json(args.path)
        if args.command == "validate-input":
            validate_input_request(package)
        elif args.command == "normalize":
            package = normalize_package(package)
            validate_package(package)
        elif args.command == "commit":
            atomic_commit(package, args.output)
        elif args.command == "publish":
            request = load_json(args.request)
            validate_input_request(request)
            package = normalize_package(package)
            package = contract_runtime.apply_request_envelope(package, request)
            validate_package(package)
            with tempfile.TemporaryDirectory() as directory:
                candidate = Path(directory) / "candidate.json"
                report = Path(directory) / "report.md"
                candidate.write_text(
                    json.dumps(package, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                report.write_text(render_markdown(package), encoding="utf-8")
                deliverables = []
                for item in request["requested_deliverables"]:
                    value = dict(item)
                    if value["format"] == "markdown":
                        value["source_path"] = str(report)
                    deliverables.append(value)
                reference = contract_runtime.publish_result(
                    workspace_root=PROJECT_ROOT,
                    registry_path=REGISTRY_PATH,
                    artifact_id="business-impact",
                    candidate_path=candidate,
                    purpose_key=request["analysis_purpose"]["purpose_key"],
                    purpose_label=request["analysis_purpose"]["purpose_label"],
                    deliverables=deliverables,
                )
        else:
            validate_package(package)
    except (PackageError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.command == "validate-input":
        print("OK: business impact input contract is valid")
    elif args.command == "normalize":
        output = json.dumps(package, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
    elif args.command == "commit":
        print(f"OK: committed {args.output}")
    elif args.command == "publish":
        print(json.dumps(reference, ensure_ascii=False, indent=2))
    else:
        print(f"OK: business impact assessment {VERSION} is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
