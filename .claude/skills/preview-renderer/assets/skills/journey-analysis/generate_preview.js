"use strict";

const fs = require("fs");
const path = require("path");

const PLACEHOLDER = "/* __JOURNEY_DATA_JSON__ */ null";

function fail(message) {
  console.error(message);
  process.exit(1);
}

function readFile(filePath, label) {
  try {
    return fs.readFileSync(filePath, "utf8");
  } catch (error) {
    fail(`failed to read ${label}: ${filePath}\n${error.message}`);
  }
}

function replaceRequired(source, marker, value) {
  if (!source.includes(marker)) fail(`required marker not found: ${marker}`);
  return source.replace(marker, value);
}

function main() {
  const args = process.argv.slice(2);
  let shellPathArg = "";
  let templatePathArg = "";
  let contextPathArg = "";
  let outputPathArg = "";

  if (args.length === 4) {
    [shellPathArg, templatePathArg, contextPathArg, outputPathArg] = args;
  } else if (args.length === 3) {
    [templatePathArg, contextPathArg, outputPathArg] = args;
    shellPathArg = ".claude/skills/preview-renderer/assets/shell/preview_shell.html";
  } else {
    fail("shell_path content_template_path context_json_path output_html_path are required");
  }

  const shellPath = path.resolve(process.cwd(), shellPathArg);
  const templatePath = path.resolve(process.cwd(), templatePathArg);
  const contextPath = path.resolve(process.cwd(), contextPathArg);
  const outputPath = path.resolve(process.cwd(), outputPathArg);

  const shellRaw = readFile(shellPath, "shell template");
  const templateRaw = readFile(templatePath, "content template");

  let contextData = null;
  try {
    contextData = JSON.parse(readFile(contextPath, "context json"));
  } catch (error) {
    fail(`failed to parse context json: ${contextPath}\n${error.message}`);
  }

  if (!templateRaw.includes(PLACEHOLDER)) {
    fail(`content template placeholder not found: ${PLACEHOLDER}`);
  }

  const contextJson = JSON.stringify(contextData, null, 2);
  const contentHtml = templateRaw
    .replace(PLACEHOLDER, contextJson)
    .replace("<!-- CONTENT_NAV_ITEMS -->", "");
  const projectName = contextData.project_name || "旅程分析";
  const sidebarNav = '<a class="preview-nav-item level-1" href="#journey-analysis-section-0" data-skill="journey-analysis">角色旅程</a>';
  const bootstrapData = JSON.stringify({
    activeSkill: "journey-analysis",
    skills: ["journey-analysis"]
  }, null, 2);

  let html = shellRaw;
  html = html.replace("<title>统一预览</title>", `<title>角色旅程预览 - ${projectName}</title>`);
  html = replaceRequired(html, "<!-- PREVIEW_SIDEBAR_NAV -->", sidebarNav);
  html = replaceRequired(html, "<!-- PREVIEW_CONTENT -->", contentHtml);
  html = replaceRequired(html, "<!-- PREVIEW_BOOTSTRAP_DATA -->", bootstrapData);
  html = html.replace("/* PREVIEW_ADDITIONAL_STYLES */", "");
  html = html.replace("<!-- PREVIEW_ADDITIONAL_SCRIPTS -->", "");

  for (const marker of ["function escapeHtml", "function render", "const JOURNEY_DATA =", "preview-shell"]) {
    if (!html.includes(marker)) fail(`generated html is missing required marker: ${marker}`);
  }

  const outputDir = path.dirname(outputPath);
  fs.mkdirSync(outputDir, { recursive: true });
  fs.writeFileSync(outputPath, html, "utf8");

  console.log(`journey-analysis preview generated: ${outputPath}`);
}

main();
