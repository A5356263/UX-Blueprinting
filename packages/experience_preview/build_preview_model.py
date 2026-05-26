from __future__ import annotations

import html as html_mod
import re
from pathlib import Path
from typing import Any

from packages.common import get_project_exports_dir, get_project_workspace_dir

_H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def _read_source(project_id: str, filename: str) -> tuple[Path, str]:
    candidates = [
        get_project_exports_dir(project_id) / "final" / filename,
        get_project_workspace_dir(project_id) / filename,
    ]
    for path in candidates:
        if path.exists():
            return path, path.read_text(encoding="utf-8")
    raise SystemExit(f"Missing {filename} for preview in project {project_id}")


def _read_business_source(project_id: str) -> tuple[Path, str]:
    candidates = [
        "business_blueprint.md",
        "business_blueprint_lite.md",
        "business_note.md",
    ]
    missing: list[str] = []
    for filename in candidates:
        try:
            return _read_source(project_id, filename)
        except SystemExit:
            missing.append(filename)
    raise SystemExit(
        "Missing business blueprint source for preview in project "
        f"{project_id}: expected one of {', '.join(missing)}"
    )


def _make_anchor(heading: str) -> str:
    return re.sub(r"[^\w\u4e00-\u9fff]+", "-", heading).strip("-").lower()


def _split_sections(text: str) -> list[dict[str, Any]]:
    matches = list(_H2_RE.finditer(text))
    sections: list[dict[str, Any]] = []
    for i, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        sections.append({"heading": heading, "level": 1, "body": body, "anchor": _make_anchor(heading)})
    return sections


def _split_subsections(text: str, level: int) -> list[dict[str, Any]]:
    prefix = "#" * level
    pattern = re.compile(rf"^{prefix}\s+(.+?)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    result: list[dict[str, Any]] = []
    for i, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        result.append({"heading": heading, "body": body})
    return result


def _inline_md(text: str) -> str:
    text = html_mod.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def _is_table_separator(line: str) -> bool:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return False
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    return bool(cells) and all(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _render_table(lines: list[str]) -> str:
    header_cells = _split_table_row(lines[0])
    body_rows = [_split_table_row(line) for line in lines[2:]]
    thead = "".join(f"<th>{_inline_md(cell)}</th>" for cell in header_cells)
    tbody_rows: list[str] = []
    for row in body_rows:
        padded = row + [""] * max(0, len(header_cells) - len(row))
        cells = "".join(f"<td>{_inline_md(cell)}</td>" for cell in padded[: len(header_cells)])
        tbody_rows.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{thead}</tr></thead><tbody>{''.join(tbody_rows)}</tbody></table>"


def _extract_markdown_table(lines: list[str]) -> tuple[list[str], list[list[str]]]:
    for i in range(len(lines) - 1):
        if lines[i].strip().startswith("|") and _is_table_separator(lines[i + 1]):
            table_lines = [lines[i], lines[i + 1]]
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                table_lines.append(lines[j])
                j += 1
            return _split_table_row(table_lines[0]), [_split_table_row(line) for line in table_lines[2:]]
    return [], []


def _remove_first_markdown_table(text: str) -> str:
    lines = text.splitlines()
    for i in range(len(lines) - 1):
        if lines[i].strip().startswith("|") and _is_table_separator(lines[i + 1]):
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                j += 1
            remaining = lines[:i] + lines[j:]
            return "\n".join(remaining).strip()
    return text.strip()


def _plain_cell_text(text: str) -> str:
    text = text.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text.strip()


def _extract_journey_gaps(body: str) -> list[str]:
    items: list[str] = []
    in_gap_section = False
    for line in body.splitlines():
        stripped = line.strip()
        if re.match(r"^###\s+旅程缺口\s*$", stripped):
            in_gap_section = True
            continue
        if in_gap_section and re.match(r"^###\s+", stripped):
            break
        if in_gap_section and stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


def _parse_interaction_summary(body: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    in_role_block = False
    for line in body.splitlines():
        stripped = line.strip()
        if stripped in {"**涉及角色：**", "**涉及角色:**"}:
            in_role_block = True
            continue
        if in_role_block and (stripped.startswith("**") or re.match(r"^\d+\.\s+", stripped)):
            break
        if in_role_block and stripped.startswith("- "):
            content = stripped[2:].strip()
            if "：" not in content:
                continue
            role, path = content.split("：", 1)
            steps = [step.strip() for step in re.split(r"\s*(?:->|→)\s*", path) if step.strip()]
            if role.strip() and steps:
                rows.append({"role": role.strip(), "steps": steps})
    return rows


def _remove_interaction_summary_role_block(body: str) -> str:
    lines = body.splitlines()
    kept: list[str] = []
    in_role_block = False
    for line in lines:
        stripped = line.strip()
        if stripped in {"**涉及角色：**", "**涉及角色:**"}:
            in_role_block = True
            continue
        if in_role_block and stripped.startswith("- "):
            continue
        if in_role_block and not stripped:
            continue
        if in_role_block:
            in_role_block = False
        kept.append(line)
    return "\n".join(kept).strip()


def _md_body_to_html(body: str) -> str:
    if not body:
        return ""
    result: list[str] = []
    lines = body.splitlines()
    i = 0

    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue

        if stripped.startswith("```"):
            i += 1
            code_lines: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            result.append(f"<pre><code>{html_mod.escape(chr(10).join(code_lines))}</code></pre>")
            continue

        heading_match = re.match(r"^(#{3,6})\s+(.+?)\s*$", stripped)
        if heading_match:
            level = len(heading_match.group(1))
            result.append(f"<h{level}>{_inline_md(heading_match.group(2))}</h{level}>")
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and _is_table_separator(lines[i + 1]):
            table_lines = [lines[i], lines[i + 1]]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            result.append(_render_table(table_lines))
            continue

        if stripped.startswith("- "):
            items: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(f"<li>{_inline_md(lines[i].strip()[2:])}</li>")
                i += 1
            result.append(f"<ul>{''.join(items)}</ul>")
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                item_text = re.sub(r"^\d+\.\s+", "", lines[i].strip(), count=1)
                items.append(f"<li>{_inline_md(item_text)}</li>")
                i += 1
            result.append(f"<ol>{''.join(items)}</ol>")
            continue

        paragraph_lines = [stripped]
        i += 1
        while i < len(lines):
            next_stripped = lines[i].strip()
            if not next_stripped:
                break
            if next_stripped.startswith("```"):
                break
            if re.match(r"^(#{3,6})\s+.+$", next_stripped):
                break
            if next_stripped.startswith("- "):
                break
            if re.match(r"^\d+\.\s+", next_stripped):
                break
            if next_stripped.startswith("|") and i + 1 < len(lines) and _is_table_separator(lines[i + 1]):
                break
            paragraph_lines.append(next_stripped)
            i += 1
        result.append(f"<p>{'<br>'.join(_inline_md(part) for part in paragraph_lines)}</p>")

    return "\n".join(result)


def _parse_experience_node(body: str) -> dict[str, Any]:
    node: dict[str, Any] = {}
    field_labels = {
        "user_action": "用户动作",
        "system_feedback": "系统反馈",
        "explanation": "需要前置解释的信息",
        "copy_text": "建议文案",
        "success_copy": "成功反馈",
        "error_copy": "异常提示",
        "failure_copy": "失败反馈",
        "buttons": "按钮",
        "next_step": "下一步",
        "options_note": "选项说明文案",
    }
    raw_lines = body.splitlines()
    current_key: str | None = None
    field_chunks: dict[str, list[str]] = {}
    description_lines: list[str] = []

    for raw_line in raw_lines:
        stripped = raw_line.strip()
        matched_key = next((key for key, label in field_labels.items() if stripped.startswith(f"**{label}")), None)
        if matched_key:
            current_key = matched_key
            field_chunks.setdefault(current_key, [])
            inline = re.sub(r"^\*\*.+?\*\*[:：]?\s*", "", stripped)
            if inline:
                field_chunks[current_key].append(inline)
            continue
        if current_key:
            field_chunks[current_key].append(stripped)
            continue
        current_key = None
        description_lines.append(raw_line)

    for key, chunks in field_chunks.items():
        value = "\n".join(line for line in chunks if line).strip()
        if value:
            node[key] = value
    node["_has_fields"] = bool(field_chunks)
    remaining = "\n".join(description_lines).strip()
    node["description_html"] = _md_body_to_html(remaining) if remaining else ""
    return node


def _extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def build_preview_model(project_id: str) -> dict[str, Any]:
    business_path, business_text = _read_business_source(project_id)
    experience_path, experience_text = _read_source(project_id, "experience_blueprint.md")

    business_sections = _split_sections(business_text)
    for section in business_sections:
        section["body_html"] = _md_body_to_html(section.pop("body"))

    experience_sections = _split_sections(experience_text)
    pages: list[dict[str, Any]] = []
    states: list[str] = []
    state_rows: list[dict[str, str]] = []
    journey: dict[str, Any] = {"heading": "", "stages": [], "rows": [], "gaps": []}
    interaction_summary: dict[str, Any] = {"heading": "", "rows": []}
    detail_flows: dict[str, list[dict[str, Any]]] = {}

    for section in experience_sections:
        heading = section["heading"]
        body = section["body"]

        if heading == "2. 交互流程总览":
            interaction_summary = {
                "heading": heading,
                "rows": _parse_interaction_summary(body),
            }
            body = _remove_interaction_summary_role_block(body)

        if heading in {"3. 主交互流程", "4. 次交互流程"}:
            subs = _split_subsections(body, 3)
            section_flows: list[dict[str, Any]] = []
            for sub in subs:
                nodes: list[dict[str, Any]] = []
                node_subs = _split_subsections(sub["body"], 4)
                for node_section in node_subs:
                    node = _parse_experience_node(node_section["body"])
                    node["name"] = node_section["heading"]
                    nodes.append(node)
                if not nodes and sub["body"].strip():
                    node = _parse_experience_node(sub["body"])
                    node["name"] = sub["heading"]
                    if any(
                        [
                            node.get("trigger"),
                            node.get("user_action"),
                            node.get("system_response"),
                            node.get("next_step"),
                            node.get("description_html"),
                        ]
                    ):
                        nodes.append(node)
                if nodes:
                    item = {"name": sub["heading"], "nodes": nodes}
                    section_flows.append(item)
                elif sub["body"].strip():
                    section_flows.append({"name": sub["heading"], "body_html": _md_body_to_html(sub["body"]), "nodes": []})
            if section_flows:
                detail_flows[heading] = section_flows

        if heading == "1. 旅程图":
            header_cells, body_rows = _extract_markdown_table(body.splitlines())
            if len(header_cells) >= 2:
                rows: list[dict[str, Any]] = []
                for row in body_rows:
                    if not row:
                        continue
                    role = _plain_cell_text(row[0])
                    cells = [_plain_cell_text(cell) for cell in row[1 : len(header_cells)]]
                    if role:
                        rows.append({"role": role, "cells": cells})
                journey = {
                    "heading": heading,
                    "stages": [_plain_cell_text(cell) for cell in header_cells[1:]],
                    "rows": rows,
                    "gaps": _extract_journey_gaps(body),
                }
            body = _remove_first_markdown_table(body)

        if heading == "6. 页面 / 弹窗 / 抽屉设计":
            subs = _split_subsections(body, 3)
            for sub in subs:
                pages.append({"name": sub["heading"], "desc_html": _md_body_to_html(sub["body"])})

        if heading == "7. 状态与反馈文案":
            header_cells, body_rows = _extract_markdown_table(body.splitlines())
            if header_cells:
                normalized_headers = [_plain_cell_text(cell) for cell in header_cells]
                for row in body_rows:
                    values = [_plain_cell_text(cell) for cell in row]
                    row_map = {
                        normalized_headers[idx]: values[idx] if idx < len(values) else ""
                        for idx in range(len(normalized_headers))
                    }
                    if row_map:
                        state_rows.append(row_map)
            for line in body.splitlines():
                stripped = line.strip()
                if stripped.startswith("- "):
                    states.append(stripped[2:])

        section["body_html"] = _md_body_to_html(body)
        section.pop("body")

    return {
        "project_id": project_id,
        "meta": {
            "title": _extract_title(experience_text, "Experience Blueprint"),
            "version": "v3",
            "source_business": str(business_path),
            "source_experience": str(experience_path),
        },
        "business": {
            "title": _extract_title(business_text, "Business Blueprint"),
            "sections": business_sections,
        },
        "experience": {
            "title": _extract_title(experience_text, "Experience Blueprint"),
            "sections": experience_sections,
            "journey": journey,
            "interaction_summary": interaction_summary,
            "detail_flows": detail_flows,
            "pages": pages,
            "states": states,
            "state_rows": state_rows,
        },
    }
