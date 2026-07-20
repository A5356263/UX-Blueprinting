"use strict";

const fs = require("fs");
const path = require("path");

const ROOT_KEYS = [
  "skill", "version", "generated_at", "project_name", "artifact_md", "source_refs",
  "decision_summary", "primary_roles", "in_scope", "out_of_scope",
  "hard_constraints", "confirmed_decisions", "open_questions",
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

  if (data.skill !== "uxb") errors.push("skill 必须为 uxb");
  if (data.version !== "4.0") errors.push("version 必须为 4.0");
  if (data.artifact_md !== "spark-output/uxb_output.md") {
    errors.push("artifact_md 必须为 spark-output/uxb_output.md");
  }
  nonEmptyString(data.generated_at, "generated_at", errors);
  nonEmptyString(data.project_name, "project_name", errors);
  nonEmptyString(data.decision_summary, "decision_summary", errors);
  stringArray(data.source_refs, "source_refs", errors);
  for (const field of [
    "primary_roles", "in_scope", "out_of_scope", "hard_constraints",
    "confirmed_decisions", "open_questions",
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
  console.log("uxb context valid");
}

if (require.main === module) main();
module.exports = { validate };
