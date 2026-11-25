import path from "node:path";
import { fail } from "./common.mjs";

const assetKinds = new Set(["Knowledge", "Pattern", "Template", "Pack Component"]);
const sourceIdPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const assetIdPattern = /^(knowledge|pattern|template|component)\.[a-z0-9]+(?:-[a-z0-9]+)*$/;
const localIdPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const identifierPattern = /^[A-Za-z_$][A-Za-z0-9_$]*$/;
const kindPrefix = new Map([
  ["Knowledge", "knowledge"],
  ["Pattern", "pattern"],
  ["Template", "template"],
  ["Pack Component", "component"]
]);
export const canonicalRuntimeThemeArtifactBasenames = Object.freeze([
  "alias-vars.generated.css",
  "antd.generated.css",
  "theme-config.generated.mjs"
]);
const commonFields = ["id", "kind", "title", "abstract"];
const knownDescriptorFields = new Set([
  ...commonFields,
  "content",
  "entry",
  "artifacts",
  "authoring",
  "configuration",
  "api",
  "usage"
]);

const pointerToken = (value) => String(value).replaceAll("~", "~0").replaceAll("/", "~1");
const childPointer = (pointer, key) => `${pointer}/${pointerToken(key)}`;
const compareStrings = (left, right) => left < right ? -1 : left > right ? 1 : 0;
const diagnosticContext = ({ assetId, file, pointer, ...rest }) => ({
  ...(assetId ? { assetId } : {}),
  ...(file ? { file } : {}),
  ...(pointer !== undefined ? { pointer } : {}),
  ...rest
});

function assertObject(value, label, context = {}) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    fail("invalid-contract", `${label} 必须是对象。`, diagnosticContext(context));
  }
}

function assertClosedObject(value, fields, label, context = {}) {
  assertObject(value, label, context);
  const allowed = new Set(fields);
  const extra = Object.keys(value).filter((key) => !allowed.has(key));
  if (extra.length) {
    const pointer = childPointer(context.pointer ?? "", extra[0]);
    fail("unknown-field", `${label} 包含未知字段：${extra.join("、")}。`, diagnosticContext({ ...context, pointer, fields: extra }));
  }
  const missing = fields.filter((key) => !Object.hasOwn(value, key));
  if (missing.length) {
    const pointer = childPointer(context.pointer ?? "", missing[0]);
    fail("missing-field", `${label} 缺少必填字段：${missing.join("、")}。`, diagnosticContext({ ...context, pointer, fields: missing }));
  }
}

function assertString(value, label, context = {}) {
  if (typeof value !== "string" || !value.trim()) fail("invalid-contract", `${label} 必须是非空字符串。`, diagnosticContext(context));
}

function assertIdentifier(value, label, context = {}) {
  assertString(value, label, context);
  if (!identifierPattern.test(value)) fail("invalid-contract", `${label} 必须是 TypeScript identifier。`, diagnosticContext(context));
}

function assertStringArray(value, label, context = {}, { nonEmpty = false } = {}) {
  if (!Array.isArray(value) || (nonEmpty && !value.length)) {
    fail("invalid-contract", `${label} 必须是${nonEmpty ? "非空" : ""}字符串数组。`, diagnosticContext(context));
  }
  for (const [index, item] of value.entries()) {
    if (typeof item !== "string" || !item.trim()) {
      fail("invalid-contract", `${label} 必须只包含非空字符串。`, diagnosticContext({ ...context, pointer: childPointer(context.pointer ?? "", index) }));
    }
  }
  const first = new Map();
  for (const [index, item] of value.entries()) {
    if (first.has(item)) {
      fail("invalid-contract", `${label} 不允许重复值：${item}。`, diagnosticContext({ ...context, pointer: childPointer(context.pointer ?? "", index), duplicateOf: first.get(item) }));
    }
    first.set(item, index);
  }
}

function assertRelativeFile(value, label, context = {}) {
  assertString(value, label, context);
  const segments = typeof value === "string" ? value.split("/") : [];
  if (path.isAbsolute(value) || value.includes("\\") || segments.includes("..") || segments.includes("") || segments.includes(".")) {
    fail("invalid-asset-path", `${label} 路径无效：${value}。`, diagnosticContext({ ...context, path: value }));
  }
}

function assertTypeScriptEntry(value, label, context = {}) {
  assertRelativeFile(value, label, context);
  if (!/\.tsx?$/.test(value)) fail("invalid-entry", `${label} 必须指向 TypeScript source。`, diagnosticContext(context));
}

function assertAssetId(value, context, category = "invalid-asset-id") {
  if (typeof value !== "string" || !assetIdPattern.test(value)) {
    fail(category, `资产 ID 格式无效：${value ?? "(missing)"}。`, diagnosticContext({ ...context, value: value ?? null }));
  }
}

function validateJsonValue(value, context, links) {
  if (value === null || typeof value === "string" || typeof value === "boolean") return;
  if (typeof value === "number") {
    if (Number.isFinite(value)) return;
    fail("invalid-content", "content 只允许标准 JSON number。", diagnosticContext(context));
  }
  if (Array.isArray(value)) {
    for (const [index, item] of value.entries()) validateJsonValue(item, { ...context, pointer: childPointer(context.pointer, index) }, links);
    return;
  }
  if (!value || typeof value !== "object" || Object.getPrototypeOf(value) !== Object.prototype) {
    fail("invalid-content", "content 只允许标准 JSON value。", diagnosticContext(context));
  }
  if (Object.hasOwn(value, "load") && !Object.hasOwn(value, "assetLink")) {
    fail("invalid-reserved-field", "load 只能与同一 object 的 assetLink 共存。", diagnosticContext({ ...context, pointer: childPointer(context.pointer, "load") }));
  }
  if (Object.hasOwn(value, "assetLink")) {
    const pointer = childPointer(context.pointer, "assetLink");
    assertAssetId(value.assetLink, { ...context, pointer }, "invalid-asset-link");
    if (Object.hasOwn(value, "load") && value.load !== "full") {
      fail("invalid-reserved-field", "load 必须严格为字符串 full。", diagnosticContext({ ...context, pointer: childPointer(context.pointer, "load") }));
    }
    links.push({ source: context.assetId, target: value.assetLink, pointer, load: value.load === "full" ? "full" : null });
  }
  for (const key of Object.keys(value)) {
    if (key === "assetLink" || key === "load") continue;
    validateJsonValue(value[key], { ...context, pointer: childPointer(context.pointer, key) }, links);
  }
}

export function collectAssetLinks(descriptor, file = "asset") {
  if (!descriptor || !["Pattern", "Knowledge"].includes(descriptor.kind)) return [];
  const links = [];
  validateJsonValue(descriptor.content, { assetId: descriptor.id, file, pointer: "/content" }, links);
  return links.sort((left, right) => compareStrings(left.pointer, right.pointer) || compareStrings(left.target, right.target));
}

function rawHtmlCandidate(source, start) {
  if (source.startsWith("<!--", start)) {
    const end = source.indexOf("-->", start + 4);
    return source.slice(start, end === -1 ? source.length : end + 3);
  }
  if (source.startsWith("<![CDATA[", start)) {
    const end = source.indexOf("]]>", start + 9);
    return source.slice(start, end === -1 ? source.length : end + 3);
  }
  if (source.startsWith("<?", start)) {
    const end = source.indexOf("?>", start + 2);
    return source.slice(start, end === -1 ? source.length : end + 2);
  }
  if (/^<![A-Z]/.test(source.slice(start))) {
    const end = source.indexOf(">", start + 2);
    return source.slice(start, end === -1 ? source.length : end + 1);
  }
  const end = source.indexOf(">", start + 1);
  if (end === -1) {
    return /^<\/?[A-Za-z][A-Za-z0-9-]*(?:\s|$)/.test(source.slice(start)) ? source.slice(start) : null;
  }
  const candidate = source.slice(start, end + 1);
  if (/^<[A-Za-z][A-Za-z0-9+.-]{1,31}:[^\s<>]*>$/.test(candidate)) return null;
  if (/^<[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+>$/.test(candidate)) return null;
  return /^<\/?[A-Za-z][^>]*>$|^<![A-Z][^>]*>$|^<\?[^>]*\?>$/.test(candidate) ? candidate : null;
}

function escapeRawHtmlInInlineGfm(source) {
  let output = "";
  for (let index = 0; index < source.length;) {
    if (source[index] === "`") {
      let run = 1;
      while (source[index + run] === "`") run += 1;
      const marker = "`".repeat(run);
      const end = source.indexOf(marker, index + run);
      if (end !== -1) {
        output += source.slice(index, end + run);
        index = end + run;
        continue;
      }
    }
    if (source[index] === "<") {
      const candidate = rawHtmlCandidate(source, index);
      if (candidate) {
        output += candidate.replaceAll("<", "&lt;").replaceAll(">", "&gt;");
        index += candidate.length;
        continue;
      }
    }
    output += source[index];
    index += 1;
  }
  return output;
}

export function projectGfmString(markdown) {
  if (typeof markdown !== "string") fail("invalid-gfm", "GFM projection requires a string.", { valueType: typeof markdown });
  const lines = markdown.split(/(?<=\n)/);
  let fence = null;
  let inline = "";
  let safeMarkdown = "";
  const flushInline = () => {
    safeMarkdown += escapeRawHtmlInInlineGfm(inline);
    inline = "";
  };
  for (const line of lines) {
    const marker = /^(?: {0,3})(`{3,}|~{3,})/.exec(line)?.[1] ?? null;
    if (fence) {
      safeMarkdown += line;
      if (marker?.[0] === fence[0] && marker.length >= fence.length) fence = null;
      continue;
    }
    if (marker) {
      flushInline();
      fence = marker;
      safeMarkdown += line;
      continue;
    }
    inline += line;
  }
  flushInline();
  return { source: markdown, safeMarkdown, flavor: "gfm", rawHtml: "escaped-text" };
}

export function projectContentGfm(value) {
  if (typeof value === "string") return projectGfmString(value);
  if (Array.isArray(value)) return value.map(projectContentGfm);
  if (!value || typeof value !== "object") return value;
  return Object.fromEntries(Object.entries(value).map(([key, item]) => [
    key,
    key === "assetLink" || key === "load" ? item : projectContentGfm(item)
  ]));
}

function validateApiRow(value, label, context) {
  assertClosedObject(value, ["name", "type", "required", "default", "description"], label, context);
  assertString(value.name, `${label}.name`, { ...context, pointer: childPointer(context.pointer, "name") });
  assertString(value.type, `${label}.type`, { ...context, pointer: childPointer(context.pointer, "type") });
  if (typeof value.required !== "boolean") fail("invalid-component-api", `${label}.required 必须是 boolean。`, diagnosticContext({ ...context, pointer: childPointer(context.pointer, "required") }));
  if (!(value.default === null || ["string", "number", "boolean"].includes(typeof value.default)) || (typeof value.default === "number" && !Number.isFinite(value.default))) {
    fail("invalid-component-api", `${label}.default 必须是 JSON scalar 或 null。`, diagnosticContext({ ...context, pointer: childPointer(context.pointer, "default") }));
  }
  assertString(value.description, `${label}.description`, { ...context, pointer: childPointer(context.pointer, "description") });
  return { ...value };
}

function validateComponentApi(value, label, context) {
  assertClosedObject(value, ["mainExport", "properties", "types"], label, context);
  assertIdentifier(value.mainExport, `${label}.mainExport`, { ...context, pointer: childPointer(context.pointer, "mainExport") });
  if (!Array.isArray(value.properties)) fail("invalid-component-api", `${label}.properties 必须是数组。`, diagnosticContext({ ...context, pointer: childPointer(context.pointer, "properties") }));
  const properties = value.properties.map((row, index) => validateApiRow(row, `${label}.properties[${index}]`, {
    ...context,
    pointer: childPointer(childPointer(context.pointer, "properties"), index)
  }));
  const propertyNames = new Set();
  for (const [index, row] of properties.entries()) {
    if (propertyNames.has(row.name)) fail("invalid-component-api", `${label}.properties.name 必须唯一。`, diagnosticContext({ ...context, pointer: childPointer(childPointer(childPointer(context.pointer, "properties"), index), "name") }));
    propertyNames.add(row.name);
  }
  if (!Array.isArray(value.types)) fail("invalid-component-api", `${label}.types 必须是数组。`, diagnosticContext({ ...context, pointer: childPointer(context.pointer, "types") }));
  const typeNames = new Set();
  const types = value.types.map((item, index) => {
    const pointer = childPointer(childPointer(context.pointer, "types"), index);
    const typeLabel = `${label}.types[${index}]`;
    assertClosedObject(item, ["name", "properties"], typeLabel, { ...context, pointer });
    assertIdentifier(item.name, `${typeLabel}.name`, { ...context, pointer: childPointer(pointer, "name") });
    if (typeNames.has(item.name)) fail("invalid-component-api", `${label}.types.name 必须唯一。`, diagnosticContext({ ...context, pointer: childPointer(pointer, "name") }));
    typeNames.add(item.name);
    if (!Array.isArray(item.properties)) fail("invalid-component-api", `${typeLabel}.properties 必须是数组。`, diagnosticContext({ ...context, pointer: childPointer(pointer, "properties") }));
    const rows = item.properties.map((row, rowIndex) => validateApiRow(row, `${typeLabel}.properties[${rowIndex}]`, {
      ...context,
      pointer: childPointer(childPointer(pointer, "properties"), rowIndex)
    }));
    if (new Set(rows.map((row) => row.name)).size !== rows.length) fail("invalid-component-api", `${typeLabel}.properties.name 必须唯一。`, diagnosticContext({ ...context, pointer: childPointer(pointer, "properties") }));
    return { name: item.name, properties: rows };
  });
  return { mainExport: value.mainExport, properties, types };
}

function validateUsage(value, label, context) {
  const fields = ["componentOwns", "consumerProvides", "doesNotOwn"];
  assertClosedObject(value, fields, label, context);
  for (const field of fields) assertStringArray(value[field], `${label}.${field}`, { ...context, pointer: childPointer(context.pointer, field) });
  return Object.fromEntries(fields.map((field) => [field, [...value[field]]]));
}

function validateTemplateAuthoring(value, label, context) {
  assertClosedObject(value, ["mainExport", "customizationSurfaces"], label, context);
  assertIdentifier(value.mainExport, `${label}.mainExport`, { ...context, pointer: childPointer(context.pointer, "mainExport") });
  if (!Array.isArray(value.customizationSurfaces)) fail("invalid-template-authoring", `${label}.customizationSurfaces 必须是数组。`, diagnosticContext({ ...context, pointer: childPointer(context.pointer, "customizationSurfaces") }));
  const ids = new Set();
  const customizationSurfaces = value.customizationSurfaces.map((surface, index) => {
    const pointer = childPointer(childPointer(context.pointer, "customizationSurfaces"), index);
    const surfaceLabel = `${label}.customizationSurfaces[${index}]`;
    assertClosedObject(surface, ["id", "purpose", "binding"], surfaceLabel, { ...context, pointer });
    if (!localIdPattern.test(surface.id ?? "") || ids.has(surface.id)) fail("invalid-template-authoring", `${surfaceLabel}.id 无效或重复。`, diagnosticContext({ ...context, pointer: childPointer(pointer, "id") }));
    assertString(surface.purpose, `${surfaceLabel}.purpose`, { ...context, pointer: childPointer(pointer, "purpose") });
    assertClosedObject(surface.binding, ["type", "name"], `${surfaceLabel}.binding`, { ...context, pointer: childPointer(pointer, "binding") });
    if (surface.binding.type !== "prop") fail("invalid-template-authoring", `${surfaceLabel}.binding.type 只支持 prop。`, diagnosticContext({ ...context, pointer: childPointer(childPointer(pointer, "binding"), "type") }));
    assertString(surface.binding.name, `${surfaceLabel}.binding.name`, { ...context, pointer: childPointer(childPointer(pointer, "binding"), "name") });
    ids.add(surface.id);
    return { id: surface.id, purpose: surface.purpose, binding: { type: "prop", name: surface.binding.name } };
  });
  return { mainExport: value.mainExport, customizationSurfaces };
}

function validateConfigurationConstraint(value, label, context, blockIds) {
  assertClosedObject(value, ["type", "when", "target"], label, context);
  if (!["requires", "excludes"].includes(value.type)) fail("invalid-template-configuration", `${label}.type 不受支持。`, diagnosticContext({ ...context, pointer: childPointer(context.pointer, "type") }));
  for (const field of ["when", "target"]) {
    const pointer = childPointer(context.pointer, field);
    assertClosedObject(value[field], ["block", "selected"], `${label}.${field}`, { ...context, pointer });
    if (!blockIds.has(value[field].block)) fail("invalid-template-configuration", `${label}.${field}.block 必须引用已声明区块。`, diagnosticContext({ ...context, pointer: childPointer(pointer, "block") }));
    if (typeof value[field].selected !== "boolean") fail("invalid-template-configuration", `${label}.${field}.selected 必须是 boolean。`, diagnosticContext({ ...context, pointer: childPointer(pointer, "selected") }));
  }
  return { type: value.type, when: { ...value.when }, target: { ...value.target } };
}

export function validateTemplateConfiguration(value, label, context) {
  assertClosedObject(value, ["schemaVersion", "configurator", "blocks", "constraints", "presets", "nonConfigurableBoundary"], label, context);
  if (value.schemaVersion !== 1) fail("unsupported-template-configuration", `${label}.schemaVersion 只支持 1。`, diagnosticContext({ ...context, pointer: childPointer(context.pointer, "schemaVersion") }));
  const configuratorPointer = childPointer(context.pointer, "configurator");
  assertClosedObject(value.configurator, ["entry", "export", "assertionExport"], `${label}.configurator`, { ...context, pointer: configuratorPointer });
  assertRelativeFile(value.configurator.entry, `${label}.configurator.entry`, { ...context, pointer: childPointer(configuratorPointer, "entry") });
  if (!/\.(?:[cm]?js|ts)$/.test(value.configurator.entry)) fail("invalid-template-configuration", `${label}.configurator.entry 必须指向脚本。`, diagnosticContext({ ...context, pointer: childPointer(configuratorPointer, "entry") }));
  assertIdentifier(value.configurator.export, `${label}.configurator.export`, { ...context, pointer: childPointer(configuratorPointer, "export") });
  assertIdentifier(value.configurator.assertionExport, `${label}.configurator.assertionExport`, { ...context, pointer: childPointer(configuratorPointer, "assertionExport") });
  if (!Array.isArray(value.blocks) || !value.blocks.length) fail("invalid-template-configuration", `${label}.blocks 必须是非空数组。`, diagnosticContext({ ...context, pointer: childPointer(context.pointer, "blocks") }));
  const ids = new Set();
  const blocks = value.blocks.map((block, index) => {
    const pointer = childPointer(childPointer(context.pointer, "blocks"), index);
    const blockLabel = `${label}.blocks[${index}]`;
    assertClosedObject(block, ["id", "label", "purpose", "help", "default", "keptResult", "removedResult"], blockLabel, { ...context, pointer });
    if (!localIdPattern.test(block.id ?? "") || ids.has(block.id)) fail("invalid-template-configuration", `${blockLabel}.id 无效或重复。`, diagnosticContext({ ...context, pointer: childPointer(pointer, "id") }));
    for (const field of ["label", "purpose", "help", "keptResult", "removedResult"]) assertString(block[field], `${blockLabel}.${field}`, { ...context, pointer: childPointer(pointer, field) });
    if (typeof block.default !== "boolean") fail("invalid-template-configuration", `${blockLabel}.default 必须是 boolean。`, diagnosticContext({ ...context, pointer: childPointer(pointer, "default") }));
    ids.add(block.id);
    return { id: block.id, label: block.label, purpose: block.purpose, help: block.help, default: block.default, keptResult: block.keptResult, removedResult: block.removedResult };
  });
  if (!Array.isArray(value.constraints)) fail("invalid-template-configuration", `${label}.constraints 必须是数组。`, diagnosticContext({ ...context, pointer: childPointer(context.pointer, "constraints") }));
  const constraints = value.constraints.map((item, index) => validateConfigurationConstraint(item, `${label}.constraints[${index}]`, { ...context, pointer: childPointer(childPointer(context.pointer, "constraints"), index) }, ids));
  if (!Array.isArray(value.presets)) fail("invalid-template-configuration", `${label}.presets 必须是数组。`, diagnosticContext({ ...context, pointer: childPointer(context.pointer, "presets") }));
  const presetIds = new Set();
  const presets = value.presets.map((preset, index) => {
    const pointer = childPointer(childPointer(context.pointer, "presets"), index);
    const presetLabel = `${label}.presets[${index}]`;
    assertClosedObject(preset, ["id", "label", "decisions"], presetLabel, { ...context, pointer });
    if (!localIdPattern.test(preset.id ?? "") || presetIds.has(preset.id)) fail("invalid-template-configuration", `${presetLabel}.id 无效或重复。`, diagnosticContext({ ...context, pointer: childPointer(pointer, "id") }));
    assertString(preset.label, `${presetLabel}.label`, { ...context, pointer: childPointer(pointer, "label") });
    assertObject(preset.decisions, `${presetLabel}.decisions`, { ...context, pointer: childPointer(pointer, "decisions") });
    const keys = Object.keys(preset.decisions).sort();
    if (keys.length !== ids.size || keys.some((key) => !ids.has(key) || typeof preset.decisions[key] !== "boolean")) fail("invalid-template-configuration", `${presetLabel}.decisions 必须完整覆盖所有区块且仅包含 boolean。`, diagnosticContext({ ...context, pointer: childPointer(pointer, "decisions") }));
    presetIds.add(preset.id);
    return { id: preset.id, label: preset.label, decisions: Object.fromEntries(keys.map((key) => [key, preset.decisions[key]])) };
  });
  assertString(value.nonConfigurableBoundary, `${label}.nonConfigurableBoundary`, { ...context, pointer: childPointer(context.pointer, "nonConfigurableBoundary") });
  return { schemaVersion: 1, configurator: { entry: value.configurator.entry, export: value.configurator.export, assertionExport: value.configurator.assertionExport }, blocks, constraints, presets, nonConfigurableBoundary: value.nonConfigurableBoundary };
}

export function configurationDecisionsAreLegal(configuration, decisions) {
  if (!configuration) return false;
  const keys = Object.keys(decisions ?? {}).sort();
  const blockIds = configuration.blocks.map((block) => block.id).sort();
  if (JSON.stringify(keys) !== JSON.stringify(blockIds) || keys.some((key) => typeof decisions[key] !== "boolean")) return false;
  return configuration.constraints.every(({ type, when, target }) => {
    if (decisions[when.block] !== when.selected) return true;
    return type === "requires" ? decisions[target.block] === target.selected : decisions[target.block] !== target.selected;
  });
}

export function validateSourceManifest(value, label = "manifest.json") {
  const fields = ["schemaVersion", "id", "version", "entrypoints", "review", "runtimeTheme", ...(value?.schemaVersion === 5 ? ["uiConfig"] : [])];
  assertClosedObject(value, fields, label, { file: label, pointer: "" });
  if (![3, 4, 5].includes(value.schemaVersion)) fail("unsupported-schema", `${label}.schemaVersion 只支持 3、4 或 5。`, { file: label, pointer: "/schemaVersion", actual: value.schemaVersion });
  if (value.schemaVersion < 5 && Object.hasOwn(value, "uiConfig")) fail("unsupported-schema", `${label}.uiConfig 需要 schemaVersion 5。`, { file: label, pointer: "/uiConfig" });
  assertString(value.id, `${label}.id`, { file: label, pointer: "/id" });
  if (!sourceIdPattern.test(value.id)) fail("invalid-source-id", `${label}.id 格式无效：${value.id}。`, { file: label, pointer: "/id", id: value.id });
  assertString(value.version, `${label}.version`, { file: label, pointer: "/version" });
  if (!/^\d+\.\d+\.\d+$/.test(value.version)) fail("invalid-version", `${label}.version 必须是 semver。`, { file: label, pointer: "/version", version: value.version });
  if (!Array.isArray(value.entrypoints) || !value.entrypoints.length) fail("invalid-entrypoints", `${label}.entrypoints 必须是非空数组。`, { file: label, pointer: "/entrypoints" });
  if (!Array.isArray(value.review)) fail("invalid-review-target", `${label}.review 必须是数组。`, { file: label, pointer: "/review" });
  const validateBindings = (bindings, stage, allowedPrefixes, category) => {
    const seen = new Map();
    return bindings.map((binding, index) => {
      const pointer = `/${stage}/${index}`;
      assertObject(binding, `${label}.${stage}[${index}]`, { file: label, pointer });
      const extra = Object.keys(binding).filter((key) => !["assetLink", "load"].includes(key));
      if (extra.length) fail("unknown-field", `${label}.${stage}[${index}] 包含未知字段：${extra.join("、")}。`, { file: label, pointer: `${pointer}/${pointerToken(extra[0])}`, fields: extra });
      if (!Object.hasOwn(binding, "assetLink")) fail("missing-field", `${label}.${stage}[${index}] 缺少必填字段：assetLink。`, { file: label, pointer: `${pointer}/assetLink`, fields: ["assetLink"] });
      assertAssetId(binding.assetLink, { file: label, pointer: `${pointer}/assetLink` }, category);
      if (!allowedPrefixes.some((prefix) => binding.assetLink.startsWith(`${prefix}.`))) fail(category, `${label}.${stage} 不允许目标：${binding.assetLink}。`, { file: label, pointer: `${pointer}/assetLink`, assetId: binding.assetLink });
      if (Object.hasOwn(binding, "load") && binding.load !== "full") fail(category, `${label}.${stage}[${index}].load 只允许 full。`, { file: label, pointer: `${pointer}/load`, actual: binding.load });
      if (seen.has(binding.assetLink)) fail(category, `${label}.${stage} 不允许重复 target：${binding.assetLink}。`, { file: label, pointer: `${pointer}/assetLink`, assetId: binding.assetLink, duplicateOf: seen.get(binding.assetLink) });
      seen.set(binding.assetLink, index);
      return { assetLink: binding.assetLink, ...(binding.load === "full" ? { load: "full" } : {}) };
    });
  };
  const entrypoints = validateBindings(value.entrypoints, "entrypoints", ["pattern"], "invalid-entrypoints");
  const review = validateBindings(value.review, "review", ["pattern", "knowledge"], "invalid-review-target");
  assertClosedObject(value.runtimeTheme, ["artifacts"], `${label}.runtimeTheme`, { file: label, pointer: "/runtimeTheme" });
  const artifacts = value.runtimeTheme.artifacts;
  if (!Array.isArray(artifacts) || artifacts.length !== canonicalRuntimeThemeArtifactBasenames.length) {
    fail("invalid-runtime-theme", `${label}.runtimeTheme.artifacts 必须且只能声明三份 canonical artifact。`, { file: label, pointer: "/runtimeTheme/artifacts", expected: canonicalRuntimeThemeArtifactBasenames, actual: artifacts });
  }
  const seenArtifacts = new Map();
  for (const [index, artifact] of artifacts.entries()) {
    assertRelativeFile(artifact, `${label}.runtimeTheme.artifacts[${index}]`, { file: label, pointer: `/runtimeTheme/artifacts/${index}` });
    if (seenArtifacts.has(artifact)) fail("invalid-runtime-theme", `${label}.runtimeTheme.artifacts 不允许重复值：${artifact}。`, { file: label, pointer: `/runtimeTheme/artifacts/${index}`, duplicateOf: seenArtifacts.get(artifact) });
    seenArtifacts.set(artifact, index);
  }
  const actualThemeBasenames = artifacts.map((artifact) => path.posix.basename(artifact)).sort(compareStrings);
  const expectedThemeBasenames = [...canonicalRuntimeThemeArtifactBasenames].sort(compareStrings);
  if (JSON.stringify(actualThemeBasenames) !== JSON.stringify(expectedThemeBasenames)) {
    fail("invalid-runtime-theme", `${label}.runtimeTheme.artifacts 必须声明三份 canonical artifact。`, { file: label, pointer: "/runtimeTheme/artifacts", expected: expectedThemeBasenames, actual: actualThemeBasenames });
  }
  if (Object.hasOwn(value, "uiConfig")) {
    assertClosedObject(value.uiConfig, ["stylesheet", "antdVersion"], `${label}.uiConfig`, { file: label, pointer: "/uiConfig" });
    assertRelativeFile(value.uiConfig.stylesheet, `${label}.uiConfig.stylesheet`, { file: label, pointer: "/uiConfig/stylesheet" });
    if (!value.uiConfig.stylesheet.endsWith(".css")) fail("invalid-ui-config", `${label}.uiConfig.stylesheet 必须指向 CSS 文件。`, { file: label, pointer: "/uiConfig/stylesheet" });
    assertString(value.uiConfig.antdVersion, `${label}.uiConfig.antdVersion`, { file: label, pointer: "/uiConfig/antdVersion" });
    if (!/^\d+\.\d+\.\d+$/.test(value.uiConfig.antdVersion)) fail("invalid-ui-config", `${label}.uiConfig.antdVersion 必须是精确版本。`, { file: label, pointer: "/uiConfig/antdVersion" });
  }
  return {
    schemaVersion: value.schemaVersion,
    id: value.id,
    version: value.version,
    entrypoints,
    review,
    runtimeTheme: { artifacts: [...value.runtimeTheme.artifacts] },
    ...(value.uiConfig ? { uiConfig: { ...value.uiConfig } } : {})
  };
}

export function validateAssetDescriptor(value, label = "asset.json") {
  assertObject(value, label, { file: label, pointer: "" });
  const extra = Object.keys(value).filter((key) => !knownDescriptorFields.has(key));
  if (extra.length) fail("unknown-field", `${label} 包含未知字段：${extra.join("、")}。`, { file: label, pointer: `/${pointerToken(extra[0])}`, fields: extra, assetId: typeof value.id === "string" ? value.id : null });
  for (const field of commonFields) if (!Object.hasOwn(value, field)) fail("missing-field", `${label} 缺少必填字段：${field}。`, { file: label, pointer: `/${field}`, assetId: typeof value.id === "string" ? value.id : null, fields: [field] });
  assertAssetId(value.id, { file: label, pointer: "/id", assetId: typeof value.id === "string" ? value.id : null });
  if (!assetKinds.has(value.kind) || value.id.split(".")[0] !== kindPrefix.get(value.kind)) fail("invalid-asset-kind", `${value.id} 的 kind/ID 前缀不匹配。`, { assetId: value.id, file: label, pointer: "/kind", kind: value.kind });
  assertString(value.title, `${value.id}.title`, { assetId: value.id, file: label, pointer: "/title" });
  assertString(value.abstract, `${value.id}.abstract`, { assetId: value.id, file: label, pointer: "/abstract" });
  const context = { assetId: value.id, file: label };

  if (value.kind === "Knowledge" || value.kind === "Pattern") {
    for (const forbidden of ["entry", "artifacts", "authoring", "configuration", "api", "usage"]) if (Object.hasOwn(value, forbidden)) fail("invalid-kind-field", `${value.id} 不允许声明 ${forbidden}。`, { ...context, pointer: `/${forbidden}` });
    if (!Object.hasOwn(value, "content") || !value.content || typeof value.content !== "object" || Array.isArray(value.content) || !Object.keys(value.content).length) fail("missing-content", `${value.id} 必须声明非空语义 content object。`, { ...context, pointer: "/content" });
    collectAssetLinks(value, label);
    return { id: value.id, kind: value.kind, title: value.title, abstract: value.abstract, content: value.content };
  }

  if (value.kind === "Template") {
    for (const forbidden of ["content", "api", "usage"]) if (Object.hasOwn(value, forbidden)) fail("invalid-kind-field", `${value.id} 不允许声明 ${forbidden}。`, { ...context, pointer: `/${forbidden}` });
    for (const required of ["entry", "artifacts", "authoring"]) if (!Object.hasOwn(value, required)) fail("missing-field", `${value.id} 缺少必填字段：${required}。`, { ...context, pointer: `/${required}`, fields: [required] });
    assertTypeScriptEntry(value.entry, `${value.id}.entry`, { ...context, pointer: "/entry" });
    assertStringArray(value.artifacts, `${value.id}.artifacts`, { ...context, pointer: "/artifacts" });
    for (const [index, artifact] of value.artifacts.entries()) assertRelativeFile(artifact, `${value.id}.artifacts[${index}]`, { ...context, pointer: `/artifacts/${index}` });
    if (value.artifacts.includes(value.entry)) fail("invalid-artifacts", `${value.id}.artifacts 不得重复 entry。`, { ...context, pointer: `/artifacts/${value.artifacts.indexOf(value.entry)}` });
    return {
      id: value.id,
      kind: value.kind,
      title: value.title,
      abstract: value.abstract,
      entry: value.entry,
      artifacts: [...value.artifacts],
      authoring: validateTemplateAuthoring(value.authoring, `${value.id}.authoring`, { ...context, pointer: "/authoring" }),
      ...(Object.hasOwn(value, "configuration") ? { configuration: validateTemplateConfiguration(value.configuration, `${value.id}.configuration`, { ...context, pointer: "/configuration" }) } : {})
    };
  }

  for (const forbidden of ["content", "authoring", "configuration"]) if (Object.hasOwn(value, forbidden)) fail("invalid-kind-field", `${value.id} 不允许声明 ${forbidden}。`, { ...context, pointer: `/${forbidden}` });
  for (const required of ["entry", "artifacts", "api", "usage"]) if (!Object.hasOwn(value, required)) fail("missing-field", `${value.id} 缺少必填字段：${required}。`, { ...context, pointer: `/${required}`, fields: [required] });
  assertTypeScriptEntry(value.entry, `${value.id}.entry`, { ...context, pointer: "/entry" });
  assertStringArray(value.artifacts, `${value.id}.artifacts`, { ...context, pointer: "/artifacts" });
  for (const [index, artifact] of value.artifacts.entries()) assertRelativeFile(artifact, `${value.id}.artifacts[${index}]`, { ...context, pointer: `/artifacts/${index}` });
  if (value.artifacts.includes(value.entry)) fail("invalid-artifacts", `${value.id}.artifacts 不得重复 entry。`, { ...context, pointer: `/artifacts/${value.artifacts.indexOf(value.entry)}` });
  return {
    id: value.id,
    kind: value.kind,
    title: value.title,
    abstract: value.abstract,
    entry: value.entry,
    artifacts: [...value.artifacts],
    api: validateComponentApi(value.api, `${value.id}.api`, { ...context, pointer: "/api" }),
    usage: validateUsage(value.usage, `${value.id}.usage`, { ...context, pointer: "/usage" })
  };
}

export function isCanonicalAssetId(value) {
  return typeof value === "string" && assetIdPattern.test(value);
}
