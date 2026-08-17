#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const DEFAULTS = {
  templatePath: "shared-workflow/progress-preview.html",
  graphPath: "shared-workflow/skill-graph.json",
  outputPath: "spark-output/progress-preview.html"
};

const slashAlias = {
  "prd-review": "/prd-review",
  "uxb": "/uxb",
  "problem-framing": "/problem-framing",
  "stories": "/stories",
  "journey-analysis": "/journey-analysis",
  "experience-blueprint": "/experience-blueprint",
  "solution-swimlane": "/solution-swimlane",
  "page-spec": "/page-spec",
  "edge": "/edge",
  "board": "/board",
  "knowledge-wiki": "/knowledge-wiki",
  "journey-metrics": "/journey-metrics"
};

const contextPathBySkill = {
  "prd-review": "spark-output/context/requirements-baseline.json",
  "uxb": "spark-output/context/uxb.json",
  "problem-framing": "spark-output/context/problem-framing.json",
  "stories": "spark-output/context/stories.json",
  "journey-analysis": "spark-output/context/journey-analysis.json",
  "experience-blueprint": "spark-output/context/experience-blueprint.json",
  "solution-swimlane": "spark-output/solution-swimlane/solution_swimlane.html",
  "page-spec": "spark-output/context/page-spec.json",
  "edge": "spark-output/context/edge.json",
  "board": "spark-output/context/board.json",
  "knowledge-wiki": "spark-output/context/knowledge-wiki.json",
  "journey-metrics": "spark-output/context/journey-metrics.json"
};

const sectionBySkill = {
  "prd-review": section("requirements-problem", "01", "需求与问题", "Requirements & Problem", "审核需求或基于问题形成业务方案", 1),
  "problem-framing": section("requirements-problem", "01", "需求与问题", "Requirements & Problem", "审核需求或基于问题形成业务方案", 1),
  "stories": section("task-journey", "02", "任务与旅程", "Task & Journey", "拆解用户任务，梳理用户完成过程", 2),
  "journey-analysis": section("task-journey", "02", "任务与旅程", "Task & Journey", "拆解用户任务，梳理用户完成过程", 2),
  "uxb": section("experience-design", "03", "体验与设计", "Experience & Design", "形成体验策略并输出交互方案", 3),
  "experience-blueprint": section("experience-design", "03", "体验与设计", "Experience & Design", "形成体验策略并输出交互方案", 3),
  "solution-swimlane": section("experience-design", "03", "体验与设计", "Experience & Design", "形成体验策略并输出交互方案", 3),
  "page-spec": section("page-build", "04", "页面生成", "Page Build", "提取设计元素", 4),
  "journey-metrics": section("validate", "05", "验证", "Validate", "定义关键节点的埋点与度量口径", 5),
  "knowledge-wiki": section("deliver", "06", "沉淀", "Archive", "产物归档、知识沉淀与后续复用", 6)
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
  const enhancementMap = new Map();
  const mainChainSet = new Set(graph.main_chain || []);

  for (const group of graph.enhancements || []) {
    for (const skillId of group.skills || []) {
      enhancementMap.set(skillId, group.before);
    }
  }

  graph.skills.forEach((skill, index) => {
    nameMap[skill.id] = slashAlias[skill.id] || `/${skill.id}`;
    const contextPath = contextPathBySkill[skill.id];
    doneMap[skill.id] = Boolean(contextPath && existsFromRoot(contextPath));

    if (skill.preview_hidden === true) return;

    const sectionMeta = sectionBySkill[skill.id] || section("experience-design", "03", "体验与设计", "Experience & Design", "形成体验策略并输出交互方案", 3);
    if (!sectionsMap.has(sectionMeta.id)) {
      sectionsMap.set(sectionMeta.id, { ...sectionMeta, skills: [] });
    }
    sectionsMap.get(sectionMeta.id).skills.push(skill);
  });

  const currentSkillId = (graph.main_chain || []).find((skillId) => !doneMap[skillId]) || null;

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
        else if (mainChainSet.has(skill.id)) status = "idle";
        else if (isReady(skill, doneMap)) status = "ready";

        return {
          id: skill.id,
          name_zh: skill.name_zh,
          slash: nameMap[skill.id],
          status,
          hint_dep: previewHint(skill.required || [], doneMap, nameMap),
          is_enhancement: enhancementMap.has(skill.id),
          enhances_before: enhancementMap.get(skill.id) || null,
          standalone_usable: Boolean(skill.standalone_usable),
          standalone_note: skill.standalone_note || null
        };
      })
    }));

  const state = {
    generated_at: formatNow(new Date()),
    main_chain: graph.main_chain || [],
    enhancements: graph.enhancements || [],
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
