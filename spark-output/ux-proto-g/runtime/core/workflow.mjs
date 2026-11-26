import { lstat, mkdir, mkdtemp, readFile, readdir, realpath, rename, rm, writeFile } from "node:fs/promises";
import { randomUUID } from "node:crypto";
import path from "node:path";
import { assertCanonicalAssetId, containedPath, digestObject, exists, fail, readJson, sha256, stableJson } from "./common.mjs";
import { resolveContextPacket, resolveStageContextPacket } from "./source-resolver.mjs";
import { configurationFingerprint, runTemplateConfigurator } from "./configurator.mjs";
import { requireUsableSnapshot } from "./snapshot.mjs";

async function snapshotRecord(snapshotRoot, id) {
  assertCanonicalAssetId(id);
  const root = path.resolve(snapshotRoot), recordsRoot = containedPath(root, "records"), file = containedPath(recordsRoot, `${id}.json`);
  if (!(await exists(file))) fail("asset-outside-snapshot", "Asset is outside the current resolved scope.", { assetId: id });
  const [rootInfo, recordsInfo, info] = await Promise.all([lstat(root), lstat(recordsRoot), lstat(file)]);
  const realRoot = await realpath(root);
  if (rootInfo.isSymbolicLink() || !rootInfo.isDirectory() || recordsInfo.isSymbolicLink() || !recordsInfo.isDirectory() || info.isSymbolicLink() || !info.isFile() || !(await realpath(recordsRoot)).startsWith(`${realRoot}${path.sep}`)) fail("snapshot-record-boundary", "Snapshot record is outside a real contained records directory.", { assetId: id });
  return readJson(file, "invalid-snapshot-record");
}

export async function authoringContextFromSnapshot(snapshotRoot) {
  const manifest = await requireUsableSnapshot(snapshotRoot);
  return resolveStageContextPacket({ resolution: { report: { status: "resolved" }, records: manifest.records }, bindings: manifest.entrypoints });
}
function templateConsumptionProjection(record) {
  const prefix = `files/${record.id}/`;
  if (!record.files.some((file) => file.path === `${prefix}${record.entry}`)) fail("template-main-entry-missing", "Template main entry is absent from materialization closure.", { assetId: record.id });
  const target = `page-assets/${record.id}`, importPath = `./${target}/${record.entry.replace(/\.(?:tsx?|jsx?)$/, "")}`;
  return { target, imports: [{ exportName: record.authoring.mainExport, importPath, statement: `import { ${record.authoring.mainExport} } from "${importPath}";` }], editPolicy: "page-owned" };
}
function normalizedRecord(record, manifest) {
  const common = { id: record.id, kind: record.kind, title: record.title, abstract: record.abstract };
  if (["Pattern", "Knowledge"].includes(record.kind)) return { ...common, content: record.content };
  if (record.kind === "Template") return { ...common, entry: record.entry, artifacts: record.artifacts, authoring: record.authoring, publicApi: record.publicApi, ...(record.configuration ? { configuration: record.configuration } : {}), materialization: templateConsumptionProjection(record) };
  const surface = manifest.publicSurface.find((item) => item.assetId === record.id);
  return { ...common, entry: record.entry, artifacts: record.artifacts, publicSurface: Object.fromEntries(Object.entries(surface ?? {}).filter(([key]) => !["assetId", "entry"].includes(key))), api: record.api, usage: record.usage };
}
export async function inspectFromSnapshot(snapshotRoot, assetId) { const manifest = await requireUsableSnapshot(snapshotRoot); return normalizedRecord(await snapshotRecord(snapshotRoot, assetId), manifest); }
export async function contextAuthoringFromSnapshot(snapshotRoot) { return authoringContextFromSnapshot(snapshotRoot); }
export async function contextReviewFromSnapshot(snapshotRoot) { const manifest = await requireUsableSnapshot(snapshotRoot); return resolveStageContextPacket({ resolution: { report: { status: "resolved" }, records: manifest.records }, bindings: manifest.review }); }
export async function catalogFromSnapshot(snapshotRoot) { return { assets: (await requireUsableSnapshot(snapshotRoot)).catalog }; }
export async function expandFromSnapshot(snapshotRoot, assetIds) { const manifest = await requireUsableSnapshot(snapshotRoot); return resolveContextPacket({ resolution: { report: { status: "resolved" }, records: manifest.records }, assetIds }); }

function markerFor(assetId, relative, digest) {
  const extension = path.extname(relative).toLowerCase();
  if ([".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"].includes(extension)) return `// ux-proto-template: ${assetId} ${digest}\n`;
  if (extension === ".css") return `/* ux-proto-template: ${assetId} ${digest} */\n`;
  if ([".html", ".htm", ".svg"].includes(extension)) return `<!-- ux-proto-template: ${assetId} ${digest} -->\n`;
  return null;
}
async function walkFiles(root, relative = "") {
  const files = [];
  for (const entry of (await readdir(path.join(root, relative), { withFileTypes: true })).sort((left, right) => left.name.localeCompare(right.name))) {
    const child = path.posix.join(relative, entry.name);
    if (entry.isSymbolicLink() || (!entry.isDirectory() && !entry.isFile())) fail("partial-materialization", "Materialized Template contains an unsupported object.", { path: child });
    if (entry.isDirectory()) files.push(...await walkFiles(root, child)); else files.push(child);
  }
  return files;
}
async function treeRecord(root) { return Promise.all((await walkFiles(root)).map(async (relative) => ({ path: relative, sha256: sha256(await readFile(containedPath(root, relative))) }))); }

async function materializationContract({ snapshotRoot, projectRoot, assetId }) {
  await requireUsableSnapshot(snapshotRoot);
  const record = await snapshotRecord(snapshotRoot, assetId);
  if (record.kind !== "Template") fail("not-materializable", "Asset is not a page-owned Template.", { assetId });
  const governedProject = path.resolve(projectRoot), pageAssetsRoot = containedPath(governedProject, "page-assets"), outputRoot = containedPath(pageAssetsRoot, assetId);
  const projectInfo = await lstat(governedProject), realProject = await realpath(governedProject);
  if (projectInfo.isSymbolicLink() || !projectInfo.isDirectory()) fail("materialization-path-boundary", "Workspace root must be a real directory.", { path: governedProject });
  const pageAssetsInfo = await lstat(pageAssetsRoot).catch((error) => error?.code === "ENOENT" ? null : Promise.reject(error));
  if (pageAssetsInfo && (pageAssetsInfo.isSymbolicLink() || !pageAssetsInfo.isDirectory() || !(await realpath(pageAssetsRoot)).startsWith(`${realProject}${path.sep}`))) fail("materialization-path-boundary", "page-assets must be a contained real directory.", { path: pageAssetsRoot });
  const snapshotRootReal = await realpath(path.resolve(snapshotRoot)), sourceRoot = containedPath(snapshotRootReal, "files", assetId);
  const sourceInfo = await lstat(sourceRoot);
  if (sourceInfo.isSymbolicLink() || !sourceInfo.isDirectory()) fail("template-path-boundary", "Template snapshot source root is invalid.", { assetId });
  const targets = await Promise.all(record.files.map(async (file) => {
    const prefix = `files/${assetId}/`;
    if (!file.path.startsWith(prefix)) fail("template-path-boundary", "Template source escapes asset root.", { assetId, path: file.path });
    const relative = file.path.slice(prefix.length), source = containedPath(sourceRoot, relative), bytes = await readFile(source);
    if (sha256(bytes) !== file.sha256) fail("template-source-hash-mismatch", "Template snapshot source hash is invalid.", { assetId, path: relative });
    return { relative, source, bytes, sha256: file.sha256 };
  }));
  return { record, governedProject, realProject, pageAssetsRoot, outputRoot, sourceRoot, targets, sidecarName: ".ux-proto-template.json" };
}
async function assertPageAssetsBoundary(contract) {
  await mkdir(contract.pageAssetsRoot, { recursive: true });
  const info = await lstat(contract.pageAssetsRoot), real = await realpath(contract.pageAssetsRoot);
  if (info.isSymbolicLink() || !info.isDirectory() || !real.startsWith(`${contract.realProject}${path.sep}`)) fail("materialization-path-boundary", "page-assets escaped the workspace boundary.", { path: contract.pageAssetsRoot });
}
async function outputContents(contract, selection) {
  if (!contract.record.configuration) return contract.targets.map((target) => ({ relative: target.relative, originalHash: target.sha256, output: Buffer.concat([Buffer.from(markerFor(contract.record.id, target.relative, target.sha256) ?? ""), target.bytes]) }));
  const result = await runTemplateConfigurator({ snapshotRoot: path.resolve(contract.sourceRoot, "..", ".."), record: contract.record, decisions: selection.decisions });
  return result.files.map(({ relative, output }) => { const hash = sha256(output); return { relative, originalHash: hash, output: Buffer.concat([Buffer.from(markerFor(contract.record.id, relative, hash) ?? ""), output]) }; });
}
function configurationMenu(record, reselect) {
  return { schemaVersion: 2, status: reselect ? "reselect-configuration-required" : "configuration-required", assetId: record.id, wrote: false, readyToAuthor: false, configuration: { fingerprint: configurationFingerprint(record), blocks: record.configuration.blocks, constraints: record.configuration.constraints, presets: record.configuration.presets, nonConfigurableBoundary: record.configuration.nonConfigurableBoundary }, nextActions: [{ kind: "materialize-submit-selection", assetId: record.id }] };
}
async function validateCurrentTarget(contract, { allowMissing = false } = {}) {
  const rootInfo = await lstat(contract.outputRoot).catch((error) => error?.code === "ENOENT" ? null : Promise.reject(error));
  if (!rootInfo) { if (allowMissing) return { status: "missing" }; fail("materialization-missing", "Template materialization is missing.", { assetId: contract.record.id }); }
  if (rootInfo.isSymbolicLink() || !rootInfo.isDirectory()) fail("partial-materialization", "Template target is not a regular directory.", { assetId: contract.record.id });
  const sidecar = await readJson(containedPath(contract.outputRoot, contract.sidecarName), "materialization-provenance-mismatch");
  if (sidecar?.kind !== "ux-proto-template-provenance" || sidecar.assetId !== contract.record.id || !Array.isArray(sidecar.files)) fail("materialization-provenance-mismatch", "Template provenance sidecar is invalid.", { assetId: contract.record.id });
  const actual = await walkFiles(contract.outputRoot), expected = [...sidecar.files.map((file) => file.path), contract.sidecarName].sort();
  if (JSON.stringify(actual.sort()) !== JSON.stringify(expected)) fail("partial-materialization", "Template target has missing or extra files.", { assetId: contract.record.id });
  for (const file of sidecar.files) {
    const bytes = await readFile(containedPath(contract.outputRoot, file.path)), marker = markerFor(contract.record.id, file.path, file.sourceHash);
    if (!marker || !bytes.toString("utf8").startsWith(marker)) fail("materialization-provenance-mismatch", "Template provenance marker does not match.", { assetId: contract.record.id, path: file.path });
    if (sidecar.schemaVersion === 2 && sha256(bytes.subarray(Buffer.byteLength(marker))) !== file.sourceHash) fail("materialization-provenance-mismatch", "Configured Template generated content does not match provenance.", { assetId: contract.record.id, path: file.path });
  }
  return { status: "verified", sidecar };
}
export async function validateMaterializedTemplate({ snapshotRoot, projectRoot, assetId, allowMissing = false }) { return validateCurrentTarget(await materializationContract({ snapshotRoot, projectRoot, assetId }), { allowMissing }); }
function originalRecordPath(contract) { return containedPath(contract.governedProject, ".ux-proto", "materialization-records", `${contract.record.id}.json`); }
async function assertOriginalRecord(contract) {
  const file = originalRecordPath(contract);
  if (!(await exists(file))) fail("reselect-original-record-missing", "This materialization predates independent original-byte records and cannot be reselected.", { assetId: contract.record.id });
  const expected = await readJson(file, "reselect-original-record-invalid"), actual = await treeRecord(contract.outputRoot);
  if (expected.kind !== "ux-proto-materialization-original-record" || expected.assetId !== contract.record.id || digestObject(expected.files) !== digestObject(actual)) fail("reselect-target-edited", "Configured Template target was edited or its proof no longer matches; reselect is refused.", { assetId: contract.record.id });
}
async function writeStage(contract, contents, selection) {
  await assertPageAssetsBoundary(contract);
  const temporary = await mkdtemp(containedPath(contract.pageAssetsRoot, `.${contract.record.id}.tmp-${process.pid}-`));
  for (const item of contents) { const target = containedPath(temporary, item.relative); await mkdir(path.dirname(target), { recursive: true }); await writeFile(target, item.output); }
  const sidecar = { schemaVersion: contract.record.configuration ? 2 : 1, kind: "ux-proto-template-provenance", assetId: contract.record.id, ...(contract.record.configuration ? { configurationFingerprint: selection.fingerprint, decisions: selection.decisions } : {}), files: contents.map((item) => ({ path: item.relative, artifactType: "text", sourceHash: item.originalHash })).sort((left, right) => left.path.localeCompare(right.path)) };
  await writeFile(containedPath(temporary, contract.sidecarName), stableJson(sidecar));
  return { temporary, original: { schemaVersion: 1, kind: "ux-proto-materialization-original-record", assetId: contract.record.id, files: await treeRecord(temporary) } };
}
async function commitNew(contract, stage) {
  const recordFile = originalRecordPath(contract), recordStage = `${recordFile}.tmp-${process.pid}`;
  await mkdir(path.dirname(recordFile), { recursive: true }); await writeFile(recordStage, stableJson(stage.original));
  try { await rename(stage.temporary, contract.outputRoot); await rename(recordStage, recordFile); }
  catch (error) { await rm(stage.temporary, { recursive: true, force: true }); await rm(recordStage, { force: true }); await rm(contract.outputRoot, { recursive: true, force: true }); throw error; }
}
export async function restoreReselectionState({ outputRoot, oldTarget, recordFile, oldRecord }) {
  if (await exists(oldTarget)) { await rm(outputRoot, { recursive: true, force: true }); await rename(oldTarget, outputRoot); }
  if (await exists(oldRecord)) { await rm(recordFile, { force: true }); await rename(oldRecord, recordFile); }
}
async function commitReselection(contract, stage, { afterTargetSwap = null } = {}) {
  const recordFile = originalRecordPath(contract), recovery = containedPath(contract.governedProject, ".ux-proto", "recovery", "materializations", contract.record.id, randomUUID()), oldTarget = containedPath(recovery, "original"), oldRecord = containedPath(recovery, "original-record.json"), recordStage = `${recordFile}.tmp-${process.pid}`;
  await mkdir(recovery, { recursive: true }); await writeFile(recordStage, stableJson(stage.original));
  try { await assertPageAssetsBoundary(contract); await rename(contract.outputRoot, oldTarget); await rename(recordFile, oldRecord); await rename(stage.temporary, contract.outputRoot); if (afterTargetSwap) await afterTargetSwap(); await rename(recordStage, recordFile); }
  catch (error) {
    await rm(stage.temporary, { recursive: true, force: true }); await rm(recordStage, { force: true });
    await restoreReselectionState({ outputRoot: contract.outputRoot, oldTarget, recordFile, oldRecord });
    throw error;
  }
  return path.relative(contract.governedProject, recovery).split(path.sep).join("/");
}
export async function materializeFromSnapshot({ snapshotRoot, projectRoot, assetId, checkOnly = false, selection = null, reselect = false, afterReselectionTargetSwap = null }) {
  const contract = await materializationContract({ snapshotRoot, projectRoot, assetId }), current = await validateCurrentTarget(contract, { allowMissing: true }), configured = Boolean(contract.record.configuration);
  if (current.status === "verified" && !reselect) return { schemaVersion: 2, status: "already-materialized", assetId, written: [], provenanceFiles: [`page-assets/${assetId}/${contract.sidecarName}`], imports: templateConsumptionProjection(contract.record).imports, editPolicy: "page-owned", customizationSurfaces: contract.record.authoring.customizationSurfaces, wrote: false, readyToAuthor: true };
  if (configured && !selection) { if (reselect) await assertOriginalRecord(contract); return configurationMenu(contract.record, reselect); }
  if (checkOnly) return { schemaVersion: 2, status: "missing", assetId, written: [], wrote: false, readyToAuthor: false };
  if (configured && (!selection || selection.fingerprint !== configurationFingerprint(contract.record))) fail("configuration-fingerprint-mismatch", "Configuration changed; read a new configuration menu before submitting selections.", { assetId });
  if (!configured && reselect) fail("reselect-not-configured", "Only configured Templates support explicit reselection.", { assetId });
  if (current.status === "verified" && reselect) await assertOriginalRecord(contract);
  if (current.status !== "missing" && !reselect) fail("partial-materialization", "Existing Template target cannot be overwritten.", { assetId });
  const resolvedSelection = configured ? { fingerprint: selection.fingerprint, decisions: selection.decisions } : null, contents = await outputContents(contract, resolvedSelection), stage = await writeStage(contract, contents, resolvedSelection);
  let recoveryPath = null;
  try { if (reselect) recoveryPath = await commitReselection(contract, stage, { afterTargetSwap: afterReselectionTargetSwap }); else await commitNew(contract, stage); } catch (error) { await rm(stage.temporary, { recursive: true, force: true }); throw error; }
  return { schemaVersion: 2, status: reselect ? "reselected" : "materialized", assetId, written: contents.map((item) => `page-assets/${assetId}/${item.relative}`), provenanceFiles: [`page-assets/${assetId}/${contract.sidecarName}`], imports: templateConsumptionProjection(contract.record).imports, editPolicy: "page-owned", customizationSurfaces: contract.record.authoring.customizationSurfaces, wrote: true, readyToAuthor: true, ...(recoveryPath ? { recoveryPath } : {}) };
}
export async function protectedSnapshotImportPlugin(snapshotRoot) { const manifest = await requireUsableSnapshot(snapshotRoot); const imports = new Map(manifest.publicSurface.map((item) => [item.specifier, containedPath(snapshotRoot, item.entry)])); return { name: "ux-proto-snapshot-public-surface", setup(build) { build.onResolve({ filter: /^@ux-proto\/assets\// }, (args) => imports.has(args.path) ? { path: imports.get(args.path) } : { errors: [{ text: `Public asset import is outside the resolved snapshot: ${args.path}` }] }); } }; }
export async function snapshotExecutionRecords(snapshotRoot) { const manifest = await requireUsableSnapshot(snapshotRoot); return new Map(manifest.publicSurface.map((item) => [containedPath(snapshotRoot, item.entry), item.assetId])); }
