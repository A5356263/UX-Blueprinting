"use strict";

const fs = require("fs");
const path = require("path");

const ROOT_KEYS = [
  "skill", "version", "generated_at", "project_name", "artifact_md", "source_refs",
  "source_status", "critical_design_judgments", "main_flow", "sub_flows",
  "exceptions", "surfaces", "states", "open_questions",
];
const SOURCE_MODES = new Set(["uxb-mode", "framing-mode", "deepened-mode", "unknown"]);
const EXPANSION_MODES = new Set(["full", "limited", "unknown"]);
const SUB_END_TYPES = new Set(["return", "result", "terminate", "unknown"]);
const EXCEPTION_END_TYPES = new Set(["return", "terminate", "unknown"]);
const ID_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

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
function id(value, field, errors) {
  string(value, field, errors);
  if (typeof value === "string" && !ID_PATTERN.test(value)) errors.push(`${field} 必须是 kebab-case`);
}
function collection(items, field, keys, idKey, errors, callback) {
  if (!array(items, field, errors)) return new Set();
  const ids = new Set();
  items.forEach((item, index) => {
    const itemPath = `${field}[${index}]`;
    if (!exact(item, keys, itemPath, errors)) return;
    id(item[idKey], `${itemPath}.${idKey}`, errors);
    if (ids.has(item[idKey])) errors.push(`${itemPath}.${idKey} 重复`);
    ids.add(item[idKey]);
    callback(item, itemPath);
  });
  return ids;
}

function validate(data) {
  const errors = [];
  if (!exact(data, ROOT_KEYS, "root", errors)) return errors;
  if (data.skill !== "experience-blueprint") errors.push("skill 必须为 experience-blueprint");
  if (data.version !== "2.0") errors.push("version 必须为 2.0");
  if (data.artifact_md !== "spark-output/experience_blueprint.md") {
    errors.push("artifact_md 必须为 spark-output/experience_blueprint.md");
  }
  string(data.generated_at, "generated_at", errors);
  string(data.project_name, "project_name", errors);
  strings(data.source_refs, "source_refs", errors);

  if (exact(data.source_status, ["source_mode", "expansion_mode", "usable", "missing_inputs"],
    "source_status", errors)) {
    if (!SOURCE_MODES.has(data.source_status.source_mode)) errors.push("source_status.source_mode 枚举非法");
    if (!EXPANSION_MODES.has(data.source_status.expansion_mode)) {
      errors.push("source_status.expansion_mode 枚举非法");
    }
    if (typeof data.source_status.usable !== "boolean") errors.push("source_status.usable 必须是布尔值");
    strings(data.source_status.missing_inputs, "source_status.missing_inputs", errors);
  }

  collection(
    data.critical_design_judgments, "critical_design_judgments",
    ["judgment_id", "judgment", "decision", "open_question", "source_anchor"], "judgment_id", errors,
    (item, itemPath) => ["judgment", "decision", "open_question", "source_anchor"].forEach((key) =>
      string(item[key], `${itemPath}.${key}`, errors)),
  );
  const nodeIds = collection(
    data.main_flow, "main_flow",
    ["node_id", "node_name", "user_action", "system_feedback", "state_change", "next_step", "source_anchor"],
    "node_id", errors,
    (item, itemPath) => ["node_name", "user_action", "system_feedback", "state_change", "next_step", "source_anchor"]
      .forEach((key) => string(item[key], `${itemPath}.${key}`, errors)),
  );
  if (Array.isArray(data.main_flow) && data.main_flow.length === 0) errors.push("main_flow 不得为空");

  collection(
    data.sub_flows, "sub_flows",
    ["flow_id", "flow_name", "trigger_condition", "user_action", "system_feedback", "next_step",
      "end_type", "end_target", "source_anchor"],
    "flow_id", errors,
    (item, itemPath) => {
      ["flow_name", "trigger_condition", "user_action", "system_feedback", "next_step", "end_target", "source_anchor"]
        .forEach((key) => string(item[key], `${itemPath}.${key}`, errors));
      if (!SUB_END_TYPES.has(item.end_type)) errors.push(`${itemPath}.end_type 枚举非法`);
      if (item.end_type === "return" && !nodeIds.has(item.end_target)) {
        const names = new Set((data.main_flow || []).map((node) => node.node_name));
        if (!names.has(item.end_target)) errors.push(`${itemPath}.end_target 未指向主流程节点`);
      }
    },
  );
  collection(
    data.exceptions, "exceptions",
    ["exception_id", "name", "timing", "trigger_condition", "system_feedback", "user_next_step",
      "recovery_path", "end_type", "end_target", "source_anchor"],
    "exception_id", errors,
    (item, itemPath) => {
      ["name", "timing", "trigger_condition", "system_feedback", "user_next_step", "recovery_path",
        "end_target", "source_anchor"].forEach((key) => string(item[key], `${itemPath}.${key}`, errors));
      if (!EXCEPTION_END_TYPES.has(item.end_type)) errors.push(`${itemPath}.end_type 枚举非法`);
      if (item.end_type === "return" && !nodeIds.has(item.end_target)) {
        const nodeNames = new Set((data.main_flow || []).map((node) => node.node_name));
        const flowIds = new Set((data.sub_flows || []).map((flow) => flow.flow_id));
        if (!nodeNames.has(item.end_target) && !flowIds.has(item.end_target)) {
          errors.push(`${itemPath}.end_target 未指向主流程或次流程`);
        }
      }
    },
  );

  const surfaceIds = new Set();
  if (exact(data.surfaces, ["pages", "modals", "drawers"], "surfaces", errors)) {
    for (const kind of ["pages", "modals", "drawers"]) {
      const ids = collection(
        data.surfaces[kind], `surfaces.${kind}`,
        ["surface_id", "name", "goal", "entry_condition", "md_anchor"], "surface_id", errors,
        (item, itemPath) => ["name", "goal", "entry_condition", "md_anchor"].forEach((key) =>
          string(item[key], `${itemPath}.${key}`, errors)),
      );
      ids.forEach((surfaceId) => {
        if (surfaceIds.has(surfaceId)) errors.push(`surfaces 中 surface_id 重复：${surfaceId}`);
        surfaceIds.add(surfaceId);
      });
    }
  }

  const flowIds = new Set((Array.isArray(data.sub_flows) ? data.sub_flows : []).map((flow) => flow.flow_id));
  const exceptionIds = new Set(
    (Array.isArray(data.exceptions) ? data.exceptions : []).map((exception) => exception.exception_id),
  );
  collection(
    data.states, "states",
    ["state_id", "state", "meaning", "applies_to", "user_action_available", "feedback_standard", "source_anchor"],
    "state_id", errors,
    (item, itemPath) => {
      ["state", "meaning", "user_action_available", "feedback_standard", "source_anchor"].forEach((key) =>
        string(item[key], `${itemPath}.${key}`, errors));
      strings(item.applies_to, `${itemPath}.applies_to`, errors);
      const allowedTargets = new Set([...nodeIds, ...flowIds, ...exceptionIds, ...surfaceIds]);
      (Array.isArray(item.applies_to) ? item.applies_to : []).forEach((ref) => {
        if (!allowedTargets.has(ref)) errors.push(`${itemPath}.applies_to 引用不存在：${ref}`);
      });
    },
  );
  collection(
    data.open_questions, "open_questions",
    ["question_id", "question", "impact", "owner", "source_anchor"], "question_id", errors,
    (item, itemPath) => ["question", "impact", "owner", "source_anchor"].forEach((key) =>
      string(item[key], `${itemPath}.${key}`, errors)),
  );
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
  console.log("experience-blueprint context valid");
}

if (require.main === module) main();
module.exports = { validate };
