#!/usr/bin/env python3
"""Comparable historical baseline analysis with strict current-window exclusion."""

from __future__ import annotations

import math
import re
from statistics import mean, median
from typing import Any

from input_adapter import stable_id
from time_parsing import parse_time


def numeric(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    low, high = int(index), min(int(index) + 1, len(ordered) - 1)
    weight = index - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def _band(values: list[float], method: str) -> dict[str, Any]:
    if method == "mean_sd":
        center = mean(values)
        deviation = math.sqrt(sum((value - center) ** 2 for value in values) / (len(values) - 1)) if len(values) > 1 else 0.0
        return {"center": center, "normal_low": center - 2 * deviation, "normal_high": center + 2 * deviation, "wide_low": center - 3 * deviation, "wide_high": center + 3 * deviation}
    return {"center": median(values), "normal_low": quantile(values, .05), "normal_high": quantile(values, .95), "wide_low": quantile(values, .01), "wide_high": quantile(values, .99)}


def _status(value: float, band: dict[str, Any], strong_allowed: bool) -> str:
    if strong_allowed and (value < band["wide_low"] or value > band["wide_high"]):
        return "strong_anomaly"
    if value < band["normal_low"] or value > band["normal_high"]:
        return "weak_anomaly"
    return "normal"


def _period_key(value: str) -> tuple[int, int, int, str] | None:
    text = value.strip()
    quarter = re.fullmatch(r"(\d{4})[-/]?Q([1-4])", text, re.I)
    month = re.fullmatch(r"(\d{4})[-/](\d{1,2})", text)
    year = re.fullmatch(r"\d{4}", text)
    if quarter:
        return int(quarter.group(1)), (int(quarter.group(2)) - 1) * 3 + 1, 1, text
    if month:
        year_value, month_value = int(month.group(1)), int(month.group(2))
        return (year_value, month_value, 1, text) if 1 <= month_value <= 12 else None
    if year:
        return int(text), 1, 1, text
    try:
        parsed = parse_time(text)
        if parsed is None:
            return None
        return parsed.year, parsed.month, parsed.day, text
    except (OverflowError, OSError, ValueError):
        return None


def _aggregate_periods(rows: list[dict[str, Any]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], str | None]:
    period_col, metric_col = str(config["period_col"]), str(config["metric_col"])
    numerator_col, denominator_col = config.get("numerator_col"), config.get("denominator_col")
    aggregation = config.get("period_aggregation")
    order_col = config.get("order_col")
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        period = str(row.get(period_col) or "").strip()
        if period:
            grouped.setdefault(period, []).append(row)
    if any(_period_key(period) is None for period in grouped):
        return [], "unsupported_period_format"
    points: list[dict[str, Any]] = []
    for period, members in grouped.items():
        value: float | None = None
        if numerator_col and denominator_col:
            numerators = [numeric(row.get(numerator_col)) for row in members]
            denominators = [numeric(row.get(denominator_col)) for row in members]
            if any(item is None for item in numerators + denominators) or not sum(item or 0 for item in denominators):
                return [], f"invalid_period_ratio_components:{period}"
            value = sum(item or 0 for item in numerators) / sum(item or 0 for item in denominators)
        else:
            values = [item for item in (numeric(row.get(metric_col)) for row in members) if item is not None]
            if len(members) == 1 and values:
                value = values[0]
            elif not aggregation:
                return [], f"period_aggregation_required:{period}"
            elif not values:
                return [], f"period_metric_missing:{period}"
            elif aggregation == "sum":
                value = sum(values)
            elif aggregation == "mean":
                value = mean(values)
            elif aggregation == "median":
                value = median(values)
            elif aggregation == "latest":
                if not order_col:
                    return [], f"latest_aggregation_requires_order_col:{period}"
                ordered = sorted(members, key=lambda row: str(row.get(order_col) or ""))
                value = numeric(ordered[-1].get(metric_col))
            else:
                return [], f"unsupported_period_aggregation:{aggregation}"
        seasons = {str(row.get(config.get("season_col")) or "") for row in members if config.get("season_col")}
        if len(seasons) > 1:
            return [], f"inconsistent_season_within_period:{period}"
        points.append({"period": period, "value": value, "season": next(iter(seasons), "")})
    points.sort(key=lambda item: _period_key(item["period"]) or (0, 0, 0, item["period"]))
    return points, None


def analyze_baseline(
    rows: list[dict[str, Any]],
    config: dict[str, Any],
    store_baseline: dict[str, Any] | None = None,
    lineage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    period_col, metric_col = config.get("period_col"), config.get("metric_col")
    if not period_col or not metric_col:
        return {"status": "not_evaluable", "reason": "baseline_config_incomplete", "definition": {}, "comparability": {"comparable": False}, "comparisons": [], "candidate": None}
    parsed, aggregation_error = _aggregate_periods(rows, config)
    if aggregation_error:
        return {"status": "not_evaluable", "reason": aggregation_error, "definition": {}, "comparability": {"comparable": False}, "comparisons": [], "candidate": None, "reliability": {"sample_size": 0, "inference_performed": False}, "limitations": [aggregation_error]}
    current_count = int(config.get("current_periods", 1))
    if current_count < 1 or len(parsed) <= current_count:
        return {"status": "not_evaluable", "reason": "no_history_after_strict_current_window_exclusion", "definition": {}, "comparability": {"comparable": False, "current_window_excluded": True}, "comparisons": [], "candidate": None}
    history, current = parsed[:-current_count], parsed[-current_count:]
    method = str(config.get("method", "median_quantile"))
    if method == "same_period":
        if not config.get("season_col"):
            return {"status": "not_evaluable", "reason": "same_period_requires_season_col", "definition": {}, "comparability": {"comparable": False}, "comparisons": [], "candidate": None}
        seasons = {item["season"] for item in current if item["season"]}
        history = [item for item in history if item["season"] in seasons]
    if config.get("rolling_window"):
        history = history[-int(config["rolling_window"]):]
    minimum = int(config.get("minimum_history", 8))
    if len(history) < minimum:
        return {"status": "not_evaluable", "reason": "insufficient_history", "definition": {"minimum_history": minimum, "history_count": len(history)}, "comparability": {"comparable": False, "current_window_excluded": True}, "comparisons": [], "candidate": None}

    metric_id = str(config.get("metric_contract_id") or metric_col)
    grain = str(config.get("grain", "overall"))
    scenario = str(config.get("scenario_key", "overall"))
    task_identity = str(config.get("task_identity") or config.get("task_name") or "").strip()
    if config.get("require_task_identity", True) and not task_identity:
        return {
            "status": "not_evaluable",
            "reason": "baseline_task_identity_required",
            "definition": {},
            "comparability": {"comparable": False},
            "comparisons": [],
            "candidate": None,
            "limitations": ["baseline_task_identity_required"],
        }
    fingerprint = stable_id("cmp", metric_id, grain, scenario, task_identity, config.get("definition_version", "1"), config.get("period_aggregation"), config.get("numerator_col"), config.get("denominator_col"))
    definition = {
        "metric_contract_id": metric_id,
        "scenario_key": scenario,
        "task_identity": task_identity,
        "grain": grain,
        "period_field": period_col,
        "metric_field": metric_col,
        "method": method,
        "history_window": {"start": history[0]["period"], "end": history[-1]["period"]},
        "current_window": {"start": current[0]["period"], "end": current[-1]["period"]},
        "current_window_strictly_excluded": True,
        "comparison_fingerprint": fingerprint,
    }
    checks = {
        "metric_contract": not store_baseline or store_baseline.get("metric_contract_ref") == metric_id,
        "grain": not store_baseline or store_baseline.get("grain") == grain,
        "scenario": not store_baseline or store_baseline.get("scenario_key") == scenario,
        "task_identity": not store_baseline or store_baseline.get("task_identity") == task_identity,
        "comparison_fingerprint": not store_baseline or store_baseline.get("comparison_fingerprint") == fingerprint,
        "current_window_excluded": not bool({item["period"] for item in history} & {item["period"] for item in current}),
    }
    comparable = all(checks.values())
    calculated_band = _band([item["value"] for item in history], "median_quantile" if method == "same_period" else method)
    candidate_id = stable_id("baseline_candidate", metric_id, scenario, history[0]["period"], history[-1]["period"])
    candidate = {
        "baseline_id": candidate_id,
        "baseline_version": "1",
        "metric_contract_ref": metric_id,
        "scenario_key": scenario,
        "task_identity": task_identity,
        "grain": grain,
        "segment_definition_ref": config.get("segment_definition_ref"),
        "baseline_window": definition["history_window"],
        "period_granularity": str(config.get("period_granularity") or "period"),
        "calculation_method": method,
        "baseline_values": {
            "center_value": calculated_band["center"],
            "normal_band": {"low": calculated_band["normal_low"], "high": calculated_band["normal_high"]},
            "wide_band": {"low": calculated_band["wide_low"], "high": calculated_band["wide_high"]},
            "history_count": len(history),
        },
        "comparability_contract": {
            "metric_contract_ref": metric_id,
            "scenario_key": scenario,
            "task_identity": task_identity,
            "grain": grain,
            "comparison_fingerprint": fingerprint,
            "current_window_excluded": True,
        },
        "comparison_fingerprint": fingerprint,
        "confidence": "high" if len(history) >= 30 else "medium" if len(history) >= 12 else "low",
        "lifecycle_status": "proposed",
        "review_status": "pending",
        "lineage": lineage or {
            "source_artifact_refs": [],
            "source_item_refs": [],
            "input_fingerprint": None,
        },
        "supersedes_ref": None,
    }
    active_id = store_baseline.get("baseline_id") if store_baseline and comparable else candidate_id
    active_version = store_baseline.get("baseline_version") if store_baseline and comparable else "candidate-1"
    active_band = calculated_band
    if store_baseline and comparable:
        values = store_baseline.get("baseline_values", {})
        normal = values.get("normal_band", {})
        wide = values.get("wide_band", normal)
        active_band = {"center": values.get("center_value"), "normal_low": normal.get("low"), "normal_high": normal.get("high"), "wide_low": wide.get("low"), "wide_high": wide.get("high")}
        if any(value is None for value in active_band.values()):
            comparable = False
            checks["numeric_band_complete"] = False
            active_id, active_version, active_band = candidate_id, "candidate-1", calculated_band
    comparisons = [{
        "comparison_id": stable_id("comparison", active_id, item["period"]),
        "baseline_id": active_id,
        "baseline_version": active_version,
        "period": item["period"],
        "current_value": item["value"],
        "absolute_delta": item["value"] - active_band["center"],
        "relative_delta": (item["value"] - active_band["center"]) / active_band["center"] if active_band["center"] else None,
        "anomaly_status": _status(item["value"], active_band, len(history) >= 100),
    } for item in current]
    return {
        "status": "completed",
        "definition": definition,
        "comparability": {"comparable": comparable, "checks": checks, "source": "baseline_store" if store_baseline and comparable else "calculated_history_candidate"},
        "comparisons": comparisons,
        "candidate": None if store_baseline and comparable else candidate,
        "limitations": [] if len(history) >= 100 else ["strong_anomaly_not_used_below_100_history_points"],
        "reliability": {
            "sample_size": len(history),
            "current_period_count": len(current),
            "period_aggregation": "ratio_recomputed" if config.get("numerator_col") and config.get("denominator_col") else config.get("period_aggregation", "single_value_per_period"),
            "comparability_confirmed": comparable,
            "inference_performed": False,
        },
    }
