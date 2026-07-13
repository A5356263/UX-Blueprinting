"use strict";

const fs = require("fs");
const path = require("path");

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

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function text(value, fallback = "未提供") {
  if (Array.isArray(value)) return value.length ? value.map((item) => text(item, fallback)).join("；") : fallback;
  if (value && typeof value === "object") return text(value.direction || value.label || value.name || fallback, fallback);
  const normalized = String(value ?? "").trim();
  return normalized || fallback;
}

function listHtml(value) {
  const list = Array.isArray(value) ? value : value ? [value] : [];
  if (!list.length) return `<span>${escapeHtml(text(null))}</span>`;
  return `<ul>${list.map((item) => `<li>${escapeHtml(text(item))}</li>`).join("")}</ul>`;
}

function confidenceClass(value) {
  const normalized = text(value, "");
  if (normalized.includes("高")) return "journey-confidence-high";
  if (normalized.includes("低")) return "journey-confidence-low";
  return "journey-confidence-medium";
}

function renderSignal(stage) {
  const confidence = text(stage.confidence);
  const risk = text(stage.dropout_risk, "");
  const badge = risk ? `<span class="journey-risk-badge">${escapeHtml(risk)}</span>` : "";
  return `
    <div class="journey-signal">
      <span class="journey-confidence ${confidenceClass(confidence)}">${escapeHtml(confidence)}</span>
      <div>${escapeHtml(text(stage.confidence_reason))}</div>
      ${badge}
    </div>
  `;
}

function renderOpportunities(value) {
  const list = Array.isArray(value) ? value : value ? [value] : [];
  if (!list.length) return `<span>${escapeHtml(text(null))}</span>`;
  return list.map((item) => {
    const direction = escapeHtml(text(item.direction || item));
    const hint = item.downstream_hint ? ` <span>(${escapeHtml(text(item.downstream_hint))})</span>` : "";
    return `<div class="journey-opportunity">${direction}${hint}</div>`;
  }).join("");
}

function renderRow(label, stages, renderer) {
  return `
    <div class="journey-label">${escapeHtml(label)}</div>
    ${stages.map((stage) => `<div class="journey-cell">${renderer(stage)}</div>`).join("")}
  `;
}

function renderTransitions(transitions) {
  const list = Array.isArray(transitions) ? transitions : [];
  if (!list.length) return `<p>${escapeHtml(text(null))}</p>`;
  return `<p>${list.map((item) => {
    const from = text(item.from);
    const to = text(item.to);
    const reason = text(item.reason);
    return `${from} -> ${to}：${reason}`;
  }).map(escapeHtml).join("；")}</p>`;
}

function renderJourney(journey, index, data) {
  const stages = Array.isArray(journey.stages) ? journey.stages : [];
  const columns = `120px repeat(${Math.max(stages.length, 1)}, minmax(180px, 1fr))`;
  const primaryRole = text(journey.role || data.primary_role);
  const stageHeaders = stages.map((stage, stageIndex) => `
    <div class="journey-stage-header">
      <span class="journey-stage-index">${stageIndex + 1}</span>
      ${escapeHtml(text(stage.name))}
    </div>
  `).join("");

  const rows = [
    renderRow("用户目标", stages, (stage) => `<div class="journey-goal">${escapeHtml(text(stage.goal))}</div>`),
    renderRow("用户行动", stages, (stage) => listHtml(stage.actions)),
    renderRow("触点", stages, (stage) => listHtml(stage.touchpoints)),
    renderRow("用户心声", stages, (stage) => `<div class="journey-quote">${escapeHtml(text(stage.user_voice))}</div>`),
    renderRow("信心与风险", stages, renderSignal),
    renderRow("痛点", stages, (stage) => listHtml(stage.pain_points)),
    renderRow("设计机会", stages, (stage) => renderOpportunities(stage.opportunities))
  ].join("");

  return `
    <section class="preview-section-block" id="journey-analysis-section-${index}" data-section-key="journey-${index}">
      <div class="journey-header">
        <h1 class="journey-title">${escapeHtml(text(data.project_name, "角色旅程"))} - User Journey Map</h1>
        <p class="journey-subtitle">${escapeHtml(text(data.generated_at))} / ${escapeHtml(text(data.mode))} / ${escapeHtml(text(data.source))}</p>
      </div>
      <div class="journey-persona-card">
        <div class="journey-avatar">${escapeHtml(primaryRole.slice(0, 1))}</div>
        <div class="journey-persona-info">
          <b>${escapeHtml(primaryRole)}</b>
          <span>${escapeHtml(text(journey.summary || data.journey_type))}</span>
        </div>
      </div>
      <p class="journey-jtbd">${escapeHtml(text(data.start_condition || journey.summary))}</p>
      <div class="journey-map-wrap">
        <div class="journey-grid" style="grid-template-columns: ${columns};">
          <div class="journey-label"></div>
          ${stageHeaders || `<div class="journey-stage-header"><span class="journey-stage-index">1</span>${escapeHtml(text(null))}</div>`}
          ${rows}
        </div>
      </div>
      <div class="journey-transition">
        <h3>阶段转折</h3>
        ${renderTransitions(journey.key_transitions)}
      </div>
    </section>
  `;
}

function buildContent(data) {
  const journeys = Array.isArray(data.journeys) ? data.journeys : [];
  if (!journeys.length) {
    return `
      <section class="preview-section-block" id="journey-analysis-section-0">
        <h1 class="journey-title">${escapeHtml(text(data.project_name, "角色旅程"))}</h1>
        <p>${escapeHtml(text(null))}</p>
      </section>
    `;
  }
  return journeys.map((journey, index) => renderJourney(journey, index, data)).join("");
}

function parseArgs(args) {
  if (args.length === 5) {
    const [shellPathArg, templatePathArg, contextPathArg, markdownPathArg, outputPathArg] = args;
    return { shellPathArg, templatePathArg, contextPathArg, markdownPathArg, outputPathArg };
  }
  if (args.length === 4) {
    const [shellPathArg, templatePathArg, contextPathArg, outputPathArg] = args;
    return { shellPathArg, templatePathArg, contextPathArg, markdownPathArg: "", outputPathArg };
  }
  if (args.length === 3) {
    const [templatePathArg, contextPathArg, outputPathArg] = args;
    return {
      shellPathArg: ".claude/skills/preview-renderer/assets/shell/preview_shell.html",
      templatePathArg,
      contextPathArg,
      markdownPathArg: "",
      outputPathArg
    };
  }
  fail("shell_path content_template_path context_json_path [markdown_path] output_html_path are required");
}

function main() {
  const { shellPathArg, templatePathArg, contextPathArg, markdownPathArg, outputPathArg } = parseArgs(process.argv.slice(2));
  const shellPath = path.resolve(process.cwd(), shellPathArg);
  const templatePath = path.resolve(process.cwd(), templatePathArg);
  const contextPath = path.resolve(process.cwd(), contextPathArg);
  const outputPath = path.resolve(process.cwd(), outputPathArg);

  const shellRaw = readFile(shellPath, "shell template");
  const templateRaw = readFile(templatePath, "content template");
  if (markdownPathArg) readFile(path.resolve(process.cwd(), markdownPathArg), "markdown source");

  let contextData = null;
  try {
    contextData = JSON.parse(readFile(contextPath, "context json"));
  } catch (error) {
    fail(`failed to parse context json: ${contextPath}\n${error.message}`);
  }

  const contentHtml = replaceRequired(templateRaw, "<!-- JOURNEY_CONTENT -->", buildContent(contextData));
  const sidebarNav = '<a class="preview-nav-item level-1" href="#journey-analysis-section-0" data-skill="journey-analysis">角色旅程</a>';
  const bootstrapData = JSON.stringify({
    activeSkill: "journey-analysis",
    skills: ["journey-analysis"]
  }, null, 2);

  let html = shellRaw;
  html = html.replace("<title>统一预览</title>", `<title>角色旅程预览 - ${escapeHtml(text(contextData.project_name, "角色旅程"))}</title>`);
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
