from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from packages.common import (
    get_project_runtime_dir,
    get_project_source_dir,
    get_project_workspace_dir,
    get_repo_root,
)

from .business_reasoner import build_business_model
from .experience_reasoner import build_experience_model
from .facts_reasoner import build_facts_model
from .interaction_map_schema import load_interaction_map_payload, validate_interaction_map_payload


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _clip(text: str, max_chars: int = 6000) -> str:
    cleaned = text.strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars].rstrip() + "\n\n[...内容过长，已截断用于输入包展示...]"


def _extract_knowledge_summary(project_id: str) -> tuple[list[str], list[str]]:
    runtime_dir = get_project_runtime_dir(project_id)
    usage_report_path = runtime_dir / "knowledge_usage_report.json"
    if not usage_report_path.exists():
        return [], []
    try:
        payload = json.loads(usage_report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [], []
    if not isinstance(payload, dict):
        return [], []

    business_hits: list[str] = []
    guideline_hits: list[str] = []
    for item in payload.get("business", []) if isinstance(payload.get("business"), list) else []:
        if isinstance(item, str) and item.strip():
            business_hits.append(item.strip())
    for item in payload.get("experience", []) if isinstance(payload.get("experience"), list) else []:
        if isinstance(item, str) and item.strip():
            guideline_hits.append(item.strip())
    return business_hits[:8], guideline_hits[:12]


def build_experience_map_input(project_id: str) -> str:
    source_dir = get_project_source_dir(project_id)
    workspace_dir = get_project_workspace_dir(project_id)
    requirement_text = _read_text(source_dir / "requirement.md")
    background_text = _read_text(source_dir / "background.md")
    facts_text = _read_text(workspace_dir / "facts.md")
    business_text = _read_text(workspace_dir / "business_blueprint.md")

    facts_model = build_facts_model(project_id)
    business_model = build_business_model(project_id, facts_model)
    experience_model = build_experience_model(project_id, facts_model, business_model)

    business_hits, guideline_hits = _extract_knowledge_summary(project_id)
    pages_summary = [f"{page.page_id} {page.name}：{page.primary_task}" for page in experience_model.pages[:8]]
    flow_summary = [f"{flow.flow_id} {flow.name}：{flow.key_steps}" for flow in experience_model.task_flows[:8]]
    state_summary = [f"{state.state_id} {state.name}：{state.page_feedback}" for state in experience_model.state_feedbacks[:8]]
    copy_summary = [f"{item.copy_id} {item.scenario}：{item.semantic_goal}" for item in experience_model.copy_contracts[:8]]
    risk_summary = [f"{risk.risk_id} {risk.name}：{risk.protection}" for risk in experience_model.risks[:8]]
    judgment_summary = [f"{item.judgment_id} {item.title}：{item.conclusion}" for item in business_model.judgments[:8]]
    fact_summary = [f"{item.fact_id}：{item.text}" for item in (facts_model.action_facts + facts_model.state_facts + facts_model.rule_facts)[:12]]

    return (
        "# Experience Map Input Package\n\n"
        "## 1. Task\n"
        f"- project_id: {project_id}\n"
        f"- task_goal: {experience_model.experience_goal}\n"
        f"- task_boundary: {experience_model.task_boundary}\n\n"
        "## 2. Raw Requirement Key Sections\n"
        "以下为原始需求关键片段（包含页面、流程、状态、异常、文案语义）：\n\n"
        "### requirement.md\n"
        f"{_clip(requirement_text) if requirement_text else '缺失 requirement.md'}\n\n"
        "### background.md\n"
        f"{_clip(background_text) if background_text else '缺失 background.md'}\n\n"
        "## 3. Facts Summary\n"
        + "\n".join(f"- {line}" for line in fact_summary)
        + "\n\n## 4. Business Judgments\n"
        + "\n".join(f"- {line}" for line in judgment_summary)
        + "\n\n## 5. Experience Model Summary\n"
        + "### pages\n"
        + ("\n".join(f"- {line}" for line in pages_summary) or "- 无")
        + "\n\n### flows\n"
        + ("\n".join(f"- {line}" for line in flow_summary) or "- 无")
        + "\n\n### states\n"
        + ("\n".join(f"- {line}" for line in state_summary) or "- 无")
        + "\n\n### copy\n"
        + ("\n".join(f"- {line}" for line in copy_summary) or "- 无")
        + "\n\n### risks\n"
        + ("\n".join(f"- {line}" for line in risk_summary) or "- 无")
        + "\n\n## 6. Design Principles\n"
        + ("### business knowledge hits\n" + "\n".join(f"- {line}" for line in business_hits) if business_hits else "### business knowledge hits\n- 无")
        + "\n\n"
        + ("### guideline hits\n" + "\n".join(f"- {line}" for line in guideline_hits) if guideline_hits else "### guideline hits\n- 无")
        + "\n\n## 7. Required Output\n"
        "- 主输出：interaction_map.json\n"
        "- 可选输出：interaction_map_draft.md\n"
        "- 严禁仅输出自由 Markdown 作为主结果\n\n"
        "## 8. Grounding Materials Snapshot\n"
        "### facts.md（截断）\n"
        f"{_clip(facts_text, max_chars=3000) if facts_text else '缺失 facts.md'}\n\n"
        "### business_blueprint.md（截断）\n"
        f"{_clip(business_text, max_chars=3000) if business_text else '缺失 business_blueprint.md'}\n"
    )


def write_experience_map_input(project_id: str) -> Path:
    runtime_dir = get_project_runtime_dir(project_id)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    output_path = runtime_dir / "experience_map_input.md"
    output_path.write_text(build_experience_map_input(project_id) + "\n", encoding="utf-8")
    return output_path


def write_experience_map_prompt(project_id: str) -> Path:
    runtime_dir = get_project_runtime_dir(project_id)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    template_path = get_repo_root() / "templates" / "experience_map_composer.prompt.md"
    prompt_text = _read_text(template_path)
    if not prompt_text:
        prompt_text = "# Experience Map Composer Prompt\n\n请生成 interaction_map.json。"
    output_path = runtime_dir / "experience_map_prompt.md"
    output_path.write_text(prompt_text + "\n", encoding="utf-8")
    return output_path


def run_prepare_experience_map(project_id: str) -> int:
    input_path = write_experience_map_input(project_id)
    prompt_path = write_experience_map_prompt(project_id)
    print(f"Prepared experience map input: {input_path}")
    print(f"Prepared experience map prompt: {prompt_path}")
    return 0


def run_validate_experience_map(project_id: str) -> int:
    payload = load_interaction_map_payload(project_id)
    if payload is None:
        print("缺少 interaction_map.json：需要 Code Agent 根据 experience_map_prompt.md 生成。")
        return 1
    blockers, warnings = validate_interaction_map_payload(payload)
    if blockers:
        print("interaction_map 校验失败：")
        for item in blockers:
            print(f"- BLOCKER: {item}")
        for item in warnings:
            print(f"- WARNING: {item}")
        return 1
    print("interaction_map 校验通过。")
    for item in warnings:
        print(f"- WARNING: {item}")
    return 0
