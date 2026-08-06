import { createHash } from "node:crypto";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";

const exists = (file) => stat(file).then(() => true, (error) => error?.code === "ENOENT" ? false : Promise.reject(error));
const stableObject = (value) => Array.isArray(value) ? value.map(stableObject) : value && typeof value === "object" ? Object.fromEntries(Object.keys(value).sort().map((key) => [key, stableObject(value[key])])) : value;
const compactJson = (value) => JSON.stringify(stableObject(value));
const sha256 = (value) => createHash("sha256").update(value).digest("hex");

export async function validatePagePlan({ receiptFile = ".ux-proto/page-plan.json", catalogFile = "registries/catalog.json", knowledgeFile = null } = {}) {
  if (!(await exists(receiptFile))) return { status: "absent", planStatus: "absent", knowledgeDelivery: "not-evaluated", executionClosure: "skipped", planningDrift: [], requestDrift: [] };
  const receipt = JSON.parse(await readFile(receiptFile, "utf8"));
  if ([1, 2].includes(receipt.schemaVersion)) throw new Error(`Page-plan schemaVersion ${receipt.schemaVersion} is no longer supported. Run orient and plan again to create schemaVersion 3.`);
  if (receipt.schemaVersion !== 3 || receipt.kind !== "ux-proto-page-plan") throw new Error("Invalid UX Proto page-plan v3 receipt.");
  for (const field of ["request", "intent", "profile", "patterns", "activatedKnowledge", "knowledgeIndexStats", "knowledgeGuidanceStats", "selectedReuse", "executionDependencies", "actions"]) if (!(field in receipt)) throw new Error(`Page-plan v3 is missing ${field}.`);
  if (receipt.request?.schemaVersion !== 3 || !Array.isArray(receipt.request.additionalKnowledge)) throw new Error("Page-plan v3 contains an invalid request snapshot.");
  if (!Array.isArray(receipt.selectedReuse) || !Array.isArray(receipt.executionDependencies) || !Array.isArray(receipt.actions?.materialize) || !Array.isArray(receipt.actions?.import)) throw new Error("Invalid page-plan v3 execution collections.");
  for (const item of receipt.selectedReuse) if (!["pattern-relation", "design-language-baseline"].includes(item.source)) throw new Error(`Page-plan v3 has invalid reuse source for ${item.asset?.id ?? "unknown"}.`);

  let guidanceBytes = 0;
  for (const item of receipt.activatedKnowledge) {
    const bytes = Buffer.byteLength(compactJson(item.knowledge));
    if (bytes !== item.utf8Bytes || bytes > 4096 || sha256(compactJson(item.knowledge)) !== item.sha256) throw new Error(`Activated Knowledge snapshot/hash is invalid for ${item.id}.`);
    guidanceBytes += bytes;
  }
  const stats = receipt.knowledgeGuidanceStats;
  if (guidanceBytes > 16384 || stats.utf8Bytes !== guidanceBytes || stats.activatedCount !== receipt.activatedKnowledge.length || stats.additionalCount !== receipt.request.additionalKnowledge.length) throw new Error("Page-plan v3 Knowledge guidance statistics are invalid.");

  const catalog = JSON.parse(await readFile(catalogFile, "utf8"));
  const active = new Set(catalog.entries.filter((entry) => entry.lifecycle === "active").map((entry) => entry.id));
  const kindById = new Map(catalog.entries.map((entry) => [entry.id, entry.kind]));
  const planningDrift = [];
  for (const item of receipt.patterns) if (!active.has(item.id)) planningDrift.push({ type: "pattern-lifecycle", id: item.id });
  for (const item of receipt.activatedKnowledge) if (!active.has(item.id)) planningDrift.push({ type: "knowledge-lifecycle", id: item.id });
  const resolvedKnowledgeFile = knowledgeFile ?? path.join(path.dirname(catalogFile), "knowledge.registry.json");
  const currentKnowledge = new Map((JSON.parse(await readFile(resolvedKnowledgeFile, "utf8"))).records.map((item) => [item.id, item.knowledge]));
  for (const item of receipt.activatedKnowledge) if (currentKnowledge.has(item.id) && sha256(compactJson(currentKnowledge.get(item.id))) !== item.sha256) planningDrift.push({ type: "knowledge-digest", id: item.id });
  const executionAssetIds = [...new Set([...receipt.actions.materialize, ...receipt.actions.import].map((item) => item.assetId))].sort();
  const derivedExecutionAssetIds = [...new Set([
    ...receipt.selectedReuse.map((item) => item.asset?.id),
    ...receipt.executionDependencies.map((item) => item.assetId),
    ...(receipt.profile.resolvedBindings ?? []).filter((item) => item.state === "on").map((item) => item.effect?.assetId)
  ].filter(Boolean))].sort();
  if (compactJson(executionAssetIds) !== compactJson(derivedExecutionAssetIds)) throw new Error(`Page-plan v3 action closure is invalid; actions=[${executionAssetIds}], derived=[${derivedExecutionAssetIds}].`);
  for (const item of receipt.actions.materialize) if (kindById.get(item.assetId) !== "template") throw new Error(`Materialize action ${item.assetId} is not a Template.`);
  for (const item of receipt.actions.import) if (kindById.get(item.assetId) !== "product-specific-component") throw new Error(`Import action ${item.assetId} is not a Product-specific component.`);
  for (const id of executionAssetIds) if (!active.has(id)) throw new Error(`Page-plan v3 references a missing or inactive execution asset: ${id}.`);

  const requestDrift = [];
  if (receipt.requestSource) {
    const source = path.resolve(path.dirname(receiptFile), "..", receipt.requestSource.path);
    if (!(await exists(source))) requestDrift.push({ type: "request-source-missing", path: receipt.requestSource.path });
    else if (sha256(await readFile(source)) !== receipt.requestSource.sha256) requestDrift.push({ type: "request-source-changed", path: receipt.requestSource.path });
  }
  if (receipt.designLanguage) {
    const baseline = path.resolve(path.dirname(receiptFile), "..", receipt.designLanguage.path);
    if (!(await exists(baseline)) || sha256(await readFile(baseline)) !== receipt.designLanguage.sha256) planningDrift.push({ type: "design-language-digest", path: receipt.designLanguage.path });
  }
  return { status: "valid", planStatus: "valid", knowledgeDelivery: "verified", executionClosure: "pending", executionAssetIds, planningDrift, requestDrift, knowledgeIndexStats: receipt.knowledgeIndexStats, knowledgeGuidanceStats: stats };
}
