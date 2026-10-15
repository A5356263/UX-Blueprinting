"use strict";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function inlineMarkdown(value) {
  return escapeHtml(value)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
}

function flushParagraph(lines, out) {
  if (!lines.length) return;
  out.push(`<p>${inlineMarkdown(lines.join(" "))}</p>`);
  lines.length = 0;
}

function flushList(list, out) {
  if (!list.items.length) return;
  const tag = list.ordered ? "ol" : "ul";
  out.push(`<${tag}>${list.items.map((item) => `<li>${inlineMarkdown(item)}</li>`).join("")}</${tag}>`);
  list.items = [];
  list.ordered = false;
}

function isDividerRow(line) {
  return /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line);
}

function parseTableRow(line) {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
}

function flushTable(table, out) {
  if (!table.rows.length) return;
  const rows = table.rows;
  const header = rows[0] || [];
  const body = rows.slice(1);
  out.push(`<div class="table-wrap"><table><thead><tr>${header.map((cell) => `<th>${inlineMarkdown(cell)}</th>`).join("")}</tr></thead><tbody>${body.map((row) => `<tr>${row.map((cell) => `<td>${inlineMarkdown(cell)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`);
  table.rows = [];
}

function markdownToSections(markdown, options = {}) {
  const prefix = options.prefix || "markdown-section";
  const fallbackTitle = options.fallbackTitle || "预览";
  const lines = String(markdown ?? "").replace(/^\uFEFF/, "").split(/\r?\n/);
  const sections = [];
  let current = null;
  let paragraph = [];
  const list = { ordered: false, items: [] };
  const table = { rows: [] };
  let code = null;

  function ensureSection(title = fallbackTitle) {
    if (!current) current = { id: `${prefix}-${sections.length}`, title, html: [] };
    return current;
  }

  function flushAll() {
    const html = ensureSection().html;
    flushParagraph(paragraph, html);
    flushList(list, html);
    flushTable(table, html);
  }

  function closeSection() {
    if (!current) return;
    flushAll();
    sections.push(current);
    current = null;
  }

  for (const rawLine of lines) {
    const line = rawLine.replace(/\s+$/, "");

    if (code) {
      if (/^```/.test(line)) {
        ensureSection().html.push(`<pre><code>${escapeHtml(code.lines.join("\n"))}</code></pre>`);
        code = null;
      } else {
        code.lines.push(rawLine);
      }
      continue;
    }

    if (/^```/.test(line)) {
      flushAll();
      code = { lines: [] };
      continue;
    }

    if (/^#\s+/.test(line)) continue;

    const h2 = line.match(/^##\s+(.+)$/);
    if (h2) {
      closeSection();
      current = { id: `${prefix}-${sections.length}`, title: h2[1].trim(), html: [] };
      continue;
    }

    const h3 = line.match(/^(#{3,6})\s+(.+)$/);
    if (h3) {
      flushAll();
      const level = Math.min(h3[1].length, 6);
      ensureSection().html.push(`<h${level}>${inlineMarkdown(h3[2].trim())}</h${level}>`);
      continue;
    }

    if (!line.trim()) {
      flushAll();
      continue;
    }

    if (line.includes("|") && /^\s*\|?[^|]+\|/.test(line)) {
      flushParagraph(paragraph, ensureSection().html);
      flushList(list, ensureSection().html);
      if (!isDividerRow(line)) table.rows.push(parseTableRow(line));
      continue;
    }

    const ordered = line.match(/^\s*\d+[.)]\s+(.+)$/);
    const unordered = line.match(/^\s*[-*]\s+(.+)$/);
    if (ordered || unordered) {
      flushParagraph(paragraph, ensureSection().html);
      flushTable(table, ensureSection().html);
      const isOrdered = Boolean(ordered);
      if (list.items.length && list.ordered !== isOrdered) flushList(list, ensureSection().html);
      list.ordered = isOrdered;
      list.items.push((ordered || unordered)[1].trim());
      continue;
    }

    flushList(list, ensureSection().html);
    flushTable(table, ensureSection().html);
    paragraph.push(line.trim());
  }

  if (code) ensureSection().html.push(`<pre><code>${escapeHtml(code.lines.join("\n"))}</code></pre>`);
  closeSection();
  if (!sections.length) sections.push({ id: `${prefix}-0`, title: fallbackTitle, html: ["<p>未提供</p>"] });
  return sections;
}

function renderSections(sections) {
  return sections.map((section) => `
    <section class="preview-section-block" id="${section.id}">
      <h2 class="preview-section-heading">${inlineMarkdown(section.title)}</h2>
      <div class="preview-section-body">${section.html.join("\n")}</div>
    </section>
  `).join("\n");
}

function renderNav(sections, skillId) {
  return sections.map((section) => `<a class="preview-nav-item level-1" href="#${section.id}" data-skill="${escapeHtml(skillId)}">${escapeHtml(section.title)}</a>`).join("\n");
}

module.exports = {
  markdownToSections,
  renderSections,
  renderNav
};
