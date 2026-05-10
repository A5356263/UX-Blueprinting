from __future__ import annotations

import json
import re
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
    "## Design Guidelines": "guideline_refs",
    "## Templates": "template_refs",
    "## Checks": "check_refs",
}

OUTPUT_REQUIREMENT_SECTIONS = {
    "## Facts Output Requirements": "facts_output_requirements",
    "## Business Output Requirements": "business_output_requirements",
    "## Experience Output Requirements": "experience_output_requirements",
}

POLICY_SUBSECTIONS = {
    "### Primary Knowledge Entry": "primary_knowledge_entries",
    "### Fallback Source": "fallback_source_refs",
    "### Fallback Conditions": "fallback_conditions",
    "### Disallowed Broad References": "disallowed_broad_references",
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
    return {
        "required_sections": parse_bullets(by_subsection.get("### Required Sections", [])),
        "recommended_id_prefixes": parse_bullets(by_subsection.get("### Recommended ID Prefixes", [])),
        "boundary": parse_bullets(by_subsection.get("### Boundary", [])),
    }


def parse_raw_section_lines(lines: list[str]) -> list[str]:
    values: list[str] = []
    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped:
            values.append(stripped)
    return values


def parse_policy_section(lines: list[str]) -> dict[str, object]:
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

    parsed: dict[str, object] = {field: [] for field in POLICY_SUBSECTIONS.values()}
    for heading, field in POLICY_SUBSECTIONS.items():
        bullet_values = parse_bullets(by_subsection.get(heading, []))
        if field.endswith("_refs") or field.endswith("_entries"):
            parsed[field] = normalize_path_values(bullet_values)
        else:
            parsed[field] = bullet_values
    return parsed


def classify_reference(reference: str) -> str:
    normalized = reference.replace("\\", "/").strip()
    if not normalized:
        return "missing"
    if "*" in normalized or "?" in normalized:
        return "pattern"
    if normalized.endswith("/"):
        return "directory"
    if normalized.endswith(".md"):
        file_name = Path(normalized).name.lower()
        if file_name in {"readme.md", "index.md"} or file_name.endswith("-index.md") or file_name.endswith("-domain-index.md"):
            return "index"
        return "file"
    if "." not in Path(normalized).name:
        return "directory"
    return "file"


def parse_reference_details(references: list[str]) -> list[dict[str, str]]:
    details: list[dict[str, str]] = []
    for reference in references:
        ref_type = classify_reference(reference)
        details.append(
            {
                "reference": reference,
                "kind": ref_type,
                "is_broad": "true" if ref_type in {"directory", "pattern"} else "false",
            }
        )
    return details


def resolve_task_card(task_card_text: str, task_id: str) -> dict[str, object]:
    sections = parse_sections(task_card_text)
    errors: list[str] = []
    warnings: list[str] = []
    recognized_sections = (
        REQUIRED_SECTIONS
        | set(REFERENCE_SECTIONS.keys())
        | set(OUTPUT_REQUIREMENT_SECTIONS.keys())
        | {"## Task Scenario", "## Read Order", "## Notes", "## Knowledge Consumption Policy", "## Platform Optimizations"}
    )

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
        "task_goal": parse_text_items(sections.get("## Task Goal", [])),
        "task_scenario": parse_text_items(sections.get("## Task Scenario", [])),
        "execution_constraints": parse_text_items(sections.get("## Constraints", [])),
        "read_order": parse_text_items(sections.get("## Read Order", [])),
        "notes": parse_text_items(sections.get("## Notes", [])),
        "required_inputs": required_inputs,
        "required_outputs": required_outputs,
        "knowledge_refs": [],
        "wiki_refs": [],
        "guideline_refs": [],
        "template_refs": [],
        "check_refs": [],
        "knowledge_refs_details": [],
        "wiki_refs_details": [],
        "raw_sections": {
            section.replace("## ", "", 1): parse_raw_section_lines(lines)
            for section, lines in sections.items()
            if parse_raw_section_lines(lines)
        },
        "unparsed_sections": sorted(section.replace("## ", "", 1) for section in sections if section not in recognized_sections),
        "primary_knowledge_entries": [],
        "fallback_source_refs": [],
        "fallback_conditions": [],
        "disallowed_broad_references": [],
        "reference_granularity": {
            "wiki_refs": "file_or_index_preferred",
            "knowledge_refs": "file_or_index_preferred",
        },
        "has_directory_ref": False,
        "requires_narrowing": False,
        "result_locations": result_locations,
        "completion_criteria": parse_bullets(sections.get("## Completion Criteria", [])),
        "facts_output_requirements": {},
        "business_output_requirements": {},
        "experience_output_requirements": {},
        "warnings": warnings,
        "errors": errors,
    }

    if not resolved["task_goal"]:
        errors.append("Task Goal is empty or unparseable")
    if not resolved["execution_constraints"]:
        errors.append("Constraints is empty or unparseable")

    for section, field in REFERENCE_SECTIONS.items():
        bullets = parse_bullets(sections.get(section, []))
        parsed_values = normalize_path_values(bullets)
        resolved[field] = parsed_values
        if section in sections and bullets and not parsed_values:
            errors.append(f"{section} exists but no valid paths were parsed")
        if field in {"knowledge_refs", "wiki_refs"}:
            resolved[f"{field}_details"] = parse_reference_details(parsed_values)

    policy_section = sections.get("## Knowledge Consumption Policy", [])
    policy = parse_policy_section(policy_section) if policy_section else parse_policy_section([])
    resolved.update(policy)

    for section, field in OUTPUT_REQUIREMENT_SECTIONS.items():
        parsed = parse_output_requirements(sections.get(section, []))
        resolved[field] = parsed
        if not parsed["required_sections"] and not parsed["boundary"]:
            pass  # Output requirements are now optional; contracts define the structure
        elif not parsed["required_sections"] or not parsed["boundary"]:
            warnings.append(f"{section} has partial output requirements (sections or boundary missing)")

    detail_items = list(resolved.get("knowledge_refs_details", [])) + list(resolved.get("wiki_refs_details", []))
    has_directory_ref = any(item.get("kind") == "directory" for item in detail_items)
    has_pattern_ref = any(item.get("kind") == "pattern" for item in detail_items)
    requires_narrowing = any(item.get("kind") in {"directory", "pattern"} for item in detail_items)
    resolved["has_directory_ref"] = has_directory_ref
    resolved["requires_narrowing"] = requires_narrowing

    if not resolved["wiki_refs"] and resolved["knowledge_refs"]:
        warnings.append("Wiki section is missing or empty; execution will rely on Knowledge directly")
    if "## Read Order" not in sections:
        warnings.append("Read Order section is missing")
    elif not resolved["read_order"]:
        warnings.append("Read Order section exists but no readable items were parsed")
    if has_directory_ref:
        warnings.append("Knowledge or Wiki references include directory-only paths; assembly must narrow them to stable entries when possible")
    if has_pattern_ref:
        warnings.append("Knowledge or Wiki references include wildcard paths; wildcard references cannot be copied directly during context assembly")
    if requires_narrowing and not policy_section:
        warnings.append("Knowledge Consumption Policy is missing while broad references are present")
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
