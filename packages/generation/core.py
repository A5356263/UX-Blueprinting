from __future__ import annotations

import json
from pathlib import Path

from packages.common import get_project_runtime_dir, get_project_workspace_dir
from packages.provenance import upsert_generated_provenance

from .reasoning import (
    render_check_report,
    render_check_status,
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


def _build_experience_prompt_preview(project_id: str) -> str:
    task_card_text = _read_source_file(project_id, "task_card.md")
    facts_text = _read_workspace_file(project_id, "facts.md")
    business_text = _read_workspace_file(project_id, "business_blueprint.md")
    gap_text = _read_workspace_file(project_id, "gap_list.md")
    runtime_dir = get_project_runtime_dir(project_id)
    context_manifest_path = runtime_dir / "context_manifest.json"
    contract_path = Path("specs/10_experience_blueprint_contract.md")
    template_path = Path("templates/experience_blueprint.template.md")
    guideline_refs: list[str] = []
    if context_manifest_path.exists():
        try:
            payload = json.loads(context_manifest_path.read_text(encoding="utf-8"))
            plan = payload.get("knowledge_consumption_plan")
            if isinstance(plan, dict):
                experience_plan = plan.get("experience")
                if isinstance(experience_plan, dict):
                    guideline_refs = [
                        str(item).replace("\\", "/")
                        for item in experience_plan.get("guideline_refs", [])
                        if isinstance(item, str) and str(item).strip()
                    ]
        except json.JSONDecodeError:
            guideline_refs = []

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

    guideline_lines = "\n".join(f"- {line}" for line in guideline_refs) if guideline_refs else "- 当前任务未命中显式指南导航，将按业务承接要求保守生成。"
    return (
        "# Experience Prompt 预览（仅调试）\n\n"
        "> 说明：此文件仅用于排查，不参与主链路生成与评审。\n"
        f"> 权威输入：`projects/{project_id}/workspace/facts.md`、`projects/{project_id}/workspace/business_blueprint.md`、`{contract_path.as_posix()}`、`{template_path.as_posix()}`\n\n"
        "## 1. 任务目标\n\n"
        + "\n".join(f"- {line}" for line in task_lines)
        + "\n\n## 2. facts 摘要\n\n"
        + "\n".join(f"- {line}" for line in facts_lines)
        + "\n\n## 3. business 核心判断与承接要求\n\n"
        + "\n\n".join(
            f"### {section_title}\n" + "\n".join(f"- {line}" for line in section_lines)
            for section_title, section_lines in business_sections
        )
        + "\n\n## 4. 设计指南导航（按需消费）\n\n"
        + guideline_lines
        + "\n\n## 5. 设计原则摘要\n\n"
        "- 先写主流程，再补次流程与异常阻断流程。\n"
        "- 页面/弹窗/抽屉必须写清页面目标、进入条件、操作、状态反馈和异常处理。\n"
        "- 文案必须给具体草案，不写抽象策略句。\n"
        "- 禁止重做事实抽取、业务判断或需求全文重读。\n\n"
        "## 6. 待确认问题\n\n"
        + "\n".join(f"- {line}" for line in gap_lines)
        + "\n\n## 7. 输出模板要求\n\n"
        "- 输出文件：`projects/{project_id}/workspace/experience_blueprint.md`\n"
        "- 固定章节：\n"
        "  - `## 1. 交互流程总览`\n"
        "  - `## 2. 主交互流程`\n"
        "  - `## 3. 次交互流程`\n"
        "  - `## 4. 异常与阻断流程`\n"
        "  - `## 5. 页面 / 弹窗 / 抽屉设计`\n"
        "  - `## 6. 状态与反馈文案`\n"
        "  - `## 7. 待确认问题`\n"
    )


def _update_experience_guideline_usage(project_id: str) -> None:
    runtime_dir = get_project_runtime_dir(project_id)
    usage_report_path = runtime_dir / "knowledge_usage_report.json"
    manifest_path = runtime_dir / "context_manifest.json"
    if not usage_report_path.exists() or not manifest_path.exists():
        return

    try:
        usage_report = json.loads(usage_report_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return

    plan = manifest.get("knowledge_consumption_plan")
    if not isinstance(plan, dict):
        return
    experience_plan = plan.get("experience")
    if not isinstance(experience_plan, dict):
        return

    guideline_refs = [
        str(item).replace("\\", "/")
        for item in experience_plan.get("guideline_refs", [])
        if isinstance(item, str) and str(item).strip()
    ]
    guideline_raw_refs = [
        str(item).replace("\\", "/")
        for item in experience_plan.get("raw_refs_from_source_refs", [])
        if isinstance(item, str) and "/guidelines/" in str(item).replace("\\", "/").lower()
    ]

    business_text = _read_workspace_file(project_id, "business_blueprint.md")
    reasons: list[str] = []
    if any(token in business_text for token in ("状态", "反馈", "异常", "阻断")):
        reasons.append("业务方案涉及状态反馈与异常阻断，需要补充反馈类设计指南。")
    if any(token in business_text for token in ("文案", "说明", "提示")):
        reasons.append("业务方案包含解释责任与提示语义，需要补充文案表达类设计指南。")
    if any(token in business_text for token in ("页面", "弹窗", "抽屉", "列表")):
        reasons.append("业务方案包含页面承载要求，需要补充容器与信息结构类设计指南。")
    if not reasons and guideline_refs:
        reasons.append("按方案承接要求补充通用交互设计指南，避免体验表达脱离业务边界。")

    stage_usage = usage_report.setdefault("stage_usage", {})
    if not isinstance(stage_usage, dict):
        return
    experience_usage = stage_usage.setdefault("experience", {})
    if not isinstance(experience_usage, dict):
        return

    experience_usage["guideline_refs_used"] = guideline_refs
    experience_usage["guideline_raw_refs_used"] = guideline_raw_refs
    experience_usage["guideline_selection_reason"] = reasons
    usage_report_path.write_text(json.dumps(usage_report, ensure_ascii=False, indent=2), encoding="utf-8")


def run_generate_facts(project_id: str) -> int:
    workspace_dir = get_project_workspace_dir(project_id)
    facts_path = workspace_dir / "facts.md"

    if facts_path.exists():
        upsert_generated_provenance(project_id, "packages.generation", "generate-facts")
        print(f"facts.md 已存在: {facts_path}")
        return 0

    print("facts.md 不存在，请 AI 根据以下文件生成：")
    print("  - specs/08_fact_extraction_contract.md")
    print("  - templates/facts.template.md")
    print(f"  - projects/{project_id}/source/requirement.md")
    print(f"  - projects/{project_id}/source/background.md")
    return 1


def run_generate_business(project_id: str) -> int:
    workspace_dir = get_project_workspace_dir(project_id)
    business_path = workspace_dir / "business_blueprint.md"

    if business_path.exists():
        upsert_generated_provenance(project_id, "packages.generation", "generate-business")
        print(f"business_blueprint.md 已存在: {business_path}")
        return 0

    print("business_blueprint.md 不存在，请 AI 根据以下文件生成：")
    print("  - specs/09_business_blueprint_contract.md")
    print("  - templates/business_blueprint.template.md")
    print(f"  - projects/{project_id}/workspace/facts.md")
    return 1


def run_generate_experience(project_id: str) -> int:
    runtime_dir = get_project_runtime_dir(project_id)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir = get_project_workspace_dir(project_id)
    experience_path = workspace_dir / "experience_blueprint.md"

    if not experience_path.exists():
        print("experience_blueprint.md 不存在，请 AI 根据以下文件生成：")
        print("  - specs/10_experience_blueprint_contract.md")
        print("  - templates/experience_blueprint.template.md")
        print(f"  - projects/{project_id}/workspace/facts.md")
        print(f"  - projects/{project_id}/workspace/business_blueprint.md")
        print(f"  参考示例: test/Experience_Blueprint 理想效果.md")
        return 1

    debug_dir = runtime_dir / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    debug_prompt_path = debug_dir / "experience_prompt_preview.md"
    debug_prompt_path.write_text(_build_experience_prompt_preview(project_id), encoding="utf-8")

    _update_experience_guideline_usage(project_id)
    upsert_generated_provenance(project_id, "packages.generation", "generate-experience")
    print(f"experience_blueprint.md 已存在: {experience_path}")
    print(f"调试预览文件（不参与主链路）: {debug_prompt_path}")
    return 0
