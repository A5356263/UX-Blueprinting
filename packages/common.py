from __future__ import annotations

import json
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


def get_project_preview_dir(project_id: str) -> Path:
    return get_project_runtime_dir(project_id) / "preview"


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


def get_examples_root_dir() -> Path:
    return get_repo_root() / "examples" / "benchmarks"


def get_project_meta_path(project_id: str) -> Path:
    return get_project_dir(project_id) / "meta.json"


def read_project_meta(project_id: str) -> dict[str, object]:
    path = get_project_meta_path(project_id)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def write_project_meta(project_id: str, payload: dict[str, object]) -> Path:
    path = get_project_meta_path(project_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def list_project_ids(include_excluded: bool = False) -> list[str]:
    projects_root = get_repo_root() / "projects"
    if not projects_root.exists():
        return []
    project_ids: list[str] = []
    for child in sorted(projects_root.iterdir()):
        if not child.is_dir():
            continue
        meta_path = child / "meta.json"
        if not meta_path.exists():
            continue
        project_id = child.name
        meta = read_project_meta(project_id)
        excluded = bool(meta.get("excluded_from_default_scan"))
        if excluded and not include_excluded:
            continue
        project_ids.append(project_id)
    return project_ids
