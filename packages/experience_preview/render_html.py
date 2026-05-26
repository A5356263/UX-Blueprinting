from __future__ import annotations

import html as html_mod
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

.summary-row {
  display: flex;
   align-items: center;
  gap: 8px;
   flex-wrap: wrap;
   margin-bottom: 8px;
}

.summary-row:last-child { margin-bottom: 0; }

.summary-role {
  min-width: 88px;
  padding: 4px 0;
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-strong);
}

.summary-path {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
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

.journey-path-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
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
  flex-wrap: wrap;
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

@media (max-width: 900px) {
  .sidebar { display: none; }
  .content { padding: 20px 16px 60px; }
}
"""


def _render_interaction_summary(summary: dict[str, Any]) -> str:
    rows = summary.get("rows") or []
    if not rows:
        return ""
    parts = ['<div class="summary-visual">']
    for row in rows:
        parts.append('<div class="summary-row">')
        parts.append(f'<div class="summary-role">{html_mod.escape(row.get("role", ""))}</div>')
        parts.append('<div class="summary-path">')
        for index, step in enumerate(row.get("steps") or []):
            parts.append(f'<span class="summary-step">{html_mod.escape(step)}</span>')
            if index < len((row.get("steps") or [])) - 1:
                parts.append('<span class="summary-arrow">→</span>')
        parts.append('</div>')
        parts.append('</div>')
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
    sections_html = _render_sections(exp["sections"], _experience_section_visuals(exp))
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
