from __future__ import annotations

import json
from pathlib import Path

from packages.archive import run_archive_artifacts
from packages.common import (
    get_examples_root_dir,
    get_project_preview_dir,
    get_project_remediation_dir,
    get_project_runtime_dir,
)
from packages.context_assemble import run_context_assemble
from packages.experience_preview import run_experience_preview
from packages.generation import (
    run_generate_business,
    run_generate_experience,
    run_generate_facts,
)
from packages.provenance import append_command_if_provenance_exists
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


def _print_run_main_repair_guidance(project_id: str, command_name: str) -> None:
    remediation_dir = get_project_remediation_dir(project_id)
    summary_path = remediation_dir / "repair_summary.md"
    retry_scope_path = remediation_dir / "retry_scope.json"

    if command_name in {"gate-facts", "gate-business", "gate-experience", "validate", "coverage"}:
        print(f"当前步骤 `{command_name}` 失败，请执行：python -m packages repair-plan {project_id}")
        if summary_path.exists() or retry_scope_path.exists():
            print("如已有 remediation 产物，请优先读取：")
            if summary_path.exists():
                print(f"- {summary_path}")
            if retry_scope_path.exists():
                print(f"- {retry_scope_path}")
        return

    if command_name == "archive":
        print(f"当前步骤 `{command_name}` 被阻断，建议先执行：python -m packages repair-status {project_id}")
        if summary_path.exists():
            print(f"并查看：{summary_path}")


def run_main(project_id: str, skip_preview: bool = False, strict: bool = False) -> int:
    steps = [
        ("assemble", lambda current_project_id: run_context_assemble(current_project_id, strict=strict)),
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
        try:
            exit_code = _run_step(project_id, command_name, runner)
        except SystemExit as exc:
            if str(exc):
                print(str(exc))
            print(f"run-main stopped at step: {command_name}")
            _print_run_main_repair_guidance(project_id, command_name)
            return int(exc.code) if isinstance(exc.code, int) else 1
        if exit_code != 0:
            print(f"run-main stopped at step: {command_name}")
            _print_run_main_repair_guidance(project_id, command_name)
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
    preview_runtime = _read_json(get_project_preview_dir(project_id) / "preview_runtime.json")
    preview_url = str(preview_runtime.get("preview_url") or "").strip()
    output_path = str(preview_runtime.get("output_path") or "").strip()
    if preview_url:
        print(f"本地预览地址：{preview_url}")
    else:
        fallback_output = output_path or f"projects/{project_id}/runtime/preview/index.html"
        print("Preview 已生成，但当前环境未启动本地服务。")
        print(f"静态预览文件：{fallback_output}")
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


def _list_example_dirs() -> list[tuple[str, str, Path]]:
    examples_root = get_examples_root_dir()
    category_roles = {
        "positive": "benchmark_positive",
        "negative": "benchmark_negative",
    }
    discovered: list[tuple[str, str, Path]] = []
    for category, default_role in category_roles.items():
        category_dir = examples_root / category
        if not category_dir.exists():
            continue
        for child in sorted(category_dir.iterdir()):
            if not child.is_dir():
                continue
            meta = _read_json(child / "meta.json")
            if not meta:
                continue
            example_id = str(meta.get("project_id") or child.name)
            role = str(meta.get("project_role") or default_role)
            discovered.append((example_id, role, child))
    return discovered


def _classify_samples() -> tuple[list[tuple[str, Path]], list[tuple[str, Path]]]:
    positive: list[tuple[str, Path]] = []
    negative: list[tuple[str, Path]] = []
    for example_id, role, example_dir in _list_example_dirs():
        if role == "benchmark_positive":
            positive.append((example_id, example_dir))
        elif role == "benchmark_negative":
            negative.append((example_id, example_dir))
    return positive, negative


def _positive_sample_issues(project_id: str, example_dir: Path) -> list[str]:
    issues: list[str] = []
    required_files = [
        example_dir / "meta.json",
        example_dir / "source" / "task_card.md",
        example_dir / "runtime" / "uxb_route_decision.json",
        example_dir / "runtime" / "context_manifest.json",
    ]
    for file_path in required_files:
        if not file_path.exists():
            issues.append(f"{project_id}: missing benchmark artifact {file_path.name}")

    manifest = _read_json(example_dir / "runtime" / "context_manifest.json")
    if manifest.get("warnings"):
        issues.append(f"{project_id}: context_manifest.json still contains warnings")

    workspace_status = _read_json(example_dir / "workspace" / "check_status.json")
    if workspace_status:
        if workspace_status.get("status") != "passed":
            issues.append(f"{project_id}: workspace status is not passed")
        if int(workspace_status.get("blocker_count", 1)) != 0:
            issues.append(f"{project_id}: workspace blocker_count is not 0")
    return issues


def _negative_sample_issues(project_id: str, example_dir: Path) -> list[str]:
    issues: list[str] = []
    workspace_status = _read_json(example_dir / "workspace" / "check_status.json")
    remediation_plan = _read_json(example_dir / "runtime" / "remediation" / "remediation_plan.json")
    if not remediation_plan:
        issues.append(f"{project_id}: missing remediation_plan.json")
        return issues

    blocker_count = int(workspace_status.get("blocker_count", 0))
    open_issue_count = int(remediation_plan.get("open_issue_count", 0))
    remediation_blockers = int(remediation_plan.get("blocker_count", 0))
    status = str(workspace_status.get("status") or "")
    if not (status == "failed" or blocker_count > 0 or remediation_blockers > 0 or open_issue_count > 0):
        issues.append(f"{project_id}: negative benchmark does not expose blocking or remediation pressure")
    return issues


def run_sample_check() -> int:
    positive, negative = _classify_samples()
    issues: list[str] = []
    if not positive:
        issues.append("missing benchmark_positive sample under packages/examples/positive/")
    if not negative:
        issues.append("missing benchmark_negative sample under packages/examples/negative/")
    for project_id, example_dir in positive:
        issues.extend(_positive_sample_issues(project_id, example_dir))
    for project_id, example_dir in negative:
        issues.extend(_negative_sample_issues(project_id, example_dir))

    runtime_dir = get_examples_root_dir() / "_runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    report_path = runtime_dir / "sample_check_report.json"
    report = {
        "positive_samples": [project_id for project_id, _ in positive],
        "negative_samples": [project_id for project_id, _ in negative],
        "issue_count": len(issues),
        "issues": issues,
        "status": "passed" if not issues else "failed",
        "examples_root": str(get_examples_root_dir()).replace("\\", "/"),
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Sample check report: {report_path}")
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}")
        return 1
    print("Sample check passed.")
    return 0
