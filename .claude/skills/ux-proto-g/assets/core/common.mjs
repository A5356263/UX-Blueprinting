import { createHash } from "node:crypto";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";

export class UxProtoError extends Error {
  constructor(category, message, context = {}) {
    super(message);
    this.name = "UxProtoError";
    this.category = category;
    this.context = context;
  }
}

export const fail = (category, message, context) => { throw new UxProtoError(category, message, context); };
export const sha256 = (value) => createHash("sha256").update(value).digest("hex");
export const stableObject = (value) => Array.isArray(value)
  ? value.map(stableObject)
  : value && typeof value === "object"
    ? Object.fromEntries(Object.keys(value).sort().map((key) => [key, stableObject(value[key])]))
    : value;
export const stableJson = (value) => `${JSON.stringify(stableObject(value), null, 2)}\n`;
export const digestObject = (value) => sha256(stableJson(value));
export const posixPath = (value) => value.split(path.sep).join("/");
export const uniqueSorted = (values) => [...new Set(values)].sort((a, b) => a.localeCompare(b));

export function assertCanonicalAssetId(value) {
  if (typeof value !== "string" || !/^[a-z0-9]+(?:[.-][a-z0-9]+)*$/.test(value)) fail("invalid-asset-id", `Asset ID is not canonical: ${value ?? "(missing)"}.`, { assetId: value ?? null });
  return value;
}

export function containedPath(root, ...segments) {
  const boundary = path.resolve(root);
  const candidate = path.resolve(boundary, ...segments);
  if (candidate === boundary || !candidate.startsWith(`${boundary}${path.sep}`)) fail("path-boundary-violation", "Resolved path escapes its governed root.", { root: boundary, path: candidate });
  return candidate;
}

export async function exists(file) {
  try { await stat(file); return true; }
  catch (error) { if (error?.code === "ENOENT") return false; throw error; }
}

export async function readJson(file, category = "invalid-json") {
  try { return JSON.parse(await readFile(file, "utf8")); }
  catch (error) { fail(category, `无法读取 JSON：${file}（${error.message}）`, { file }); }
}

export function assertKeys(value, allowed, label) {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail("invalid-contract", `${label} 必须是对象。`, { label });
  const extra = Object.keys(value).filter((key) => !allowed.includes(key));
  if (extra.length) fail("unknown-field", `${label} 包含未知字段：${extra.join("、")}。`, { label, fields: extra });
}

export function assertString(value, label) {
  if (typeof value !== "string" || !value.trim()) fail("invalid-contract", `${label} 必须是非空字符串。`, { label });
}

export function assertStringArray(value, label, { nonEmpty = false } = {}) {
  if (!Array.isArray(value) || (nonEmpty && !value.length) || value.some((item) => typeof item !== "string" || !item.trim()) || new Set(value).size !== value.length) {
    fail("invalid-contract", `${label} 必须是${nonEmpty ? "非空" : ""}且不重复的字符串数组。`, { label });
  }
}
