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

function asList(value) {
  if (Array.isArray(value)) return value.filter((item) => item !== undefined && item !== null && String(item).trim());
  if (value && typeof value === "object") return Object.entries(value).map(([key, item]) => `${key}: ${formatValue(item)}`);
  if (value === undefined || value === null || String(value).trim() === "") return [];
  return [value];
}

function pick(data, keys) {
  for (const key of keys) {
    if (data[key] !== undefined && data[key] !== null && String(formatValue(data[key])).trim()) return data[key];
  }
  return "";
}

function renderList(items, ordered = false) {
  const list = asList(items);
  if (!list.length) return '<p class="preview-empty">' + TEXT.missing + "</p>";
  const tag = ordered ? "ol" : "ul";
  const className = ordered ? "pf-number-list" : "pf-list";
  return `<${tag} class="${className}">${list.map((item) => `<li>${escapeHtml(formatValue(item))}</li>`).join("")}</${tag}>`;
}

function renderLeadItem(label, value) {
  return `
    <div class="pf-lead-item">
      <p class="pf-lead-label">${escapeHtml(label)}</p>
      <p class="pf-lead-value">${escapeHtml(formatValue(value))}</p>
    </div>
  `;
}

function renderSection(id, index, title, bodyHtml) {
  const indexText = String(index).padStart(2, "0");
  return `
    <section class="preview-section-block" id="${id}">
      <h2 class="preview-section-heading"><span class="pf-section-icon">&#9670;</span>${indexText} ${escapeHtml(title)}</h2>
      <div class="preview-section-body">${bodyHtml}</div>
    </section>
  `;
}

function renderKnowledgeAnchoring(value) {
  if (!value || typeof value !== "object") return '<p class="preview-empty">' + TEXT.missing + "</p>";
  const rows = Object.entries(value).map(([key, item]) => `
    <tr><th>${escapeHtml(key)}</th><td>${escapeHtml(formatValue(item))}</td></tr>
  `);
  return rows.length ? `<div class="table-wrap"><table><tbody>${rows.join("")}</tbody></table></div>` : '<p class="preview-empty">' + TEXT.missing + "</p>";
}

function buildContent(data) {
  const projectName = pick(data, ["project_name", "name", "title"]) || TEXT.product;
  const recommendedDirection = pick(data, ["recommended_direction", "recommendation", "direction"]);
  const problemDefinition = pick(data, ["problem_definition", "core_problem", "problem"]);
  const targetRoles = pick(data, ["target_roles", "roles", "primary_roles"]);
  const constraints = pick(data, ["constraints", "non_goals", "scope_constraints"]);
  const sections = [];
  const nav = [];

  function add(id, title, body) {
    const index = sections.length + 1;
    sections.push(renderSection(id, index, title, body));
    nav.push({ id, title: `${String(index).padStart(2, "0")} ${title}`, level: 1 });
  }

  const hero = `
    <div class="pf-document-lead">
      <h1 class="preview-document-title">${TEXT.product}\uff1a${escapeHtml(formatValue(projectName))}</h1>
      <div class="pf-lead-grid">
        ${renderLeadItem(TEXT.leadRecommended, recommendedDirection)}
        ${renderLeadItem(TEXT.leadProblem, problemDefinition)}
        ${renderLeadItem(TEXT.leadRole, asList(targetRoles).join(" / "))}
        ${renderLeadItem(TEXT.leadConstraint, asList(constraints).slice(0, 3).join("\uff1b"))}
      </div>
    </div>
  `;

  add("problem-framing-summary", TEXT.summary, `<p>${escapeHtml(formatValue(pick(data, ["input_summary", "summary", "context"])))}</p>`);
  add("problem-framing-definition", TEXT.definition, `<p>${escapeHtml(formatValue(problemDefinition))}</p>`);
  add("problem-framing-roles", TEXT.roles, `<h3 class="pf-subtitle">${TEXT.targetRole}</h3>${renderList(targetRoles)}<h3 class="pf-subtitle">${TEXT.targetScenario}</h3>${renderList(pick(data, ["target_scenarios", "scenarios", "use_scenarios"]))}`);
  add("problem-framing-workarounds", TEXT.workarounds, renderList(pick(data, ["current_workarounds", "workarounds", "current_solution"])));
  add("problem-framing-opportunities", TEXT.opportunities, renderList(pick(data, ["opportunities", "opportunity_points"]), true));
  add("problem-framing-directions", TEXT.directions, renderList(pick(data, ["candidate_directions", "directions", "options"]), true));
  add("problem-framing-recommendation", TEXT.recommendation, `<p>${escapeHtml(formatValue(recommendedDirection))}</p>`);
  add("problem-framing-handoff", TEXT.handoff, renderList(pick(data, ["handoff_contract", "downstream_contract", "handoff"])));
  add("problem-framing-constraints", TEXT.constraints, renderList(constraints));
  add("problem-framing-gaps", TEXT.gaps, renderList(pick(data, ["gaps", "open_gaps", "open_questions"])));
  add("problem-framing-knowledge", TEXT.knowledge, renderKnowledgeAnchoring(pick(data, ["knowledge_anchoring", "knowledge_anchor"])));

  return { html: hero + sections.join("\n"), nav, projectName };
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
  const [shellArg, templateArg, contextArg, markdownArg, outputArg] = process.argv.slice(2);
  if (!shellArg || !templateArg || !contextArg || !markdownArg || !outputArg) {
    fail("shell_path content_template_path context_json_path markdown_path output_html_path are required");
  }

  const shellRaw = readFile(path.resolve(process.cwd(), shellArg), "shell template");
  const templateRaw = readFile(path.resolve(process.cwd(), templateArg), "content template");
  const markdown = readFile(path.resolve(process.cwd(), markdownArg), "markdown");

  let data = null;
  try {
    const contextRaw = readFile(path.resolve(process.cwd(), contextArg), "context json", false);
    if (contextRaw.trim()) data = JSON.parse(contextRaw);
  } catch (_) {
    data = null;
  }

  const hasDetailedContext = Boolean(data && (
    data.problem_definition ||
    data.target_roles ||
    data.candidate_directions ||
    data.handoff_contract ||
    data.knowledge_anchoring
  ));
  const rendered = hasDetailedContext ? buildContent(data) : buildMarkdownFallback(markdown);
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
