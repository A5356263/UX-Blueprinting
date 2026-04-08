from __future__ import annotations

import json
from pathlib import Path

from packages.common import (
    get_project_dir,
    get_project_exports_dir,
    get_project_gates_dir,
    get_project_source_dir,
    get_project_workspace_dir,
    get_repo_root,
)


TEMPLATE_MAP = {
    "task_card.template.md": ("source", "task_card.md"),
    "facts.template.md": ("workspace", "facts.md"),
    "business_blueprint.template.md": ("workspace", "business_blueprint.md"),
    "experience_blueprint.template.md": ("workspace", "experience_blueprint.md"),
    "gap_list.template.md": ("workspace", "gap_list.md"),
    "check_report.template.md": ("workspace", "check_report.md"),
    "check_status.template.json": ("workspace", "check_status.json"),
}


def render_template(content: str, project_id: str, task_name: str, domain: str) -> str:
    return (
        content.replace("{{TASK_ID}}", project_id)
        .replace("{{TASK_NAME}}", task_name)
        .replace("{{DOMAIN}}", domain)
    )


def write_text(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_task_bootstrap(
    project_id: str,
    task_name: str = "Demo Task",
    domain: str = "permission",
    force: bool = False,
) -> int:
    repo_root = get_repo_root()
    templates_dir = repo_root / "templates"
    project_dir = get_project_dir(project_id)
    source_dir = get_project_source_dir(project_id)
    workspace_dir = get_project_workspace_dir(project_id)
    gates_dir = get_project_gates_dir(project_id)
    exports_dir = get_project_exports_dir(project_id)

    for path in [source_dir, workspace_dir, gates_dir, exports_dir]:
        path.mkdir(parents=True, exist_ok=True)

    for template_name, (target, output_name) in TEMPLATE_MAP.items():
        template_path = templates_dir / template_name
        output_root = source_dir if target == "source" else workspace_dir
        output_path = output_root / output_name
        rendered = render_template(
            template_path.read_text(encoding="utf-8"),
            project_id=project_id,
            task_name=task_name,
            domain=domain,
        )
        write_text(output_path, rendered, force)

    requirement_content = "\n".join(
        [
            "# Requirement",
            "",
            f"- Project ID: {project_id}",
            f"- Task Name: {task_name}",
            f"- Domain: {domain}",
            "- 请在这里粘贴原始需求正文。",
            "",
        ]
    )
    background_content = "\n".join(
        [
            "# Background",
            "",
            "- 请在这里补充背景资料、约束、相关链接或历史上下文。",
            "- 如果目前信息不足，也请显式写出缺失信息。",
            "",
        ]
    )

    write_text(source_dir / "requirement.md", requirement_content, force)
    write_text(source_dir / "background.md", background_content, force)
    write_text(
        project_dir / "meta.json",
        json.dumps(
            {
                "project_id": project_id,
                "task_name": task_name,
                "domain": domain,
                "status": "draft",
            },
            ensure_ascii=False,
            indent=2,
        ),
        force,
    )

    print(f"Project created: {project_dir}")
    return 0
