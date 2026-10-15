"use strict";

const fs = require("fs");
const path = require("path");

const ROOT_KEYS = [
  "skill", "version", "generated_at", "project_name", "artifact_md", "source_refs",
  "mode", "decision_summary", "problem_statement", "primary_roles", "solution_goal",
  "success_signals", "recommended_solution", "recommendation_basis", "business_solution_points",
  "handoff_requirements", "hard_constraints", "out_of_scope", "confirmed_facts",
  "working_assumptions", "open_questions",
];

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function exactObject(value, keys, field, errors) {
  if (!isObject(value)) {
    errors.push(`${field} 必须是对象`);
    return false;
  }
  const allowed = new Set(keys);
  for (const key of keys) {
    if (!Object.prototype.hasOwnProperty.call(value, key)) errors.push(`${field}.${key} 缺失`);
  }
  for (const key of Object.keys(value)) {
    if (!allowed.has(key)) errors.push(`${field}.${key} 不允许出现`);
  }
  return true;
}

function nonEmptyString(value, field, errors) {
  if (typeof value !== "string" || !value.trim()) errors.push(`${field} 必须是非空字符串`);
}

function stringArray(value, field, errors) {
  if (!Array.isArray(value)) {
    errors.push(`${field} 必须是数组`);
    return;
  }
  value.forEach((item, index) => nonEmptyString(item, `${field}[${index}]`, errors));
}

function validate(data) {
  const errors = [];
  if (!exactObject(data, ROOT_KEYS, "root", errors)) return errors;
  if (data.skill !== "problem-framing") errors.push("skill 必须为 problem-framing");
  if (data.version !== "3.0") errors.push("version 必须为 3.0");
  if (data.artifact_md !== "spark-output/problem_framing.md") {
    errors.push("artifact_md 必须为 spark-output/problem_framing.md");
  }
  for (const field of [
    "generated_at", "project_name", "decision_summary", "problem_statement",
    "mode", "decision_summary", "problem_statement", "solution_goal", "recommended_solution",
  ]) {
    nonEmptyString(data[field], field, errors);
  }
  if (!["problem-definition", "direction-correction", "unknown"].includes(data.mode)) {
    errors.push("mode 必须为 problem-definition、direction-correction 或 unknown");
  }
  for (const field of [
    "source_refs", "primary_roles", "success_signals", "recommendation_basis",
    "business_solution_points", "handoff_requirements", "hard_constraints", "out_of_scope",
    "confirmed_facts", "working_assumptions", "open_questions",
  ]) {
    stringArray(data[field], field, errors);
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
  console.log("problem-framing context valid");
}

if (require.main === module) main();
module.exports = { validate };
