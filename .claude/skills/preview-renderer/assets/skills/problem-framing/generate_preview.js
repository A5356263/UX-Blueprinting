"use strict";

const fs = require("fs");
const path = require("path");

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

function asList(value) {
  if (Array.isArray(value)) return value.filter((item) => item !== undefined && item !== null && String(item).trim());
  if (value && typeof value === "object") return Object.entries(value).map(([key, item]) => `${key}: ${formatValue(item)}`);
  if (value === undefined || value === null || String(value).trim() === "") return [];
  return [value];
}

function formatValue(value) {
  if (Array.isArray(value)) return value.map(formatValue).join("；");
  if (value && typeof value === "object") return Object.entries(value).map(([key, item]) => `${key}: ${formatValue(item)}`).join("；");
  return String(value ?? "").trim() || "未提供";
}

function renderList(items) {
  const list = asList(items);
  if (!list.length) return '<p class="preview-empty">未提供</p>';
  return `<ul class="pf-list">${list.map((item) => `<li>${escapeHtml(formatValue(item))}</li>`).join("")}</ul>`;
}

function renderSection(id, title, bodyHtml) {
  return `
    <section class="preview-section-block" id="${id}">
      <h2 class="preview-section-heading">${escapeHtml(title)}</h2>
      <div class="preview-section-body">${bodyHtml}</div>
    </section>
  `;
}

function renderCard(label, value) {
  return `
    <div class="pf-card">
      <p class="pf-card-label">${escapeHtml(label)}</p>
      <p class="pf-card-value">${escapeHtml(formatValue(value))}</p>
    </div>
  `;
}

function pick(data, keys) {
  for (const key of keys) {
    if (data[key] !== undefined && data[key] !== null && String(formatValue(data[key])).trim()) return data[key];
  }
  return "";
}

function renderKnowledgeAnchoring(value) {
  if (!value || typeof value !== "object") return '<p class="preview-empty">未提供</p>';
  const rows = Object.entries(value).map(([key, item]) => `
    <tr><th>${escapeHtml(key)}</th><td>${escapeHtml(formatValue(item))}</td></tr>
  `);
  return rows.length ? `<div class="table-wrap"><table><tbody>${rows.join("")}</tbody></table></div>` : '<p class="preview-empty">未提供</p>';
}

function buildContent(data) {
  const projectName = pick(data, ["project_name", "name", "title"]) || "问题框定";
  const recommendedDirection = pick(data, ["recommended_direction", "recommendation", "direction"]);
  const problemDefinition = pick(data, ["problem_definition", "core_problem", "problem"]);
  const targetRoles = pick(data, ["target_roles", "roles", "primary_roles"]);
  const constraints = pick(data, ["constraints", "non_goals", "scope_constraints"]);
  const sections = [];
  const nav = [];

  function add(id, title, body) {
    sections.push(renderSection(id, title, body));
    nav.push({ id, title, level: 1 });
  }

  const hero = `
    <h1 class="preview-document-title">问题框定：${escapeHtml(formatValue(projectName))}</h1>
    <div class="pf-hero">
      ${renderCard("推荐方向", recommendedDirection)}
      ${renderCard("核心问题", problemDefinition)}
      ${renderCard("目标角色", asList(targetRoles).join(" / "))}
      ${renderCard("关键约束", asList(constraints).slice(0, 3).join("；"))}
    </div>
  `;

  add("problem-framing-summary", "输入摘要", `<p>${escapeHtml(formatValue(pick(data, ["input_summary", "summary", "context"])))}</p>`);
  add("problem-framing-definition", "问题定义", `<p>${escapeHtml(formatValue(problemDefinition))}</p>`);
  add("problem-framing-roles", "目标用户与场景", `<h3>目标角色</h3>${renderList(targetRoles)}<h3>目标场景</h3>${renderList(pick(data, ["target_scenarios", "scenarios", "use_scenarios"]))}`);
  add("problem-framing-workarounds", "当前替代做法", renderList(pick(data, ["current_workarounds", "workarounds", "current_solution"])));
  add("problem-framing-opportunities", "机会点", renderList(pick(data, ["opportunities", "opportunity_points"])));
  add("problem-framing-directions", "候选方向", renderList(pick(data, ["candidate_directions", "directions", "options"])));
  add("problem-framing-recommendation", "推荐方向", `<p>${escapeHtml(formatValue(recommendedDirection))}</p>`);
  add("problem-framing-handoff", "承接契约", renderList(pick(data, ["handoff_contract", "downstream_contract", "handoff"])));
  add("problem-framing-constraints", "约束与不做什么", renderList(constraints));
  add("problem-framing-gaps", "待确认问题", renderList(pick(data, ["gaps", "open_gaps", "open_questions"])));
  add("problem-framing-knowledge", "知识锚定", renderKnowledgeAnchoring(pick(data, ["knowledge_anchoring", "knowledge_anchor"])));

  return { html: hero + sections.join("\n"), nav };
}

function main() {
  const [shellArg, templateArg, contextArg, markdownArg, outputArg] = process.argv.slice(2);
  if (!shellArg || !templateArg || !contextArg || !markdownArg || !outputArg) {
    fail("shell_path content_template_path context_json_path markdown_path output_html_path are required");
  }

  const shellRaw = readFile(path.resolve(process.cwd(), shellArg), "shell template");
  const templateRaw = readFile(path.resolve(process.cwd(), templateArg), "content template");
  readFile(path.resolve(process.cwd(), markdownArg), "markdown", false);

  let data = null;
  try {
    data = JSON.parse(readFile(path.resolve(process.cwd(), contextArg), "context json"));
  } catch (error) {
    fail(`failed to parse context json: ${contextArg}\n${error.message}`);
  }

  const rendered = buildContent(data);
  const contentHtml = requiredReplace(templateRaw, "<!-- PROBLEM_FRAMING_CONTENT -->", rendered.html);
  const sidebarNav = rendered.nav.map((item) => `<a class="preview-nav-item level-${item.level}" href="#${item.id}" data-skill="problem-framing">${escapeHtml(item.title)}</a>`).join("\n");
  const bootstrapData = JSON.stringify({ activeSkill: "problem-framing", skills: ["problem-framing"] }, null, 2);

  let html = shellRaw;
  html = html.replace("<title>统一预览</title>", `<title>问题框定预览 - ${escapeHtml(formatValue(pick(data, ["project_name", "name", "title"]) || "未命名项目"))}</title>`);
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
