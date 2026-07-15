"use strict";

const fs = require("fs");
const path = require("path");

const allowedModes = new Set([
  "stories-chain",
  "uxb-chain",
  "framing-chain",
  "prd-standalone",
  "unknown",
]);
const allowedResultLevels = new Set(["full", "completed", "skeleton", "unknown"]);
const allowedReadiness = new Set(["通过", "部分通过", "不通过", "unknown"]);
const allowedConfidence = new Set(["高", "中", "低", "unknown"]);

const rootKeys = [
  "skill",
  "version",
  "generated_at",
  "project_name",
  "artifact_md",
  "source_refs",
  "read_sections",
  "mode",
  "completion_used",
  "result_level",
  "journey_subject",
  "readiness",
  "skeleton_result",
  "stages",
  "key_transitions",
  "gaps",
  "user_completion",
];

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function pushError(errors, fieldPath, message) {
  errors.push(`${fieldPath} ${message}`);
}

function requireExactKeys(value, keys, fieldPath, errors) {
  if (!isObject(value)) {
    pushError(errors, fieldPath, "must be an object");
    return false;
  }

  const expected = new Set(keys);
  for (const key of keys) {
    if (!Object.prototype.hasOwnProperty.call(value, key)) {
      pushError(errors, `${fieldPath}.${key}`, "is required");
    }
  }
  for (const key of Object.keys(value)) {
    if (!expected.has(key)) {
      pushError(errors, `${fieldPath}.${key}`, "is not allowed");
    }
  }
  return true;
}

function requireString(value, fieldPath, errors) {
  if (typeof value !== "string" || !value.trim()) {
    pushError(errors, fieldPath, "must be a non-empty string");
  }
}

function requireArray(value, fieldPath, errors) {
  if (!Array.isArray(value)) {
    pushError(errors, fieldPath, "must be an array");
    return false;
  }
  return true;
}

function requireEnum(value, allowed, fieldPath, errors) {
  requireString(value, fieldPath, errors);
  if (typeof value === "string" && !allowed.has(value)) {
    pushError(errors, fieldPath, `has invalid value: ${value}`);
  }
}

function validateJourneySubject(value, errors) {
  const keys = [
    "primary_role",
    "journey_scope",
    "journey_type",
    "start_condition",
    "end_condition",
  ];
  if (!requireExactKeys(value, keys, "journey_subject", errors)) return;
  for (const key of keys) requireString(value[key], `journey_subject.${key}`, errors);
}

function validateReadiness(value, errors) {
  const keys = [
    "role_clarity",
    "scope_clarity",
    "stage_divisibility",
    "touchpoint_recoverability",
    "painpoint_evidence",
  ];
  if (!requireExactKeys(value, keys, "readiness", errors)) return;
  for (const key of keys) requireEnum(value[key], allowedReadiness, `readiness.${key}`, errors);
}

function validateSkeletonResult(value, errors) {
  const keys = [
    "primary_role_candidates",
    "journey_theme",
    "rough_stages",
    "current_gaps",
    "reason_full_journey_unavailable",
    "suggested_next_step",
  ];
  if (!requireExactKeys(value, keys, "skeleton_result", errors)) return;
  for (const key of ["primary_role_candidates", "rough_stages", "current_gaps"]) {
    requireArray(value[key], `skeleton_result.${key}`, errors);
  }
  for (const key of ["journey_theme", "reason_full_journey_unavailable", "suggested_next_step"]) {
    requireString(value[key], `skeleton_result.${key}`, errors);
  }
}

function validateStage(value, index, errors) {
  const fieldPath = `stages[${index}]`;
  const keys = [
    "stage_id",
    "stage_name",
    "user_goal",
    "actions",
    "touchpoints",
    "user_voice",
    "emotion",
    "confidence",
    "confidence_reason",
    "pain_points",
    "dropout_risk",
    "opportunities",
    "evidence",
  ];
  if (!requireExactKeys(value, keys, fieldPath, errors)) return;

  for (const key of [
    "stage_id",
    "stage_name",
    "user_goal",
    "user_voice",
    "emotion",
    "confidence_reason",
  ]) {
    requireString(value[key], `${fieldPath}.${key}`, errors);
  }
  requireEnum(value.confidence, allowedConfidence, `${fieldPath}.confidence`, errors);
  for (const key of ["actions", "touchpoints", "pain_points", "opportunities", "evidence"]) {
    requireArray(value[key], `${fieldPath}.${key}`, errors);
  }

  if (requireExactKeys(value.dropout_risk, ["level", "reason"], `${fieldPath}.dropout_risk`, errors)) {
    requireString(value.dropout_risk.level, `${fieldPath}.dropout_risk.level`, errors);
    requireString(value.dropout_risk.reason, `${fieldPath}.dropout_risk.reason`, errors);
  }
}

function validateTransition(value, index, errors) {
  const fieldPath = `key_transitions[${index}]`;
  const keys = ["from_stage", "to_stage", "trigger", "risk"];
  if (!requireExactKeys(value, keys, fieldPath, errors)) return;
  for (const key of keys) requireString(value[key], `${fieldPath}.${key}`, errors);
}

function validateGap(value, index, errors) {
  const fieldPath = `gaps[${index}]`;
  const keys = ["gap", "impact", "needed_input"];
  if (!requireExactKeys(value, keys, fieldPath, errors)) return;
  for (const key of keys) requireString(value[key], `${fieldPath}.${key}`, errors);
}

function validateUserCompletion(value, errors) {
  const keys = [
    "primary_role",
    "journey_scope",
    "journey_type",
    "start_condition",
    "end_condition",
    "suspected_breakpoints",
    "evidence_sources",
    "notes",
  ];
  if (!requireExactKeys(value, keys, "user_completion", errors)) return;
  for (const key of [
    "primary_role",
    "journey_scope",
    "journey_type",
    "start_condition",
    "end_condition",
    "notes",
  ]) {
    requireString(value[key], `user_completion.${key}`, errors);
  }
  requireArray(value.suspected_breakpoints, "user_completion.suspected_breakpoints", errors);
  requireArray(value.evidence_sources, "user_completion.evidence_sources", errors);
}

function validateRoot(data) {
  const errors = [];
  if (!requireExactKeys(data, rootKeys, "root", errors)) return errors;

  for (const key of ["version", "generated_at", "project_name"]) {
    requireString(data[key], key, errors);
  }
  if (data.skill !== "journey-analysis") pushError(errors, "skill", "must equal journey-analysis");
  if (data.artifact_md !== "spark-output/journey_analysis.md") {
    pushError(errors, "artifact_md", "must equal spark-output/journey_analysis.md");
  }
  requireArray(data.source_refs, "source_refs", errors);
  requireArray(data.read_sections, "read_sections", errors);
  requireEnum(data.mode, allowedModes, "mode", errors);
  if (typeof data.completion_used !== "boolean") {
    pushError(errors, "completion_used", "must be a boolean");
  }
  requireEnum(data.result_level, allowedResultLevels, "result_level", errors);

  validateJourneySubject(data.journey_subject, errors);
  validateReadiness(data.readiness, errors);
  validateSkeletonResult(data.skeleton_result, errors);
  validateUserCompletion(data.user_completion, errors);

  if (requireArray(data.stages, "stages", errors)) {
    data.stages.forEach((stage, index) => validateStage(stage, index, errors));
    if (["full", "completed"].includes(data.result_level) && data.stages.length === 0) {
      pushError(errors, "stages", "must not be empty for full or completed results");
    }
  }
  if (requireArray(data.key_transitions, "key_transitions", errors)) {
    data.key_transitions.forEach((transition, index) => validateTransition(transition, index, errors));
  }
  if (requireArray(data.gaps, "gaps", errors)) {
    data.gaps.forEach((gap, index) => validateGap(gap, index, errors));
  }

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
    parsed = JSON.parse(fs.readFileSync(resolvedPath, "utf8"));
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
