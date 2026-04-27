from __future__ import annotations

from pathlib import Path

from packages.common import get_project_runtime_dir, get_project_workspace_dir
from packages.provenance import upsert_generated_provenance

from .reasoning import (
    build_business_model,
    build_facts_model,
    render_business_markdown,
    render_check_report,
    render_check_status,
    render_facts_markdown,
    render_gap_list,
)


def _write_workspace_file(project_id: str, file_name: str, content: str) -> None:
    workspace_dir = get_project_workspace_dir(project_id)
    workspace_dir.mkdir(parents=True, exist_ok=True)
    (workspace_dir / file_name).write_text(content, encoding="utf-8")


def _read_workspace_file(project_id: str, file_name: str) -> str:
    file_path = get_project_workspace_dir(project_id) / file_name
    if not file_path.exists():
        return ""
    return file_path.read_text(encoding="utf-8")


def _read_source_file(project_id: str, file_name: str) -> str:
    source_path = get_project_workspace_dir(project_id).parent / "source" / file_name
    if not source_path.exists():
        return ""
    return source_path.read_text(encoding="utf-8")


def _extract_bullets(text: str, limit: int = 10) -> list[str]:
    bullets: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            value = stripped[2:].strip()
            if value:
                bullets.append(value)
        if len(bullets) >= limit:
            break
    return bullets


def _first_lines(text: str, limit: int = 12) -> list[str]:
    result: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        result.append(stripped[2:].strip() if stripped.startswith("- ") else stripped)
        if len(result) >= limit:
            break
    return result


def _extract_markdown_section(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    collecting = False
    collected: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == heading:
            collecting = True
            continue
        if collecting and stripped.startswith("## "):
            break
        if not collecting:
            continue
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        collected.append(stripped[2:].strip() if stripped.startswith("- ") else stripped)
    return collected


def _build_experience_blueprint_input(project_id: str) -> str:
    task_card_text = _read_source_file(project_id, "task_card.md")
    facts_text = _read_workspace_file(project_id, "facts.md")
    business_text = _read_workspace_file(project_id, "business_blueprint.md")
    gap_text = _read_workspace_file(project_id, "gap_list.md")

    task_lines = _extract_bullets(task_card_text, limit=8)
    facts_lines = _first_lines(facts_text, limit=12)
    business_section_titles = [
        "## 5. 推荐业务方案",
        "## 6. 必须守住的规则和边界",
        "## 7. 主要风险与保护策略",
        "## 8. 方案承接要求",
        "## 9. 待确认问题",
    ]
    business_sections: list[tuple[str, list[str]]] = []
    for title in business_section_titles:
        section_lines = _extract_markdown_section(business_text, title)
        if section_lines:
            business_sections.append((title.replace("## ", "", 1), section_lines[:12]))
    gap_lines = _extract_bullets(gap_text, limit=8)

    if not task_lines:
        task_lines = ["请结合当前任务上下文补全任务目标。"]
    if not facts_lines:
        facts_lines = ["facts.md 暂缺或内容不足，请先补齐 facts。"]
    if not business_sections:
        fallback = _first_lines(business_text, limit=12)
        business_sections = [("business 核心判断", fallback)] if fallback else [("business 核心判断", ["business_blueprint.md 暂缺或内容不足，请先补齐 business。"])]
    if not gap_lines:
        gap_lines = ["当前暂无显式待确认问题，需在生成时主动暴露不确定项。"]

    return (
        "# Experience Blueprint 输入包\n\n"
        "## 1. 任务目标\n\n"
        + "\n".join(f"- {line}" for line in task_lines)
        + "\n\n## 2. facts 摘要\n\n"
        + "\n".join(f"- {line}" for line in facts_lines)
        + "\n\n## 3. business 核心判断与承接要求\n\n"
        + "\n\n".join(
            f"### {section_title}\n" + "\n".join(f"- {line}" for line in section_lines)
            for section_title, section_lines in business_sections
        )
        + "\n\n## 4. 设计原则摘要\n\n"
        "- 先写主流程，再补次流程与异常阻断流程。\n"
        "- 页面/弹窗/抽屉必须写清页面目标、进入条件、操作、状态反馈和异常处理。\n"
        "- 文案必须给具体草案，不写抽象策略句。\n"
        "- 禁止重做事实抽取、业务判断或需求全文重读。\n\n"
        "## 5. 待确认问题\n\n"
        + "\n".join(f"- {line}" for line in gap_lines)
        + "\n\n## 6. 输出模板要求\n\n"
        "- 输出文件：`projects/{project_id}/workspace/experience_blueprint.md`\n"
        "- 固定章节：\n"
        "  - `## 1. 体验结论`\n"
        "  - `## 2. 主交互流程`\n"
        "  - `## 3. 次交互流程`\n"
        "  - `## 4. 异常与阻断流程`\n"
        "  - `## 5. 页面 / 弹窗 / 抽屉设计`\n"
        "  - `## 6. 状态与反馈文案`\n"
        "  - `## 7. 待确认问题`\n"
        "  - `## 附录：依据与追踪`\n"
    )


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
    runtime_dir = get_project_runtime_dir(project_id)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    input_path = runtime_dir / "experience_blueprint_input.md"
    input_path.write_text(_build_experience_blueprint_input(project_id), encoding="utf-8")

    experience_path = get_project_workspace_dir(project_id) / "experience_blueprint.md"
    upsert_generated_provenance(project_id, "packages.generation", "generate-experience")
    print(f"已生成输入包: {input_path}")
    if experience_path.exists():
        print(f"检测到已有体验蓝图: {experience_path}")
        return 0
    print("请根据 runtime/experience_blueprint_input.md 生成 workspace/experience_blueprint.md")
    return 0
