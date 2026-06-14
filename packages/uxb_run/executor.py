from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from packages.common import get_project_source_dir, get_project_workspace_dir, sanitize_json_text
from packages.provenance import upsert_generated_provenance_commands, validate_provenance
from packages.route_decision import load_uxb_execution_decision
from packages.archive import run_archive_artifacts
from packages.context_assemble import run_context_assemble
from packages.experience_preview import run_experience_preview
from packages.repair_loop import run_repair_close, run_repair_plan
from packages.task_bootstrap import run_task_bootstrap
from packages.validate.core import PLACEHOLDER_PATTERN, TEMPLATE_HINT_MARKERS
from packages.validate import (
    run_business_gate,
    run_business_lite_gate,
    run_business_note_gate,
    run_coverage_check,
    run_coverage_lite,
    run_experience_gate,
    run_experience_lite_gate,
    run_facts_gate,
    run_validate_lite,
    run_validate_outputs,
)


@dataclass
class CommandResult:
    command_name: str
    exit_code: int
    preflight_errors: list[str] | None = None
    target_artifacts: list[str] | None = None


def _command_map() -> dict[str, Callable[..., int]]:
    return {
        "bootstrap": run_task_bootstrap,
        "assemble": run_context_assemble,
        "gate-facts": run_facts_gate,
        "gate-business": run_business_gate,
        "gate-business-lite": run_business_lite_gate,
        "gate-business-note": run_business_note_gate,
        "gate-experience": run_experience_gate,
        "gate-experience-lite": run_experience_lite_gate,
        "validate": run_validate_outputs,
        "validate-lite": run_validate_lite,
        "coverage": run_coverage_check,
        "coverage-lite": run_coverage_lite,
        "preview": run_experience_preview,
        "archive": run_archive_artifacts,
        "repair-plan": run_repair_plan,
        "repair-close": run_repair_close,
    }


def _required_output_paths(project_id: str) -> list[Path]:
    decision = load_uxb_execution_decision(project_id) or {}
    outputs = decision.get("required_outputs", [])
    workspace_dir = get_project_workspace_dir(project_id)
    if not isinstance(outputs, list):
        return []
    return [workspace_dir / str(item).strip() for item in outputs if str(item).strip()]


def _target_paths_for_command(project_id: str, command_name: str) -> list[Path]:
    workspace_dir = get_project_workspace_dir(project_id)
    source_dir = get_project_source_dir(project_id)
    mapping = {
        "gate-facts": [workspace_dir / "facts.md"],
        "gate-business": [workspace_dir / "business_blueprint.md"],
        "gate-business-lite": [workspace_dir / "business_blueprint_lite.md"],
        "gate-business-note": [workspace_dir / "business_note.md"],
        "gate-experience": [workspace_dir / "experience_blueprint.md"],
        "gate-experience-lite": [workspace_dir / "experience_blueprint.md"],
        "validate": _required_output_paths(project_id),
        "validate-lite": _required_output_paths(project_id),
        "coverage": _required_output_paths(project_id),
        "coverage-lite": _required_output_paths(project_id),
        "repair-plan": [
            source_dir / "requirement.md",
            source_dir / "background.md",
        ],
    }
    targets = mapping.get(command_name, [])
    return [Path(item) for item in targets]


def _phase_generation_commands_for_command(project_id: str, command_name: str) -> list[str]:
    decision = load_uxb_execution_decision(project_id) or {}
    execution_mode = str(decision.get("execution_mode") or "").strip()
    if command_name == "gate-facts":
        return ["generate-facts"]
    if command_name == "gate-business":
        return ["generate-business"]
    if command_name == "gate-business-lite":
        return ["generate-business-lite"]
    if command_name == "gate-business-note":
        return ["generate-business-note"]
    if command_name in {"gate-experience", "gate-experience-lite"}:
        if execution_mode == "full":
            return ["generate-facts", "generate-business", "generate-experience"]
        if execution_mode == "standard":
            return ["generate-facts", "generate-business-lite", "generate-experience"]
        return ["generate-facts", "generate-business-note", "generate-experience"]
    return []


def _load_json_if_exists(path: Path) -> dict[str, object] | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        payload = json.loads(sanitize_json_text(path.read_text(encoding="utf-8")))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _has_meaningful_heading(content: str) -> bool:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return True
        if stripped.startswith("## "):
            return True
    return False


def _has_placeholder_residue(content: str) -> bool:
    if PLACEHOLDER_PATTERN.search(content):
        return True
    common_markers = ("[待补充]", "[TODO]", "TODO", "<待补充>", "<填写", "<缺失项>")
    return any(marker in content for marker in common_markers)


def preflight_check(project_id: str, command_name: str) -> tuple[list[str], list[Path]]:
    targets = _target_paths_for_command(project_id, command_name)
    if command_name == "repair-plan":
        return [], targets

    errors: list[str] = []
    for path in targets:
        if not path.exists():
            errors.append(f"缺少文件：{path.name}")
            continue
        if path.suffix == ".json":
            if _load_json_if_exists(path) is None:
                errors.append(f"JSON 非法：{path.name}")
            continue

        content = path.read_text(encoding="utf-8")
        if not content.strip():
            errors.append(f"文件为空：{path.name}")
            continue
        if not _has_meaningful_heading(content):
            errors.append(f"缺少必填章节骨架：{path.name}")
        if _has_placeholder_residue(content) or any(marker in content for marker in TEMPLATE_HINT_MARKERS):
            errors.append(f"存在占位符残留：{path.name}")
    return errors, targets


def run_existing_command(command_name: str, project_id: str, options: dict[str, object] | None = None) -> CommandResult:
    options = options or {}
    command_map = _command_map()
    runner = command_map.get(command_name)
    if runner is None:
        raise ValueError(f"Unsupported uxb run command: {command_name}")

    preflight_errors, targets = preflight_check(project_id, command_name)
    if preflight_errors:
        return CommandResult(
            command_name=command_name,
            exit_code=2,
            preflight_errors=preflight_errors,
            target_artifacts=[str(path).replace("\\", "/") for path in targets],
        )

    if command_name in {
        "gate-facts",
        "gate-business",
        "gate-business-lite",
        "gate-business-note",
        "gate-experience",
        "gate-experience-lite",
        "validate",
        "validate-lite",
        "coverage",
        "coverage-lite",
        "repair-plan",
    }:
        command_names = _phase_generation_commands_for_command(project_id, command_name)
        command_names.append(command_name)
        upsert_generated_provenance_commands(project_id, producer="uxb_run", command_names=command_names)
        provenance_issues = validate_provenance(project_id, required_commands=[command_name])
        if provenance_issues:
            return CommandResult(
                command_name=command_name,
                exit_code=2,
                preflight_errors=provenance_issues,
                target_artifacts=[f"projects/{project_id}/runtime/provenance.json"],
            )

    if command_name == "bootstrap":
        exit_code = runner(
            project_id,
            domain=str(options.get("domain") or ""),
            task_name=str(options.get("task_name") or "UXB Run Task"),
            force=bool(options.get("force", False)),
        )
    elif command_name == "assemble":
        exit_code = runner(project_id, strict=bool(options.get("strict", False)))
    elif command_name == "preview":
        exit_code = runner(project_id, host="127.0.0.1", port=0, serve=False)
    else:
        exit_code = runner(project_id)

    return CommandResult(
        command_name=command_name,
        exit_code=int(exit_code),
        preflight_errors=[],
        target_artifacts=[str(path).replace("\\", "/") for path in targets],
    )
