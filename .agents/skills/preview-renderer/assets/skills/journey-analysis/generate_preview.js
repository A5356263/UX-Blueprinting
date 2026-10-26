"use strict";

const fs = require("fs");
const path = require("path");
const markdownRenderer = require("../../markdown_renderer");

const TEXT = {
  missing: "\u672a\u63d0\u4f9b",
  product: "\u89d2\u8272\u65c5\u7a0b",
  previewTitle: "\u89d2\u8272\u65c5\u7a0b\u9884\u89c8",
  userGoal: "\u7528\u6237\u76ee\u6807",
  userAction: "\u7528\u6237\u884c\u52a8",
  touchpoint: "\u89e6\u70b9",
  userVoice: "\u7528\u6237\u5fc3\u58f0",
  confidenceRisk: "\u4fe1\u5fc3\u4e0e\u98ce\u9669",
  painPoint: "\u75db\u70b9",
  opportunity: "\u8bbe\u8ba1\u673a\u4f1a",
  transition: "\u9636\u6bb5\u8f6c\u6298",
  high: "\u9ad8",
  low: "\u4f4e"
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

function replaceRequired(source, marker, value) {
  if (!source.includes(marker)) fail(`required marker not found: ${marker}`);
  return source.replace(marker, value);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function buildMarkdownFallback(markdown) {
  const sections = markdownRenderer.markdownToSections(markdown, {
    prefix: "journey-analysis-markdown-section",
    fallbackTitle: TEXT.product
  });
  return {
    contentHtml: `<h1 class="preview-document-title">${TEXT.product}</h1>${markdownRenderer.renderSections(sections)}`,
    navHtml: markdownRenderer.renderNav(sections, "journey-analysis"),
    title: TEXT.product
  };
}

function parseArgs(args) {
  if (args.length === 4) {
    const [shellPathArg, templatePathArg, markdownPathArg, outputPathArg] = args;
    return { shellPathArg, templatePathArg, markdownPathArg, outputPathArg };
  }
  fail("shell_path content_template_path markdown_path output_html_path are required");
}

function main() {
  const { shellPathArg, templatePathArg, markdownPathArg, outputPathArg } = parseArgs(process.argv.slice(2));
  const shellPath = path.resolve(process.cwd(), shellPathArg);
  const templatePath = path.resolve(process.cwd(), templatePathArg);
  const outputPath = path.resolve(process.cwd(), outputPathArg);

  const shellRaw = readFile(shellPath, "shell template");
  const templateRaw = readFile(templatePath, "content template");
  const markdown = readFile(path.resolve(process.cwd(), markdownPathArg), "markdown source");
  const rendered = buildMarkdownFallback(markdown);
  const contentHtml = replaceRequired(templateRaw, "<!-- JOURNEY_CONTENT -->", rendered.contentHtml);
  const sidebarNav = rendered.navHtml;
  const bootstrapData = JSON.stringify({
    activeSkill: "journey-analysis",
    skills: ["journey-analysis"]
  }, null, 2);

  let html = shellRaw;
  html = html.replace("<title>\u7edf\u4e00\u9884\u89c8</title>", `<title>${TEXT.previewTitle} - ${escapeHtml(TEXT.product)}</title>`);
  html = replaceRequired(html, "<!-- PREVIEW_SIDEBAR_NAV -->", sidebarNav);
  html = replaceRequired(html, "<!-- PREVIEW_CONTENT -->", contentHtml);
  html = replaceRequired(html, "<!-- PREVIEW_BOOTSTRAP_DATA -->", bootstrapData);
  html = html.replace("/* PREVIEW_ADDITIONAL_STYLES */", "");
  html = html.replace("<!-- PREVIEW_ADDITIONAL_SCRIPTS -->", "");

  const unresolvedMarkers = [
    "PROJECT_NAME_HERE",
    "PREVIEW_SKILL_TABS",
    "<!-- JOURNEY_CONTENT -->",
    "FOOTER_SOURCE_PATH",
    "__JOURNEY_DATA_JSON__"
  ];
  for (const marker of unresolvedMarkers) {
    if (html.includes(marker)) fail(`generated html contains unresolved marker: ${marker}`);
  }

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, html, "utf8");
  console.log(`journey-analysis preview generated: ${outputPath}`);
}

main();
