"use strict";

const fs = require("fs");
const path = require("path");
const markdownRenderer = require("../../markdown_renderer");

const TEXT = {
  missing: "\u672a\u63d0\u4f9b",
  product: "\u7528\u6237\u6545\u4e8b",
  previewTitle: "\u7528\u6237\u6545\u4e8b\u9884\u89c8",
  untitledProject: "\u672a\u547d\u540d\u9879\u76ee",
  untitledStory: "\u672a\u547d\u540d\u6545\u4e8b",
  overview: "\u6545\u4e8b\u6982\u89c8",
  source: "\u6765\u6e90",
  storyCount: "\u6545\u4e8b\u6570\u91cf",
  p0: "P0 \u4e3b\u94fe",
  assumption: "\u5173\u952e\u5047\u8bbe",
  role: "\u89d2\u8272",
  goal: "\u76ee\u6807",
  scenario: "\u573a\u666f",
  userTask: "\u7528\u6237\u8981\u5b8c\u6210\u4ec0\u4e48",
  acceptance: "\u5b8c\u6210\u6807\u51c6",
  touchpoints: "\u8bbe\u8ba1\u89e6\u70b9",
  sourceRisk: "\u6765\u6e90\u4e0e\u98ce\u9669",
  sourceBasis: "\u6765\u6e90\u4f9d\u636e",
  risk: "\u98ce\u9669",
  mainAndAssumption: "\u4e3b\u94fe\u4e0e\u5047\u8bbe",
  p0List: "P0 \u4e3b\u94fe\u6e05\u5355",
  auxiliaryList: "\u8f85\u52a9\u80fd\u529b\u6e05\u5355",
  assumptionList: "\u5047\u8bbe\u9879\u6e05\u5355",
  employee: "\u5458\u5de5",
  approver: "\u5ba1\u6279\u4eba",
  admin: "\u7ba1\u7406\u5458",
  system: "\u7cfb\u7edf",
  priorityMissing: "\u672a\u6807\u4f18\u5148\u7ea7",
  summaryMissing: "\u672a\u63d0\u4f9b\u65b9\u5411\u6458\u8981"
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

function buildMarkdownFallback(markdown) {
  const sections = markdownRenderer.markdownToSections(markdown, {
    prefix: "stories-markdown-section",
    fallbackTitle: TEXT.product
  });
  return {
    html: `<h1 class="preview-document-title">${TEXT.product}</h1>${markdownRenderer.renderSections(sections)}`,
    nav: sections.map((section) => ({ id: section.id, title: section.title, level: 1 }))
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
  const contentHtml = requiredReplace(templateRaw, "<!-- STORIES_CONTENT -->", rendered.html);
  const sidebarNav = rendered.nav.map((item) => `<a class="preview-nav-item level-${item.level}" href="#${item.id}" data-skill="stories">${escapeHtml(item.title)}</a>`).join("\n");
  const bootstrapData = JSON.stringify({ activeSkill: "stories", skills: ["stories"] }, null, 2);

  let html = shellRaw;
  html = html.replace("<title>\u7edf\u4e00\u9884\u89c8</title>", `<title>${TEXT.previewTitle} - ${escapeHtml(TEXT.untitledProject)}</title>`);
  html = requiredReplace(html, "<!-- PREVIEW_SIDEBAR_NAV -->", sidebarNav);
  html = requiredReplace(html, "<!-- PREVIEW_CONTENT -->", contentHtml);
  html = requiredReplace(html, "<!-- PREVIEW_BOOTSTRAP_DATA -->", bootstrapData);
  html = html.replace("/* PREVIEW_ADDITIONAL_STYLES */", "");
  html = html.replace("<!-- PREVIEW_ADDITIONAL_SCRIPTS -->", "");

  for (const marker of ["PROJECT_NAME_HERE", "PREVIEW_SKILL_TABS", "<!-- STORIES_CONTENT -->", "FOOTER_SOURCE_PATH"]) {
    if (html.includes(marker)) fail(`generated html contains unresolved marker: ${marker}`);
  }

  const outputPath = path.resolve(process.cwd(), outputArg);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, html, "utf8");
  console.log(`stories preview generated: ${outputPath}`);
}

main();
