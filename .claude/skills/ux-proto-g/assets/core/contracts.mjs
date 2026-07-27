import path from "node:path";
import { assertKeys, assertString, assertStringArray, fail, stableObject, uniqueSorted } from "./common.mjs";

const sourceTypes = new Set(["pack", "overlay"]);
const assetKinds = new Set(["Knowledge", "Pattern", "Template", "Pack Component"]);
const lifecycles = new Set(["draft", "active", "deprecated"]);
const relationTypes = new Set(["requires", "supports", "recommended-for", "distinguishes-from"]);
const sourceIdPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const assetIdPattern = /^(knowledge|pattern|template|component)\.[a-z0-9]+(?:-[a-z0-9]+)*$/;
const recommendationIdPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const kindPrefix = new Map([
  ["Knowledge", "knowledge"],
  ["Pattern", "pattern"],
  ["Template", "template"],
  ["Pack Component", "component"]
]);

function assertRelativeFile(value, label) {
  assertString(value, label);
  if (path.isAbsolute(value) || value.includes("\\") || value.split("/").includes("..")) fail("invalid-asset-path", `${label} 路径无效：${value}。`, { path: value });
}

function validateSelection(value, label) {
  assertKeys(value, ["useWhen", "avoidWhen"], label);
  assertStringArray(value.useWhen, `${label}.useWhen`);
  assertStringArray(value.avoidWhen, `${label}.avoidWhen`);
  return { useWhen: [...value.useWhen], avoidWhen: [...value.avoidWhen] };
}

function validateApiRow(value, label) {
  assertKeys(value, ["name", "type", "required", "default", "description"], label);
  assertString(value.name, `${label}.name`);
  assertString(value.type, `${label}.type`);
  if (typeof value.required !== "boolean") fail("invalid-component-api", `${label}.required 必须是 boolean。`);
  if (!(value.default === null || ["string", "number", "boolean"].includes(typeof value.default))) fail("invalid-component-api", `${label}.default 必须是 JSON scalar 或 null。`);
  assertString(value.description, `${label}.description`);
  return stableObject(value);
}

function validateComponentApi(value, label) {
  assertKeys(value, ["mainExport", "properties", "types"], label);
  assertString(value.mainExport, `${label}.mainExport`);
  if (!Array.isArray(value.properties)) fail("invalid-component-api", `${label}.properties 必须是数组。`);
  const properties = value.properties.map((row, index) => validateApiRow(row, `${label}.properties[${index}]`));
  if (new Set(properties.map((row) => row.name)).size !== properties.length) fail("invalid-component-api", `${label}.properties.name 必须唯一。`);
  const types = value.types ?? [];
  if (!Array.isArray(types)) fail("invalid-component-api", `${label}.types 必须是数组。`);
  const normalizedTypes = types.map((item, index) => {
    const typeLabel = `${label}.types[${index}]`;
    assertKeys(item, ["name", "properties"], typeLabel);
    assertString(item.name, `${typeLabel}.name`);
    if (!Array.isArray(item.properties)) fail("invalid-component-api", `${typeLabel}.properties 必须是数组。`);
    const rows = item.properties.map((row, rowIndex) => validateApiRow(row, `${typeLabel}.properties[${rowIndex}]`));
    if (new Set(rows.map((row) => row.name)).size !== rows.length) fail("invalid-component-api", `${typeLabel}.properties.name 必须唯一。`);
    return { name: item.name, properties: rows };
  });
  if (new Set(normalizedTypes.map((item) => item.name)).size !== normalizedTypes.length) fail("invalid-component-api", `${label}.types.name 必须唯一。`);
  return stableObject({ mainExport: value.mainExport, properties, types: normalizedTypes });
}

function validateUsage(value, label) {
  assertKeys(value, ["componentOwns", "consumerProvides", "doesNotOwn", "guidance", "limitations"], label);
  for (const field of ["componentOwns", "consumerProvides", "doesNotOwn"]) assertStringArray(value[field], `${label}.${field}`);
  if ("guidance" in value) assertStringArray(value.guidance, `${label}.guidance`);
  if ("limitations" in value) assertStringArray(value.limitations, `${label}.limitations`);
  return stableObject({
    componentOwns: value.componentOwns,
    consumerProvides: value.consumerProvides,
    doesNotOwn: value.doesNotOwn,
    ...(value.guidance ? { guidance: value.guidance } : {}),
    ...(value.limitations ? { limitations: value.limitations } : {})
  });
}

export function validateSourceManifest(value, label = "manifest") {
  assertKeys(value, ["schemaVersion", "id", "type", "version", "note", "consumption", "runtimeTheme"], label);
  if (value.schemaVersion !== 2) fail("unsupported-schema", `${label}.schemaVersion 只支持 2。`, { actual: value.schemaVersion });
  assertString(value.id, `${label}.id`);
  if (!sourceIdPattern.test(value.id)) fail("invalid-source-id", `${label}.id 格式无效：${value.id}。`, { id: value.id });
  if (!sourceTypes.has(value.type)) fail("invalid-source-type", `${label}.type 只允许 pack 或 overlay。`, { type: value.type });
  if (value.type === "overlay") {
    for (const forbidden of ["version", "consumption", "runtimeTheme"]) if (forbidden in value) fail("overlay-forbidden-field", `Overlay 不允许声明 ${forbidden}。`, { field: forbidden });
    if ("note" in value) assertString(value.note, `${label}.note`);
    return stableObject(value);
  }
  assertString(value.version, `${label}.version`);
  if (!/^\d+\.\d+\.\d+$/.test(value.version)) fail("invalid-version", `${label}.version 必须是 semver。`, { version: value.version });
  assertString(value.note, `${label}.note`);
  assertKeys(value.consumption, ["baseline", "recommendations", "review"], `${label}.consumption`);
  assertKeys(value.consumption.baseline, ["id", "artifact"], `${label}.consumption.baseline`);
  if (!recommendationIdPattern.test(value.consumption.baseline.id ?? "")) fail("invalid-baseline", `${label}.consumption.baseline.id 无效。`);
  assertRelativeFile(value.consumption.baseline.artifact, `${label}.consumption.baseline.artifact`);
  if (!Array.isArray(value.consumption.recommendations)) fail("invalid-recommendations", `${label}.consumption.recommendations 必须是数组。`);
  const recommendationIds = new Set();
  const recommendations = value.consumption.recommendations.map((item, index) => {
    const itemLabel = `${label}.consumption.recommendations[${index}]`;
    assertKeys(item, ["id", "assetId"], itemLabel);
    if (!recommendationIdPattern.test(item.id ?? "") || recommendationIds.has(item.id)) fail("invalid-recommendation", `recommendation id 无效或重复：${item.id}。`, { id: item.id });
    assertString(item.assetId, `${itemLabel}.assetId`);
    recommendationIds.add(item.id);
    return { id: item.id, assetId: item.assetId };
  }).sort((a, b) => a.id.localeCompare(b.id));
  assertKeys(value.consumption.review, ["assets"], `${label}.consumption.review`);
  assertStringArray(value.consumption.review.assets, `${label}.consumption.review.assets`);
  if (value.runtimeTheme) {
    assertKeys(value.runtimeTheme, ["artifacts"], `${label}.runtimeTheme`);
    assertStringArray(value.runtimeTheme.artifacts, `${label}.runtimeTheme.artifacts`, { nonEmpty: true });
    for (const artifact of value.runtimeTheme.artifacts) assertRelativeFile(artifact, `${label}.runtimeTheme.artifacts[]`);
  }
  return stableObject({
    ...value,
    consumption: {
      baseline: value.consumption.baseline,
      recommendations,
      review: { assets: [...value.consumption.review.assets] }
    },
    ...(value.runtimeTheme ? { runtimeTheme: { artifacts: uniqueSorted(value.runtimeTheme.artifacts) } } : {})
  });
}

export function validateAssetDescriptor(value, label = "asset") {
  assertKeys(value, ["schemaVersion", "id", "kind", "lifecycle", "name", "summary", "selection", "relations", "requires", "content", "entry", "artifacts", "authoring", "api", "usage"], label);
  if (value.schemaVersion !== 2) fail("unsupported-schema", `${label}.schemaVersion 只支持 2。`, { actual: value.schemaVersion });
  assertString(value.id, `${label}.id`);
  if (!assetIdPattern.test(value.id)) fail("invalid-asset-id", `资产 ID 格式无效：${value.id}。`, { id: value.id });
  if (!assetKinds.has(value.kind) || value.id.split(".")[0] !== kindPrefix.get(value.kind)) fail("invalid-asset-kind", `${value.id} 的 kind/ID 前缀不匹配。`, { kind: value.kind });
  if (!lifecycles.has(value.lifecycle)) fail("invalid-lifecycle", `${value.id} 的 lifecycle 无效。`, { lifecycle: value.lifecycle });
  if ("name" in value) assertString(value.name, `${value.id}.name`);
  assertString(value.summary, `${value.id}.summary`);
  const selection = validateSelection(value.selection, `${value.id}.selection`);
  assertStringArray(value.requires ?? [], `${value.id}.requires`);
  if (!Array.isArray(value.relations ?? [])) fail("invalid-relations", `${value.id}.relations 必须是数组。`, { id: value.id });
  const relations = (value.relations ?? []).map((relation, index) => {
    assertKeys(relation, ["type", "target"], `${value.id}.relations[${index}]`);
    if (!relationTypes.has(relation.type)) fail("invalid-relation-type", `${value.id} 包含未知 relation type：${relation.type}。`, { assetId: value.id, type: relation.type });
    assertString(relation.target, `${value.id}.relations[${index}].target`);
    return relation;
  }).sort((a, b) => a.target.localeCompare(b.target) || a.type.localeCompare(b.type));
  const result = { ...value, selection, requires: uniqueSorted(value.requires ?? []), relations };
  if (value.kind === "Knowledge" || value.kind === "Pattern") {
    if (!value.content || typeof value.content !== "object" || Array.isArray(value.content) || !Object.keys(value.content).length) fail("missing-content", `${value.id} 必须声明语义 content。`, { id: value.id });
    for (const forbidden of ["entry", "artifacts", "authoring", "api", "usage"]) if (forbidden in value) fail("invalid-kind-field", `${value.id} 不允许声明 ${forbidden}。`);
  }
  if (value.kind === "Template") {
    assertString(value.entry, `${value.id}.entry`);
    assertStringArray(value.artifacts ?? [], `${value.id}.artifacts`);
    assertKeys(value.authoring, ["mainExport", "customizationSurfaces"], `${value.id}.authoring`);
    assertString(value.authoring.mainExport, `${value.id}.authoring.mainExport`);
    const surfaces = value.authoring.customizationSurfaces ?? [];
    if (!Array.isArray(surfaces)) fail("invalid-template-authoring", `${value.id}.authoring.customizationSurfaces 必须是数组。`);
    const ids = new Set();
    for (const [index, surface] of surfaces.entries()) {
      const surfaceLabel = `${value.id}.authoring.customizationSurfaces[${index}]`;
      assertKeys(surface, ["id", "purpose", "binding"], surfaceLabel);
      if (!recommendationIdPattern.test(surface.id ?? "") || ids.has(surface.id)) fail("invalid-template-authoring", `${surfaceLabel}.id 无效或重复。`);
      assertString(surface.purpose, `${surfaceLabel}.purpose`);
      assertKeys(surface.binding, ["type", "name"], `${surfaceLabel}.binding`);
      if (surface.binding.type !== "prop") fail("invalid-template-authoring", `${surfaceLabel}.binding.type 只支持 prop。`);
      assertString(surface.binding.name, `${surfaceLabel}.binding.name`);
      ids.add(surface.id);
    }
    result.authoring = stableObject({ mainExport: value.authoring.mainExport, customizationSurfaces: surfaces });
    for (const forbidden of ["content", "api", "usage"]) if (forbidden in value) fail("invalid-kind-field", `${value.id} 不允许声明 ${forbidden}。`);
  }
  if (value.kind === "Pack Component") {
    assertString(value.entry, `${value.id}.entry`);
    assertStringArray(value.artifacts ?? [], `${value.id}.artifacts`);
    result.api = validateComponentApi(value.api, `${value.id}.api`);
    result.usage = validateUsage(value.usage, `${value.id}.usage`);
    for (const forbidden of ["content", "authoring"]) if (forbidden in value) fail("invalid-kind-field", `${value.id} 不允许声明 ${forbidden}。`);
  }
  for (const relative of [value.entry, ...(value.artifacts ?? [])].filter(Boolean)) assertRelativeFile(relative, `${value.id}.artifact`);
  return stableObject(result);
}
