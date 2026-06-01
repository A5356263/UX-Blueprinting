from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from packages.common import (
    get_project_dir,
    get_project_meta_path,
    get_project_runtime_dir,
    get_project_source_dir,
    get_project_structure_check_json_path,
    get_project_structure_check_md_path,
    get_project_workspace_dir,
)


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


def _write_report(project_id: str, status: str, missing: list[str]) -> None:
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
    }
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

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
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_project_structure_check(project_id: str) -> int:
    missing = _missing_required_entries(project_id)
    status = "failed" if missing else "passed"
    _write_report(project_id, status, missing)
    if missing:
        print(
            "Project structure check failed: missing "
            + ", ".join(missing)
            + f" in project {project_id}"
        )
        return 1
    print(f"Project structure check passed: {project_id}")
    return 0
