from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from packages.common import get_project_dir, get_project_exports_dir, get_project_workspace_dir


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
PAGE_ID_RE = re.compile(r"\bP-\d+\b", re.IGNORECASE)


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


def _extract_title(text: str, source_path: Path) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return source_path.stem


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


def _split_labels(value: str) -> list[str]:
    raw_parts = re.split(r"[、,，/；;]", value)
    return [part.strip() for part in raw_parts if part.strip()]


def _page_keywords(page: dict[str, Any]) -> list[str]:
    keywords = [
        str(page.get("view_id") or ""),
        str(page.get("view_name") or ""),
        str(page.get("summary") or ""),
    ]
    normalized = []
    for keyword in keywords:
        cleaned = keyword
        for suffix in ["页面", "页", "弹窗", "抽屉", "窗口", "子页面"]:
            cleaned = cleaned.replace(suffix, "")
        cleaned = cleaned.strip()
        if cleaned:
            normalized.append(cleaned)
        if keyword.strip():
            normalized.append(keyword.strip())
    return [keyword for keyword in normalized if keyword]


def _char_bigrams(value: str) -> set[str]:
    compact = re.sub(r"\s+", "", value)
    if len(compact) < 2:
        return {compact} if compact else set()
    return {compact[index : index + 2] for index in range(len(compact) - 1)}


def _assign_page_index(text: str, pages: list[dict[str, Any]]) -> int | None:
    lowered = text.lower()
    for index, page in enumerate(pages):
        page_id = str(page.get("view_id") or "").lower()
        page_name = str(page.get("view_name") or "").lower()
        if page_id and page_id in lowered:
            return index
        if page_name and page_name in lowered:
            return index

    item_bigrams = _char_bigrams(text)
    best_score = 0
    best_index: int | None = None
    for index, page in enumerate(pages):
        page_text = " ".join(_page_keywords(page))
        score = len(item_bigrams & _char_bigrams(page_text))
        if score > best_score:
            best_score = score
            best_index = index
    if best_score <= 1:
        return None
    return best_index


def _infer_view_type(name: str) -> str:
    lowered = name.lower()
    if "抽屉" in name or "drawer" in lowered:
        return "抽屉"
    if "弹窗" in name or "modal" in lowered or "dialog" in lowered:
        return "弹窗"
    if "子页面" in name or "subpage" in lowered:
        return "子页面"
    return "页面"


def _build_pages(sections: dict[str, str]) -> list[dict[str, Any]]:
    table_rows = _parse_markdown_table(sections.get("页面 / 窗口清单", ""))
    pages: list[dict[str, Any]] = []
    for row in table_rows:
        view_id = row.get("页面ID") or row.get("页面 Id") or row.get("ID") or ""
        view_name = row.get("名称") or row.get("页面名称") or ""
        summary = row.get("用途") or row.get("说明") or row.get("目标") or ""
        if not view_name.strip():
            continue
        pages.append(
            {
                "view_id": view_id.strip() or view_name.strip(),
                "view_name": view_name.strip(),
                "view_type": _infer_view_type(view_name.strip()),
                "audience": "",
                "summary": summary.strip(),
                "sketch_blocks": [],
                "key_understanding": [],
                "states": [],
                "copy_items": [],
                "risks": [],
                "blockers": [],
                "principles": [],
                "trace_items": [],
                "open_items": [],
                "gap_items": [],
                "source_refs": [],
            }
        )
    return pages


def _apply_page_blueprints(sections: dict[str, str], pages: list[dict[str, Any]]) -> None:
    bullets = _parse_bullets(sections.get("页面蓝图", ""))
    for bullet in bullets:
        match = PAGE_ID_RE.search(bullet)
        target_index = None
        if match:
            target_index = _assign_page_index(match.group(0), pages)
        if target_index is None:
            target_index = _assign_page_index(bullet, pages)
        if target_index is None:
            continue
        block_text = bullet.split("：", 1)[-1]
        labels = _split_labels(block_text)
        pages[target_index]["sketch_blocks"] = [
            {
                "label": label,
                "block_type": "Main Area" if index == 0 else "Detail Area",
            }
            for index, label in enumerate(labels[:8])
        ]
        pages[target_index]["source_refs"].append("页面蓝图")


def _apply_key_understanding(sections: dict[str, str], pages: list[dict[str, Any]]) -> None:
    experience_goals = _parse_bullets(sections.get("体验目标", ""))
    task_flows = _parse_bullets(sections.get("核心任务流", ""))
    for page in pages:
        items = []
        if page.get("summary"):
            items.append(str(page["summary"]))
        items.extend(experience_goals[:2])
        related_flows = [flow for flow in task_flows if _assign_page_index(flow, [page]) == 0]
        items.extend(related_flows[:2])
        page["key_understanding"] = list(dict.fromkeys(items))
        if items:
            page["source_refs"].append("体验目标/核心任务流")


def _apply_states(sections: dict[str, str], pages: list[dict[str, Any]], global_notes: list[dict[str, str]]) -> None:
    rows = _parse_markdown_table(sections.get("状态与反馈矩阵", ""))
    for row in rows:
        state_item = {
            "name": row.get("状态", "").strip(),
            "trigger": row.get("条件", "").strip(),
            "feedback": row.get("反馈", "").strip(),
            "outcome": row.get("下一步", "").strip(),
        }
        state_text = " ".join(value for value in state_item.values() if value)
        target_index = _assign_page_index(state_text, pages)
        if target_index is None:
            global_notes.append({"type": "状态", "content": state_text or "未能归属的状态项"})
            continue
        pages[target_index]["states"].append(state_item)
        if any(flag in state_item["name"] for flag in ["失败", "阻断", "不可用"]):
            blocker_parts = [state_item["name"], state_item["trigger"], state_item["outcome"]]
            blocker = " / ".join(part for part in blocker_parts if part)
            if blocker:
                pages[target_index]["blockers"].append(blocker)
        pages[target_index]["source_refs"].append("状态与反馈矩阵")


def _apply_risks(sections: dict[str, str], pages: list[dict[str, Any]], global_notes: list[dict[str, str]]) -> None:
    bullets = _parse_bullets(sections.get("风险场景与体验保护", ""))
    pending_risk: str | None = None
    for bullet in bullets:
        if bullet.startswith("风险："):
            pending_risk = bullet.replace("风险：", "", 1).strip()
            continue
        if bullet.startswith("保护："):
            protection = bullet.replace("保护：", "", 1).strip()
            risk_item = {
                "name": pending_risk or "未命名风险",
                "trigger": "",
                "confusion_reason": pending_risk or "",
                "protection": protection,
            }
            target_index = _assign_page_index(f"{pending_risk or ''} {protection}", pages)
            if target_index is None:
                global_notes.append({"type": "风险", "content": f"{risk_item['name']} -> {protection}"})
            else:
                pages[target_index]["risks"].append(risk_item)
                pages[target_index]["source_refs"].append("风险场景与体验保护")
            pending_risk = None


def _apply_principles(sections: dict[str, str], pages: list[dict[str, Any]], global_notes: list[dict[str, str]]) -> None:
    bullets = _parse_bullets(sections.get("原则引用与映射", ""))
    principle_items: list[str] = []
    trace_items: list[str] = []
    for bullet in bullets:
        if bullet.startswith("原则ID："):
            principle_items.extend(_split_labels(bullet.replace("原则ID：", "", 1)))
        elif bullet.startswith("引用事实："):
            trace_items.extend(_split_labels(bullet.replace("引用事实：", "", 1)))
        elif bullet.startswith("引用判断："):
            trace_items.extend(_split_labels(bullet.replace("引用判断：", "", 1)))
    if not pages:
        for item in principle_items:
            global_notes.append({"type": "原则", "content": item})
        for item in trace_items:
            global_notes.append({"type": "追踪", "content": item})
        return
    for page in pages:
        page["principles"].extend(principle_items)
        page["trace_items"].extend(trace_items)
        if principle_items or trace_items:
            page["source_refs"].append("原则引用与映射")


def _apply_open_questions(sections: dict[str, str], pages: list[dict[str, Any]], global_notes: list[dict[str, str]]) -> None:
    bullets = _parse_bullets(sections.get("开放问题", ""))
    for bullet in bullets:
        target_index = _assign_page_index(bullet, pages)
        cleaned = bullet.split(":", 1)[-1].strip() if ":" in bullet else bullet
        cleaned = cleaned.split("：", 1)[-1].strip() if "：" in cleaned else cleaned
        if target_index is None:
            global_notes.append({"type": "开放问题", "content": cleaned})
            continue
        pages[target_index]["open_items"].append(cleaned)
        pages[target_index]["source_refs"].append("开放问题")


def _apply_missing_defaults(pages: list[dict[str, Any]]) -> None:
    for page in pages:
        if not page["sketch_blocks"]:
            fallback_labels = _split_labels(str(page.get("summary") or "主内容区/操作区"))
            if not fallback_labels:
                fallback_labels = ["主内容区", "操作区"]
            page["sketch_blocks"] = [
                {"label": label, "block_type": "Main Area" if index == 0 else "Detail Area"}
                for index, label in enumerate(fallback_labels[:6])
            ]
            page["gap_items"].append("缺少直接区块来源，已按页面摘要降级抽象草图")
        if not page["states"]:
            page["gap_items"].append("本页无直接专属状态项")
        if not page["copy_items"]:
            page["gap_items"].append("本页无直接专属文案项")
        page["source_refs"] = sorted(set(str(item) for item in page["source_refs"] if item))


def _build_global_flow(sections: dict[str, str], pages: list[dict[str, Any]]) -> dict[str, Any]:
    task_flows = _parse_bullets(sections.get("核心任务流", ""))
    nodes: list[dict[str, str]] = []
    if pages:
        for page in pages:
            nodes.append(
                {
                    "id": str(page.get("view_id") or page.get("view_name") or ""),
                    "name": str(page.get("view_name") or ""),
                    "type": str(page.get("view_type") or "页面"),
                    "goal": str(page.get("summary") or ""),
                }
            )
    else:
        for index, flow in enumerate(task_flows):
            nodes.append(
                {
                    "id": f"node-{index + 1}",
                    "name": flow.split(" ", 1)[-1] if " " in flow else flow,
                    "type": "流程节点",
                    "goal": flow,
                }
            )

    edges = []
    for index in range(len(nodes) - 1):
        edges.append(
            {
                "from": nodes[index]["id"],
                "to": nodes[index + 1]["id"],
                "path_type": "success",
                "label": task_flows[index] if index < len(task_flows) else "",
            }
        )
    return {"nodes": nodes, "edges": edges}


def build_preview_model(project_id: str) -> dict[str, Any]:
    source_path, text = _read_blueprint_source(project_id)
    sections = _split_sections(text)
    pages = _build_pages(sections)
    global_notes: list[dict[str, str]] = []
    unresolved_items: list[dict[str, str]] = []

    _apply_page_blueprints(sections, pages)
    _apply_key_understanding(sections, pages)
    _apply_states(sections, pages, global_notes)
    _apply_risks(sections, pages, global_notes)
    _apply_principles(sections, pages, global_notes)
    _apply_open_questions(sections, pages, global_notes)

    if not pages:
        unresolved_items.append(
            {
                "type": "page_inventory_missing",
                "message": "未识别到页面 / 窗口清单，页面预览卡无法稳定构建。",
            }
        )

    _apply_missing_defaults(pages)

    return {
        "project_id": project_id,
        "meta": {
            "title": _extract_title(text, source_path),
            "subject": "体验蓝图浏览器预览",
            "context": {
                "source_blueprint": str(source_path),
                "input_mode": "formal_export" if "exports" in str(source_path) else "workspace_fallback",
            },
        },
        "global_flow": _build_global_flow(sections, pages),
        "page_views": pages,
        "global_notes": global_notes,
        "unresolved_items": unresolved_items,
        "source_refs": [str(source_path)],
    }
