from __future__ import annotations

import json
import re
from pathlib import Path

from packages.common import get_project_runtime_dir, get_project_workspace_dir, get_repo_root, get_specs_root_dir, get_templates_root_dir
from packages.knowledge_consumption import parse_summary_metadata
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


def _load_experience_guideline_plan(project_id: str) -> tuple[list[str], list[str], list[str]]:
    runtime_dir = get_project_runtime_dir(project_id)
    context_manifest_path = runtime_dir / "context_manifest.json"
    if not context_manifest_path.exists():
        return [], [], []

    try:
        payload = json.loads(context_manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [], [], []

    plan = payload.get("knowledge_consumption_plan")
    if not isinstance(plan, dict):
        return [], [], []
    experience_plan = plan.get("experience")
    if not isinstance(experience_plan, dict):
        return [], [], []

    def _collect(field: str) -> list[str]:
        return [
            str(item).replace("\\", "/")
            for item in experience_plan.get(field, [])
            if isinstance(item, str) and str(item).strip()
        ]

    return _collect("guideline_entry_refs"), _collect("guideline_refs"), _collect("raw_refs_from_source_refs")


def _read_context_manifest(project_id: str) -> dict[str, object] | None:
    manifest_path = get_project_runtime_dir(project_id) / "context_manifest.json"
    if not manifest_path.exists():
        return None
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _write_context_manifest(project_id: str, payload: dict[str, object]) -> None:
    manifest_path = get_project_runtime_dir(project_id) / "context_manifest.json"
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        normalized = value.replace("\\", "/").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


TOKEN_RE = re.compile(r"[A-Za-z]{3,}|[\u4e00-\u9fff]{2,8}")
TOKEN_STOPWORDS = {
    "需要",
    "判断",
    "场景",
    "方案",
    "设计",
    "任务",
    "评估",
    "当前",
    "用户",
    "系统",
    "相关",
    "原则",
    "summary",
    "readme",
    "guidelines",
}


def _extract_signal_tokens(text: str) -> list[str]:
    seen: set[str] = set()
    tokens: list[str] = []
    for match in TOKEN_RE.finditer(text.lower()):
        token = match.group(0).strip()
        if len(token) < 2 or token in TOKEN_STOPWORDS or token in seen:
            continue
        seen.add(token)
        tokens.append(token)
    return tokens


def _read_guideline_candidate_text(repo_root: Path, summary_ref: str) -> tuple[str, list[str]]:
    path = repo_root / Path(summary_ref.replace("/", "\\"))
    if not path.exists() or not path.is_file():
        return "", []

    text = path.read_text(encoding="utf-8")
    title = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            break

    trigger_lines = _extract_markdown_section(text, "## 2. 任务触发线索")[:6]
    coverage_lines = _extract_markdown_section(text, "## 3. 覆盖内容")[:4]
    candidate_text = "\n".join([title, *trigger_lines, *coverage_lines])
    matched_fragments = [line for line in trigger_lines + coverage_lines if line]
    return candidate_text, matched_fragments


def _read_summary_metadata(repo_root: Path, summary_ref: str) -> dict[str, object]:
    path = repo_root / Path(summary_ref.replace("/", "\\"))
    if not path.exists() or not path.is_file():
        return {}
    return parse_summary_metadata(path.read_text(encoding="utf-8"))


def _is_guideline_summary_metadata(metadata: dict[str, object]) -> bool:
    return metadata.get("page_type") == "summary" and metadata.get("source_group") == "guideline"


def _collect_guideline_candidate_refs(repo_root: Path, entry_refs: list[str]) -> list[str]:
    candidates: list[str] = []
    for entry_ref in entry_refs:
        normalized = entry_ref.replace("\\", "/").strip()
        if not normalized.endswith(".md"):
            continue
        entry_path = repo_root / Path(normalized.replace("/", "\\"))
        if not entry_path.exists() or not entry_path.is_file():
            continue

        if entry_path.name.lower() == "readme.md":
            sibling_refs = [
                str(item.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
                for item in sorted(entry_path.parent.glob("*.md"))
                if item.is_file() and item.name.lower() != "readme.md"
            ]
            candidates.extend(sibling_refs)

        metadata = parse_summary_metadata(entry_path.read_text(encoding="utf-8"))
        candidates.extend(
            str(item).replace("\\", "/")
            for item in metadata.get("related_summaries", [])
            if isinstance(item, str)
        )
        if entry_path.name.lower() != "readme.md":
            candidates.append(normalized)
    return _dedupe_keep_order([ref for ref in candidates if _is_guideline_summary_metadata(_read_summary_metadata(repo_root, ref))])


def _select_guidelines_from_business(business_text: str, entry_refs: list[str]) -> tuple[list[str], list[str], list[dict[str, str]]]:
    repo_root = get_repo_root()
    candidate_refs = _collect_guideline_candidate_refs(repo_root, entry_refs)
    business_text_lower = business_text.lower()
    ranked: list[tuple[int, str, str]] = []

    for summary_ref in candidate_refs:
        candidate_text, fragments = _read_guideline_candidate_text(repo_root, summary_ref)
        if not candidate_text:
            continue
        tokens = _extract_signal_tokens(candidate_text)
        matched_tokens = [token for token in tokens if token in business_text_lower]
        if not matched_tokens:
            continue
        score = len(matched_tokens)
        reason_fragment = ""
        for fragment in fragments:
            fragment_tokens = _extract_signal_tokens(fragment)
            if any(token in business_text_lower for token in fragment_tokens):
                reason_fragment = fragment
                break
        if not reason_fragment and fragments:
            reason_fragment = fragments[0]
        ranked.append((score, summary_ref, reason_fragment))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    selected_refs = [summary_ref for _, summary_ref, _ in ranked[:3]]

    selected_raw_refs: list[str] = []
    selection_reasons: list[dict[str, str]] = []
    for _, summary_ref, reason_fragment in ranked[:3]:
        summary_path = repo_root / Path(summary_ref.replace("/", "\\"))
        metadata = parse_summary_metadata(summary_path.read_text(encoding="utf-8"))
        raw_refs = [str(item).replace("\\", "/") for item in metadata.get("source_refs", []) if isinstance(item, str)]
        selected_raw_refs.extend(raw_refs[:1])
        selection_reasons.append(
            {
                "guideline": summary_ref,
                "reason": f"business_blueprint 命中了该指南的触发线索：{reason_fragment}" if reason_fragment else "business_blueprint 与该指南的任务触发线索存在明显重合。",
            }
        )

    return selected_refs, _dedupe_keep_order(selected_raw_refs), selection_reasons


def _materialize_experience_guidelines(project_id: str) -> tuple[list[str], list[str], list[str], list[dict[str, str]]]:
    manifest = _read_context_manifest(project_id)
    if not manifest:
        return [], [], [], []

    plan = manifest.get("knowledge_consumption_plan")
    if not isinstance(plan, dict):
        return [], [], [], []
    experience_plan = plan.get("experience")
    if not isinstance(experience_plan, dict):
        return [], [], [], []

    guideline_entry_refs = [
        str(item).replace("\\", "/")
        for item in experience_plan.get("guideline_entry_refs", [])
        if isinstance(item, str) and str(item).strip()
    ]
    guideline_refs = [
        str(item).replace("\\", "/")
        for item in experience_plan.get("guideline_refs", [])
        if isinstance(item, str) and str(item).strip()
    ]
    raw_refs_from_source_refs = [
        str(item).replace("\\", "/")
        for item in experience_plan.get("raw_refs_from_source_refs", [])
        if isinstance(item, str) and str(item).strip()
    ]

    reasons: list[dict[str, str]] = []
    business_text = _read_workspace_file(project_id, "business_blueprint.md")
    if not guideline_refs and guideline_entry_refs and business_text.strip():
        selected_guideline_refs, selected_guideline_raw_refs, reasons = _select_guidelines_from_business(business_text, guideline_entry_refs)
        guideline_refs = _dedupe_keep_order(selected_guideline_refs)
        raw_refs_from_source_refs = _dedupe_keep_order(raw_refs_from_source_refs + selected_guideline_raw_refs)
        experience_plan["guideline_refs"] = guideline_refs
        experience_plan["raw_refs_from_source_refs"] = raw_refs_from_source_refs
        _write_context_manifest(project_id, manifest)
    elif guideline_refs:
        reasons = [
            {
                "guideline": guideline,
                "reason": "该指南已作为 experience 阶段的明确设计指南输入进入上下文。",
            }
            for guideline in guideline_refs
        ]
    elif guideline_entry_refs:
        reasons = [
            {
                "guideline": "",
                "reason": "已保留 Design Guidelines 入口，但当前 business_blueprint 未形成足够明确的场景信号，暂未自动选中具体指南。",
            }
        ]

    guideline_source_refs: list[str] = []
    for summary_ref in guideline_entry_refs + guideline_refs:
        metadata = _read_summary_metadata(get_repo_root(), summary_ref)
        if not _is_guideline_summary_metadata(metadata):
            continue
        guideline_source_refs.extend(str(item).replace("\\", "/") for item in metadata.get("source_refs", []) if isinstance(item, str))
    guideline_raw_refs = [ref for ref in raw_refs_from_source_refs if ref in set(guideline_source_refs)]
    return guideline_entry_refs, guideline_refs, guideline_raw_refs, reasons


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
    except json.JSONDecodeError:
        return

    guideline_entry_refs, guideline_refs, guideline_raw_refs, reasons = _materialize_experience_guidelines(project_id)

    stage_usage = usage_report.setdefault("stage_usage", {})
    if not isinstance(stage_usage, dict):
        return
    experience_usage = stage_usage.setdefault("experience", {})
    if not isinstance(experience_usage, dict):
        return

    experience_usage["guideline_entry_refs"] = guideline_entry_refs
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
