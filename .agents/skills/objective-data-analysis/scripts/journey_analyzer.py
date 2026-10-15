#!/usr/bin/env python3
"""Analyze observed task paths and emit reconciled Sankey-ready structures."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import timezone
from typing import Any

from time_parsing import parse_time

def time_sort_key(value: Any) -> tuple[int, float, str]:
    parsed = parse_time(value)
    raw = str(value or "")
    if parsed is None:
        return (1, 0.0, raw)
    if parsed.tzinfo is None:
        return (0, parsed.replace(tzinfo=timezone.utc).timestamp(), raw)
    return (0, parsed.timestamp(), raw)


def _collapse(sequence: list[str]) -> list[str]:
    output: list[str] = []
    for value in sequence:
        if value and (not output or output[-1] != value):
            output.append(value)
    return output


def _as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and float(value) in {0, 1}:
        return bool(value)
    text = str(value or "").strip().lower()
    if text in {"1", "1.0", "true", "yes", "y", "是", "完成", "成功"}:
        return True
    if text in {"0", "0.0", "false", "no", "n", "否", "未完成", "失败"}:
        return False
    return None


def _positive_number(value: Any) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def _number(value: Any) -> float | None:
    try:
        number = float(value)
        return number if number >= 0 else None
    except (TypeError, ValueError):
        return None


def _percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    low, high = int(index), min(int(index) + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (index - low)


def _matches(row: dict[str, Any], conditions: list[dict[str, Any]]) -> bool:
    for condition in conditions:
        actual, operation = row.get(condition.get("field")), condition.get("op", "eq")
        if operation == "eq" and str(actual) != str(condition.get("value")):
            return False
        if operation == "in" and actual not in condition.get("values", []):
            return False
        if operation == "not_empty" and actual in (None, ""):
            return False
        if operation == "contains" and str(condition.get("value")) not in str(actual or ""):
            return False
    return True


def _select_blueprint(
    context: dict[str, Any],
    expected_steps: list[str],
    blueprints: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if blueprints:
        matches = [
            item for item in blueprints
            if _matches(context, item.get("applicability_conditions", []))
        ]
        return matches[0] if len(matches) == 1 else None
    if expected_steps:
        return {
            "blueprint_id": "linear-expected-steps",
            "required_steps": expected_steps,
            "optional_steps": [],
            "alternative_step_groups": [],
            "allowed_terminals": [],
        }
    return None


def compile_business_blueprints(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Compile registered journey nodes without treating row order as business order."""
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        journey_name = str(row.get("journey_name") or "").strip()
        node = str(row.get("registered_node_name") or "").strip()
        if not journey_name or not node:
            continue
        grouped[
            (
                str(row.get("business_scenario") or "").strip(),
                str(row.get("sub_business_scenario") or "").strip(),
                journey_name,
            )
        ].append(row)
    definitions: list[dict[str, Any]] = []
    formal_blueprints: list[dict[str, Any]] = []
    for (scenario, sub_scenario, journey_name), items in grouped.items():
        nodes = list(
            dict.fromkeys(
                str(item.get("registered_node_name") or "").strip()
                for item in items
                if item.get("registered_node_name")
            )
        )
        orders = [_number(item.get("registered_node_order")) for item in items]
        has_formal_order = bool(items) and all(value is not None for value in orders)
        unique_order = has_formal_order and len(set(orders)) == len(orders)
        authority = {
            str(item.get("_blueprint_authority") or "") for item in items
        } - {""}
        formal = unique_order and authority <= {"formal", "user_confirmed", "business_confirmed"}
        ordered_nodes = [
            str(item.get("registered_node_name"))
            for _, item in sorted(zip(orders, items), key=lambda pair: pair[0])
        ] if unique_order else []
        definition = {
            "definition_id": f"registered:{scenario}:{sub_scenario}:{journey_name}",
            "business_scenario": scenario or None,
            "sub_business_scenario": sub_scenario or None,
            "journey_name": journey_name,
            "registered_nodes": nodes,
            "definition_status": "formal" if formal else "registered_nodes_only",
            "order_status": "explicit_complete" if unique_order else "unavailable",
            "allowed_terminals_status": "unavailable",
            "basis": {
                "source": "business_blueprint_input",
                "authority": sorted(authority) or ["unspecified"],
            },
        }
        definitions.append(definition)
        if formal:
            formal_blueprints.append({
                "blueprint_id": definition["definition_id"],
                "label": journey_name,
                "applicability_conditions": [],
                "required_steps": ordered_nodes,
                "optional_steps": [],
                "alternative_step_groups": [],
                "allowed_terminals": [],
                "basis": {
                    "source": "business_config",
                    "ref": definition["definition_id"],
                    "confirmation_status": "confirmed",
                },
            })
    statuses = {item["definition_status"] for item in definitions}
    return {
        "status": "completed" if definitions else "not_evaluable",
        **({"reason": "business_blueprint_rows_unavailable"} if not definitions else {}),
        "definitions": definitions,
        "formal_blueprints": formal_blueprints,
        "definition_status": (
            next(iter(statuses)) if len(statuses) == 1
            else "mixed" if statuses
            else "unavailable"
        ),
        "limitations": (
            []
            if definitions and len(formal_blueprints) == len(definitions)
            else [
                "registered nodes without explicit confirmed order remain reference nodes; blueprint deviation is not evaluated"
            ]
            if definitions
            else []
        ),
    }


def _analyze_records(
    records: list[dict[str, Any]],
    *,
    expected_steps: list[str] | None = None,
    journey_blueprints: list[dict[str, Any]] | None = None,
    source_semantic_type: str,
) -> dict[str, Any]:
    paths: Counter[tuple[str, ...]] = Counter()
    path_events: Counter[tuple[str, ...]] = Counter()
    successful: Counter[tuple[str, ...]] = Counter()
    unsuccessful: Counter[tuple[str, ...]] = Counter()
    error_cohort: Counter[tuple[str, ...]] = Counter()
    no_error_cohort: Counter[tuple[str, ...]] = Counter()
    node_tasks: dict[str, set[str]] = defaultdict(set)
    node_events: Counter[str] = Counter()
    node_durations: dict[str, list[float]] = defaultdict(list)
    node_error_tasks: dict[str, set[str]] = defaultdict(set)
    transition_tasks: dict[tuple[str, str], set[str]] = defaultdict(set)
    transition_events: Counter[tuple[str, str]] = Counter()
    transition_durations: dict[tuple[str, str], list[float]] = defaultdict(list)
    path_durations: dict[tuple[str, ...], list[float]] = defaultdict(list)
    terminal: Counter[str] = Counter()
    loops: Counter[str] = Counter()
    error_after: Counter[str] = Counter()
    deviations: Counter[str] = Counter()
    exit_nodes: Counter[tuple[str, str]] = Counter()
    blueprint_matches = 0
    expected_steps = expected_steps or []
    journey_blueprints = journey_blueprints or []
    for record in records:
        key = str(record["task_key"])
        raw_steps = [str(value) for value in record.get("raw_steps", []) if value]
        steps = _collapse(raw_steps)
        path = tuple(steps)
        paths[path] += 1
        path_events[path] += len(raw_steps)
        task_duration = _number(record.get("task_duration_seconds"))
        if task_duration is not None:
            path_durations[path].append(task_duration)
        classes = [str(value) for value in record.get("classes", [])]
        success = bool(record.get("success"))
        (successful if success else unsuccessful)[path] += 1
        (error_cohort if record.get("has_error") else no_error_cohort)[path] += 1
        for step in raw_steps:
            node_tasks[step].add(key)
            node_events[step] += 1
        for step, duration in record.get("step_durations", []):
            numeric = _number(duration)
            if step and numeric is not None:
                node_durations[str(step)].append(numeric)
        for step in record.get("error_steps", []):
            if step:
                node_error_tasks[str(step)].add(key)
        for source, target in zip(steps, steps[1:]):
            transition_tasks[(source, target)].add(key)
            transition_events[(source, target)] += 1
        for source, target, duration in record.get("transition_durations", []):
            numeric = _number(duration)
            if source and target and numeric is not None:
                transition_durations[(str(source), str(target))].append(numeric)
        if success:
            outcome = "success"
        elif record.get("draft"):
            outcome = "draft"
        elif record.get("exit"):
            outcome = "exit"
        elif record.get("last_is_error"):
            outcome = "error_without_observed_followup"
        elif record.get("completion_known") is False:
            outcome = "incomplete_or_tracking_ended"
        else:
            outcome = "unknown"
        terminal[outcome] += 1
        if not success and steps:
            exit_nodes[(steps[-1], outcome)] += 1
        for index in range(len(steps) - 2):
            if steps[index] == steps[index + 2] and steps[index] != steps[index + 1]:
                loops[f"{steps[index]}->{steps[index + 1]}->{steps[index + 2]}"] += 1
        for next_class in record.get("error_after", []):
            error_after[str(next_class)] += 1
        blueprint = _select_blueprint(record.get("context", {}), expected_steps, journey_blueprints)
        if blueprint:
            blueprint_matches += 1
            required = [str(value) for value in blueprint.get("required_steps", [])]
            optional = {str(value) for value in blueprint.get("optional_steps", [])}
            alternatives = [
                {str(value) for value in group}
                for group in blueprint.get("alternative_step_groups", [])
            ]
            allowed = set(required) | optional | set().union(*alternatives) if alternatives else set(required) | optional
            if any(step not in allowed for step in steps):
                deviations["detour"] += 1
            if any(step not in steps for step in required):
                deviations["missing_required_step"] += 1
            order = {step: index for index, step in enumerate(required)}
            comparable = [step for step in steps if step in order]
            if any(order[left] > order[right] for left, right in zip(comparable, comparable[1:])):
                deviations["out_of_order_or_backtrack"] += 1
            if len(set(raw_steps)) < len(raw_steps):
                deviations["repeated_step"] += 1
            allowed_terminals = {str(value) for value in blueprint.get("allowed_terminals", [])}
            if allowed_terminals and steps and steps[-1] not in allowed_terminals:
                deviations["unexpected_terminal"] += 1
    total = len(records)
    nodes = [
        {
            "node_id": step,
            "label": step,
            "task_count": len(tasks),
            "event_count": node_events[step],
            "share_of_total_tasks": len(tasks) / total if total else None,
            "duration_seconds": {
                "p50": _percentile(node_durations[step], .5),
                "p70": _percentile(node_durations[step], .7),
                "p90": _percentile(node_durations[step], .9),
            },
            "error_task_count": len(node_error_tasks[step]),
            "error_task_share": len(node_error_tasks[step]) / len(tasks) if tasks else None,
        }
        for step, tasks in sorted(node_tasks.items(), key=lambda item: (-len(item[1]), item[0]))
    ]
    outgoing_total, incoming_total = Counter(), Counter()
    for pair, tasks in transition_tasks.items():
        outgoing_total[pair[0]] += len(tasks)
        incoming_total[pair[1]] += len(tasks)
    links = [{
        "source": source,
        "target": target,
        "task_count": len(tasks),
        "transition_event_count": transition_events[(source, target)],
        "share_of_total_tasks": len(tasks) / total if total else None,
        "share_of_source_outflow": len(tasks) / outgoing_total[source] if outgoing_total[source] else None,
        "share_of_target_inflow": len(tasks) / incoming_total[target] if incoming_total[target] else None,
        "duration_seconds": {
            "p50": _percentile(transition_durations[(source, target)], .5),
            "p70": _percentile(transition_durations[(source, target)], .7),
            "p90": _percentile(transition_durations[(source, target)], .9),
        },
    } for (source, target), tasks in sorted(transition_tasks.items(), key=lambda item: (-len(item[1]), item[0]))]
    terminal_outcomes = [
        {"outcome": name, "task_count": count, "share": count / total if total else None}
        for name, count in terminal.most_common()
    ]
    def path_facts(counter: Counter[tuple[str, ...]], limit: int | None = None) -> list[dict[str, Any]]:
        ordered = counter.most_common(limit)
        return [
            {
                "path": list(key),
                "task_count": count,
                "event_count": path_events[key],
                "share": count / total if total else None,
                "duration_seconds": {
                    "p50": _percentile(path_durations[key], .5),
                    "p70": _percentile(path_durations[key], .7),
                    "p90": _percentile(path_durations[key], .9),
                },
            }
            for key, count in ordered
        ]
    top = lambda counter: path_facts(counter, 20)
    inferred_candidate = (
        {
            **path_facts(paths, 1)[0],
            "status": "candidate",
            "allowed_use": "observed_reference_only",
            "forbidden_uses": ["formal_ideal_path", "blueprint_deviation_baseline"],
        }
        if paths
        else None
    )
    return {
        "status": "completed" if total else "not_evaluable",
        **({"reason": "journey_records_unavailable"} if not total else {}),
        "source_semantic_type": source_semantic_type,
        "journey_definition": {
            "grain": "task_instance",
            "terminal_rule": "explicit_completion_then_draft_then_exit_then_error_followup_then_incomplete_or_unknown",
        },
        "task_instance_count": total,
        "path_construction_rules": {"grain": "task_instance", "collapse_consecutive_duplicate_steps": True},
        "path_patterns": path_facts(paths),
        "top_path_patterns": top(paths),
        "inferred_reference_path_candidate": inferred_candidate,
        "success_and_failure_paths": {"success": top(successful), "non_success": top(unsuccessful)},
        "error_cohort_paths": {"with_error": top(error_cohort), "without_error": top(no_error_cohort)},
        "backtrack_and_loop_paths": [{"path": path, "task_count": count} for path, count in loops.most_common(20)],
        "error_after_behavior_paths": [{"next_event_class": name, "event_count": count} for name, count in error_after.most_common()],
        "blueprint_deviations": [{"type": name, "task_count": count} for name, count in deviations.most_common()],
        "stage_nodes": nodes,
        "stage_transitions": links,
        "terminal_outcomes": terminal_outcomes,
        "exit_points": [
            {
                "node_id": node,
                "outcome": outcome,
                "task_count": count,
                "share_of_total_tasks": count / total if total else None,
            }
            for (node, outcome), count in exit_nodes.most_common()
        ],
        "segment_journey_comparisons": [],
        "reconciliation": {"task_instance_count": total, "terminal_outcome_count": sum(terminal.values()), "balanced": total == sum(terminal.values())},
        "reliability": {
            "sample_size": total,
            "journey_definition_status": (
                "formal_matched"
                if blueprint_matches == total and total > 0
                else "partially_matched"
                if blueprint_matches
                else "observed_only"
            ),
            "blueprint_coverage": blueprint_matches / total if total else None,
            "inference_performed": False,
        },
        "limitations": [] if blueprint_matches == total and total else ["confirmed journey blueprint unavailable for part or all of the cohort; deviation analysis was limited"],
    }


def analyze_rows(
    rows: list[dict[str, Any]],
    *,
    task_col: str = "task_instance_id",
    session_col: str = "session_id",
    step_col: str = "journey_step",
    class_col: str = "event_class",
    time_col: str = "event_time",
    order_col: str = "journey_step_order",
    expected_steps: list[str] | None = None,
    journey_blueprints: list[dict[str, Any]] | None = None,
    error_task_ids: set[str] | None = None,
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = str(row.get(task_col) or row.get(session_col) or "")
        if key:
            grouped[key].append(row)
    records = []
    error_task_ids = error_task_ids or set()
    for key, events in grouped.items():
        has_explicit_order = all(
            row.get(order_col) not in (None, "") for row in events
        )
        events.sort(
            key=(
                (lambda row: (_number(row.get(order_col)) if _number(row.get(order_col)) is not None else float("inf")))
                if has_explicit_order
                else (lambda row: time_sort_key(row.get(time_col)))
            )
        )
        classes = [str(row.get(class_col) or "") for row in events]
        parsed_times = [parse_time(row.get(time_col)) for row in events]
        valid_times = [value for value in parsed_times if value is not None]
        transition_duration_rows: list[tuple[str, str, float]] = []
        for left, right, left_time, right_time in zip(
            events,
            events[1:],
            parsed_times,
            parsed_times[1:],
        ):
            source = str(left.get(step_col) or "")
            target = str(right.get(step_col) or "")
            if source and target and left_time and right_time:
                transition_duration_rows.append(
                    (source, target, max(0.0, (right_time - left_time).total_seconds()))
                )
        records.append({
            "task_key": key,
            "raw_steps": [str(row.get(step_col) or "") for row in events if row.get(step_col)],
            "step_durations": [
                (str(row.get(step_col) or ""), row.get("journey_step_duration_seconds"))
                for row in events
                if row.get(step_col)
            ],
            "transition_durations": transition_duration_rows,
            "task_duration_seconds": (
                max(0.0, (valid_times[-1] - valid_times[0]).total_seconds())
                if len(valid_times) >= 2
                else None
            ),
            "error_steps": [
                str(row.get(step_col) or "")
                for row in events
                if row.get(class_col) == "error_event"
            ],
            "classes": classes,
            "success": "success_event" in classes,
            "completion_known": "success_event" in classes,
            "draft": "draft_event" in classes,
            "exit": "exit_event" in classes,
            "last_is_error": bool(classes and classes[-1] == "error_event"),
            "has_error": key in error_task_ids or "error_event" in classes,
            "error_after": [
                str(events[index + 1].get(class_col) or "step_event") if index + 1 < len(events) else "NO_FOLLOWUP"
                for index, event in enumerate(events)
                if event.get(class_col) == "error_event"
            ],
            "context": events[0] if events else {},
        })
    result = _analyze_records(
        records,
        expected_steps=expected_steps,
        journey_blueprints=journey_blueprints,
        source_semantic_type="journey_node_detail_or_general_event_log",
    )
    result.setdefault("path_construction_rules", {})["sort"] = (
        "explicit_node_order_ascending"
        if rows and all(row.get(order_col) not in (None, "") for row in rows)
        else "event_time_ascending"
    )
    result["reliability"]["step_mapping_coverage"] = sum(bool(row.get(step_col)) for row in rows) / len(rows) if rows else None
    return result


def analyze_task_summaries(
    rows: list[dict[str, Any]],
    *,
    delimiter: str,
    expected_steps: list[str] | None = None,
    journey_blueprints: list[dict[str, Any]] | None = None,
    error_task_ids: set[str] | None = None,
) -> dict[str, Any]:
    records = []
    error_task_ids = error_task_ids or set()
    for row in rows:
        task = str(row.get("task_instance_id") or "")
        raw_path = str(row.get("journey_path") or "")
        if not task or not raw_path:
            continue
        completed = _as_bool(row.get("completion_flag"))
        records.append({
            "task_key": task,
            "raw_steps": [part.strip() for part in raw_path.split(delimiter) if part.strip()],
            "step_durations": [],
            "transition_durations": [],
            "task_duration_seconds": row.get("task_duration_seconds_normalized"),
            "error_steps": [],
            "classes": [],
            "success": completed is True,
            "completion_known": completed,
            "draft": False,
            "exit": False,
            "last_is_error": False,
            "has_error": task in error_task_ids or _positive_number(row.get("task_error_count")),
            "error_after": [],
            "context": row,
        })
    return _analyze_records(
        records,
        expected_steps=expected_steps,
        journey_blueprints=journey_blueprints,
        source_semantic_type="task_summary",
    )
