"use strict";

const fs = require("fs");

const REQUIRED_FIELDS = [
  "schema_version",
  "project_name",
  "baseline_status",
  "source_trace",
  "goal_and_scope",
  "business_objects",
  "roles_and_permissions",
  "functions_and_task_closure",
  "business_rules",
  "states_and_transitions",
  "exceptions_and_business_results",
  "data_system_and_audit",
  "constraints_and_out_of_scope",
  "experience_decisions",
  "completion_criteria",
];

const ROOT_FIELDS = new Set(REQUIRED_FIELDS);
const SOURCE_TYPES = new Set(["prd", "formal_knowledge", "product_response"]);
const EXPERIENCE_SOURCE_TYPES = new Set([...SOURCE_TYPES, "user_supplement"]);
const CHANGE_TYPES = new Set(["keep", "add", "modify", "remove"]);

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function checkObject(value, path, errors) {
  if (!isObject(value)) errors.push(`${path} 必须是对象`);
}

function checkArray(value, path, errors) {
  if (!Array.isArray(value)) errors.push(`${path} 必须是数组`);
}

function checkString(value, path, errors, allowEmpty = false) {
  if (typeof value !== "string" || (!allowEmpty && value.trim() === "")) {
    errors.push(`${path} 必须是${allowEmpty ? "" : "非空"}字符串`);
  }
}

function checkStringArray(value, path, errors) {
  if (!Array.isArray(value)) {
    errors.push(`${path} 必须是数组`);
    return;
  }
  value.forEach((item, index) => checkString(item, `${path}[${index}]`, errors));
}

function checkSources(value, path, errors, allowedTypes = SOURCE_TYPES) {
  if (!Array.isArray(value)) {
    errors.push(`${path} 必须是数组`);
    return;
  }
  value.forEach((source, index) => {
    const itemPath = `${path}[${index}]`;
    if (!isObject(source)) {
      errors.push(`${itemPath} 必须是对象`);
      return;
    }
    checkString(source.type, `${itemPath}.type`, errors);
    if (typeof source.type === "string" && !allowedTypes.has(source.type)) {
      errors.push(`${itemPath}.type 不是允许的来源类型`);
    }
    checkString(source.reference, `${itemPath}.reference`, errors);
    checkString(source.location, `${itemPath}.location`, errors);
  });
}

function checkObjectArray(value, path, prefix, fields, errors) {
  if (!Array.isArray(value)) {
    errors.push(`${path} 必须是数组`);
    return;
  }

  const ids = new Set();
  value.forEach((item, index) => {
    const itemPath = `${path}[${index}]`;
    if (!isObject(item)) {
      errors.push(`${itemPath} 必须是对象`);
      return;
    }

    checkString(item.id, `${itemPath}.id`, errors);
    if (typeof item.id === "string") {
      if (!new RegExp(`^${prefix}-\\d{3}$`).test(item.id)) {
        errors.push(`${itemPath}.id 必须使用 ${prefix}-001 格式`);
      }
      if (ids.has(item.id)) errors.push(`${path} 内编号重复：${item.id}`);
      ids.add(item.id);
    }

    for (const [field, type] of Object.entries(fields)) {
      if (!Object.prototype.hasOwnProperty.call(item, field)) {
        errors.push(`${itemPath} 缺少字段：${field}`);
        continue;
      }
      if (type === "string") checkString(item[field], `${itemPath}.${field}`, errors);
      if (type === "optional-string") checkString(item[field], `${itemPath}.${field}`, errors, true);
      if (type === "array") checkStringArray(item[field], `${itemPath}.${field}`, errors);
      if (type === "boolean" && typeof item[field] !== "boolean") {
        errors.push(`${itemPath}.${field} 必须是布尔值`);
      }
      if (type === "sources") checkSources(item[field], `${itemPath}.${field}`, errors);
      if (type === "experience-sources") checkSources(item[field], `${itemPath}.${field}`, errors, EXPERIENCE_SOURCE_TYPES);
    }
  });
}

function validate(data) {
  const errors = [];

  if (!isObject(data)) {
    return ["根节点必须是 JSON 对象"];
  }

  for (const field of REQUIRED_FIELDS) {
    if (!Object.prototype.hasOwnProperty.call(data, field)) {
      errors.push(`缺少必需字段：${field}`);
    }
  }

  for (const field of Object.keys(data)) {
    if (!ROOT_FIELDS.has(field)) errors.push(`未知根字段：${field}`);
  }

  if ("schema_version" in data) {
    checkString(data.schema_version, "schema_version", errors);
    if (typeof data.schema_version === "string" && data.schema_version !== "2.1") {
      errors.push("schema_version 只允许 2.1");
    }
  }
  if ("project_name" in data) checkString(data.project_name, "project_name", errors);
  if ("baseline_status" in data) {
    checkString(data.baseline_status, "baseline_status", errors);
    if (typeof data.baseline_status === "string" && data.baseline_status !== "formal") {
      errors.push("baseline_status 只允许 formal");
    }
  }

  if ("source_trace" in data) {
    checkObject(data.source_trace, "source_trace", errors);
    if (isObject(data.source_trace)) {
      checkSources(data.source_trace.prd, "source_trace.prd", errors);
      checkSources(data.source_trace.formal_knowledge, "source_trace.formal_knowledge", errors);
      checkStringArray(data.source_trace.product_responses, "source_trace.product_responses", errors);
      if (Array.isArray(data.source_trace.product_responses)) {
        data.source_trace.product_responses.forEach((id, index) => {
          if (typeof id === "string" && !/^Q-\d{3}$/.test(id)) {
            errors.push(`source_trace.product_responses[${index}] 必须使用 Q-001 格式`);
          }
        });
      }
    }
  }

  if ("goal_and_scope" in data) {
    checkObject(data.goal_and_scope, "goal_and_scope", errors);
    if (isObject(data.goal_and_scope)) {
      for (const field of ["business_problem", "goals", "in_scope", "out_of_scope", "success_results"]) {
        checkStringArray(data.goal_and_scope[field], `goal_and_scope.${field}`, errors);
      }
    }
  }

  if ("business_objects" in data) {
    checkObjectArray(data.business_objects, "business_objects", "BO", {
      name: "string",
      definition: "string",
      relations: "array",
      entry_conditions: "array",
      exclusion_conditions: "array",
      sources: "sources",
    }, errors);
    if (Array.isArray(data.business_objects)) {
      data.business_objects.forEach((item, index) => {
        if (!isObject(item)) return;
        if (!Object.prototype.hasOwnProperty.call(item, "change_type")) {
          errors.push(`business_objects[${index}] 缺少字段：change_type`);
        } else if (!CHANGE_TYPES.has(item.change_type)) {
          errors.push(`business_objects[${index}].change_type 不是允许的枚举值`);
        }
      });
    }
  }

  if ("roles_and_permissions" in data) {
    checkObjectArray(data.roles_and_permissions, "roles_and_permissions", "RP", {
      role: "string",
      responsibilities: "array",
      allowed_actions: "array",
      permission_prerequisites: "array",
      business_scope: "array",
      forbidden_actions: "array",
      sources: "sources",
    }, errors);
  }

  if ("functions_and_task_closure" in data) {
    checkObjectArray(data.functions_and_task_closure, "functions_and_task_closure", "FN", {
      name: "string",
      actor: "string",
      trigger_conditions: "array",
      main_steps: "array",
      success_results: "array",
      failure_or_rejection_results: "array",
      next_business_nodes: "array",
      sources: "sources",
    }, errors);
    if (Array.isArray(data.functions_and_task_closure)) {
      data.functions_and_task_closure.forEach((item, index) => {
        if (!isObject(item)) return;
        const itemPath = `functions_and_task_closure[${index}]`;
        if (Object.prototype.hasOwnProperty.call(item, "existing_task_location")) {
          checkString(item.existing_task_location, `${itemPath}.existing_task_location`, errors);
        }
        if (Object.prototype.hasOwnProperty.call(item, "existing_carriers")) {
          checkStringArray(item.existing_carriers, `${itemPath}.existing_carriers`, errors);
        }
        if (Object.prototype.hasOwnProperty.call(item, "existing_entry")) {
          checkString(item.existing_entry, `${itemPath}.existing_entry`, errors);
        }
      });
    }
  }

  if ("business_rules" in data) {
    checkObjectArray(data.business_rules, "business_rules", "BR", {
      name: "string",
      applicable_objects: "array",
      trigger_conditions: "array",
      decision_conditions: "array",
      business_results: "array",
      priority_or_exclusion: "array",
      sources: "sources",
    }, errors);
  }

  if ("states_and_transitions" in data) {
    checkObjectArray(data.states_and_transitions, "states_and_transitions", "ST", {
      business_object: "string",
      state: "string",
      meaning: "string",
      entry_conditions: "array",
      allowed_actions: "array",
      forbidden_actions: "array",
      next_states: "array",
      irreversible: "boolean",
      sources: "sources",
    }, errors);
  }

  if ("exceptions_and_business_results" in data) {
    checkObjectArray(data.exceptions_and_business_results, "exceptions_and_business_results", "EX", {
      scenario: "string",
      trigger_conditions: "array",
      business_decision: "string",
      task_result: "string",
      object_state_result: "string",
      retry_or_recovery: "string",
      responsible_party: "optional-string",
      sources: "sources",
    }, errors);
  }

  if ("data_system_and_audit" in data) {
    checkObject(data.data_system_and_audit, "data_system_and_audit", errors);
    if (isObject(data.data_system_and_audit)) {
      for (const field of ["data_changes", "system_impacts", "synchronization_and_failures", "audit_facts", "historical_data"]) {
        checkStringArray(data.data_system_and_audit[field], `data_system_and_audit.${field}`, errors);
      }
    }
  }

  if ("constraints_and_out_of_scope" in data) {
    checkObject(data.constraints_and_out_of_scope, "constraints_and_out_of_scope", errors);
    if (isObject(data.constraints_and_out_of_scope)) {
      for (const field of ["business_constraints", "dependencies", "explicitly_out_of_scope", "future_considerations"]) {
        checkStringArray(data.constraints_and_out_of_scope[field], `constraints_and_out_of_scope.${field}`, errors);
      }
    }
  }

  if ("completion_criteria" in data) {
    checkObjectArray(data.completion_criteria, "completion_criteria", "AC", {
      related_ids: "array",
      preconditions: "array",
      actions: "array",
      observable_results: "array",
      sources: "sources",
    }, errors);
  }

  if ("experience_decisions" in data) {
    checkObject(data.experience_decisions, "experience_decisions", errors);
    if (isObject(data.experience_decisions)) {
      checkObjectArray(data.experience_decisions.confirmed_constraints, "experience_decisions.confirmed_constraints", "EC", {
        applicable_tasks: "array",
        constraint: "string",
        sources: "experience-sources",
      }, errors);
      checkObjectArray(data.experience_decisions.pending_items, "experience_decisions.pending_items", "E", {
        applicable_tasks: "array",
        decision_topic: "string",
        sources: "sources",
      }, errors);
      if (Array.isArray(data.experience_decisions.pending_items)) {
        data.experience_decisions.pending_items.forEach((item, index) => {
          if (!isObject(item) || !Array.isArray(item.sources)) return;
          item.sources.forEach((source, sourceIndex) => {
            if (isObject(source) && source.type === "user_supplement") {
              errors.push(`experience_decisions.pending_items[${index}].sources[${sourceIndex}].type 不允许使用 user_supplement`);
            }
          });
        });
      }
    }
  }

  const knownIds = new Set();
  for (const field of [
    "business_objects",
    "roles_and_permissions",
    "functions_and_task_closure",
    "business_rules",
    "states_and_transitions",
    "exceptions_and_business_results",
    "completion_criteria",
  ]) {
    if (Array.isArray(data[field])) {
      data[field].forEach((item) => {
        if (isObject(item) && typeof item.id === "string") knownIds.add(item.id);
      });
    }
  }
  if (Array.isArray(data.completion_criteria)) {
    data.completion_criteria.forEach((item, index) => {
      if (!isObject(item) || !Array.isArray(item.related_ids)) return;
      item.related_ids.forEach((id, refIndex) => {
        if (typeof id === "string" && !knownIds.has(id)) {
          errors.push(`completion_criteria[${index}].related_ids[${refIndex}] 引用了不存在的编号`);
        }
      });
    });
  }
  if (isObject(data.experience_decisions)) {
    const functionIds = new Set(
      Array.isArray(data.functions_and_task_closure)
        ? data.functions_and_task_closure.filter(isObject).map((item) => item.id)
        : [],
    );
    for (const field of ["confirmed_constraints", "pending_items"]) {
      if (!Array.isArray(data.experience_decisions[field])) continue;
      data.experience_decisions[field].forEach((item, index) => {
        if (!isObject(item) || !Array.isArray(item.applicable_tasks)) return;
        item.applicable_tasks.forEach((id, refIndex) => {
          if (typeof id === "string" && !functionIds.has(id)) {
            errors.push(`experience_decisions.${field}[${index}].applicable_tasks[${refIndex}] 必须引用已有的 FN 编号`);
          }
        });
      });
    }
  }

  return errors;
}

function main() {
  const target = process.argv[2];
  if (!target) {
    console.error("用法：node validate-context.js <requirements-baseline.json>");
    process.exit(1);
  }

  let data;
  try {
    data = JSON.parse(fs.readFileSync(target, "utf8"));
  } catch (error) {
    console.error(`JSON 读取失败：${error.message}`);
    process.exit(1);
  }

  const errors = validate(data);
  if (errors.length > 0) {
    for (const error of errors) console.error(`- ${error}`);
    process.exit(1);
  }

  console.log("Context JSON 结构校验通过。");
}

if (require.main === module) main();

module.exports = { REQUIRED_FIELDS, validate };
