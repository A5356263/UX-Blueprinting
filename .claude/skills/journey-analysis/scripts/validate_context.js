"use strict";

const fs = require("fs");
const path = require("path");

const allowedConfidence = new Set(["高", "中", "低"]);
const allowedDownstream = new Set(["蓝图", "故事", "待确认"]);

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function pushError(errors, fieldPath, message) {
  errors.push(`${fieldPath} ${message}`);
}

function validateOpportunity(opportunity, fieldPath, errors) {
  if (!isObject(opportunity)) {
    pushError(errors, fieldPath, "must be an object");
    return;
  }

  if (typeof opportunity.direction !== "string" || !opportunity.direction.trim()) {
    pushError(errors, `${fieldPath}.direction`, "is required");
  }

  if (typeof opportunity.downstream_hint !== "string" || !opportunity.downstream_hint.trim()) {
    pushError(errors, `${fieldPath}.downstream_hint`, "is required");
  } else if (!allowedDownstream.has(opportunity.downstream_hint)) {
    pushError(errors, `${fieldPath}.downstream_hint`, "must be one of: 蓝图, 故事, 待确认");
  }
}

function validateTransition(transition, fieldPath, errors) {
  if (!isObject(transition)) {
    pushError(errors, fieldPath, "must be an object");
    return;
  }

  for (const key of ["from", "to", "trigger"]) {
    if (typeof transition[key] !== "string" || !transition[key].trim()) {
      pushError(errors, `${fieldPath}.${key}`, "is required");
    }
  }
}

function validateStage(stage, fieldPath, errors) {
  if (!isObject(stage)) {
    pushError(errors, fieldPath, "must be an object");
    return;
  }

  for (const key of ["name", "goal", "user_voice", "confidence_reason", "dropout_risk"]) {
    if (typeof stage[key] !== "string" || !stage[key].trim()) {
      pushError(errors, `${fieldPath}.${key}`, "is required");
    }
  }

  if (typeof stage.confidence !== "string" || !stage.confidence.trim()) {
    pushError(errors, `${fieldPath}.confidence`, "is required");
  } else if (!allowedConfidence.has(stage.confidence)) {
    pushError(errors, `${fieldPath}.confidence`, "must be one of: 高, 中, 低");
  }

  for (const key of ["actions", "touchpoints", "pain_points", "opportunities"]) {
    if (!Array.isArray(stage[key])) {
      pushError(errors, `${fieldPath}.${key}`, "must be an array");
    }
  }

  if (Array.isArray(stage.opportunities)) {
    stage.opportunities.forEach((opportunity, index) => {
      validateOpportunity(opportunity, `${fieldPath}.opportunities[${index}]`, errors);
    });
  }
}

function validateJourney(journey, fieldPath, errors) {
  if (!isObject(journey)) {
    pushError(errors, fieldPath, "must be an object");
    return;
  }

  for (const key of ["role", "summary"]) {
    if (typeof journey[key] !== "string" || !journey[key].trim()) {
      pushError(errors, `${fieldPath}.${key}`, "is required");
    }
  }

  if (!Array.isArray(journey.stages)) {
    pushError(errors, `${fieldPath}.stages`, "must be an array");
  } else {
    journey.stages.forEach((stage, index) => {
      validateStage(stage, `${fieldPath}.stages[${index}]`, errors);
    });
  }

  if (journey.key_transitions !== undefined) {
    if (!Array.isArray(journey.key_transitions)) {
      pushError(errors, `${fieldPath}.key_transitions`, "must be an array");
    } else {
      journey.key_transitions.forEach((transition, index) => {
        validateTransition(transition, `${fieldPath}.key_transitions[${index}]`, errors);
      });
    }
  }
}

function validateRoot(data) {
  const errors = [];

  if (!isObject(data)) {
    pushError(errors, "root", "must be an object");
    return errors;
  }

  if (!Array.isArray(data.journeys)) {
    pushError(errors, "journeys", "must be an array");
    return errors;
  }

  data.journeys.forEach((journey, index) => {
    validateJourney(journey, `journeys[${index}]`, errors);
  });

  return errors;
}

function main() {
  const filePath = process.argv[2];

  if (!filePath) {
    console.error("context_json_path is required");
    process.exit(1);
  }

  const resolvedPath = path.resolve(process.cwd(), filePath);
  let parsed;

  try {
    const raw = fs.readFileSync(resolvedPath, "utf8");
    parsed = JSON.parse(raw);
  } catch (error) {
    console.error(`failed to read or parse JSON: ${resolvedPath}`);
    console.error(error.message);
    process.exit(1);
  }

  const errors = validateRoot(parsed);

  if (errors.length > 0) {
    errors.forEach((message) => console.error(message));
    process.exit(1);
  }

  console.log("journey-analysis context valid");
}

main();
