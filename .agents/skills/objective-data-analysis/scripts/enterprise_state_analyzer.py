#!/usr/bin/env python3
"""Compile enterprise-state membership inputs into aggregate population facts."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any


STATE_LABELS = {
    "active": "月活",
    "deep_active": "深度月活",
    "retained": "存续",
}


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return float(value) > 0
    return str(value or "").strip().lower() in {
        "1",
        "1.0",
        "true",
        "yes",
        "y",
        "是",
        "有",
        "属于",
    }


def _period(value: Any) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    text = str(value or "").strip()
    return text[:10] if text else "UNKNOWN_PERIOD"


def _wide_retained_memberships(row: dict[str, Any]) -> list[tuple[str, str | None]]:
    output: list[tuple[str, str | None]] = []
    for field, value in row.items():
        label = str(field)
        if (
            label.startswith("是否")
            and label.endswith("存续")
            and _truthy(value)
            and not label.startswith("_")
        ):
            board = label.removeprefix("是否").removesuffix("存续")
            output.append(("retained", board or None))
    return output


def _row_memberships(row: dict[str, Any]) -> list[tuple[str, str | None]]:
    declared = str(row.get("_enterprise_state_type") or row.get("enterprise_state") or "")
    board = str(row.get("business_board") or "").strip() or None
    if declared:
        state = {
            "月活": "active",
            "深度月活": "deep_active",
            "存续": "retained",
        }.get(declared, declared)
        member = row.get("enterprise_state_member")
        return [(state, board)] if member in (None, "") or _truthy(member) else []
    return _wide_retained_memberships(row)


def _count_memberships(
    members: dict[tuple[str, str, str | None], set[str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    overall: dict[tuple[str, str], set[str]] = defaultdict(set)
    for (period, state, board), enterprises in members.items():
        overall[(period, state)].update(enterprises)
    snapshots = [
        {
            "period": period,
            "state": state,
            "state_label": STATE_LABELS.get(state, state),
            "enterprise_count": len(enterprises),
            "measurement_scope": {
                "grain": "enterprise",
                "period": period,
                "business_board": None,
            },
        }
        for (period, state), enterprises in sorted(overall.items())
    ]
    board_snapshots = [
        {
            "period": period,
            "state": state,
            "state_label": STATE_LABELS.get(state, state),
            "business_board": board,
            "enterprise_count": len(enterprises),
            "measurement_scope": {
                "grain": "enterprise_x_business_board",
                "period": period,
                "business_board": board,
            },
        }
        for (period, state, board), enterprises in sorted(
            members.items(), key=lambda item: tuple(str(value or "") for value in item[0])
        )
        if board
    ]
    return snapshots, board_snapshots


def _membership_changes(
    members: dict[tuple[str, str, str | None], set[str]],
) -> list[dict[str, Any]]:
    periods = sorted({period for period, _, _ in members})
    changes: list[dict[str, Any]] = []
    for start, end in zip(periods, periods[1:]):
        keys = {
            (state, board)
            for period, state, board in members
            if period in {start, end}
        }
        for state, board in sorted(keys, key=lambda item: tuple(str(value or "") for value in item)):
            before = members.get((start, state, board), set())
            after = members.get((end, state, board), set())
            scope = {
                "grain": "enterprise_x_business_board" if board else "enterprise",
                "period_start": start,
                "period_end": end,
                "business_board": board,
            }
            changes.extend(
                [
                    {
                        "period_start": start,
                        "period_end": end,
                        "state": state,
                        "state_label": STATE_LABELS.get(state, state),
                        "business_board": board,
                        "change_type": "entered",
                        "enterprise_count": len(after - before),
                        "measurement_scope": scope,
                    },
                    {
                        "period_start": start,
                        "period_end": end,
                        "state": state,
                        "state_label": STATE_LABELS.get(state, state),
                        "business_board": board,
                        "change_type": "exited",
                        "enterprise_count": len(before - after),
                        "measurement_scope": scope,
                    },
                    {
                        "period_start": start,
                        "period_end": end,
                        "state": state,
                        "state_label": STATE_LABELS.get(state, state),
                        "business_board": board,
                        "change_type": "persisted",
                        "enterprise_count": len(before & after),
                        "measurement_scope": scope,
                    },
                ]
            )
    return changes


def analyze(
    rows: list[dict[str, Any]],
    transition_rules: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    members: dict[tuple[str, str, str | None], set[str]] = defaultdict(set)
    source_rows = 0
    unmatched_rows = 0
    for row in rows:
        enterprise = str(row.get("enterprise_id") or "").strip()
        if not enterprise:
            unmatched_rows += 1
            continue
        source_rows += 1
        period = _period(row.get("statistics_date") or row.get("event_time"))
        memberships = _row_memberships(row)
        if not memberships:
            unmatched_rows += 1
        for state, board in memberships:
            members[(period, state, board)].add(enterprise)

    snapshots, board_snapshots = _count_memberships(members)
    changes = _membership_changes(members)
    periods = sorted({item["period"] for item in snapshots})
    limitations: list[str] = []
    if len(periods) < 2:
        limitations.append(
            "single_period_only; enterprise state changes and optimization attribution are not evaluable"
        )
    if not transition_rules:
        limitations.append(
            "formal state conversion rules unavailable; only membership snapshots and entered/exited/persisted changes are reported"
        )
    return {
        "status": "completed_with_caveats" if members and limitations else "completed" if members else "not_evaluable",
        **({"reason": "enterprise_state_membership_unavailable"} if not members else {}),
        "state_semantics": {
            "model": "membership_observation",
            "states_are_mutually_exclusive": False,
            "hierarchy_or_conversion_inferred": False,
            "transition_rules": transition_rules or [],
        },
        "enterprise_state_snapshots": snapshots,
        "enterprise_board_state_snapshots": board_snapshots,
        "state_membership_changes": changes,
        "population_facts": snapshots + board_snapshots + changes,
        "reconciliation": {
            "source_row_count": source_rows,
            "unmatched_row_count": unmatched_rows,
            "period_count": len(periods),
            "distinct_enterprise_count": len(set().union(*members.values())) if members else 0,
            "row_level_enterprise_ids_persisted": False,
        },
        "reliability": {
            "sample_size": len(set().union(*members.values())) if members else 0,
            "inference_performed": False,
        },
        "limitations": limitations,
    }
