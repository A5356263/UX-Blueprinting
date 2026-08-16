"use strict";

const fs = require("fs");

const ROOT_FIELDS = [
  "skill",
  "version",
  "generated_at",
  "project_name",
  "artifact_md",
  "result_status",
  "strategy_basis",
  "key_insights",
  "experience_strategies",
  "design_criteria",
  "strategy_boundaries",
  "source_trace",
];

const SOURCE_TYPES = new Set([
  "formal_input",
  "stories",
  "journey",
  "business_knowledge",
  "design_principle",
  "interaction_pattern",
  "user_confirmation",
]);
const CONFIDENCE_VALUES = new Set(["high", "medium", "low"]);
const RESULT_STATUS_VALUES = new Set(["strategy_ready", "no_independent_strategy"]);

const ARRAY_SCHEMAS = {
  key_insights: {
    prefix: "KI",
    required: {
      insight: "string",
      applies_to: "nonempty-string-array",
      evidence_refs: "nonempty-string-array",
    },
  },
  experience_strategies: {
    prefix: "ES",
    required: {
      title: "string",
      thesis: "string",
      tension: "string",
      applies_to: "nonempty-string-array",
      expected_outcome: "string",
      handoff_outcome: "string",
      evidence_refs: "nonempty-string-array",
      confidence: "confidence",
    },
  },
  design_criteria: {
    prefix: "DC",
    required: {
      criterion: "string",
      strategy_refs: "nonempty-string-array",
      source_refs: "nonempty-string-array",
    },
  },
  strategy_boundaries: {
    prefix: "SB",
    required: {
      boundary: "string",
      strategy_refs: "nonempty-string-array",
    },
  },
  source_trace: {
    prefix: "ST",
    required: {
      source_type: "source-type",
      source_name: "string",
      used_for: "nonempty-string-array",
    },
    optional: {
      source_path: "string",
    },
  },
};

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function validateString(value, field, errors) {
  if (typeof value !== "string" || value.trim() === "") {
    errors.push(field + " 必须是非空字符串");
  }
}

function validateStringArray(value, field, errors, requireNonEmpty) {
  if (!Array.isArray(value)) {
    errors.push(field + " 必须是数组");
    return;
  }
  if (requireNonEmpty && value.length === 0) {
    errors.push(field + " 不得为空数组");
  }
  value.forEach(function validateItem(item, index) {
    validateString(item, field + "[" + index + "]", errors);
  });
}

function validateType(value, field, type, errors) {
  if (type === "string") {
    validateString(value, field, errors);
    return;
  }
  if (type === "nonempty-string-array") {
    validateStringArray(value, field, errors, true);
    return;
  }
  if (type === "string-array") {
    validateStringArray(value, field, errors, false);
    return;
  }
  if (type === "confidence") {
    if (!CONFIDENCE_VALUES.has(value)) {
      errors.push(field + " 必须为 high、medium 或 low");
    }
    return;
  }
  if (type === "source-type" && !SOURCE_TYPES.has(value)) {
    errors.push(field + " 不是允许的 source_type");
  }
}

function validateStructuredObject(value, field, required, optional, errors) {
  if (!isObject(value)) {
    errors.push(field + " 必须是对象");
    return;
  }
  const optionalFields = optional || {};
  const allowed = new Set(Object.keys(required).concat(Object.keys(optionalFields)));

  Object.keys(required).forEach(function validateRequired(key) {
    if (!Object.prototype.hasOwnProperty.call(value, key)) {
      errors.push(field + "." + key + " 缺失");
      return;
    }
    validateType(value[key], field + "." + key, required[key], errors);
  });

  Object.keys(optionalFields).forEach(function validateOptional(key) {
    if (Object.prototype.hasOwnProperty.call(value, key)) {
      validateType(value[key], field + "." + key, optionalFields[key], errors);
    }
  });

  Object.keys(value).forEach(function rejectUnknown(key) {
    if (!allowed.has(key)) errors.push(field + "." + key + " 不允许出现");
  });
}

function validateObjectArray(value, field, config, errors) {
  if (!Array.isArray(value)) {
    errors.push(field + " 必须是数组");
    return [];
  }
  const ids = new Set();
  const required = Object.assign({ id: "string" }, config.required);
  const idPattern = new RegExp("^" + config.prefix + "-\\d{3}$");

  value.forEach(function validateObject(item, index) {
    const itemField = field + "[" + index + "]";
    validateStructuredObject(item, itemField, required, config.optional, errors);
    if (!isObject(item) || typeof item.id !== "string") return;
    if (!idPattern.test(item.id)) {
      errors.push(itemField + ".id 必须使用 " + config.prefix + "-001 格式");
    }
    if (ids.has(item.id)) errors.push(field + " 内编号重复：" + item.id);
    ids.add(item.id);
  });
  return Array.from(ids);
}

function validateGeneratedAt(value, errors) {
  validateString(value, "generated_at", errors);
  if (typeof value === "string" && !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(value)) {
    errors.push("generated_at 必须使用 ISO 8601 时间格式");
  }
}

function validateStrategyBasis(value, errors) {
  validateStructuredObject(value, "strategy_basis", {
    source_ref: "string",
    problem_or_goal: "string",
    target_users: "nonempty-string-array",
    key_tasks: "nonempty-string-array",
    solution_direction: "string",
    scope: "nonempty-string-array",
    out_of_scope: "string-array",
  }, {}, errors);
}

function validateReferences(data, ids, errors) {
  const sourceIds = new Set(ids.source_trace);
  const strategyIds = new Set(ids.experience_strategies);
  const knownIds = new Set(["strategy_basis"].concat(
    ids.key_insights,
    ids.experience_strategies,
    ids.design_criteria,
    ids.strategy_boundaries,
  ));

  if (isObject(data.strategy_basis) && !sourceIds.has(data.strategy_basis.source_ref)) {
    errors.push("strategy_basis.source_ref 必须引用存在的 ST 编号");
  }

  function requireSourceRefs(items, field) {
    if (!Array.isArray(items)) return;
    items.forEach(function checkItem(item, index) {
      if (!isObject(item)) return;
      ["evidence_refs", "source_refs"].forEach(function checkKey(key) {
        if (!Array.isArray(item[key])) return;
        item[key].forEach(function checkRef(ref, refIndex) {
          if (!sourceIds.has(ref)) {
            errors.push(field + "[" + index + "]." + key + "[" + refIndex + "] 必须引用存在的 ST 编号");
          }
        });
      });
    });
  }

  requireSourceRefs(data.key_insights, "key_insights");
  requireSourceRefs(data.experience_strategies, "experience_strategies");
  requireSourceRefs(data.design_criteria, "design_criteria");

  ["design_criteria", "strategy_boundaries"].forEach(function checkStrategyRefs(field) {
    const items = data[field];
    if (!Array.isArray(items)) return;
    items.forEach(function checkItem(item, index) {
      if (!isObject(item) || !Array.isArray(item.strategy_refs)) return;
      item.strategy_refs.forEach(function checkRef(ref, refIndex) {
        if (!strategyIds.has(ref)) {
          errors.push(field + "[" + index + "].strategy_refs[" + refIndex + "] 必须引用存在的 ES 编号");
        }
      });
    });
  });

  if (Array.isArray(data.source_trace)) {
    data.source_trace.forEach(function checkSource(item, index) {
      if (!isObject(item) || !Array.isArray(item.used_for)) return;
      item.used_for.forEach(function checkUsedFor(ref, refIndex) {
        if (!knownIds.has(ref)) {
          errors.push("source_trace[" + index + "].used_for[" + refIndex + "] 必须引用存在的对象编号或 strategy_basis");
        }
      });
    });
  }
}

function validateStatus(data, errors) {
  if (!RESULT_STATUS_VALUES.has(data.result_status)) {
    errors.push("result_status 必须为 strategy_ready 或 no_independent_strategy");
    return;
  }
  const counts = {
    insights: Array.isArray(data.key_insights) ? data.key_insights.length : 0,
    strategies: Array.isArray(data.experience_strategies) ? data.experience_strategies.length : 0,
    criteria: Array.isArray(data.design_criteria) ? data.design_criteria.length : 0,
    boundaries: Array.isArray(data.strategy_boundaries) ? data.strategy_boundaries.length : 0,
  };
  if (data.result_status === "strategy_ready" && (
    counts.insights === 0 || counts.strategies === 0 || counts.criteria === 0 || counts.boundaries === 0
  )) {
    errors.push("strategy_ready 时关键判断、策略、设计标准和策略边界均不得为空");
  }
  if (data.result_status === "no_independent_strategy" && (
    counts.strategies !== 0 || counts.criteria !== 0 || counts.boundaries !== 0
  )) {
    errors.push("no_independent_strategy 时策略、设计标准和策略边界必须为空数组");
  }
}

function validate(data) {
  const errors = [];
  if (!isObject(data)) return ["根节点必须是 JSON 对象"];

  const allowedRoot = new Set(ROOT_FIELDS);
  ROOT_FIELDS.forEach(function requireRoot(field) {
    if (!Object.prototype.hasOwnProperty.call(data, field)) errors.push("root." + field + " 缺失");
  });
  Object.keys(data).forEach(function rejectUnknownRoot(field) {
    if (!allowedRoot.has(field)) errors.push("root." + field + " 不允许出现");
  });

  ["skill", "version", "project_name", "artifact_md"].forEach(function validateRootString(field) {
    if (Object.prototype.hasOwnProperty.call(data, field)) validateString(data[field], field, errors);
  });
  if (Object.prototype.hasOwnProperty.call(data, "generated_at")) validateGeneratedAt(data.generated_at, errors);
  if (data.skill !== "uxb") errors.push("skill 必须为 uxb");
  if (data.version !== "10.0") errors.push("version 必须为 10.0");
  if (data.artifact_md !== "spark-output/uxb_output.md") {
    errors.push("artifact_md 必须为 spark-output/uxb_output.md");
  }

  validateStrategyBasis(data.strategy_basis, errors);
  const ids = {};
  Object.keys(ARRAY_SCHEMAS).forEach(function validateArray(field) {
    ids[field] = validateObjectArray(data[field], field, ARRAY_SCHEMAS[field], errors);
  });
  validateStatus(data, errors);
  validateReferences(data, ids, errors);
  return errors;
}

function main() {
  const targetPath = process.argv[2];
  if (!targetPath) {
    console.error("用法：node validate-context.js <uxb.json>");
    process.exit(1);
  }
  let data;
  try {
    data = JSON.parse(fs.readFileSync(targetPath, "utf8"));
  } catch (error) {
    console.error("无法读取或解析 JSON：" + error.message);
    process.exit(1);
  }
  const errors = validate(data);
  if (errors.length > 0) {
    console.error("UXB Context 10.0 校验失败：\n- " + errors.join("\n- "));
    process.exit(1);
  }
  console.log("UXB Context 10.0 结构校验通过。");
}

if (require.main === module) main();

module.exports = { validate };
