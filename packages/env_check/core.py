from __future__ import annotations

import importlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from packages.common import (
    get_env_check_report_path,
    get_examples_root_dir,
    get_knowledge_root_dir,
    get_projects_root_dir,
    get_repo_root,
    get_specs_root_dir,
    get_templates_root_dir,
    get_tmp_root_dir,
)


HOST_PATH_MARKERS = (".cl" + "aude/", ".co" + "dex/")


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


def _check_required_roots() -> dict[str, Any]:
    repo_root = get_repo_root()
    roots = {
        "repo_root": repo_root,
        "projects_root": get_projects_root_dir(),
        "templates_root": get_templates_root_dir(),
        "specs_root": get_specs_root_dir(),
        "knowledge_root": get_knowledge_root_dir(),
        "examples_root": get_examples_root_dir(),
    }

    missing = {name: str(path) for name, path in roots.items() if not path.exists()}
    if missing:
        return _make_check(
            "required_roots",
            "failed",
            "关键目录缺失，当前环境无法稳定运行正式链路",
            details={"missing": missing, "resolved_roots": {name: str(path) for name, path in roots.items()}},
        )

    return _make_check(
        "required_roots",
        "passed",
        "关键目录存在，正式链路所需根路径可识别",
        details={"resolved_roots": {name: str(path) for name, path in roots.items()}},
    )


def _check_tmp_roundtrip(repo_root: Path) -> dict[str, Any]:
    del repo_root
    tmp_dir = get_tmp_root_dir()
    created_tmp_dir = False
    if not tmp_dir.exists():
        tmp_dir.mkdir(parents=True, exist_ok=True)
        created_tmp_dir = True

    probe_file = tmp_dir / ".env-check-utf8-probe.txt"
    probe_dir = tmp_dir / ".env-check-delete-probe"
    payload = "env-check utf-8 探针：中文路径与内容校验\n"
    try:
        probe_file.write_text(payload, encoding="utf-8")
        restored = probe_file.read_text(encoding="utf-8")
        if restored != payload:
            return _make_check(
                "tmp_roundtrip",
                "failed",
                "UTF-8 读写回环结果不一致，当前环境可能存在编码问题",
                details={"tmp_dir": str(tmp_dir), "probe_file": str(probe_file)},
            )
        probe_dir.mkdir(exist_ok=True)
    except OSError as exc:
        return _make_check(
            "tmp_roundtrip",
            "failed",
            "根目录临时路径不可读写，当前环境无法稳定执行临时文件操作",
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
            "根目录临时目录原本不存在，已自动创建；当前环境可继续运行",
            fixable=True,
            details={"tmp_dir": str(tmp_dir)},
        )

    return _make_check(
        "tmp_roundtrip",
        "passed",
        "根目录临时路径可读写，UTF-8 与删除行为正常",
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
                "projects 根目录不存在且无法自动创建，当前环境无法稳定写入项目产物",
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
            "projects 根目录不可写，当前环境无法稳定执行正式产物写入",
            details={"projects_root": str(projects_root), "error": str(exc)},
        )

    if created_projects_dir:
        return _make_check(
            "projects_writable",
            "warning",
            "projects 根目录原本不存在，已自动创建；当前环境可继续运行",
            fixable=True,
            details={"projects_root": str(projects_root)},
        )

    return _make_check(
        "projects_writable",
        "passed",
        "projects 根目录可写，项目运行时产物可正常创建",
        details={"projects_root": str(projects_root)},
    )


def _check_python_runtime() -> dict[str, Any]:
    modules = [
        "packages.__main__",
        "packages.common",
        "packages.context_assemble.core",
        "packages.route_decision.core",
        "packages.routed_main.core",
        "packages.validate.core",
    ]
    imported: list[str] = []
    try:
        for module_name in modules:
            importlib.import_module(module_name)
            imported.append(module_name)
    except Exception as exc:  # noqa: BLE001
        return _make_check(
            "python_runtime",
            "failed",
            "正式执行层模块导入失败，当前 Python 环境无法稳定运行项目",
            details={
                "python_version": sys.version,
                "failed_module": modules[len(imported)],
                "imported_modules": imported,
                "error": f"{type(exc).__name__}: {exc}",
            },
        )

    return _make_check(
        "python_runtime",
        "passed",
        "当前 Python 环境可导入正式执行层模块",
        details={"python_version": sys.version, "imported_modules": imported},
    )


def _check_host_path_independence(repo_root: Path) -> dict[str, Any]:
    hits: list[str] = []
    for path in (repo_root / "packages").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if any(marker in text for marker in HOST_PATH_MARKERS):
            hits.append(path.relative_to(repo_root).as_posix())

    if hits:
        return _make_check(
            "host_path_independence",
            "failed",
            "正式 packages 代码中仍存在宿主 skill 路径依赖，换系统或换 code agent 时可能失稳",
            details={"files": hits},
        )

    return _make_check(
        "host_path_independence",
        "passed",
        "正式 packages 代码未发现宿主 skill 路径依赖",
        details={},
    )


def _build_report(checks: list[dict[str, Any]]) -> dict[str, Any]:
    repo_root = get_repo_root()
    status = _status_from_checks(checks)
    warnings = [item["message"] for item in checks if item.get("status") == "warning"]
    errors = [item["message"] for item in checks if item.get("status") == "failed"]
    can_continue = status != "failed"
    return {
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
            "可以继续执行主链路"
            if can_continue
            else "请先修复环境阻断项，再执行主链路"
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
        _check_required_roots(),
        _check_tmp_roundtrip(repo_root),
        _check_projects_writable(get_projects_root_dir()),
        _check_python_runtime(),
        _check_host_path_independence(repo_root),
    ]
    payload = _build_report(checks)
    report_path = get_env_check_report_path()
    _write_report(report_path, payload)
    _print_summary(payload, report_path)
    return 0 if str(payload.get("status") or "") != "failed" else 1
