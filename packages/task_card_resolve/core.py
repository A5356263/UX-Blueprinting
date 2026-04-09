from __future__ import annotations

import json
from pathlib import Path

from packages.common import get_project_runtime_dir, get_project_source_dir


REQUIRED_SECTIONS = {
    "## Protocol",
    "## Task Goal",
    "## Required Inputs",
    "## Required Outputs",
    "## Constraints",
    "## Templates",
    "## Checks",
    "## Result Locations",
    "## Completion Criteria",
    "## Facts Output Requirements",
    "## Business Output Requirements",
    "## Experience Output Requirements",
}

REFERENCE_SECTIONS = {
    "## Knowledge": "knowledge_refs",
    "## Wiki": "wiki_refs",
    "## Templates": "template_refs",
    "## Checks": "check_refs",
}

OUTPUT_REQUIREMENT_SECTIONS = {
    "## Facts Output Requirements": "facts_output_requirements",
    "## Business Output Requirements": "business_output_requirements",
    "## Experience Output Requirements": "experience_output_requirements",
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
            values.append(candidate)
    return values


def parse_output_requirements(lines: list[str]) -> dict[str, object]:
    by_subsection: dict[str, list[str]] = {}
    current = ""
    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped.startswith("### "):
            current = stripped
            by_subsection.setdefault(current, [])
            continue
        if current:
            by_subsection[current].append(raw_line)
    required_sections = parse_bullets(by_subsection.get("### Required Sections", []))
    recommended_id_prefixes = parse_bullets(by_subsection.get("### Recommended ID Prefixes", []))
    boundary_rules = parse_bullets(by_subsection.get("### Boundary", []))
    return {
        "required_sections": required_sections,
        "recommended_id_prefixes": recommended_id_prefixes,
        "boundary": boundary_rules,
    }


def resolve_task_card(task_card_text: str, task_id: str) -> dict[str, object]:
    sections = parse_sections(task_card_text)
    errors: list[str] = []
    warnings: list[str] = []

    missing_sections = sorted(section for section in REQUIRED_SECTIONS if section not in sections)
    for section in missing_sections:
        errors.append(f"Missing required section: {section}")

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
    result_locations = {
        key or f"location_{index + 1}": value
        for index, item in enumerate(parse_bullets(sections.get("## Result Locations", [])))
        for key, value in [split_kv(item)]
        if value
    }

    if not required_outputs:
        errors.append("Required Outputs is empty")

    workspace_prefix = f"projects/{task_id}/workspace/"
    for output in required_outputs:
        if not output.startswith(workspace_prefix):
            errors.append(f"Output path must stay under workspace: {output}")

    if not result_locations:
        errors.append("Result Locations is empty or unparseable")

    resolved: dict[str, object] = {
        "task_id": parsed_task_id or task_id,
        "protocol_name": protocol_name,
        "protocol_version": protocol_version,
        "task_name": task_name,
        "domain": domain,
        "required_inputs": required_inputs,
        "required_outputs": required_outputs,
        "knowledge_refs": [],
        "wiki_refs": [],
        "template_refs": [],
        "check_refs": [],
        "result_locations": result_locations,
        "completion_criteria": parse_bullets(sections.get("## Completion Criteria", [])),
        "facts_output_requirements": {},
        "business_output_requirements": {},
        "experience_output_requirements": {},
        "warnings": warnings,
        "errors": errors,
    }

    for section, field in REFERENCE_SECTIONS.items():
        bullets = parse_bullets(sections.get(section, []))
        parsed_values = normalize_path_values(bullets)
        resolved[field] = parsed_values
        if section in sections and bullets and not parsed_values:
            errors.append(f"{section} exists but no valid paths were parsed")

    for section, field in OUTPUT_REQUIREMENT_SECTIONS.items():
        parsed = parse_output_requirements(sections.get(section, []))
        resolved[field] = parsed
        if not parsed["required_sections"] or not parsed["boundary"]:
            errors.append(f"{section} is missing required subsections or bullet values")

    if not resolved["wiki_refs"] and resolved["knowledge_refs"]:
        warnings.append("Wiki section is missing or empty; execution will rely on Knowledge directly")
    if "## Read Order" not in sections:
        warnings.append("Read Order section is missing")
    if any(str(ref).endswith("/") for ref in resolved["knowledge_refs"]):
        warnings.append("Knowledge references include directory-only paths; consider narrowing to files or wiki indices")
    if "## Platform Optimizations" in sections and not parse_bullets(sections["## Platform Optimizations"]):
        warnings.append("Platform Optimizations section is present but empty")

    return resolved


def resolve_task_card_file(task_id: str, write_output: bool = True) -> tuple[dict[str, object], Path]:
    source_dir = get_project_source_dir(task_id)
    runtime_dir = get_project_runtime_dir(task_id)
    task_card_path = source_dir / "task_card.md"
    resolved_path = runtime_dir / "task_card_resolved.json"

    if not task_card_path.exists():
        raise FileNotFoundError(f"Task card not found: {task_card_path}")
    task_card_text = task_card_path.read_text(encoding="utf-8")
    resolved = resolve_task_card(task_card_text, task_id)

    if write_output:
        runtime_dir.mkdir(parents=True, exist_ok=True)
        resolved_path.write_text(json.dumps(resolved, ensure_ascii=False, indent=2), encoding="utf-8")

    return resolved, resolved_path
