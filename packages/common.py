from __future__ import annotations

import json
import os
from pathlib import Path


UXB_COMPLEXITY_REF_MARKER = "skills/uxb/references/complexity/"


def _env_path(env_var: str, default: Path) -> Path:
    value = os.environ.get(env_var)
    return Path(value).resolve() if value else default


def get_repo_root() -> Path:
    default = Path(__file__).resolve().parent.parent
    return _env_path("UXB_ROOT", default)


def get_projects_root_dir() -> Path:
    return _env_path("UXB_PROJECTS_DIR", get_repo_root() / "projects")


def get_knowledge_root_dir() -> Path:
    return _env_path("UXB_KNOWLEDGE_DIR", get_repo_root() / "knowledge")


def get_specs_root_dir() -> Path:
    env_value = os.environ.get("UXB_SPECS_DIR")
    if env_value:
        return Path(env_value).resolve()
    return get_repo_root() / "specs"


def get_templates_root_dir() -> Path:
    env_value = os.environ.get("UXB_TEMPLATES_DIR")
    if env_value:
        return Path(env_value).resolve()
    return get_repo_root() / "templates"


def get_memory_root_dir() -> Path:
    return _env_path("UXB_MEMORY_DIR", get_repo_root() / "memory")


def get_examples_root_dir() -> Path:
    env_value = os.environ.get("UXB_EXAMPLES_DIR")
    if env_value:
        return Path(env_value).resolve()
    external_examples = get_repo_root() / "packages" / "examples"
    if external_examples.exists():
        return external_examples
    bundled_examples = Path(__file__).resolve().parent / "examples"
    return bundled_examples


def get_project_dir(project_id: str) -> Path:
    return get_projects_root_dir() / project_id


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


def normalize_repo_ref(ref: str) -> str:
    return str(ref or "").replace("\\", "/").strip().lstrip("/")


def repo_ref_to_path(ref: str) -> Path:
    normalized = normalize_repo_ref(ref)
    if not normalized:
        raise ValueError("Repository reference cannot be empty")
    if "*" in normalized or "?" in normalized:
        raise ValueError(f"Wildcard reference cannot be copied directly: {normalized}")
    return Path(*normalized.split("/"))


def to_repo_ref(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def extract_uxb_complexity_ref_suffix(ref: str) -> str | None:
    normalized = normalize_repo_ref(ref)
    marker_index = normalized.find(UXB_COMPLEXITY_REF_MARKER)
    if marker_index == -1:
        return None
    return normalized[marker_index + len(UXB_COMPLEXITY_REF_MARKER) :]


def list_project_ids(include_excluded: bool = False) -> list[str]:
    projects_root = get_projects_root_dir()
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
