from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any


STYLE_CSS = """
:root {
  --bg: #f2f0e8;
  --panel: #fffdf8;
  --panel-strong: #ffffff;
  --panel-subtle: #f6f3ec;
  --line: #d8d1c2;
  --line-strong: #c7bca7;
  --text: #1f2933;
  --text-muted: #6b7280;
  --text-soft: #8b8f97;
  --accent: #1f6b5b;
  --accent-soft: #e2f1eb;
  --accent-strong: #155245;
  --warn: #8a5a14;
  --warn-soft: #f6ead5;
  --danger: #8b3a3a;
  --danger-soft: #f8e4e1;
  --shadow: 0 10px 28px rgba(63, 49, 30, 0.08);
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
  background:
    radial-gradient(circle at top right, rgba(31, 107, 91, 0.08), transparent 24%),
    linear-gradient(180deg, #f7f4ed 0%, var(--bg) 100%);
  color: var(--text);
}

body,
button,
input,
textarea {
  font: inherit;
}

.page {
  width: min(1400px, calc(100% - 32px));
  margin: 0 auto;
  padding: 20px 0 40px;
}

.hero,
.panel,
.page-card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 18px;
  box-shadow: var(--shadow);
}

.layout {
  display: grid;
  gap: 16px;
}

.hero {
  padding: 16px 18px;
  margin-bottom: 16px;
}

.hero-top {
  margin-bottom: 8px;
}

.hero h1 {
  margin: 0;
  font-size: 24px;
  line-height: 1.2;
}

.hero p {
  margin: 0;
  font-size: 12px;
  line-height: 1.55;
  color: var(--text-muted);
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.meta span,
.hero-detail dt,
.hero-detail dd,
.legend-chip,
.tiny-chip,
.node-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: var(--panel-subtle);
  color: var(--text-muted);
  font-size: 11px;
  line-height: 1;
}

.hero-detail {
  margin-top: 10px;
  display: grid;
  gap: 6px;
}

.hero-detail-row {
  display: grid;
  grid-template-columns: 92px 1fr;
  gap: 8px;
  align-items: start;
  font-size: 12px;
  line-height: 1.55;
}

.hero-detail dt,
.hero-detail dd {
  margin: 0;
  min-height: unset;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  font-size: 12px;
  line-height: 1.55;
}

.hero-detail dt {
  color: var(--text-soft);
}

.hero-detail dd {
  color: var(--text);
}

.panel {
  padding: 16px;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.section-title {
  margin: 0;
  font-size: 18px;
  line-height: 1.3;
}

.section-desc {
  margin: 4px 0 0;
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-muted);
}

.lane-list {
  display: grid;
  gap: 12px;
}

.lane {
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.62);
}

.lane-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.lane h3 {
  margin: 0;
  font-size: 16px;
}

.lane-meta {
  font-size: 11px;
  color: var(--text-soft);
}

.chain-list {
  display: grid;
  gap: 10px;
}

.chain {
  padding: 12px;
  border: 1px solid rgba(31, 107, 91, 0.14);
  border-radius: 14px;
  background: linear-gradient(180deg, rgba(226, 241, 235, 0.88), rgba(255, 255, 255, 0.96));
}

.chain-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.chain-head h4 {
  margin: 0;
  font-size: 15px;
  line-height: 1.35;
}

.chain-goal {
  margin: 4px 0 0;
  font-size: 12px;
  line-height: 1.55;
  color: var(--text-muted);
}

.chain-badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.tiny-chip.primary {
  color: var(--accent-strong);
  background: var(--accent-soft);
  border-color: rgba(31, 107, 91, 0.16);
}

.tiny-chip.secondary {
  color: var(--warn);
  background: var(--warn-soft);
  border-color: rgba(138, 90, 20, 0.16);
}

.node-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: stretch;
  margin-top: 10px;
}

.flow-arrow {
  align-self: center;
  color: var(--text-soft);
  font-size: 16px;
}

.flow-node {
  flex: 1 1 156px;
  min-width: 156px;
  max-width: 220px;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(31, 107, 91, 0.16);
  background: var(--panel-strong);
}

.flow-node small {
  display: block;
  margin-bottom: 5px;
  font-size: 11px;
  line-height: 1.4;
  color: var(--text-soft);
}

.flow-node strong {
  display: block;
  font-size: 14px;
  line-height: 1.35;
}

.flow-node p {
  margin: 6px 0 0;
  font-size: 12px;
  line-height: 1.55;
  color: var(--text-muted);
}

.flow-node .node-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.flow-node .node-note {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed rgba(199, 188, 167, 0.8);
}

.flow-node.decision {
  border-color: rgba(138, 90, 20, 0.22);
  background: linear-gradient(180deg, #fff9ef 0%, #fffcf5 100%);
}

.flow-node.decision strong {
  color: #7b4f11;
}

.decision-branches {
  display: grid;
  gap: 6px;
  margin-top: 8px;
}

.decision-branches span {
  display: block;
  padding: 6px 8px;
  border-radius: 10px;
  font-size: 11px;
  line-height: 1.5;
}

.decision-pass {
  background: rgba(31, 107, 91, 0.08);
  color: var(--accent-strong);
}

.decision-stop {
  background: rgba(139, 58, 58, 0.08);
  color: var(--danger);
}

.flow-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.chain-judgment {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid rgba(216, 209, 194, 0.9);
}

.chain-judgment h5 {
  margin: 0 0 8px;
  font-size: 12px;
  line-height: 1.4;
  color: var(--text-soft);
}

.judgment-lines {
  display: grid;
  gap: 4px;
}

.judgment-lines span {
  display: block;
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-muted);
}

.legend-chip {
  color: var(--text-muted);
}

.confirm-list,
.page-list,
.detail-list,
.source-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.confirm-list {
  display: grid;
  gap: 8px;
}

.confirm-list li {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  line-height: 1.6;
}

.confirm-list strong {
  color: var(--accent-strong);
}

.pages {
  display: grid;
  gap: 14px;
}

.page-card {
  padding: 16px;
}

.page-card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.page-card-title {
  display: grid;
  gap: 8px;
}

.page-card h3 {
  margin: 0;
  font-size: 20px;
  line-height: 1.3;
}

.page-code {
  font-size: 11px;
  color: var(--text-soft);
}

.page-type {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  min-height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid rgba(31, 107, 91, 0.14);
  background: var(--accent-soft);
  color: var(--accent-strong);
  font-size: 11px;
  font-weight: 600;
}

.page-card-grid {
  display: grid;
  grid-template-columns: minmax(300px, 1.05fr) minmax(360px, 1.25fr);
  gap: 14px;
}

.page-main,
.page-side {
  display: grid;
  gap: 0;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.76);
}

.page-side {
  background: var(--panel-subtle);
}

.info-block {
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
}

.info-block + .info-block {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid rgba(216, 209, 194, 0.9);
}

.info-block h4 {
  margin: 0 0 8px;
  font-size: 13px;
  line-height: 1.4;
}

.info-block p {
  margin: 0;
  font-size: 13px;
  line-height: 1.65;
  color: var(--text-muted);
}

.meta-list {
  display: grid;
  gap: 8px;
  margin: 0;
}

.meta-row {
  display: grid;
  grid-template-columns: 64px 1fr;
  gap: 10px;
  font-size: 12px;
  line-height: 1.6;
}

.meta-row dt {
  margin: 0;
  color: var(--text-soft);
}

.meta-row dd {
  margin: 0;
  color: var(--text);
}

.detail-list {
  display: grid;
  gap: 8px;
}

.detail-list li {
  padding: 8px 10px;
  border-radius: 12px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.88);
}

.detail-list strong {
  display: block;
  margin-bottom: 4px;
  font-size: 13px;
  line-height: 1.45;
}

.detail-list span {
  display: block;
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-muted);
}

.bullet-list {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 6px;
}

.bullet-list li {
  font-size: 13px;
  line-height: 1.65;
  color: var(--text);
}

.empty-note {
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-soft);
}

.sketch-shell {
  border: 1px dashed var(--line-strong);
  border-radius: 14px;
  background: linear-gradient(180deg, #fffdf8 0%, #faf6ee 100%);
  padding: 12px;
}

.sketch-shell.drawer {
  margin-left: 36px;
}

.sketch-shell.modal {
  max-width: 280px;
}

.sketch-label {
  font-size: 11px;
  color: var(--text-soft);
  margin-bottom: 8px;
}

.sketch-grid {
  display: grid;
  gap: 8px;
}

.sketch-block {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid #d6ccb7;
  background: rgba(255, 255, 255, 0.86);
  font-size: 12px;
  color: var(--text-muted);
  text-align: center;
}

details {
  border: 1px solid var(--line);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.82);
}

details summary {
  cursor: pointer;
  padding: 10px 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
}

.source-list {
  display: grid;
  gap: 6px;
  padding: 0 12px 12px;
}

.source-list li {
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-muted);
}

code,
pre {
  font-family: Consolas, "Courier New", monospace;
}

pre {
  margin: 0;
  padding: 0 12px 12px;
  overflow: auto;
  background: transparent;
  color: var(--text);
  font-size: 12px;
  line-height: 1.55;
}

@media (max-width: 1024px) {
  .page-card-grid {
    grid-template-columns: 1fr;
  }

  .flow-node {
    max-width: none;
  }
}

@media (max-width: 720px) {
  .page {
    width: min(100% - 20px, 100%);
    padding: 12px 0 28px;
  }

  .hero,
  .panel,
  .page-card {
    border-radius: 16px;
  }

  .hero,
  .panel,
  .page-card {
    padding-left: 14px;
    padding-right: 14px;
  }

  .hero-top,
  .panel-header,
  .lane-head,
  .chain-head,
  .page-card-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .meta-row {
    grid-template-columns: 1fr;
    gap: 2px;
  }

  .sketch-shell.drawer {
    margin-left: 0;
  }
}
""".strip()

_IDENTIFIER_RE = re.compile(r"^(?P<code>[A-Za-z]{1,4}-\d{2})(?:\s+(?P<label>.+))?$")
_TRAILING_PUNCTUATION = "。．.、，,；;：:！!？?"


def _escape(value: Any) -> str:
    return html.escape(str(value))


def _normalize_text(value: Any) -> str:
    text = str(value or "").strip()
    return re.sub(r"\s+", " ", text)


def _canonical_text(value: Any) -> str:
    return _normalize_text(value).rstrip(_TRAILING_PUNCTUATION).lower()


def _dedupe_strings(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        cleaned = _normalize_text(item)
        if not cleaned:
            continue
        marker = _canonical_text(cleaned)
        if marker in seen:
            continue
        seen.add(marker)
        result.append(cleaned)
    return result


def _render_chips(items: list[str], chip_class: str = "node-chip") -> str:
    values = _dedupe_strings(items)
    if not values:
        return ""
    return "".join(f'<span class="{chip_class}">{_escape(item)}</span>' for item in values)


def _render_bullet_list(items: list[str]) -> str:
    values = _dedupe_strings(items)
    if not values:
        return ""
    entries = "".join(f"<li>{_escape(item)}</li>" for item in values)
    return f'<ul class="bullet-list">{entries}</ul>'


def _render_detail_list(items: list[str]) -> str:
    values = _dedupe_strings(items)
    if not values:
        return ""
    entries = "".join(
        f"<li><strong>{_escape(_split_title_and_body(item)[0])}</strong><span>{_escape(_split_title_and_body(item)[1])}</span></li>"
        for item in values
    )
    return f'<ul class="detail-list">{entries}</ul>'


def _render_named_items(items: list[dict[str, Any]], formatter) -> str:
    if not items:
        return ""
    entries = "".join(f"<li>{formatter(item)}</li>" for item in items)
    return f'<ul class="detail-list">{entries}</ul>'


def _render_meta_rows(rows: list[tuple[str, str]]) -> str:
    filtered_rows = [(label, value) for label, value in rows if _normalize_text(value)]
    if not filtered_rows:
        return ""
    entries = "".join(
        "<div class=\"meta-row\">"
        f"<dt>{_escape(label)}</dt>"
        f"<dd>{_escape(value)}</dd>"
        "</div>"
        for label, value in filtered_rows
    )
    return f'<dl class="meta-list">{entries}</dl>'


def _render_hero_rows(rows: list[tuple[str, str]]) -> str:
    filtered_rows = [(label, value) for label, value in rows if _normalize_text(value)]
    if not filtered_rows:
        return ""
    entries = "".join(
        "<div class=\"hero-detail-row\">"
        f"<dt>{_escape(label)}</dt>"
        f"<dd>{_escape(value)}</dd>"
        "</div>"
        for label, value in filtered_rows
    )
    return f'<dl class="hero-detail">{entries}</dl>'


def _render_section(title: str, body: str) -> str:
    if not body:
        return ""
    return f'<section class="info-block"><h4>{_escape(title)}</h4>{body}</section>'


def _render_source_details(items: list[str]) -> str:
    values = _dedupe_strings(items)
    if not values:
        return ""
    entries = "".join(f"<li>{_escape(item)}</li>" for item in values)
    return (
        "<details>"
        f"<summary>来源说明（{len(values)}）</summary>"
        f'<ul class="source-list">{entries}</ul>'
        "</details>"
    )


def _split_code_and_label(value: str) -> tuple[str, str]:
    text = _normalize_text(value)
    match = _IDENTIFIER_RE.match(text)
    if not match:
        return "", text
    return _normalize_text(match.group("code")), _normalize_text(match.group("label"))


def _split_title_and_body(value: str) -> tuple[str, str]:
    text = _normalize_text(value)
    if "：" in text:
        title, body = text.split("：", 1)
    elif ":" in text:
        title, body = text.split(":", 1)
    else:
        return text, ""
    return _normalize_text(title), _normalize_text(body)


def _clean_roles(items: list[str]) -> list[str]:
    return _dedupe_strings([_normalize_text(item).rstrip(_TRAILING_PUNCTUATION) for item in items])


def _path_label(chain: dict[str, Any]) -> str:
    if chain.get("is_primary"):
        return "主链路"
    if str(chain.get("path_type") or "").lower() == "secondary":
        return "辅助链路"
    return _normalize_text(chain.get("path_type") or "链路")


def _derive_node_title(node: dict[str, Any], page_names: dict[str, str] | None = None) -> tuple[str, str]:
    code, label = _split_code_and_label(str(node.get("name") or ""))
    if label:
        return code, label
    if code:
        return code, code
    return "", _normalize_text(node.get("name") or "未命名节点")


def _render_pairs(pairs: list[tuple[str, str]]) -> str:
    rows = [(label, _normalize_text(value)) for label, value in pairs if _normalize_text(value)]
    if not rows:
        return ""
    return "".join(f"<span>{_escape(label)}：{_escape(value)}</span>" for label, value in rows)


def _render_structured_list(items: list[dict[str, Any]], title_builder, field_builder) -> str:
    if not items:
        return ""
    entries: list[str] = []
    for item in items:
        title = _normalize_text(title_builder(item))
        fields = field_builder(item)
        field_html = _render_pairs(fields)
        if not title and not field_html:
            continue
        entries.append(
            "<li>"
            + (f"<strong>{_escape(title)}</strong>" if title else "")
            + field_html
            + "</li>"
        )
    if not entries:
        return ""
    return f'<ul class="detail-list">{"".join(entries)}</ul>'


def _render_sketch_blocks(page: dict[str, Any]) -> str:
    blocks = page.get("sketch_blocks", [])
    if not blocks:
        return ""

    view_type = _normalize_text(page.get("view_type") or "页面")
    shell_class = "page"
    if view_type == "抽屉":
        shell_class = "drawer"
    elif view_type == "弹窗":
        shell_class = "modal"
    elif view_type == "子页面":
        shell_class = "subpage"

    rendered_blocks = "".join(
        f'<div class="sketch-block">{_escape(_normalize_text(block.get("label") or "未命名区块"))}</div>'
        for block in blocks
    )
    return (
        f'<div class="sketch-shell {shell_class}">'
        f'<div class="sketch-label">{_escape(view_type)}线框草图</div>'
        f'<div class="sketch-grid">{rendered_blocks}</div>'
        "</div>"
    )


def _render_flow(model: dict[str, Any]) -> str:
    global_flow = model.get("global_flow", {})
    lanes = global_flow.get("lanes", [])
    chains = {chain.get("chain_id"): chain for chain in global_flow.get("chains", [])}

    if not lanes:
        return '<p class="empty-note">暂无流程可展示。</p>'

    lane_html: list[str] = []
    nodes = global_flow.get("nodes", [])
    for lane in lanes:
        chain_html: list[str] = []
        chain_ids = [_normalize_text(item) for item in lane.get("chain_ids", []) if _normalize_text(item)]
        for chain_id in chain_ids:
            chain = chains.get(chain_id, {})
            chain_nodes = [node for node in nodes if _normalize_text(node.get("chain_id")) == chain_id]
            node_parts: list[str] = []

            for index, node in enumerate(chain_nodes):
                code, title = _derive_node_title(node, {})
                node_meta: list[str] = []
                page_id = _normalize_text(node.get("page_id"))
                if code and code != title:
                    node_meta.append(code)
                if page_id:
                    node_meta.append(page_id)
                node_parts.append(
                    "<div class=\"flow-node\">"
                    f"<small>{_escape(_normalize_text(node.get('type') or '节点'))}</small>"
                    f"<strong>{_escape(title or '未命名节点')}</strong>"
                    + (f'<div class="node-meta">{_render_chips(node_meta)}</div>' if node_meta else "")
                    + "</div>"
                )
                if index < len(chain_nodes) - 1:
                    node_parts.append('<div class="flow-arrow">→</div>')

            node_row_html = "".join(node_parts) if node_parts else '<p class="empty-note">暂无链路节点。</p>'
            chain_judgment_html = _render_chain_judgment(chain)

            chain_html.append(
                "<section class=\"chain\">"
                "<div class=\"chain-head\">"
                "<div>"
                f"<h4>{_escape(_normalize_text(chain.get('name') or chain_id))}</h4>"
                f"<p class=\"chain-goal\">{_escape(_normalize_text(chain.get('goal') or ''))}</p>"
                "</div>"
                "<div class=\"chain-badges\">"
                f'<span class="tiny-chip {"primary" if chain.get("is_primary") else "secondary"}">{_escape(_path_label(chain))}</span>'
                f'<span class="tiny-chip">{_escape(chain_id)}</span>'
                "</div>"
                "</div>"
                f'<div class="node-row">{node_row_html}</div>'
                f"{chain_judgment_html}"
                "</section>"
            )

        lane_body_html = "".join(chain_html) if chain_html else '<p class="empty-note">暂无链路。</p>'
        lane_html.append(
            "<section class=\"lane\">"
            "<div class=\"lane-head\">"
            f"<h3>{_escape(_normalize_text(lane.get('role') or '未命名角色'))}</h3>"
            f"<span class=\"lane-meta\">{len(chain_html)} 条链路</span>"
            "</div>"
            f'<div class="chain-list">{lane_body_html}</div>'
            "</section>"
        )

    return f'<div class="lane-list">{"".join(lane_html)}</div>'


def _render_chain_judgment(chain: dict[str, Any]) -> str:
    lines = _render_pairs(
        [
            ("依赖 / 前提", chain.get("start")),
            ("判断 / 阻断", chain.get("judgment")),
            ("失败后去向 / 回退关系", chain.get("failure_result")),
        ]
    )
    if not lines:
        return ""
    return (
        '<div class="chain-judgment">'
        "<h5>判断说明</h5>"
        f'<div class="judgment-lines">{lines}</div>'
        "</div>"
    )


def _render_page_card(page: dict[str, Any]) -> str:
    page_id = _normalize_text(page.get("page_id"))
    view_name = _normalize_text(page.get("view_name") or "未命名页面")
    roles = " / ".join(_clean_roles([str(role) for role in page.get("roles", [])]))
    meta_rows = _render_meta_rows(
        [
            ("编号", page_id),
            ("角色", roles),
            ("入口", _normalize_text(page.get("entry"))),
            ("退出", _normalize_text(page.get("exit"))),
        ]
    )

    summary = _normalize_text(page.get("summary"))
    if summary == view_name:
        summary = ""

    key_understanding_blocks: list[str] = []
    understanding_html = _render_bullet_list([str(item) for item in page.get("key_understanding", [])])
    if understanding_html:
        key_understanding_blocks.append(understanding_html)

    action_html = _render_structured_list(
        page.get("action_items", []),
        lambda item: f"{_normalize_text(item.get('action_id'))} { _normalize_text(item.get('name')) }".strip(),
        lambda item: [
            ("触发条件", item.get("trigger")),
            ("即时反馈", item.get("feedback")),
            ("后续结果", item.get("outcome")),
            ("风险保护", item.get("protection")),
        ],
    )
    if action_html:
        key_understanding_blocks.append(action_html)

    info_contract_html = _render_structured_list(
        page.get("info_contract_items", []),
        lambda item: f"{_normalize_text(item.get('info_id'))} { _normalize_text(item.get('purpose')) }".strip(),
        lambda item: [
            ("优先级", item.get("priority")),
            ("推荐位置", item.get("position")),
            ("触发时机", item.get("trigger")),
            ("不展示风险", item.get("risk")),
        ],
    )
    if info_contract_html:
        key_understanding_blocks.append(info_contract_html)

    left_sections = "".join(
        [
            _render_section("线框草图", _render_sketch_blocks(page)),
            _render_section("页面信息", meta_rows),
            _render_section("页面摘要", f"<p>{_escape(summary)}</p>" if summary else ""),
            _render_section("关键理解", "".join(key_understanding_blocks)),
            _render_section("来源说明", _render_source_details([str(item) for item in page.get("source_refs", [])])),
        ]
    )

    states_html = _render_structured_list(
        page.get("states", []),
        lambda item: f"{_normalize_text(item.get('state_id'))} {_normalize_text(item.get('name'))}".strip(),
        lambda item: [
            ("触发条件", item.get("trigger")),
            ("可用动作", item.get("actions")),
            ("页面反馈", item.get("feedback")),
            ("文案反馈", item.get("copy_feedback")),
            ("下游结果", item.get("outcome")),
        ],
    )

    copy_html = _render_structured_list(
        page.get("copy_items", []),
        lambda item: f"{_normalize_text(item.get('copy_id'))} {_normalize_text(item.get('scene'))}".strip(),
        lambda item: [
            ("文案类型", item.get("copy_type")),
            ("语义目标", item.get("goal")),
            ("必含信息", item.get("required")),
            ("禁止写法", item.get("avoid")),
            ("示例方向", item.get("example")),
        ],
    )

    risk_html = _render_structured_list(
        page.get("risks", []),
        lambda item: f"{_normalize_text(item.get('risk_id'))} {_normalize_text(item.get('name'))}".strip(),
        lambda item: [
            ("触发场景", item.get("trigger")),
            ("困惑原因", item.get("confusion_reason")),
            ("保护策略", item.get("protection")),
        ],
    )

    blocker_html = _render_structured_list(
        page.get("blockers", []),
        lambda item: f"{_normalize_text(item.get('id'))} {_normalize_text(item.get('name'))}".strip(),
        lambda item: [
            ("触发条件", item.get("trigger")),
            ("影响", item.get("impact")),
        ],
    )

    principle_html = _render_structured_list(
        page.get("principles", []),
        lambda item: f"{_normalize_text(item.get('principle_id'))} {_normalize_text(item.get('name'))}".strip(),
        lambda item: [("命中原因", item.get("reason"))],
    )

    mode_trace_html = _render_structured_list(
        [{"mode": page.get("view_type")}] + list(page.get("trace_items", [])),
        lambda item: _normalize_text(item.get("mode")) if item.get("mode") else f"{_normalize_text(item.get('trace_id'))} {_normalize_text(item.get('object'))}".strip(),
        lambda item: [("承载模式", item.get("mode"))] if item.get("mode") else [
            ("承接业务判断", item.get("business_judgment")),
            ("承接事实 / 规则 / 异常", item.get("facts")),
            ("承接原则", item.get("principles")),
            ("说明", item.get("note")),
        ],
    )

    pending_items = _dedupe_strings(
        [str(item) for item in page.get("open_items", [])] + [str(item) for item in page.get("gap_items", [])]
    )

    right_sections = "".join(
        [
            _render_section("状态与反馈", states_html),
            _render_section("文案", copy_html),
            _render_section("风险与阻断", "".join([risk_html, blocker_html])),
            _render_section("原则", principle_html),
            _render_section("模式与追踪", mode_trace_html),
            _render_section("待确认项", _render_bullet_list(pending_items)),
        ]
    )

    return (
        "<article class=\"page-card\">"
        "<div class=\"page-card-head\">"
        "<div class=\"page-card-title\">"
        f"<span class=\"page-type\">{_escape(_normalize_text(page.get('view_type') or '页面'))}</span>"
        f"<h3>{_escape(view_name)}</h3>"
        "</div>"
        + (f'<span class="page-code">{_escape(page_id)}</span>' if page_id else "")
        + "</div>"
        "<div class=\"page-card-grid\">"
        f'<div class="page-main">{left_sections}</div>'
        f'<div class="page-side">{right_sections}</div>'
        "</div>"
        "</article>"
    )


def render_preview_html(model: dict[str, Any]) -> str:
    meta = model.get("meta", {})
    global_context = model.get("global_context", {})
    overview = meta.get("overview", {})
    global_principles_html = _render_bullet_list(
        [_normalize_text(item.get("label") or item.get("principle_id")) for item in global_context.get("principles", [])]
    )
    global_notes_html = _render_structured_list(
        global_context.get("notes", []),
        lambda item: _normalize_text(item.get("type")),
        lambda item: [
            ("内容", item.get("content")),
            ("推荐位置", item.get("position")),
        ],
    )

    pending_global_items = []
    for item in global_context.get("open_questions", []):
        pending_global_items.append(
            f"{_normalize_text(item.get('id') or 'OQ')}：{_normalize_text(item.get('content') or item.get('label') or '无直接项')}"
        )
    for item in global_context.get("gaps", []):
        pending_global_items.append(
            f"{_normalize_text(item.get('id') or 'GAP')}：{_normalize_text(item.get('content') or item.get('label') or '无直接项')}"
        )
    for item in model.get("unresolved_items", []):
        pending_global_items.append(
            f"{_normalize_text(item.get('type') or '待确认')}：{_normalize_text(item.get('message') or '无直接项')}"
        )

    flow_html = _render_flow(model)
    page_cards = "".join(_render_page_card(page) for page in model.get("page_views", []))
    debug_payload = html.escape(json_dumps(model))
    global_reference_body = "".join(
        [
            _render_section("原则引用", global_principles_html),
            _render_section("信息优先级", global_notes_html),
        ]
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{_escape(_normalize_text(meta.get("title") or "体验蓝图预览"))}</title>
  <link rel="stylesheet" href="./assets/style.css" />
</head>
<body>
  <main class="page">
    <section class="hero">
      <div class="hero-top">
        <h1>{_escape(_normalize_text(meta.get("title") or "体验蓝图预览"))}</h1>
      </div>
      {_render_hero_rows([
          ("只读说明", "该页面仅用于本地阅读正式体验蓝图的派生预览，不回写正式蓝图，也不新增业务语义。"),
          ("项目", _normalize_text(model.get("project_id") or "")),
          ("来源", _normalize_text(meta.get("context", {}).get("source_blueprint") or "")),
          ("目标用户与角色", _normalize_text(overview.get("目标用户与角色") or "").replace("目标用户与角色：", "", 1)),
          ("体验目标", _normalize_text(overview.get("体验目标") or "").replace("体验目标：", "", 1)),
          ("任务边界", _normalize_text(overview.get("任务边界") or "").replace("任务边界：", "", 1)),
      ])}
    </section>

    <div class="layout">
      <section class="panel">
        <div class="panel-header">
          <div>
            <h2 class="section-title">全局流程总览</h2>
          </div>
        </div>
        {flow_html}
        <div class="flow-legend">
          <span class="legend-chip">按角色分泳道</span>
          <span class="legend-chip">按链路分组</span>
        </div>
      </section>

      {_render_section_panel("全局待确认", _render_global_confirm_list(pending_global_items))}

      {_render_section_panel("全局原文补充", global_reference_body)}

      <section class="panel">
        <div class="panel-header">
          <div>
            <h2 class="section-title">页面预览卡</h2>
          </div>
        </div>
        <div class="pages">{page_cards or '<p class="empty-note">无可渲染页面。</p>'}</div>
      </section>

      <section class="panel">
        <div class="panel-header">
          <div>
            <h2 class="section-title">调试信息</h2>
          </div>
        </div>
        <details>
          <summary>展开 preview_model.json</summary>
          <pre>{debug_payload}</pre>
        </details>
      </section>
    </div>
  </main>
</body>
</html>
"""


def _render_global_confirm_list(items: list[str]) -> str:
    values = _dedupe_strings(items)
    if not values:
        return ""
    entries = "".join(
        f"<li><strong>{_escape(_split_title_and_body(item)[0])}</strong> {_escape(_split_title_and_body(item)[1])}</li>"
        for item in values
    )
    return f'<ul class="confirm-list">{entries}</ul>'


def _render_section_panel(title: str, body: str, desc: str = "") -> str:
    if not body:
        return ""
    desc_html = f"<p class=\"section-desc\">{_escape(desc)}</p>" if _normalize_text(desc) else ""
    return (
        "<section class=\"panel\">"
        "<div class=\"panel-header\">"
        "<div>"
        f"<h2 class=\"section-title\">{_escape(title)}</h2>"
        f"{desc_html}"
        "</div>"
        "</div>"
        f"{body}"
        "</section>"
    )


def json_dumps(payload: dict[str, Any]) -> str:
    import json

    return json.dumps(payload, ensure_ascii=False, indent=2)


def write_preview_site(output_dir: Path, model: dict[str, Any]) -> None:
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / "style.css").write_text(STYLE_CSS + "\n", encoding="utf-8")
    (output_dir / "index.html").write_text(render_preview_html(model), encoding="utf-8")
