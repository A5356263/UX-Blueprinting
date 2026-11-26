import path from "node:path";
import { pathToFileURL } from "node:url";
import { containedPath, digestObject, fail, sha256 } from "./common.mjs";
import { configurationDecisionsAreLegal } from "./contracts.mjs";

export const configuratorContractVersion = 1;

export function enumerateLegalConfigurations(configuration) {
  if (!configuration) return [];
  const blocks = [...configuration.blocks].sort((left, right) => left.id.localeCompare(right.id));
  const combinations = [];
  for (let mask = 0; mask < 2 ** blocks.length; mask += 1) {
    const decisions = Object.fromEntries(blocks.map((block, index) => [block.id, Boolean(mask & (1 << index))]));
    if (configurationDecisionsAreLegal(configuration, decisions)) combinations.push(decisions);
  }
  if (!combinations.length) fail("unsatisfiable-template-configuration", "Template configuration has no legal block selections.", {});
  return combinations;
}

export function assertConfigurationDecisions(configuration, decisions) {
  if (!configurationDecisionsAreLegal(configuration, decisions)) fail("invalid-template-selection", "Template selection must contain every block exactly once and satisfy its hard constraints.", { expectedBlocks: configuration.blocks.map((block) => block.id).sort() });
  return Object.fromEntries(Object.keys(decisions).sort().map((key) => [key, decisions[key]]));
}

export function configurationFingerprint(record) {
  return `sha256:${digestObject({ configuration: record.configuration, templateSourceDigest: record.templateSourceDigest, configuratorFiles: record.configuratorFiles ?? [] })}`;
}

function sourceFileMap(record, snapshotRoot) {
  const prefix = `files/${record.id}/`;
  return Object.fromEntries(record.files.map((file) => {
    const snapshotPath = file.path ?? file.snapshotPath;
    if (!snapshotPath?.startsWith(prefix)) fail("invalid-configurator-source", "Template source file is outside its snapshot root.", { assetId: record.id, path: snapshotPath ?? null });
    return [snapshotPath.slice(prefix.length), containedPath(snapshotRoot, snapshotPath)];
  }));
}

function normalizeReturnedFiles({ record, returned }) {
  if (!returned || typeof returned !== "object" || Array.isArray(returned) || !returned.files || typeof returned.files !== "object" || Array.isArray(returned.files)) fail("invalid-configurator-output", "Configurator must return a files object.", { assetId: record.id });
  const allowed = new Set(record.files.map((file) => (file.path ?? file.snapshotPath).slice(`files/${record.id}/`.length)));
  const entries = Object.entries(returned.files).sort(([left], [right]) => left.localeCompare(right));
  if (!entries.length || entries.some(([relative, content]) => !allowed.has(relative) || typeof content !== "string")) fail("invalid-configurator-output", "Configurator output may only rewrite or omit existing Template files as base64 strings.", { assetId: record.id, allowed: [...allowed].sort() });
  const files = entries.map(([relative, content]) => ({ relative, output: Buffer.from(content, "base64") }));
  const entry = record.entry;
  if (!entries.some(([relative]) => relative === entry)) fail("invalid-configurator-output", "Configurator output must retain the Template entry file.", { assetId: record.id, entry });
  return files;
}

export async function runTemplateConfigurator({ snapshotRoot, record, decisions }) {
  if (!record.configuration) fail("template-not-configured", "Template has no configured materialization contract.", { assetId: record.id });
  const normalized = assertConfigurationDecisions(record.configuration, decisions);
  const entry = record.configuration.configurator.entry;
  const root = containedPath(snapshotRoot, "files", record.id);
  const modulePath = containedPath(root, entry);
  const expected = new Map((record.configuratorFiles ?? []).map((file) => [file.path ?? file.snapshotPath, file.sha256]));
  const snapshotPath = `files/${record.id}/${entry}`;
  if (!expected.has(snapshotPath)) fail("configurator-missing", "Resolved snapshot does not contain the declared configurator closure.", { assetId: record.id, path: snapshotPath });
  const module = await import(`${pathToFileURL(modulePath).href}?uxProto=${expected.get(snapshotPath)}`);
  const execute = module[record.configuration.configurator.export];
  if (typeof execute !== "function") fail("configurator-export-missing", "Declared configurator export is unavailable.", { assetId: record.id, export: record.configuration.configurator.export });
  const sources = sourceFileMap(record, snapshotRoot);
  const files = {};
  for (const [relative, source] of Object.entries(sources)) files[relative] = (await import("node:fs/promises")).readFile(source).then((value) => value.toString("base64"));
  const resolvedFiles = Object.fromEntries(await Promise.all(Object.entries(files).map(async ([relative, contents]) => [relative, await contents])));
  let returned;
  try {
    returned = await execute({ schemaVersion: configuratorContractVersion, assetId: record.id, decisions: normalized, files: resolvedFiles });
  } catch (error) {
    fail("configurator-threw", `Configurator threw: ${error?.message ?? String(error)}`, { assetId: record.id });
  }
  const output = normalizeReturnedFiles({ record, returned });
  return { decisions: normalized, files: output, outputDigest: `sha256:${digestObject(output.map((file) => ({ path: file.relative, sha256: sha256(file.output) })))}` };
}

export async function runTemplateSemanticAssertion({ snapshotRoot, record, decisions, files }) {
  if (!record.configuration) fail("template-not-configured", "Template has no configured materialization contract.", { assetId: record.id });
  const normalized = assertConfigurationDecisions(record.configuration, decisions);
  const entry = record.configuration.configurator.entry;
  const snapshotPath = `files/${record.id}/${entry}`;
  const expected = new Map((record.configuratorFiles ?? []).map((file) => [file.path ?? file.snapshotPath, file.sha256]));
  const root = containedPath(snapshotRoot, "files", record.id);
  if (!expected.has(snapshotPath)) fail("configurator-missing", "Resolved snapshot does not contain the declared configurator closure.", { assetId: record.id, path: snapshotPath });
  const module = await import(`${pathToFileURL(containedPath(root, entry)).href}?uxProtoAssertion=${expected.get(snapshotPath)}`);
  const assertOutput = module[record.configuration.configurator.assertionExport];
  if (typeof assertOutput !== "function") fail("configurator-assertion-missing", "Declared configurator semantic assertion export is unavailable.", { assetId: record.id, export: record.configuration.configurator.assertionExport });
  let result;
  try {
    result = await assertOutput({ schemaVersion: configuratorContractVersion, assetId: record.id, decisions: normalized, files: Object.fromEntries(files.map((file) => [file.relative, file.output.toString("base64")])) });
  } catch (error) {
    fail("configurator-semantic-assertion-failed", `Configurator semantic assertion threw: ${error?.message ?? String(error)}`, { assetId: record.id });
  }
  if (result !== true) fail("configurator-semantic-assertion-failed", "Configurator semantic assertion must return true for this generated output.", { assetId: record.id, decisions: normalized });
  return { asserted: true, decisions: normalized };
}
