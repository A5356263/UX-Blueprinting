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

GUIDELINE_ROUTE_RULES: list[tuple[list[str], list[str], str]] = [
    (
        ["信息", "结构", "模块", "分组", "页面", "归属", "层级", "开始"],
        [
            "knowledge/wiki/summaries/设计准则/信息架构.md",
            "knowledge/wiki/summaries/设计准则/视觉.md",
            "knowledge/wiki/summaries/设计准则/认知.md",
        ],
        "facts/business 出现信息组织、页面结构或模块分组信号。",
    ),
    (
        ["流程", "步骤", "闭环", "前后", "连续", "任务"],
        [
            "knowledge/wiki/summaries/设计准则/流程模式.md",
            "knowledge/wiki/summaries/设计准则/可用性.md",
            "knowledge/wiki/summaries/设计准则/认知.md",
        ],
        "facts/business 出现操作流程、步骤拆分或任务闭环信号。",
    ),
    (
        ["报错", "失败", "阻断", "校验", "权限", "不可操作", "必填", "格式", "重复", "超限"],
        [
            "knowledge/wiki/summaries/设计准则/反馈与报错/00_反馈与报错体验设计指南.md",
            "knowledge/wiki/summaries/设计准则/可用性.md",
            "knowledge/wiki/summaries/设计准则/可读性.md",
        ],
        "facts/business 出现报错、阻断、校验或权限不足信号。",
    ),
    (
        ["审批", "待生效", "异步", "后台", "任务", "状态", "变化", "进度"],
        [
            "knowledge/wiki/summaries/设计准则/可用性.md",
            "knowledge/wiki/summaries/设计准则/治理.md",
            "knowledge/wiki/summaries/设计准则/反馈与报错/00_反馈与报错体验设计指南.md",
        ],
        "facts/business 出现审批、延迟生效、后台任务或状态流转信号。",
    ),
    (
        ["批量", "删除", "关闭", "不可逆", "多人", "范围", "权限变更", "风险"],
        [
            "knowledge/wiki/summaries/设计准则/可用性.md",
            "knowledge/wiki/summaries/设计准则/治理.md",
            "knowledge/wiki/summaries/设计准则/认知.md",
        ],
        "facts/business 出现批量操作、高风险配置或权限变更信号。",
    ),
    (
        ["列表", "表格", "结果", "明细", "空状态", "部分成功", "全部失败"],
        [
            "knowledge/wiki/summaries/设计准则/信息架构.md",
            "knowledge/wiki/summaries/设计准则/可用性.md",
            "knowledge/wiki/summaries/设计准则/视觉.md",
            "knowledge/wiki/summaries/设计准则/反馈与报错/00_反馈与报错体验设计指南.md",
        ],
        "facts/business 出现列表、表格、结果明细或空状态信号。",
    ),
    (
        ["弹窗", "抽屉", "详情", "确认", "临时配置", "上下文"],
        [
            "knowledge/wiki/summaries/设计准则/信息架构.md",
            "knowledge/wiki/summaries/设计准则/流程模式.md",
            "knowledge/wiki/summaries/设计准则/可用性.md",
            "knowledge/wiki/summaries/设计准则/认知.md",
        ],
        "facts/business 出现弹窗、抽屉、详情承载或二次确认信号。",
    ),
    (
        ["术语", "文案", "命名", "原因", "下一步", "理解", "错误码"],
        [
            "knowledge/wiki/summaries/设计准则/可读性.md",
            "knowledge/wiki/summaries/设计准则/可用性.md",
            "knowledge/wiki/summaries/设计准则/治理.md",
        ],
        "facts/business 出现术语、文案或用户理解成本信号。",
    ),
    (
        ["配置", "规则", "选择", "认知", "渐进", "披露", "复杂"],
        [
            "knowledge/wiki/summaries/设计准则/认知.md",
            "knowledge/wiki/summaries/设计准则/信息架构.md",
            "knowledge/wiki/summaries/设计准则/流程模式.md",
            "knowledge/wiki/summaries/设计准则/视觉.md",
        ],
        "facts/business 出现复杂配置、高认知负担或渐进披露信号。",
    ),
    (
        ["密度", "视觉", "层级", "扫读", "卡片", "表格", "详情"],
        [
            "knowledge/wiki/summaries/设计准则/视觉.md",
            "knowledge/wiki/summaries/设计准则/信息架构.md",
            "knowledge/wiki/summaries/设计准则/可读性.md",
        ],
        "facts/business 出现视觉层级、信息密度或可扫读信号。",
    ),
    (
        ["无障碍", "键盘", "颜色", "感知", "可达", "可操作"],
        [
            "knowledge/wiki/summaries/设计准则/无障碍.md",
            "knowledge/wiki/summaries/设计准则/可用性.md",
            "knowledge/wiki/summaries/设计准则/可读性.md",
        ],
        "facts/business 出现无障碍、可感知或可操作信号。",
    ),
    (
        ["质量", "有效", "效率", "满意", "返工", "价值", "完成"],
        [
            "knowledge/wiki/summaries/设计准则/质量.md",
            "knowledge/wiki/summaries/设计准则/可用性.md",
            "knowledge/wiki/summaries/设计准则/认知.md",
        ],
        "facts/business 出现体验质量、效率、完成度或风险评估信号。",
    ),
]


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

    route_lines = _extract_markdown_section(text, "## 场景路由")[:12]
    trigger_lines = _extract_markdown_section(text, "## 2. 任务触发线索")[:6]
    coverage_lines = _extract_markdown_section(text, "## 3. 覆盖内容")[:4]
    candidate_text = "\n".join([title, *route_lines, *trigger_lines, *coverage_lines])
    matched_fragments = [line for line in route_lines + trigger_lines + coverage_lines if line]
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
        if normalized == "knowledge/wiki/index.md":
            guideline_root = repo_root / "knowledge" / "wiki" / "summaries" / "设计准则"
            if guideline_root.exists():
                candidates.extend(
                    str(item.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
                    for item in sorted(guideline_root.glob("**/*.md"))
                    if item.is_file()
                )
        if not normalized.endswith(".md"):
            continue
        entry_path = repo_root / Path(normalized.replace("/", "\\"))
        if not entry_path.exists() or not entry_path.is_file():
            continue

        if entry_path.name.lower() == "readme.md":
            sibling_refs = [
                str(item.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
                for item in sorted(entry_path.parent.glob("**/*.md"))
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


def _valid_guideline_raw_refs(metadata: dict[str, object], limit: int = 3) -> list[str]:
    raw_refs: list[str] = []
    for item in metadata.get("source_refs", []):
        if not isinstance(item, str):
            continue
        normalized = item.replace("\\", "/").strip()
        if not normalized.startswith("knowledge/raw/"):
            continue
        if normalized.endswith("/") or "." not in Path(normalized).name:
            continue
        raw_refs.append(normalized)
        if len(raw_refs) >= limit:
            break
    return raw_refs


def _collect_source_refs_for_guidelines(repo_root: Path, guideline_refs: list[str]) -> list[str]:
    raw_refs: list[str] = []
    for summary_ref in guideline_refs:
        metadata = _read_summary_metadata(repo_root, summary_ref)
        if not _is_guideline_summary_metadata(metadata):
            continue
        raw_refs.extend(_valid_guideline_raw_refs(metadata))
    return _dedupe_keep_order(raw_refs)


def _select_guidelines_from_business(context_text: str, entry_refs: list[str]) -> tuple[list[str], list[str], list[dict[str, str]]]:
    repo_root = get_repo_root()
    candidate_refs = _collect_guideline_candidate_refs(repo_root, entry_refs)
    candidate_ref_set = set(candidate_refs)
    context_text_lower = context_text.lower()
    ranked: list[tuple[int, str, str]] = []

    for summary_ref in candidate_refs:
        candidate_text, fragments = _read_guideline_candidate_text(repo_root, summary_ref)
        if not candidate_text:
            continue
        tokens = _extract_signal_tokens(candidate_text)
        matched_tokens = [token for token in tokens if token in context_text_lower]
        if not matched_tokens:
            continue
        score = len(matched_tokens)
        reason_fragment = ""
        for fragment in fragments:
            fragment_tokens = _extract_signal_tokens(fragment)
            if any(token in context_text_lower for token in fragment_tokens):
                reason_fragment = fragment
                break
        if not reason_fragment and fragments:
            reason_fragment = fragments[0]
        ranked.append((score, summary_ref, reason_fragment))

    for signal_tokens, routed_refs, reason in GUIDELINE_ROUTE_RULES:
        hits = [token for token in signal_tokens if token.lower() in context_text_lower]
        if not hits:
            continue
        for routed_ref in routed_refs:
            if routed_ref in candidate_ref_set:
                ranked.append((len(hits) + 20, routed_ref, reason))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    selected_ranked: list[tuple[int, str, str]] = []
    seen_guidelines: set[str] = set()
    for item in ranked:
        if item[1] in seen_guidelines:
            continue
        seen_guidelines.add(item[1])
        selected_ranked.append(item)
        if len(selected_ranked) >= 3:
            break
    selected_refs = [summary_ref for _, summary_ref, _ in selected_ranked]

    selected_raw_refs: list[str] = []
    selection_reasons: list[dict[str, str]] = []
    for _, summary_ref, reason_fragment in selected_ranked:
        summary_path = repo_root / Path(summary_ref.replace("/", "\\"))
        metadata = parse_summary_metadata(summary_path.read_text(encoding="utf-8"))
        selected_raw_refs.extend(_valid_guideline_raw_refs(metadata))
        selection_reasons.append(
            {
                "guideline": summary_ref,
                "reason": f"facts/business 命中了该指南的场景线索：{reason_fragment}" if reason_fragment else "facts/business 与该指南的任务触发线索存在明显重合。",
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

    raw_existing_reasons = experience_plan.get("guideline_selection_reason")
    reasons: list[dict[str, str]] = []
    if isinstance(raw_existing_reasons, list):
        reasons = [
            {"guideline": str(item.get("guideline", "")), "reason": str(item.get("reason", ""))}
            for item in raw_existing_reasons
            if isinstance(item, dict)
        ]
    facts_text = _read_workspace_file(project_id, "facts.md")
    business_text = _read_workspace_file(project_id, "business_blueprint.md")
    context_text = "\n".join([facts_text, business_text])
    if not guideline_refs and guideline_entry_refs and context_text.strip():
        selected_guideline_refs, selected_guideline_raw_refs, reasons = _select_guidelines_from_business(context_text, guideline_entry_refs)
        guideline_refs = _dedupe_keep_order(selected_guideline_refs)
        raw_refs_from_source_refs = _dedupe_keep_order(raw_refs_from_source_refs + selected_guideline_raw_refs)
        experience_plan["guideline_refs"] = guideline_refs
        experience_plan["raw_refs_from_source_refs"] = raw_refs_from_source_refs
        experience_plan["guideline_selection_reason"] = reasons
        _write_context_manifest(project_id, manifest)
    elif guideline_refs:
        plan_changed = False
        reasons_are_generic = bool(reasons) and all("明确设计指南输入" in item.get("reason", "") for item in reasons)
        reasons_need_refresh = reasons_are_generic or any("在以下设计任务中触发" in item.get("reason", "") for item in reasons)
        if (not reasons or reasons_need_refresh) and guideline_entry_refs and context_text.strip():
            selected_refs, selected_raw_refs, selected_reasons = _select_guidelines_from_business(context_text, guideline_entry_refs)
            if reasons_need_refresh and selected_refs:
                guideline_refs = _dedupe_keep_order(selected_refs)
                raw_refs_from_source_refs = _dedupe_keep_order(raw_refs_from_source_refs + selected_raw_refs)
                experience_plan["guideline_refs"] = guideline_refs
                experience_plan["raw_refs_from_source_refs"] = raw_refs_from_source_refs
                plan_changed = True
            selected_reason_by_ref = {item["guideline"]: item["reason"] for item in selected_reasons}
            reasons = [
                {
                    "guideline": guideline,
                    "reason": selected_reason_by_ref.get(guideline, "facts/business 已保留该 guideline 作为 experience 阶段输入，但未重新命中更具体的场景片段。"),
                }
                for guideline in guideline_refs
            ]
            experience_plan["guideline_selection_reason"] = reasons
            plan_changed = True
        selected_guideline_raw_refs = _collect_source_refs_for_guidelines(get_repo_root(), guideline_refs)
        updated_raw_refs = _dedupe_keep_order(raw_refs_from_source_refs + selected_guideline_raw_refs)
        if updated_raw_refs != raw_refs_from_source_refs:
            raw_refs_from_source_refs = updated_raw_refs
            experience_plan["raw_refs_from_source_refs"] = raw_refs_from_source_refs
            plan_changed = True
        if not reasons:
            reasons = [
                {
                    "guideline": guideline,
                    "reason": "该指南已作为 experience 阶段的明确设计指南输入进入上下文，并已补齐 source_refs 指向的 raw。",
                }
                for guideline in guideline_refs
            ]
        if plan_changed:
            _write_context_manifest(project_id, manifest)
    elif guideline_entry_refs:
        reasons = [
            {
                "guideline": "",
                "reason": "已保留 Design Guidelines 入口，但当前 business_blueprint 未形成足够明确的场景信号，暂未自动选中具体指南。",
            }
        ]

    guideline_source_refs = _collect_source_refs_for_guidelines(get_repo_root(), guideline_entry_refs + guideline_refs)
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
        + "\n\n## 5. 设计指南消费判断\n\n"
        "在输出体验蓝图前，请基于 facts.md 和 business_blueprint.md 判断：\n"
        "1. 本次业务蓝图中是否出现报错、阻断、校验、状态反馈、审批延迟、批量风险、高风险配置等体验问题。\n"
        "2. 这些问题是否命中 Design Guidelines 中的具体 summary。\n"
        "3. 如果命中 summary，必须读取其 source_refs 指向的 raw，并只吸收原则，不暴露大段原文。\n"
        "4. 体验蓝图不得凭指南替代业务事实；业务事实不足时，只能输出待确认问题或条件型建议。\n"
        "5. 输出方案时，需要说明反馈时机、反馈形式、用户可见文案和用户下一步。\n"
        + "\n\n## 6. 设计原则摘要\n\n"
        "- 先写主流程，再补次流程与异常阻断流程。\n"
        "- 页面/弹窗/抽屉必须写清页面目标、进入条件、操作、状态反馈和异常处理。\n"
        "- 文案必须给具体草案，不写抽象策略句。\n"
        "- 禁止重做事实抽取、业务判断或需求全文重读。\n\n"
        "## 7. 待确认问题\n\n"
        + "\n".join(f"- {line}" for line in gap_lines)
        + "\n\n## 8. 输出模板要求\n\n"
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
