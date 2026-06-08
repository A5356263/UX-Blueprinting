from __future__ import annotations

import re
from pathlib import Path

from packages.common import get_project_source_dir


REQUIRED_SECTIONS = {
    "## Protocol",
    "## Required Inputs",
    "## Required Outputs",
    "## Constraints",
    "## Templates",
    "## Checks",
}

REFERENCE_SECTIONS = {
    "## Templates": "template_refs",
    "## Checks": "check_refs",
}

IGNORED_LEGACY_SECTIONS = {
    "## Knowledge",
    "## Wiki",
    "## Design Guidelines",
    "## Knowledge Consumption Policy",
}

DISALLOWED_LEGACY_SECTIONS = {
    "## Task Goal",
    "## Task Scenario",
    "## Read Order",
    "## Notes",
    "## Platform Optimizations",
    "## Result Locations",
    "## Completion Criteria",
    "## Facts Output Requirements",
    "## Business Output Requirements",
    "## Experience Output Requirements",
}


def split_kv(value: str) -> tuple[str, str]:
    for separator in ("：", ":"):
        if separator in value:
            left, right = value.split(separator, 1)
            return left.strip(), right.strip()
    return value.strip(), ""


def parse_sections(task_card_text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_section = ""
    for raw_line in task_card_text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("## "):
            current_section = stripped
            sections.setdefault(current_section, [])
            continue
        if current_section:
            sections[current_section].append(raw_line.rstrip())
    return sections


def parse_bullets(lines: list[str]) -> list[str]:
    values: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            values.append(stripped[2:].strip())
    return values


def parse_text_items(lines: list[str]) -> list[str]:
    values: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            values.append(stripped[2:].strip())
            continue
        match = re.match(r"^\d+[\.、]\s*(.+)$", stripped)
        if match:
            values.append(match.group(1).strip())
    return values


def parse_protocol(lines: list[str]) -> dict[str, str]:
    protocol: dict[str, str] = {}
    for item in parse_bullets(lines):
        key, value = split_kv(item)
        if key:
            protocol[key] = value
    return protocol


def normalize_path_values(items: list[str]) -> list[str]:
    values: list[str] = []
    for item in items:
        key, value = split_kv(item)
        candidate = value or key
        if "/" in candidate:
            values.append(candidate.replace("\\", "/").strip())
    return values


def parse_raw_section_lines(lines: list[str]) -> list[str]:
    values: list[str] = []
    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped:
            values.append(stripped)
    return values


def resolve_task_card(task_card_text: str, task_id: str) -> dict[str, object]:
    sections = parse_sections(task_card_text)
    errors: list[str] = []
    warnings: list[str] = []
    recognized_sections = (
        REQUIRED_SECTIONS
        | set(REFERENCE_SECTIONS.keys())
        | DISALLOWED_LEGACY_SECTIONS
        | IGNORED_LEGACY_SECTIONS
    )

    missing_sections = sorted(section for section in REQUIRED_SECTIONS if section not in sections)
    for section in missing_sections:
        errors.append(f"Missing required section: {section}")
    for section in sorted(DISALLOWED_LEGACY_SECTIONS):
        if section in sections:
            errors.append(f"Legacy section is no longer allowed: {section}")

    protocol = parse_protocol(sections.get("## Protocol", []))
    protocol_name = protocol.get("Protocol Name", "")
    protocol_version = protocol.get("Protocol Version", "")
    parsed_task_id = protocol.get("Task ID", "")
    task_name = protocol.get("Task Name", "")
    domain = protocol.get("Domain", "")

    for key in ("Protocol Name", "Protocol Version", "Task ID"):
        if not protocol.get(key):
            errors.append(f"Missing protocol field: {key}")

    if parsed_task_id and parsed_task_id != task_id:
        errors.append(f"Task ID mismatch: expected {task_id}, got {parsed_task_id}")

    required_inputs = normalize_path_values(parse_bullets(sections.get("## Required Inputs", [])))
    required_outputs = normalize_path_values(parse_bullets(sections.get("## Required Outputs", [])))
    if not required_outputs:
        errors.append("Required Outputs is empty")

    workspace_prefix = f"projects/{task_id}/workspace/"
    for output in required_outputs:
        if not output.startswith(workspace_prefix):
            errors.append(f"Output path must stay under workspace: {output}")

    resolved: dict[str, object] = {
        "task_id": parsed_task_id or task_id,
        "protocol_name": protocol_name,
        "protocol_version": protocol_version,
        "task_name": task_name,
        "domain": domain,
        "execution_constraints": parse_text_items(sections.get("## Constraints", [])),
        "required_inputs": required_inputs,
        "required_outputs": required_outputs,
        "template_refs": [],
        "check_refs": [],
        "raw_sections": {
            section.replace("## ", "", 1): parse_raw_section_lines(lines)
            for section, lines in sections.items()
            if parse_raw_section_lines(lines)
        },
        "unparsed_sections": sorted(
            section.replace("## ", "", 1) for section in sections if section not in recognized_sections
        ),
        "result_locations": {},
        "completion_criteria": [],
        "facts_output_requirements": {},
        "business_output_requirements": {},
        "experience_output_requirements": {},
        "warnings": warnings,
        "errors": errors,
    }

    if not resolved["execution_constraints"]:
        errors.append("Constraints is empty or unparseable")

    for section, field in REFERENCE_SECTIONS.items():
        bullets = parse_bullets(sections.get(section, []))
        parsed_values = normalize_path_values(bullets)
        resolved[field] = parsed_values
        if section in sections and bullets and not parsed_values:
            errors.append(f"{section} exists but no valid paths were parsed")

    return resolved


def resolve_task_card_file(task_id: str) -> tuple[dict[str, object], Path]:
    source_dir = get_project_source_dir(task_id)
    task_card_path = source_dir / "task_card.md"

    if not task_card_path.exists():
        raise FileNotFoundError(f"Task card not found: {task_card_path}")
    task_card_text = task_card_path.read_text(encoding="utf-8")
    resolved = resolve_task_card(task_card_text, task_id)
    return resolved, task_card_path
