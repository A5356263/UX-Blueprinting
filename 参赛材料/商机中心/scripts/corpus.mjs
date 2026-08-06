import { createHash } from "node:crypto";
import { mkdir, readFile, rename, rm, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const workspaceRoot = path.resolve(here, "..");
const registriesRoot = path.join(workspaceRoot, "registries");
const protectedRoots = ["components/product", "components/product-specific", "patterns", "registries", "templates", "theme", "scripts"];

function argument(name, fallback) {
  const index = process.argv.indexOf(name);
  if (index === -1) return fallback;
  if (!process.argv[index + 1]) throw new Error(`${name} requires a value.`);
  return process.argv[index + 1];
}

const readJson = async (file) => JSON.parse(await readFile(file, "utf8"));
const exists = async (file) => stat(file).then(() => true, (error) => error?.code === "ENOENT" ? false : Promise.reject(error));
const sha256 = (value) => createHash("sha256").update(value).digest("hex");
const stableObject = (value) => Array.isArray(value) ? value.map(stableObject) : value && typeof value === "object" ? Object.fromEntries(Object.keys(value).sort().map((key) => [key, stableObject(value[key])])) : value;
const compactJson = (value) => JSON.stringify(stableObject(value));
const utf8Bytes = (value) => Buffer.byteLength(compactJson(value));
const reusableKinds = new Set(["template", "product-specific-component"]);

async function catalog() {
  const value = await readJson(path.join(registriesRoot, "catalog.json"));
  if (value.schemaVersion !== 2) throw new Error("This corpus runtime requires a schemaVersion 2 consumer.");
  return value;
}

async function detailedRecord(id, kind) {
  const files = {
    knowledge: "knowledge.registry.json",
    pattern: "page-patterns.registry.json",
    template: "templates.registry.json",
    "product-specific-component": "product-specific-components.registry.json"
  };
  const file = files[kind];
  if (!file || !(await exists(path.join(registriesRoot, file)))) return null;
  return (await readJson(path.join(registriesRoot, file))).records.find((record) => record.id === id) ?? null;
}

const selectionPacket = (entry, detail) => {
  const component = detail?.productSpecificComponent;
  return {
    id: entry.id,
    kind: entry.kind,
    title: entry.title,
    summary: entry.summary,
    selection: detail?.selection ?? null,
    ...(detail?.schemaVersion >= 3 ? { ownerNamespace: entry.id.split(".")[1] } : {}),
    ...(component ? { maturity: component.maturity, states: component.states, mockBoundaries: component.mockBoundaries, limitations: component.limitations, dependencies: component.dependencies } : {}),
    ...(detail?.template?.limitations ? { limitations: detail.template.limitations } : {}),
    ...(detail?.knowledge ? { knowledge: detail.knowledge } : {})
  };
};

async function inspectPattern(id, data = null) {
  data ??= await catalog();
  const entry = data.entries.find((item) => item.id === id && item.lifecycle === "active");
  if (!entry) throw new Error(`Unknown or inactive asset id ${id}.`);
  if (entry.kind !== "pattern") throw new Error(`inspect requires a Pattern id; ${id} is ${entry.kind}.`);
  const detail = await detailedRecord(id, entry.kind);
  const expanded = [id];
  const resolveRelations = async (relations, targetField) => {
    const values = [];
    for (const relation of relations) {
      const relatedId = relation[targetField];
      const relatedEntry = data.entries.find((item) => item.id === relatedId && item.lifecycle === "active");
      if (!relatedEntry) continue;
      const relatedDetail = await detailedRecord(relatedEntry.id, relatedEntry.kind);
      values.push({ relationType: relation.type, asset: selectionPacket(relatedEntry, relatedDetail) });
      expanded.push(relatedEntry.id);
    }
    return values.sort((a, b) => a.asset.id.localeCompare(b.asset.id));
  };
  const outgoing = detail?.resolvedRelations?.outgoing ?? entry.relations;
  const incoming = detail?.resolvedRelations?.incoming ?? [];
  return {
    pattern: selectionPacket(entry, detail),
    requiredKnowledge: (await resolveRelations(outgoing.filter((item) => item.type === "requires"), "target")).filter((item) => item.asset.kind === "knowledge"),
    recommendedReuse: await resolveRelations(incoming.filter((item) => item.type === "recommended-for"), "source"),
    compareAgainst: [
      ...await resolveRelations(outgoing.filter((item) => item.type === "distinguishes-from"), "target"),
      ...await resolveRelations(incoming.filter((item) => item.type === "distinguishes-from"), "source")
    ].sort((a, b) => a.asset.id.localeCompare(b.asset.id)),
    expanded
  };
}

async function comparePatterns() {
  const data = await catalog();
  const entries = data.entries.filter((entry) => entry.kind === "pattern" && entry.lifecycle === "active").sort((a, b) => a.id.localeCompare(b.id));
  const patterns = [];
  for (const entry of entries) {
    const detail = await detailedRecord(entry.id, entry.kind);
    const packet = await inspectPattern(entry.id, data);
    patterns.push({
      id: entry.id,
      title: entry.title,
      responsibilities: {
        required: detail.pattern.requiredRegions.map(({ id, responsibility }) => ({ id, responsibility })),
        optional: detail.pattern.optionalRegions.map(({ id, responsibility }) => ({ id, responsibility }))
      },
      useWhen: detail.selection.useWhen,
      avoidWhen: detail.selection.avoidWhen,
      requiredKnowledgeIds: packet.requiredKnowledge.map((item) => item.asset.id),
      recommendedReuseIds: packet.recommendedReuse.map((item) => item.asset.id),
      comparisonIds: packet.compareAgainst.map((item) => item.asset.id)
    });
  }
  return {
    schemaVersion: 1,
    command: "compare-patterns",
    returnedIds: patterns.map((item) => item.id),
    patterns,
    disclosure: { returned: patterns.map((item) => item.id), expanded: [], materializedOrUsed: [], mutated: [] }
  };
}

async function orient() {
  const compared = await comparePatterns();
  const index = await readJson(path.join(registriesRoot, "knowledge-discovery.registry.json"));
  if (index.schemaVersion !== 1 || index.kind !== "ux-proto-knowledge-discovery-index") throw new Error("Invalid Knowledge Discovery Index.");
  for (const item of index.entries) if (utf8Bytes(item) > index.stats.entryLimitBytes) throw new Error(`${item.id}: Knowledge Summary exceeds ${index.stats.entryLimitBytes} UTF-8 bytes.`);
  if (utf8Bytes(index.entries) > index.stats.indexLimitBytes || sha256(compactJson(index.entries)) !== index.sha256) throw new Error("Knowledge Discovery Index digest or byte budget is invalid.");
  const data = await catalog();
  const state = { schemaVersion: 1, catalogSha256: data.contentHash, knowledgeIndexSha256: index.sha256, knowledgeIndexStats: { ...index.stats, sha256: index.sha256 } };
  await mkdir(path.join(workspaceRoot, ".ux-proto"), { recursive: true });
  await writeFile(path.join(workspaceRoot, ".ux-proto/orient-state.json"), `${JSON.stringify(state, null, 2)}\n`);
  return { schemaVersion: 1, command: "orient", patterns: compared.patterns, knowledgeIndex: index.entries, knowledgeIndexStats: state.knowledgeIndexStats, disclosure: compared.disclosure };
}

async function inspect() {
  const id = process.argv[3];
  if (!id) throw new Error("inspect requires a Pattern id.");
  const packet = await inspectPattern(id);
  return { schemaVersion: 2, command: "inspect", id, pattern: packet.pattern, requiredKnowledge: packet.requiredKnowledge, recommendedReuse: packet.recommendedReuse, compareAgainst: packet.compareAgainst, disclosure: { returned: [], expanded: [...new Set(packet.expanded)], materializedOrUsed: [], mutated: [] } };
}

function migrationError(kind, version) {
  return `${kind} schemaVersion ${version} is no longer supported. Run orient, add required additionalKnowledge, and create a UX Proto ${kind} schemaVersion 3 document.`;
}

function validatePlanRequest(request) {
  if ([1, 2].includes(request.schemaVersion)) throw new Error(migrationError("plan request", request.schemaVersion));
  if (request.schemaVersion !== 3) throw new Error("Plan request schemaVersion must be 3.");
  const expectedKeys = ["additionalKnowledge", "bindingOverrides", "primaryPattern", "rationale", "schemaVersion", "selectedReuse", "supportingPatterns"];
  if (compactJson(Object.keys(request).sort()) !== compactJson(expectedKeys)) throw new Error(`Plan request v3 must contain exactly: ${expectedKeys.join(", ")}.`);
  if ("query" in request) throw new Error("Plan request v3 does not accept query.");
  if (request.primaryPattern !== null && (typeof request.primaryPattern !== "string" || !request.primaryPattern.startsWith("pattern."))) throw new Error("primaryPattern must be a Pattern ID or null.");
  if (!Array.isArray(request.supportingPatterns) || new Set(request.supportingPatterns).size !== request.supportingPatterns.length || request.supportingPatterns.some((id) => typeof id !== "string" || !id.startsWith("pattern."))) throw new Error("Invalid supportingPatterns.");
  if (request.primaryPattern !== null && request.supportingPatterns.includes(request.primaryPattern)) throw new Error("Primary Pattern cannot also be supporting.");
  if (!Array.isArray(request.selectedReuse) || new Set(request.selectedReuse).size !== request.selectedReuse.length || request.selectedReuse.some((id) => !/^(template|product)\./.test(id))) throw new Error("Invalid selectedReuse.");
  if (!Array.isArray(request.additionalKnowledge) || request.additionalKnowledge.length > 8 || new Set(request.additionalKnowledge).size !== request.additionalKnowledge.length || request.additionalKnowledge.some((id) => typeof id !== "string" || !id.startsWith("knowledge."))) throw new Error("additionalKnowledge is required and accepts at most 8 unique Knowledge IDs.");
  if (!request.rationale || typeof request.rationale !== "object" || typeof request.rationale.supporting !== "object" || Array.isArray(request.rationale.supporting)) throw new Error("Invalid rationale.");
  const rationaleKeys = Object.keys(request.rationale).sort();
  const expectedRationaleKeys = request.primaryPattern === null ? ["supporting"] : ["primary", "supporting"];
  if (compactJson(rationaleKeys) !== compactJson(expectedRationaleKeys)) throw new Error("rationale contains fields that do not follow actual Pattern selection.");
  if (request.primaryPattern === null && "primary" in request.rationale) throw new Error("Omit rationale.primary when primaryPattern is null.");
  if (request.primaryPattern !== null && (typeof request.rationale.primary !== "string" || !request.rationale.primary.trim())) throw new Error("Selected primary Pattern requires rationale.primary.");
  const supportingRationales = Object.keys(request.rationale.supporting).sort();
  if (JSON.stringify(supportingRationales) !== JSON.stringify([...request.supportingPatterns].sort())) throw new Error("rationale.supporting must contain exactly the selected supporting Pattern IDs.");
  for (const id of request.supportingPatterns) if (typeof request.rationale.supporting[id] !== "string" || !request.rationale.supporting[id].trim()) throw new Error(`Missing supporting rationale for ${id}.`);
  if (!request.bindingOverrides || typeof request.bindingOverrides !== "object" || Array.isArray(request.bindingOverrides)) throw new Error("bindingOverrides is required.");
  for (const value of Object.values(request.bindingOverrides)) if (!new Set(["on", "off"]).has(value)) throw new Error("Binding overrides must be on or off.");
}

async function projectContext() {
  const file = path.join(workspaceRoot, "design-context.json");
  if (!(await exists(file))) return { file: null, value: null };
  const value = await readJson(file);
  if (value.schemaVersion !== 1 || typeof value.profileId !== "string" || typeof value.bindingOverrides !== "object") throw new Error("Invalid design-context.json.");
  for (const state of Object.values(value.bindingOverrides)) if (!new Set(["on", "off"]).has(state)) throw new Error("Project binding overrides must be on or off.");
  return { file: "design-context.json", value };
}

async function designLanguage(data) {
  const file = path.join(workspaceRoot, "design-language.md");
  if (!(await exists(file))) return null;
  const contents = await readFile(file);
  const ids = [...new Set(contents.toString("utf8").match(/\b(?:template|product)\.[a-z0-9-]+(?:\.[a-z0-9-]+)?\b/g) ?? [])].sort();
  const authorizedReuse = new Set();
  for (const id of ids) {
    const entry = data.entries.find((item) => item.id === id && item.lifecycle === "active");
    if (entry && reusableKinds.has(entry.kind)) authorizedReuse.add(id);
  }
  return { path: "design-language.md", sha256: sha256(contents), authorizedReuse };
}

async function plan() {
  const requestPath = argument("--request", null);
  if (!requestPath) throw new Error("plan requires --request <file>.");
  const requestFile = path.resolve(workspaceRoot, requestPath);
  const requestContents = await readFile(requestFile);
  const request = JSON.parse(requestContents.toString("utf8"));
  validatePlanRequest(request);
  const data = await catalog();
  const [orientation, discovery] = await Promise.all([
    readJson(path.join(workspaceRoot, ".ux-proto/orient-state.json")).catch(() => null),
    readJson(path.join(registriesRoot, "knowledge-discovery.registry.json"))
  ]);
  if (!orientation) throw new Error("Plan v3 requires current orientation state. Run node scripts/corpus.mjs orient first.");
  if (orientation.catalogSha256 !== data.contentHash || orientation.knowledgeIndexSha256 !== discovery.sha256) throw new Error("Orientation state is stale. Run node scripts/corpus.mjs orient again.");
  const discoveryIds = new Set(discovery.entries.map((item) => item.id));
  for (const id of request.additionalKnowledge) if (!discoveryIds.has(id)) throw new Error(`additionalKnowledge ${id} is not active in the current Knowledge Discovery Index.`);
  const [profile, context, baseline] = await Promise.all([
    readJson(path.join(registriesRoot, "active-profile.registry.json")), projectContext(), designLanguage(data)
  ]);
  if (context.value?.profileId && context.value.profileId !== profile.id) throw new Error(`Project profile ${context.value.profileId} does not match active profile ${profile.id}.`);
  const bindingIds = new Set(profile.bindings.map((item) => item.id));
  for (const source of [context.value?.bindingOverrides ?? {}, request.bindingOverrides]) for (const id of Object.keys(source)) if (!bindingIds.has(id)) throw new Error(`Unknown binding override ${id}.`);
  const resolvedBindings = profile.bindings.map((binding) => {
    let state = binding.activation.defaultState;
    let source = "profile";
    if (context.value?.bindingOverrides?.[binding.id]) { state = context.value.bindingOverrides[binding.id]; source = "project"; }
    if (request.bindingOverrides[binding.id]) { state = request.bindingOverrides[binding.id]; source = "task"; }
    return { id: binding.id, state, source, defaultState: binding.activation.defaultState, reason: binding.reason, effect: binding.effect };
  });

  const selectedPatternIds = [...(request.primaryPattern ? [request.primaryPattern] : []), ...request.supportingPatterns];
  const packets = [];
  for (const id of selectedPatternIds) packets.push({ role: id === request.primaryPattern ? "primary" : "supporting", id, rationale: id === request.primaryPattern ? request.rationale.primary : request.rationale.supporting[id], ...(await inspectPattern(id, data)) });
  const activatedKnowledge = new Map();
  const patternReuse = new Map();
  const expanded = [];
  for (const packet of packets) {
    for (const item of packet.requiredKnowledge) {
      const current = activatedKnowledge.get(item.asset.id) ?? { asset: item.asset, sources: [] };
      current.sources.push({ type: "pattern-relation", patternId: packet.id });
      activatedKnowledge.set(item.asset.id, current);
    }
    for (const item of packet.recommendedReuse) patternReuse.set(item.asset.id, item);
    expanded.push(...packet.expanded);
  }

  const selectedReuse = [];
  for (const id of request.selectedReuse) {
    const entry = data.entries.find((item) => item.id === id && item.lifecycle === "active");
    if (!entry || !reusableKinds.has(entry.kind)) throw new Error(`Selected reuse ${id} is not an active executable reusable asset.`);
    if (patternReuse.has(id)) selectedReuse.push({ source: "pattern-relation", ...patternReuse.get(id) });
    else if (baseline?.authorizedReuse.has(id)) selectedReuse.push({ source: "design-language-baseline", asset: selectionPacket(entry, await detailedRecord(id, entry.kind)) });
    else throw new Error(`Selected reuse ${id} is not authorized by a selected Pattern relation${baseline ? " or design-language.md" : "; no design-language baseline is staged"}.`);
  }

  const executionRoots = new Map();
  for (const item of selectedReuse) executionRoots.set(item.asset.id, item.asset);
  for (const binding of resolvedBindings.filter((item) => item.state === "on" && item.effect?.assetId)) {
    const entry = data.entries.find((item) => item.id === binding.effect.assetId && item.lifecycle === "active");
    if (!entry || !reusableKinds.has(entry.kind)) throw new Error(`Active Binding ${binding.id} targets an invalid execution asset.`);
    executionRoots.set(entry.id, selectionPacket(entry, await detailedRecord(entry.id, entry.kind)));
  }
  const executionAssets = new Map(executionRoots);
  const executionDependencies = [];
  const queue = [...executionRoots.keys()];
  while (queue.length) {
    const parentId = queue.shift();
    const parent = data.entries.find((item) => item.id === parentId);
    const detail = await detailedRecord(parentId, parent.kind);
    const dependencies = parent.kind === "template" ? (detail.template.usesProductComponents ?? []) : (detail.productSpecificComponent.dependencies?.productComponents ?? []);
    for (const id of dependencies) {
      const entry = data.entries.find((item) => item.id === id && item.lifecycle === "active" && item.kind === "product-specific-component");
      if (!entry) throw new Error(`${parentId} declares missing or inactive Product-specific component dependency ${id}.`);
      if (!executionAssets.has(id)) {
        executionAssets.set(id, selectionPacket(entry, await detailedRecord(id, entry.kind)));
        queue.push(id);
      }
      executionDependencies.push({ assetId: id, requiredBy: parentId });
    }
  }

  for (const [assetId, asset] of executionAssets) {
    const entry = data.entries.find((item) => item.id === assetId);
    const detail = await detailedRecord(assetId, entry.kind);
    for (const relation of detail.resolvedRelations?.outgoing ?? entry.relations ?? []) if (relation.type === "requires") {
      const knowledgeEntry = data.entries.find((item) => item.id === relation.target && item.lifecycle === "active" && item.kind === "knowledge");
      if (!knowledgeEntry) continue;
      const knowledgeDetail = await detailedRecord(knowledgeEntry.id, knowledgeEntry.kind);
      const current = activatedKnowledge.get(knowledgeEntry.id) ?? { asset: selectionPacket(knowledgeEntry, knowledgeDetail), sources: [] };
      const bindingIdsForAsset = resolvedBindings.filter((item) => item.state === "on" && item.effect?.assetId === assetId).map((item) => `profile-binding:${item.id}`).sort();
      current.sources.push({ type: "asset-relation", assetId, ...(bindingIdsForAsset.length ? { reachedBy: bindingIdsForAsset } : {}) });
      activatedKnowledge.set(knowledgeEntry.id, current);
    }
  }
  for (const id of request.additionalKnowledge) {
    const entry = data.entries.find((item) => item.id === id && item.lifecycle === "active" && item.kind === "knowledge");
    const current = activatedKnowledge.get(id) ?? { asset: selectionPacket(entry, await detailedRecord(id, "knowledge")), sources: [] };
    current.sources.push({ type: "knowledge-index-selection" });
    activatedKnowledge.set(id, current);
  }

  const materialize = new Map();
  const imports = new Map();
  const addMaterialize = (assetId, source) => {
    const current = materialize.get(assetId) ?? { assetId, sources: [], command: `node scripts/corpus.mjs materialize ${assetId}` };
    if (!current.sources.includes(source)) current.sources.push(source);
    materialize.set(assetId, current);
  };
  for (const binding of resolvedBindings.filter((item) => item.state === "on" && item.effect.type === "materialize-template")) addMaterialize(binding.effect.assetId, `profile-binding:${binding.id}`);
  for (const [assetId, asset] of executionAssets) {
    const selected = selectedReuse.find((item) => item.asset.id === assetId);
    const dependencySources = executionDependencies.filter((item) => item.assetId === assetId).map((item) => `dependency:${item.requiredBy}`);
    const actionSources = [...new Set([...(selected ? [selected.source] : []), ...dependencySources])].sort();
    if (asset.kind === "template" && selected) addMaterialize(asset.id, selected.source);
    if (asset.kind === "product-specific-component") {
      const detail = await detailedRecord(asset.id, asset.kind);
      const implementation = detail.productSpecificComponent.implementation;
      imports.set(asset.id, { assetId: asset.id, sources: actionSources, maturity: detail.productSpecificComponent.maturity, importPath: implementation.importPath, exportName: implementation.exportName, statement: `import { ${implementation.exportName} } from "./${implementation.importPath}";` });
    }
  }

  const knowledgeSnapshots = [...activatedKnowledge.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([id, item]) => {
    const knowledge = item.asset.knowledge;
    const bytes = utf8Bytes(knowledge);
    if (bytes > 4096) throw new Error(`${id}: activated Knowledge guidance exceeds 4096 UTF-8 bytes (${bytes}).`);
    const sources = [...new Map(item.sources.map((source) => [compactJson(source), source])).values()].sort((a, b) => compactJson(a).localeCompare(compactJson(b)));
    return { id, title: item.asset.title, sha256: sha256(compactJson(knowledge)), utf8Bytes: bytes, knowledge, sources };
  });
  const guidanceBytes = knowledgeSnapshots.reduce((sum, item) => sum + item.utf8Bytes, 0);
  if (guidanceBytes > 16384) throw new Error(`Activated Knowledge guidance exceeds 16384 UTF-8 bytes (${guidanceBytes}).`);

  const receipt = {
    schemaVersion: 3,
    kind: "ux-proto-page-plan",
    request: stableObject(request),
    requestSource: { path: path.relative(workspaceRoot, requestFile), sha256: sha256(requestContents) },
    intent: { primaryPattern: request.primaryPattern, supportingPatterns: request.supportingPatterns, rationale: request.rationale },
    ...(baseline ? { designLanguage: { path: baseline.path, sha256: baseline.sha256 } } : {}),
    profile: { id: profile.id, contextFile: context.file, resolvedBindings, suppressedBindings: resolvedBindings.filter((item) => item.state === "off") },
    patterns: packets.map((packet) => ({ role: packet.role, id: packet.id, rationale: packet.rationale })),
    activatedKnowledge: knowledgeSnapshots,
    knowledgeIndexStats: orientation.knowledgeIndexStats,
    knowledgeGuidanceStats: { activatedCount: knowledgeSnapshots.length, additionalCount: request.additionalKnowledge.length, utf8Bytes: guidanceBytes, entryLimitBytes: 4096, totalLimitBytes: 16384 },
    selectedReuse,
    executionDependencies: [...new Map(executionDependencies.map((item) => [`${item.assetId}\0${item.requiredBy}`, item])).values()].sort((a, b) => a.assetId.localeCompare(b.assetId) || a.requiredBy.localeCompare(b.requiredBy)),
    actions: { materialize: [...materialize.values()].sort((a, b) => a.assetId.localeCompare(b.assetId)), import: [...imports.values()].sort((a, b) => a.assetId.localeCompare(b.assetId)) }
  };
  const writeRelative = argument("--write", ".ux-proto/page-plan.json");
  const output = path.resolve(workspaceRoot, writeRelative);
  const relative = path.relative(workspaceRoot, output);
  if (relative.startsWith("..") || path.isAbsolute(relative)) throw new Error("Plan receipt must remain inside the workspace.");
  await mkdir(path.dirname(output), { recursive: true });
  await writeFile(output, `${JSON.stringify(receipt, null, 2)}\n`);
  return { command: "plan", receipt: relative, ...receipt, disclosure: { returned: [], expanded: [...new Set(expanded)].sort(), materializedOrUsed: [], mutated: [] } };
}

function assertPageOwned(output) {
  const relative = path.relative(workspaceRoot, output);
  if (relative.startsWith("..") || path.isAbsolute(relative)) throw new Error("Materialize output must remain inside the workspace.");
  if (protectedRoots.some((root) => relative === root || relative.startsWith(`${root}${path.sep}`))) throw new Error(`Materialize output is protected: ${relative}`);
}

async function materialize() {
  const id = process.argv[3];
  if (!id) throw new Error("materialize requires a Template id.");
  if (process.argv.includes("--output")) throw new Error("materialize uses the fixed page-assets/<template-id>/ target; --output is not supported.");
  const registry = await readJson(path.join(registriesRoot, "templates.registry.json"));
  const record = registry.records.find((item) => item.id === id);
  if (!record) throw new Error(`Unknown Template id ${id}.`);
  const output = path.join(workspaceRoot, "page-assets", id);
  assertPageOwned(output);
  const artifacts = record.template.artifacts;
  const receiptFile = path.join(workspaceRoot, ".ux-proto/page-plan.json");
  if (await exists(receiptFile)) {
    const validator = await import(pathToFileURL(path.join(workspaceRoot, "scripts/validate-page-plan.mjs")));
    await validator.validatePagePlan({ receiptFile, catalogFile: path.join(registriesRoot, "catalog.json"), knowledgeFile: path.join(registriesRoot, "knowledge.registry.json") });
    const receipt = await readJson(receiptFile);
    if ([1, 2].includes(receipt.schemaVersion)) throw new Error(migrationError("page-plan", receipt.schemaVersion));
    if (receipt.schemaVersion !== 3 || !receipt.actions?.materialize?.some((item) => item.assetId === id)) throw new Error(`Materialize ${id} is not authorized by the current page-plan. Update selectedReuse or Binding selection and rerun plan.`);
  }
  const expected = [];
  const imports = artifacts.filter((artifact) => ["tsx", "ts"].includes(artifact.role)).map((artifact) => {
    const exportName = path.basename(artifact.target, path.extname(artifact.target));
    const importPath = `./${path.relative(workspaceRoot, path.join(output, exportName)).split(path.sep).join("/")}`;
    return { exportName, importPath, statement: `import { ${exportName} } from "${importPath}";` };
  });
  let complete = true;
  let presentCount = 0;
  for (const artifact of artifacts) {
    const source = path.join(workspaceRoot, artifact.consumerPath);
    const destination = path.join(output, artifact.target);
    assertPageOwned(destination);
    const contents = await readFile(source, "utf8");
    if (sha256(contents) !== artifact.contentHash) throw new Error(`Template consumer hash mismatch for ${artifact.consumerPath}`);
    const marker = artifact.role === "css" ? `/* ux-proto-template: ${id} ${artifact.contentHash} */\n` : `// ux-proto-template: ${id} ${artifact.contentHash}\n`;
    const present = await exists(destination);
    if (present) {
      presentCount += 1;
      const existing = await readFile(destination, "utf8");
      if (!existing.startsWith(marker)) throw new Error(`Existing materialized file has missing or mismatched provenance: ${destination}`);
    } else complete = false;
    expected.push({ destination, contents: marker + contents });
  }
  if (complete) return { schemaVersion: 3, command: "materialize", id, status: "already-materialized", contentHashes: Object.fromEntries(artifacts.map((item) => [item.target, item.contentHash])), written: [], imports, disclosure: { returned: [], expanded: [id], materializedOrUsed: [id], mutated: [] } };
  if (presentCount) throw new Error(`Partial materialization for ${id}; remove or repair the complete page-owned asset set before retrying.`);
  const temporary = `${output}.tmp-${process.pid}`;
  await rm(temporary, { recursive: true, force: true });
  await mkdir(temporary, { recursive: true });
  try {
    for (const item of expected) {
      const target = path.join(temporary, path.relative(output, item.destination));
      await mkdir(path.dirname(target), { recursive: true });
      await writeFile(target, item.contents, "utf8");
    }
    await mkdir(path.dirname(output), { recursive: true });
    await rename(temporary, output);
  } catch (error) {
    await rm(temporary, { recursive: true, force: true });
    throw error;
  }
  const written = expected.map((item) => path.relative(workspaceRoot, item.destination));
  return { schemaVersion: 3, command: "materialize", id, status: "materialized", contentHashes: Object.fromEntries(artifacts.map((item) => [item.target, item.contentHash])), written, imports, disclosure: { returned: [], expanded: [id], materializedOrUsed: [id], mutated: [] } };
}

const command = process.argv[2];
if (command === "search") throw new Error("The lexical search command was removed by UX Proto Consumer Workflow v2. Use compare-patterns, then exact-ID inspect.");
const result = command === "orient" ? await orient() : command === "compare-patterns" ? await comparePatterns() : command === "inspect" ? await inspect() : command === "plan" ? await plan() : command === "materialize" ? await materialize() : null;
if (!result) throw new Error("Usage: corpus.mjs orient|compare-patterns|inspect|plan|materialize ...");
console.log(JSON.stringify(result, null, 2));
