"use strict";

const fs = require("fs");
const path = require("path");
const markdownRenderer = require("../../markdown_renderer");

const TEXT = {
  missing: "\u672a\u63d0\u4f9b",
  product: "\u95ee\u9898\u4e0e\u4e1a\u52a1\u65b9\u6848",
  previewTitle: "\u95ee\u9898\u4e0e\u4e1a\u52a1\u65b9\u6848\u9884\u89c8",
  projectUntitled: "\u672a\u547d\u540d\u9879\u76ee",
  leadRecommended: "\u63a8\u8350\u65b9\u5411",
  leadProblem: "\u6838\u5fc3\u95ee\u9898",
  leadRole: "\u76ee\u6807\u89d2\u8272",
  leadConstraint: "\u5173\u952e\u7ea6\u675f",
  summary: "\u8f93\u5165\u6458\u8981",
  definition: "\u95ee\u9898\u5b9a\u4e49",
  roles: "\u76ee\u6807\u7528\u6237\u4e0e\u573a\u666f",
  targetRole: "\u76ee\u6807\u89d2\u8272",
  targetScenario: "\u76ee\u6807\u573a\u666f",
  workarounds: "\u5f53\u524d\u66ff\u4ee3\u505a\u6cd5",
  opportunities: "\u673a\u4f1a\u70b9",
  directions: "\u5019\u9009\u65b9\u5411",
  recommendation: "\u63a8\u8350\u65b9\u5411",
  handoff: "\u627f\u63a5\u5951\u7ea6",
  constraints: "\u7ea6\u675f\u4e0e\u4e0d\u505a\u4ec0\u4e48",
  gaps: "\u5f85\u786e\u8ba4\u95ee\u9898",
  knowledge: "\u77e5\u8bc6\u951a\u5b9a"
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

function formatValue(value) {
  if (Array.isArray(value)) return value.map(formatValue).join("\uff1b");
  if (value && typeof value === "object") {
    return Object.entries(value).map(([key, item]) => `${key}: ${formatValue(item)}`).join("\uff1b");
  }
  return String(value ?? "").trim() || TEXT.missing;
}

function buildMarkdownFallback(markdown) {
  const sections = markdownRenderer.markdownToSections(markdown, {
    prefix: "problem-framing-markdown-section",
    fallbackTitle: TEXT.product
  });
  return {
    html: `<h1 class="preview-document-title">${TEXT.product}</h1>${markdownRenderer.renderSections(sections)}`,
    nav: sections.map((section) => ({ id: section.id, title: section.title, level: 1 })),
    projectName: TEXT.product
  };
}

function main() {
  const [shellArg, templateArg, markdownArg, outputArg] = process.argv.slice(2);
  if (!shellArg || !templateArg || !markdownArg || !outputArg) {
    fail("shell_path content_template_path markdown_path output_html_path are required");
  }

  const shellRaw = readFile(path.resolve(process.cwd(), shellArg), "shell template");
  const templateRaw = readFile(path.resolve(process.cwd(), templateArg), "content template");
  const markdown = readFile(path.resolve(process.cwd(), markdownArg), "markdown");

  const rendered = buildMarkdownFallback(markdown);
  const contentHtml = requiredReplace(templateRaw, "<!-- PROBLEM_FRAMING_CONTENT -->", rendered.html);
  const sidebarNav = rendered.nav.map((item) => `<a class="preview-nav-item level-${item.level}" href="#${item.id}" data-skill="problem-framing">${escapeHtml(item.title)}</a>`).join("\n");
  const bootstrapData = JSON.stringify({ activeSkill: "problem-framing", skills: ["problem-framing"] }, null, 2);

  let html = shellRaw;
  html = html.replace("<title>\u7edf\u4e00\u9884\u89c8</title>", `<title>${TEXT.previewTitle} - ${escapeHtml(formatValue(rendered.projectName || TEXT.projectUntitled))}</title>`);
  html = requiredReplace(html, "<!-- PREVIEW_SIDEBAR_NAV -->", sidebarNav);
  html = requiredReplace(html, "<!-- PREVIEW_CONTENT -->", contentHtml);
  html = requiredReplace(html, "<!-- PREVIEW_BOOTSTRAP_DATA -->", bootstrapData);
  html = html.replace("/* PREVIEW_ADDITIONAL_STYLES */", "");
  html = html.replace("<!-- PREVIEW_ADDITIONAL_SCRIPTS -->", "");

  for (const marker of ["PROJECT_NAME_HERE", "PREVIEW_SKILL_TABS", "<!-- PROBLEM_FRAMING_CONTENT -->", "FOOTER_SOURCE_PATH"]) {
    if (html.includes(marker)) fail(`generated html contains unresolved marker: ${marker}`);
  }

  const outputPath = path.resolve(process.cwd(), outputArg);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, html, "utf8");
  console.log(`problem-framing preview generated: ${outputPath}`);
}

main();
