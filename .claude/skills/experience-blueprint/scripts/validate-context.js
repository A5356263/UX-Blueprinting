"use strict";

const fs = require("fs");
const path = require("path");

const ROOT_KEYS = [
  "skill", "version", "generated_at", "project_name", "artifact_md", "source_refs",
  "upstream_contract",
  "information_architecture",
  "critical_design_judgments", "journey_consumption", "interaction_overview",
  "main_flow", "sub_flows", "exceptions", "surfaces", "states", "feedbacks",
  "upstream_trace",
];
const FORBIDDEN_KEYS = new Set([
  "source_status", "source_anchor", "md_anchor", "end_type", "end_target",
  "lanes", "nodes", "edges", "coverage_manifest",
]);

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function exact(value, keys, field, errors) {
  if (!isObject(value)) {
    errors.push(`${field} 必须是对象`);
    return false;
  }
  const allowed = new Set(keys);
  keys.forEach((key) => {
    if (!Object.prototype.hasOwnProperty.call(value, key)) errors.push(`${field}.${key} 缺失`);
  });
  Object.keys(value).forEach((key) => {
    if (!allowed.has(key)) errors.push(`${field}.${key} 不允许出现`);
  });
  return true;
}

function string(value, field, errors) {
  if (typeof value !== "string" || !value.trim()) errors.push(`${field} 必须是非空字符串`);
}

function array(value, field, errors) {
  if (!Array.isArray(value)) {
    errors.push(`${field} 必须是数组`);
    return false;
  }
  return true;
}

function strings(value, field, errors) {
  if (!array(value, field, errors)) return;
  value.forEach((item, index) => string(item, `${field}[${index}]`, errors));
}

function collection(items, field, keys, errors, callback) {
  if (!array(items, field, errors)) return;
  items.forEach((item, index) => {
    const itemPath = `${field}[${index}]`;
    if (!exact(item, keys, itemPath, errors)) return;
    callback(item, itemPath);
  });
}

function rejectForbiddenKeys(value, field, errors) {
  if (Array.isArray(value)) {
    value.forEach((item, index) => rejectForbiddenKeys(item, `${field}[${index}]`, errors));
    return;
  }
  if (!isObject(value)) return;
  Object.entries(value).forEach(([key, child]) => {
    if (FORBIDDEN_KEYS.has(key) || /_id$/.test(key)) errors.push(`${field}.${key} 为禁止字段`);
    rejectForbiddenKeys(child, `${field}.${key}`, errors);
  });
}

function validate(data) {
  const errors = [];
  if (!exact(data, ROOT_KEYS, "root", errors)) return errors;
  rejectForbiddenKeys(data, "root", errors);

  if (data.skill !== "experience-blueprint") errors.push("skill 必须为 experience-blueprint");
  if (data.version !== "4.0") errors.push("version 必须为 4.0");
  if (data.artifact_md !== "spark-output/experience_blueprint.md") {
    errors.push("artifact_md 必须为 spark-output/experience_blueprint.md");
  }
  string(data.generated_at, "generated_at", errors);
  string(data.project_name, "project_name", errors);
  strings(data.source_refs, "source_refs", errors);

  if (exact(
    data.upstream_contract,
    ["mode", "requirements_baseline_refs", "uxb_refs"],
    "upstream_contract",
    errors,
  )) {
    string(data.upstream_contract.mode, "upstream_contract.mode", errors);
    strings(
      data.upstream_contract.requirements_baseline_refs,
      "upstream_contract.requirements_baseline_refs",
      errors,
    );
    strings(data.upstream_contract.uxb_refs, "upstream_contract.uxb_refs", errors);

    const modes = new Set(["baseline-mode", "uxb-mode", "framing-mode"]);
    if (!modes.has(data.upstream_contract.mode)) {
      errors.push("upstream_contract.mode 不是允许的模式");
    }

    const baselineRefs = [
      "spark-output/requirements_baseline.md",
      "spark-output/context/requirements-baseline.json",
    ];
    const uxbRefs = [
      "spark-output/uxb_output.md",
      "spark-output/context/uxb.json",
    ];
    const sameRefs = (actual, expected) =>
      Array.isArray(actual) &&
      actual.length === expected.length &&
      expected.every((item) => actual.includes(item));

    if (["baseline-mode", "uxb-mode"].includes(data.upstream_contract.mode) &&
        !sameRefs(data.upstream_contract.requirements_baseline_refs, baselineRefs)) {
      errors.push("主链模式必须包含完整需求基线引用");
    }
    if (data.upstream_contract.mode === "baseline-mode" &&
        (!Array.isArray(data.upstream_contract.uxb_refs) ||
         data.upstream_contract.uxb_refs.length !== 0)) {
      errors.push("baseline-mode 的 uxb_refs 必须为空数组");
    }
    if (data.upstream_contract.mode === "uxb-mode" &&
        !sameRefs(data.upstream_contract.uxb_refs, uxbRefs)) {
      errors.push("uxb-mode 必须包含完整 UXB 引用");
    }
    if (data.upstream_contract.mode === "framing-mode" &&
        ((!Array.isArray(data.upstream_contract.requirements_baseline_refs) ||
          data.upstream_contract.requirements_baseline_refs.length !== 0) ||
         (!Array.isArray(data.upstream_contract.uxb_refs) ||
          data.upstream_contract.uxb_refs.length !== 0))) {
      errors.push("framing-mode 不得写入需求基线或 UXB 引用");
    }
  }

  if (exact(data.information_architecture, ["primary_navigation", "site_tree"], "information_architecture", errors)) {
    collection(
      data.information_architecture.primary_navigation, "information_architecture.primary_navigation",
      ["label", "route", "icon_hint", "access", "children"], errors,
      (item, itemPath) => {
        ["label", "route", "icon_hint", "access"].forEach((key) =>
          string(item[key], `${itemPath}.${key}`, errors));
        if (!Array.isArray(item.children)) errors.push(`${itemPath}.children 必须是数组`);
      },
    );
    if (!Array.isArray(data.information_architecture.site_tree)) {
      errors.push("information_architecture.site_tree 必须是数组");
    } else {
      data.information_architecture.site_tree.forEach((node, index) => {
        const nodePath = `information_architecture.site_tree[${index}]`;
        if (!exact(node, ["label", "route", "access", "surface_type", "children"], nodePath, errors)) return;
        ["label", "access", "surface_type"].forEach((key) => string(node[key], `${nodePath}.${key}`, errors));
        if (node.route !== null) string(node.route, `${nodePath}.route`, errors);
        if (!Array.isArray(node.children)) errors.push(`${nodePath}.children 必须是数组`);
      });
    }
  }

  collection(
    data.critical_design_judgments, "critical_design_judgments",
    ["judgment", "impacts", "recommended_approach", "not_recommended"],
    errors,
    (item, itemPath) => {
      string(item.judgment, `${itemPath}.judgment`, errors);
      strings(item.impacts, `${itemPath}.impacts`, errors);
      ["recommended_approach", "not_recommended"].forEach((key) =>
        string(item[key], `${itemPath}.${key}`, errors));
    },
  );
  collection(
    data.journey_consumption, "journey_consumption",
    ["type", "finding", "source_stage", "blueprint_target"], errors,
    (item, itemPath) => ["type", "finding", "source_stage", "blueprint_target"].forEach((key) =>
      string(item[key], `${itemPath}.${key}`, errors)),
  );
  collection(
    data.interaction_overview, "interaction_overview",
    ["name", "path_type", "steps", "branches"], errors,
    (item, itemPath) => {
      ["name", "path_type"].forEach((key) => string(item[key], `${itemPath}.${key}`, errors));
      strings(item.steps, `${itemPath}.steps`, errors);
      strings(item.branches, `${itemPath}.branches`, errors);
    },
  );
  collection(
    data.main_flow, "main_flow",
    ["name", "user_action", "system_feedback", "pre_explanations", "copy_suggestions", "next_step"],
    errors,
    (item, itemPath) => {
      ["name", "user_action", "system_feedback", "next_step"].forEach((key) =>
        string(item[key], `${itemPath}.${key}`, errors));
      strings(item.pre_explanations, `${itemPath}.pre_explanations`, errors);
      strings(item.copy_suggestions, `${itemPath}.copy_suggestions`, errors);
    },
  );
  collection(
    data.sub_flows, "sub_flows",
    ["name", "trigger_condition", "user_action", "system_feedback", "pre_explanations",
      "copy_suggestions", "next_step"],
    errors,
    (item, itemPath) => {
      ["name", "trigger_condition", "user_action", "system_feedback", "next_step"].forEach((key) =>
        string(item[key], `${itemPath}.${key}`, errors));
      strings(item.pre_explanations, `${itemPath}.pre_explanations`, errors);
      strings(item.copy_suggestions, `${itemPath}.copy_suggestions`, errors);
    },
  );
  collection(
    data.exceptions, "exceptions",
    ["name", "timing", "trigger_condition", "basis", "feedback_type", "system_feedback",
      "user_next_step", "recovery_path"],
    errors,
    (item, itemPath) => {
      ["name", "timing", "trigger_condition", "basis", "feedback_type", "system_feedback",
        "user_next_step", "recovery_path"].forEach((key) =>
        string(item[key], `${itemPath}.${key}`, errors));
    },
  );

  const surfaceKeys = [
    "name", "goal", "entry_condition", "markdown_heading", "structure_notes", "fields",
    "validation_rules", "state_feedback", "exception_structure_changes", "copy_items",
    "buttons", "success_feedback", "failure_feedback",
  ];
  if (exact(data.surfaces, ["pages", "modals", "drawers"], "surfaces", errors)) {
    for (const kind of ["pages", "modals", "drawers"]) {
      collection(data.surfaces[kind], `surfaces.${kind}`, surfaceKeys, errors, (item, itemPath) => {
        ["name", "goal", "entry_condition", "markdown_heading"].forEach((key) =>
          string(item[key], `${itemPath}.${key}`, errors));
        surfaceKeys.slice(4).forEach((key) => strings(item[key], `${itemPath}.${key}`, errors));
      });
    }
  }

  collection(
    data.states, "states",
    ["state", "meaning", "applies_to", "user_actions", "feedback"], errors,
    (item, itemPath) => {
      ["state", "meaning", "applies_to", "feedback"].forEach((key) =>
        string(item[key], `${itemPath}.${key}`, errors));
      strings(item.user_actions, `${itemPath}.user_actions`, errors);
    },
  );
  collection(
    data.feedbacks, "feedbacks", ["scenario", "type", "copy"], errors,
    (item, itemPath) => ["scenario", "type", "copy"].forEach((key) =>
      string(item[key], `${itemPath}.${key}`, errors)),
  );
  collection(
    data.upstream_trace, "upstream_trace",
    ["upstream_judgment", "experience_meaning", "design_decision", "blueprint_target"], errors,
    (item, itemPath) => ["upstream_judgment", "experience_meaning", "design_decision", "blueprint_target"]
      .forEach((key) => string(item[key], `${itemPath}.${key}`, errors)),
  );

  if (Array.isArray(data.critical_design_judgments) && !data.critical_design_judgments.length) {
    errors.push("critical_design_judgments 不得为空");
  }
  if (Array.isArray(data.interaction_overview) && !data.interaction_overview.length) {
    errors.push("interaction_overview 不得为空");
  }
  if (Array.isArray(data.main_flow) && !data.main_flow.length) errors.push("main_flow 不得为空");
  if (isObject(data.surfaces)) {
    const total = ["pages", "modals", "drawers"]
      .reduce((sum, key) => sum + (Array.isArray(data.surfaces[key]) ? data.surfaces[key].length : 0), 0);
    if (!total) errors.push("surfaces 至少包含一个页面、弹窗或抽屉");
  }
  return errors;
}

function main() {
  const input = process.argv[2];
  if (!input) {
    console.error("缺少 context_json_path");
    process.exit(1);
  }
  const resolved = path.resolve(process.cwd(), input);
  let data;
  try {
    data = JSON.parse(fs.readFileSync(resolved, "utf8").replace(/^\uFEFF/, ""));
  } catch (error) {
    console.error(`JSON 读取或解析失败：${resolved}`);
    console.error(error.message);
    process.exit(1);
  }
  const errors = validate(data);
  if (errors.length) {
    errors.forEach((error) => console.error(error));
    process.exit(1);
  }
  console.log("experience-blueprint context valid");
}

if (require.main === module) main();
module.exports = { validate };
