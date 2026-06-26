#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_FILES = (
    "journey_visual.md",
    "journey_visual.html",
    "journey_tracking_spec.md",
    "error_tracking_spec.md",
)

PLACEHOLDERS = ("待定", "TBD", "<TODO", "[TODO")


def fail(messages: list[str]) -> int:
    for message in messages:
        print(f"ERROR: {message}")
    return 1


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def table_rows_after_marker(text: str, marker: str) -> list[list[str]]:
    marker_pos = text.find(marker)
    if marker_pos < 0:
        return []
    rows: list[list[str]] = []
    for line in text[marker_pos:].splitlines()[1:]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if cells and not all(re.fullmatch(r"-+", cell or "-") for cell in cells):
                rows.append(cells)
    return rows


def extract_tracking_events(text: str) -> list[dict[str, str]]:
    events: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    field_map = {
        "taskNodeName": "taskNodeName",
        "节点描述": "node_description",
        "节点类型": "node_type",
        "所属任务": "task_name",
        "触发时机": "trigger_timing",
        "所属页面/模块": "page_module",
        "对应旅程节点": "journey_node_id",
        "来源": "source",
    }

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("| **taskNodeName**"):
            if current:
                events.append(current)
            current = {}
        if current is None or not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2:
            continue
        key = cells[0].replace("*", "").strip()
        value = cells[1].replace("`", "").strip()
        if key in field_map:
            current[field_map[key]] = value.strip("[]")

    if current:
        events.append(current)
    return events


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validate_journey_metrics.py <journey_metrics_dir>")
        return 2

    root = Path(argv[1])
    errors: list[str] = []

    if not root.is_dir():
        return fail([f"not a directory: {root}"])

    for name in REQUIRED_FILES:
        if not (root / name).exists():
            errors.append(f"missing required file: {name}")

    if errors:
        return fail(errors)

    visual = read(root / "journey_visual.md")
    visual_html = read(root / "journey_visual.html")
    tracking = read(root / "journey_tracking_spec.md")
    error_doc = read(root / "error_tracking_spec.md")
    all_text = "\n".join((visual, tracking, error_doc))

    for line_no, line in enumerate(all_text.splitlines(), start=1):
        if any(skip in line for skip in ("不得使用", "不得出现", "no `", "placeholder")):
            continue
        for placeholder in PLACEHOLDERS:
            if placeholder in line:
                errors.append(f"placeholder found on combined line {line_no}: {placeholder}")

    if "<html" not in visual_html.lower() or "</html>" not in visual_html.lower():
        errors.append("journey_visual.html does not look like a complete HTML document")

    appendix_rows = table_rows_after_marker(visual, "节点-埋点对照")
    if not appendix_rows:
        errors.append("journey_visual.md missing node-to-tracking appendix table")
    else:
        header = appendix_rows[0]
        required_header = ["节点标识", "节点名称", "角色", "来源", "节点类型", "关联 taskNodeName"]
        missing = [field for field in required_header if field not in header]
        if missing:
            errors.append(f"appendix table missing columns: {', '.join(missing)}")

    events = extract_tracking_events(tracking)
    if not events:
        errors.append("journey_tracking_spec.md contains no taskNodeName event blocks")
    for index, event in enumerate(events, start=1):
        for field in ("taskNodeName", "node_description", "node_type", "task_name", "trigger_timing", "page_module", "journey_node_id", "source"):
            if not event.get(field):
                errors.append(f"tracking event #{index} missing {field}")
        source = event.get("source", "")
        if source and source not in {"confirmed", "inferred", "conflict"}:
            errors.append(f"tracking event #{index} has invalid source: {source}")

    if errors:
        return fail(errors)

    print(f"OK: journey metrics artifacts validated: {root}")
    print(f"OK: tracking events parsed: {len(events)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
