"use strict";

const fs = require("fs");
const path = require("path");

const ROOT_KEYS = [
  "skill", "version", "generated_at", "project_name", "artifact_md", "source_refs",
  "page_summary", "generation_scope", "entities", "entity_relationships", "coverage",
  "open_questions", "edge_consumed", "edge_trace",
];
const SUMMARY_KEYS = ["product_domain", "page_type", "user_role", "core_task"];
const SCOPE_KEYS = ["generate", "reference_only", "do_not_generate"];
const COVERAGE_KEYS = [
  "pages", "entities", "flows", "validation_rules", "states", "exceptions",
  "result_states", "copy_items", "template_variables",
];
const MODES = new Set(["generate", "reference_only", "do_not_generate"]);
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

function validate(data) {
  const errors = [];
  if (!exact(data, ROOT_KEYS, "root", errors)) return errors;
  if (data.skill !== "page-spec") errors.push("skill 必须为 page-spec");
  if (data.version !== "2.0") errors.push("version 必须为 2.0");
  if (data.artifact_md !== "spark-output/page_spec.md") {
    errors.push("artifact_md 必须为 spark-output/page_spec.md");
  }
  string(data.generated_at, "generated_at", errors);
  string(data.project_name, "project_name", errors);
  strings(data.source_refs, "source_refs", errors);

  if (exact(data.page_summary, SUMMARY_KEYS, "page_summary", errors)) {
    SUMMARY_KEYS.forEach((key) => string(data.page_summary[key], `page_summary.${key}`, errors));
  }
  const scopeSets = {};
  if (exact(data.generation_scope, SCOPE_KEYS, "generation_scope", errors)) {
    SCOPE_KEYS.forEach((key) => {
      strings(data.generation_scope[key], `generation_scope.${key}`, errors);
      scopeSets[key] = new Set(Array.isArray(data.generation_scope[key]) ? data.generation_scope[key] : []);
    });
    const seen = new Set();
    SCOPE_KEYS.forEach((key) => scopeSets[key].forEach((entityId) => {
      if (seen.has(entityId)) errors.push(`generation_scope 中实体重复归类：${entityId}`);
      seen.add(entityId);
    }));
  }

  const entityIds = new Set();
  if (array(data.entities, "entities", errors)) {
    if (data.entities.length === 0) errors.push("entities 完整页面规格中不得为空");
    data.entities.forEach((entity, index) => {
      const field = `entities[${index}]`;
      if (!exact(entity, ["entity_id", "name", "type", "generate_mode", "md_anchor"], field, errors)) return;
      string(entity.entity_id, `${field}.entity_id`, errors);
      if (typeof entity.entity_id === "string" && !ID_PATTERN.test(entity.entity_id)) {
        errors.push(`${field}.entity_id 必须是 kebab-case`);
      }
      if (entityIds.has(entity.entity_id)) errors.push(`${field}.entity_id 重复`);
      entityIds.add(entity.entity_id);
      ["name", "type", "md_anchor"].forEach((key) => string(entity[key], `${field}.${key}`, errors));
      if (!MODES.has(entity.generate_mode)) errors.push(`${field}.generate_mode 枚举非法`);
      if (scopeSets[entity.generate_mode] && !scopeSets[entity.generate_mode].has(entity.entity_id)) {
        errors.push(`${field}.generate_mode 与 generation_scope 不一致`);
      }
    });
  }
  if (scopeSets.generate && scopeSets.generate.size === 0) errors.push("generation_scope.generate 不得为空");
  if (Object.keys(scopeSets).length) {
    const scoped = new Set(SCOPE_KEYS.flatMap((key) => [...scopeSets[key]]));
    scoped.forEach((entityId) => {
      if (!entityIds.has(entityId)) errors.push(`generation_scope 引用不存在：${entityId}`);
    });
    entityIds.forEach((entityId) => {
      if (!scoped.has(entityId)) errors.push(`实体未归入 generation_scope：${entityId}`);
    });
  }

  if (array(data.entity_relationships, "entity_relationships", errors)) {
    data.entity_relationships.forEach((relation, index) => {
      const field = `entity_relationships[${index}]`;
      if (!exact(relation, ["from_entity_id", "to_entity_id", "relation"], field, errors)) return;
      ["from_entity_id", "to_entity_id", "relation"].forEach((key) =>
        string(relation[key], `${field}.${key}`, errors));
      for (const key of ["from_entity_id", "to_entity_id"]) {
        if (!entityIds.has(relation[key])) errors.push(`${field}.${key} 引用不存在：${relation[key]}`);
      }
    });
  }
  if (exact(data.coverage, COVERAGE_KEYS, "coverage", errors)) {
    COVERAGE_KEYS.forEach((key) => {
      const value = data.coverage[key];
      if (!Number.isInteger(value) || value < 0) errors.push(`coverage.${key} 必须是非负整数`);
    });
  }
  array(data.open_questions, "open_questions", errors);
  if (typeof data.edge_consumed !== "boolean") errors.push("edge_consumed 必须是布尔值");
  if (array(data.edge_trace, "edge_trace", errors) && !data.edge_consumed && data.edge_trace.length) {
    errors.push("edge_consumed=false 时 edge_trace 必须为空");
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
  console.log("page-spec context valid");
}

if (require.main === module) main();
module.exports = { validate };
