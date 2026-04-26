from __future__ import annotations

from packages.common import get_project_workspace_dir
from packages.provenance import upsert_generated_provenance

from .reasoning import (
    build_business_model,
    build_experience_model,
    build_facts_model,
    render_business_markdown,
    render_check_report,
    render_check_status,
    render_experience_markdown,
    render_facts_markdown,
    render_gap_list,
    run_prepare_experience_map as _run_prepare_experience_map,
    run_validate_experience_map as _run_validate_experience_map,
)


def _write_workspace_file(project_id: str, file_name: str, content: str) -> None:
    workspace_dir = get_project_workspace_dir(project_id)
    workspace_dir.mkdir(parents=True, exist_ok=True)
    (workspace_dir / file_name).write_text(content, encoding="utf-8")


def run_generate_facts(project_id: str) -> int:
    facts_model = build_facts_model(project_id)
    _write_workspace_file(project_id, "facts.md", render_facts_markdown(facts_model))
    _write_workspace_file(project_id, "gap_list.md", render_gap_list())
    _write_workspace_file(project_id, "check_report.md", render_check_report())
    _write_workspace_file(project_id, "check_status.json", render_check_status(project_id))
    upsert_generated_provenance(project_id, "packages.generation", "generate-facts")
    print(f"Generated facts: {get_project_workspace_dir(project_id) / 'facts.md'}")
    return 0


def run_generate_business(project_id: str) -> int:
    facts_model = build_facts_model(project_id)
    business_model = build_business_model(project_id, facts_model)
    _write_workspace_file(project_id, "business_blueprint.md", render_business_markdown(business_model))
    upsert_generated_provenance(project_id, "packages.generation", "generate-business")
    print(f"Generated business blueprint: {get_project_workspace_dir(project_id) / 'business_blueprint.md'}")
    return 0


def run_generate_experience(project_id: str) -> int:
    facts_model = build_facts_model(project_id)
    business_model = build_business_model(project_id, facts_model)
    experience_model = build_experience_model(project_id, facts_model, business_model)
    _write_workspace_file(project_id, "experience_blueprint.md", render_experience_markdown(experience_model))
    upsert_generated_provenance(project_id, "packages.generation", "generate-experience")
    print(f"Generated experience blueprint: {get_project_workspace_dir(project_id) / 'experience_blueprint.md'}")
    return 0


def run_prepare_experience_map(project_id: str) -> int:
    exit_code = _run_prepare_experience_map(project_id)
    if exit_code == 0:
        upsert_generated_provenance(project_id, "packages.generation", "prepare-experience-map")
    return exit_code


def run_validate_experience_map(project_id: str) -> int:
    exit_code = _run_validate_experience_map(project_id)
    if exit_code == 0:
        upsert_generated_provenance(project_id, "packages.generation", "validate-experience-map")
    return exit_code
