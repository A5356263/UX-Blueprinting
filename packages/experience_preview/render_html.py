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

.app { display: flex; min-height: 100vh; }

/* ---- sidebar ---- */
.sidebar {
  width: 280px;
  min-width: 280px;
  background: var(--panel);
  border-right: 1px solid var(--line);
  padding: 24px 0;
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: hidden;
}

.sidebar-header {
  padding: 0 20px 16px;
  border-bottom: 1px solid var(--line);
}

.sidebar-header h2 {
  margin: 0 0 4px;
  font-size: 18px;
  color: var(--accent-strong);
}

.project-badge {
  font-size: 12px;
  color: var(--text-muted);
  background: var(--panel-subtle);
  padding: 2px 8px;
  border-radius: 4px;
  display: inline-block;
  margin-top: 4px;
}

.sidebar-tabs {
  display: flex;
  padding: 12px 12px 0;
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
  padding: 8px 0;
}

.nav-section { padding: 0 20px; }

.nav-item {
  display: block;
  padding: 5px 12px;
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
.nav-divider {
  font-size: 11px;
  color: var(--text-soft);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 12px 12px 4px;
  font-weight: 600;
}

/* ---- main content ---- */
.content {
  flex: 1;
  padding: 32px 40px 80px;
  max-width: 960px;
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
  color: var(--text);
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
.section-body ul {
  margin: 8px 0 16px;
  padding-left: 20px;
  list-style: none;
}

.section-body ul li {
  position: relative;
  padding: 4px 0 4px 16px;
  margin: 2px 0;
}

.section-body ul li::before {
  content: "—";
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

.section-body ol {
  margin: 8px 0 16px;
  padding-left: 22px;
}

.section-body ol li {
  padding: 4px 0;
}

/* ---- flow groups ---- */
.flow-group { margin-bottom: 28px; }

.flow-name {
  font-size: 16px;
  font-weight: 500;
  color: var(--text);
  margin: 0 0 16px;
  padding: 8px 14px;
  background: var(--accent-soft);
  border-radius: var(--radius);
  border-left: 4px solid var(--accent);
}

/* ---- node cards ---- */
.node-card {
  background: var(--panel-strong);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04);
}

.node-name {
  font-size: 15px;
  font-weight: 500;
  color: var(--text);
  margin: 0 0 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--line);
}

.node-field {
  margin-bottom: 10px;
  display: flex;
  gap: 8px;
}

.node-field-label {
  min-width: 72px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
  padding-top: 2px;
}

.node-field-value {
  flex: 1;
  font-size: 14px;
}

.node-field-value p { margin: 0; }

.node-desc {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px dashed var(--line);
  font-size: 14px;
  color: var(--text-muted);
}

/* ---- page cards ---- */
.page-card {
  background: var(--panel-strong);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 16px 20px;
  margin-bottom: 12px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04);
}

.page-card-name {
  font-size: 15px;
  font-weight: 500;
  color: var(--text);
  margin: 0 0 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-card-name .icon { font-size: 18px; }

.page-card-desc { font-size: 14px; }
.page-card-desc p { margin: 0 0 6px; }

/* ---- states list ---- */
.states-list {
  list-style: none;
  padding: 0;
  display: grid;
  gap: 8px;
}

.state-item {
  background: var(--panel-strong);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 12px 16px;
  font-size: 14px;
  box-shadow: 0 1px 4px rgba(63, 49, 30, 0.03);
}

.state-item strong { color: var(--accent-strong); }

/* ---- footer ---- */
.preview-footer {
  margin-top: 48px;
  padding-top: 16px;
  border-top: 1px solid var(--line);
  font-size: 12px;
  color: var(--text-soft);
}

/* ---- responsive ---- */
@media (max-width: 900px) {
  .sidebar { display: none; }
  .content { padding: 20px 16px 60px; }
}
"""


def _field_label(key: str) -> str:
    labels = {
        "user_action": "用户动作",
        "system_feedback": "系统反馈",
        "explanation": "前置解释",
        "copy_text": "页面文案",
        "success_copy": "成功文案",
        "error_copy": "异常提示",
        "failure_copy": "失败反馈",
        "buttons": "按钮",
        "next_step": "下一步",
        "options_note": "选项说明",
    }
    return labels.get(key, key)


def _render_node_card(node: dict[str, Any]) -> str:
    parts = [f'<h4 class="node-name">{html_mod.escape(node.get("name", ""))}</h4>']
    field_order = ["user_action", "system_feedback", "explanation", "copy_text", "success_copy", "error_copy", "failure_copy", "options_note", "buttons", "next_step"]
    for key in field_order:
        value = node.get(key, "")
        if value:
            label = _field_label(key)
            parts.append(
                f'<div class="node-field">'
                f'<span class="node-field-label">{label}</span>'
                f'<span class="node-field-value">{_inline_text(value)}</span>'
                f"</div>"
            )
    if node.get("description_html"):
        parts.append(f'<div class="node-desc">{node["description_html"]}</div>')
    parts_html = "\n".join(parts)
    return f'<div class="node-card">{parts_html}</div>'


def _inline_text(text: str) -> str:
    text = html_mod.escape(text)
    text = text.replace("**", "")
    text = text.replace("\n", "<br>")
    return text


def _render_sections(sections: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for s in sections:
        level_class = f"level-{s['level']}" if s["level"] > 1 else ""
        parts.append(f'<div class="section-block" id="{s["anchor"]}">')
        parts.append(f'<h2 class="section-heading {level_class}">{html_mod.escape(s["heading"])}</h2>')
        parts.append(f'<div class="section-body">{s["body_html"]}</div>')
        parts.append("</div>")
    return "\n".join(parts)


def _render_nav_items(sections: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for s in sections:
        cls = f"level-{s['level']}" if s["level"] > 1 else ""
        parts.append(f'<a class="nav-item {cls}" data-target="{s["anchor"]}">{html_mod.escape(s["heading"])}</a>')
    return "\n".join(parts)


def _render_business(model: dict[str, Any]) -> str:
    biz = model["business"]
    sections_html = _render_sections(biz["sections"])
    return f"""
    <div class="content-panel" id="content-business">
      <h1 style="font-size:24px;font-weight:700;color:var(--accent-strong);margin:0 0 28px;">{html_mod.escape(biz['title'])}</h1>
      {sections_html}
    </div>"""


def _render_experience(model: dict[str, Any]) -> str:
    exp = model["experience"]
    sections_html = _render_sections(exp["sections"])
    return f"""
    <div class="content-panel hidden" id="content-experience">
      <h1 style="font-size:24px;font-weight:700;color:var(--accent-strong);margin:0 0 28px;">{html_mod.escape(exp['title'])}</h1>
      {sections_html}
    </div>"""


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
<title>蓝图预览 — {html_mod.escape(project_id)}</title>
<link rel="stylesheet" href="./assets/style.css">
</head>
<body>
<div class="app">

<nav class="sidebar">
  <div class="sidebar-header">
    <h2>蓝图预览</h2>
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
    assets_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / "style.css").write_text(STYLE_CSS, encoding="utf-8")
    (preview_dir / "index.html").write_text(_render_html(model), encoding="utf-8")
