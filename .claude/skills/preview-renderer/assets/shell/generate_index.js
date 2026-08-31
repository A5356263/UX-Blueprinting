"use strict";

const fs = require("fs");
const path = require("path");

const PRODUCTS = [
  {
    id: "prd-review",
    label: "需求基线",
    purpose: "审核闭环后的正式需求事实与待定案事项",
    markdown: "spark-output/requirements_baseline.md",
    context: "spark-output/context/requirements-baseline.json",
    script: ".claude/skills/preview-renderer/assets/skills/prd-review/generate_preview.js",
    preview: "spark-output/preview/requirements_baseline_preview.html"
  },
  {
    id: "uxb",
    label: "业务蓝图",
    purpose: "需求定案与业务边界的正式入口",
    markdown: "spark-output/uxb_output.md",
    context: "spark-output/context/uxb.json",
    script: ".claude/skills/preview-renderer/assets/skills/uxb/generate_preview.js",
    preview: "spark-output/preview/uxb_preview.html"
  },
  {
    id: "problem-framing",
    label: "问题与业务方案",
    purpose: "基于问题形成并确定主推荐业务方案",
    markdown: "spark-output/problem_framing.md",
    context: "spark-output/context/problem-framing.json",
    script: ".claude/skills/preview-renderer/assets/skills/problem-framing/generate_preview.js",
    preview: "spark-output/preview/problem_framing_preview.html"
  },
  {
    id: "stories",
    label: "用户故事",
    purpose: "把上游结论转成任务单元与验收口径",
    markdown: "spark-output/stories.md",
    context: "spark-output/context/stories.json",
    script: ".claude/skills/preview-renderer/assets/skills/stories/generate_preview.js",
    preview: "spark-output/preview/stories_preview.html"
  },
  {
    id: "journey-analysis",
    label: "角色旅程",
    purpose: "展开角色阶段、触点、断点和机会点",
    markdown: "spark-output/journey_analysis.md",
    context: "spark-output/context/journey-analysis.json",
    script: ".claude/skills/preview-renderer/assets/skills/journey-analysis/generate_preview.js",
    preview: "spark-output/preview/journey_analysis_preview.html"
  },
  {
    id: "experience-blueprint",
    label: "体验蓝图",
    purpose: "把上游结论展开为交互流程、页面和状态方案",
    markdown: "spark-output/experience_blueprint.md",
    context: "spark-output/context/experience-blueprint.json",
    script: ".claude/skills/preview-renderer/assets/skills/experience-blueprint/generate_preview.js",
    preview: "spark-output/preview/experience_blueprint_preview.html"
  },
  {
    id: "page-spec",
    label: "页面设计文档",
    purpose: "提取页面实体、结构、状态和页面生成所需事实",
    markdown: "spark-output/page_spec.md",
    context: "spark-output/context/page-spec.json",
    script: ".claude/skills/preview-renderer/assets/skills/page-spec/generate_preview.js",
    preview: "spark-output/preview/page_spec_preview.html"
  }
];

function exists(root, filePath) {
  return fs.existsSync(path.resolve(root, filePath));
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function stateFor(product, root) {
  const markdownExists = exists(root, product.markdown);
  const contextExists = exists(root, product.context);
  const scriptExists = exists(root, product.script);
  const previewExists = exists(root, product.preview);
  let status = "missing_markdown";

  if (markdownExists && previewExists) status = "generated";
  else if (markdownExists && scriptExists) status = "missing_preview";
  else if (markdownExists && !scriptExists) status = "missing_script";

  return {
    ...product,
    markdownExists,
    contextExists,
    scriptExists,
    previewExists,
    canGenerate: markdownExists && scriptExists,
    status
  };
}

function statusLabel(status) {
  if (status === "generated") return "已生成";
  if (status === "missing_preview") return "待生成预览";
  if (status === "missing_script") return "缺少渲染脚本";
  return "未生成正式产物";
}

function statusClass(status) {
  if (status === "generated") return "is-ready";
  if (status === "missing_preview") return "is-pending";
  if (status === "missing_script") return "is-blocked";
  return "is-empty";
}

function boolText(value) {
  return value ? "已存在" : "未检测到";
}

function renderCard(item) {
  const href = item.status === "generated"
    ? `./${path.basename(item.preview)}`
    : "";
  const action = item.status === "generated"
    ? `<a class="preview-card-action" href="${escapeHtml(href)}">打开预览</a>`
    : `<span class="preview-card-action is-disabled">${escapeHtml(statusLabel(item.status))}</span>`;

  return `
    <article class="preview-card ${statusClass(item.status)}">
      <div class="preview-card-topline">
        <span class="preview-card-kicker">${escapeHtml(item.id)}</span>
        <span class="preview-card-status">${escapeHtml(statusLabel(item.status))}</span>
      </div>
      <h2>${escapeHtml(item.label)}</h2>
      <p class="preview-card-purpose">${escapeHtml(item.purpose)}</p>
      <dl class="preview-card-meta">
        <div><dt>正式 Markdown</dt><dd>${escapeHtml(boolText(item.markdownExists))}</dd></div>
        <div><dt>Context JSON</dt><dd>${escapeHtml(boolText(item.contextExists))}</dd></div>
        <div><dt>HTML 预览</dt><dd>${escapeHtml(boolText(item.previewExists))}</dd></div>
      </dl>
      ${action}
    </article>
  `;
}

function renderHtml(items) {
  const generated = items.filter((item) => item.status === "generated").length;
  const pending = items.filter((item) => item.status === "missing_preview").length;
  const missing = items.filter((item) => item.status === "missing_markdown").length;

  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>预览目录</title>
  <style>
    :root {
      --bg: #f5f4ed;
      --panel: #fbfaf6;
      --panel-soft: #f0eee6;
      --line: #e2ded2;
      --line-strong: #d2cab8;
      --text: #2c2b27;
      --muted: #6f6c63;
      --soft: #8d897f;
      --accent: #1f6b5b;
      --accent-soft: #e3f1eb;
      --warn: #8a5a14;
      --warn-soft: #f7ead2;
      --empty: #77746a;
      --shadow: 0 18px 45px rgba(40, 36, 26, 0.08);
      --radius: 18px;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: "PingFang SC", "Microsoft YaHei", "Segoe UI", system-ui, sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at 12% 8%, rgba(31, 107, 91, 0.12), transparent 28%),
        linear-gradient(180deg, #fbfaf6 0%, var(--bg) 100%);
      min-height: 100vh;
    }

    .preview-index {
      max-width: 1180px;
      margin: 0 auto;
      padding: 56px 28px 72px;
    }

    .preview-hero {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 28px;
      align-items: end;
      margin-bottom: 28px;
    }

    .preview-eyebrow {
      margin: 0 0 10px;
      color: var(--accent);
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    h1 {
      margin: 0;
      color: #173f36;
      font-size: clamp(30px, 5vw, 52px);
      line-height: 1.05;
      letter-spacing: -0.04em;
    }

    .preview-lead {
      max-width: 620px;
      margin: 16px 0 0;
      color: var(--muted);
      font-size: 16px;
      line-height: 1.7;
    }

    .preview-stats {
      display: grid;
      grid-template-columns: repeat(3, 110px);
      gap: 10px;
    }

    .preview-stat {
      background: rgba(251, 250, 246, 0.82);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 14px 16px;
      box-shadow: 0 10px 26px rgba(40, 36, 26, 0.05);
    }

    .preview-stat strong {
      display: block;
      color: var(--accent);
      font-size: 28px;
      line-height: 1;
      margin-bottom: 8px;
    }

    .preview-stat span {
      color: var(--soft);
      font-size: 13px;
    }

    .preview-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 18px;
    }

    .preview-card {
      min-height: 310px;
      display: flex;
      flex-direction: column;
      background: rgba(251, 250, 246, 0.94);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 22px;
      box-shadow: var(--shadow);
      transition: transform 0.16s ease, border-color 0.16s ease, box-shadow 0.16s ease;
    }

    .preview-card.is-ready:hover {
      transform: translateY(-3px);
      border-color: rgba(31, 107, 91, 0.45);
      box-shadow: 0 24px 52px rgba(31, 107, 91, 0.12);
    }

    .preview-card-topline {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      margin-bottom: 18px;
    }

    .preview-card-kicker {
      color: var(--soft);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.05em;
    }

    .preview-card-status {
      border-radius: 999px;
      padding: 4px 9px;
      background: var(--panel-soft);
      color: var(--empty);
      font-size: 12px;
      font-weight: 700;
    }

    .is-ready .preview-card-status {
      background: var(--accent-soft);
      color: var(--accent);
    }

    .is-pending .preview-card-status {
      background: var(--warn-soft);
      color: var(--warn);
    }

    .preview-card h2 {
      margin: 0 0 10px;
      color: #1f2d29;
      font-size: 24px;
      letter-spacing: -0.02em;
    }

    .preview-card-purpose {
      min-height: 52px;
      margin: 0 0 18px;
      color: var(--muted);
      line-height: 1.6;
    }

    .preview-card-meta {
      display: grid;
      gap: 9px;
      margin: 0 0 22px;
    }

    .preview-card-meta div {
      display: flex;
      justify-content: space-between;
      gap: 14px;
      padding: 9px 0;
      border-bottom: 1px solid rgba(226, 222, 210, 0.72);
    }

    .preview-card-meta dt {
      color: var(--soft);
      font-size: 13px;
    }

    .preview-card-meta dd {
      margin: 0;
      color: var(--text);
      font-size: 13px;
      font-weight: 700;
    }

    .preview-card-action {
      display: inline-flex;
      justify-content: center;
      align-items: center;
      min-height: 40px;
      margin-top: auto;
      border-radius: 999px;
      background: var(--accent);
      color: white;
      text-decoration: none;
      font-size: 14px;
      font-weight: 700;
    }

    .preview-card-action.is-disabled {
      background: var(--panel-soft);
      color: var(--muted);
      border: 1px solid var(--line);
    }

    @media (max-width: 960px) {
      .preview-hero { grid-template-columns: 1fr; }
      .preview-stats { grid-template-columns: repeat(3, 1fr); }
      .preview-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }

    @media (max-width: 640px) {
      .preview-index { padding: 34px 16px 48px; }
      .preview-grid { grid-template-columns: 1fr; }
      .preview-stats { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main class="preview-index">
    <section class="preview-hero">
      <div>
        <p class="preview-eyebrow">Preview Index</p>
        <h1>预览目录</h1>
        <p class="preview-lead">这里仅展示正式 Markdown 产物对应的 HTML 预览状态。点击已生成的卡片进入对应预览页；预览不会改变主链状态。</p>
      </div>
      <div class="preview-stats" aria-label="预览状态统计">
        <div class="preview-stat"><strong>${generated}</strong><span>已生成</span></div>
        <div class="preview-stat"><strong>${pending}</strong><span>待生成</span></div>
        <div class="preview-stat"><strong>${missing}</strong><span>未产出</span></div>
      </div>
    </section>
    <section class="preview-grid" aria-label="预览产物">
      ${items.map(renderCard).join("\n")}
    </section>
  </main>
</body>
</html>`;
}

function main() {
  const root = process.cwd();
  const outputPath = path.resolve(root, "spark-output/preview/index.html");
  const items = PRODUCTS.map((product) => stateFor(product, root));

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, renderHtml(items), "utf8");
  console.log(`preview index generated: ${outputPath}`);
}

main();
