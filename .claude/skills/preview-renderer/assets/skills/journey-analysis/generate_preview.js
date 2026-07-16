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

function text(value, fallback = TEXT.missing) {
  if (Array.isArray(value)) return value.length ? value.map((item) => text(item, fallback)).join("\uff1b") : fallback;
  if (value && typeof value === "object") return text(value.direction || value.label || value.name || fallback, fallback);
  const normalized = String(value ?? "").trim();
  return normalized || fallback;
}

function normalizeStage(stage) {
  const risk = stage.dropout_risk;
  const normalizedRisk = risk && typeof risk === "object"
    ? `${text(risk.level, "")}${risk.reason ? `：${text(risk.reason, "")}` : ""}`
    : risk;
  return {
    ...stage,
    name: stage.name || stage.stage_name,
    goal: stage.goal || stage.user_goal,
    dropout_risk: normalizedRisk
  };
}

function normalizeTransition(transition) {
  const reason = [transition.reason, transition.trigger, transition.risk]
    .map((item) => text(item, ""))
    .filter(Boolean)
    .join("；");
  return {
    from: transition.from || transition.from_stage,
    to: transition.to || transition.to_stage,
    reason
  };
}

function normalizeContext(data) {
  const subject = data.journey_subject || {};
  const nestedJourneys = Array.isArray(data.journeys)
    ? data.journeys.filter((journey) => Array.isArray(journey.stages) && journey.stages.length)
    : [];
  const journeys = nestedJourneys.length
    ? nestedJourneys
    : (Array.isArray(data.stages) && data.stages.length ? [{
        role: subject.primary_role,
        summary: subject.journey_scope,
        stages: data.stages,
        key_transitions: data.key_transitions
      }] : []);

  return {
    ...data,
    primary_role: data.primary_role || subject.primary_role,
    journey_type: data.journey_type || subject.journey_type,
    start_condition: data.start_condition || subject.start_condition,
    journeys: journeys.map((journey) => ({
      ...journey,
      stages: journey.stages.map(normalizeStage),
      key_transitions: Array.isArray(journey.key_transitions)
        ? journey.key_transitions.map(normalizeTransition)
        : []
    }))
  };
}

function listHtml(value) {
  const list = Array.isArray(value) ? value : value ? [value] : [];
  if (!list.length) return `<span>${escapeHtml(text(null))}</span>`;
  return `<ul>${list.map((item) => `<li>${escapeHtml(text(item))}</li>`).join("")}</ul>`;
}

function confidenceClass(value) {
  const normalized = text(value, "");
  if (normalized.includes(TEXT.high)) return "journey-confidence-high";
  if (normalized.includes(TEXT.low)) return "journey-confidence-low";
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
    return `${from} -> ${to}\uff1a${reason}`;
  }).map(escapeHtml).join("\uff1b")}</p>`;
}

function renderJourney(journey, index, data) {
  const stages = Array.isArray(journey.stages) ? journey.stages : [];
  const columns = `120px repeat(${Math.max(stages.length, 1)}, 250px)`;
  const primaryRole = text(journey.role || data.primary_role);
  const stageHeaders = stages.map((stage, stageIndex) => `
    <div class="journey-stage-header" id="journey-analysis-section-${index}-stage-${stageIndex}">
      <span class="journey-stage-index">${stageIndex + 1}</span>
      <span>${escapeHtml(text(stage.name))}</span>
    </div>
  `).join("");

  const rows = [
    renderRow(TEXT.userGoal, stages, (stage) => `<div class="journey-goal">${escapeHtml(text(stage.goal))}</div>`),
    renderRow(TEXT.userAction, stages, (stage) => listHtml(stage.actions)),
    renderRow(TEXT.touchpoint, stages, (stage) => listHtml(stage.touchpoints)),
    renderRow(TEXT.userVoice, stages, (stage) => `<div class="journey-quote">${escapeHtml(text(stage.user_voice))}</div>`),
    renderRow(TEXT.confidenceRisk, stages, renderSignal),
    renderRow(TEXT.painPoint, stages, (stage) => listHtml(stage.pain_points)),
    renderRow(TEXT.opportunity, stages, (stage) => renderOpportunities(stage.opportunities))
  ].join("");

  return `
    <section class="preview-section-block" id="journey-analysis-section-${index}" data-section-key="journey-${index}">
      <div class="journey-header">
        <h1 class="journey-title">${escapeHtml(text(data.project_name, TEXT.product))} - User Journey Map</h1>
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
          ${stageHeaders || `<div class="journey-stage-header"><span class="journey-stage-index">1</span><span>${escapeHtml(text(null))}</span></div>`}
          ${rows}
        </div>
      </div>
      <div class="journey-transition">
        <h3>${TEXT.transition}</h3>
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
        <h1 class="journey-title">${escapeHtml(text(data.project_name, TEXT.product))}</h1>
        <p>${escapeHtml(text(null))}</p>
      </section>
    `;
  }
  return journeys.map((journey, index) => renderJourney(journey, index, data)).join("");
}

function buildJourneyNav(data) {
  return data.journeys.flatMap((journey, journeyIndex) => {
    const role = text(journey.role || data.primary_role);
    const roleNav = `<a class="preview-nav-item level-1" href="#journey-analysis-section-${journeyIndex}" data-skill="journey-analysis">${escapeHtml(role)}旅程</a>`;
    const stageNav = journey.stages.map((stage, stageIndex) =>
      `<a class="preview-nav-item level-2" href="#journey-analysis-section-${journeyIndex}-stage-${stageIndex}" data-skill="journey-analysis">${escapeHtml(text(stage.name))}</a>`
    );
    return [roleNav, ...stageNav];
  }).join("\n");
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
  const markdown = markdownPathArg ? readFile(path.resolve(process.cwd(), markdownPathArg), "markdown source") : "";

  let contextData = null;
  try {
    const contextRaw = readFile(contextPath, "context json", false);
    if (contextRaw.trim()) contextData = JSON.parse(contextRaw);
  } catch (_) {
    contextData = null;
  }

  const normalizedData = contextData ? normalizeContext(contextData) : null;
  const hasStructuredJourney = Boolean(normalizedData && normalizedData.journeys.length);
  const fallback = hasStructuredJourney ? null : buildMarkdownFallback(markdown);
  const contentHtml = replaceRequired(templateRaw, "<!-- JOURNEY_CONTENT -->", hasStructuredJourney ? buildContent(normalizedData) : fallback.contentHtml);
  const sidebarNav = hasStructuredJourney ? buildJourneyNav(normalizedData) : fallback.navHtml;
  const bootstrapData = JSON.stringify({
    activeSkill: "journey-analysis",
    skills: ["journey-analysis"]
  }, null, 2);

  let html = shellRaw;
  html = html.replace("<title>\u7edf\u4e00\u9884\u89c8</title>", `<title>${TEXT.previewTitle} - ${escapeHtml(normalizedData ? text(normalizedData.project_name, TEXT.product) : TEXT.product)}</title>`);
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
