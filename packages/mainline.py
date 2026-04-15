from __future__ import annotations

import json
from pathlib import Path

from packages.archive import run_archive_artifacts
from packages.common import (
    get_project_exports_dir,
    get_project_runtime_dir,
    list_project_ids,
    read_project_meta,
)
from packages.context_assemble import run_context_assemble
from packages.experience_preview import run_experience_preview
from packages.generation import run_generate_business, run_generate_experience, run_generate_facts
from packages.provenance import append_command_if_provenance_exists
from packages.repair_loop import run_repair_plan
from packages.validate import (
    run_business_gate,
    run_coverage_check,
    run_experience_gate,
    run_facts_gate,
    run_validate_outputs,
)


def _run_step(project_id: str, command_name: str, runner) -> int:
    exit_code = runner(project_id)
    append_command_if_provenance_exists(project_id, command_name)
    return exit_code


def run_main(project_id: str, skip_preview: bool = False) -> int:
    steps = [
        ("assemble", run_context_assemble),
        ("generate-facts", run_generate_facts),
        ("gate-facts", run_facts_gate),
        ("generate-business", run_generate_business),
        ("gate-business", run_business_gate),
        ("generate-experience", run_generate_experience),
        ("gate-experience", run_experience_gate),
        ("validate", run_validate_outputs),
        ("coverage", run_coverage_check),
        ("archive", run_archive_artifacts),
    ]

    for command_name, runner in steps:
        exit_code = _run_step(project_id, command_name, runner)
        if exit_code != 0:
            print(f"run-main stopped at step: {command_name}")
            return exit_code

    append_command_if_provenance_exists(project_id, "run-main")
    if skip_preview:
        print("run-main finished without preview.")
        return 0

    try:
        preview_code = run_experience_preview(project_id, host="127.0.0.1", port=0, serve=False)
    except SystemExit as exc:
        print(f"Preview failed after archive, but mainline remains successful: {exc}")
        return 0
    if preview_code != 0:
        print("Preview failed after archive, but mainline remains successful.")
        return 0
    append_command_if_provenance_exists(project_id, "preview")
    return 0


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _classify_samples() -> tuple[list[str], list[str]]:
    positive: list[str] = []
    negative: list[str] = []
    for project_id in list_project_ids(include_excluded=True):
        meta = read_project_meta(project_id)
        role = str(meta.get("project_role") or "")
        if role == "benchmark_positive":
            positive.append(project_id)
        elif role == "benchmark_negative":
            negative.append(project_id)
    if not positive and Path("projects/real-self-apply-v1").exists():
        positive.append("real-self-apply-v1")
    if not negative and Path("projects/demo-smoke-v1").exists():
        negative.append("demo-smoke-v1")
    return positive, negative


def _positive_sample_issues(project_id: str) -> list[str]:
    issues: list[str] = []
    workspace_status = _read_json(Path(f"projects/{project_id}/workspace/check_status.json"))
    preview_runtime = _read_json(Path(f"projects/{project_id}/runtime/preview/preview_runtime.json"))
    provenance = _read_json(Path(f"projects/{project_id}/runtime/provenance.json"))
    if workspace_status.get("status") != "passed":
        issues.append(f"{project_id}: status 不是 passed")
    if int(workspace_status.get("blocker_count", 1)) != 0:
        issues.append(f"{project_id}: blocker_count 不是 0")
    if int(workspace_status.get("warning_count", 1)) != 0:
        issues.append(f"{project_id}: warning_count 不是 0")
    final_dir = get_project_exports_dir(project_id) / "final"
    for file_name in ["facts.md", "business_blueprint.md", "experience_blueprint.md"]:
        if not (final_dir / file_name).exists():
            issues.append(f"{project_id}: 缺少正式产物 {file_name}")
    if str(preview_runtime.get("ready_state") or "") not in {"built", "ready"}:
        issues.append(f"{project_id}: preview 未生成")
    if str(provenance.get("generation_mode") or "") != "generated":
        issues.append(f"{project_id}: provenance 非 generated")
    return issues


def _negative_sample_issues(project_id: str) -> list[str]:
    issues: list[str] = []
    workspace_status = _read_json(Path(f"projects/{project_id}/workspace/check_status.json"))
    blocker_count = int(workspace_status.get("blocker_count", 0))
    status = str(workspace_status.get("status") or "")
    if not (status == "failed" or blocker_count > 0):
        issues.append(f"{project_id}: 反例未暴露失败状态或 blocker")
    repair_code = run_repair_plan(project_id)
    if repair_code != 0:
        issues.append(f"{project_id}: repair-plan 未能生成修复计划")
    return issues


def run_sample_check() -> int:
    positive, negative = _classify_samples()
    issues: list[str] = []
    for project_id in positive:
        issues.extend(_positive_sample_issues(project_id))
    for project_id in negative:
        issues.extend(_negative_sample_issues(project_id))

    runtime_dir = get_project_runtime_dir("sample-check")
    runtime_dir.mkdir(parents=True, exist_ok=True)
    report_path = runtime_dir / "sample_check_report.json"
    report = {
        "positive_samples": positive,
        "negative_samples": negative,
        "issue_count": len(issues),
        "issues": issues,
        "status": "passed" if not issues else "failed",
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Sample check report: {report_path}")
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}")
        return 1
    print("Sample check passed.")
    return 0
