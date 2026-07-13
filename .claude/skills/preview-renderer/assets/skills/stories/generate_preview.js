"use strict";

const fs = require("fs");
const path = require("path");

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

function renderList(items) {
  const list = asList(items);
  if (!list.length) return '<p class="preview-empty">' + TEXT.missing + "</p>";
  return `<ul>${list.map((item) => `<li>${escapeHtml(formatValue(item))}</li>`).join("")}</ul>`;
}

function normalizeRole(role) {
  const roleText = formatValue(role);
  if (roleText.includes(TEXT.employee)) return TEXT.employee;
  if (roleText.includes("\u5ba1\u6279") || roleText.includes("\u8d1f\u8d23\u4eba")) return TEXT.approver;
  if (roleText.includes("\u7ba1\u7406")) return TEXT.admin;
  if (roleText.includes(TEXT.system)) return TEXT.system;
  return roleText;
}

function roleIcon(role) {
  if (role === TEXT.employee) return "01";
  if (role === TEXT.approver) return "02";
  if (role === TEXT.admin) return "03";
  if (role === TEXT.system) return "04";
  return "#";
}

function priorityClass(priority) {
  return String(priority || "").toUpperCase() === "P0" ? "p0" : "";
}

function renderStoryCard(story) {
  const assumption = story.critical_assumption || "";
  return `
    <article class="story-card">
      <div class="story-card-head">
        <h3>${escapeHtml(story.id || "Story")} · ${escapeHtml(story.title || TEXT.untitledStory)}</h3>
      </div>
      <div class="story-meta">
        <span class="story-pill ${priorityClass(story.priority)}">${escapeHtml(story.priority || TEXT.priorityMissing)}</span>
        <span class="story-pill">${escapeHtml(story.size || story.type || "Story")}</span>
        ${assumption ? `<span class="story-pill assumption">${TEXT.assumption}</span>` : ""}
      </div>
      <p><strong>${TEXT.role}\uff1a</strong>${escapeHtml(story.persona || story.role || TEXT.missing)}</p>
      <p><strong>${TEXT.goal}\uff1a</strong>${escapeHtml(story.goal || TEXT.missing)}</p>
      <p><strong>${TEXT.scenario}\uff1a</strong>${escapeHtml(story.scenario || TEXT.missing)}</p>
      <div class="story-card-section">
        <h4>${TEXT.userTask}</h4>
        <p>${escapeHtml(story.story_text || story.user_story || TEXT.missing)}</p>
      </div>
      <div class="story-card-section">
        <h4>${TEXT.acceptance}</h4>
        ${renderList(story.acceptance_criteria)}
      </div>
      <div class="story-card-section">
        <h4>${TEXT.touchpoints}</h4>
        ${renderList(story.design_touchpoints)}
      </div>
      <div class="story-card-section">
        <h4>${TEXT.sourceRisk}</h4>
        <p><strong>${TEXT.sourceBasis}\uff1a</strong>${escapeHtml(story.source_basis || TEXT.missing)}</p>
        <p><strong>${TEXT.risk}\uff1a</strong>${escapeHtml(story.risk || TEXT.missing)}</p>
        ${assumption ? `<p><strong>${TEXT.assumption}\uff1a</strong>${escapeHtml(assumption)}</p>` : ""}
      </div>
    </article>
  `;
}

function storyArray(data) {
  if (Array.isArray(data.stories)) return data.stories;
  if (Array.isArray(data.user_stories)) return data.user_stories;
  if (Array.isArray(data.story_map)) return data.story_map;
  return [];
}

function buildContent(data) {
  const stories = storyArray(data);
  const groups = new Map();
  for (const story of stories) {
    const role = normalizeRole(story.persona || story.role);
    if (!groups.has(role)) groups.set(role, []);
    groups.get(role).push(story);
  }

  const p0Count = stories.filter((story) => String(story.priority || "").toUpperCase() === "P0").length;
  const assumptionCount = stories.filter((story) => story.critical_assumption).length;
  const nav = [{ id: "stories-overview", title: TEXT.overview, level: 1 }];

  let html = `
    <h1 class="preview-document-title">${TEXT.product}\uff1a${escapeHtml(data.project_name || TEXT.untitledProject)}</h1>
    <section class="preview-section-block" id="stories-overview">
      <h2 class="preview-section-heading">${TEXT.overview}</h2>
      <div class="story-summary">
        <div class="story-summary-card"><span>${TEXT.source}</span><strong>${escapeHtml(data.source_mode || data.source || TEXT.missing)}</strong></div>
        <div class="story-summary-card"><span>${TEXT.storyCount}</span><strong>${stories.length}</strong></div>
        <div class="story-summary-card"><span>${TEXT.p0}</span><strong>${p0Count}</strong></div>
        <div class="story-summary-card"><span>${TEXT.assumption}</span><strong>${assumptionCount}</strong></div>
      </div>
      <p>${escapeHtml(data.direction || data.summary || TEXT.summaryMissing)}</p>
    </section>
  `;

  for (const [role, roleStories] of groups.entries()) {
    const id = `stories-role-${nav.length}`;
    nav.push({ id, title: role, level: 1 });
    html += `
      <section class="preview-section-block story-role-group" id="${id}">
        <h2 class="story-role-title"><span class="story-role-icon">${escapeHtml(roleIcon(role))}</span>${escapeHtml(role)}</h2>
        <div class="story-grid">${roleStories.map(renderStoryCard).join("")}</div>
      </section>
    `;
  }

  const p0Stories = stories
    .filter((story) => String(story.priority || "").toUpperCase() === "P0")
    .map((story) => `${story.id || "Story"} ${story.title || ""}`.trim());
  const auxiliaryStories = stories
    .filter((story) => String(story.priority || "").toUpperCase() !== "P0")
    .map((story) => `${story.id || "Story"} ${story.title || ""}`.trim());
  const assumptions = stories
    .filter((story) => story.critical_assumption)
    .map((story) => `${story.id || "Story"}\uff1a${story.critical_assumption}`);

  nav.push({ id: "stories-lists", title: TEXT.mainAndAssumption, level: 1 });
  html += `
    <section class="preview-section-block" id="stories-lists">
      <h2 class="preview-section-heading">${TEXT.mainAndAssumption}</h2>
      <div class="preview-section-body">
        <h3>${TEXT.p0List}</h3>${renderList(p0Stories)}
        <h3>${TEXT.auxiliaryList}</h3>${renderList(auxiliaryStories)}
        <h3>${TEXT.assumptionList}</h3>${renderList(assumptions)}
      </div>
    </section>
  `;

  return { html, nav };
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
  const contentHtml = requiredReplace(templateRaw, "<!-- STORIES_CONTENT -->", rendered.html);
  const sidebarNav = rendered.nav.map((item) => `<a class="preview-nav-item level-${item.level}" href="#${item.id}" data-skill="stories">${escapeHtml(item.title)}</a>`).join("\n");
  const bootstrapData = JSON.stringify({ activeSkill: "stories", skills: ["stories"] }, null, 2);

  let html = shellRaw;
  html = html.replace("<title>\u7edf\u4e00\u9884\u89c8</title>", `<title>${TEXT.previewTitle} - ${escapeHtml(data.project_name || TEXT.untitledProject)}</title>`);
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
