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
  return `<ul>${list.map((item) => `<li>${escapeHtml(formatValue(item))}</li>`).join("")}</ul>`;
}

function normalizeRole(role) {
  const roleText = formatValue(role);
  if (roleText.includes("员工")) return "员工";
  if (roleText.includes("审批") || roleText.includes("负责人")) return "审批人";
  if (roleText.includes("管理")) return "管理员";
  if (roleText.includes("系统")) return "系统";
  return roleText;
}

function priorityClass(priority) {
  return String(priority || "").toUpperCase() === "P0" ? "p0" : "";
}

function renderStoryCard(story) {
  const assumption = story.critical_assumption || "";
  return `
    <article class="story-card">
      <div class="story-card-head">
        <h3>${escapeHtml(story.id || "Story")} · ${escapeHtml(story.title || "未命名故事")}</h3>
      </div>
      <div class="story-meta">
        <span class="story-pill ${priorityClass(story.priority)}">${escapeHtml(story.priority || "未标优先级")}</span>
        <span class="story-pill">${escapeHtml(story.size || story.type || "Story")}</span>
        ${assumption ? '<span class="story-pill assumption">关键假设</span>' : ""}
      </div>
      <p><strong>角色：</strong>${escapeHtml(story.persona || story.role || "未提供")}</p>
      <p><strong>目标：</strong>${escapeHtml(story.goal || "未提供")}</p>
      <p><strong>场景：</strong>${escapeHtml(story.scenario || "未提供")}</p>
      <div class="story-card-section">
        <h4>Story 主体</h4>
        <p>${escapeHtml(story.story_text || story.user_story || "未提供")}</p>
      </div>
      <div class="story-card-section">
        <h4>完成标准</h4>
        ${renderList(story.acceptance_criteria)}
      </div>
      <div class="story-card-section">
        <h4>设计触点</h4>
        ${renderList(story.design_touchpoints)}
      </div>
      <div class="story-card-section">
        <h4>来源与风险</h4>
        <p><strong>来源依据：</strong>${escapeHtml(story.source_basis || "未提供")}</p>
        <p><strong>风险：</strong>${escapeHtml(story.risk || "未提供")}</p>
        ${assumption ? `<p><strong>关键假设：</strong>${escapeHtml(assumption)}</p>` : ""}
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
  const nav = [{ id: "stories-overview", title: "故事概览", level: 1 }];

  let html = `
    <h1 class="preview-document-title">用户故事：${escapeHtml(data.project_name || "未命名项目")}</h1>
    <section class="preview-section-block" id="stories-overview">
      <h2 class="preview-section-heading">故事概览</h2>
      <div class="story-summary">
        <div class="story-summary-card"><span>来源</span><strong>${escapeHtml(data.source_mode || data.source || "未提供")}</strong></div>
        <div class="story-summary-card"><span>故事数量</span><strong>${stories.length}</strong></div>
        <div class="story-summary-card"><span>P0 主链</span><strong>${p0Count}</strong></div>
        <div class="story-summary-card"><span>关键假设</span><strong>${assumptionCount}</strong></div>
      </div>
      <p>${escapeHtml(data.direction || data.summary || "未提供方向摘要")}</p>
    </section>
  `;

  for (const [role, roleStories] of groups.entries()) {
    const id = `stories-role-${nav.length}`;
    nav.push({ id, title: role, level: 1 });
    html += `
      <section class="preview-section-block story-role-group" id="${id}">
        <h2 class="story-role-title">${escapeHtml(role)}</h2>
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
    .map((story) => `${story.id || "Story"}：${story.critical_assumption}`);

  nav.push({ id: "stories-lists", title: "主链与假设", level: 1 });
  html += `
    <section class="preview-section-block" id="stories-lists">
      <h2 class="preview-section-heading">主链与假设</h2>
      <div class="preview-section-body">
        <h3>P0 主链清单</h3>${renderList(p0Stories)}
        <h3>辅助能力清单</h3>${renderList(auxiliaryStories)}
        <h3>假设项清单</h3>${renderList(assumptions)}
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
  html = html.replace("<title>统一预览</title>", `<title>用户故事预览 - ${escapeHtml(data.project_name || "未命名项目")}</title>`);
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
