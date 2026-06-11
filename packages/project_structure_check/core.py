from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path

from packages.common import (
    get_project_dir,
    get_project_exports_dir,
    get_project_meta_path,
    get_project_runtime_dir,
    get_project_source_dir,
    get_project_structure_check_json_path,
    get_project_structure_check_md_path,
    get_project_workspace_dir,
)


WORKSPACE_FORBIDDEN_PATTERNS = ["*.template.md", "*template*", "*log*", "*debug*", "*diagnosis*", "*.bak"]
WORKSPACE_FORBIDDEN_EXACT = {
    "facts.template.md",
    "business_blueprint.template.md",
    "experience_blueprint.template.md",
    "diagnosis.md",
    "log.md",
    "debug.md",
}
WORKSPACE_ALLOWED = {"check_report.md", "check_status.json", "gap_list.md"}

SOURCE_FORBIDDEN_EXACT = {
    "check_status.json",
    "check_report.md",
    "routed_main_report.json",
    "routed_main_plan.json",
    "context_manifest.json",
    "knowledge_trace.json",
}
SOURCE_FORBIDDEN_PATTERNS = ["*_gate_status.json", "*_gate_report.json"]

RUNTIME_ROOT_FORBIDDEN = {
    "facts.md",
    "business_blueprint.md",
    "business_blueprint_lite.md",
    "business_note.md",
    "experience_blueprint.md",
    "gap_list.md",
}

EXPORTS_FORBIDDEN_PATTERNS = ["*debug*", "*diagnosis*", "*.tmp"]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _missing_required_entries(project_id: str) -> list[str]:
    required_paths: list[tuple[str, Path]] = [
        ("source/", get_project_source_dir(project_id)),
        ("workspace/", get_project_workspace_dir(project_id)),
        ("runtime/", get_project_runtime_dir(project_id)),
        ("meta.json", get_project_meta_path(project_id)),
    ]
    missing: list[str] = []
    for label, path in required_paths:
        if not path.exists():
            missing.append(label)
    return missing


def _issue(severity: str, path: str, reason: str, suggestion: str) -> dict[str, str]:
    return {
        "severity": severity,
        "path": path,
        "reason": reason,
        "suggestion": suggestion,
    }


def _matches_any(name: str, patterns: list[str]) -> bool:
    lowered = name.lower()
    return any(fnmatch(lowered, pattern.lower()) for pattern in patterns)


def _repo_like(project_id: str, relative_path: str) -> str:
    return f"projects/{project_id}/{relative_path}".replace("\\", "/")


def _workspace_issues(project_id: str) -> list[dict[str, str]]:
    workspace_dir = get_project_workspace_dir(project_id)
    issues: list[dict[str, str]] = []
    if not workspace_dir.exists():
        return issues

    for child in sorted(workspace_dir.iterdir()):
        if not child.is_file():
            continue
        name = child.name
        lowered = name.lower()
        if lowered in WORKSPACE_ALLOWED:
            continue
        if lowered in WORKSPACE_FORBIDDEN_EXACT or _matches_any(name, WORKSPACE_FORBIDDEN_PATTERNS):
            issues.append(
                _issue(
                    "blocker",
                    _repo_like(project_id, f"workspace/{name}"),
                    "workspace 是正式产物目录，不应混入模板、诊断、日志或调试文件。",
                    "请移动到 source/notes/、runtime/diagnostics/ 或保留在 templates/ 中。",
                )
            )
    return issues


def _source_issues(project_id: str) -> list[dict[str, str]]:
    source_dir = get_project_source_dir(project_id)
    issues: list[dict[str, str]] = []
    if not source_dir.exists():
        return issues

    for child in sorted(source_dir.iterdir()):
        if not child.is_file():
            continue
        name = child.name
        lowered = name.lower()
        if lowered in SOURCE_FORBIDDEN_EXACT or _matches_any(name, SOURCE_FORBIDDEN_PATTERNS):
            issues.append(
                _issue(
                    "blocker",
                    _repo_like(project_id, f"source/{name}"),
                    "source 是输入资料目录，不应放运行状态文件。",
                    "请移动到 runtime/ 或等待对应检查阶段自动生成。",
                )
            )
    return issues


def _runtime_issues(project_id: str) -> list[dict[str, str]]:
    runtime_dir = get_project_runtime_dir(project_id)
    issues: list[dict[str, str]] = []
    if not runtime_dir.exists():
        return issues

    for child in sorted(runtime_dir.iterdir()):
        if not child.is_file():
            continue
        name = child.name.lower()
        if name in RUNTIME_ROOT_FORBIDDEN:
            issues.append(
                _issue(
                    "blocker",
                    _repo_like(project_id, f"runtime/{child.name}"),
                    "runtime 根目录不应放正式蓝图主产物。",
                    "请移动到 workspace/，或保留在 runtime/context_bundle/ 作为装配资料。",
                )
            )
    return issues


def _exports_issues(project_id: str) -> list[dict[str, str]]:
    exports_dir = get_project_exports_dir(project_id)
    issues: list[dict[str, str]] = []
    if not exports_dir.exists():
        return issues

    for child in sorted(exports_dir.iterdir()):
        name = child.name
        if _matches_any(name, EXPORTS_FORBIDDEN_PATTERNS):
            issues.append(
                _issue(
                    "warning",
                    _repo_like(project_id, f"exports/{name}"),
                    "exports 是归档目录，不建议混入调试、诊断或临时文件。",
                    "请移出 exports/，或只在 runtime/ 中保留调试材料。",
                )
            )
    return issues


def _task_id_consistency_issues(project_id: str) -> list[dict[str, str]]:
    task_card_path = get_project_source_dir(project_id) / "task_card.md"
    if not task_card_path.exists():
        return []

    text = task_card_path.read_text(encoding="utf-8")
    match = re.search(r"^\s*-\s*Task ID\s*:\s*(.+?)\s*$", text, re.MULTILINE)
    if not match:
        return [
            _issue(
                "warning",
                _repo_like(project_id, "source/task_card.md"),
                "task_card.md 存在，但无法解析其中声明的 Task ID。",
                "请在 Protocol 区补齐 `- Task ID: <project-id>`。",
            )
        ]

    declared_task_id = match.group(1).strip()
    if declared_task_id == project_id:
        return []

    return [
        _issue(
            "blocker",
            _repo_like(project_id, "source/task_card.md"),
            f"task_card.md 中声明的 Task ID 为 `{declared_task_id}`，与当前项目 `{project_id}` 不一致。",
            "请修正 task_card.md 中的 Task ID，或为新任务创建独立项目目录。",
        )
    ]


def _collect_issues(project_id: str, missing: list[str]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for item in missing:
        issues.append(
            _issue(
                "blocker",
                _repo_like(project_id, item),
                "项目基础目录或元数据缺失。",
                "请补齐 bootstrap 最小结构后再继续。",
            )
        )
    issues.extend(_workspace_issues(project_id))
    issues.extend(_source_issues(project_id))
    issues.extend(_runtime_issues(project_id))
    issues.extend(_exports_issues(project_id))
    issues.extend(_task_id_consistency_issues(project_id))
    return issues


def _status_from_issues(issues: list[dict[str, str]]) -> str:
    if any(item["severity"] == "blocker" for item in issues):
        return "failed"
    if any(item["severity"] == "warning" for item in issues):
        return "warning"
    return "passed"


def _write_report(project_id: str, status: str, missing: list[str], issues: list[dict[str, str]]) -> None:
    json_path = get_project_structure_check_json_path(project_id)
    md_path = get_project_structure_check_md_path(project_id)
    project_dir = get_project_dir(project_id)

    payload = {
        "project_id": project_id,
        "status": status,
        "checked_at": _now_iso(),
        "project_dir": str(project_dir).replace("\\", "/"),
        "required_entries": ["source/", "workspace/", "runtime/", "meta.json"],
        "missing_entries": missing,
        "issues": issues,
        "blocker_count": sum(1 for item in issues if item["severity"] == "blocker"),
        "warning_count": sum(1 for item in issues if item["severity"] == "warning"),
    }
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if status == "passed":
        if md_path.exists():
            md_path.unlink()
        return

    lines = [
        "# Project Structure Check",
        "",
        f"- project_id: `{project_id}`",
        f"- status: `{status}`",
        f"- checked_at: `{payload['checked_at']}`",
        f"- project_dir: `{payload['project_dir']}`",
        "",
        "## Required Entries",
        "",
        "- `source/`",
        "- `workspace/`",
        "- `runtime/`",
        "- `meta.json`",
    ]
    if missing:
        lines.extend(["", "## Missing Entries", ""])
        lines.extend(f"- `{item}`" for item in missing)
    if issues:
        lines.extend(["", "## Issues", ""])
        for item in issues:
            lines.append(f"- [{item['severity']}] `{item['path']}`")
            lines.append(f"  原因：{item['reason']}")
            lines.append(f"  建议：{item['suggestion']}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_project_structure_check(project_id: str) -> int:
    missing = _missing_required_entries(project_id)
    issues = _collect_issues(project_id, missing)
    status = _status_from_issues(issues)
    _write_report(project_id, status, missing, issues)
    if status == "failed":
        blocker_paths = [item["path"] for item in issues if item["severity"] == "blocker"]
        print(
            "Project structure check failed: "
            + ", ".join(blocker_paths[:5])
            + ("" if len(blocker_paths) <= 5 else ", ...")
        )
        return 1
    if status == "warning":
        print(f"Project structure check warning: {project_id}")
        return 0
    print(f"Project structure check passed: {project_id}")
    return 0
