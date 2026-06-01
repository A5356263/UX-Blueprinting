from __future__ import annotations

import html as html_mod
import re
from pathlib import Path
from typing import Any

STYLE_CSS = r"""
:root {
  --bg: #f5f4ed;
  --panel: #faf9f5;
  --panel-strong: #faf9f5;
  --panel-subtle: #f2f0e8;
  --line: #e8e6dc;
  --line-strong: #d8d1c2;
  --text: #2b2b28;
  --text-muted: #6b6a64;
  --text-soft: #75746e;
  --accent: #1f6b5b;
  --accent-soft: #e2f1eb;
  --accent-strong: #155245;
  --warn: #8a5a14;
  --warn-soft: #f6ead5;
  --danger: #8b3a3a;
  --danger-soft: #f8e4e1;
  --shadow: 0 2px 16px rgba(0, 0, 0, 0.06);
  --radius: 8px;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: "PingFang SC", "Microsoft YaHei", "Segoe UI", system-ui, sans-serif;
  background: linear-gradient(180deg, #faf9f5 0%, var(--bg) 100%);
  color: var(--text);
  line-height: 1.55;
}

.hidden { display: none !important; }

.app { display: flex; min-height: 100vh; }

.sidebar {
  width: 280px;
  min-width: 280px;
  background: var(--panel);
  border-right: 1px solid var(--line);
  padding: 14px 0;
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: hidden;
}

.sidebar-header {
  padding: 0 16px 10px;
  border-bottom: 1px solid var(--line);
}

.sidebar-header h2 {
  margin: 0 0 3px;
  font-size: 16px;
  color: var(--accent-strong);
}

.project-badge {
  font-size: 11px;
  color: var(--text-muted);
  background: var(--panel-subtle);
  padding: 2px 8px;
  border-radius: 4px;
  display: inline-block;
  margin-top: 2px;
}

.sidebar-tabs {
  display: flex;
  padding: 10px 12px 0;
  gap: 4px;
}

.tab-btn {
  flex: 1;
  padding: 8px 4px;
  border: 1px solid var(--line);
  background: var(--panel-subtle);
  color: var(--text-muted);
  font-size: 13px;
  cursor: pointer;
  border-radius: 6px 6px 0 0;
  transition: all 0.15s;
  text-align: center;
}

.tab-btn.active {
  background: var(--panel-strong);
  color: var(--accent-strong);
  border-bottom-color: var(--panel-strong);
  font-weight: 600;
}

.tab-btn:hover:not(.active) { color: var(--text); }

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 6px 0 8px;
}

.nav-section { padding: 0 16px; }

.nav-item {
  display: block;
  padding: 4px 10px;
  font-size: 13px;
  color: var(--text-muted);
  text-decoration: none;
  border-radius: 4px;
  margin: 1px 0;
  transition: all 0.12s;
  cursor: pointer;
}

.nav-item:hover { background: var(--accent-soft); color: var(--accent-strong); }
.nav-item.level-2 { padding-left: 24px; font-size: 12px; }
.nav-item.level-3 { padding-left: 36px; font-size: 12px; color: var(--text-soft); }

.content {
  flex: 1;
  padding: 32px 40px 80px;
  max-width: 1080px;
}

.content-panel { display: block; }
.content-panel.hidden { display: none; }

.section-block {
  margin-bottom: 36px;
  scroll-margin-top: 24px;
}

.section-heading {
  font-size: 18px;
  font-weight: 500;
  color: var(--text);
  margin: 0 0 12px;
  padding-left: 12px;
  border-left: 3px solid var(--accent);
}

.section-heading.level-2 {
  font-size: 16px;
  border-bottom: 1px solid var(--line);
}

.section-heading.level-3 {
  font-size: 15px;
  color: var(--text-muted);
  border-bottom: none;
  font-weight: 600;
}

.section-body { font-size: 15px; }
.section-body p { margin: 0 0 10px; }
.section-body ul { margin: 8px 0 16px; padding-left: 20px; list-style: none; }
.section-body ul li {
  position: relative;
  padding: 4px 0 4px 16px;
  margin: 2px 0;
}
.section-body ul li::before {
  content: "•";
  position: absolute;
  left: 0;
  color: var(--accent);
  font-size: 12px;
}
.section-body strong { color: var(--accent-strong); font-weight: 600; }
.section-body code {
  background: var(--panel-subtle);
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 0.9em;
  border: 1px solid var(--line);
}
.section-body pre {
  background: var(--panel-subtle);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 16px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.5;
}
.section-body h3,
.section-body h4,
.section-body h5,
.section-body h6 {
  margin: 18px 0 10px;
  color: var(--accent-strong);
  font-weight: 600;
}
.section-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0 18px;
  background: var(--panel-strong);
  border: 1px solid var(--line);
}
.section-body th,
.section-body td {
  padding: 10px 12px;
  border: 1px solid var(--line);
  text-align: left;
  vertical-align: top;
}
.section-body th {
  background: var(--panel-subtle);
  color: var(--accent-strong);
  font-weight: 600;
}
.section-body ol { margin: 8px 0 16px; padding-left: 22px; }
.section-body ol li { padding: 4px 0; }

.summary-visual,
.journey-visual {
  margin: 0 0 18px;
  padding: 12px;
  background: var(--panel-subtle);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow-x: auto;
}

.summary-path {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
  flex: 1 1 auto;
  min-width: max-content;
}

.summary-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: nowrap;
  margin-bottom: 10px;
}

.summary-row:last-child { margin-bottom: 0; }

.summary-role {
  min-width: 96px;
  padding: 4px 0;
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-strong);
  flex: 0 0 auto;
}

.flow-arrow,
.summary-arrow {
  color: var(--text-soft);
  font-size: 13px;
  display: flex;
  align-items: center;
  flex: 0 0 auto;
}

.summary-step {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 6px 10px;
  background: var(--panel-strong);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  color: var(--text);
  font-size: 12px;
  line-height: 1.35;
}

.summary-step strong {
  color: var(--accent-strong);
  margin-right: 4px;
}

.journey-path-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: nowrap;
  min-width: max-content;
  margin-bottom: 10px;
}

.journey-path-row:last-child { margin-bottom: 0; }

.journey-path-role {
  min-width: 96px;
  padding: 4px 0;
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-strong);
}

.journey-path-nodes {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
  min-width: max-content;
}

.journey-path-node {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 6px 10px;
  background: var(--panel-strong);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  color: var(--text);
  font-size: 12px;
  line-height: 1.35;
}

.journey-path-arrow {
  color: var(--text-soft);
  font-size: 13px;
  display: flex;
  align-items: center;
  flex: 0 0 auto;
}

.preview-footer {
  margin-top: 48px;
  padding-top: 16px;
  border-top: 1px solid var(--line);
  font-size: 12px;
  color: var(--text-soft);
}

.component-intro:empty,
.component-visuals:empty,
.component-cards:empty,
.component-notes:empty {
  display: none;
}

.component-intro {
  margin-bottom: 12px;
}

.component-intro:last-child {
  margin-bottom: 0;
}

.component-visuals {
  margin-bottom: 12px;
}

.component-visuals:last-child {
  margin-bottom: 0;
}

.component-cards {
  display: block;
}

.component-card {
  background: transparent;
  border: none;
  padding: 0;
  margin-bottom: 18px;
}

.component-card:last-child {
  margin-bottom: 0;
}

.component-card + .component-card {
  margin-top: 6px;
}

.component-card-title {
  margin: 18px 0 10px;
  font-size: 15px;
  font-weight: 600;
  color: var(--accent-strong);
}

.experience-component[data-section-key="main-flow"] .section-body h3,
.experience-component[data-section-key="secondary-flow"] .section-body h3,
.experience-component[data-section-key="exception-flow"] .section-body h3 {
  margin: 32px 0 10px;
}

.experience-component[data-section-key="main-flow"] .section-body h3:first-child,
.experience-component[data-section-key="secondary-flow"] .section-body h3:first-child,
.experience-component[data-section-key="exception-flow"] .section-body h3:first-child {
  margin-top: 0;
}

.experience-component .section-body .flow-field-label {
  margin-top: 20px;
}

.experience-component .section-body .flow-field-label + * {
  margin-top: 0;
}

.component-card-body > *:last-child {
  margin-bottom: 0;
}

.component-note-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}

.component-note-item {
  padding: 8px 0 8px 16px;
  border: none;
  border-radius: 0;
  background: transparent;
  position: relative;
}

.component-note-item::before {
  content: "•";
  position: absolute;
  left: 0;
  color: var(--accent);
  font-size: 12px;
}

.component-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.component-pill {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: var(--panel-subtle);
  color: var(--text-muted);
  font-size: 12px;
}

.state-feedback-table-wrap {
  overflow-x: auto;
}

.state-feedback-table-wrap table {
  min-width: 680px;
  margin-bottom: 0;
}

@media (max-width: 900px) {
  .sidebar { display: none; }
  .content { padding: 20px 16px 60px; }
}
"""

FLOW_FIELD_LABELS: list[tuple[str, str]] = [
    ("user_action", "用户动作"),
    ("system_feedback", "系统反馈"),
    ("explanation", "需要前置解释的信息"),
    ("copy_text", "建议文案"),
    ("success_copy", "成功反馈"),
    ("error_copy", "异常提示"),
    ("failure_copy", "失败反馈"),
    ("buttons", "按钮"),
    ("next_step", "下一步"),
    ("options_note", "选项说明文案"),
]


def _render_interaction_summary(summary: dict[str, Any]) -> str:
    rows = summary.get("rows") or []
    if not rows:
        return ""
    parts = ['<div class="summary-visual main-node-map">']
    for row in rows:
        parts.append('<div class="summary-row">')
        parts.append(f'<div class="summary-role">{html_mod.escape(str(row.get("role", "")))}</div>')
        parts.append('<div class="summary-path">')
        nodes = row.get("nodes") or []
        for index, node in enumerate(nodes):
            if node.get("has_detail") and node.get("id"):
                parts.append(
                    f'<span class="summary-step"><strong>{html_mod.escape(str(node.get("id", "")))}</strong> '
                    f'{html_mod.escape(str(node.get("name", "")))}</span>'
                )
            else:
                parts.append(f'<span class="summary-step">{html_mod.escape(str(node.get("name", "")))}</span>')
            if index < len(nodes) - 1:
                parts.append('<span class="summary-arrow">→</span>')
        parts.append('</div></div>')
    parts.append("</div>")
    return "".join(parts)


def _render_journey_visual(journey: dict[str, Any]) -> str:
    paths = journey.get("paths") or []
    if not paths:
        return ""
    parts = ['<div class="journey-visual">']
    for path in paths:
        parts.append('<div class="journey-path-row">')
        parts.append(f'<div class="journey-path-role">{html_mod.escape(path.get("role", ""))}</div>')
        parts.append('<div class="journey-path-nodes">')
        nodes = path.get("nodes") or []
        for index, node in enumerate(nodes):
            parts.append(f'<span class="journey-path-node">{html_mod.escape(node)}</span>')
            if index < len(nodes) - 1:
                parts.append('<span class="journey-path-arrow">→</span>')
        parts.append('</div>')
        parts.append('</div>')
    parts.append("</div>")
    return "".join(parts)


def _render_sections(sections: list[dict[str, Any]], section_visuals: dict[str, str] | None = None) -> str:
    parts: list[str] = []
    visuals = section_visuals or {}
    for section in sections:
        level_class = f"level-{section['level']}" if section["level"] > 1 else ""
        body_html = visuals.get(section["heading"], "") + section["body_html"]
        parts.append(f'<div class="section-block" id="{section["anchor"]}">')
        parts.append(f'<h2 class="section-heading {level_class}">{html_mod.escape(section["heading"])}</h2>')
        parts.append(f'<div class="section-body">{body_html}</div>')
        parts.append("</div>")
    return "\n".join(parts)


def _soften_code_blocks(body_html: str) -> str:
    def _replace(match: re.Match[str]) -> str:
        raw = html_mod.unescape(match.group(1)).strip()
        if not raw:
            return ""
        lines = [line.rstrip() for line in raw.splitlines()]
        rendered = "<br>".join(html_mod.escape(line) for line in lines)
        return f"<p>{rendered}</p>"

    return re.sub(r"<pre><code>([\s\S]*?)</code></pre>", _replace, body_html)


def _render_flow_value(value: str) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    html = value
    if "<" not in value:
        html = _mdish_to_html(value)
    return _soften_code_blocks(html)


def _mdish_to_html(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    parts: list[str] = []
    bullet_buffer: list[str] = []

    def flush_bullets() -> None:
        nonlocal bullet_buffer
        if bullet_buffer:
            items = "".join(f"<li>{html_mod.escape(item)}</li>" for item in bullet_buffer)
            parts.append(f"<ul>{items}</ul>")
            bullet_buffer = []

    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if paragraph_lines:
            parts.append(f"<p>{'<br>'.join(html_mod.escape(line) for line in paragraph_lines)}</p>")
            paragraph_lines = []

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            flush_bullets()
            flush_paragraph()
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            bullet_buffer.append(stripped[2:].strip())
            continue
        flush_bullets()
        paragraph_lines.append(stripped)

    flush_bullets()
    flush_paragraph()
    return "".join(parts)


def _render_detail_flow_groups(groups: list[dict[str, Any]]) -> str:
    if not groups:
        return ""
    parts: list[str] = []
    for group in groups:
        group_name = str(group.get("name", "")).strip()
        if group_name:
            parts.append(f"<h3>{html_mod.escape(group_name)}</h3>")

        group_body_html = str(group.get("body_html", "") or "")
        if group_body_html:
            parts.append(_soften_code_blocks(group_body_html))
            continue

        nodes = group.get("nodes") or []
        for node in nodes:
            node_name = str(node.get("name", "")).strip()
            if node_name and node_name != group_name:
                parts.append(f"<h4>{html_mod.escape(node_name)}</h4>")

            description_html = str(node.get("description_html", "") or "")
            if description_html:
                parts.append(_soften_code_blocks(description_html))

            for key, label in FLOW_FIELD_LABELS:
                rendered = _render_flow_value(str(node.get(key, "") or ""))
                if rendered:
                    parts.append(f"<p><strong>{html_mod.escape(label)}：</strong></p>")
                    parts.append(rendered)
    return "".join(parts)


def _render_note_list(items: list[str]) -> str:
    if not items:
        return ""
    parts = ['<ul class="component-note-list">']
    for item in items:
        parts.append(f'<li class="component-note-item">{html_mod.escape(str(item))}</li>')
    parts.append("</ul>")
    return "".join(parts)


def _render_detail_flow_groups_stable(groups: list[dict[str, Any]]) -> str:
    if not groups:
        return ""
    parts: list[str] = []
    for group in groups:
        group_name = str(group.get("name", "")).strip()
        if group_name:
            parts.append(f"<h3>{html_mod.escape(group_name)}</h3>")

        group_body_html = str(group.get("body_html", "") or "")
        if group_body_html:
            parts.append(_soften_code_blocks(group_body_html))
            continue

        nodes = group.get("nodes") or []
        for node in nodes:
            node_name = str(node.get("name", "")).strip()
            if node_name and node_name != group_name:
                parts.append(f"<h4>{html_mod.escape(node_name)}</h4>")

            description_html = str(node.get("description_html", "") or "")
            if description_html:
                parts.append(_soften_code_blocks(description_html))

            for key, label in FLOW_FIELD_LABELS:
                rendered = _render_flow_value(str(node.get(key, "") or ""))
                if rendered:
                    parts.append(f'<p class="flow-field-label"><strong>{html_mod.escape(label)}：</strong></p>')
                    parts.append(rendered)
    return "".join(parts)


def _render_titled_note_list(title: str, items: list[str]) -> str:
    if not items:
        return ""
    return f"<h3>{html_mod.escape(title)}</h3>{_render_note_list(items)}"


def _render_state_feedback_table(rows: list[dict[str, str]]) -> str:
    if not rows:
        return ""
    headers = list(rows[0].keys())
    thead = "".join(f"<th>{html_mod.escape(header)}</th>" for header in headers)
    tbody_rows: list[str] = []
    for row in rows:
        cells = "".join(f"<td>{html_mod.escape(str(row.get(header, '')))}</td>" for header in headers)
        tbody_rows.append(f"<tr>{cells}</tr>")
    return (
        '<div class="state-feedback-table-wrap"><table>'
        f"<thead><tr>{thead}</tr></thead><tbody>{''.join(tbody_rows)}</tbody></table></div>"
    )


def _render_experience_section(section: dict[str, Any], exp: dict[str, Any]) -> str:
    section_key = str(section.get("section_key", "generic"))
    heading = html_mod.escape(str(section.get("heading", "")))
    anchor = html_mod.escape(str(section.get("anchor", "")))
    intro_html = str(section.get("intro_html") or "")
    fallback_body_html = str(section.get("body_html") or "")

    body_parts: list[str] = []

    if section_key == "journey":
        visual_html = _render_journey_visual(exp.get("journey") or {})
        if visual_html:
            body_parts.append(visual_html)
        notes_html = _render_titled_note_list("旅程缺口", (exp.get("journey") or {}).get("gaps") or [])
        if notes_html:
            body_parts.append(notes_html)
        body_html = "".join(body_parts) or _soften_code_blocks(intro_html or fallback_body_html)
    elif section_key == "flow-overview":
        summary_html = _render_interaction_summary(exp.get("interaction_summary") or {})
        if summary_html:
            body_parts.append(summary_html)
        if intro_html:
            body_parts.append(_soften_code_blocks(intro_html))
        body_html = "".join(body_parts) or _soften_code_blocks(fallback_body_html)
    elif section_key in {"main-flow", "secondary-flow"}:
        body_html = _render_detail_flow_groups_stable((exp.get("detail_flows") or {}).get(section.get("heading", ""), [])) or _soften_code_blocks(fallback_body_html)
    elif section_key in {"exception-flow", "page-structure"}:
        body_html = _render_detail_flow_groups_stable(
            [{"name": sub.get("heading", ""), "body_html": sub.get("body_html", "")} for sub in (section.get("subsections") or [])]
        ) or _soften_code_blocks(fallback_body_html)
    elif section_key == "state-feedback":
        table_html = _render_state_feedback_table(exp.get("state_rows") or [])
        if table_html:
            body_parts.append(table_html)
        if intro_html:
            body_parts.append(_soften_code_blocks(intro_html))
        body_html = "".join(body_parts) or _soften_code_blocks(fallback_body_html)
    else:
        body_html = _soften_code_blocks(fallback_body_html)

    return (
        f'<div class="section-block experience-component" id="{anchor}" data-section-key="{html_mod.escape(section_key)}">'
        f'<h2 class="section-heading">{heading}</h2>'
        f'<div class="section-body">{body_html}</div>'
        "</div>"
    )


def _render_experience_sections(exp: dict[str, Any]) -> str:
    return "\n".join(_render_experience_section(section, exp) for section in exp["sections"])


def _render_nav_items(sections: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for section in sections:
        cls = f"level-{section['level']}" if section["level"] > 1 else ""
        parts.append(f'<a class="nav-item {cls}" data-target="{section["anchor"]}">{html_mod.escape(section["heading"])}</a>')
    return "\n".join(parts)


def _experience_section_visuals(exp: dict[str, Any]) -> dict[str, str]:
    visuals: dict[str, str] = {}
    journey = exp.get("journey") or {}
    if journey.get("heading"):
        visuals[journey["heading"]] = _render_journey_visual(journey)
    summary = exp.get("interaction_summary") or {}
    if summary.get("heading"):
        visuals[summary["heading"]] = _render_interaction_summary(summary)
    return visuals


def _render_business(model: dict[str, Any]) -> str:
    biz = model["business"]
    sections_html = _render_sections(biz["sections"])
    return (
        '<div class="content-panel" id="content-business">'
        f'<h1 style="font-size:24px;font-weight:700;color:var(--accent-strong);margin:0 0 28px;">{html_mod.escape(biz["title"])}</h1>'
        f"{sections_html}</div>"
    )


def _render_experience(model: dict[str, Any]) -> str:
    exp = model["experience"]
    sections_html = _render_experience_sections(exp)
    return (
        '<div class="content-panel hidden" id="content-experience">'
        f'<h1 style="font-size:24px;font-weight:700;color:var(--accent-strong);margin:0 0 28px;">{html_mod.escape(exp["title"])}</h1>'
        f"{sections_html}</div>"
    )


def _render_html(model: dict[str, Any]) -> str:
    project_id = model["project_id"]
    business_nav = _render_nav_items(model["business"]["sections"])
    experience_nav = _render_nav_items(model["experience"]["sections"])
    business_content = _render_business(model)
    experience_content = _render_experience(model)
    meta = model["meta"]

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>体验策略 — {html_mod.escape(project_id)}</title>
<style>
{STYLE_CSS}
</style>
</head>
<body>
<div class="app">
<nav class="sidebar">
  <div class="sidebar-header">
    <h2>体验策略</h2>
    <span class="project-badge">{html_mod.escape(project_id)}</span>
  </div>
  <div class="sidebar-tabs">
    <button class="tab-btn active" data-panel="business">业务蓝图</button>
    <button class="tab-btn" data-panel="experience">体验蓝图</button>
  </div>
  <div class="sidebar-nav" id="nav-business">
    <div class="nav-section">{business_nav}</div>
  </div>
  <div class="sidebar-nav hidden" id="nav-experience">
    <div class="nav-section">{experience_nav}</div>
  </div>
</nav>
<main class="content">
  {business_content}
  {experience_content}
  <footer class="preview-footer">
    来源：{html_mod.escape(meta.get('source_experience', ''))} &nbsp;|&nbsp; 版本 {html_mod.escape(meta.get('version', ''))}
  </footer>
</main>
</div>
<script>
(function() {{
  var tabs = document.querySelectorAll('.tab-btn');
  var navBusiness = document.getElementById('nav-business');
  var navExperience = document.getElementById('nav-experience');
  var contentBusiness = document.getElementById('content-business');
  var contentExperience = document.getElementById('content-experience');
  var current = 'business';

  function switchPanel(name) {{
    current = name;
    tabs.forEach(function(t) {{ t.classList.toggle('active', t.dataset.panel === name); }});
    navBusiness.classList.toggle('hidden', name !== 'business');
    navExperience.classList.toggle('hidden', name !== 'experience');
    contentBusiness.classList.toggle('hidden', name !== 'business');
    contentExperience.classList.toggle('hidden', name !== 'experience');
  }}

  tabs.forEach(function(t) {{
    t.addEventListener('click', function() {{ switchPanel(t.dataset.panel); }});
  }});

  document.querySelectorAll('.nav-item').forEach(function(item) {{
    item.addEventListener('click', function(e) {{
      e.preventDefault();
      var panel = item.closest('.sidebar-nav').id === 'nav-business' ? 'business' : 'experience';
      if (panel !== current) switchPanel(panel);
      var target = document.getElementById(item.dataset.target);
      if (target) target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }});
  }});
}})();
</script>
</body>
</html>"""


def write_preview_site(preview_dir: Path, model: dict[str, Any]) -> None:
    assets_dir = preview_dir / "assets"
    legacy_style = assets_dir / "style.css"
    if legacy_style.exists():
        legacy_style.unlink()
    if assets_dir.exists():
        try:
            assets_dir.rmdir()
        except OSError:
            pass
    (preview_dir / "index.html").write_text(_render_html(model), encoding="utf-8")
