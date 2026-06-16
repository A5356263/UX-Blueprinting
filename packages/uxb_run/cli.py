from __future__ import annotations

import json
from packages.common import get_repo_root
from packages.provenance import read_provenance
from packages.uxb_run.executor import CommandResult, run_existing_command
from packages.uxb_run.history import append_run_history
from packages.uxb_run.models import CurrentAction, PhaseState, ProjectRunState, StageContext, UXBRunHistoryItem
from packages.uxb_run.planner import plan_current_action
from packages.uxb_run.state_reader import read_project_run_state
from packages.uxb_run.task_writer import write_phase_state, write_stage_context


def _write_history(
    project_id: str,
    *,
    phase_before: str,
    phase_after: str,
    action_type: str,
    owner: str,
    auto_commands_run: list[str],
    result: str,
    timestamp: str,
) -> None:
    append_run_history(
        project_id,
        UXBRunHistoryItem(
            timestamp=timestamp,
            project_id=project_id,
            command=f"python -m packages run {project_id}",
            phase_before=phase_before,
            phase_after=phase_after,
            action_type=action_type,
            owner=owner,
            auto_commands_run=auto_commands_run,
            result=result,
            next_phase=(phase_after if phase_after != phase_before else ""),
        ),
    )


def _phase_name_for_action(action: CurrentAction) -> str:
    if action.stage in {"formal", "facts", "business", "experience", "final"}:
        return action.stage
    if action.action_type in {"write_formal_inputs", "fix_route_decision"}:
        return "formal"
    if action.action_type == "completed":
        return "final"
    return "formal"


def _phase_refs_for_action(action: CurrentAction) -> dict[str, list[str]]:
    if action.action_type == "write_formal_inputs":
        return {
            "required_inputs": [
                "source/task_card.md",
                ".codex/skills/uxb/SKILL.md",
                ".codex/skills/uxb/references/execution_guide.md",
                ".codex/skills/uxb/references/uxb_route_decision_authoring_guide.md",
            ],
            "template_refs": [],
            "rule_refs": [
                ".codex/skills/uxb/SKILL.md",
                ".codex/skills/uxb/references/execution_guide.md",
                ".codex/skills/uxb/references/uxb_route_decision_authoring_guide.md",
            ],
        }
    if action.action_type == "fix_route_decision":
        return {
            "required_inputs": [
                f"projects/{action.project_id}/source/requirement.md",
                f"projects/{action.project_id}/source/background.md",
                ".codex/skills/uxb/references/uxb_route_decision_authoring_guide.md",
            ],
            "template_refs": [],
            "rule_refs": [".codex/skills/uxb/references/uxb_route_decision_authoring_guide.md"],
        }
    if action.action_type in {"generate_artifact", "phase_work"}:
        if action.stage == "facts":
            return {
                "required_inputs": [
                    f"projects/{action.project_id}/source/requirement.md",
                    f"projects/{action.project_id}/source/background.md",
                    f"projects/{action.project_id}/runtime/context_manifest.json",
                    "templates/facts.template.md",
                    "specs/08_fact_extraction_contract.md",
                ],
                "template_refs": ["templates/facts.template.md"],
                "rule_refs": ["specs/08_fact_extraction_contract.md"],
            }
        if action.stage == "business":
            return {
                "required_inputs": [
                    f"projects/{action.project_id}/workspace/facts.md",
                    "specs/09_business_blueprint_contract.md",
                ],
                "template_refs": [],
                "rule_refs": ["specs/09_business_blueprint_contract.md"],
            }
        if action.stage == "final":
            return {
                "required_inputs": [
                    f"projects/{action.project_id}/workspace/facts.md",
                    f"projects/{action.project_id}/workspace/check_status.json",
                ],
                "template_refs": [],
                "rule_refs": ["specs/11_repair_loop_contract.md"],
            }
        return {
            "required_inputs": [
                f"projects/{action.project_id}/workspace/facts.md",
                f"projects/{action.project_id}/workspace/business_blueprint.md",
                f"projects/{action.project_id}/workspace/business_blueprint_lite.md",
                f"projects/{action.project_id}/workspace/business_note.md",
                "specs/10_experience_blueprint_contract.md",
            ],
            "template_refs": [],
            "rule_refs": ["specs/10_experience_blueprint_contract.md"],
        }
    if action.action_type == "repair_artifact":
        repair_refs = [
            f"projects/{action.project_id}/runtime/remediation/issue_index.json",
            f"projects/{action.project_id}/runtime/remediation/remediation_plan.json",
            f"projects/{action.project_id}/runtime/remediation/retry_scope.json",
            f"projects/{action.project_id}/runtime/remediation/repair_summary.md",
        ]
        return {
            "required_inputs": list(dict.fromkeys((action.status_sources or []) + repair_refs)),
            "template_refs": [],
            "rule_refs": [],
        }
    return {"required_inputs": [], "template_refs": [], "rule_refs": []}


def _build_phase_state(action: CurrentAction, *, status_override: str | None = None, warnings_override: list[str] | None = None) -> PhaseState:
    refs = _phase_refs_for_action(action)
    if status_override == "ok":
        status = "passed"
    elif status_override == "passed_with_warnings":
        status = "passed_with_warnings"
    elif status_override == "failed":
        status = "blocked"
    elif status_override is not None:
        status = status_override
    else:
        status = (
        "blocked"
        if action.action_type == "blocked"
        else "passed"
        if action.action_type == "completed"
        else "needs_revision"
        if action.action_type == "repair_artifact"
        else "in_progress"
        )
    repair_refs = []
    if action.action_type == "repair_artifact":
        repair_refs = [
            f"projects/{action.project_id}/runtime/remediation/issue_index.json",
            f"projects/{action.project_id}/runtime/remediation/remediation_plan.json",
            f"projects/{action.project_id}/runtime/remediation/retry_scope.json",
            f"projects/{action.project_id}/runtime/remediation/repair_summary.md",
        ]
    return PhaseState(
        project_id=action.project_id,
        phase=_phase_name_for_action(action),
        execution_mode=action.execution_mode,
        status=status,
        target_artifact=(action.target_artifacts[0] if action.target_artifacts else ""),
        target_artifacts=list(action.target_artifacts),
        required_inputs=list(refs["required_inputs"]),
        template_refs=list(refs["template_refs"]),
        rule_refs=list(refs["rule_refs"]),
        preflight_errors=list(action.blocking_reasons),
        repair_mode=(action.action_type == "repair_artifact"),
        repair_refs=repair_refs,
        gate_status_refs=list(action.status_sources),
        warnings=(list(warnings_override) if warnings_override is not None else []),
        created_at=action.created_at,
        updated_at=action.updated_at,
    )


def _build_stage_context(action: CurrentAction, state: ProjectRunState | None = None, *, appended_warnings: list[dict[str, object]] | None = None) -> StageContext:
    existing = state.stage_context if state is not None else {}
    execution_trace = read_provenance(action.project_id)
    if not execution_trace and isinstance(existing, dict):
        execution_trace = existing.get("execution_trace", {})
    context_manifest = state.context_manifest if state is not None and isinstance(state.context_manifest, dict) else {}
    knowledge_trace = context_manifest.get("knowledge_trace", {})
    if (not isinstance(knowledge_trace, dict) or not knowledge_trace) and isinstance(existing, dict):
        existing_knowledge_trace = existing.get("knowledge_trace", {})
        if isinstance(existing_knowledge_trace, dict):
            knowledge_trace = existing_knowledge_trace
    accumulated_warnings = existing.get("accumulated_warnings", []) if isinstance(existing, dict) else []
    if appended_warnings:
        accumulated_warnings = list(accumulated_warnings) + list(appended_warnings)
    return StageContext(
        project_id=action.project_id,
        context={
            "selection_source": str(context_manifest.get("selection_source") or ""),
            "context_manifest_ref": (
                f"projects/{action.project_id}/runtime/context_manifest.json"
                if context_manifest
                else ""
            ),
            "context_bundle_ref": (
                f"projects/{action.project_id}/runtime/context_bundle"
                if state is not None and state.context_bundle_exists
                else ""
            ),
        },
        knowledge_trace=(knowledge_trace if isinstance(knowledge_trace, dict) else {}),
        execution_trace=(execution_trace if isinstance(execution_trace, dict) else {}),
        accumulated_warnings=(list(accumulated_warnings) if isinstance(accumulated_warnings, list) else []),
        updated_at=action.updated_at,
    )


def _write_agent_bundle(
    project_id: str,
    action: CurrentAction,
    auto_commands_run: list[str],
    state: ProjectRunState | None = None,
    *,
    history_phase_before: str | None = None,
) -> None:
    write_phase_state(project_id, _build_phase_state(action))
    write_stage_context(project_id, _build_stage_context(action, state))
    phase_after = _phase_name_for_action(action)
    _write_history(
        project_id,
        phase_before=(history_phase_before or phase_after),
        phase_after=phase_after,
        action_type=action.action_type,
        owner=action.owner,
        auto_commands_run=auto_commands_run,
        result=action.status,
        timestamp=action.updated_at,
    )


def _write_terminal_report(
    project_id: str,
    action: CurrentAction,
    auto_commands_run: list[str],
    status: str,
    state: ProjectRunState | None = None,
    *,
    history_phase_before: str | None = None,
) -> None:
    warning_messages: list[str] = []
    if status == "passed_with_warnings" and state is not None and isinstance(state.phase_state, dict):
        values = state.phase_state.get("warnings", [])
        if isinstance(values, list):
            warning_messages = [str(item).strip() for item in values if str(item).strip()]
    write_phase_state(project_id, _build_phase_state(action, status_override=status, warnings_override=warning_messages))
    write_stage_context(project_id, _build_stage_context(action, state))
    phase_after = _phase_name_for_action(action)
    _write_history(
        project_id,
        phase_before=(history_phase_before or phase_after),
        phase_after=phase_after,
        action_type=action.action_type,
        owner=action.owner,
        auto_commands_run=auto_commands_run,
        result=status,
        timestamp=action.updated_at,
    )


def _command_for_action(action: CurrentAction) -> str | None:
    if action.action_type == "assemble_context":
        return "assemble"
    if action.action_type == "preview":
        return "preview"
    if action.action_type == "archive":
        return "archive"
    if action.action_type not in {"run_checks", "phase_work"}:
        return None
    if action.stage == "facts":
        return "gate-facts"
    if action.stage == "business":
        return {
            "full": "gate-business",
            "standard": "gate-business-lite",
            "fast": "gate-business-note",
        }.get(action.execution_mode, "gate-business-lite")
    if action.stage == "experience":
        return {
            "full": "gate-experience",
            "standard": "gate-experience-lite",
            "fast": "gate-experience-lite",
        }.get(action.execution_mode, "gate-experience-lite")
    return {"full": "validate", "standard": "validate-lite", "fast": "validate-lite"}.get(action.execution_mode, "validate-lite")


def _needs_followup_check(action: CurrentAction) -> bool:
    return action.stage == "final" and action.execution_mode in {"full", "standard"}

def _ensure_repair_plan(project_id: str, auto_commands_run: list[str]) -> bool:
    result = run_existing_command("repair-plan", project_id)
    auto_commands_run.append("repair-plan")
    return result.exit_code == 0

def _run_auto_command(
    project_id: str,
    action: CurrentAction,
    *,
    domain: str | None,
    task_name: str | None,
    strict: bool,
    auto_commands_run: list[str],
) -> list[CommandResult]:
    command_results: list[CommandResult] = []
    if action.action_type == "write_formal_inputs":
        return command_results
    command_name = _command_for_action(action)
    if not command_name:
        return command_results

    options: dict[str, object] = {"strict": strict}
    if command_name == "bootstrap":
        options.update({"domain": domain or "", "task_name": task_name or "UXB Run Task"})
    result = run_existing_command(command_name, project_id, options=options)
    auto_commands_run.append(command_name)
    command_results.append(result)

    if _needs_followup_check(action) and result.exit_code == 0:
        coverage_command = "coverage" if action.execution_mode == "full" else "coverage-lite"
        coverage_result = run_existing_command(coverage_command, project_id, options=options)
        auto_commands_run.append(coverage_command)
        command_results.append(coverage_result)

    return command_results


def _repair_action_for_preflight_failure(state: ProjectRunState, action: CurrentAction, errors: list[str], targets: list[str]) -> CurrentAction:
    return CurrentAction(
        project_id=state.project_id,
        action_id=f"preflight-{action.stage}-{action.action_id}",
        phase="repair",
        action_type="repair_artifact",
        owner="agent",
        execution_mode=action.execution_mode,
        stage=action.stage,
        status="requires_agent",
        target_artifacts=(targets or list(action.target_artifacts)),
        required_inputs=[],
        status_sources=[],
        blocking_reasons=list(errors),
        created_at=action.created_at,
        updated_at=action.updated_at,
    )


def _phase_target_exists(project_id: str, action: CurrentAction) -> bool:
    if action.stage == "final":
        return True
    if not action.target_artifacts:
        return False
    target = get_repo_root() / action.target_artifacts[0]
    return target.exists()


def _phase_status_payload(state: ProjectRunState, action: CurrentAction) -> dict[str, object]:
    if action.stage == "facts":
        return state.gate_status("facts")
    if action.stage == "business":
        if action.execution_mode == "full":
            return state.gate_status("business")
        if action.execution_mode == "standard":
            return state.gate_status("business_lite")
        return state.gate_status("business_note")
    if action.stage == "experience":
        if action.execution_mode == "full":
            return state.gate_status("experience")
        return state.gate_status("experience_lite")
    return state.check_status


def _extract_warnings(payload: dict[str, object]) -> list[str]:
    issues = payload.get("issues", {})
    if isinstance(issues, dict):
        warnings = issues.get("warnings", [])
        if isinstance(warnings, list):
            return [str(item) for item in warnings if str(item).strip()]
    return []


def _append_warning_entries(project_id: str, state: ProjectRunState, action: CurrentAction, warnings: list[str]) -> None:
    if not warnings:
        return
    source = "check_status" if action.stage == "final" else f"gate-{action.stage}"
    existing = state.stage_context if isinstance(state.stage_context, dict) else {}
    existing_items = existing.get("accumulated_warnings", []) if isinstance(existing, dict) else []
    known = {
        (str(item.get("phase") or ""), str(item.get("source") or ""), str(item.get("message") or ""))
        for item in existing_items
        if isinstance(item, dict)
    }
    existing_messages_from_gate = {
        str(item.get("message") or "")
        for item in existing_items
        if isinstance(item, dict)
        and str(item.get("source") or "") != "check_status"
        and str(item.get("message") or "").strip()
    }
    entries = []
    for item in warnings:
        key = (action.stage, source, item)
        if key in known:
            continue
        if source == "check_status" and item in existing_messages_from_gate:
            continue
        entries.append({"phase": action.stage, "source": source, "message": item})
    write_stage_context(project_id, _build_stage_context(action, state, appended_warnings=entries))


def _repair_action_for_failed_phase(state: ProjectRunState, action: CurrentAction) -> CurrentAction:
    return CurrentAction(
        project_id=state.project_id,
        action_id=f"repair-{action.stage}-{action.action_id}",
        phase="repair",
        action_type="repair_artifact",
        owner="agent",
        execution_mode=action.execution_mode,
        stage=action.stage,
        status="requires_agent",
        target_artifacts=list(action.target_artifacts),
        required_inputs=[],
        status_sources=list(action.status_sources),
        blocking_reasons=[],
        created_at=action.created_at,
        updated_at=action.updated_at,
    )


def _has_accumulated_warnings(state: ProjectRunState) -> bool:
    payload = state.stage_context if isinstance(state.stage_context, dict) else {}
    warnings = payload.get("accumulated_warnings", []) if isinstance(payload, dict) else []
    return bool(warnings)


def _next_phase_name(stage: str) -> str | None:
    mapping = {
        "facts": "business",
        "business": "experience",
        "experience": "final",
    }
    return mapping.get(stage)


def _next_phase_action(state: ProjectRunState, action: CurrentAction, next_stage: str) -> CurrentAction:
    execution_mode = action.execution_mode
    if next_stage == "business":
        target_artifacts = (
            [f"projects/{state.project_id}/workspace/business_blueprint.md"]
            if execution_mode == "full"
            else [f"projects/{state.project_id}/workspace/business_blueprint_lite.md"]
            if execution_mode == "standard"
            else [f"projects/{state.project_id}/workspace/business_note.md"]
        )
    elif next_stage == "experience":
        target_artifacts = [f"projects/{state.project_id}/workspace/experience_blueprint.md"]
    elif next_stage == "final":
        decision = state.route_decision if isinstance(state.route_decision, dict) else {}
        outputs = decision.get("required_outputs", []) if isinstance(decision, dict) else []
        target_artifacts = [
            f"projects/{state.project_id}/workspace/{str(item).strip()}"
            for item in outputs
            if str(item).strip()
        ]
    else:
        target_artifacts = [f"projects/{state.project_id}/workspace/facts.md"]
    return CurrentAction(
        project_id=state.project_id,
        action_id=f"phase-{next_stage}-{action.action_id}",
        phase="mainline",
        action_type="phase_work",
        owner="agent",
        execution_mode=execution_mode,
        stage=next_stage,
        status="requires_agent",
        target_artifacts=target_artifacts,
        required_inputs=[],
        status_sources=[],
        blocking_reasons=[],
        created_at=action.created_at,
        updated_at=action.updated_at,
    )


def run_uxb_run(
    project_id: str,
    *,
    domain: str | None = None,
    task_name: str | None = None,
    strict: bool = False,
    skip_preview: bool = False,
    archive: bool = False,
    json_output: bool = False,
) -> int:
    auto_commands_run: list[str] = []
    history_phase_before: str | None = None

    while True:
        state = read_project_run_state(project_id)
        if not state.project_exists:
            if not domain:
                action = CurrentAction(
                    project_id=project_id,
                    action_id="blocked-missing-domain",
                    phase="formal_handoff",
                    action_type="blocked",
                    owner="user",
                    stage="formal",
                    status="blocked",
                    blocking_reasons=["项目不存在时必须提供 --domain 才能自动 bootstrap。"],
                )
                _write_terminal_report(project_id, action, auto_commands_run, "blocked")
                if json_output:
                    print(json.dumps({"status": "blocked", "project_id": project_id, "message": "missing --domain"}, ensure_ascii=False))
                return 2
            bootstrap_result = run_existing_command(
                "bootstrap",
                project_id,
                options={"domain": domain, "task_name": task_name or "UXB Run Task", "force": False},
            )
            auto_commands_run.append("bootstrap")
            if bootstrap_result.exit_code != 0:
                action = CurrentAction(
                    project_id=project_id,
                    action_id="failed-bootstrap",
                    phase="formal_handoff",
                    action_type="blocked",
                    owner="system",
                    stage="formal",
                    status="blocked",
                    blocking_reasons=["bootstrap 执行失败。"],
                )
                _write_terminal_report(project_id, action, auto_commands_run, "failed")
                return 5
            continue

        action = plan_current_action(state)
        if history_phase_before is None:
            history_phase_before = _phase_name_for_action(action)
        if action.action_type in {"write_formal_inputs", "fix_route_decision", "repair_artifact"}:
            if action.action_type == "repair_artifact":
                if not _ensure_repair_plan(project_id, auto_commands_run):
                    _write_terminal_report(project_id, action, auto_commands_run, "failed", state, history_phase_before=history_phase_before)
                    return 5
                state = read_project_run_state(project_id)
            _write_agent_bundle(project_id, action, auto_commands_run, state, history_phase_before=history_phase_before)
            if json_output:
                print(json.dumps({"status": "ok", "project_id": project_id, "phase": _phase_name_for_action(action), "state_file": f"projects/{project_id}/runtime/phase_state.json"}, ensure_ascii=False))
            return 0

        if action.action_type == "phase_work":
            if not _phase_target_exists(project_id, action):
                _write_agent_bundle(project_id, action, auto_commands_run, state, history_phase_before=history_phase_before)
                if json_output:
                    print(json.dumps({"status": "ok", "project_id": project_id, "phase": _phase_name_for_action(action), "state_file": f"projects/{project_id}/runtime/phase_state.json"}, ensure_ascii=False))
                return 0

            command_results = _run_auto_command(
                project_id,
                action,
                domain=domain,
                task_name=task_name,
                strict=strict,
                auto_commands_run=auto_commands_run,
            )
            preflight_failures = [item for item in command_results if item.preflight_errors]
            if preflight_failures:
                failure = preflight_failures[0]
                repair_action = _repair_action_for_preflight_failure(
                    state,
                    action,
                    failure.preflight_errors or [],
                    failure.target_artifacts or [],
                )
                _write_agent_bundle(
                    project_id,
                    repair_action,
                    auto_commands_run,
                    state,
                    history_phase_before=history_phase_before,
                )
                if json_output:
                    print(json.dumps({"status": "ok", "project_id": project_id, "phase": _phase_name_for_action(repair_action), "state_file": f"projects/{project_id}/runtime/phase_state.json"}, ensure_ascii=False))
                return 0
            if any(item.exit_code != 0 for item in command_results):
                next_state = read_project_run_state(project_id)
                phase_payload = _phase_status_payload(next_state, action)
                if str(phase_payload.get("status") or "").strip() == "failed":
                    repair_action = _repair_action_for_failed_phase(next_state, action)
                    if not _ensure_repair_plan(project_id, auto_commands_run):
                        _write_terminal_report(project_id, repair_action, auto_commands_run, "failed", next_state, history_phase_before=history_phase_before)
                        return 5
                    next_state = read_project_run_state(project_id)
                    _write_agent_bundle(project_id, repair_action, auto_commands_run, next_state, history_phase_before=history_phase_before)
                    if json_output:
                        print(json.dumps({"status": "ok", "project_id": project_id, "phase": _phase_name_for_action(repair_action), "state_file": f"projects/{project_id}/runtime/phase_state.json"}, ensure_ascii=False))
                    return 0
                _write_terminal_report(project_id, action, auto_commands_run, "failed", state, history_phase_before=history_phase_before)
                return 5

            next_state = read_project_run_state(project_id)
            phase_payload = _phase_status_payload(next_state, action)
            phase_status = str(phase_payload.get("status") or "").strip()
            warnings = _extract_warnings(phase_payload)
            if warnings:
                _append_warning_entries(project_id, next_state, action, warnings)
                next_state = read_project_run_state(project_id)
            if phase_status == "failed":
                repair_action = _repair_action_for_failed_phase(next_state, action)
                if not _ensure_repair_plan(project_id, auto_commands_run):
                    _write_terminal_report(project_id, repair_action, auto_commands_run, "failed", next_state, history_phase_before=history_phase_before)
                    return 5
                next_state = read_project_run_state(project_id)
                _write_agent_bundle(project_id, repair_action, auto_commands_run, next_state, history_phase_before=history_phase_before)
                if json_output:
                    print(json.dumps({"status": "ok", "project_id": project_id, "phase": _phase_name_for_action(repair_action), "state_file": f"projects/{project_id}/runtime/phase_state.json"}, ensure_ascii=False))
                    return 0
            if action.stage != "final":
                next_stage = _next_phase_name(action.stage)
                if next_stage:
                    next_action = _next_phase_action(next_state, action, next_stage)
                    write_phase_state(project_id, _build_phase_state(next_action))
                    write_stage_context(project_id, _build_stage_context(next_action, next_state))
                    continue
            final_status = "passed_with_warnings" if warnings or _has_accumulated_warnings(next_state) else "ok"
            write_phase_state(project_id, _build_phase_state(action, status_override=final_status, warnings_override=warnings))
            write_stage_context(project_id, _build_stage_context(action, next_state))
            continue

        if action.action_type == "completed":
            if archive:
                archive_action = CurrentAction(**{**action.to_dict(), "phase": "finalize", "action_type": "archive", "status": "auto_executed"})
                command_results = _run_auto_command(project_id, archive_action, domain=domain, task_name=task_name, strict=strict, auto_commands_run=auto_commands_run)
                if any(item.exit_code != 0 for item in command_results):
                    _write_terminal_report(project_id, archive_action, auto_commands_run, "failed", state, history_phase_before=history_phase_before)
                    return 5
                final_action = CurrentAction(**{**action.to_dict(), "updated_at": archive_action.updated_at})
                terminal_status = "passed_with_warnings" if _has_accumulated_warnings(state) else "ok"
                _write_terminal_report(project_id, final_action, auto_commands_run, terminal_status, state, history_phase_before=history_phase_before)
                if json_output:
                    print(json.dumps({"status": "ok", "project_id": project_id, "phase": "final"}, ensure_ascii=False))
                return 0
            terminal_status = "passed_with_warnings" if _has_accumulated_warnings(state) else "ok"
            _write_terminal_report(project_id, action, auto_commands_run, terminal_status, state, history_phase_before=history_phase_before)
            if json_output:
                print(json.dumps({"status": "ok", "project_id": project_id, "phase": "final"}, ensure_ascii=False))
            return 0

        if action.action_type == "preview" and skip_preview:
            skipped_action = CurrentAction(**{**action.to_dict(), "phase": "finalize", "action_type": "completed", "status": "completed"})
            terminal_status = "passed_with_warnings" if _has_accumulated_warnings(state) else "ok"
            _write_terminal_report(project_id, skipped_action, auto_commands_run, terminal_status, state, history_phase_before=history_phase_before)
            if json_output:
                print(json.dumps({"status": "ok", "project_id": project_id, "phase": "final"}, ensure_ascii=False))
            return 0

        command_results = _run_auto_command(
            project_id,
            action,
            domain=domain,
            task_name=task_name,
            strict=strict,
            auto_commands_run=auto_commands_run,
        )
        if any(item.exit_code != 0 for item in command_results):
            _write_terminal_report(project_id, action, auto_commands_run, "failed", state, history_phase_before=history_phase_before)
            return 5


def main(args) -> int:
    return run_uxb_run(
        args.project_id,
        domain=args.domain,
        task_name=args.task_name,
        strict=args.strict,
        skip_preview=args.skip_preview,
        archive=args.archive,
        json_output=args.json,
    )
