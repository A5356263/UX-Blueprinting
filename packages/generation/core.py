from __future__ import annotations

import json
from pathlib import Path

from packages.common import get_project_runtime_dir, get_project_workspace_dir, get_specs_root_dir, get_templates_root_dir
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


def _read_context_manifest(project_id: str) -> dict[str, object] | None:
    manifest_path = get_project_runtime_dir(project_id) / "context_manifest.json"
    if not manifest_path.exists():
        return None
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _read_route_decision(project_id: str) -> dict[str, object] | None:
    route_path = get_project_runtime_dir(project_id) / "route_decision.json"
    if not route_path.exists():
        return None
    try:
        payload = json.loads(route_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _route_decision_prompt_lines(project_id: str, target_stage: str) -> list[str]:
    decision = _read_route_decision(project_id)
    if not decision:
        return []
    demand_type = str(decision.get("demand_type") or "不确定")
    route = str(decision.get("route") or "standard")
    confidence = str(decision.get("confidence") or "unknown")
    reason = str(decision.get("reason") or "").strip()
    pressure = "、".join(str(item) for item in decision.get("design_pressure", []) if str(item).strip())
    focus = "；".join(str(item) for item in decision.get("experience_focus", [])[:3] if str(item).strip())
    non_focus = "；".join(str(item) for item in decision.get("non_focus_guidance", [])[:2] if str(item).strip())
    lines = [
        f"- 需求类型：{demand_type}；建议路线：{route}；置信度：{confidence}。",
        f"- 重点维度：{pressure or '请结合 facts/business 补充判断'}。",
    ]
    if target_stage == "business":
        lines.append(f"- route 输出建议：{non_focus or 'route_decision 未提供非重点章节建议。'}")
    else:
        lines.append(f"- route 输出建议：{focus or 'route_decision 未提供体验重点建议。'}")
    escalation = "；".join(str(item) for item in decision.get("escalation_signals", [])[:2] if str(item).strip())
    if escalation:
        lines.append(f"- 升级信号：{escalation}")
    if reason:
        lines.append(f"- route 判断理由：{reason}")
    lines.append("- 写作规则以对应 specs 中的路线说明要求为准。")
    return lines


def _materialize_experience_guidelines(project_id: str) -> tuple[list[str], list[str], list[str], list[dict[str, str]]]:
    manifest = _read_context_manifest(project_id)
    if not manifest:
        return [], [], [], []

    references = manifest.get("references")
    if not isinstance(references, list):
        return [], [], [], []

    guideline_refs: list[str] = []
    reasons: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in references:
        if not isinstance(item, dict):
            continue
        if str(item.get("group") or "").strip() != "guideline_refs":
            continue
        reference = str(item.get("reference") or "").replace("\\", "/").strip()
        if not reference or reference in seen:
            continue
        seen.add(reference)
        guideline_refs.append(reference)
        reasons.append({"guideline": reference, "reason": str(item.get("selection_reason") or "").strip()})

    return [], guideline_refs, [], reasons


def _build_experience_prompt_preview(project_id: str) -> str:
    task_card_text = _read_source_file(project_id, "task_card.md")
    facts_text = _read_workspace_file(project_id, "facts.md")
    business_text = _read_workspace_file(project_id, "business_blueprint.md")
    gap_text = _read_workspace_file(project_id, "gap_list.md")
    contract_path = get_specs_root_dir() / "10_experience_blueprint_contract.md"
    template_path = get_templates_root_dir() / "experience_blueprint.template.md"
    guideline_entry_refs, guideline_refs, _, _ = _materialize_experience_guidelines(project_id)

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
    route_lines = _route_decision_prompt_lines(project_id, target_stage="experience")

    if not task_lines:
        task_lines = ["请结合当前任务上下文补全任务目标。"]
    if not facts_lines:
        facts_lines = ["facts.md 暂缺或内容不足，请先补齐 facts。"]
    if not business_sections:
        fallback = _first_lines(business_text, limit=12)
        business_sections = [("business 核心判断", fallback)] if fallback else [("business 核心判断", ["business_blueprint.md 暂缺或内容不足，请先补齐 business。"])]
    if not gap_lines:
        gap_lines = ["当前暂无显式待确认问题，需在生成时主动暴露不确定项。"]

    if guideline_refs:
        guideline_lines = "已选中的具体指南：\n" + "\n".join(f"- {line}" for line in guideline_refs)
    elif guideline_entry_refs:
        guideline_lines = "当前仅声明了指南入口，需先结合 business 选择具体指南：\n" + "\n".join(f"- {line}" for line in guideline_entry_refs)
    else:
        guideline_lines = "- 当前任务未命中显式指南导航，将按业务承接要求保守生成。"
    return (
        "# Experience Prompt 预览（仅调试）\n\n"
        "> 说明：此文件仅用于排查，不参与主链路生成与评审。\n"
        f"> 权威输入：`projects/{project_id}/workspace/facts.md`、`projects/{project_id}/workspace/business_blueprint.md`、`{contract_path.as_posix()}`、`{template_path.as_posix()}`\n\n"
        "## 1. 任务目标\n\n"
        + "\n".join(f"- {line}" for line in task_lines)
        + "\n\n## 2. route 判断\n\n"
        + ("\n".join(route_lines) if route_lines else "- 当前未生成 route_decision.json，按 facts 与 business 保守判断输出重点。")
        + "\n\n## 3. facts 摘要\n\n"
        + "\n".join(f"- {line}" for line in facts_lines)
        + "\n\n## 4. business 核心判断与承接要求\n\n"
        + "\n\n".join(
            f"### {section_title}\n" + "\n".join(f"- {line}" for line in section_lines)
            for section_title, section_lines in business_sections
        )
        + "\n\n## 5. 设计指南导航（按需消费）\n\n"
        + guideline_lines
        + "\n\n## 6. 设计指南消费判断\n\n"
        "在输出体验蓝图前，请基于 facts.md 和 business_blueprint.md 判断：\n"
        "1. 本次业务蓝图中是否出现报错、阻断、校验、状态反馈、审批延迟、批量风险、高风险配置等体验问题。\n"
        "2. 这些问题是否命中 Design Guidelines 中的具体 summary。\n"
        "3. 如果命中 summary，必须读取其 source_refs 指向的 raw，并只吸收原则，不暴露大段原文。\n"
        "4. 体验蓝图不得凭指南替代业务事实；业务事实不足时，只能输出待确认问题或条件型建议。\n"
        "5. 输出方案时，需要说明反馈时机、反馈形式、用户可见文案和用户下一步。\n"
        + "\n\n## 7. 设计原则摘要\n\n"
        "- 先写主流程，再补次流程与异常阻断流程。\n"
        "- 页面/弹窗/抽屉必须写清页面目标、进入条件、操作、状态反馈和异常处理。\n"
        "- 文案必须给具体草案，不写抽象策略句。\n"
        "- 禁止重做事实抽取、业务判断或需求全文重读。\n\n"
        "## 8. 待确认问题\n\n"
        + "\n".join(f"- {line}" for line in gap_lines)
        + "\n\n## 9. 输出模板要求\n\n"
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
    del project_id


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
    route_lines = _route_decision_prompt_lines(project_id, target_stage="business")
    if route_lines:
        print(f"  - projects/{project_id}/runtime/route_decision.json")
    print("  - specs/09_business_blueprint_contract.md")
    print("  - templates/business_blueprint.template.md")
    print(f"  - projects/{project_id}/workspace/facts.md")
    if route_lines:
        print("route 判断摘要：")
        for line in route_lines:
            print(f"  {line}")
    return 1


def run_generate_business_note(project_id: str) -> int:
    workspace_dir = get_project_workspace_dir(project_id)
    note_path = workspace_dir / "business_note.md"

    if note_path.exists():
        upsert_generated_provenance(project_id, "packages.generation", "generate-business-note")
        print(f"business_note.md 已存在: {note_path}")
        return 0

    print("business_note.md 不存在，请 AI 根据以下文件生成：")
    route_lines = _route_decision_prompt_lines(project_id, target_stage="business")
    if route_lines:
        print(f"  - projects/{project_id}/runtime/route_decision.json")
    print("  - specs/16_business_note_contract.md")
    print("  - templates/business_note.template.md")
    print(f"  - projects/{project_id}/workspace/facts.md")
    if route_lines:
        print("route 判断摘要：")
        for line in route_lines:
            print(f"  {line}")
    return 1


def run_generate_business_lite(project_id: str) -> int:
    workspace_dir = get_project_workspace_dir(project_id)
    business_lite_path = workspace_dir / "business_blueprint_lite.md"

    if business_lite_path.exists():
        upsert_generated_provenance(project_id, "packages.generation", "generate-business-lite")
        print(f"business_blueprint_lite.md 已存在: {business_lite_path}")
        return 0

    print("business_blueprint_lite.md 不存在，请 AI 根据以下文件生成：")
    route_lines = _route_decision_prompt_lines(project_id, target_stage="business")
    if route_lines:
        print(f"  - projects/{project_id}/runtime/route_decision.json")
    print("  - specs/17_business_blueprint_lite_contract.md")
    print("  - templates/business_blueprint_lite.template.md")
    print(f"  - projects/{project_id}/workspace/facts.md")
    if route_lines:
        print("route 判断摘要：")
        for line in route_lines:
            print(f"  {line}")
    return 1


def run_generate_experience(project_id: str) -> int:
    runtime_dir = get_project_runtime_dir(project_id)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir = get_project_workspace_dir(project_id)
    experience_path = workspace_dir / "experience_blueprint.md"

    if not experience_path.exists():
        print("experience_blueprint.md 不存在，请 AI 根据以下文件生成：")
        route_lines = _route_decision_prompt_lines(project_id, target_stage="experience")
        if route_lines:
            print(f"  - projects/{project_id}/runtime/route_decision.json")
        print("  - specs/10_experience_blueprint_contract.md")
        print("  - templates/experience_blueprint.template.md")
        print(f"  - projects/{project_id}/workspace/facts.md")
        business_lite_path = workspace_dir / "business_blueprint_lite.md"
        business_note_path = workspace_dir / "business_note.md"
        if business_lite_path.exists():
            print(f"  - projects/{project_id}/workspace/business_blueprint_lite.md")
        elif business_note_path.exists():
            print(f"  - projects/{project_id}/workspace/business_note.md")
        else:
            print(f"  - projects/{project_id}/workspace/business_blueprint.md")
        print(f"  参考示例: test/Experience_Blueprint 理想效果.md")
        if route_lines:
            print("route 判断摘要：")
            for line in route_lines:
                print(f"  {line}")
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
