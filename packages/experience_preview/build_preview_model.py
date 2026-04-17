from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from packages.common import get_project_dir, get_project_exports_dir, get_project_workspace_dir


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
PAGE_ID_RE = re.compile(r"\bP-\d+\b", re.IGNORECASE)
FLOW_ID_RE = re.compile(r"\bTF-\d+\b", re.IGNORECASE)
IA_ID_RE = re.compile(r"\bIA-\d+\b", re.IGNORECASE)
COPY_ID_RE = re.compile(r"\bCOPY-\d+\b", re.IGNORECASE)
TRACE_ID_RE = re.compile(r"\bTR-\d+\b", re.IGNORECASE)
PRINCIPLE_ID_RE = re.compile(r"\bPR-\d+\b", re.IGNORECASE)
BLOCK_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
SUB_BLOCK_RE = re.compile(r"^####\s+(.+?)\s*$", re.MULTILINE)


def _read_blueprint_source(project_id: str) -> tuple[Path, str]:
    project_dir = get_project_dir(project_id)
    candidates = [
        get_project_exports_dir(project_id) / "final" / "experience_blueprint.md",
        get_project_workspace_dir(project_id) / "experience_blueprint.md",
    ]
    for path in candidates:
        if path.exists():
            return path, path.read_text(encoding="utf-8")
    raise SystemExit(f"Missing experience blueprint for preview: {project_dir}")


def _split_sections(text: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1).strip()] = text[start:end].strip()
    return sections


def _split_heading_blocks(section_text: str, pattern: re.Pattern[str]) -> dict[str, str]:
    matches = list(pattern.finditer(section_text))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section_text)
        blocks[match.group(1).strip()] = section_text[start:end].strip()
    return blocks


def _extract_title(text: str, source_path: Path) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return source_path.stem


def _extract_overview(section_text: str) -> dict[str, str]:
    result = {
        "目标用户与角色": "",
        "体验目标": "",
        "任务边界": "",
    }
    for line in _parse_bullets(section_text):
        for key in list(result.keys()):
            prefix = f"{key}："
            if line.startswith(prefix):
                result[key] = line
    return result


def _normalize(value: str) -> str:
    compact = re.sub(r"\s+", "", value).lower()
    for token in ["页面", "页", "弹窗", "抽屉", "子页面", "窗口", "结果通知", "结果", "记录", "/", "（", "）", "(", ")"]:
        compact = compact.replace(token, "")
    return compact


def _split_labels(value: str) -> list[str]:
    raw_parts = re.split(r"[、,，/；;]", value)
    return [part.strip() for part in raw_parts if part.strip()]


def _split_arrow_steps(value: str) -> list[str]:
    return [part.strip(" -") for part in re.split(r"->|→", value) if part.strip(" -")]


def _parse_bullets(section_text: str) -> list[str]:
    items: list[str] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


def _parse_markdown_table(section_text: str) -> list[dict[str, str]]:
    rows = [line.strip() for line in section_text.splitlines() if line.strip().startswith("|")]
    if len(rows) < 2:
        return []
    headers = [cell.strip() for cell in rows[0].strip("|").split("|")]
    result: list[dict[str, str]] = []
    for row in rows[2:]:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        result.append({headers[index]: cells[index] for index in range(len(headers))})
    return result


def _extract_code_block(section_text: str) -> str:
    match = re.search(r"```(?:text)?\n([\s\S]*?)```", section_text)
    return match.group(1).strip() if match else ""


def _infer_view_type(name: str, fallback: str = "") -> str:
    lowered = f"{name} {fallback}".lower()
    if "抽屉" in lowered or "drawer" in lowered:
        return "抽屉"
    if "弹窗" in lowered or "modal" in lowered or "dialog" in lowered:
        return "弹窗"
    if "子页面" in lowered or "subpage" in lowered:
        return "子页面"
    return "页面"


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = re.sub(r"\s+", " ", str(value)).strip()
        if not cleaned:
            continue
        marker = cleaned.lower()
        if marker in seen:
            continue
        seen.add(marker)
        result.append(cleaned)
    return result


def _dedupe_dicts(items: list[dict[str, Any]], key_fields: list[str]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        marker = "||".join(str(item.get(field, "")).strip().lower() for field in key_fields)
        if not marker.strip("|"):
            continue
        if marker in seen:
            continue
        seen.add(marker)
        result.append(item)
    return result


def _empty_page(page_id: str, view_name: str, view_type: str, roles: list[str], summary: str, entry: str, exit_text: str, relation: str) -> dict[str, Any]:
    return {
        "page_id": page_id,
        "view_name": view_name,
        "view_type": view_type,
        "roles": roles,
        "summary": summary,
        "entry": entry,
        "exit": exit_text,
        "upstream_links": [],
        "downstream_links": [],
        "sketch_blocks": [],
        "key_understanding": [],
        "action_items": [],
        "info_contract_items": [],
        "states": [],
        "copy_items": [],
        "risks": [],
        "blockers": [],
        "principles": [],
        "design_patterns": [],
        "trace_items": [],
        "open_items": [],
        "gap_items": [],
        "source_refs": [f"页面 / 窗口清单:{page_id}"],
        "_relation_text": relation,
        "_aliases": [page_id, view_name, _normalize(view_name)],
    }


def _build_page_index(sections: dict[str, str]) -> dict[str, dict[str, Any]]:
    rows = _parse_markdown_table(sections.get("页面 / 窗口清单", ""))
    page_index: dict[str, dict[str, Any]] = {}
    for row in rows:
        page_id = (row.get("page_id") or row.get("页面ID") or row.get("ID") or "").strip()
        view_name = (row.get("名称") or row.get("页面名称") or "").strip()
        if not page_id or not view_name:
            continue
        view_type = _infer_view_type(row.get("类型", ""), view_name)
        roles = _split_labels(row.get("目标用户", ""))
        summary = (row.get("主任务") or row.get("目标") or "").strip()
        entry = (row.get("入口") or "").strip()
        exit_text = (row.get("退出方式") or "").strip()
        relation = (row.get("上下游关系") or "").strip()
        page = _empty_page(page_id, view_name, view_type, roles, summary, entry, exit_text, relation)

        related_ids = [match.upper() for match in PAGE_ID_RE.findall(relation)]
        for related_id in related_ids:
            if "上游" in relation and related_id != page_id:
                page["upstream_links"].append(related_id)
            elif related_id != page_id:
                page["downstream_links"].append(related_id)
        page_index[page_id] = page
    return page_index


def _build_ia_index(sections: dict[str, str]) -> dict[str, dict[str, Any]]:
    rows = _parse_markdown_table(sections.get("信息架构总览", ""))
    ia_index: dict[str, dict[str, Any]] = {}
    for row in rows:
        ia_id = (row.get("ia_node") or row.get("IA节点") or row.get("节点") or "").strip().upper()
        if not ia_id:
            continue
        ia_index[ia_id] = {
            "ia_id": ia_id,
            "roles": _split_labels(row.get("面向角色", "")),
            "type": (row.get("类型") or "").strip(),
            "entry": (row.get("入口") or "").strip(),
            "task": (row.get("承接对象 / 主任务") or "").strip(),
            "relation": (row.get("与其他节点关系") or "").strip(),
        }
    return ia_index


def _ia_page_refs(label: str, ia_index: dict[str, dict[str, Any]], page_index: dict[str, dict[str, Any]]) -> list[str]:
    refs: list[str] = []
    for ia_id in [match.group(0).upper() for match in IA_ID_RE.finditer(label)]:
        ia_item = ia_index.get(ia_id)
        if ia_item is None:
            continue
        binding_text = " ".join(
            [
                ia_id,
                str(ia_item.get("entry") or ""),
                str(ia_item.get("task") or ""),
                str(ia_item.get("relation") or ""),
            ]
        )
        refs.extend(_bind_pages(binding_text, page_index))
    return _dedupe_strings(refs)


def _page_aliases(page: dict[str, Any]) -> list[str]:
    aliases = [str(item) for item in page.get("_aliases", []) if str(item).strip()]
    aliases.extend(
        [
            str(page.get("page_id") or ""),
            str(page.get("view_name") or ""),
            _normalize(str(page.get("view_name") or "")),
            _normalize(str(page.get("summary") or "")),
        ]
    )
    aliases.extend(str(role) for role in page.get("roles", []))
    return _dedupe_strings([alias for alias in aliases if alias])


def _bind_pages(text: str, page_index: dict[str, dict[str, Any]]) -> list[str]:
    page_ids = [match.upper() for match in PAGE_ID_RE.findall(text)]
    if page_ids:
        stable = [page_id for page_id in page_ids if page_id in page_index]
        if stable:
            return _dedupe_strings(stable)

    lowered = text.lower()
    matched: list[str] = []
    for page_id, page in page_index.items():
        aliases = _page_aliases(page)
        if str(page.get("view_name") or "").lower() in lowered:
            matched.append(page_id)
            continue
        if any(alias and alias.lower() in lowered for alias in aliases if len(alias) >= 2):
            matched.append(page_id)
            continue
    return _dedupe_strings(matched)


def _explicit_page_refs(text: str, page_index: dict[str, dict[str, Any]]) -> list[str]:
    return [page_id for page_id in _dedupe_strings([match.upper() for match in PAGE_ID_RE.findall(text)]) if page_id in page_index]


def _bind_best_page(text: str, page_index: dict[str, dict[str, Any]]) -> str | None:
    matches = _bind_pages(text, page_index)
    if matches:
        return matches[0]

    normalized = _normalize(text)
    best_page_id: str | None = None
    best_score = 0
    for page_id, page in page_index.items():
        score = 0
        for alias in _page_aliases(page):
            alias_norm = _normalize(alias)
            if not alias_norm:
                continue
            if alias_norm in normalized:
                score = max(score, len(alias_norm))
        if score > best_score:
            best_score = score
            best_page_id = page_id
    return best_page_id if best_score >= 2 else None


def _append_page_string(page: dict[str, Any], field: str, value: str, source_ref: str) -> None:
    if not value.strip():
        return
    page[field] = _dedupe_strings(list(page.get(field, [])) + [value.strip()])
    page["source_refs"] = _dedupe_strings(list(page.get("source_refs", [])) + [source_ref])


def _append_page_dict(page: dict[str, Any], field: str, value: dict[str, Any], key_fields: list[str], source_ref: str) -> None:
    page[field] = _dedupe_dicts(list(page.get(field, [])) + [value], key_fields)
    page["source_refs"] = _dedupe_strings(list(page.get("source_refs", [])) + [source_ref])


def _extract_page_blueprint_blocks(section_text: str) -> dict[str, dict[str, str]]:
    page_blocks = _split_heading_blocks(section_text, BLOCK_RE)
    result: dict[str, dict[str, str]] = {}
    for heading, body in page_blocks.items():
        page_id_match = PAGE_ID_RE.search(heading)
        if not page_id_match:
            continue
        page_id = page_id_match.group(0).upper()
        result[page_id] = _split_heading_blocks(body, SUB_BLOCK_RE)
    return result


def _apply_page_blueprints(page_index: dict[str, dict[str, Any]], sections: dict[str, str]) -> None:
    blocks = _extract_page_blueprint_blocks(sections.get("关键页面蓝图", ""))
    for page_id, sub_blocks in blocks.items():
        page = page_index.get(page_id)
        if page is None:
            continue

        goal_lines = _parse_bullets(sub_blocks.get("页面目标", ""))
        for line in goal_lines:
            if line.startswith("页面目标："):
                page["summary"] = line.replace("页面目标：", "", 1).strip()
            elif line.startswith("目标用户："):
                page["roles"] = _dedupe_strings(page.get("roles", []) + _split_labels(line.replace("目标用户：", "", 1)))
            elif line.startswith("进入条件："):
                page["entry"] = line.replace("进入条件：", "", 1).strip()
            elif line.startswith("主任务 / 次任务："):
                _append_page_string(page, "key_understanding", line.replace("主任务 / 次任务：", "", 1), f"关键页面蓝图:{page_id}:页面目标")

        focus_lines = _parse_bullets(sub_blocks.get("首屏重点与关键信息", ""))
        for line in focus_lines:
            cleaned = line.split("：", 1)[-1].strip() if "：" in line else line
            _append_page_string(page, "key_understanding", cleaned, f"关键页面蓝图:{page_id}:首屏重点与关键信息")

        action_rows = _parse_markdown_table(sub_blocks.get("关键动作与状态", ""))
        for row in action_rows:
            action_item = {
                "action_id": row.get("action_id", "").strip(),
                "name": row.get("动作", "").strip(),
                "trigger": row.get("触发条件", "").strip(),
                "feedback": row.get("即时反馈", "").strip(),
                "outcome": row.get("后续结果", "").strip(),
                "protection": row.get("风险保护", "").strip(),
            }
            _append_page_dict(page, "action_items", action_item, ["action_id", "name"], f"关键页面蓝图:{page_id}:关键动作与状态")


def _apply_layout_blocks(page_index: dict[str, dict[str, Any]], sections: dict[str, str]) -> None:
    blocks = _split_heading_blocks(sections.get("区块布局示意", ""), BLOCK_RE)
    for heading, body in blocks.items():
        page_id_match = PAGE_ID_RE.search(heading)
        if not page_id_match:
            continue
        page_id = page_id_match.group(0).upper()
        page = page_index.get(page_id)
        if page is None:
            continue
        code_block = _extract_code_block(body)
        lines = [line.strip().strip("[]") for line in code_block.splitlines() if line.strip()]
        for index, line in enumerate(lines):
            if ":" in line:
                label, summary = line.split(":", 1)
                block_item = {
                    "label": label.strip(),
                    "block_type": "Main Area" if index == 0 else "Detail Area",
                    "summary": summary.strip(),
                }
            else:
                block_item = {
                    "label": line.strip(),
                    "block_type": "Main Area" if index == 0 else "Detail Area",
                    "summary": "",
                }
            _append_page_dict(page, "sketch_blocks", block_item, ["label", "summary"], f"区块布局示意:{page_id}")


def _apply_content_contract(page_index: dict[str, dict[str, Any]], sections: dict[str, str], global_context: dict[str, list[Any]]) -> None:
    rows = _parse_markdown_table(sections.get("内容与信息优先级合同", ""))
    for row in rows:
        item = {
            "info_id": row.get("info_item", "").strip(),
            "purpose": row.get("信息目的", "").strip(),
            "priority": row.get("优先级", "").strip(),
            "position": row.get("推荐位置", "").strip(),
            "trigger": row.get("触发时机", "").strip(),
            "risk": row.get("不展示风险", "").strip(),
        }
        refs = _bind_pages(item["position"], page_index)
        if not refs:
            global_context["notes"].append({"type": "信息优先级", "content": item["purpose"], "position": item["position"]})
            continue
        for page_id in refs:
            _append_page_dict(page_index[page_id], "info_contract_items", item, ["info_id"], f"内容与信息优先级合同:{item['info_id']}")


def _state_binding_hint(state_id: str, state_name: str, feedback: str, outcome: str) -> str:
    text = " ".join([state_id, state_name, feedback, outcome])
    if state_id in {"ST-01", "ST-02", "ST-03", "ST-04"}:
        return "P-01"
    if state_id in {"ST-05", "ST-06", "ST-07"}:
        return "P-06"
    if state_id == "ST-08":
        return "P-07"
    if "结果页" in text or "申请记录" in text:
        return "P-06"
    return ""


def _apply_states(page_index: dict[str, dict[str, Any]], sections: dict[str, str], global_context: dict[str, list[Any]], global_flow: dict[str, Any]) -> None:
    rows = _parse_markdown_table(sections.get("状态与反馈矩阵", ""))
    for row in rows:
        state_item = {
            "state_id": row.get("state_id", "").strip(),
            "name": row.get("状态名称", "").strip(),
            "trigger": row.get("触发条件", "").strip(),
            "actions": row.get("可用动作", "").strip(),
            "feedback": row.get("页面反馈", "").strip(),
            "copy_feedback": row.get("文案反馈", "").strip(),
            "outcome": row.get("下游结果", "").strip(),
        }
        text = " ".join(value for value in state_item.values() if value)
        bound_pages = _bind_pages(text, page_index)
        hint_page = _state_binding_hint(state_item["state_id"], state_item["name"], state_item["feedback"], state_item["outcome"])
        if hint_page and hint_page in page_index:
            bound_pages = _dedupe_strings(bound_pages + [hint_page])

        if not bound_pages:
            global_context["notes"].append({"type": "状态", "content": text})
        for page_id in bound_pages:
            page = page_index[page_id]
            _append_page_dict(page, "states", state_item, ["state_id", "name"], f"状态与反馈矩阵:{state_item['state_id']}")
            if any(flag in state_item["name"] for flag in ["失败", "阻断", "拒绝", "撤销"]):
                blocker = {
                    "id": state_item["state_id"],
                    "name": state_item["name"],
                    "trigger": state_item["trigger"],
                    "impact": state_item["outcome"] or state_item["copy_feedback"],
                    "page_id": page_id,
                }
                _append_page_dict(page, "blockers", blocker, ["id", "page_id"], f"状态与反馈矩阵:{state_item['state_id']}")


def _copy_binding_hint(copy_id: str, scene: str) -> list[str]:
    if copy_id in {"COPY-01", "COPY-02"} or "启用" in scene:
        return ["P-01"]
    if copy_id in {"COPY-03", "COPY-04"} or "申请" in scene:
        return ["P-05"]
    if copy_id == "COPY-05" or "审批结果" in scene:
        return ["P-06"]
    if copy_id == "COPY-06" or "关闭失败" in scene:
        return ["P-07"]
    return []


def _apply_copy_items(page_index: dict[str, dict[str, Any]], sections: dict[str, str], global_context: dict[str, list[Any]]) -> None:
    rows = _parse_markdown_table(sections.get("文案合同", ""))
    for row in rows:
        item = {
            "copy_id": row.get("copy_id", "").strip(),
            "scene": row.get("场景", "").strip(),
            "copy_type": row.get("文案类型", "").strip(),
            "goal": row.get("语义目标", "").strip(),
            "required": row.get("必含信息", "").strip(),
            "avoid": row.get("禁止写法", "").strip(),
            "example": row.get("示例方向", "").strip(),
        }
        bound_pages = _copy_binding_hint(item["copy_id"], item["scene"])
        if not bound_pages:
            bound_pages = _bind_pages(" ".join(item.values()), page_index)
        if not bound_pages:
            global_context["notes"].append({"type": "文案", "content": f"{item['copy_id']} {item['scene']}"})
            continue
        valid_page_ids = [page_id for page_id in bound_pages if page_id in page_index]
        if not valid_page_ids:
            global_context["notes"].append(
                {
                    "type": "文案",
                    "content": f"{item['copy_id']} 引用了未落盘页面: {', '.join(bound_pages)}",
                }
            )
            continue
        for page_id in valid_page_ids:
            _append_page_dict(page_index[page_id], "copy_items", item, ["copy_id"], f"文案合同:{item['copy_id']}")


def _apply_risks(page_index: dict[str, dict[str, Any]], sections: dict[str, str], global_context: dict[str, list[Any]]) -> None:
    rows = _parse_markdown_table(sections.get("风险、疑惑点与保护策略", ""))
    for row in rows:
        item = {
            "risk_id": row.get("risk_id", "").strip(),
            "name": row.get("风险 / 疑惑点", "").strip(),
            "trigger": row.get("触发场景", "").strip(),
            "confusion_reason": row.get("用户为什么会困惑 / 出错", "").strip(),
            "protection": row.get("保护策略", "").strip(),
        }
        binding_text = row.get("对应页面 / 流程 / 文案", "").strip()
        bound_pages = _bind_pages(binding_text, page_index)
        if not bound_pages:
            global_context["risks"].append(item)
            continue
        for page_id in bound_pages:
            _append_page_dict(page_index[page_id], "risks", item, ["risk_id"], f"风险、疑惑点与保护策略:{item['risk_id']}")


def _apply_principles(page_index: dict[str, dict[str, Any]], sections: dict[str, str], global_context: dict[str, list[Any]]) -> None:
    basis_lines = _parse_bullets(sections.get("体验推导依据", ""))
    for line in basis_lines:
        if line.startswith("原则引用："):
            for item in _split_labels(line.replace("原则引用：", "", 1)):
                global_context["principles"].append({"principle_id": item.split(" ", 1)[0], "label": item})

    rows = _parse_markdown_table(sections.get("体验推导依据", ""))
    for row in rows:
        principle_id = row.get("principle_id", "").strip()
        if not principle_id:
            continue
        item = {
            "principle_id": principle_id,
            "name": row.get("原则名称", "").strip(),
            "reason": row.get("命中原因", "").strip(),
        }
        refs = _bind_pages(row.get("作用位置", ""), page_index)
        if not refs:
            global_context["principles"].append(item)
            continue
        for page_id in refs:
            _append_page_dict(page_index[page_id], "principles", item, ["principle_id"], f"已命中的设计原则:{principle_id}")


def _apply_trace(page_index: dict[str, dict[str, Any]], sections: dict[str, str]) -> None:
    rows = _parse_markdown_table(sections.get("体验追踪映射", ""))
    for row in rows:
        item = {
            "trace_id": row.get("trace_id", "").strip(),
            "object": row.get("页面 / 流程 / 文案对象", "").strip(),
            "business_judgment": row.get("承接业务判断", "").strip(),
            "facts": row.get("承接事实 / 规则 / 异常", "").strip(),
            "principles": row.get("承接原则", "").strip(),
            "note": row.get("说明", "").strip(),
        }
        refs = _bind_pages(item["object"], page_index)
        for page_id in refs:
            _append_page_dict(page_index[page_id], "trace_items", item, ["trace_id"], f"体验追踪映射:{item['trace_id']}")


def _open_item_binding_hint(text: str) -> list[str]:
    hints: list[str] = []
    if "功能权限申请" in text:
        hints.append("P-05")
    if "审批人" in text or "审批流" in text:
        hints.append("P-01")
    return hints


def _apply_open_questions(page_index: dict[str, dict[str, Any]], sections: dict[str, str], global_context: dict[str, list[Any]]) -> None:
    for bullet in _parse_bullets(sections.get("开放问题与缺口", "")):
        item_id = bullet.split("：", 1)[0].strip()
        content = bullet.split("：", 1)[1].strip() if "：" in bullet else bullet
        target_field = "open_items" if item_id.startswith("OQ-") else "gap_items"
        global_field = "open_questions" if item_id.startswith("OQ-") else "gaps"
        bound_pages = _bind_pages(content, page_index)
        for hint in _open_item_binding_hint(content):
            if hint in page_index:
                bound_pages.append(hint)
        bound_pages = _dedupe_strings(bound_pages)
        if not bound_pages:
            global_context[global_field].append({"id": item_id, "content": content})
            continue
        for page_id in bound_pages:
            _append_page_string(page_index[page_id], target_field, f"{item_id}：{content}", f"开放问题与缺口:{item_id}")


def _build_flow_dependencies(flow_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return []


def _infer_role(start_label: str, bound_pages: list[str], page_index: dict[str, dict[str, Any]], ia_index: dict[str, dict[str, Any]]) -> str:
    for ia_id in [match.group(0).upper() for match in IA_ID_RE.finditer(start_label)]:
        roles = ia_index.get(ia_id, {}).get("roles", [])
        if roles:
            return _dedupe_strings([str(role) for role in roles])[0]
    combined_roles: list[str] = []
    for page_id in bound_pages:
        combined_roles.extend(str(role) for role in page_index.get(page_id, {}).get("roles", []))
    if combined_roles:
        return _dedupe_strings(combined_roles)[0]
    if "员工" in start_label:
        return "员工"
    if "审批" in start_label:
        return "审批人"
    return "超管"


def _flow_page_refs(flow_name: str, text: str, page_index: dict[str, dict[str, Any]], ia_index: dict[str, dict[str, Any]]) -> list[str]:
    refs = _explicit_page_refs(f"{flow_name} {text}", page_index)
    refs.extend(_ia_page_refs(text, ia_index, page_index))
    return _dedupe_strings(refs)


def _infer_step_page(label: str, chain_pages: list[str], page_index: dict[str, dict[str, Any]], ia_index: dict[str, dict[str, Any]]) -> str:
    ia_refs = _ia_page_refs(label, ia_index, page_index)
    if ia_refs:
        return ia_refs[0]
    refs = _explicit_page_refs(label, page_index)
    if refs:
        return refs[0]
    return chain_pages[0] if len(chain_pages) == 1 else ""


def _build_global_flow(page_index: dict[str, dict[str, Any]], sections: dict[str, str], ia_index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows = _parse_markdown_table(sections.get("任务流蓝图", ""))
    chains: list[dict[str, Any]] = []
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    lanes: dict[str, dict[str, Any]] = {}
    blockers: list[dict[str, Any]] = []

    for row in rows:
        flow_id = row.get("flow_id", "").strip()
        if not flow_id:
            continue
        flow_name = row.get("流程名称", "").strip()
        steps = _split_arrow_steps(row.get("关键步骤", "").strip())
        start_label = row.get("起点", "").strip()
        step_labels = [start_label] + steps
        full_text = " ".join(step_labels + [row.get("关键判断 / 阻断", ""), row.get("成功结果", ""), row.get("失败 / 异常结果", "")])
        chain_pages = _flow_page_refs(flow_name, full_text, page_index, ia_index)
        role = _infer_role(start_label, chain_pages, page_index, ia_index)
        chain = {
            "chain_id": flow_id,
            "name": flow_name,
            "role": role,
            "path_type": "primary" if flow_id in {"TF-01", "TF-03", "TF-05"} else "secondary",
            "is_primary": flow_id in {"TF-01", "TF-03", "TF-05"},
            "start": start_label,
            "judgment": row.get("关键判断 / 阻断", "").strip(),
            "goal": row.get("成功结果", "").strip(),
            "failure_result": row.get("失败 / 异常结果", "").strip(),
            "depends_on": [],
            "page_refs": chain_pages,
        }
        chains.append(chain)
        lanes.setdefault(role, {"role": role, "chain_ids": []})
        lanes[role]["chain_ids"].append(flow_id)

        previous_node_id: str | None = None
        for index, label in enumerate(step_labels):
            node_id = f"{flow_id}-N{index + 1}"
            bound_page_id = _infer_step_page(label, chain_pages, page_index, ia_index)
            node = {
                "node_id": node_id,
                "name": label,
                "type": "页面节点" if bound_page_id else "流程步骤",
                "role": role,
                "chain_id": flow_id,
                "goal": row.get("成功结果", "").strip() or flow_name,
                "page_id": bound_page_id,
            }
            nodes.append(node)
            if previous_node_id is not None:
                edges.append(
                    {
                        "from": previous_node_id,
                        "to": node_id,
                        "path_type": "success",
                        "label": "",
                        "role": role,
                        "chain_id": flow_id,
                    }
                )
            previous_node_id = node_id

        failure_text = row.get("失败 / 异常结果", "").strip()
        judgment_text = row.get("关键判断 / 阻断", "").strip()
        if failure_text or judgment_text:
            blockers.append(
                {
                    "id": flow_id,
                    "name": flow_name,
                    "role": role,
                    "chain_id": flow_id,
                    "trigger": judgment_text,
                    "success_result": row.get("成功结果", "").strip(),
                    "impact": failure_text,
                    "failure_result": failure_text,
                    "return_direction": "",
                }
            )

    dependencies = _build_flow_dependencies(rows)
    for dependency in dependencies:
        source_chain = next((chain for chain in chains if chain["chain_id"] == dependency["from_chain_id"]), None)
        if source_chain is not None:
            source_chain["depends_on"].append(dependency["to_chain_id"])

    return {
        "lanes": list(lanes.values()),
        "chains": chains,
        "nodes": nodes,
        "edges": edges,
        "dependencies": dependencies,
        "blockers": blockers,
    }


def _finalize_pages(page_index: dict[str, dict[str, Any]], unresolved_items: list[dict[str, str]]) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    for page_id, page in page_index.items():
        page["roles"] = _dedupe_strings([str(role) for role in page.get("roles", [])])
        page["upstream_links"] = _dedupe_strings([str(item) for item in page.get("upstream_links", []) if item])
        page["downstream_links"] = _dedupe_strings([str(item) for item in page.get("downstream_links", []) if item])
        page["key_understanding"] = _dedupe_strings([str(item) for item in page.get("key_understanding", [])])
        page["open_items"] = _dedupe_strings([str(item) for item in page.get("open_items", [])])
        page["gap_items"] = _dedupe_strings([str(item) for item in page.get("gap_items", [])])
        page["source_refs"] = _dedupe_strings([str(item) for item in page.get("source_refs", [])])
        page["design_patterns"] = _dedupe_strings([str(item) for item in page.get("design_patterns", [])])
        page["action_items"] = _dedupe_dicts(list(page.get("action_items", [])), ["action_id", "name"])
        page["info_contract_items"] = _dedupe_dicts(list(page.get("info_contract_items", [])), ["info_id"])
        page["states"] = _dedupe_dicts(list(page.get("states", [])), ["state_id", "name"])
        page["copy_items"] = _dedupe_dicts(list(page.get("copy_items", [])), ["copy_id"])
        page["risks"] = _dedupe_dicts(list(page.get("risks", [])), ["risk_id", "name"])
        page["blockers"] = _dedupe_dicts(list(page.get("blockers", [])), ["id", "page_id"])
        page["principles"] = _dedupe_dicts(list(page.get("principles", [])), ["principle_id"])
        page["trace_items"] = _dedupe_dicts(list(page.get("trace_items", [])), ["trace_id"])
        page["sketch_blocks"] = _dedupe_dicts(list(page.get("sketch_blocks", [])), ["label", "summary"])

        page.pop("_relation_text", None)
        page.pop("_aliases", None)
        pages.append(page)
    return pages


def build_preview_model(project_id: str) -> dict[str, Any]:
    source_path, text = _read_blueprint_source(project_id)
    sections = _split_sections(text)
    page_index = _build_page_index(sections)
    ia_index = _build_ia_index(sections)
    overview = _extract_overview(sections.get("体验目标与任务边界", ""))
    unresolved_items: list[dict[str, str]] = []
    global_context: dict[str, list[Any]] = {
        "principles": [],
        "dependencies": [],
        "risks": [],
        "open_questions": [],
        "gaps": [],
        "notes": [],
    }

    if not page_index:
        unresolved_items.append(
            {
                "type": "page_inventory_missing",
                "message": "未识别到页面 / 窗口清单，页面聚合无法稳定构建。",
            }
        )

    global_flow = _build_global_flow(page_index, sections, ia_index)
    global_context["dependencies"] = list(global_flow.get("dependencies", []))

    _apply_page_blueprints(page_index, sections)
    _apply_layout_blocks(page_index, sections)
    _apply_content_contract(page_index, sections, global_context)
    _apply_states(page_index, sections, global_context, global_flow)
    _apply_copy_items(page_index, sections, global_context)
    _apply_risks(page_index, sections, global_context)
    _apply_principles(page_index, sections, global_context)
    _apply_trace(page_index, sections)
    _apply_open_questions(page_index, sections, global_context)

    pages = _finalize_pages(page_index, unresolved_items)
    for key in list(global_context.keys()):
        if key == "notes":
            global_context[key] = _dedupe_dicts(list(global_context[key]), ["type", "content"])
        elif key in {"dependencies", "risks"}:
            global_context[key] = _dedupe_dicts(list(global_context[key]), list(global_context[key][0].keys()) if global_context[key] else ["type"])
        else:
            global_context[key] = _dedupe_dicts(list(global_context[key]), ["principle_id", "label", "id", "content"])

    return {
        "project_id": project_id,
        "meta": {
            "title": _extract_title(text, source_path),
            "subject": "体验蓝图浏览器预览",
            "version": "v2",
            "context": {
                "source_blueprint": str(source_path),
                "input_mode": "formal_export" if "exports" in str(source_path) else "workspace_fallback",
            },
            "overview": overview,
        },
        "global_flow": global_flow,
        "page_views": pages,
        "global_context": global_context,
        "unresolved_items": unresolved_items,
        "source_refs": [str(source_path)],
    }
