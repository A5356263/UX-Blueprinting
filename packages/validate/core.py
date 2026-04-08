from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from packages.common import (
    get_project_gates_dir,
    get_project_runtime_dir,
    get_project_source_dir,
    get_project_workspace_dir,
)


REQUIRED_HEADINGS = {
    "facts.md": ["## 任务目标", "## 业务事实清单", "## 已知约束", "## 输入来源", "## 开放问题"],
    "business_blueprint.md": ["## 场景定义", "## 核心判断", "## 关键规则与约束", "## 决策链路与依赖", "## 风险与缺口", "## 开放问题"],
    "experience_blueprint.md": ["## 体验目标", "## 关键场景", "## 体验要求", "## 原则引用", "## 风险与保护", "## 开放问题"],
    "gap_list.md": ["## Blockers", "## Warnings", "## 待补信息"],
}

FORBIDDEN_TERMS = {
    "facts.md": ["高保真", "视觉稿", "页面布局"],
    "business_blueprint.md": ["高保真", "视觉稿", "组件样式"],
    "experience_blueprint.md": ["数据库表", "接口字段", "SQL"],
}

TRACKED_OUTPUTS = [
    "facts.md",
    "business_blueprint.md",
    "experience_blueprint.md",
    "gap_list.md",
    "check_report.md",
    "check_status.json",
]

FACT_ID_PATTERN = re.compile(r"\bF-\d+\b")
GENERIC_ID_PATTERN = re.compile(r"\b[A-Z]{1,6}-\d+\b")


def get_workspace_dir(project_id: str) -> Path:
    return get_project_workspace_dir(project_id)


def get_gate_paths(project_id: str, stage: str) -> tuple[Path, Path]:
    gates_dir = get_project_gates_dir(project_id)
    gates_dir.mkdir(parents=True, exist_ok=True)
    return gates_dir / f"{stage}_gate_report.md", gates_dir / f"{stage}_gate_status.json"


def add_issue(issues: list[tuple[str, str]], level: str, message: str) -> None:
    issues.append((level, message))


def summarize_issues(issues: list[tuple[str, str]]) -> tuple[list[str], list[str], list[str], str]:
    blockers = [message for level, message in issues if level == "blocker"]
    warnings = [message for level, message in issues if level == "warning"]
    infos = [message for level, message in issues if level == "info"]

    status = "passed"
    if blockers:
        status = "failed"
    elif warnings:
        status = "warning"

    return blockers, warnings, infos, status


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def extract_fact_ids(text: str) -> list[str]:
    return sorted(set(FACT_ID_PATTERN.findall(text)))


def extract_generic_ids(text: str) -> list[str]:
    return sorted(set(GENERIC_ID_PATTERN.findall(text)))


def check_required_headings(file_name: str, content: str, issues: list[tuple[str, str]]) -> None:
    for heading in REQUIRED_HEADINGS.get(file_name, []):
        if heading not in content:
            add_issue(issues, "blocker", f"{file_name} 缺少栏目：{heading}")


def check_forbidden_terms(file_name: str, content: str, issues: list[tuple[str, str]]) -> None:
    for term in FORBIDDEN_TERMS.get(file_name, []):
        if term in content:
            add_issue(issues, "warning", f"{file_name} 可能越过阶段边界：包含 {term}")


def check_placeholders(file_name: str, content: str, issues: list[tuple[str, str]]) -> None:
    if "<填写" in content or "{{TASK_ID}}" in content or "<project-id>" in content:
        add_issue(issues, "warning", f"{file_name} 仍包含占位内容")


def render_report(
    project_id: str,
    blockers: list[str],
    warnings: list[str],
    infos: list[str],
    status: str,
    present_outputs: list[str],
) -> str:
    lines = [
        "# Check Report",
        "",
        "## Summary",
        "",
        f"- status: {status}",
        f"- has_blocker: {'true' if blockers else 'false'}",
        f"- blocker_count: {len(blockers)}",
        f"- warning_count: {len(warnings)}",
        f"- info_count: {len(infos)}",
        "",
        "## Output Status",
        "",
    ]

    for output_name in TRACKED_OUTPUTS:
        status_value = "present" if output_name in present_outputs else "missing"
        lines.append(f"- {output_name}: {status_value}")

    lines.extend(["", "## Blockers", ""])
    lines.extend([f"- {item}" for item in blockers] or ["- none"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {item}" for item in warnings] or ["- none"])
    lines.extend(["", "## Infos", ""])
    lines.extend([f"- {item}" for item in infos] or ["- none"])
    lines.extend(
        [
            "",
            "## Machine Status",
            "",
            f"- 机器可读状态文件：`projects/{project_id}/workspace/check_status.json`",
            "",
        ]
    )
    return "\n".join(lines)


def render_stage_gate_report(
    project_id: str,
    stage: str,
    next_stage: str,
    blockers: list[str],
    warnings: list[str],
    infos: list[str],
    status: str,
    checked_files: list[str],
) -> str:
    lines = [
        "# Stage Gate Report",
        "",
        "## Summary",
        "",
        f"- project_id: {project_id}",
        f"- stage: {stage}",
        f"- status: {status}",
        f"- next_stage: {next_stage}",
        f"- can_proceed: {'true' if status != 'failed' else 'false'}",
        f"- blocker_count: {len(blockers)}",
        f"- warning_count: {len(warnings)}",
        f"- info_count: {len(infos)}",
        "",
        "## Checked Files",
        "",
    ]
    lines.extend([f"- {item}" for item in checked_files] or ["- none"])
    lines.extend(["", "## Blockers", ""])
    lines.extend([f"- {item}" for item in blockers] or ["- none"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {item}" for item in warnings] or ["- none"])
    lines.extend(["", "## Infos", ""])
    lines.extend([f"- {item}" for item in infos] or ["- none"])
    return "\n".join(lines)


def build_status_payload(
    task_id: str,
    blockers: list[str],
    warnings: list[str],
    infos: list[str],
    status: str,
    completed_outputs: list[str],
    missing_outputs: list[str],
    generated_by: str,
) -> dict[str, object]:
    return {
        "task_id": task_id,
        "status": status,
        "has_blocker": bool(blockers),
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "info_count": len(infos),
        "completed_outputs": completed_outputs,
        "missing_outputs": missing_outputs,
        "generated_by": generated_by,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "issues": {
            "blockers": blockers,
            "warnings": warnings,
            "infos": infos,
        },
    }


def build_gate_payload(
    project_id: str,
    stage: str,
    next_stage: str,
    blockers: list[str],
    warnings: list[str],
    infos: list[str],
    checked_files: list[str],
) -> dict[str, object]:
    status = "passed"
    if blockers:
        status = "failed"
    elif warnings:
        status = "warning"

    return {
        "project_id": project_id,
        "stage": stage,
        "status": status,
        "can_proceed": status != "failed",
        "next_stage": next_stage,
        "generated_by": "packages.validate",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "checked_files": checked_files,
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "info_count": len(infos),
        "issues": {
            "blockers": blockers,
            "warnings": warnings,
            "infos": infos,
        },
    }


def replace_section(content: str, title: str, items: list[str]) -> str:
    lines = content.splitlines()
    new_lines: list[str] = []
    in_section = False
    replaced = False
    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped == f"## {title}":
            in_section = True
            replaced = True
            new_lines.extend([f"## {title}", ""])
            new_lines.extend([f"- {item}" for item in items] or ["- none"])
            continue
        if in_section and stripped.startswith("## "):
            in_section = False
        if not in_section:
            new_lines.append(raw_line)
    if not replaced:
        if new_lines and new_lines[-1] != "":
            new_lines.append("")
        new_lines.extend([f"## {title}", ""])
        new_lines.extend([f"- {item}" for item in items] or ["- none"])
    return "\n".join(new_lines).rstrip() + "\n"


def replace_summary(content: str, status: str, blocker_count: int, warning_count: int, info_count: int) -> str:
    lines = content.splitlines()
    new_lines: list[str] = []
    in_summary = False
    replaced = False
    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped == "## Summary":
            in_summary = True
            replaced = True
            new_lines.extend(
                [
                    "## Summary",
                    "",
                    f"- status: {status}",
                    f"- has_blocker: {'true' if blocker_count else 'false'}",
                    f"- blocker_count: {blocker_count}",
                    f"- warning_count: {warning_count}",
                    f"- info_count: {info_count}",
                ]
            )
            continue
        if in_summary and stripped.startswith("## "):
            in_summary = False
        if not in_summary:
            new_lines.append(raw_line)
    if not replaced:
        new_lines = [
            "# Check Report",
            "",
            "## Summary",
            "",
            f"- status: {status}",
            f"- has_blocker: {'true' if blocker_count else 'false'}",
            f"- blocker_count: {blocker_count}",
            f"- warning_count: {warning_count}",
            f"- info_count: {info_count}",
            "",
        ] + new_lines
    return "\n".join(new_lines).rstrip() + "\n"


def write_gate_artifacts(
    project_id: str,
    stage: str,
    next_stage: str,
    blockers: list[str],
    warnings: list[str],
    infos: list[str],
    checked_files: list[str],
) -> tuple[Path, Path, str]:
    report_path, status_path = get_gate_paths(project_id, stage)
    payload = build_gate_payload(project_id, stage, next_stage, blockers, warnings, infos, checked_files)
    report = render_stage_gate_report(project_id, stage, next_stage, blockers, warnings, infos, payload["status"], checked_files)
    report_path.write_text(report, encoding="utf-8")
    status_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return report_path, status_path, str(payload["status"])


def read_gate_status(project_id: str, stage: str) -> dict[str, object] | None:
    _, status_path = get_gate_paths(project_id, stage)
    if not status_path.exists():
        return None
    return json.loads(status_path.read_text(encoding="utf-8"))


def run_validate_outputs(project_id: str) -> int:
    workspace_dir = get_workspace_dir(project_id)
    report_path = workspace_dir / "check_report.md"
    status_path = workspace_dir / "check_status.json"
    issues: list[tuple[str, str]] = []

    for file_name, headings in REQUIRED_HEADINGS.items():
        file_path = workspace_dir / file_name
        if not file_path.exists():
            add_issue(issues, "blocker", f"{file_name} 缺失")
            continue

        content = file_path.read_text(encoding="utf-8")
        for heading in headings:
            if heading not in content:
                add_issue(issues, "blocker", f"{file_name} 缺少栏目：{heading}")

        check_forbidden_terms(file_name, content, issues)
        check_placeholders(file_name, content, issues)

    completed_outputs = [
        name
        for name in TRACKED_OUTPUTS
        if name not in {"check_report.md", "check_status.json"} and (workspace_dir / name).exists()
    ]
    add_issue(issues, "info", "结构检查已执行")

    blockers, warnings, infos, status = summarize_issues(issues)
    report_path.write_text(
        render_report(
            project_id,
            blockers,
            warnings,
            infos,
            status,
            sorted(set(completed_outputs + ["check_report.md", "check_status.json"])),
        ),
        encoding="utf-8",
    )

    completed_with_status = completed_outputs + ["check_report.md", "check_status.json"]
    missing_outputs = sorted(set(TRACKED_OUTPUTS) - set(completed_with_status))
    payload = build_status_payload(
        project_id,
        blockers,
        warnings,
        infos,
        status,
        sorted(set(completed_with_status)),
        missing_outputs,
        "packages.validate",
    )
    status_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Validation finished: {report_path}")
    print(f"Machine status written: {status_path}")
    return 0


def run_coverage_check(project_id: str) -> int:
    workspace_dir = get_workspace_dir(project_id)
    report_path = workspace_dir / "check_report.md"
    status_path = workspace_dir / "check_status.json"

    report_content = read_text(report_path)
    if not report_content:
        raise SystemExit(f"Missing report: {report_path}")
    if not status_path.exists():
        raise SystemExit(f"Missing machine status: {status_path}")

    status_data = json.loads(status_path.read_text(encoding="utf-8"))
    facts_text = read_text(workspace_dir / "facts.md")
    business_text = read_text(workspace_dir / "business_blueprint.md")
    experience_text = read_text(workspace_dir / "experience_blueprint.md")

    coverage_lines: list[str] = []
    new_warnings: list[str] = []
    fact_ids = extract_fact_ids(facts_text)

    if not fact_ids:
        message = "facts.md 中未找到事实 ID"
        coverage_lines.append(f"warning: {message}")
        new_warnings.append(message)
    else:
        for fact_id in fact_ids:
            in_business = fact_id in business_text
            in_experience = fact_id in experience_text
            if in_business or in_experience:
                coverage_lines.append(f"info: {fact_id} 已被蓝图承接")
            else:
                message = f"{fact_id} 未在业务蓝图或体验蓝图中引用"
                coverage_lines.append(f"warning: {message}")
                new_warnings.append(message)

    blockers = list(status_data.get("issues", {}).get("blockers", []))
    warnings = list(status_data.get("issues", {}).get("warnings", []))
    infos = list(status_data.get("issues", {}).get("infos", []))

    for warning in new_warnings:
        if warning not in warnings:
            warnings.append(warning)
    for line in coverage_lines or ["info: 无可检查项"]:
        if line not in infos:
            infos.append(line)

    status = "passed"
    if blockers:
        status = "failed"
    elif warnings:
        status = "warning"

    updated_report = replace_section(report_content, "Coverage Check", coverage_lines or ["info: 无可检查项"])
    updated_report = replace_section(updated_report, "Warnings", warnings)
    updated_report = replace_section(updated_report, "Infos", infos)
    updated_report = replace_summary(updated_report, status, len(blockers), len(warnings), len(infos))
    report_path.write_text(updated_report, encoding="utf-8")

    status_data["status"] = status
    status_data["has_blocker"] = bool(blockers)
    status_data["blocker_count"] = len(blockers)
    status_data["warning_count"] = len(warnings)
    status_data["info_count"] = len(infos)
    status_data["generated_by"] = "packages.validate"
    status_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    status_data.setdefault("issues", {})
    status_data["issues"]["blockers"] = blockers
    status_data["issues"]["warnings"] = warnings
    status_data["issues"]["infos"] = infos
    status_data["coverage"] = coverage_lines or ["info: 无可检查项"]
    status_path.write_text(json.dumps(status_data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Coverage check finished: {report_path}")
    print(f"Machine status updated: {status_path}")
    return 0


def run_facts_gate(project_id: str) -> int:
    source_dir = get_project_source_dir(project_id)
    runtime_dir = get_project_runtime_dir(project_id)
    workspace_dir = get_workspace_dir(project_id)
    issues: list[tuple[str, str]] = []
    checked_files = [
        f"projects/{project_id}/source/task_card.md",
        f"projects/{project_id}/source/requirement.md",
        f"projects/{project_id}/source/background.md",
        f"projects/{project_id}/runtime/task_card_resolved.json",
        f"projects/{project_id}/runtime/context_manifest.json",
        f"projects/{project_id}/workspace/facts.md",
    ]

    for path in [
        source_dir / "task_card.md",
        source_dir / "requirement.md",
        source_dir / "background.md",
        runtime_dir / "task_card_resolved.json",
        runtime_dir / "context_manifest.json",
        workspace_dir / "facts.md",
    ]:
        if not path.exists():
            add_issue(issues, "blocker", f"缺少文件：{path.relative_to(path.parents[2])}")

    facts_path = workspace_dir / "facts.md"
    facts_text = read_text(facts_path)
    if facts_text:
        check_required_headings("facts.md", facts_text, issues)
        check_forbidden_terms("facts.md", facts_text, issues)
        check_placeholders("facts.md", facts_text, issues)

        fact_ids = extract_fact_ids(facts_text)
        if not fact_ids:
            add_issue(issues, "blocker", "facts.md 未提炼出事实 ID")
        else:
            add_issue(issues, "info", f"facts.md 已提炼 {len(fact_ids)} 条事实")

        source_hits = sum(1 for path in [f"projects/{project_id}/source/requirement.md", f"projects/{project_id}/source/background.md"] if path in facts_text)
        if source_hits == 0:
            add_issue(issues, "warning", "facts.md 尚未显式引用输入来源路径")

    blockers, warnings, infos, _ = summarize_issues(issues)
    report_path, status_path, status = write_gate_artifacts(
        project_id,
        "facts",
        "business",
        blockers,
        warnings,
        infos,
        checked_files,
    )
    print(f"Facts gate finished: {report_path}")
    print(f"Facts gate status: {status_path}")
    return 0 if status != "failed" else 1


def run_business_gate(project_id: str) -> int:
    workspace_dir = get_workspace_dir(project_id)
    issues: list[tuple[str, str]] = []
    checked_files = [
        f"projects/{project_id}/workspace/facts.md",
        f"projects/{project_id}/workspace/business_blueprint.md",
        f"projects/{project_id}/runtime/gates/facts_gate_status.json",
    ]

    facts_gate = read_gate_status(project_id, "facts")
    if not facts_gate:
        add_issue(issues, "blocker", "缺少 facts 阶段 gate 结果，请先运行 gate-facts")
    elif facts_gate.get("status") == "failed":
        add_issue(issues, "blocker", "facts 阶段未通过，不能进入业务蓝图阶段")
    else:
        add_issue(issues, "info", f"facts 阶段状态：{facts_gate.get('status')}")

    facts_text = read_text(workspace_dir / "facts.md")
    business_text = read_text(workspace_dir / "business_blueprint.md")

    if not facts_text:
        add_issue(issues, "blocker", "缺少 facts.md")
    if not business_text:
        add_issue(issues, "blocker", "缺少 business_blueprint.md")

    if business_text:
        check_required_headings("business_blueprint.md", business_text, issues)
        check_forbidden_terms("business_blueprint.md", business_text, issues)
        check_placeholders("business_blueprint.md", business_text, issues)

    if facts_text and business_text:
        fact_ids = extract_fact_ids(facts_text)
        if not fact_ids:
            add_issue(issues, "blocker", "facts.md 中没有可承接的事实 ID")
        else:
            referenced = [fact_id for fact_id in fact_ids if fact_id in business_text]
            missing = [fact_id for fact_id in fact_ids if fact_id not in business_text]
            if not referenced:
                add_issue(issues, "blocker", "business_blueprint.md 未显式承接任何事实 ID")
            else:
                add_issue(issues, "info", f"business_blueprint.md 已承接 {len(referenced)} 条事实")
            if missing:
                sample = ", ".join(missing[:5])
                add_issue(issues, "warning", f"部分事实尚未在 business_blueprint.md 中显式承接：{sample}")

    blockers, warnings, infos, _ = summarize_issues(issues)
    report_path, status_path, status = write_gate_artifacts(
        project_id,
        "business",
        "experience",
        blockers,
        warnings,
        infos,
        checked_files,
    )
    print(f"Business gate finished: {report_path}")
    print(f"Business gate status: {status_path}")
    return 0 if status != "failed" else 1


def run_experience_gate(project_id: str) -> int:
    workspace_dir = get_workspace_dir(project_id)
    issues: list[tuple[str, str]] = []
    checked_files = [
        f"projects/{project_id}/workspace/facts.md",
        f"projects/{project_id}/workspace/business_blueprint.md",
        f"projects/{project_id}/workspace/experience_blueprint.md",
        f"projects/{project_id}/runtime/gates/business_gate_status.json",
    ]

    business_gate = read_gate_status(project_id, "business")
    if not business_gate:
        add_issue(issues, "blocker", "缺少 business 阶段 gate 结果，请先运行 gate-business")
    elif business_gate.get("status") == "failed":
        add_issue(issues, "blocker", "business 阶段未通过，不能进入体验蓝图阶段")
    else:
        add_issue(issues, "info", f"business 阶段状态：{business_gate.get('status')}")

    facts_text = read_text(workspace_dir / "facts.md")
    business_text = read_text(workspace_dir / "business_blueprint.md")
    experience_text = read_text(workspace_dir / "experience_blueprint.md")

    if not facts_text:
        add_issue(issues, "blocker", "缺少 facts.md")
    if not business_text:
        add_issue(issues, "blocker", "缺少 business_blueprint.md")
    if not experience_text:
        add_issue(issues, "blocker", "缺少 experience_blueprint.md")

    if experience_text:
        check_required_headings("experience_blueprint.md", experience_text, issues)
        check_forbidden_terms("experience_blueprint.md", experience_text, issues)
        check_placeholders("experience_blueprint.md", experience_text, issues)

    if facts_text and experience_text:
        fact_ids = extract_fact_ids(facts_text)
        referenced_facts = [fact_id for fact_id in fact_ids if fact_id in experience_text]
        if not referenced_facts:
            add_issue(issues, "blocker", "experience_blueprint.md 未显式承接任何事实 ID")
        else:
            add_issue(issues, "info", f"experience_blueprint.md 已承接 {len(referenced_facts)} 条事实")

        all_ids = extract_generic_ids(experience_text)
        principle_ids = [item for item in all_ids if item not in fact_ids]
        if not principle_ids:
            add_issue(issues, "blocker", "experience_blueprint.md 未显式引用任何原则 ID")
        else:
            add_issue(issues, "info", f"experience_blueprint.md 已引用 {len(principle_ids)} 个原则 ID")

    blockers, warnings, infos, _ = summarize_issues(issues)
    report_path, status_path, status = write_gate_artifacts(
        project_id,
        "experience",
        "final-validate",
        blockers,
        warnings,
        infos,
        checked_files,
    )
    print(f"Experience gate finished: {report_path}")
    print(f"Experience gate status: {status_path}")
    return 0 if status != "failed" else 1
