import { readFile } from "node:fs/promises";
import { fail } from "./common.mjs";

const schema = JSON.parse(await readFile(new URL("./schemas/materialization.schema.json", import.meta.url), "utf8"));
if (schema.$id !== "https://ux-proto.local/schemas/materialization-v2.json") throw new Error("Materialization schema binding is invalid.");
export const materializationSchemaVersion = schema.$defs.request.properties.schemaVersion.const;

function typeMatches(value, type) {
  if (type === "null") return value === null;
  if (type === "array") return Array.isArray(value);
  if (type === "object") return Boolean(value) && typeof value === "object" && !Array.isArray(value);
  return typeof value === type;
}
function resolved(definition) {
  if (!definition.$ref) return definition;
  return definition.$ref.replace(/^#\//, "").split("/").reduce((value, token) => value?.[token], schema);
}
function validate(value, definition, at = "$") {
  const rule = resolved(definition);
  if (!rule) return `${at}: unresolved schema reference`;
  if (rule.allOf) for (const item of rule.allOf) { const error = validate(value, item, at); if (error) return error; }
  if (rule.oneOf) {
    const matches = rule.oneOf.filter((item) => !validate(value, item, at)).length;
    if (matches !== 1) return `${at}: expected exactly one schema variant, received ${matches}`;
  }
  if (rule.type !== undefined) {
    const types = Array.isArray(rule.type) ? rule.type : [rule.type];
    if (!types.some((type) => typeMatches(value, type))) return `${at}: expected ${types.join("|")}`;
  }
  if (Object.hasOwn(rule, "const") && value !== rule.const) return `${at}: expected constant ${JSON.stringify(rule.const)}`;
  if (rule.enum && !rule.enum.includes(value)) return `${at}: expected one of ${rule.enum.join(", ")}`;
  if (typeof value === "string") {
    if (rule.minLength !== undefined && value.length < rule.minLength) return `${at}: string is shorter than ${rule.minLength}`;
    if (rule.pattern && !(new RegExp(rule.pattern).test(value))) return `${at}: string does not match required pattern`;
  }
  if (Array.isArray(value)) {
    if (rule.minItems !== undefined && value.length < rule.minItems) return `${at}: array has fewer than ${rule.minItems} items`;
    if (rule.items) for (const [index, item] of value.entries()) { const error = validate(item, rule.items, `${at}[${index}]`); if (error) return error; }
  }
  if (value && typeof value === "object" && !Array.isArray(value)) {
    for (const key of rule.required ?? []) if (!Object.hasOwn(value, key)) return `${at}: missing required ${key}`;
    const properties = rule.properties ?? {};
    if (rule.additionalProperties === false) for (const key of Object.keys(value)) if (!Object.hasOwn(properties, key)) return `${at}: unexpected ${key}`;
    for (const [key, item] of Object.entries(value)) {
      const property = properties[key] ?? (rule.additionalProperties && typeof rule.additionalProperties === "object" ? rule.additionalProperties : null);
      if (property) { const error = validate(item, property, `${at}.${key}`); if (error) return error; }
    }
  }
  return null;
}
function validateSchema(value, definition, category) {
  const error = validate(value, definition);
  if (error) fail(category, `Materialization v${materializationSchemaVersion} data does not conform to its schema: ${error}.`, {});
  return value;
}

export function parseMaterializationRequest(input) {
  let request;
  try { request = typeof input === "string" ? JSON.parse(input) : input; }
  catch { fail("invalid-materialization-request", "materialize request must be JSON data.", {}); }
  return validateSchema(request, { $ref: "#/$defs/request" }, "invalid-materialization-request");
}
export function validateMaterializationRequest({ assetId, selection = null, reselect = false }) {
  return parseMaterializationRequest({ schemaVersion: materializationSchemaVersion, assetId, selection, reselect });
}
export function parseMaterializationSelection(input) {
  let selection;
  try { selection = JSON.parse(input); }
  catch { fail("invalid-selection-json", "--selection must be a JSON object.", {}); }
  return validateSchema(selection, { $ref: "#/$defs/selection" }, "invalid-materialization-request");
}
export function serializeMaterializationResult(result) {
  const data = { ...result, target: `page-assets/${result.assetId}`, proof: result.provenanceFiles?.[0] ?? null };
  return validateSchema(data, { $ref: "#/$defs/result" }, "invalid-materialization-result");
}
export function serializeMaterializationSuccess(result) {
  return validateSchema({ schemaVersion: materializationSchemaVersion, command: "materialize", status: "success", data: serializeMaterializationResult(result) }, { $ref: "#/$defs/successEnvelope" }, "invalid-materialization-result");
}
export function serializeMaterializationFailure(error) {
  return validateSchema({ schemaVersion: materializationSchemaVersion, command: "materialize", status: "failed", error }, { $ref: "#/$defs/failureEnvelope" }, "invalid-materialization-failure");
}
export function parseMaterializationCliEnvelope(input) {
  let envelope;
  try { envelope = typeof input === "string" ? JSON.parse(input) : input; }
  catch { fail("invalid-materialization-result", "materialize CLI output must be JSON data.", {}); }
  return validateSchema(envelope, { oneOf: [{ $ref: "#/$defs/successEnvelope" }, { $ref: "#/$defs/failureEnvelope" }] }, "invalid-materialization-result");
}
