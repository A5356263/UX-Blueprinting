from __future__ import annotations

import json

from packages.common import (
    get_project_runtime_dir,
    get_project_workspace_dir,
    get_specs_root_dir,
    get_templates_root_dir,
    sanitize_json_text,
)
from packages.provenance import upsert_generated_provenance


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


def _read_business_workspace_context(project_id: str) -> tuple[str, str]:
    for file_name in ("business_blueprint.md", "business_blueprint_lite.md", "business_note.md"):
        content = _read_workspace_file(project_id, file_name)
        if content:
            return file_name, content
    return "business_blueprint.md", ""


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
        if not stripped or stripped.startswith("#"):
            continue
        collected.append(stripped[2:].strip() if stripped.startswith("- ") else stripped)
    return collected


def _read_context_manifest(project_id: str) -> dict[str, object] | None:
    manifest_path = get_project_runtime_dir(project_id) / "context_manifest.json"
    if not manifest_path.exists():
        return None
    try:
        payload = json.loads(sanitize_json_text(manifest_path.read_text(encoding="utf-8")))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _read_uxb_route_decision(project_id: str) -> dict[str, object] | None:
    decision_path = get_project_runtime_dir(project_id) / "uxb_route_decision.json"
    if not decision_path.exists():
        return None
    try:
        payload = json.loads(sanitize_json_text(decision_path.read_text(encoding="utf-8")))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _clean_list(value: object, limit: int | None = None) -> list[str]:
    if not isinstance(value, list):
        return []
    items = [str(item).strip() for item in value if str(item).strip()]
    return items[:limit] if limit is not None else items


def _stage_knowledge_refs(project_id: str, stage: str) -> tuple[list[str], list[str], dict[str, str]]:
    manifest = _read_context_manifest(project_id)
    if not manifest:
        return [], [], {}

    summary_refs: list[str] = []
    raw_refs: list[str] = []
    reason_map: dict[str, str] = {}
    references = manifest.get("references")
    if isinstance(references, list):
        for item in references:
            if not isinstance(item, dict):
                continue
            consumed_by = [str(value).strip() for value in item.get("consumed_by", []) if str(value).strip()]
            if stage not in consumed_by:
                continue
            reference = str(item.get("reference") or "").replace("\\", "/").strip()
            if not reference or reference in reason_map:
                continue
            if reference.startswith("knowledge/raw/"):
                raw_refs.append(reference)
            else:
                summary_refs.append(reference)
            reason_map[reference] = str(item.get("selection_reason") or "").strip()

    return _clean_list(summary_refs), _clean_list(raw_refs), reason_map


def _uxb_judgment_prompt_lines(project_id: str, target_stage: str) -> list[str]:
    decision = _read_uxb_route_decision(project_id)
    if not decision:
        return []

    business_depth = str(decision.get("business_depth") or "").strip()
    experience_output = str(decision.get("experience_output") or "").strip()
    execution = decision.get("execution")
    if not isinstance(execution, dict):
        execution = {}
    required_outputs = "、".join(_clean_list(execution.get("required_outputs"), limit=6))
    execution_notes = "；".join(_clean_list(execution.get("notes"), limit=3))

    lines: list[str] = []
    if target_stage == "business" and business_depth:
        lines.append(f"- 这次需要达到的业务判断深度：{business_depth}")
    if target_stage == "experience" and experience_output:
        lines.append(f"- 这次需要产出的体验结果：{experience_output}")
    if required_outputs:
        lines.append(f"- 本次主链路必须产出的文件：{required_outputs}")
    if execution_notes:
        lines.append(f"- 本次执行提示：{execution_notes}")
    lines.append("- 这里只读取执行控制信息，不把 runtime 当成需求语义来源。")
    return lines


def _materialize_experience_guidelines(project_id: str) -> tuple[list[str], list[str], list[str], list[dict[str, str]]]:
    summary_refs, raw_refs, reason_map = _stage_knowledge_refs(project_id, "experience")
    guideline_refs: list[str] = []
    reasons: list[dict[str, str]] = []
    for reference in [*summary_refs, *raw_refs]:
        normalized = reference.replace("\\", "/").strip()
        if "设计准则" not in normalized and "guideline" not in normalized.lower():
            continue
        guideline_refs.append(normalized)
        reasons.append({"guideline": normalized, "reason": reason_map.get(normalized, "")})

    return [], guideline_refs, raw_refs, reasons


def _build_experience_prompt_preview(project_id: str) -> str:
    task_card_text = _read_source_file(project_id, "task_card.md")
    business_file_name, business_text = _read_business_workspace_context(project_id)
    gap_text = _read_workspace_file(project_id, "gap_list.md")
    contract_path = get_specs_root_dir() / "10_experience_blueprint_contract.md"
    template_path = get_templates_root_dir() / "experience_blueprint.template.md"
    guideline_entry_refs, guideline_refs, stage_raw_refs, _ = _materialize_experience_guidelines(project_id)

    task_lines = _extract_bullets(task_card_text, limit=8)
    business_section_titles = [
        "## 5. 推荐业务方案",
        "## 6. 必须守住的规则和边界",
        "## 7. 主要风险与保护策略",
        "## 8. 方案承接要求",
        "## 9. 待确认问题",
        "## 2. 关键业务规则",
        "## 3. 边界与风险",
        "## 4. 体验承接要求",
        "## 2. 核心业务规则影响",
        "## 3. 体验可承接内容",
        "## 5. 待确认问题",
    ]
    business_sections: list[tuple[str, list[str]]] = []
    for title in business_section_titles:
        section_lines = _extract_markdown_section(business_text, title)
        if section_lines:
            business_sections.append((title.replace("## ", "", 1), section_lines[:12]))
    gap_lines = _extract_bullets(gap_text, limit=8)
    judgment_lines = _uxb_judgment_prompt_lines(project_id, target_stage="experience")

    if not task_lines:
        task_lines = ["请结合当前任务上下文补全任务目标。"]
    if not business_sections:
        fallback = _first_lines(business_text, limit=12)
        if fallback:
            business_sections = [("business 核心判断", fallback)]
        else:
            business_sections = [("business 核心判断", [f"{business_file_name} 暂缺或内容不足，请先补齐 business。"])]
    if not gap_lines:
        gap_lines = ["当前暂无显式待确认问题，但仍需主动筛出是否存在影响核心判断的关键待确认。"]

    if guideline_refs:
        guideline_lines = "已装配的设计参考：\n" + "\n".join(f"- {line}" for line in guideline_refs)
    elif guideline_entry_refs:
        guideline_lines = "当前仅声明了设计参考入口，需要先结合同批已装配内容判断具体引用：\n" + "\n".join(
            f"- {line}" for line in guideline_entry_refs
        )
    else:
        guideline_lines = "- 当前任务未装配显式设计参考，将按业务承接要求保守生成。"

    raw_lines = (
        "当前阶段允许读取的 raw：\n" + "\n".join(f"- {line}" for line in stage_raw_refs)
        if stage_raw_refs
        else "- 当前阶段未登记额外 raw；如 summary 已足够，不要默认升级 raw。"
    )

    return (
        "# Experience Prompt 预览（仅调试）\n\n"
        "> 说明：此文件仅用于排查，不参与主链路生成与评审。\n"
        f"> 权威输入：`projects/{project_id}/workspace/{business_file_name}`、`{contract_path.as_posix()}`、`{template_path.as_posix()}`\n\n"
        "## 1. 任务目标\n\n"
        + "\n".join(f"- {line}" for line in task_lines)
        + "\n\n## 2. UXB 判断摘要\n\n"
        + ("\n".join(judgment_lines) if judgment_lines else "- 当前未提供 uxb_route_decision.json，请先补齐 UXB 判断后再执行主链路。")
        + "\n\n## 3. business 核心判断与承接要求\n\n"
        + "\n\n".join(
            f"### {section_title}\n" + "\n".join(f"- {line}" for line in section_lines)
            for section_title, section_lines in business_sections
        )
        + "\n\n## 4. 设计参考\n\n"
        + guideline_lines
        + "\n\n## 5. 当前阶段 raw\n\n"
        + raw_lines
        + "\n\n## 6. 知识使用规则\n\n"
        "- 只使用 UXB AI 明确指定并已经装配到 context 的知识与设计参考。\n"
        "- 不根据关键词自动补充其他知识，也不自动扩展额外原文材料。\n"
        "- 如 summary 已足够，不要因为进入正式主链路就默认继续读取 raw。\n"
        "- 如果 facts 或 business 事实不足，只能暴露缺口与待确认项，不能自行补判断。\n"
        "- 输出方案时，需要说清反馈时机、反馈形式、用户可见文案和用户下一步。\n"
        + "\n\n## 7. 设计原则摘要\n\n"
        "- 先写旅程图，再写交互流程总览、主流程、次流程与异常阻断流程。\n"
        "- 旅程图必须基于角色路径正式生成，不得从 HTML 或交互流程反推。\n"
        "- 旅程图使用“角色：节点 → 节点 → 节点”的路径表达；依据不足时进入“旅程缺口”，不要把依据和规则塞回路径节点。\n"
        "- 只有 `## 6. 页面 / 弹窗 / 抽屉设计` 中的“页面结构”部分允许使用 ASCII 框图；其他章节一律不要使用 ASCII 框图。\n"
        "- `## 2. 交互流程总览` 必须使用分角色流程节点表达，不得写成 ASCII 框图、字符边框图或终端布局图。\n"
        "- `## 4. 次交互流程` 不能退化成一整段自然语言说明，必须写出清晰的步骤结构、节点感或分段层次，但不要死套固定模板。\n"
        "- 页面 / 弹窗 / 抽屉必须写清页面目标、进入条件、操作、状态反馈和异常处理。\n"
        "- 状态与反馈文案优先收敛为统一状态口径表，不重复完整流程说明。\n"
        "- 附录除设计指南消费外，还要说明业务知识如何转成体验策略与落点。\n"
        "- 文案必须给具体草案，不写抽象策略句。\n"
        "- 禁止重做事实抽取、业务判断或需求全文重述。\n\n"
        "## 8. 待确认问题\n\n"
        + "\n".join(f"- {line}" for line in gap_lines)
        + "\n\n## 9. 输出模板要求\n\n"
        f"- 输出文件：`projects/{project_id}/workspace/experience_blueprint.md`\n"
        "- 固定章节：\n"
        "- `## 1. 旅程图`\n"
        "- `## 2. 交互流程总览`\n"
        "- `## 3. 主交互流程`\n"
        "- `## 4. 次交互流程`\n"
        "- `## 5. 异常与阻断流程`\n"
        "- `## 6. 页面 / 弹窗 / 抽屉设计`\n"
        "- `## 7. 状态与反馈文案`\n"
        "- `## 8. 待确认问题`\n"
        "- 额外格式约束：除 `## 6. 页面 / 弹窗 / 抽屉设计` 的页面结构部分外，其他章节不要输出 ASCII 框图。\n"
        "- 次交互流程额外要求：必须明显不是一段话，至少要能看出步骤边界、节点感或分段层次。\n"
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
    facts_summary_refs, facts_raw_refs, _ = _stage_knowledge_refs(project_id, "facts")
    print("  - specs/08_fact_extraction_contract.md")
    print("  - templates/facts.template.md")
    print(f"  - projects/{project_id}/source/requirement.md")
    print(f"  - projects/{project_id}/source/background.md")
    if facts_summary_refs:
        print("当前阶段允许读取的 summary：")
        for ref in facts_summary_refs:
            print(f"  - {ref}")
    if facts_raw_refs:
        print("当前阶段允许读取的 raw：")
        for ref in facts_raw_refs:
            print(f"  - {ref}")
    return 1


def run_generate_business(project_id: str) -> int:
    workspace_dir = get_project_workspace_dir(project_id)
    business_path = workspace_dir / "business_blueprint.md"

    if business_path.exists():
        upsert_generated_provenance(project_id, "packages.generation", "generate-business")
        print(f"business_blueprint.md 已存在: {business_path}")
        return 0

    print("business_blueprint.md 不存在，请 AI 根据以下文件生成：")
    judgment_lines = _uxb_judgment_prompt_lines(project_id, target_stage="business")
    business_summary_refs, business_raw_refs, _ = _stage_knowledge_refs(project_id, "business")
    if judgment_lines:
        print(f"  - projects/{project_id}/runtime/uxb_route_decision.json")
    print("  - specs/09_business_blueprint_contract.md")
    print("  - templates/business_blueprint.template.md")
    print(f"  - projects/{project_id}/workspace/facts.md")
    if business_summary_refs:
        print("当前阶段允许读取的 summary：")
        for ref in business_summary_refs:
            print(f"  - {ref}")
    if business_raw_refs:
        print("当前阶段允许读取的 raw：")
        for ref in business_raw_refs:
            print(f"  - {ref}")
    if judgment_lines:
        print("UXB 判断摘要：")
        for line in judgment_lines:
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
    judgment_lines = _uxb_judgment_prompt_lines(project_id, target_stage="business")
    business_summary_refs, business_raw_refs, _ = _stage_knowledge_refs(project_id, "business")
    if judgment_lines:
        print(f"  - projects/{project_id}/runtime/uxb_route_decision.json")
    print("  - specs/16_business_note_contract.md")
    print("  - templates/business_note.template.md")
    print(f"  - projects/{project_id}/workspace/facts.md")
    if business_summary_refs:
        print("当前阶段允许读取的 summary：")
        for ref in business_summary_refs:
            print(f"  - {ref}")
    if business_raw_refs:
        print("当前阶段允许读取的 raw：")
        for ref in business_raw_refs:
            print(f"  - {ref}")
    if judgment_lines:
        print("UXB 判断摘要：")
        for line in judgment_lines:
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
    judgment_lines = _uxb_judgment_prompt_lines(project_id, target_stage="business")
    business_summary_refs, business_raw_refs, _ = _stage_knowledge_refs(project_id, "business")
    if judgment_lines:
        print(f"  - projects/{project_id}/runtime/uxb_route_decision.json")
    print("  - specs/17_business_blueprint_lite_contract.md")
    print("  - templates/business_blueprint_lite.template.md")
    print(f"  - projects/{project_id}/workspace/facts.md")
    if business_summary_refs:
        print("当前阶段允许读取的 summary：")
        for ref in business_summary_refs:
            print(f"  - {ref}")
    if business_raw_refs:
        print("当前阶段允许读取的 raw：")
        for ref in business_raw_refs:
            print(f"  - {ref}")
    if judgment_lines:
        print("UXB 判断摘要：")
        for line in judgment_lines:
            print(f"  {line}")
    return 1


def run_generate_experience(project_id: str) -> int:
    workspace_dir = get_project_workspace_dir(project_id)
    experience_path = workspace_dir / "experience_blueprint.md"

    if not experience_path.exists():
        print("experience_blueprint.md 不存在，请 AI 根据以下文件生成：")
        judgment_lines = _uxb_judgment_prompt_lines(project_id, target_stage="experience")
        experience_summary_refs, experience_raw_refs, _ = _stage_knowledge_refs(project_id, "experience")
        if judgment_lines:
            print(f"  - projects/{project_id}/runtime/uxb_route_decision.json")
        print("  - specs/10_experience_blueprint_contract.md")
        print("  - templates/experience_blueprint.template.md")
        business_lite_path = workspace_dir / "business_blueprint_lite.md"
        business_note_path = workspace_dir / "business_note.md"
        if business_lite_path.exists():
            print(f"  - projects/{project_id}/workspace/business_blueprint_lite.md")
        elif business_note_path.exists():
            print(f"  - projects/{project_id}/workspace/business_note.md")
        else:
            print(f"  - projects/{project_id}/workspace/business_blueprint.md")
        if experience_summary_refs:
            print("当前阶段允许读取的 summary：")
            for ref in experience_summary_refs:
                print(f"  - {ref}")
        if experience_raw_refs:
            print("当前阶段允许读取的 raw：")
            for ref in experience_raw_refs:
                print(f"  - {ref}")
        if judgment_lines:
            print("UXB 判断摘要：")
            for line in judgment_lines:
                print(f"  {line}")
        return 1

    _update_experience_guideline_usage(project_id)
    upsert_generated_provenance(project_id, "packages.generation", "generate-experience")
    print(f"experience_blueprint.md 已存在: {experience_path}")
    return 0
