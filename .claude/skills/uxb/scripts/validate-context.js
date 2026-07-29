"use strict";

const fs = require("fs");
const path = require("path");

const ROOT_FIELDS = [
  "skill",
  "version",
  "generated_at",
  "project_name",
  "artifact_md",
  "baseline_ref",
  "core_experience_decision",
  "experience_impact_scope",
  "experience_goals",
  "information_architecture_directions",
  "interaction_flow_directions",
  "node_explanation_strategies",
  "information_reading_strategies",
  "state_feedback_and_role_continuity",
  "experience_tradeoffs",
  "blueprint_handoff_requirements",
];

const ARRAY_SCHEMAS = {
  experience_goals: {
    prefix: "EG",
    fields: {
      goal: "string",
      priority: "priority",
      pressure: "string",
      conflict_principle: "string",
    },
  },
  information_architecture_directions: {
    prefix: "IA",
    fields: {
      scope: "string",
      direction: "string",
      rationale: "string",
      stable_relationships: "string-array",
    },
  },
  interaction_flow_directions: {
    prefix: "FL",
    fields: {
      task: "string",
      direction: "string",
      sequence_principles: "string-array",
      exception_continuity: "string",
    },
  },
  node_explanation_strategies: {
    prefix: "NE",
    fields: {
      node: "string",
      before: "string-array",
      during: "string-array",
      after: "string-array",
      purpose: "string",
    },
  },
  information_reading_strategies: {
    prefix: "IR",
    fields: {
      scope: "string",
      reading_order: "string-array",
      clarity_principles: "string-array",
      concept_distinctions: "string-array",
    },
  },
  state_feedback_and_role_continuity: {
    prefix: "SF",
    fields: {
      scenario: "string",
      feedback_strategy: "string",
      action_understanding: "string",
      role_continuity: "optional-string",
      cross_node_or_channel_continuity: "optional-string",
    },
  },
  experience_tradeoffs: {
    prefix: "TD",
    fields: {
      topic: "string",
      chosen_direction: "string",
      rejected_directions: "string-array",
      reason: "string",
      impact_scope: "string-array",
    },
  },
  blueprint_handoff_requirements: {
    prefix: "BH",
    fields: {
      requirement: "string",
      purpose: "string",
      must_preserve: "string-array",
      solution_space: "string",
    },
  },
};

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function validateString(value, field, errors, allowEmpty = false) {
  if (typeof value !== "string" || (!allowEmpty && value.trim() === "")) {
    errors.push(`${field} 必须是${allowEmpty ? "" : "非空"}字符串`);
  }
}

function validateStringArray(value, field, errors) {
  if (!Array.isArray(value)) {
    errors.push(`${field} 必须是数组`);
    return;
  }
  value.forEach((item, index) => validateString(item, `${field}[${index}]`, errors));
}

function validateExactObject(value, field, schema, errors) {
  if (!isObject(value)) {
    errors.push(`${field} 必须是对象`);
    return;
  }

  const allowed = new Set(Object.keys(schema));
  for (const key of Object.keys(schema)) {
    if (!Object.prototype.hasOwnProperty.call(value, key)) {
      errors.push(`${field}.${key} 缺失`);
      continue;
    }
    validateType(value[key], `${field}.${key}`, schema[key], errors);
  }
  for (const key of Object.keys(value)) {
    if (!allowed.has(key)) errors.push(`${field}.${key} 不允许出现`);
  }
}

function validateType(value, field, type, errors) {
  if (type === "string") validateString(value, field, errors);
  if (type === "optional-string") validateString(value, field, errors, true);
  if (type === "string-array") validateStringArray(value, field, errors);
  if (type === "priority") {
    validateString(value, field, errors);
    if (typeof value === "string" && !["P0", "P1", "P2"].includes(value)) {
      errors.push(`${field} 只允许 P0、P1、P2`);
    }
  }
}

function validateObjectArray(value, field, config, errors) {
  if (!Array.isArray(value)) {
    errors.push(`${field} 必须是数组`);
    return;
  }

  const ids = new Set();
  const schema = { id: "string", ...config.fields };
  value.forEach((item, index) => {
    const itemField = `${field}[${index}]`;
    validateExactObject(item, itemField, schema, errors);
    if (!isObject(item) || typeof item.id !== "string") return;
    if (!new RegExp(`^${config.prefix}-\\d{3}$`).test(item.id)) {
      errors.push(`${itemField}.id 必须使用 ${config.prefix}-001 格式`);
    }
    if (ids.has(item.id)) errors.push(`${field} 内编号重复：${item.id}`);
    ids.add(item.id);
  });
}

function validate(data) {
  const errors = [];
  if (!isObject(data)) return ["根节点必须是 JSON 对象"];

  const allowedRoot = new Set(ROOT_FIELDS);
  for (const field of ROOT_FIELDS) {
    if (!Object.prototype.hasOwnProperty.call(data, field)) {
      errors.push(`root.${field} 缺失`);
    }
  }
  for (const field of Object.keys(data)) {
    if (!allowedRoot.has(field)) errors.push(`root.${field} 不允许出现`);
  }

  for (const field of ["skill", "version", "generated_at", "project_name", "artifact_md"]) {
    if (field in data) validateString(data[field], field, errors);
  }

  if (data.skill !== "uxb") errors.push("skill 必须为 uxb");
  if (data.version !== "6.0") errors.push("version 必须为 6.0");
  if (data.artifact_md !== "spark-output/uxb_output.md") {
    errors.push("artifact_md 必须为 spark-output/uxb_output.md");
  }

  if ("baseline_ref" in data) {
    validateExactObject(data.baseline_ref, "baseline_ref", {
      artifact_md: "string",
      status: "string",
    }, errors);
    if (isObject(data.baseline_ref)) {
      if (data.baseline_ref.artifact_md !== "spark-output/requirements_baseline.md") {
        errors.push("baseline_ref.artifact_md 路径不正确");
      }
      if (data.baseline_ref.status !== "formal") {
        errors.push("baseline_ref.status 必须为 formal");
      }
    }
  }

  if ("core_experience_decision" in data) {
    validateExactObject(data.core_experience_decision, "core_experience_decision", {
      direction: "string",
      primary_tradeoff: "string",
      blueprint_principle: "string",
    }, errors);
  }

  if ("experience_impact_scope" in data) {
    validateExactObject(data.experience_impact_scope, "experience_impact_scope", {
      tasks: "string-array",
      role_perspectives: "string-array",
      key_nodes: "string-array",
      unaffected_scope: "string-array",
    }, errors);
  }

  for (const [field, config] of Object.entries(ARRAY_SCHEMAS)) {
    if (field in data) validateObjectArray(data[field], field, config, errors);
  }

  return errors;
}

function main() {
  const input = process.argv[2];
  if (!input) {
    console.error("用法：node validate-context.js <uxb.json>");
    process.exit(1);
  }

  const resolved = path.resolve(process.cwd(), input);
  let data;
  try {
    data = JSON.parse(fs.readFileSync(resolved, "utf8"));
  } catch (error) {
    console.error(`JSON 读取或解析失败：${resolved}`);
    console.error(error.message);
    process.exit(1);
  }

  const errors = validate(data);
  if (errors.length > 0) {
    errors.forEach((error) => console.error(error));
    process.exit(1);
  }

  console.log("UXB Context JSON 结构校验通过。");
}

if (require.main === module) main();

module.exports = { ROOT_FIELDS, validate };
