from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


STYLE_CSS = """
body {
  margin: 0;
  font-family: "Segoe UI", Arial, sans-serif;
  background: #f5f7fb;
  color: #1f2937;
}

.page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}

.hero,
.panel,
.page-card {
  background: #ffffff;
  border: 1px solid #d9e2f0;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
}

.hero {
  padding: 24px;
  margin-bottom: 24px;
}

.hero h1 {
  margin: 0 0 12px;
  font-size: 28px;
}

.hero p,
.hero li,
.panel li,
.page-card li {
  line-height: 1.6;
}

.meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  color: #4b5563;
  font-size: 14px;
}

.layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

.panel {
  padding: 20px;
}

.section-title {
  margin: 0 0 16px;
  font-size: 20px;
}

.flow-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.flow-node {
  min-width: 180px;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid #bdd2f4;
  background: #eef4ff;
}

.flow-node small {
  display: block;
  color: #4b5563;
  margin-bottom: 8px;
}

.flow-arrow {
  color: #64748b;
  font-size: 22px;
}

.flow-legend {
  display: flex;
  gap: 16px;
  margin-top: 16px;
  color: #475569;
  font-size: 14px;
}

.pages {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
}

.page-card {
  padding: 20px;
}

.page-card h3 {
  margin: 0 0 8px;
}

.page-type {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: #eef2ff;
  color: #4338ca;
  font-size: 12px;
  margin-bottom: 12px;
}

.info-block {
  margin-top: 18px;
}

.info-block h4 {
  margin: 0 0 10px;
  font-size: 15px;
}

.empty {
  color: #6b7280;
}

.sketch-shell {
  border: 1px dashed #8fa6c8;
  border-radius: 12px;
  background: #fbfdff;
  padding: 12px;
}

.sketch-shell.drawer {
  margin-left: 48px;
}

.sketch-shell.modal {
  max-width: 260px;
  margin: 0 auto;
}

.sketch-shell.subpage {
  border-style: dotted;
}

.sketch-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 10px;
}

.sketch-block {
  padding: 10px 12px;
  border-radius: 10px;
  background: #e8eef9;
  border: 1px solid #c8d5eb;
  margin-top: 8px;
  text-align: center;
  font-size: 13px;
}

code,
pre {
  font-family: Consolas, "Courier New", monospace;
}

pre {
  padding: 12px;
  border-radius: 12px;
  background: #0f172a;
  color: #e2e8f0;
  overflow: auto;
}
""".strip()


def _escape(value: Any) -> str:
    return html.escape(str(value))


def _render_list(items: list[str]) -> str:
    if not items:
        return '<div class="empty">无直接项</div>'
    entries = "".join(f"<li>{_escape(item)}</li>" for item in items)
    return f"<ul>{entries}</ul>"


def _render_named_items(items: list[dict[str, Any]], formatter) -> str:
    if not items:
        return '<div class="empty">无直接项</div>'
    entries = "".join(f"<li>{formatter(item)}</li>" for item in items)
    return f"<ul>{entries}</ul>"


def _render_sketch_blocks(page: dict[str, Any]) -> str:
    view_type = str(page.get("view_type") or "页面")
    shell_class = "page"
    if view_type == "抽屉":
        shell_class = "drawer"
    elif view_type == "弹窗":
        shell_class = "modal"
    elif view_type == "子页面":
        shell_class = "subpage"

    blocks = page.get("sketch_blocks", [])
    rendered_blocks = "".join(
        f'<div class="sketch-block">{_escape(block.get("label") or "未命名区块")}</div>'
        for block in blocks
    )
    return (
        f'<div class="sketch-shell {shell_class}">'
        f'<div class="sketch-label">{_escape(view_type)}线框草图</div>'
        f"{rendered_blocks}"
        "</div>"
    )


def render_preview_html(model: dict[str, Any]) -> str:
    meta = model.get("meta", {})
    global_flow = model.get("global_flow", {})
    nodes = global_flow.get("nodes", [])
    flow_parts = []
    for index, node in enumerate(nodes):
        flow_parts.append(
            "<div class=\"flow-node\">"
            f"<small>{_escape(node.get('type') or '节点')}</small>"
            f"<strong>{_escape(node.get('name') or '未命名节点')}</strong>"
            f"<div>{_escape(node.get('goal') or '无直接项')}</div>"
            "</div>"
        )
        if index < len(nodes) - 1:
            flow_parts.append('<div class="flow-arrow">→</div>')

    page_cards = []
    for page in model.get("page_views", []):
        states_html = _render_named_items(
            page.get("states", []),
            lambda item: (
                f"<strong>{_escape(item.get('name') or '未命名状态')}</strong>"
                f" | 触发条件：{_escape(item.get('trigger') or '无直接项')}"
                f" | 页面反馈：{_escape(item.get('feedback') or '无直接项')}"
                f" | 下游结果：{_escape(item.get('outcome') or '无直接项')}"
            ),
        )
        copy_html = _render_named_items(
            page.get("copy_items", []),
            lambda item: (
                f"<strong>{_escape(item.get('id') or item.get('scene') or '文案项')}</strong>"
                f" | 场景：{_escape(item.get('scene') or '无直接项')}"
                f" | 语义目标：{_escape(item.get('goal') or '无直接项')}"
            ),
        )
        risk_items = [
            (
                f"<strong>{_escape(item.get('name') or '风险')}</strong>"
                f" | 困惑原因：{_escape(item.get('confusion_reason') or '无直接项')}"
                f" | 保护策略：{_escape(item.get('protection') or '无直接项')}"
            )
            for item in page.get("risks", [])
        ]
        risk_items.extend(_escape(item) for item in page.get("blockers", []))
        risk_html = '<div class="empty">无直接项</div>' if not risk_items else f"<ul>{''.join(f'<li>{item}</li>' for item in risk_items)}</ul>"

        principle_items = [str(item) for item in page.get("principles", [])]
        principle_items.extend(str(item) for item in page.get("trace_items", []))
        gap_items = [str(item) for item in page.get("open_items", [])]
        gap_items.extend(str(item) for item in page.get("gap_items", []))

        page_cards.append(
            "<article class=\"page-card\">"
            f"<div class=\"page-type\">{_escape(page.get('view_type') or '页面')}</div>"
            f"<h3>{_escape(page.get('view_name') or '未命名页面')}</h3>"
            f"<div>{_escape(page.get('view_id') or '')}</div>"
            "<div class=\"info-block\"><h4>页面摘要</h4>"
            f"{_render_list([str(page.get('summary') or '')] if page.get('summary') else [])}</div>"
            "<div class=\"info-block\"><h4>线框草图</h4>"
            f"{_render_sketch_blocks(page)}</div>"
            "<div class=\"info-block\"><h4>关键理解</h4>"
            f"{_render_list([str(item) for item in page.get('key_understanding', [])])}</div>"
            "<div class=\"info-block\"><h4>状态</h4>"
            f"{states_html}</div>"
            "<div class=\"info-block\"><h4>文案</h4>"
            f"{copy_html}</div>"
            "<div class=\"info-block\"><h4>风险与阻断</h4>"
            f"{risk_html}</div>"
            "<div class=\"info-block\"><h4>原则与追踪</h4>"
            f"{_render_list(principle_items)}</div>"
            "<div class=\"info-block\"><h4>开放问题 / 缺口</h4>"
            f"{_render_list(gap_items)}</div>"
            "</article>"
        )

    global_notes = model.get("global_notes", [])
    unresolved_items = model.get("unresolved_items", [])
    notes_payload = json.dumps(model, ensure_ascii=False, indent=2)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{_escape(meta.get("title") or "体验蓝图预览")}</title>
  <link rel="stylesheet" href="./assets/style.css" />
</head>
<body>
  <main class="page">
    <section class="hero">
      <h1>{_escape(meta.get("title") or "体验蓝图预览")}</h1>
      <p>该页面是正式体验蓝图的只读派生预览层，用于本地浏览器阅读，不回写正式蓝图、不新增业务语义。</p>
      <div class="meta">
        <span>项目：{_escape(model.get("project_id") or "")}</span>
        <span>来源：{_escape(meta.get("context", {}).get("source_blueprint") or "")}</span>
      </div>
    </section>

    <div class="layout">
      <section class="panel">
        <h2 class="section-title">全局流程总览</h2>
        <div class="flow-row">{''.join(flow_parts) if flow_parts else '<div class="empty">无直接项</div>'}</div>
        <div class="flow-legend">
          <span>实线关系：主成功路径</span>
          <span>虚线路径：阻断 / 回退可在风险与阻断区查看</span>
        </div>
      </section>

      <section class="panel">
        <h2 class="section-title">页面预览卡</h2>
        <div class="pages">{''.join(page_cards) if page_cards else '<div class="empty">无可渲染页面</div>'}</div>
      </section>

      <section class="panel">
        <h2 class="section-title">全局说明</h2>
        {_render_named_items(global_notes, lambda item: f"<strong>{_escape(item.get('type') or '说明')}</strong> | {_escape(item.get('content') or '无直接项')}")}
      </section>

      <section class="panel">
        <h2 class="section-title">待人工确认</h2>
        {_render_named_items(unresolved_items, lambda item: f"<strong>{_escape(item.get('type') or '未分类')}</strong> | {_escape(item.get('message') or '无直接项')}")}
      </section>

      <section class="panel">
        <h2 class="section-title">预览模型</h2>
        <pre>{_escape(notes_payload)}</pre>
      </section>
    </div>
  </main>
</body>
</html>
"""


def write_preview_site(output_dir: Path, model: dict[str, Any]) -> None:
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / "style.css").write_text(STYLE_CSS + "\n", encoding="utf-8")
    (output_dir / "index.html").write_text(render_preview_html(model), encoding="utf-8")
