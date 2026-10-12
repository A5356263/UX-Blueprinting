#!/usr/bin/env python3
"""Task metrics, fixed funnel, controlled slices, and feature usage."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from math import sqrt
from typing import Any

import error_analyzer
from time_parsing import parse_time


def time_sort_key(value: Any) -> tuple[int, float, str]:
    parsed = parse_time(value)
    raw = str(value or "")
    if parsed is None:
        return (1, 0.0, raw)
    return (0, parsed.timestamp(), raw)


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    low, high = int(index), min(int(index) + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (index - low)


def _as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        if float(value) == 1:
            return True
        if float(value) == 0:
            return False
    text = str(value or "").strip().lower()
    if text in {"1", "1.0", "true", "yes", "y", "是", "完成", "成功"}:
        return True
    if text in {"0", "0.0", "false", "no", "n", "否", "未完成", "失败"}:
        return False
    return None


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_rate(value: Any) -> float | None:
    if isinstance(value, str) and value.strip().endswith("%"):
        number = _as_float(value.strip()[:-1])
        return number / 100 if number is not None else None
    number = _as_float(value)
    if number is None:
        return None
    return number / 100 if 1 < number <= 100 else number


def analyze_aggregate_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Read already-aggregated KPI rows without inventing missing denominators."""
    items = []
    for row in rows:
        completion = _as_rate(row.get("aggregate_completion_rate"))
        one_time = _as_rate(row.get("aggregate_one_time_completion_rate"))
        if completion is None and one_time is None:
            continue
        items.append({
            "task_name": str(row.get("task_name") or "未声明任务"),
            "completion_rate": completion,
            "one_time_completion_rate": one_time,
            "task_instance_count": int(_as_float(row.get("aggregate_task_count")) or 0) or None,
            "participant_count": int(_as_float(row.get("participant_count")) or 0) or None,
            "error_event_count": int(_as_float(row.get("aggregate_error_event_count")) or 0) or None,
            "error_affected_count": int(_as_float(row.get("aggregate_error_affected_count")) or 0) or None,
            "source_ref": str(row.get("_source_ref") or ""),
        })
    return {
        "status": "completed" if items else "not_evaluable",
        **({"reason": "aggregate_metric_fields_unavailable"} if not items else {}),
        "reported_metrics": items,
        "reliability": {
            "sample_size": sum(item.get("task_instance_count") or 0 for item in items),
            "row_grain": "aggregate_metric_summary",
            "inference_performed": False,
        },
        "limitations": [
            "aggregate rates without an explicit denominator remain reported rates and are not back-calculated"
        ] if any(item.get("task_instance_count") is None for item in items) else [],
    }


def _task_duration_unit(contract: dict[str, Any]) -> str | None:
    declared = str(contract.get("task_duration_unit") or "").strip().lower()
    aliases = {
        "s": "seconds",
        "sec": "seconds",
        "second": "seconds",
        "seconds": "seconds",
        "秒": "seconds",
        "m": "minutes",
        "min": "minutes",
        "minute": "minutes",
        "minutes": "minutes",
        "分钟": "minutes",
        "h": "hours",
        "hr": "hours",
        "hour": "hours",
        "hours": "hours",
        "小时": "hours",
        "ms": "milliseconds",
        "millisecond": "milliseconds",
        "milliseconds": "milliseconds",
        "毫秒": "milliseconds",
    }
    if declared:
        return aliases.get(declared)
    source_field = str(
        contract.get("field_mapping", {}).get("task_duration") or ""
    ).lower()
    if any(token in source_field for token in ("(min)", "分钟", "minute")):
        return "minutes"
    if any(token in source_field for token in ("(ms)", "毫秒", "millisecond")):
        return "milliseconds"
    if any(token in source_field for token in ("(hour)", "(hr)", "小时")):
        return "hours"
    if any(token in source_field for token in ("(s)", "秒", "second")):
        return "seconds"
    return None


def _duration_seconds(value: Any, unit: str | None) -> float | None:
    numeric = _as_float(value)
    if numeric is None or numeric < 0 or unit is None:
        return None
    multipliers = {
        "milliseconds": 0.001,
        "seconds": 1.0,
        "minutes": 60.0,
        "hours": 3600.0,
    }
    return numeric * multipliers[unit]


def analyze_task_summaries(rows: list[dict[str, Any]], contract: dict[str, Any]) -> dict[str, Any]:
    """Analyze one-row-per-task data without reconstructing event sequences."""
    by_task = {
        str(row.get("task_instance_id")): row
        for row in rows
        if row.get("task_instance_id")
    }
    total = len(by_task)
    completed = {key for key, row in by_task.items() if _as_bool(row.get("completion_flag")) is True}
    one_time = {key for key, row in by_task.items() if _as_bool(row.get("one_time_completion_flag")) is True}
    duration_unit = _task_duration_unit(contract)
    durations = [
        value
        for value in (
            _duration_seconds(row.get("task_duration"), duration_unit)
            for row in by_task.values()
        )
        if value is not None
    ]
    error_counts = [value for value in (_as_float(row.get("task_error_count")) for row in by_task.values()) if value is not None and value >= 0]
    delimiter = contract.get("journey_path_delimiter")
    paths: dict[tuple[str, ...], int] = defaultdict(int)
    for row in by_task.values():
        raw = str(row.get("journey_path") or "").strip()
        if raw and delimiter:
            sanitized = []
            for part in raw.split(str(delimiter)):
                part = part.strip()
                if not part:
                    continue
                label, state, _ = error_analyzer.redact_message(part)
                sanitized.append(
                    label if state == "safe" else "unclassified_redacted_step"
                )
            path = tuple(sanitized)
            if path:
                paths[path] += 1
    explicit_completion_count = sum(_as_bool(row.get("completion_flag")) is not None for row in by_task.values())
    explicit_one_time_count = sum(_as_bool(row.get("one_time_completion_flag")) is not None for row in by_task.values())
    completion_evaluable = bool(total) and explicit_completion_count == total
    one_time_evaluable = bool(total) and explicit_one_time_count == total
    reliability = {
        "sample_size": total,
        "row_grain": "task_summary",
        "explicit_completion_count": explicit_completion_count,
        "explicit_one_time_completion_count": explicit_one_time_count,
        "inference_performed": False,
    }
    limitations = []
    if not delimiter and any(row.get("journey_path") for row in by_task.values()):
        limitations.append("journey_path_delimiter_not_declared")
    if duration_unit is None and any(
        row.get("task_duration") not in (None, "") for row in by_task.values()
    ):
        limitations.append("task_duration_unit_not_declared")
    if total and not completion_evaluable:
        limitations.append("completion_signal_unavailable")
    if total and not one_time_evaluable:
        limitations.append("one_time_completion_signal_unavailable")
    return {
        "status": "completed" if completion_evaluable else "completed_with_caveats",
        "metrics": {
            "status": "completed" if completion_evaluable else "not_evaluable",
            **({"reason": "completion_signal_unavailable"} if total and not completion_evaluable else {}),
            "task_instance_count": total,
            "completion_count": len(completed) if completion_evaluable else None,
            "completion_rate": len(completed) / total if completion_evaluable else None,
            "one_time_completion_count": len(one_time) if one_time_evaluable else None,
            "one_time_completion_rate": len(one_time) / total if one_time_evaluable else None,
            "error_task_count": sum(value > 0 for value in error_counts) if error_counts else None,
            "error_task_rate": sum(value > 0 for value in error_counts) / total if total and error_counts else None,
            "duration_seconds": {"p50": percentile(durations, .5), "p70": percentile(durations, .7), "p90": percentile(durations, .9)},
            "task_duration_source_unit": duration_unit,
            "reliability": reliability,
            "limitations": limitations,
        },
        "funnel": {
            "status": "not_evaluable",
            "reason": "task_summary_has_no_step_level_funnel_contract",
            "limitations": ["task_summary_has_no_step_level_funnel_contract"],
        },
        "journey_paths": [
            {"path": list(path), "task_count": count, "share": count / total if total else None}
            for path, count in sorted(paths.items(), key=lambda item: (-item[1], item[0]))
        ],
        "reliability": reliability,
    }


def wilson_interval(successes: int, total: int, z: float = 1.96) -> dict[str, float] | None:
    if total <= 0:
        return None
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    margin = z * sqrt(
        proportion * (1 - proportion) / total + z * z / (4 * total * total)
    ) / denominator
    return {
        "estimate": proportion,
        "low": max(0.0, center - margin),
        "high": min(1.0, center + margin),
        "confidence_level": 0.95,
        "method": "wilson",
    }


def proportion_difference_interval(
    first_successes: int,
    first_total: int,
    second_successes: int,
    second_total: int,
    z: float = 1.96,
) -> dict[str, float] | None:
    if first_total <= 0 or second_total <= 0:
        return None
    first = first_successes / first_total
    second = second_successes / second_total
    difference = first - second
    standard_error = sqrt(
        first * (1 - first) / first_total
        + second * (1 - second) / second_total
    )
    return {
        "estimate": difference,
        "low": difference - z * standard_error,
        "high": difference + z * standard_error,
        "confidence_level": 0.95,
        "method": "unpooled_normal_approximation",
    }


def analyze_tasks(rows: list[dict[str, Any]], contract: dict[str, Any]) -> dict[str, Any]:
    steps = [str(value) for value in contract.get("funnel_steps", [])]
    completion_events = set(contract.get("completion_events", []))
    submit_events = set(contract.get("submit_events", []))
    draft_events = set(contract.get("draft_events", []))
    exit_events = set(contract.get("exit_events", []))
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = str(row.get("task_instance_id") or row.get("session_id") or "")
        if key:
            grouped[key].append(row)

    reached = {step: 0 for step in steps}
    durations: dict[str, list[float]] = {step: [] for step in steps}
    step_errors: dict[str, set[str]] = {step: set() for step in steps}
    unmapped_error_tasks: set[str] = set()
    task_durations: list[float] = []
    completed: set[str] = set()
    errored: set[str] = set()
    one_time: set[str] = set()
    drafted: set[str] = set()
    exited: set[str] = set()
    task_depth: dict[str, int] = {}
    completion_conflicts: set[str] = set()
    explicit_completion: dict[str, bool] = {}
    event_completion_declared = bool(completion_events) or any(
        str(row.get("event_class") or "") == "success_event" for row in rows
    )

    for key, events in grouped.items():
        values = {
            parsed
            for parsed in (_as_bool(row.get("completion_flag")) for row in events)
            if parsed is not None
        }
        if len(values) > 1:
            completion_conflicts.add(key)
        elif values:
            explicit_completion[key] = next(iter(values))

    all_tasks_explicit = bool(grouped) and len(explicit_completion) == len(grouped)
    completion_evaluable = not completion_conflicts and (
        event_completion_declared or all_tasks_explicit
    )

    for key, events in grouped.items():
        events.sort(key=lambda row: time_sort_key(row.get("event_time")))
        valid_times = [parsed for parsed in (parse_time(row.get("event_time")) for row in events) if parsed]
        if len(valid_times) >= 2:
            task_durations.append((valid_times[-1] - valid_times[0]).total_seconds())
        names = [str(row.get("event_name") or "") for row in events]
        classes = [str(row.get("event_class") or "") for row in events]
        event_complete = bool(completion_events.intersection(names)) or "success_event" in classes
        explicit_complete = explicit_completion.get(key)
        if (
            event_completion_declared
            and explicit_complete is not None
            and explicit_complete != event_complete
        ):
            completion_conflicts.add(key)
            completion_evaluable = False
        is_complete = explicit_complete if explicit_complete is not None else event_complete
        has_error = "error_event" in classes
        if is_complete:
            completed.add(key)
        if has_error:
            errored.add(key)
        if draft_events.intersection(names) or "draft_event" in classes:
            drafted.add(key)
        if exit_events.intersection(names) or "exit_event" in classes:
            exited.add(key)
        submit_count = sum(name in submit_events or cls == "submit_event" for name, cls in zip(names, classes))
        backtrack_count = classes.count("backtrack_event")
        if is_complete and submit_count <= 1 and backtrack_count == 0:
            one_time.add(key)

        cursor = 0
        prior_time: datetime | None = None
        depth = 0
        step_sequence = [str(row.get("journey_step") or "") for row in events]
        for position, step in enumerate(steps, start=1):
            match = next(((index, row) for index, row in enumerate(events[cursor:], start=cursor) if str(row.get("journey_step") or "") == step), None)
            if not match:
                break
            index, row = match
            reached[step] += 1
            depth = position
            now = parse_time(row.get("event_time"))
            if prior_time and now:
                durations[step].append((now - prior_time).total_seconds())
            prior_time = now
            cursor = index + 1
        for row in events:
            if row.get("event_class") == "error_event":
                error_step = str(row.get("journey_step") or "")
                if error_step in step_errors:
                    step_errors[error_step].add(key)
                else:
                    unmapped_error_tasks.add(key)
        task_depth[key] = depth
    total = len(grouped)
    step_metrics: list[dict[str, Any]] = []
    previous = total
    for step in steps:
        count = reached[step]
        values = durations[step]
        step_metrics.append({
            "step": step,
            "entered_count": count,
            "step_conversion_rate": count / previous if previous else None,
            "overall_conversion_rate": count / total if total else None,
            "absolute_dropoff_count": max(previous - count, 0),
            "error_task_count": len(step_errors[step]),
            "error_task_rate": len(step_errors[step]) / count if count else None,
            "duration_seconds": {"p50": percentile(values, .5), "p70": percentile(values, .7), "p90": percentile(values, .9)},
        })
        previous = count

    inference_config = contract.get("statistical_inference", {})
    inference_requested = inference_config.get("enabled") is True
    minimum_inference_sample = int(inference_config.get("minimum_sample", 30))
    same_depth = []
    for depth in sorted(set(task_depth.values())):
        members = {key for key, value in task_depth.items() if value == depth}
        with_error, without_error = members & errored, members - errored
        comparison = {
            "depth": depth,
            "with_error": _completion_summary(with_error, completed, completion_evaluable),
            "without_error": _completion_summary(without_error, completed, completion_evaluable),
            "relationship": "correlational_only",
        }
        if (
            completion_evaluable
            and inference_requested
            and len(with_error) >= minimum_inference_sample
            and len(without_error) >= minimum_inference_sample
        ):
            comparison["completion_rate_difference_interval"] = (
                proportion_difference_interval(
                    len(with_error & completed),
                    len(with_error),
                    len(without_error & completed),
                    len(without_error),
                )
            )
        elif inference_requested:
            comparison["inference_status"] = "not_evaluable"
            comparison["inference_reason"] = "minimum_group_sample_not_met"
        same_depth.append(comparison)

    completion_reason = (
        "completion_signal_conflict"
        if completion_conflicts
        else "completion_signal_unavailable"
    )
    metrics = {
        "status": "completed" if total and completion_evaluable else "not_evaluable",
        **({"reason": completion_reason} if total and not completion_evaluable else {}),
        "task_instance_count": total,
        "completion_count": len(completed) if completion_evaluable else None,
        "completion_rate": len(completed) / total if total and completion_evaluable else None,
        "one_time_completion_count": len(one_time) if completion_evaluable else None,
        "one_time_completion_rate": len(one_time) / total if total and completion_evaluable else None,
        "error_task_count": len(errored),
        "error_task_rate": len(errored) / total if total else None,
        "draft_task_count": len(drafted),
        "draft_rate": len(drafted) / total if total else None,
        "exit_task_count": len(exited),
        "exit_rate": len(exited) / total if total else None,
        "task_duration_seconds": {"p50": percentile(task_durations, .5), "p70": percentile(task_durations, .7), "p90": percentile(task_durations, .9)},
        "reliability": {
            "sample_size": total,
            "completion_evaluable": completion_evaluable,
            "completion_basis": (
                "declared_event_semantics"
                if event_completion_declared
                else "explicit_task_flags"
                if all_tasks_explicit
                else "unavailable"
            ),
            "completion_conflict_count": len(completion_conflicts),
            "inference_performed": False,
        },
        "limitations": [completion_reason] if total and not completion_evaluable else [],
    }
    proportion_intervals: dict[str, Any] = {}
    if completion_evaluable and inference_requested and total >= minimum_inference_sample:
        proportion_intervals = {
            "completion_rate": wilson_interval(len(completed), total),
            "error_task_rate": wilson_interval(len(errored), total),
        }
    largest = max(step_metrics, key=lambda item: item["absolute_dropoff_count"], default=None)
    return {
        "status": "completed" if total and completion_evaluable else "completed_with_caveats" if total else "not_evaluable",
        "metrics": metrics,
        "funnel": {
            "status": "completed" if total and steps else "not_evaluable",
            "definition": {"steps": steps, "grain": "task_instance", "ordering": "first_ordered_occurrence"},
            "steps": step_metrics,
            "largest_dropoff": largest,
            "same_depth_error_comparison": same_depth,
            "unmapped_error_task_count": len(unmapped_error_tasks),
            "reliability": {
                "sample_size": total,
                "step_mapping_coverage": (len(errored - unmapped_error_tasks) / len(errored)) if errored else 1.0,
                "inference_performed": bool(
                    inference_requested
                    and any(
                        item.get("completion_rate_difference_interval")
                        for item in same_depth
                    )
                ),
            },
        },
        "reliability": {
            "statistical_mode": "descriptive_default",
            "sample_size": total,
            "impact_scale_required": True,
            "inference_requested": inference_requested,
            "inference_performed": bool(proportion_intervals),
            "inference_status": (
                "completed"
                if proportion_intervals
                else ("not_evaluable" if inference_requested else "not_requested")
            ),
            "inference_reason": (
                None
                if proportion_intervals or not inference_requested
                else "minimum_sample_not_met"
            ),
            "proportion_intervals": proportion_intervals,
        },
    }


def _completion_summary(
    members: set[str], completed: set[str], evaluable: bool = True
) -> dict[str, Any]:
    if not evaluable:
        return {
            "task_count": len(members),
            "completion_count": None,
            "completion_rate": None,
            "status": "not_evaluable",
            "reason": "completion_signal_unavailable",
        }
    count = len(members & completed)
    return {"task_count": len(members), "completion_count": count, "completion_rate": count / len(members) if members else None}


def _matches(row: dict[str, Any], conditions: list[dict[str, Any]]) -> bool:
    for condition in conditions:
        actual = row.get(condition.get("field"))
        operation = condition.get("op", "eq")
        if operation == "eq" and str(actual) != str(condition.get("value")):
            return False
        if operation == "in" and actual not in condition.get("values", []):
            return False
        if operation == "not_empty" and actual in (None, ""):
            return False
        if operation == "contains" and str(condition.get("value")) not in str(actual or ""):
            return False
    return True


def analyze_segments(rows: list[dict[str, Any]], definitions: list[dict[str, Any]], minimum_sample: int = 30) -> dict[str, Any]:
    if not definitions:
        return {"status": "not_evaluable", "reason": "confirmed_business_segment_definitions_missing", "segments": []}
    grouped_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    task_classes: dict[str, set[str]] = defaultdict(set)
    task_completion: dict[str, bool | None] = {}
    for row in rows:
        task = str(row.get("task_instance_id") or row.get("session_id") or "")
        if task:
            grouped_rows[task].append(row)
            task_classes[task].add(str(row.get("event_class") or ""))
            explicit = _as_bool(row.get("completion_flag"))
            if explicit is not None:
                if task in task_completion and task_completion[task] != explicit:
                    task_completion[task] = None
                else:
                    task_completion[task] = explicit
    fields = sorted({str(condition.get("field")) for definition in definitions for condition in definition.get("conditions", []) if condition.get("field")})
    representatives: dict[str, dict[str, Any]] = {}
    field_conflict_tasks: set[str] = set()
    for task, task_rows in grouped_rows.items():
        representative: dict[str, Any] = {}
        resolution = str(next((item.get("task_field_resolution") for item in definitions if item.get("task_field_resolution")), "require_consistent"))
        for field in fields:
            values = [row.get(field) for row in task_rows if row.get(field) not in (None, "")]
            unique = list(dict.fromkeys(str(value) for value in values))
            if len(unique) > 1 and resolution == "require_consistent":
                field_conflict_tasks.add(task)
                representative[field] = ""
            elif values:
                representative[field] = values[-1] if resolution == "last_non_empty" else values[0]
        representatives[task] = representative
    assignments: dict[str, list[str]] = defaultdict(list)
    overlap_count = 0
    overlapping_tasks: list[str] = []
    for task, row in representatives.items():
        matches = [definition for definition in definitions if _matches(row, definition.get("conditions", []))]
        if len(matches) > 1:
            overlap_count += 1
            overlapping_tasks.append(task)
        label = str((matches[0].get("label") or matches[0].get("segment_id")) if matches else "UNKNOWN")
        assignments[label].append(task)
    if overlap_count:
        return {
            "status": "not_evaluable",
            "reason": "segment_rules_not_mutually_exclusive",
            "mode": "controlled_business_rules",
            "rule_sources": sorted({str(item.get("basis", {}).get("source") or "") for item in definitions}),
            "mutually_exclusive": False,
            "overlap_task_count": overlap_count,
            "overlap_task_refs": overlapping_tasks[:20],
            "unknown_bucket": True,
            "minimum_sample": minimum_sample,
            "definitions": definitions,
            "segments": [],
            "limitations": ["segment_rules_overlap; comparable segment conclusions are blocked"],
            "reliability": {"sample_size": len(representatives), "rule_confirmation_state": "confirmed", "inference_performed": False},
        }
    segments = []
    for label, tasks in sorted(assignments.items()):
        complete = sum(
            task_completion.get(task) is True
            or (
                task_completion.get(task) is None
                and "success_event" in task_classes[task]
            )
            for task in tasks
        )
        segments.append({
            "label": label,
            "sample_size": len(tasks),
            "share": len(tasks) / len(representatives) if representatives else None,
            "completion_count": complete,
            "completion_rate": complete / len(tasks) if tasks else None,
            "sample_status": "sufficient" if len(tasks) >= minimum_sample else "low_sample_risk",
        })
    assigned = sum(len(tasks) for tasks in assignments.values())
    global_complete = sum(
        task_completion.get(task) is True
        or (
            task_completion.get(task) is None
            and "success_event" in task_classes[task]
        )
        for task in representatives
    )
    segment_complete = sum(item["completion_count"] for item in segments)
    comparable = [item for item in segments if item["label"] != "UNKNOWN" and item["sample_status"] == "sufficient"]
    return {
        "status": "completed" if representatives else "not_evaluable",
        "mode": "controlled_business_rules",
        "rule_sources": sorted({str(item.get("basis", {}).get("source") or "confirmed_business_rule") for item in definitions}),
        "mutually_exclusive": overlap_count == 0,
        "overlap_task_count": overlap_count,
        "unknown_bucket": True,
        "minimum_sample": minimum_sample,
        "definitions": definitions,
        "segments": segments,
        "reconciliation": {
            "task_count": len(representatives),
            "assigned_task_count": assigned,
            "global_completion_count": global_complete,
            "segment_completion_count": segment_complete,
            "balanced": assigned == len(representatives) and segment_complete == global_complete,
        },
        "comparison_evaluable": len(comparable) >= 2,
        "field_conflict_task_count": len(field_conflict_tasks),
        "reliability": {
            "sample_size": len(representatives),
            "low_sample_segment_count": sum(item["sample_status"] == "low_sample_risk" for item in segments),
            "rule_confirmation_state": "confirmed",
            "inference_performed": False,
        },
        "limitations": (
            (["segment_field_values_conflicted_within_task"] if field_conflict_tasks else [])
            + ([] if len(comparable) >= 2 else ["fewer_than_two_sufficient_business_segments; comparison not performed"])
        ),
    }


def analyze_feature_usage(rows: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    required = [config.get("subject_col"), config.get("entry_event"), config.get("usage_event")]
    if not all(required):
        return {"status": "not_evaluable", "reason": "feature_config_incomplete", "usage_metrics": []}
    subject_col = str(config["subject_col"])
    event_col = str(config.get("event_col", "event_name"))
    valid = [row for row in rows if row.get(subject_col)]
    subjects = lambda event: {str(row[subject_col]) for row in valid if row.get(event_col) == event}
    entry, usage = subjects(config["entry_event"]), subjects(config["usage_event"])
    metrics = [_rate("entry_to_usage", usage, entry)]
    populations = [{"population": "entry", "subject_count": len(entry)}, {"population": "usage", "subject_count": len(usage)}]
    if config.get("exposure_event"):
        metrics.append(_rate("exposure_to_usage", usage, subjects(config["exposure_event"])))
    if config.get("completion_event"):
        metrics.append(_rate("usage_to_completion", subjects(config["completion_event"]), usage))
    eligibility = config.get("eligibility", {})
    eligible: set[str] = set()
    if eligibility.get("event"):
        eligible = subjects(eligibility["event"])
    elif eligibility.get("subject_ids"):
        eligible = {str(value) for value in eligibility["subject_ids"]}
    elif eligibility.get("conditions"):
        eligible = {str(row[subject_col]) for row in valid if _matches(row, eligibility["conditions"])}
    if eligible:
        metrics.append(_rate("eligible_to_usage", usage, eligible))
        populations.append({"population": "eligible", "subject_count": len(eligible)})
    return {
        "status": "completed" if entry else "not_evaluable",
        **({"reason": "feature_entry_population_empty"} if not entry else {}),
        "grain": subject_col,
        "definition": {key: config.get(key) for key in ("entry_event", "usage_event", "exposure_event", "completion_event")},
        "populations": populations,
        "usage_metrics": metrics,
        "eligibility_status": "evaluated" if eligible else "not_requested" if not eligibility else "not_evaluable",
        "reliability": {"sample_size": len(entry), "subject_coverage": len(valid), "inference_performed": False},
        "limitations": ["eligibility_definition_did_not_resolve_subjects"] if eligibility and not eligible else [],
    }


def _rate(metric_id: str, numerator: set[str], denominator: set[str]) -> dict[str, Any]:
    matched = numerator & denominator
    return {"metric_id": metric_id, "numerator": len(matched), "denominator": len(denominator), "value": len(matched) / len(denominator) if denominator else None}
