from __future__ import annotations

import json
from pathlib import Path

from packages.common import (
    get_project_dir,
    get_project_preview_dir,
    get_project_remediation_dir,
    get_project_runtime_dir,
    get_project_source_dir,
    get_project_workspace_dir,
    sanitize_json_text,
)
from packages.route_decision import load_uxb_execution_decision
from packages.routed_main.core import BOOTSTRAP_PLACEHOLDER_MARKERS
from packages.uxb_run.models import ProjectRunState
from packages.uxb_run.staleness import is_context_stale
from packages.validate.core import read_gate_status


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists() or not path.is_file():
        return {}
    try:
        payload = json.loads(sanitize_json_text(path.read_text(encoding="utf-8")))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _formal_handoff_checklist(
    source_dir: Path,
    runtime_dir: Path,
    *,
    requirement_ready: bool,
    background_ready: bool,
    task_card_ready: bool,
    route_ready: bool,
) -> list[str]:
    requirement_label = "✓" if requirement_ready else "✗"
    background_label = "✓" if background_ready else "✗"
    task_card_label = "✓" if task_card_ready else "✗"
    route_label = "✓" if route_ready else "✗"
    return [
        "缺少以下正式交接文件：",
        f"  {task_card_label} source/task_card.md",
        f"  {requirement_label} source/requirement.md",
        f"  {background_label} source/background.md",
        f"  {route_label} runtime/uxb_route_decision.json",
        "请补齐后重新运行。",
    ]


def _source_ready(source_dir: Path, runtime_dir: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    requirement_path = source_dir / "requirement.md"
    background_path = source_dir / "background.md"
    task_card_path = source_dir / "task_card.md"
    route_decision_path = runtime_dir / "uxb_route_decision.json"

    requirement_ready = requirement_path.exists()
    background_ready = background_path.exists()
    task_card_ready = task_card_path.exists()
    route_ready = route_decision_path.exists()

    if not requirement_ready:
        errors.append("source/requirement.md 缺失")
    if not background_ready:
        errors.append("source/background.md 缺失")
    if not task_card_ready:
        errors.append("source/task_card.md 缺失")

    for path, label in (
        (requirement_path, "source/requirement.md"),
        (background_path, "source/background.md"),
        (task_card_path, "source/task_card.md"),
    ):
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        if any(marker in content for marker in BOOTSTRAP_PLACEHOLDER_MARKERS):
            errors.append(f"{label} 仍包含 bootstrap 占位内容")
            if path == requirement_path:
                requirement_ready = False
            elif path == background_path:
                background_ready = False
            elif path == task_card_path:
                task_card_ready = False

    if errors:
        errors.extend(
            _formal_handoff_checklist(
                source_dir,
                runtime_dir,
                requirement_ready=requirement_ready,
                background_ready=background_ready,
                task_card_ready=task_card_ready,
                route_ready=route_ready,
            )
        )

    return not errors, errors


def read_project_run_state(project_id: str) -> ProjectRunState:
    project_dir = get_project_dir(project_id)
    source_dir = get_project_source_dir(project_id)
    runtime_dir = get_project_runtime_dir(project_id)
    workspace_dir = get_project_workspace_dir(project_id)
    preview_dir = get_project_preview_dir(project_id)
    remediation_dir = get_project_remediation_dir(project_id)

    project_exists = project_dir.exists() and project_dir.is_dir()
    source_ready, source_errors = _source_ready(source_dir, runtime_dir) if project_exists else (False, [])
    route_decision = load_uxb_execution_decision(project_id) if project_exists else {}
    context_manifest_path = runtime_dir / "context_manifest.json"
    context_bundle_dir = runtime_dir / "context_bundle"
    context_manifest = _read_json(context_manifest_path)
    gate_statuses = {
        "facts": read_gate_status(project_id, "facts") or {},
        "business": read_gate_status(project_id, "business") or {},
        "business_lite": read_gate_status(project_id, "business_lite") or {},
        "business_note": read_gate_status(project_id, "business_note") or {},
        "experience": read_gate_status(project_id, "experience") or {},
        "experience_lite": read_gate_status(project_id, "experience_lite") or {},
    }
    return ProjectRunState(
        project_id=project_id,
        project_dir=project_dir,
        source_dir=source_dir,
        runtime_dir=runtime_dir,
        workspace_dir=workspace_dir,
        preview_dir=preview_dir,
        project_exists=project_exists,
        source_ready=source_ready,
        source_errors=source_errors,
        route_decision=route_decision,
        phase_state=_read_json(runtime_dir / "phase_state.json"),
        stage_context=_read_json(runtime_dir / "stage_context.json"),
        context_manifest=context_manifest,
        context_manifest_exists=context_manifest_path.exists(),
        context_bundle_exists=context_bundle_dir.exists(),
        context_is_stale=(
            is_context_stale(
                context_manifest_path,
                context_bundle_dir,
                source_dir / "requirement.md",
                source_dir / "background.md",
                runtime_dir / "uxb_route_decision.json",
            )
            if project_exists
            else False
        ),
        remediation_plan=_read_json(remediation_dir / "remediation_plan.json"),
        retry_scope=_read_json(remediation_dir / "retry_scope.json"),
        gate_statuses=gate_statuses,
        check_status=_read_json(workspace_dir / "check_status.json"),
        preview_exists=(preview_dir / "index.html").exists(),
    )
