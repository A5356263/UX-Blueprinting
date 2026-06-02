from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from packages.common import (
    get_env_check_report_path,
    get_knowledge_root_dir,
    get_projects_root_dir,
    get_repo_root,
    get_specs_root_dir,
    get_templates_root_dir,
    get_tmp_root_dir,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _make_check(
    check_id: str,
    status: str,
    message: str,
    *,
    fixable: bool = False,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "status": status,
        "message": message,
        "fixable": fixable,
        "details": details or {},
    }


def _status_from_checks(checks: list[dict[str, Any]]) -> str:
    statuses = {str(item.get("status") or "") for item in checks}
    if "failed" in statuses:
        return "failed"
    if "warning" in statuses:
        return "warning"
    return "passed"


def _write_report(report_path: Path, payload: dict[str, Any]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _release_core_path(repo_root: Path) -> Path:
    name = "uxb-core.exe" if os.name == "nt" else "uxb-core"
    return repo_root / "bin" / name


def _is_release_layout(repo_root: Path) -> bool:
    init_path = repo_root / "packages" / "__init__.py"
    if not init_path.exists():
        return False
    if not _release_core_path(repo_root).exists():
        return False
    try:
        marker = init_path.read_text(encoding="utf-8").strip()
    except OSError:
        return False
    return marker == '"""UXB release package thin entry."""'


def _check_required_roots(repo_root: Path) -> dict[str, Any]:
    roots = {
        "repo_root": repo_root,
        "projects_root": get_projects_root_dir(),
        "templates_root": get_templates_root_dir(),
        "specs_root": get_specs_root_dir(),
        "knowledge_root": get_knowledge_root_dir(),
    }

    missing = {name: str(path) for name, path in roots.items() if not path.exists()}
    if missing:
        return _make_check(
            "required_roots",
            "failed",
            "Release runtime roots are missing; the package cannot run stably on this machine.",
            details={"missing": missing, "resolved_roots": {name: str(path) for name, path in roots.items()}},
        )

    return _make_check(
        "required_roots",
        "passed",
        "Release runtime roots are present.",
        details={"resolved_roots": {name: str(path) for name, path in roots.items()}},
    )


def _check_release_layout(repo_root: Path) -> dict[str, Any]:
    core_path = _release_core_path(repo_root)
    packages_dir = repo_root / "packages"
    init_path = packages_dir / "__init__.py"
    main_path = packages_dir / "__main__.py"

    details = {
        "core_path": str(core_path),
        "packages_dir": str(packages_dir),
        "is_release_layout": _is_release_layout(repo_root),
    }

    if core_path.exists():
        missing = [str(path.relative_to(repo_root)) for path in (init_path, main_path) if not path.exists()]
        if missing:
            return _make_check(
                "release_layout",
                "failed",
                "Release thin-entry files are missing.",
                details={**details, "missing": missing},
            )
        return _make_check(
            "release_layout",
            "passed",
            "Release executable and thin entry files are present.",
            details=details,
        )

    return _make_check(
        "release_layout",
        "warning",
        "Release executable was not found in the current root; env-check is running outside a packaged release.",
        fixable=False,
        details=details,
    )


def _check_platform_match(repo_root: Path) -> dict[str, Any]:
    core_path = _release_core_path(repo_root)
    system_name = platform.system().lower()
    if core_path.exists():
        if os.name == "nt":
            return _make_check(
                "platform_match",
                "passed",
                "Current Windows environment matches the packaged executable format.",
                details={"platform": platform.platform(), "core_path": str(core_path)},
            )
        return _make_check(
            "platform_match",
            "failed",
            "A Windows release executable was found, but the current system is not Windows.",
            details={"platform": platform.platform(), "core_path": str(core_path)},
        )

    return _make_check(
        "platform_match",
        "warning",
        f"No packaged executable was found for explicit platform verification. Current system: {system_name}.",
        details={"platform": platform.platform()},
    )


def _check_tmp_roundtrip() -> dict[str, Any]:
    tmp_dir = get_tmp_root_dir()
    created_tmp_dir = False
    if not tmp_dir.exists():
        tmp_dir.mkdir(parents=True, exist_ok=True)
        created_tmp_dir = True

    probe_file = tmp_dir / ".env-check-utf8-probe.txt"
    probe_dir = tmp_dir / ".env-check-delete-probe"
    payload = "env-check utf-8 probe: 中文路径与内容校验\n"
    try:
        probe_file.write_text(payload, encoding="utf-8")
        restored = probe_file.read_text(encoding="utf-8")
        if restored != payload:
            return _make_check(
                "tmp_roundtrip",
                "failed",
                "UTF-8 roundtrip failed in the package temp area.",
                details={"tmp_dir": str(tmp_dir), "probe_file": str(probe_file)},
            )
        probe_dir.mkdir(exist_ok=True)
    except OSError as exc:
        return _make_check(
            "tmp_roundtrip",
            "failed",
            "The package temp area is not readable and writable.",
            details={"tmp_dir": str(tmp_dir), "error": str(exc)},
        )
    finally:
        try:
            if probe_file.exists():
                probe_file.unlink()
            if probe_dir.exists():
                probe_dir.rmdir()
        except OSError:
            pass

    if created_tmp_dir:
        return _make_check(
            "tmp_roundtrip",
            "warning",
            "The package temp area was missing and has been created successfully.",
            fixable=True,
            details={"tmp_dir": str(tmp_dir)},
        )

    return _make_check(
        "tmp_roundtrip",
        "passed",
        "The package temp area supports UTF-8 read/write and cleanup.",
        details={"tmp_dir": str(tmp_dir)},
    )


def _check_projects_writable(projects_root: Path) -> dict[str, Any]:
    created_projects_dir = False
    if not projects_root.exists():
        try:
            projects_root.mkdir(parents=True, exist_ok=True)
            created_projects_dir = True
        except OSError as exc:
            return _make_check(
                "projects_writable",
                "failed",
                "The projects directory cannot be created in the current environment.",
                details={"projects_root": str(projects_root), "error": str(exc)},
            )

    probe_path = projects_root / ".env-check-write-probe"
    try:
        probe_path.write_text("ok\n", encoding="utf-8")
        probe_path.unlink()
    except OSError as exc:
        return _make_check(
            "projects_writable",
            "failed",
            "The projects directory is not writable.",
            details={"projects_root": str(projects_root), "error": str(exc)},
        )

    if created_projects_dir:
        return _make_check(
            "projects_writable",
            "warning",
            "The projects directory was missing and has been created successfully.",
            fixable=True,
            details={"projects_root": str(projects_root)},
        )

    return _make_check(
        "projects_writable",
        "passed",
        "The projects directory is writable.",
        details={"projects_root": str(projects_root)},
    )


def _run_cli_command(command: list[str], cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part).strip()
    return int(completed.returncode), output


def _packages_command(repo_root: Path, *args: str) -> list[str]:
    if _is_release_layout(repo_root):
        return [str(_release_core_path(repo_root)), *args]
    return [sys.executable, "-m", "packages", *args]


def _check_cli_entrypoint(repo_root: Path) -> dict[str, Any]:
    command = _packages_command(repo_root, "--help")
    returncode, output = _run_cli_command(command, cwd=repo_root)
    if returncode != 0:
        return _make_check(
            "cli_entrypoint",
            "failed",
            "The package CLI entrypoint could not start.",
            details={"command": " ".join(command), "output": output},
        )
    return _make_check(
        "cli_entrypoint",
        "passed",
        "The package CLI entrypoint starts successfully.",
        details={"command": " ".join(command)},
    )


def _check_capability_listing(repo_root: Path) -> dict[str, Any]:
    command = _packages_command(repo_root, "capabilities-list")
    returncode, output = _run_cli_command(command, cwd=repo_root)
    if returncode != 0:
        return _make_check(
            "capability_listing",
            "failed",
            "The package could not list capabilities.",
            details={"command": " ".join(command), "output": output},
        )
    return _make_check(
        "capability_listing",
        "passed",
        "The package can list capabilities.",
        details={"command": " ".join(command)},
    )


def _check_run_script(repo_root: Path) -> dict[str, Any]:
    if os.name != "nt":
        return _make_check(
            "run_script",
            "warning",
            "Windows PowerShell launch script was not verified because the current system is not Windows.",
            details={"platform": platform.platform()},
        )

    script_path = repo_root / "run_packages.ps1"
    if not script_path.exists():
        return _make_check(
            "run_script",
            "failed",
            "The Windows launch script is missing.",
            details={"script_path": str(script_path)},
        )

    command = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
        "capabilities-list",
    ]
    returncode, output = _run_cli_command(command, cwd=repo_root)
    if returncode != 0:
        return _make_check(
            "run_script",
            "failed",
            "The Windows launch script could not start the package.",
            details={"command": " ".join(command), "output": output},
        )
    return _make_check(
        "run_script",
        "passed",
        "The Windows launch script can start the package.",
        details={"command": "powershell -ExecutionPolicy Bypass -File run_packages.ps1 capabilities-list"},
    )


def _check_smoke_project(repo_root: Path) -> dict[str, Any]:
    project_id = "env-check-smoke"
    projects_root = get_projects_root_dir()
    project_dir = projects_root / project_id
    if project_dir.exists():
        shutil.rmtree(project_dir, ignore_errors=True)

    commands = [
        _packages_command(
            repo_root,
            "bootstrap",
            project_id,
            "--task-name",
            "Env Check Smoke",
            "--domain",
            "权限管理",
            "--force",
        ),
        _packages_command(repo_root, "project-structure-check", project_id),
    ]
    outputs: list[dict[str, str | int]] = []
    try:
        for command in commands:
            returncode, output = _run_cli_command(command, cwd=repo_root)
            outputs.append({"command": " ".join(command), "returncode": returncode, "output": output})
            if returncode != 0:
                return _make_check(
                    "smoke_project",
                    "failed",
                    "The package could not complete the minimal bootstrap smoke flow.",
                    details={"project_id": project_id, "steps": outputs},
                )
    finally:
        shutil.rmtree(project_dir, ignore_errors=True)

    return _make_check(
        "smoke_project",
        "passed",
        "The package completed the minimal bootstrap smoke flow successfully.",
        details={"project_id": project_id, "steps": outputs},
    )


def _build_report(checks: list[dict[str, Any]], *, mode: str) -> dict[str, Any]:
    repo_root = get_repo_root()
    status = _status_from_checks(checks)
    warnings = [item["message"] for item in checks if item.get("status") == "warning"]
    errors = [item["message"] for item in checks if item.get("status") == "failed"]
    can_continue = status != "failed"
    return {
        "mode": mode,
        "status": status,
        "checked_at": _now_iso(),
        "repo_root": str(repo_root),
        "cwd": str(Path.cwd()),
        "system": {
            "platform": sys.platform,
            "platform_detail": platform.platform(),
            "python_version": sys.version,
        },
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "can_continue_mainline": can_continue,
        "recommended_next_action": (
            "The package can continue running in the current environment."
            if can_continue
            else "Fix the blocking environment issues before using this package."
        ),
    }


def _print_summary(payload: dict[str, Any], report_path: Path) -> None:
    status = str(payload.get("status") or "failed")
    checks = payload.get("checks", [])
    if not isinstance(checks, list):
        checks = []
    passed_count = sum(1 for item in checks if item.get("status") == "passed")
    warning_count = sum(1 for item in checks if item.get("status") == "warning")
    failed_count = sum(1 for item in checks if item.get("status") == "failed")

    print("env-check summary")
    print(f"- mode: {payload.get('mode')}")
    print(f"- status: {status}")
    print(f"- passed_checks: {passed_count}")
    print(f"- warning_checks: {warning_count}")
    print(f"- failed_checks: {failed_count}")
    print(f"- can_continue_mainline: {str(payload.get('can_continue_mainline')).lower()}")

    warnings = payload.get("warnings", [])
    if isinstance(warnings, list):
        for item in warnings[:5]:
            print(f"- warning: {item}")

    errors = payload.get("errors", [])
    if isinstance(errors, list):
        for item in errors[:5]:
            print(f"- error: {item}")

    print(f"- report: {report_path}")


def run_env_check() -> int:
    repo_root = get_repo_root()
    checks = [
        _check_required_roots(repo_root),
        _check_release_layout(repo_root),
        _check_platform_match(repo_root),
        _check_tmp_roundtrip(),
        _check_projects_writable(get_projects_root_dir()),
        _check_cli_entrypoint(repo_root),
        _check_capability_listing(repo_root),
        _check_run_script(repo_root),
        _check_smoke_project(repo_root),
    ]
    payload = _build_report(checks, mode="package_runtime")
    report_path = get_env_check_report_path()
    _write_report(report_path, payload)
    _print_summary(payload, report_path)
    return 0 if str(payload.get("status") or "") != "failed" else 1
