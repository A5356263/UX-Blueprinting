"use strict";

const fs = require("fs");
const path = require("path");

const ROOT_KEYS = [
  "skill", "version", "generated_at", "project_name", "artifact_md", "source_refs",
  "mode", "result_level", "journeys", "source_trace", "gaps",
];
const JOURNEY_KEYS = ["role", "role_type", "summary", "stages", "key_transitions"];
const STAGE_KEYS = [
  "name", "goal", "actions", "touchpoints", "user_voice", "confidence",
  "confidence_reason", "pain_points", "dropout_risk", "opportunities",
];
const TRANSITION_KEYS = ["from", "to", "trigger"];
const SOURCE_TRACE_KEYS = ["conclusion", "source_type", "source"];
const GAP_KEYS = ["gap", "impact", "suggested_source"];
const MODES = new Set(["stories-chain", "uxb-chain", "framing-chain", "prd-standalone", "unknown"]);
const ROLE_TYPES = new Set(["主线角色", "支持角色"]);
const CONFIDENCE_VALUES = new Set(["高", "中", "低", "unknown"]);
const SOURCE_TYPES = new Set(["原文提取", "用户补充", "规则推导", "未提供", "unknown"]);

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

function objectArray(value, field, errors, validateItem, allowEmpty = true) {
  if (!Array.isArray(value)) {
    errors.push(`${field} 必须是数组`);
    return;
  }
  if (!allowEmpty && value.length === 0) errors.push(`${field} 不得为空`);
  value.forEach((item, index) => validateItem(item, `${field}[${index}]`, errors));
}

function validateStage(stage, field, errors) {
  if (!exactObject(stage, STAGE_KEYS, field, errors)) return;
  for (const key of [
    "name", "goal", "user_voice", "confidence", "confidence_reason", "dropout_risk",
  ]) {
    nonEmptyString(stage[key], `${field}.${key}`, errors);
  }
  for (const key of ["actions", "touchpoints", "pain_points", "opportunities"]) {
    stringArray(stage[key], `${field}.${key}`, errors);
  }
  if (typeof stage.confidence === "string" && !CONFIDENCE_VALUES.has(stage.confidence)) {
    errors.push(`${field}.confidence 值不合法`);
  }
}

function validateTransition(transition, field, errors) {
  if (!exactObject(transition, TRANSITION_KEYS, field, errors)) return;
  for (const key of TRANSITION_KEYS) nonEmptyString(transition[key], `${field}.${key}`, errors);
}

function validateJourney(journey, field, errors) {
  if (!exactObject(journey, JOURNEY_KEYS, field, errors)) return;
  for (const key of ["role", "role_type", "summary"]) {
    nonEmptyString(journey[key], `${field}.${key}`, errors);
  }
  if (typeof journey.role_type === "string" && !ROLE_TYPES.has(journey.role_type)) {
    errors.push(`${field}.role_type 值不合法`);
  }
  objectArray(journey.stages, `${field}.stages`, errors, validateStage, false);
  objectArray(journey.key_transitions, `${field}.key_transitions`, errors, validateTransition);
}

function validateSourceTrace(item, field, errors) {
  if (!exactObject(item, SOURCE_TRACE_KEYS, field, errors)) return;
  for (const key of SOURCE_TRACE_KEYS) nonEmptyString(item[key], `${field}.${key}`, errors);
  if (typeof item.source_type === "string" && !SOURCE_TYPES.has(item.source_type)) {
    errors.push(`${field}.source_type 值不合法`);
  }
}

function validateGap(item, field, errors) {
  if (!exactObject(item, GAP_KEYS, field, errors)) return;
  for (const key of GAP_KEYS) nonEmptyString(item[key], `${field}.${key}`, errors);
}

function validateRoot(data) {
  const errors = [];
  if (!exactObject(data, ROOT_KEYS, "root", errors)) return errors;

  if (data.skill !== "journey-analysis") errors.push("skill 必须为 journey-analysis");
  if (data.version !== "3.0") errors.push("version 必须为 3.0");
  if (data.artifact_md !== "spark-output/journey_analysis.md") {
    errors.push("artifact_md 必须为 spark-output/journey_analysis.md");
  }
  for (const field of ["generated_at", "project_name", "mode", "result_level"]) {
    nonEmptyString(data[field], field, errors);
  }
  if (typeof data.mode === "string" && !MODES.has(data.mode)) errors.push("mode 值不合法");
  stringArray(data.source_refs, "source_refs", errors);
  objectArray(data.journeys, "journeys", errors, validateJourney, false);
  objectArray(data.source_trace, "source_trace", errors, validateSourceTrace);
  objectArray(data.gaps, "gaps", errors, validateGap);
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
  const errors = validateRoot(data);
  if (errors.length) {
    errors.forEach((error) => console.error(error));
    process.exit(1);
  }
  console.log("journey-analysis context valid");
}

if (require.main === module) main();
module.exports = { validateRoot };
