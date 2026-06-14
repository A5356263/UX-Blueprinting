from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from packages.uxb_run.models import CurrentAction, ProjectRunState


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stable_action_id(
    project_id: str,
    phase: str,
    stage: str,
    action_type: str,
    target_artifacts: list[str],
) -> str:
    raw = "|".join([project_id, phase, stage, action_type, ",".join(sorted(target_artifacts))])
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
    return f"{action_type}-{digest}"


def _make_action(
    state: ProjectRunState,
    *,
    phase: str,
    action_type: str,
    owner: str,
    stage: str,
    status: str,
    execution_mode: str = "unknown",
    target_artifacts: list[str] | None = None,
    required_inputs: list[str] | None = None,
    status_sources: list[str] | None = None,
    blocking_reasons: list[str] | None = None,
) -> CurrentAction:
    targets = target_artifacts or []
    action_id = _stable_action_id(state.project_id, phase, stage, action_type, targets)
    now = _now_iso()
    return CurrentAction(
        project_id=state.project_id,
        action_id=action_id,
        phase=phase,
        action_type=action_type,
        owner=owner,
        execution_mode=execution_mode,
        stage=stage,
        status=status,
        target_artifacts=targets,
        required_inputs=required_inputs or [],
        status_sources=status_sources or [],
        blocking_reasons=blocking_reasons or [],
        created_at=now,
        updated_at=now,
    )


def _execution_mode(state: ProjectRunState) -> str:
    value = str(state.route_decision.get("execution_mode") or "").strip()
    return value or "unknown"


def _required_outputs(state: ProjectRunState) -> list[str]:
    outputs = state.route_decision.get("required_outputs", [])
    if not isinstance(outputs, list):
        return []
    return [str(item).strip() for item in outputs if str(item).strip()]


def _artifact_path(state: ProjectRunState, name: str) -> Path:
    return state.workspace_dir / name


def _required_workspace_paths(state: ProjectRunState) -> list[Path]:
    return [_artifact_path(state, name) for name in _required_outputs(state)]


def _phase_from_state(state: ProjectRunState) -> str:
    payload = state.phase_state if isinstance(state.phase_state, dict) else {}
    phase = str(payload.get("phase") or "").strip()
    if phase in {"facts", "business", "experience", "final"}:
        return phase
    return "facts"


def _status_from_state(state: ProjectRunState) -> str:
    payload = state.phase_state if isinstance(state.phase_state, dict) else {}
    return str(payload.get("status") or "").strip()


def _phase_targets(state: ProjectRunState, phase: str) -> list[str]:
    execution_mode = _execution_mode(state)
    if phase == "facts":
        return [f"projects/{state.project_id}/workspace/facts.md"]
    if phase == "business":
        business_output = (
            "business_blueprint.md"
            if execution_mode == "full"
            else "business_blueprint_lite.md"
            if execution_mode == "standard"
            else "business_note.md"
        )
        return [f"projects/{state.project_id}/workspace/{business_output}"]
    if phase == "experience":
        return [f"projects/{state.project_id}/workspace/experience_blueprint.md"]
    if phase == "final":
        return [str(path).replace("\\", "/") for path in _required_workspace_paths(state)]
    return []


def plan_current_action(state: ProjectRunState) -> CurrentAction:
    if not state.project_exists:
        return _make_action(
            state,
            phase="formal_handoff",
            action_type="write_formal_inputs",
            owner="agent",
            stage="formal",
            status="requires_agent",
            target_artifacts=[
                f"projects/{state.project_id}/source/task_card.md",
                f"projects/{state.project_id}/source/requirement.md",
                f"projects/{state.project_id}/source/background.md",
                f"projects/{state.project_id}/runtime/uxb_route_decision.json",
            ],
        )

    if not state.source_ready:
        return _make_action(
            state,
            phase="formal_handoff",
            action_type="write_formal_inputs",
            owner="agent",
            stage="formal",
            status="requires_agent",
            target_artifacts=[
                f"projects/{state.project_id}/source/task_card.md",
                f"projects/{state.project_id}/source/requirement.md",
                f"projects/{state.project_id}/source/background.md",
                f"projects/{state.project_id}/runtime/uxb_route_decision.json",
            ],
            blocking_reasons=state.source_errors,
            status_sources=[
                f"projects/{state.project_id}/source/requirement.md",
                f"projects/{state.project_id}/source/background.md",
            ],
        )

    if str(state.route_decision.get("status") or "") != "confirmed":
        return _make_action(
            state,
            phase="formal_handoff",
            action_type="fix_route_decision",
            owner="agent",
            stage="formal",
            status="requires_agent",
            target_artifacts=[f"projects/{state.project_id}/runtime/uxb_route_decision.json"],
            blocking_reasons=[str(item) for item in state.route_decision.get("validation_errors", []) if str(item).strip()],
            status_sources=[f"projects/{state.project_id}/runtime/uxb_route_decision.json"],
        )

    if state.context_is_stale:
        return _make_action(
            state,
            phase="mainline",
            action_type="assemble_context",
            owner="system",
            stage="runtime",
            status="auto_executed",
            execution_mode=_execution_mode(state),
            status_sources=[
                f"projects/{state.project_id}/source/requirement.md",
                f"projects/{state.project_id}/source/background.md",
                f"projects/{state.project_id}/runtime/uxb_route_decision.json",
                f"projects/{state.project_id}/runtime/context_manifest.json",
            ],
        )

    execution_mode = _execution_mode(state)
    current_phase = _phase_from_state(state)
    current_status = _status_from_state(state)

    if current_phase == "final" and current_status in {"passed", "passed_with_warnings"}:
        if not state.preview_exists:
            return _make_action(
                state,
                phase="finalize",
                action_type="preview",
                owner="system",
                stage="final",
                status="auto_executed",
                execution_mode=execution_mode,
                target_artifacts=[f"projects/{state.project_id}/runtime/preview/index.html"],
            )
        return _make_action(
            state,
            phase="completed",
            action_type="completed",
            owner="system",
            stage="final",
            status="completed",
            execution_mode=execution_mode,
        )

    return _make_action(
        state,
        phase="mainline",
        action_type="phase_work",
        owner="agent",
        stage=current_phase,
        status="requires_agent",
        execution_mode=execution_mode,
        target_artifacts=_phase_targets(state, current_phase),
    )
