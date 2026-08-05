"use strict";

const fs = require("fs");
const path = require("path");

const ROOT_FIELDS = [
  "skill",
  "version",
  "generated_at",
  "project_name",
  "artifact_md",
  "decisions",
  "cross_cutting_constraints",
  "upstream_trace",
];

const ARRAY_SCHEMAS = {
  decisions: {
    prefix: "ED",
    required: {
      task: "string",
      roles: "nonempty-string-array",
      decision: "string",
    },
    optional: {
      business_objects: "nonempty-string-array",
      states: "nonempty-string-array",
      conditions: "nonempty-string-array",
      additional_constraints: "nonempty-string-array",
      source_refs: "nonempty-string-array",
    },
  },
  cross_cutting_constraints: {
    prefix: "CC",
    required: {
      constraint: "string",
      applies_to: "nonempty-string-array",
    },
    optional: {},
  },
  upstream_trace: {
    prefix: "UT",
    required: {
      source_type: "string",
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
  }
}

function validateStructuredObject(value, field, required, optional, errors) {
  if (!isObject(value)) {
    errors.push(field + " 必须是对象");
    return;
  }

  const allowed = new Set(Object.keys(required).concat(Object.keys(optional)));

  Object.keys(required).forEach(function validateRequired(key) {
    if (!Object.prototype.hasOwnProperty.call(value, key)) {
      errors.push(field + "." + key + " 缺失");
      return;
    }
    validateType(value[key], field + "." + key, required[key], errors);
  });

  Object.keys(optional).forEach(function validateOptional(key) {
    if (Object.prototype.hasOwnProperty.call(value, key)) {
      validateType(value[key], field + "." + key, optional[key], errors);
    }
  });

  Object.keys(value).forEach(function rejectUnknown(key) {
    if (!allowed.has(key)) {
      errors.push(field + "." + key + " 不允许出现");
    }
  });
}

function validateObjectArray(value, field, config, errors) {
  if (!Array.isArray(value)) {
    errors.push(field + " 必须是数组");
    return;
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
    if (ids.has(item.id)) {
      errors.push(field + " 内编号重复：" + item.id);
    }
    ids.add(item.id);
  });
}

function validateGeneratedAt(value, errors) {
  validateString(value, "generated_at", errors);
  if (
    typeof value === "string"
    && !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(value)
  ) {
    errors.push("generated_at 必须使用 ISO 8601 时间格式");
  }
}

function validate(data) {
  const errors = [];

  if (!isObject(data)) {
    return ["根节点必须是 JSON 对象"];
  }

  const allowedRoot = new Set(ROOT_FIELDS);

  ROOT_FIELDS.forEach(function requireRoot(field) {
    if (!Object.prototype.hasOwnProperty.call(data, field)) {
      errors.push("root." + field + " 缺失");
    }
  });

  Object.keys(data).forEach(function rejectUnknownRoot(field) {
    if (!allowedRoot.has(field)) {
      errors.push("root." + field + " 不允许出现");
    }
  });

  ["skill", "version", "project_name", "artifact_md"].forEach(function validateRootString(field) {
    if (Object.prototype.hasOwnProperty.call(data, field)) {
      validateString(data[field], field, errors);
    }
  });

  if (Object.prototype.hasOwnProperty.call(data, "generated_at")) {
    validateGeneratedAt(data.generated_at, errors);
  }

  if (data.skill !== "uxb") {
    errors.push("skill 必须为 uxb");
  }
  if (data.version !== "9.0") {
    errors.push("version 必须为 9.0");
  }
  if (data.artifact_md !== "spark-output/uxb_output.md") {
    errors.push("artifact_md 必须为 spark-output/uxb_output.md");
  }

  Object.keys(ARRAY_SCHEMAS).forEach(function validateArray(field) {
    if (Object.prototype.hasOwnProperty.call(data, field)) {
      validateObjectArray(data[field], field, ARRAY_SCHEMAS[field], errors);
    }
  });

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
    console.error("JSON 读取或解析失败：" + resolved);
    console.error(error.message);
    process.exit(1);
  }

  const errors = validate(data);

  if (errors.length > 0) {
    errors.forEach(function printError(error) {
      console.error(error);
    });
    process.exit(1);
  }

  console.log("UXB Context 9.0 结构校验通过。");
}

if (require.main === module) {
  main();
}

module.exports = { ROOT_FIELDS, validate };
