from __future__ import annotations

from pathlib import Path


def get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_project_dir(project_id: str) -> Path:
    return get_repo_root() / "projects" / project_id


def get_project_source_dir(project_id: str) -> Path:
    return get_project_dir(project_id) / "source"


def get_project_workspace_dir(project_id: str) -> Path:
    return get_project_dir(project_id) / "workspace"


def get_project_runtime_dir(project_id: str) -> Path:
    return get_project_dir(project_id) / "runtime"


def get_project_exports_dir(project_id: str) -> Path:
    return get_project_dir(project_id) / "exports"


def get_project_gates_dir(project_id: str) -> Path:
    return get_project_runtime_dir(project_id) / "gates"


def get_project_remediation_dir(project_id: str) -> Path:
    return get_project_runtime_dir(project_id) / "remediation"


def get_project_memory_dir(project_id: str) -> Path:
    return get_project_runtime_dir(project_id) / "memory"


def get_memory_root_dir() -> Path:
    return get_repo_root() / "memory"
