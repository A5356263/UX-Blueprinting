"use strict";

const fs = require("fs");
const path = require("path");

const ROOT_FIELDS = [
  "skill",
  "version",
  "generated_at",
  "project_name",
  "artifact_md",
  "experience_scope",
  "task_experience_decisions",
  "cross_stage_decisions",
  "state_recovery_decisions",
  "blueprint_requirements",
  "upstream_trace",
];

const ARRAY_SCHEMAS = {
  task_experience_decisions: {
    prefix: "TE",
    required: {
      task: "string",
      roles: "nonempty-string-array",
      business_objects: "nonempty-string-array",
      business_nodes: "nonempty-string-array",
      perceived_stage: "string",
      orchestration_actions: "orchestration-array",
      orchestration_reason: "string",
      experience_breakpoint: "string",
      user_must_understand: "nonempty-string-array",
      experience_decision: "string",
      blueprint_requirements: "nonempty-string-array",
    },
    optional: {
      information_order: "nonempty-string-array",
      explanation_timing: "explanation-timing",
      state_result_requirements: "nonempty-string-array",
      continuity_requirements: "nonempty-string-array",
    },
  },
  cross_stage_decisions: {
    prefix: "CS",
    required: {
      task: "string",
      from_stage: "string",
      to_stage: "string",
      transition_trigger: "string",
      context_to_preserve: "nonempty-string-array",
      transition_decision: "string",
      blueprint_requirements: "nonempty-string-array",
    },
    optional: {},
  },
  state_recovery_decisions: {
    prefix: "SR",
    required: {
      task: "string",
      business_states: "nonempty-string-array",
      user_visible_meaning: "string",
      result_or_next_action: "string",
      experience_decision: "string",
      blueprint_requirements: "nonempty-string-array",
    },
    optional: {},
  },
  blueprint_requirements: {
    prefix: "BR",
    required: {
      task: "string",
      roles: "nonempty-string-array",
      perceived_stage: "string",
      requirement: "string",
      purpose: "string",
      must_preserve: "nonempty-string-array",
    },
    optional: {},
  },
  upstream_trace: {
    prefix: "UT",
    required: {
      source_type: "source-type",
      source_name: "string",
      status: "formal-status",
      used_for: "string-array",
    },
    optional: {
      source_path: "string",
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

function validateStringArray(value, field, errors, requireNonEmpty = false) {
  if (!Array.isArray(value)) {
    errors.push(`${field} 必须是数组`);
    return;
  }
  if (requireNonEmpty && value.length === 0) {
    errors.push(`${field} 不得为空数组`);
  }
  value.forEach((item, index) => validateString(item, `${field}[${index}]`, errors));
}

function validateExplanationTiming(value, field, errors) {
  if (!isObject(value)) {
    errors.push(`${field} 必须是对象`);
    return;
  }
  const allowed = new Set(["before", "during", "after"]);
  if (Object.keys(value).length === 0) errors.push(`${field} 不得为空对象`);
  for (const key of Object.keys(value)) {
    if (!allowed.has(key)) {
      errors.push(`${field}.${key} 不允许出现`);
      continue;
    }
    validateStringArray(value[key], `${field}.${key}`, errors, true);
  }
}

function validateStructuredObject(value, field, required, optional, errors) {
  if (!isObject(value)) {
    errors.push(`${field} 必须是对象`);
    return;
  }

  const allowed = new Set([...Object.keys(required), ...Object.keys(optional)]);
  for (const key of Object.keys(required)) {
    if (!Object.prototype.hasOwnProperty.call(value, key)) {
      errors.push(`${field}.${key} 缺失`);
      continue;
    }
    validateType(value[key], `${field}.${key}`, required[key], errors);
  }
  for (const key of Object.keys(optional)) {
    if (Object.prototype.hasOwnProperty.call(value, key)) {
      validateType(value[key], `${field}.${key}`, optional[key], errors);
    }
  }
  for (const key of Object.keys(value)) {
    if (!allowed.has(key)) errors.push(`${field}.${key} 不允许出现`);
  }
}

function validateType(value, field, type, errors) {
  if (type === "string") validateString(value, field, errors);
  if (type === "string-array") validateStringArray(value, field, errors);
  if (type === "nonempty-string-array") validateStringArray(value, field, errors, true);
  if (type === "explanation-timing") validateExplanationTiming(value, field, errors);
  if (type === "orchestration-array") {
    validateStringArray(value, field, errors, true);
    if (Array.isArray(value)) {
      for (const item of value) {
        if (typeof item === "string" && !["retain", "merge", "split", "reorder"].includes(item)) {
          errors.push(`${field} 包含不允许的编排动作：${item}`);
        }
      }
    }
  }
  if (type === "source-type") {
    validateString(value, field, errors);
    if (typeof value === "string" && ![
      "requirements_baseline",
      "business_knowledge",
      "design_guideline",
      "interaction_pattern",
    ].includes(value)) {
      errors.push(`${field} 不是允许的来源类型`);
    }
  }
  if (type === "formal-status") {
    validateString(value, field, errors);
    if (value !== "formal") errors.push(`${field} 必须为 formal`);
  }
}

function validateObjectArray(value, field, config, errors) {
  if (!Array.isArray(value)) {
    errors.push(`${field} 必须是数组`);
    return;
  }

  const ids = new Set();
  const required = { id: "string", ...config.required };
  value.forEach((item, index) => {
    const itemField = `${field}[${index}]`;
    validateStructuredObject(item, itemField, required, config.optional, errors);
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
  if (data.version !== "8.0") errors.push("version 必须为 8.0");

  if ("experience_scope" in data) {
    validateStructuredObject(data.experience_scope, "experience_scope", {
      tasks: "string-array",
      roles: "string-array",
      business_objects: "string-array",
      key_nodes: "string-array",
      relevant_states: "string-array",
      relevant_results: "string-array",
      unaffected_scope: "string-array",
    }, {}, errors);
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
