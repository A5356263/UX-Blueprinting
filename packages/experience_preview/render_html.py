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

.panel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

.mini-panel {
  border: 1px solid #d9e2f0;
  border-radius: 14px;
  padding: 16px;
  background: #fafcff;
}

.mini-panel h3 {
  margin: 0 0 10px;
  font-size: 16px;
}

.section-title {
  margin: 0 0 16px;
  font-size: 20px;
}

.lane-list {
  display: grid;
  gap: 16px;
}

.lane {
  border: 1px solid #d9e2f0;
  border-radius: 16px;
  padding: 16px;
  background: #fafcff;
}

.lane h3 {
  margin: 0 0 12px;
  font-size: 18px;
}

.chain-list {
  display: grid;
  gap: 12px;
}

.chain {
  border: 1px solid #cfe0fb;
  border-radius: 14px;
  padding: 14px;
  background: #eef4ff;
}

.chain-head {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  align-items: center;
  margin-bottom: 10px;
}

.chip {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  background: #e2e8f0;
  color: #334155;
}

.chip.primary {
  background: #dbeafe;
  color: #1d4ed8;
}

.chip.secondary {
  background: #ede9fe;
  color: #6d28d9;
}

.node-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.flow-node {
  min-width: 180px;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid #bdd2f4;
  background: #ffffff;
}

.flow-node small {
  display: block;
  color: #4b5563;
  margin-bottom: 6px;
}

.flow-arrow {
  color: #64748b;
  font-size: 20px;
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

.page-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  color: #64748b;
  font-size: 13px;
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

.inline-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
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

details {
  border: 1px solid #d9e2f0;
  border-radius: 12px;
  padding: 12px 14px;
  background: #fbfdff;
}

summary {
  cursor: pointer;
  font-weight: 600;
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


def _render_chips(items: list[str]) -> str:
    if not items:
        return '<div class="empty">无直接项</div>'
    return f"<div class=\"inline-list\">{''.join(f'<span class=\"chip\">{_escape(item)}</span>' for item in items)}</div>"


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


def _dedupe_strings(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        cleaned = str(item).strip()
        if not cleaned:
            continue
        marker = cleaned.lower()
        if marker in seen:
            continue
        seen.add(marker)
        result.append(cleaned)
    return result


def _render_flow(model: dict[str, Any]) -> str:
    global_flow = model.get("global_flow", {})
    lanes = global_flow.get("lanes", [])
    chains = {chain.get("chain_id"): chain for chain in global_flow.get("chains", [])}
    nodes = global_flow.get("nodes", [])
    if not lanes:
        return '<div class="empty">无直接项</div>'

    lane_html = []
    for lane in lanes:
        chain_html = []
        for chain_id in lane.get("chain_ids", []):
            chain = chains.get(chain_id, {})
            chain_nodes = [node for node in nodes if node.get("chain_id") == chain_id]
            node_parts = []
            for index, node in enumerate(chain_nodes):
                node_parts.append(
                    "<div class=\"flow-node\">"
                    f"<small>{_escape(node.get('type') or '节点')}</small>"
                    f"<strong>{_escape(node.get('name') or '未命名节点')}</strong>"
                    f"<div>{_escape(node.get('page_id') or node.get('goal') or '')}</div>"
                    "</div>"
                )
                if index < len(chain_nodes) - 1:
                    node_parts.append('<div class="flow-arrow">→</div>')
            chain_html.append(
                "<div class=\"chain\">"
                "<div class=\"chain-head\">"
                f"<strong>{_escape(chain.get('name') or chain_id)}</strong>"
                f"<span class=\"chip {'primary' if chain.get('is_primary') else 'secondary'}\">{_escape(chain.get('path_type') or 'chain')}</span>"
                f"<span class=\"chip\">{_escape(chain_id)}</span>"
                "</div>"
                f"<div>{_escape(chain.get('goal') or '')}</div>"
                f"<div class=\"node-row\">{''.join(node_parts) if node_parts else '<div class=\"empty\">无节点</div>'}</div>"
                "</div>"
            )
        lane_html.append(
            "<section class=\"lane\">"
            f"<h3>{_escape(lane.get('role') or '未命名角色')}</h3>"
            f"<div class=\"chain-list\">{''.join(chain_html) if chain_html else '<div class=\"empty\">无链路</div>'}</div>"
            "</section>"
        )
    return f"<div class=\"lane-list\">{''.join(lane_html)}</div>"


def _render_dependency_list(items: list[dict[str, Any]]) -> str:
    return _render_named_items(
        items,
        lambda item: (
            f"<strong>{_escape(item.get('from_chain_id') or '')}</strong>"
            f" 依赖 <strong>{_escape(item.get('to_chain_id') or '')}</strong>"
            f" | {_escape(item.get('reason') or '')}"
        ),
    )


def _render_blocker_list(items: list[dict[str, Any]]) -> str:
    return _render_named_items(
        items,
        lambda item: (
            f"<strong>{_escape(item.get('name') or item.get('id') or '阻断')}</strong>"
            f" | 触发：{_escape(item.get('trigger') or '无直接项')}"
            f" | 影响：{_escape(item.get('impact') or '无直接项')}"
        ),
    )


def render_preview_html(model: dict[str, Any]) -> str:
    meta = model.get("meta", {})
    global_flow = model.get("global_flow", {})
    global_context = model.get("global_context", {})

    def render_global_list(field: str, title_key: str, fallback_key: str = "content") -> str:
        items = global_context.get(field, [])
        return _render_named_items(
            items,
            lambda item: (
                f"<strong>{_escape(item.get(title_key) or item.get('id') or item.get('type') or '项')}</strong>"
                f" | {_escape(item.get(fallback_key) or item.get('label') or item.get('reason') or item.get('position') or '无直接项')}"
            ),
        )

    page_cards = []
    for page in model.get("page_views", []):
        page_id = str(page.get("page_id") or "")
        view_name = str(page.get("view_name") or "未命名页面")
        show_page_id = bool(page_id and page_id != view_name)

        summary_items = []
        summary = str(page.get("summary") or "").strip()
        if summary and summary != view_name:
            summary_items.append(summary)

        state_items = page.get("states", [])
        states_html = _render_named_items(
            state_items,
            lambda item: (
                f"<strong>{_escape(item.get('name') or item.get('state_id') or '未命名状态')}</strong>"
                f" | 触发：{_escape(item.get('trigger') or '无直接项')}"
                f" | 反馈：{_escape(item.get('feedback') or item.get('copy_feedback') or '无直接项')}"
                f" | 结果：{_escape(item.get('outcome') or '无直接项')}"
            ),
        )

        copy_html = _render_named_items(
            page.get("copy_items", []),
            lambda item: (
                f"<strong>{_escape(item.get('copy_id') or '文案项')}</strong>"
                f" | 场景：{_escape(item.get('scene') or '无直接项')}"
                f" | 语义目标：{_escape(item.get('goal') or '无直接项')}"
                f" | 示例：{_escape(item.get('example') or '无直接项')}"
            ),
        )

        risk_html = _render_named_items(
            page.get("risks", []),
            lambda item: (
                f"<strong>{_escape(item.get('name') or item.get('risk_id') or '风险')}</strong>"
                f" | 困惑原因：{_escape(item.get('confusion_reason') or '无直接项')}"
                f" | 保护策略：{_escape(item.get('protection') or '无直接项')}"
            ),
        )
        blocker_html = _render_blocker_list(page.get("blockers", []))

        principle_items = [
            f"{item.get('principle_id', '')} {item.get('name', '')} {item.get('reason', '')}".strip()
            for item in page.get("principles", [])
        ]
        pattern_items = [str(item) for item in page.get("design_patterns", [])]
        trace_items = [
            f"{item.get('trace_id', '')} {item.get('note', '')}".strip()
            for item in page.get("trace_items", [])
        ]

        open_gap_items = _dedupe_strings(
            [str(item) for item in page.get("open_items", [])] + [str(item) for item in page.get("gap_items", [])]
        )

        page_meta_items = _dedupe_strings(
            [str(role) for role in page.get("roles", [])]
            + ([f"入口：{page.get('entry')}" ] if page.get("entry") else [])
            + ([f"退出：{page.get('exit')}" ] if page.get("exit") else [])
        )

        page_cards.append(
            "<article class=\"page-card\">"
            f"<div class=\"page-type\">{_escape(page.get('view_type') or '页面')}</div>"
            f"<h3>{_escape(view_name)}</h3>"
            + (f"<div class=\"page-meta\"><span>{_escape(page_id)}</span></div>" if show_page_id else "")
            + f"<div class=\"page-meta\">{''.join(f'<span>{_escape(item)}</span>' for item in page_meta_items)}</div>"
            + "<div class=\"info-block\"><h4>页面摘要</h4>"
            + f"{_render_list(summary_items)}</div>"
            + "<div class=\"info-block\"><h4>线框草图</h4>"
            + f"{_render_sketch_blocks(page)}</div>"
            + "<div class=\"info-block\"><h4>关键理解</h4>"
            + f"{_render_list([str(item) for item in page.get('key_understanding', [])])}</div>"
            + "<div class=\"info-block\"><h4>状态</h4>"
            + f"{states_html}</div>"
            + "<div class=\"info-block\"><h4>文案</h4>"
            + f"{copy_html}</div>"
            + "<div class=\"info-block\"><h4>风险与阻断</h4>"
            + f"{risk_html}{blocker_html if page.get('blockers') else ''}</div>"
            + "<div class=\"info-block\"><h4>原则、设计模式与追踪</h4>"
            + f"{_render_list(_dedupe_strings(principle_items + pattern_items + trace_items))}</div>"
            + "<div class=\"info-block\"><h4>开放问题 / 缺口</h4>"
            + f"{_render_list(open_gap_items)}</div>"
            + "<div class=\"info-block\"><details><summary>来源说明</summary>"
            + f"{_render_list([str(item) for item in page.get('source_refs', [])])}</details></div>"
            + "</article>"
        )

    notes_payload = json.dumps(model, ensure_ascii=False, indent=2)

    dependencies_html = _render_dependency_list(global_flow.get("dependencies", []))
    blockers_html = _render_blocker_list(global_flow.get("blockers", []))

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
        <span>版本：{_escape(meta.get("version") or "v2")}</span>
        <span>来源：{_escape(meta.get("context", {}).get("source_blueprint") or "")}</span>
      </div>
    </section>

    <div class="layout">
      <section class="panel">
        <h2 class="section-title">全局流程总览</h2>
        {_render_flow(model)}
        <div class="flow-legend">
          <span>按角色分泳道</span>
          <span>按链路分组</span>
          <span>阻断与依赖单独列示</span>
        </div>
      </section>

      <section class="panel">
        <h2 class="section-title">全局依赖 / 前提</h2>
        {dependencies_html}
      </section>

      <section class="panel">
        <h2 class="section-title">全局区块</h2>
        <div class="panel-grid">
          <section class="mini-panel">
            <h3>全局原则</h3>
            {render_global_list("principles", "principle_id")}
          </section>
          <section class="mini-panel">
            <h3>全局风险</h3>
            {render_global_list("risks", "risk_id", "protection")}
          </section>
          <section class="mini-panel">
            <h3>全局开放问题</h3>
            {render_global_list("open_questions", "id")}
          </section>
          <section class="mini-panel">
            <h3>全局缺口</h3>
            {render_global_list("gaps", "id")}
          </section>
        </div>
      </section>

      <section class="panel">
        <h2 class="section-title">流程级阻断</h2>
        {blockers_html}
      </section>

      <section class="panel">
        <h2 class="section-title">页面预览卡</h2>
        <div class="pages">{''.join(page_cards) if page_cards else '<div class="empty">无可渲染页面</div>'}</div>
      </section>

      <section class="panel">
        <h2 class="section-title">待人工确认</h2>
        {_render_named_items(model.get("unresolved_items", []), lambda item: f"<strong>{_escape(item.get('type') or '未分类')}</strong> | {_escape(item.get('message') or '无直接项')}")}
      </section>

      <section class="panel">
        <h2 class="section-title">调试信息</h2>
        <details>
          <summary>展开 preview_model.json</summary>
          <pre>{_escape(notes_payload)}</pre>
        </details>
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
