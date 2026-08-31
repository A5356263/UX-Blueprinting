"use strict";

const fs = require("fs");
const path = require("path");
const markdownRenderer = require("../../markdown_renderer");

const TEXT = {
  product: "页面设计文档",
  previewTitle: "页面设计文档预览"
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

function getDocumentTitle(markdown) {
  const match = markdown.replace(/^\uFEFF/, "").match(/^#\s+(.+)$/m);
  return match ? match[1].trim() : TEXT.product;
}

function parseArgs(args) {
  if (args.length === 5) {
    const [shellPathArg, templatePathArg, contextPathArg, markdownPathArg, outputPathArg] = args;
    return { shellPathArg, templatePathArg, contextPathArg, markdownPathArg, outputPathArg };
  }
  if (args.length === 0) {
    return {
      shellPathArg: ".claude/skills/preview-renderer/assets/shell/preview_shell.html",
      templatePathArg: ".claude/skills/preview-renderer/assets/skills/page-spec/preview_template.html",
      contextPathArg: "spark-output/context/page-spec.json",
      markdownPathArg: "spark-output/page_spec.md",
      outputPathArg: "spark-output/preview/page_spec_preview.html"
    };
  }
  fail("shell_path content_template_path context_json_path markdown_path output_html_path are required");
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const shellRaw = readFile(path.resolve(process.cwd(), args.shellPathArg), "shell template");
  let templateRaw = readFile(path.resolve(process.cwd(), args.templatePathArg), "content template");
  const markdown = readFile(path.resolve(process.cwd(), args.markdownPathArg), "markdown source");
  readFile(path.resolve(process.cwd(), args.contextPathArg), "context json", false);

  if (hasMojibake(markdown) || hasMojibake(shellRaw) || hasMojibake(templateRaw)) {
    fail("source contains obvious mojibake; stop preview generation");
  }

  const sections = markdownRenderer.markdownToSections(markdown, {
    prefix: "page-spec-section",
    fallbackTitle: TEXT.product
  });
  templateRaw = requiredReplace(templateRaw, "DOCUMENT_TITLE", escapeHtml(getDocumentTitle(markdown)));
  templateRaw = requiredReplace(templateRaw, "<!-- CONTENT_SECTIONS -->", markdownRenderer.renderSections(sections));
  templateRaw = requiredReplace(templateRaw, "FOOTER_SOURCE_PATH", escapeHtml(args.markdownPathArg));

  let html = shellRaw;
  html = html.replace("<title>统一预览</title>", `<title>${TEXT.previewTitle}</title>`);
  html = requiredReplace(html, "<!-- PREVIEW_SIDEBAR_NAV -->", markdownRenderer.renderNav(sections, "page-spec"));
  html = requiredReplace(html, "<!-- PREVIEW_CONTENT -->", templateRaw);
  html = requiredReplace(html, "<!-- PREVIEW_BOOTSTRAP_DATA -->", JSON.stringify({ activeSkill: "page-spec", skills: ["page-spec"] }, null, 2));
  html = html.replace("/* PREVIEW_ADDITIONAL_STYLES */", "");
  html = html.replace("<!-- PREVIEW_ADDITIONAL_SCRIPTS -->", "");

  for (const marker of ["DOCUMENT_TITLE", "CONTENT_SECTIONS", "FOOTER_SOURCE_PATH", "PREVIEW_SIDEBAR_NAV", "PREVIEW_CONTENT", "PREVIEW_BOOTSTRAP_DATA"]) {
    if (html.includes(marker)) fail(`generated html contains unresolved marker: ${marker}`);
  }

  const outputPath = path.resolve(process.cwd(), args.outputPathArg);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, html, "utf8");
  console.log(`page-spec preview generated: ${outputPath}`);
}

main();
