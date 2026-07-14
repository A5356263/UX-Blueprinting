#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const DEFAULTS = {
  templatePath: "shared-workflow/progress-preview.html",
  graphPath: "shared-workflow/skill-graph.json",
  outputPath: "spark-output/progress-preview.html"
};

const slashAlias = {
  "uxb": "/uxb",
  "problem-framing": "/problem-framing",
  "stories": "/stories",
  "journey-analysis": "/journey-analysis",
  "experience-blueprint": "/experience-blueprint",
  "page-spec": "/page-spec",
  "xft-design": "/xft-design",
  "edge": "/edge",
  "check": "/check",
  "board": "/board",
  "knowledge-wiki": "/knowledge-wiki",
  "product-analysis": "/product-analysis",
  "design-strategy": "/design-strategy",
  "journey-metrics": "/journey-metrics",
  "interface-audit": "/interface-audit"
};

const contextPathBySkill = {
  "uxb": "spark-output/context/uxb.json",
  "problem-framing": "spark-output/context/problem-framing.json",
  "stories": "spark-output/context/stories.json",
  "journey-analysis": "spark-output/context/journey-analysis.json",
  "experience-blueprint": "spark-output/context/experience-blueprint.json",
  "page-spec": "spark-output/context/page-spec.json",
  "xft-design": "spark-output/context/xft-design.json",
  "edge": "spark-output/context/edge.json",
  "check": "spark-output/context/check.json",
  "board": "spark-output/context/board.json",
  "knowledge-wiki": "spark-output/context/knowledge-wiki.json",
  "product-analysis": "spark-output/context/product-analysis.json",
  "design-strategy": "spark-output/context/design-strategy.json",
  "journey-metrics": "spark-output/context/journey-metrics.json",
  "interface-audit": "spark-output/context/interface-audit.json"
};

const sectionBySkill = {
  "product-analysis": section("explore", "01", "探索", "Explore", "需求读取、问题诊断与方向收敛", 1),
  "interface-audit": section("explore", "01", "探索", "Explore", "需求读取、问题诊断与方向收敛", 1),
  "design-strategy": section("explore", "01", "探索", "Explore", "需求读取、问题诊断与方向收敛", 1),
  "uxb": section("explore", "01", "探索", "Explore", "需求读取、问题诊断与方向收敛", 1),
  "problem-framing": section("explore", "01", "探索", "Explore", "需求读取、问题诊断与方向收敛", 1),
  "stories": section("define", "02", "定义", "Define", "用户故事、旅程结构与需求补全", 2),
  "journey-analysis": section("define", "02", "定义", "Define", "用户故事、旅程结构与需求补全", 2),
  "experience-blueprint": section("design", "03", "设计", "Design", "方案生成、规格细化与页面落地", 3),
  "board": section("design", "03", "设计", "Design", "方案生成、规格细化与页面落地", 3),
  "page-spec": section("design", "03", "设计", "Design", "方案生成、规格细化与页面落地", 3),
  "xft-design": section("design", "03", "设计", "Design", "方案生成、规格细化与页面落地", 3),
  "edge": section("validate", "04", "验证", "Validate", "异常覆盖、质量校验与度量口径", 4),
  "check": section("validate", "04", "验证", "Validate", "异常覆盖、质量校验与度量口径", 4),
  "journey-metrics": section("validate", "04", "验证", "Validate", "异常覆盖、质量校验与度量口径", 4),
  "knowledge-wiki": section("deliver", "05", "沉淀", "Archive", "产物归档、知识沉淀与后续复用", 5)
};

function section(id, number, nameZh, nameEn, note, order) {
  return { id, number, name_zh: nameZh, name_en: nameEn, note, order };
}

function parseArgs(argv) {
  const options = { ...DEFAULTS };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = argv[i + 1];
    if (arg === "--template" && next) {
      options.templatePath = next;
      i += 1;
    } else if (arg === "--graph" && next) {
      options.graphPath = next;
      i += 1;
    } else if (arg === "--output" && next) {
      options.outputPath = next;
      i += 1;
    }
  }
  return options;
}

function resolveFromRoot(filePath) {
  return path.resolve(process.cwd(), filePath);
}

function existsFromRoot(filePath) {
  return fs.existsSync(resolveFromRoot(filePath));
}

function isReady(skill, doneMap) {
  for (const dep of skill.required || []) {
    if (!doneMap[dep]) return false;
  }
  return true;
}

function previewHint(dependsOn, doneMap, nameMap) {
  for (const dep of dependsOn || []) {
    if (!doneMap[dep]) return nameMap[dep] || null;
  }
  return null;
}

function main() {
  const options = parseArgs(process.argv.slice(2));
  const templateRaw = fs.readFileSync(resolveFromRoot(options.templatePath), "utf8");
  const graph = JSON.parse(fs.readFileSync(resolveFromRoot(options.graphPath), "utf8"));

  const nameMap = {};
  const doneMap = {};
  const sectionsMap = new Map();
  const mainChainSkills = [];

  graph.skills.forEach((skill, index) => {
    nameMap[skill.id] = slashAlias[skill.id] || `/${skill.id}`;
    const contextPath = contextPathBySkill[skill.id];
    doneMap[skill.id] = Boolean(contextPath && existsFromRoot(contextPath));

    if (skill.type !== "infrastructure" && skill.phase !== null && skill.phase !== undefined) {
      mainChainSkills.push({
        id: skill.id,
        phase: Number(skill.phase),
        required: skill.required || [],
        order: index
      });
    }

    const sectionMeta = sectionBySkill[skill.id] || section("design", "03", "设计", "Design", "方案生成、规格细化与页面落地", 3);
    if (!sectionsMap.has(sectionMeta.id)) {
      sectionsMap.set(sectionMeta.id, { ...sectionMeta, skills: [] });
    }
    sectionsMap.get(sectionMeta.id).skills.push(skill);
  });

  const currentSkill = mainChainSkills
    .sort((a, b) => a.phase - b.phase || a.order - b.order)
    .find((skill) => !doneMap[skill.id] && isReady(skill, doneMap));
  const currentSkillId = currentSkill ? currentSkill.id : null;

  const sections = Array.from(sectionsMap.values())
    .sort((a, b) => a.order - b.order)
    .map((sectionMeta) => ({
      id: sectionMeta.id,
      number: sectionMeta.number,
      name_zh: sectionMeta.name_zh,
      name_en: sectionMeta.name_en,
      note: sectionMeta.note,
      skills: sectionMeta.skills.map((skill) => {
        let status = "idle";
        if (doneMap[skill.id]) status = "done";
        else if (currentSkillId === skill.id) status = "current";
        else if (isReady(skill, doneMap)) status = "ready";

        return {
          id: skill.id,
          name_zh: skill.name_zh,
          slash: nameMap[skill.id],
          status,
          hint_dep: previewHint(skill.required || [], doneMap, nameMap),
          standalone_usable: Boolean(skill.standalone_usable),
          standalone_note: skill.standalone_note || null
        };
      })
    }));

  const state = {
    generated_at: formatNow(new Date()),
    sections
  };

  const injectScript = `<script>window.__PREVIEW_STATE__ = ${JSON.stringify(state, null, 2)};</script>`;
  const html = templateRaw.replace("<!--__PREVIEW_STATE_INJECT__-->", injectScript);
  const outputPath = resolveFromRoot(options.outputPath);

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, html, "utf8");
  console.log(`OK: ${outputPath}`);
}

function formatNow(date) {
  const pad = (value) => String(value).padStart(2, "0");
  return [
    date.getFullYear(),
    "-",
    pad(date.getMonth() + 1),
    "-",
    pad(date.getDate()),
    " ",
    pad(date.getHours()),
    ":",
    pad(date.getMinutes()),
    ":",
    pad(date.getSeconds())
  ].join("");
}

try {
  main();
} catch (error) {
  console.warn(`Progress preview refresh skipped: ${error.message}`);
}
