from __future__ import annotations

import json
from pathlib import Path

from packages.common import get_project_runtime_dir
from packages.uxb_run.models import PhaseState, StageContext

_LEGACY_RUNTIME_FILES = (
    "current_action.json",
    "agent_next_task.md",
    "agent_task_status.json",
    "uxb_run_report.json",
    "knowledge_trace.json",
)


def _write_json(path: Path, payload: dict[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def remove_legacy_runtime_files(project_id: str) -> None:
    runtime_dir = get_project_runtime_dir(project_id)
    for filename in _LEGACY_RUNTIME_FILES:
        path = runtime_dir / filename
        if path.exists():
            path.unlink()


def write_phase_state(project_id: str, phase_state: PhaseState) -> Path:
    runtime_dir = get_project_runtime_dir(project_id)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    remove_legacy_runtime_files(project_id)
    return _write_json(runtime_dir / "phase_state.json", phase_state.to_dict())


def write_stage_context(project_id: str, stage_context: StageContext) -> Path:
    runtime_dir = get_project_runtime_dir(project_id)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    remove_legacy_runtime_files(project_id)
    return _write_json(runtime_dir / "stage_context.json", stage_context.to_dict())
