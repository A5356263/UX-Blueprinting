"use strict";

const fs = require("fs");
const path = require("path");

const ROOT_SCHEMA = {
  skill: "string",
  version: "string",
  generated_at: "string",
  project_name: "string",
  artifact_md: "string",
  source_refs: ["string"],
  key_design_judgments: [{
    judgment: "string",
    impact: "string",
    recommended_approach: "string",
    not_recommended: "string",
    open_question: "string",
  }],
  input_summary: {
    raw_request: "string",
    confirmed_facts: ["string"],
    explicit_constraints: ["string"],
    missing_information: ["string"],
  },
  business_scenario_judgment: {
    scenario: "string",
    role: "string",
    task: "string",
    value: "string",
  },
  viability_judgment: {
    is_valid: "string",
    reason: "string",
    blocking_issues: ["string"],
    assumptions: ["string"],
  },
  business_boundary: {
    in_scope: ["string"],
    out_of_scope: ["string"],
    boundary_reason: ["string"],
  },
  roles: [{
    name: "string",
    type: "string",
    responsibility: "string",
    needs: ["string"],
  }],
  features: [{
    name: "string",
    input: "string",
    process: "string",
    output: "string",
    result: "string",
    boundary: "string",
  }],
  business_rules: [{
    rule: "string",
    trigger: "string",
    result: "string",
    fallback: "string",
  }],
  states: [{
    state: "string",
    meaning: "string",
    system_result: "string",
    user_next_step: "string",
  }],
  exceptions: [{
    exception: "string",
    trigger: "string",
    handling: "string",
    recovery: "string",
  }],
  experience_handoff_requirements: [{
    requirement: "string",
    business_judgment: "string",
    experience_impact: "string",
    must_address: ["string"],
    do_not_rejudge: ["string"],
  }],
  constraints: {
    hard_constraints: ["string"],
    dependencies: ["string"],
    do_not_do: ["string"],
    safety_or_business_boundaries: ["string"],
  },
  open_questions: [{
    question: "string",
    impact: "string",
    owner: "string",
    level: "string",
  }],
};

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function validateValue(value, schema, field, errors) {
  if (schema === "string") {
    if (typeof value !== "string" || !value.trim()) {
      errors.push(`${field} 必须是非空字符串`);
    }
    return;
  }
  if (Array.isArray(schema)) {
    if (!Array.isArray(value)) {
      errors.push(`${field} 必须是数组`);
      return;
    }
    value.forEach((item, index) => validateValue(item, schema[0], `${field}[${index}]`, errors));
    return;
  }
  if (!isObject(value)) {
    errors.push(`${field} 必须是对象`);
    return;
  }
  const expectedKeys = Object.keys(schema);
  const allowed = new Set(expectedKeys);
  for (const key of expectedKeys) {
    if (!Object.prototype.hasOwnProperty.call(value, key)) {
      errors.push(`${field}.${key} 缺失`);
    } else {
      validateValue(value[key], schema[key], `${field}.${key}`, errors);
    }
  }
  for (const key of Object.keys(value)) {
    if (!allowed.has(key)) errors.push(`${field}.${key} 不允许出现`);
  }
}

function validate(data) {
  const errors = [];
  validateValue(data, ROOT_SCHEMA, "root", errors);
  if (!isObject(data)) return errors;
  if (data.skill !== "uxb") errors.push("skill 必须为 uxb");
  if (data.version !== "5.0") errors.push("version 必须为 5.0");
  if (data.artifact_md !== "spark-output/uxb_output.md") {
    errors.push("artifact_md 必须为 spark-output/uxb_output.md");
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
    data = JSON.parse(fs.readFileSync(resolved, "utf8"));
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
  console.log("uxb context valid");
}

if (require.main === module) main();
module.exports = { validate };
