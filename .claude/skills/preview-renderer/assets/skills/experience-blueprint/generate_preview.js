"use strict";

const fs = require("fs");
const path = require("path");

const TEXT = {
  product: "\u4f53\u9a8c\u84dd\u56fe",
  previewTitle: "\u4f53\u9a8c\u84dd\u56fe\u9884\u89c8",
  missing: "\u672a\u63d0\u4f9b"
};

function fail(message) {
  console.error(message);
  process.exit(1);
}

function readFile(filePath, label, required = true) {
  try {
    return fs.readFileSync(filePath, "utf8");
  } catch (error) {
    if (!required) return "";
    fail(`failed to read ${label}: ${filePath}\n${error.message}`);
  }
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function requiredReplace(source, marker, value) {
  if (!source.includes(marker)) fail(`required marker not found: ${marker}`);
  return source.replace(marker, value);
}

function hasMojibake(value) {
  return /[�锟]|(\?{4,})/.test(value);
}

function inlineMarkdown(value) {
  return escapeHtml(value)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
}

function decodeHtml(value) {
  return String(value ?? "")
    .replaceAll("&lt;", "<")
    .replaceAll("&gt;", ">")
    .replaceAll("&quot;", '"')
    .replaceAll("&#39;", "'")
    .replaceAll("&amp;", "&");
}

function plainTextFromHtml(value) {
  return decodeHtml(String(value ?? "").replace(/<[^>]+>/g, "")).trim();
}

function flowLabelFromPrevious(html) {
  const strong = String(html ?? "").match(/<strong>([\s\S]*?)<\/strong>/);
  const label = plainTextFromHtml(strong ? strong[1] : html);
  return label || "\u4e3b\u8def\u5f84";
}

function flowNodesFromCode(codeHtml) {
  const text = decodeHtml(codeHtml)
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .join(" ");
  if (!/[→]|->/.test(text)) return [];
  return text
    .split(/\s*(?:→|->)\s*/)
    .map((node) => node.trim())
    .filter(Boolean);
}

function renderFlowVisual(label, nodes) {
  if (nodes.length < 2) return "";
  const steps = nodes.map((node, index) => {
    const step = `<span class="summary-step">${inlineMarkdown(node)}</span>`;
    if (index === nodes.length - 1) return step;
    return `${step}<span class="summary-arrow">→</span>`;
  }).join("");
  return `
    <div class="summary-visual main-node-map">
      <div class="summary-row">
        <div class="summary-role">${escapeHtml(label)}</div>
        <div class="summary-path">${steps}</div>
      </div>
    </div>
  `;
}

function enhanceFlowOverview(sections) {
  for (const section of sections) {
    if (!section.title.includes("\u4ea4\u4e92\u6d41\u7a0b\u603b\u89c8")) continue;
    section.html = section.html.map((item, index, list) => {
      const match = item.match(/^<pre><code>([\s\S]*?)<\/code><\/pre>$/);
      if (!match) return item;
      const nodes = flowNodesFromCode(match[1]);
      if (nodes.length < 2) return item;
      const label = flowLabelFromPrevious(list[index - 1]);
      return renderFlowVisual(label, nodes);
    });
  }
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

function flushTable(table, out) {
  if (!table.rows.length) return;
  const rows = table.rows;
  const header = rows[0] || [];
  const body = rows.slice(1);
  out.push(`<div class="table-wrap"><table><thead><tr>${header.map((cell) => `<th>${inlineMarkdown(cell)}</th>`).join("")}</tr></thead><tbody>${body.map((row) => `<tr>${row.map((cell) => `<td>${inlineMarkdown(cell)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`);
  table.rows = [];
}

function isDividerRow(line) {
  return /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line);
}

function parseTableRow(line) {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
}

function slug(index) {
  return `experience-blueprint-section-${index}`;
}

function markdownToSections(markdown) {
  const lines = markdown.replace(/^\uFEFF/, "").split(/\r?\n/);
  const sections = [];
  let current = null;
  let paragraph = [];
  const list = { ordered: false, items: [] };
  const table = { rows: [] };
  let code = null;

  function ensureSection(title = TEXT.product) {
    if (!current) current = { id: slug(sections.length), title, html: [] };
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

    const h1 = line.match(/^#\s+(.+)$/);
    if (h1) continue;

    const h2 = line.match(/^##\s+(.+)$/);
    if (h2) {
      closeSection();
      current = { id: slug(sections.length), title: h2[1].trim(), html: [] };
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
  if (!sections.length) sections.push({ id: slug(0), title: TEXT.product, html: [`<p>${TEXT.missing}</p>`] });
  enhanceFlowOverview(sections);
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

function renderNav(sections) {
  return sections.map((section) => `<a class="preview-nav-item level-1" href="#${section.id}" data-skill="experience-blueprint">${escapeHtml(section.title)}</a>`).join("\n");
}

function parseArgs(args) {
  if (args.length === 5) {
    const [shellPathArg, templatePathArg, contextPathArg, markdownPathArg, outputPathArg] = args;
    return { shellPathArg, templatePathArg, contextPathArg, markdownPathArg, outputPathArg };
  }
  if (args.length === 0) {
    return {
      shellPathArg: ".claude/skills/preview-renderer/assets/shell/preview_shell.html",
      templatePathArg: ".claude/skills/preview-renderer/assets/skills/experience-blueprint/preview_template.html",
      contextPathArg: "spark-output/context/experience-blueprint.json",
      markdownPathArg: "spark-output/experience_blueprint.md",
      outputPathArg: "spark-output/preview/experience_blueprint_preview.html"
    };
  }
  fail("shell_path content_template_path context_json_path markdown_path output_html_path are required");
}

const ADDITIONAL_STYLES = `
    .summary-visual {
      margin: 12px 0 14px;
      padding: 16px;
      background: var(--panel-subtle);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      overflow-x: auto;
      box-shadow: none;
    }

    .summary-row {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      flex-wrap: nowrap;
      min-width: max-content;
    }

    .summary-role {
      min-width: 132px;
      max-width: 180px;
      color: var(--accent-strong);
      font-size: 13px;
      font-weight: 700;
      line-height: 32px;
      white-space: nowrap;
    }

    .summary-path {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: nowrap;
      min-width: max-content;
    }

    .summary-step {
      display: inline-flex;
      align-items: center;
      min-height: 32px;
      max-width: 260px;
      padding: 6px 11px;
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--text);
      font-size: 12px;
      line-height: 1.45;
      white-space: normal;
    }

    .summary-arrow {
      color: var(--text-soft);
      font-size: 13px;
      flex: 0 0 auto;
    }
`;

function main() {
  const args = parseArgs(process.argv.slice(2));
  const shellRaw = readFile(path.resolve(process.cwd(), args.shellPathArg), "shell template");
  let templateRaw = readFile(path.resolve(process.cwd(), args.templatePathArg), "content template");
  const markdown = readFile(path.resolve(process.cwd(), args.markdownPathArg), "markdown source");
  readFile(path.resolve(process.cwd(), args.contextPathArg), "context json", false);

  if (hasMojibake(markdown) || hasMojibake(shellRaw) || hasMojibake(templateRaw)) {
    fail("source contains obvious mojibake; stop preview generation");
  }

  const sections = markdownToSections(markdown);
  templateRaw = templateRaw.replace("<!-- CONTENT_NAV_ITEMS -->", "");
  templateRaw = templateRaw.replace("<!-- CONTENT_SECTIONS -->", renderSections(sections));
  templateRaw = templateRaw.replace("<!-- EXPERIENCE_SECTIONS -->", "");
  templateRaw = templateRaw.replace("FOOTER_SOURCE_PATH", escapeHtml(args.markdownPathArg));

  const bootstrapData = JSON.stringify({ activeSkill: "experience-blueprint", skills: ["experience-blueprint"] }, null, 2);
  let html = shellRaw;
  html = html.replace("<title>\u7edf\u4e00\u9884\u89c8</title>", `<title>${TEXT.previewTitle}</title>`);
  html = requiredReplace(html, "<!-- PREVIEW_SIDEBAR_NAV -->", renderNav(sections));
  html = requiredReplace(html, "<!-- PREVIEW_CONTENT -->", templateRaw);
  html = requiredReplace(html, "<!-- PREVIEW_BOOTSTRAP_DATA -->", bootstrapData);
  html = html.replace("/* PREVIEW_ADDITIONAL_STYLES */", ADDITIONAL_STYLES);
  html = html.replace("<!-- PREVIEW_ADDITIONAL_SCRIPTS -->", "");

  for (const marker of ["PROJECT_NAME_HERE", "PREVIEW_SKILL_TABS", "CONTENT_SECTIONS", "EXPERIENCE_SECTIONS", "FOOTER_SOURCE_PATH"]) {
    if (html.includes(marker)) fail(`generated html contains unresolved marker: ${marker}`);
  }

  const outputPath = path.resolve(process.cwd(), args.outputPathArg);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, html, "utf8");
  console.log(`experience-blueprint preview generated: ${outputPath}`);
}

main();
