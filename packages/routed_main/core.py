from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from packages.common import get_project_runtime_dir, get_project_source_dir, get_project_workspace_dir
from packages.context_assemble import run_context_assemble
from packages.experience_preview import run_experience_preview
from packages.generation import (
    run_generate_business,
    run_generate_business_lite,
    run_generate_business_note,
    run_generate_experience,
    run_generate_facts,
)
from packages.project_structure_check import run_project_structure_check
from packages.provenance import append_command_if_provenance_exists
from packages.route_decision import load_uxb_execution_decision, run_route_decision
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


BOOTSTRAP_PLACEHOLDER_MARKERS = (
    "请在这里粘贴原始需求正文",
    "请在这里补充背景资料、约束、相关链接或历史上下文",
    "如果目前信息不足，也请显式写出缺失信息",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _actual_outputs(project_id: str) -> list[str]:
    workspace_dir = get_project_workspace_dir(project_id)
    runtime_dir = get_project_runtime_dir(project_id)
    candidates = [
        workspace_dir / "facts.md",
        workspace_dir / "business_note.md",
        workspace_dir / "business_blueprint_lite.md",
        workspace_dir / "business_blueprint.md",
        workspace_dir / "experience_blueprint.md",
        workspace_dir / "check_status.json",
        runtime_dir / "routed_main_plan.json",
        runtime_dir / "routed_main_report.json",
    ]
    return [str(path).replace("\\", "/") for path in candidates if path.exists()]


def _has_preview_source(project_id: str) -> bool:
    workspace_dir = get_project_workspace_dir(project_id)
    experience_path = workspace_dir / "experience_blueprint.md"
    business_candidates = [
        workspace_dir / "business_blueprint.md",
        workspace_dir / "business_blueprint_lite.md",
        workspace_dir / "business_note.md",
    ]
    has_experience = experience_path.exists() and experience_path.is_file() and experience_path.stat().st_size > 0
    has_business = any(path.exists() and path.is_file() and path.stat().st_size > 0 for path in business_candidates)
    return has_experience and has_business


def _steps_for_execution_mode(execution_mode: str) -> list[tuple[str, Callable[[str], int]]]:
    if execution_mode == "full":
        return [
            ("generate-facts", run_generate_facts),
            ("gate-facts", run_facts_gate),
            ("generate-business", run_generate_business),
            ("gate-business", run_business_gate),
            ("generate-experience", run_generate_experience),
            ("gate-experience", run_experience_gate),
            ("validate", run_validate_outputs),
            ("coverage", run_coverage_check),
        ]
    if execution_mode == "standard":
        return [
            ("generate-facts", run_generate_facts),
            ("gate-facts", run_facts_gate),
            ("generate-business-lite", run_generate_business_lite),
            ("gate-business-lite", run_business_lite_gate),
            ("generate-experience", run_generate_experience),
            ("gate-experience-lite", run_experience_lite_gate),
            ("validate-lite", run_validate_lite),
            ("coverage-lite", run_coverage_lite),
        ]
    return [
        ("generate-facts", run_generate_facts),
        ("generate-business-note", run_generate_business_note),
        ("gate-business-note", run_business_note_gate),
        ("generate-experience", run_generate_experience),
        ("gate-experience-lite", run_experience_lite_gate),
        ("validate-lite", run_validate_lite),
    ]


def _print_repair_hint(project_id: str, command_name: str) -> None:
    if command_name.startswith("gate") or command_name in {"validate", "validate-lite", "coverage", "coverage-lite"}:
        print(
            f"当前步骤 `{command_name}` 失败，请查看 runtime/gates 或 workspace/check_status.json：{project_id}"
        )


def _formal_input_errors(project_id: str) -> list[str]:
    source_dir = get_project_source_dir(project_id)
    required_files = {
        "source/task_card.md": source_dir / "task_card.md",
        "source/requirement.md": source_dir / "requirement.md",
        "source/background.md": source_dir / "background.md",
    }
    errors: list[str] = []

    for label, path in required_files.items():
        if not path.exists() or not path.is_file():
            errors.append(f"Missing {label}")

    for label in ("source/requirement.md", "source/background.md"):
        path = required_files[label]
        if not path.exists() or not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        if any(marker in content for marker in BOOTSTRAP_PLACEHOLDER_MARKERS):
            errors.append(f"{label} still contains bootstrap placeholder content")

    return errors


def _write_execution_report(
    report_path: Path,
    project_id: str,
    status: str,
    stopped_at: str,
    steps: list[dict[str, object]],
    message: str = "",
    blocking_issue: str = "",
    execution_mode: str = "",
) -> None:
    payload = {
        "project_id": project_id,
        "status": status,
        "generated_at": _now_iso(),
        "mainline_entry": "user_confirmed_formal_blueprint_task",
        "stopped_at": stopped_at,
        "message": message,
        "blocking_issue": blocking_issue,
        "execution_mode": execution_mode,
        "steps": steps,
        "actual_outputs": _actual_outputs(project_id),
    }
    _write_json(report_path, payload)


def run_routed_main(project_id: str, route: str = "auto", skip_preview: bool = False, strict: bool = False) -> int:
    if route not in {"auto", "fast", "standard", "full"}:
        print(f"ERROR: unsupported route: {route}")
        return 1
    if route != "auto":
        print("ERROR: run-routed-main 不再支持手动指定 route，请先由 UXB 写好 runtime/uxb_route_decision.json。")
        return 1

    runtime_dir = get_project_runtime_dir(project_id)
    plan_path = runtime_dir / "routed_main_plan.json"
    report_path = runtime_dir / "routed_main_report.json"
    runtime_dir.mkdir(parents=True, exist_ok=True)

    setup_results: list[dict[str, object]] = []
    structure_code = run_project_structure_check(project_id)
    setup_results.append({"command": "project-structure-check", "exit_code": structure_code})
    if structure_code != 0:
        message = "执行发现正式蓝图主链路前半段未完成，请先完成项目目录初始化后再继续。"
        _write_execution_report(report_path, project_id, "failed", "project-structure-check", setup_results, message=message)
        print(message)
        print(f"routed_main_report.json: {report_path}")
        return 1

    input_errors = _formal_input_errors(project_id)
    if input_errors:
        message = "执行发现正式输入尚未准备完成，请先用已确认的分析结论覆盖 bootstrap 骨架后再继续。"
        _write_execution_report(
            report_path,
            project_id,
            "failed",
            "formal-inputs",
            setup_results,
            message=message,
            blocking_issue="; ".join(input_errors),
        )
        print(message)
        print("; ".join(input_errors))
        print(f"routed_main_report.json: {report_path}")
        return 1

    execution_decision = load_uxb_execution_decision(project_id)
    if str(execution_decision.get("status") or "") != "confirmed":
        route_code = run_route_decision(project_id)
        setup_results.append({"command": "route-decision", "exit_code": route_code})
        blocking_issue = "; ".join(
            str(item) for item in execution_decision.get("validation_errors", []) if str(item).strip()
        )
        message = "执行中发现当前 UXB 判断不足以驱动主链路，请先重新判断。"
        _write_execution_report(
            report_path,
            project_id,
            "needs_rejudgment",
            "precheck",
            setup_results,
            message=message,
            blocking_issue=blocking_issue,
        )
        print(message)
        if blocking_issue:
            print(blocking_issue)
        print(f"routed_main_report.json: {report_path}")
        return 1

    route_code = run_route_decision(project_id)
    setup_results.append({"command": "route-decision", "exit_code": route_code})
    if route_code == 0:
        append_command_if_provenance_exists(project_id, "route-decision")
        execution_decision = load_uxb_execution_decision(project_id)

    try:
        assemble_code = run_context_assemble(project_id, strict=strict)
    except (FileNotFoundError, SystemExit) as exc:
        assemble_code = int(exc.code) if isinstance(exc, SystemExit) and isinstance(exc.code, int) else 1
        message = str(exc)
        if message:
            print(message)
        setup_results.append({"command": "assemble", "exit_code": assemble_code, "message": message})
        _write_execution_report(report_path, project_id, "failed", "assemble", setup_results, message=message)
        print(f"routed_main_report.json: {report_path}")
        return assemble_code

    setup_results.append({"command": "assemble", "exit_code": assemble_code})
    append_command_if_provenance_exists(project_id, "assemble")
    if assemble_code != 0:
        _write_execution_report(report_path, project_id, "failed", "assemble", setup_results)
        return assemble_code

    execution_mode = str(execution_decision.get("execution_mode") or "")
    steps = _steps_for_execution_mode(execution_mode)
    plan = {
        "project_id": project_id,
        "generated_at": _now_iso(),
        "decision_source": "uxb_route_decision.json",
        "requested_route": route,
        "execution_mode": execution_mode,
        "mainline_entry": "user_confirmed_formal_blueprint_task",
        "planned_steps": [item["command"] for item in setup_results] + [name for name, _ in steps],
        "uxb_route_decision": execution_decision,
    }
    _write_json(plan_path, plan)

    results: list[dict[str, object]] = list(setup_results)
    status = "passed"
    stopped_at = ""
    for command_name, runner in steps:
        try:
            exit_code = runner(project_id)
        except SystemExit as exc:
            exit_code = int(exc.code) if isinstance(exc.code, int) else 1
            if str(exc):
                print(str(exc))
        append_command_if_provenance_exists(project_id, command_name)
        results.append({"command": command_name, "exit_code": exit_code})
        if exit_code != 0:
            status = "failed"
            stopped_at = command_name
            print(f"run-routed-main stopped at step: {command_name}")
            _print_repair_hint(project_id, command_name)
            break

    if status == "passed" and not skip_preview:
        if _has_preview_source(project_id):
            try:
                preview_code = run_experience_preview(project_id, host="127.0.0.1", port=0, serve=False)
            except SystemExit as exc:
                preview_code = int(exc.code) if isinstance(exc.code, int) else 1
                if str(exc):
                    print(str(exc))
            results.append({"command": "preview", "exit_code": preview_code})
            if preview_code == 0:
                append_command_if_provenance_exists(project_id, "preview")
        else:
            print("Preview skipped: missing usable business/experience workspace sources after mainline success.")

    report = {
        "project_id": project_id,
        "status": status,
        "generated_at": _now_iso(),
        "requested_route": route,
        "execution_mode": execution_mode,
        "mainline_entry": "user_confirmed_formal_blueprint_task",
        "stopped_at": stopped_at,
        "steps": results,
        "actual_outputs": _actual_outputs(project_id),
        "recommend_enable_routed_execution": False,
        "recommendation_reason": "当前执行判断已收敛到 UXB 已确认结果；是否默认启用，仍应基于样例和真实任务继续验证。",
    }
    _write_json(report_path, report)
    append_command_if_provenance_exists(project_id, "run-routed-main")
    print(f"routed_main_plan.json: {plan_path}")
    print(f"routed_main_report.json: {report_path}")
    if status == "passed":
        print(f"run-routed-main finished: execution_mode={execution_mode}")
    return 0 if status == "passed" else 1
