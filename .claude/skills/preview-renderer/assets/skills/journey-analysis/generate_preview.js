"use strict";

const fs = require("fs");
const path = require("path");

const PLACEHOLDER = "/* __JOURNEY_DATA_JSON__ */ null";

function fail(message) {
  console.error(message);
  process.exit(1);
}

function main() {
  const [templatePathArg, contextPathArg, outputPathArg] = process.argv.slice(2);

  if (!templatePathArg || !contextPathArg || !outputPathArg) {
    fail("template_path context_json_path output_html_path are required");
  }

  const templatePath = path.resolve(process.cwd(), templatePathArg);
  const contextPath = path.resolve(process.cwd(), contextPathArg);
  const outputPath = path.resolve(process.cwd(), outputPathArg);

  let templateRaw = "";
  let contextRaw = "";
  let contextData = null;

  try {
    templateRaw = fs.readFileSync(templatePath, "utf8");
  } catch (error) {
    fail(`failed to read template: ${templatePath}\n${error.message}`);
  }

  try {
    contextRaw = fs.readFileSync(contextPath, "utf8");
    contextData = JSON.parse(contextRaw);
  } catch (error) {
    fail(`failed to read or parse context json: ${contextPath}\n${error.message}`);
  }

  if (!templateRaw.includes(PLACEHOLDER)) {
    fail(`template placeholder not found: ${PLACEHOLDER}`);
  }

  const contextJson = JSON.stringify(contextData, null, 2);
  const html = templateRaw.replace(PLACEHOLDER, contextJson);

  if (html.includes(PLACEHOLDER)) {
    fail("template placeholder was not fully replaced");
  }

  for (const marker of ["function escapeHtml", "function render", "const JOURNEY_DATA ="]) {
    if (!html.includes(marker)) {
      fail(`generated html is missing required marker: ${marker}`);
    }
  }

  const outputDir = path.dirname(outputPath);
  fs.mkdirSync(outputDir, { recursive: true });
  fs.writeFileSync(outputPath, html, "utf8");

  console.log(`journey-analysis preview generated: ${outputPath}`);
}

main();
