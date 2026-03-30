from __future__ import annotations

import argparse
from pathlib import Path


TEMPLATE_MAP = {
    "task_card.template.md": "task_card.md",
    "facts.template.md": "facts.md",
    "business_blueprint.template.md": "business_blueprint.md",
    "experience_blueprint.template.md": "experience_blueprint.md",
    "gap_list.template.md": "gap_list.md",
    "check_report.template.md": "check_report.md",
}


def render_template(content: str, task_id: str, task_name: str, domain: str) -> str:
    return (
        content.replace("{{TASK_ID}}", task_id)
        .replace("{{TASK_NAME}}", task_name)
        .replace("{{DOMAIN}}", domain)
    )


def write_text(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id")
    parser.add_argument("--task-name", default="Demo Task")
    parser.add_argument("--domain", default="permission")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    templates_dir = repo_root / "templates"
    task_dir = repo_root / "tasks" / "active" / args.task_id
    inputs_dir = task_dir / "inputs"
    workspace_dir = task_dir / "workspace"
    task_artifacts_dir = task_dir / "artifacts"

    for path in [
        inputs_dir / "attachments",
        workspace_dir,
        task_artifacts_dir / "context_bundle",
        task_artifacts_dir / "run_logs",
        task_artifacts_dir / "snapshots",
    ]:
        path.mkdir(parents=True, exist_ok=True)

    for template_name, output_name in TEMPLATE_MAP.items():
        template_path = templates_dir / template_name
        output_path = task_dir / output_name if output_name == "task_card.md" else workspace_dir / output_name
        rendered = render_template(
            template_path.read_text(encoding="utf-8"),
            task_id=args.task_id,
            task_name=args.task_name,
            domain=args.domain,
        )
        write_text(output_path, rendered, args.force)

    requirement_content = "\n".join(
        [
            "# Requirement",
            "",
            f"- Task ID：{args.task_id}",
            f"- Task Name：{args.task_name}",
            f"- Domain：{args.domain}",
            "- 请在此粘贴原始需求正文",
            "",
        ]
    )
    background_content = "\n".join(
        [
            "# Background",
            "",
            "- 请在此补充背景资料、约束、相关链接或历史上下文",
            "",
        ]
    )
    write_text(inputs_dir / "requirement.md", requirement_content, args.force)
    write_text(inputs_dir / "background.md", background_content, args.force)
    write_text(inputs_dir / "attachments" / ".gitkeep", "", args.force)
    write_text(task_artifacts_dir / "context_bundle" / ".gitkeep", "", args.force)
    write_text(task_artifacts_dir / "run_logs" / ".gitkeep", "", args.force)
    write_text(task_artifacts_dir / "snapshots" / ".gitkeep", "", args.force)

    print(f"Task created: {task_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
