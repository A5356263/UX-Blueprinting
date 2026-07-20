"use strict";

const fs = require("fs");
const path = require("path");

const ROOT_KEYS = [
  "skill", "version", "generated_at", "project_name", "artifact_md", "source_refs",
  "source_mode", "direction_summary", "primary_roles", "story_titles",
  "p0_story_titles", "critical_assumptions", "out_of_scope", "open_questions",
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
  if (data.skill !== "stories") errors.push("skill 必须为 stories");
  if (data.version !== "2.0") errors.push("version 必须为 2.0");
  if (data.artifact_md !== "spark-output/stories.md") {
    errors.push("artifact_md 必须为 spark-output/stories.md");
  }
  for (const field of ["generated_at", "project_name", "source_mode", "direction_summary"]) {
    nonEmptyString(data[field], field, errors);
  }
  for (const field of [
    "source_refs", "primary_roles", "story_titles", "p0_story_titles",
    "critical_assumptions", "out_of_scope", "open_questions",
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
  console.log("stories context valid");
}

if (require.main === module) main();
module.exports = { validate };
