import { lstat, mkdir, mkdtemp, readFile, readdir, realpath, rename, rm, rmdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { assertCanonicalAssetId, containedPath, digestObject, exists, fail, readJson, sha256, stableJson } from "./common.mjs";
import { requireUsableSnapshot } from "./snapshot.mjs";

async function snapshotRecord(snapshotRoot, id) {
  assertCanonicalAssetId(id);
  const root = path.resolve(snapshotRoot);
  const rootInfo = await lstat(root);
  if (rootInfo.isSymbolicLink() || !rootInfo.isDirectory()) fail("snapshot-record-boundary", "Snapshot root must be a real directory.", { path: root });
  const recordsRoot = containedPath(root, "records");
  const recordsInfo = await lstat(recordsRoot);
  const realRoot = await realpath(root);
  if (recordsInfo.isSymbolicLink() || !recordsInfo.isDirectory() || !(await realpath(recordsRoot)).startsWith(`${realRoot}${path.sep}`)) fail("snapshot-record-boundary", "Snapshot records must be a contained real directory.", { path: recordsRoot });
  const file = containedPath(recordsRoot, `${id}.json`);
  if (!(await exists(file))) fail("asset-outside-snapshot", `资产不在当前 resolved Scope：${id}。`, { assetId: id });
  const info = await lstat(file);
  const realRecordsRoot = await realpath(recordsRoot);
  if (info.isSymbolicLink() || !info.isFile() || !((await realpath(file)).startsWith(`${realRecordsRoot}${path.sep}`))) fail("snapshot-record-boundary", `Snapshot record is not a contained regular file: ${id}.`, { assetId: id });
  return readJson(file, "invalid-snapshot-record");
}

export async function authoringContextFromSnapshot(snapshotRoot) {
  const manifest = await requireUsableSnapshot(snapshotRoot);
  return {
    readyToAuthor: true,
    snapshot: { state: "usable", contentDigest: manifest.contentDigest, proof: ".ux-proto/resolved-assets/manifest.json" },
    pack: { id: manifest.pack.id, version: manifest.pack.version },
    baseline: manifest.baseline,
    recommendations: manifest.recommendations,
    assetCatalog: manifest.assetCatalog
  };
}

function templateConsumptionProjection(record) {
  const target = `page-assets/${record.id}`;
  const prefix = `files/${record.id}/`;
  const entryFile = record.files.find((file) => file.path.startsWith(prefix) && file.path.slice(prefix.length) === record.entry);
  if (!entryFile) fail("template-main-entry-missing", `${record.id} 的 main entry 未进入 materialization closure。`, { assetId: record.id });
  const relativeEntry = entryFile.path.slice(prefix.length);
  const importPath = `./${target}/${relativeEntry.replace(/\.(?:tsx?|jsx?)$/, "")}`;
  const mainExport = record.authoring.mainExport;
  return {
    target,
    imports: [{ exportName: mainExport, importPath, statement: `import { ${mainExport} } from "${importPath}";` }],
    editPolicy: "page-owned"
  };
}

function normalizedRecord(record, manifest) {
  const base = {
    id: record.id,
    kind: record.kind,
    summary: record.summary,
    selection: record.selection,
    requires: record.requires,
    relations: record.relations,
    ...(record.content ? { content: record.content } : {}),
    ...(record.kind === "Template" ? { authoring: record.authoring, materialization: templateConsumptionProjection(record) } : {}),
    ...(record.kind === "Pack Component" ? {
      publicSurface: Object.fromEntries(Object.entries(manifest.publicSurface.find((item) => item.assetId === record.id)).filter(([key]) => !["assetId", "entry"].includes(key))),
      api: record.api,
      usage: record.usage
    } : {})
  };
  return base;
}

export async function inspectFromSnapshot(snapshotRoot, assetId) {
  assertCanonicalAssetId(assetId);
  const manifest = await requireUsableSnapshot(snapshotRoot);
  const record = await snapshotRecord(snapshotRoot, assetId);
  const requiredKnowledge = [];
  for (const id of [...new Set(record.requires ?? [])].sort()) {
    const dependency = await snapshotRecord(snapshotRoot, id);
    if (dependency.kind === "Knowledge") requiredKnowledge.push(normalizedRecord(dependency, manifest));
  }
  return { ...normalizedRecord(record, manifest), requiredKnowledge };
}

export async function contextAuthoringFromSnapshot(snapshotRoot) {
  const manifest = await requireUsableSnapshot(snapshotRoot);
  return { baseline: manifest.baseline };
}

export async function contextReviewFromSnapshot(snapshotRoot) {
  const manifest = await requireUsableSnapshot(snapshotRoot);
  const review = [];
  for (const id of manifest.review.assets) {
    const record = await snapshotRecord(snapshotRoot, id);
    if (record.kind !== "Knowledge" || record.lifecycle !== "active") fail("invalid-review-target", `review target 不是 active Knowledge：${id}。`, { assetId: id });
    review.push(normalizedRecord(record, manifest));
  }
  return { review };
}

function markerFor(assetId, relative, digest) {
  const extension = path.extname(relative).toLowerCase();
  if ([".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"].includes(extension)) return `// ux-proto-template: ${assetId} ${digest}\n`;
  if (extension === ".css") return `/* ux-proto-template: ${assetId} ${digest} */\n`;
  if ([".html", ".htm", ".svg"].includes(extension)) return `<!-- ux-proto-template: ${assetId} ${digest} -->\n`;
  return null;
}

async function materializationContract({ snapshotRoot, projectRoot, assetId }) {
  assertCanonicalAssetId(assetId);
  await requireUsableSnapshot(snapshotRoot);
  const record = await snapshotRecord(snapshotRoot, assetId);
  if (record.kind !== "Template") fail("not-materializable", `${assetId} 不是 page-owned Template。`, { assetId });
  const governedProject = path.resolve(projectRoot);
  const pageAssetsRoot = containedPath(governedProject, "page-assets");
  const projectInfo = await lstat(governedProject);
  if (projectInfo.isSymbolicLink() || !projectInfo.isDirectory()) fail("materialization-path-boundary", "Workspace root must be a real directory.", { path: governedProject });
  const existingPageAssets = await lstat(pageAssetsRoot).catch((error) => error?.code === "ENOENT" ? null : Promise.reject(error));
  if (existingPageAssets) {
    const realProjectRoot = await realpath(governedProject);
    if (existingPageAssets.isSymbolicLink() || !existingPageAssets.isDirectory() || !(await realpath(pageAssetsRoot)).startsWith(`${realProjectRoot}${path.sep}`)) fail("materialization-path-boundary", "page-assets must be a contained real directory.", { path: pageAssetsRoot });
  }
  const outputRoot = containedPath(pageAssetsRoot, assetId);
  const snapshotBoundary = path.resolve(snapshotRoot);
  const assetFilesRoot = containedPath(snapshotBoundary, "files", assetId);
  const assetFilesInfo = await lstat(assetFilesRoot);
  const realSnapshotBoundary = await realpath(snapshotBoundary);
  const realAssetFilesRoot = await realpath(assetFilesRoot);
  if (assetFilesInfo.isSymbolicLink() || !assetFilesInfo.isDirectory() || !realAssetFilesRoot.startsWith(`${realSnapshotBoundary}${path.sep}`)) fail("template-path-boundary", `Template files root escapes the current snapshot: ${assetId}.`, { assetId, path: assetFilesRoot });
  const targets = record.files.map((file) => {
    const source = containedPath(snapshotBoundary, file.path);
    const relative = path.relative(assetFilesRoot, source);
    if (!relative || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) fail("template-path-boundary", `Template file escapes its governed asset root: ${file.path}.`, { assetId, path: file.path });
    return { ...file, relative, source, destination: containedPath(outputRoot, relative) };
  });
  const contents = [];
  for (const target of targets) {
    const sourceInfo = await lstat(target.source);
    if (sourceInfo.isSymbolicLink() || !sourceInfo.isFile() || !(await realpath(target.source)).startsWith(`${realAssetFilesRoot}${path.sep}`)) fail("template-path-boundary", `Template source is not a contained regular file: ${target.path}.`, { assetId, path: target.path });
    const source = await readFile(target.source);
    if (sha256(source) !== target.sha256) fail("template-source-hash-mismatch", `Template snapshot hash 无效：${target.path}。`, { assetId, path: target.path });
    const marker = markerFor(assetId, target.relative, target.sha256);
    contents.push({ ...target, output: marker ? Buffer.concat([Buffer.from(marker), source]) : source, marker, artifactType: marker ? "text" : "binary" });
  }
  const sidecarName = ".ux-proto-template.json";
  const sidecar = {
    schemaVersion: 1,
    kind: "ux-proto-template-provenance",
    assetId,
    files: contents.map((item) => ({ path: item.relative.split(path.sep).join("/"), artifactType: item.artifactType, sourceHash: item.sha256 })).sort((a, b) => a.path.localeCompare(b.path))
  };
  return { record, pageAssetsRoot, outputRoot, targets, contents, sidecarName, sidecar, existingPageAssets };
}

export async function validateMaterializedTemplate({ snapshotRoot, projectRoot, assetId, allowMissing = false }) {
  const contract = await materializationContract({ snapshotRoot, projectRoot, assetId });
  const { outputRoot, sidecarName } = contract;
  const existingRoot = await lstat(outputRoot).catch((error) => error?.code === "ENOENT" ? null : Promise.reject(error));
  if (!existingRoot) {
    if (allowMissing) return { ...contract, status: "missing" };
    fail("materialization-missing", `Template materialization is missing: ${assetId}.`, { assetId });
  }
  if (existingRoot.isSymbolicLink() || !existingRoot.isDirectory()) fail("partial-materialization", `Template 目标不是普通目录：${assetId}。`, { assetId });
  const existingFiles = [];
  const walk = async (directory, prefix = "") => {
    for (const entry of (await readdir(directory, { withFileTypes: true })).sort((a, b) => a.name.localeCompare(b.name))) {
      const relative = path.posix.join(prefix, entry.name);
      if (entry.isSymbolicLink() || (!entry.isDirectory() && !entry.isFile())) fail("partial-materialization", `Template 目标包含不支持的对象：${assetId}。`, { assetId, path: relative });
      if (entry.isDirectory()) await walk(path.join(directory, entry.name), relative); else existingFiles.push(relative);
    }
  };
  await walk(outputRoot);
  if (!(await exists(path.join(outputRoot, sidecarName)))) fail("partial-materialization", `检测到缺少 provenance sidecar 的 Template 目标，拒绝覆盖：${assetId}。`, { assetId });
  const actualSidecar = await readJson(path.join(outputRoot, sidecarName), "materialization-provenance-mismatch").catch(() => fail("materialization-provenance-mismatch", `Template provenance sidecar 无效：${assetId}。`, { assetId }));
  if (actualSidecar?.schemaVersion !== 1 || actualSidecar?.kind !== "ux-proto-template-provenance" || actualSidecar?.assetId !== assetId || !Array.isArray(actualSidecar.files) || new Set(actualSidecar.files.map((item) => item.path)).size !== actualSidecar.files.length) fail("materialization-provenance-mismatch", `Template provenance sidecar shape 无效：${assetId}。`, { assetId });
  const expectedFiles = [...actualSidecar.files.map((item) => item.path), sidecarName].sort();
  if (digestObject(existingFiles.sort()) !== digestObject(expectedFiles)) fail("partial-materialization", `检测到不完整或额外的 page-owned Template 集合，拒绝覆盖：${assetId}。`, { assetId, expectedFiles, existingFiles });
  for (const item of actualSidecar.files) {
    if (typeof item.path !== "string" || path.isAbsolute(item.path) || item.path.split(/[\\/]/).includes("..") || !/^[a-f0-9]{64}$/.test(item.sourceHash ?? "") || !["text", "binary"].includes(item.artifactType)) fail("materialization-provenance-mismatch", `Template provenance file entry 无效：${assetId}。`, { assetId });
    const destination = containedPath(outputRoot, item.path);
    const materialized = await readFile(destination);
    const marker = markerFor(assetId, item.path, item.sourceHash);
    if (item.artifactType === "text" ? !marker || !materialized.toString("utf8").startsWith(marker) : sha256(materialized) !== item.sourceHash) fail("materialization-provenance-mismatch", `已物化 Template provenance 不匹配：${destination}。`, { assetId, path: item.path });
  }
  return { ...contract, status: "verified" };
}

export async function materializeFromSnapshot({ snapshotRoot, projectRoot, assetId, checkOnly = false }) {
  assertCanonicalAssetId(assetId);
  const contract = await validateMaterializedTemplate({ snapshotRoot, projectRoot, assetId, allowMissing: true });
  const { pageAssetsRoot, outputRoot, targets, contents, sidecarName, sidecar, existingPageAssets } = contract;
  const contentHashes = Object.fromEntries(targets.map((item) => [item.relative.split(path.sep).join("/"), item.sha256]).sort(([a], [b]) => a.localeCompare(b)));
  const provenanceFiles = [path.relative(projectRoot, path.join(outputRoot, sidecarName)).split(path.sep).join("/")];
  const projection = templateConsumptionProjection(contract.record);
  const imports = projection.imports;
  const customizationSurfaces = contract.record.authoring.customizationSurfaces;
  if (contract.status === "verified") return { schemaVersion: 1, status: "already-materialized", assetId, contentHashes, written: [], provenanceFiles, imports, editPolicy: projection.editPolicy, customizationSurfaces };
  if (checkOnly) return { schemaVersion: 1, status: "missing", assetId, contentHashes, written: [], provenanceFiles, imports, editPolicy: projection.editPolicy, customizationSurfaces };
  let temporary = null;
  try {
    await mkdir(pageAssetsRoot, { recursive: true });
    const pageAssetsInfo = await lstat(pageAssetsRoot);
    const realProjectRoot = await realpath(path.resolve(projectRoot));
    if (pageAssetsInfo.isSymbolicLink() || !pageAssetsInfo.isDirectory() || !(await realpath(pageAssetsRoot)).startsWith(`${realProjectRoot}${path.sep}`)) fail("materialization-path-boundary", "page-assets escaped the workspace boundary.", { path: pageAssetsRoot });
    temporary = await mkdtemp(containedPath(pageAssetsRoot, `.${assetId}.tmp-${process.pid}-`));
    const realTemporary = await realpath(temporary);
    if (!realTemporary.startsWith(`${await realpath(pageAssetsRoot)}${path.sep}`)) fail("materialization-path-boundary", "Materialization temporary directory escaped page-assets.", { path: temporary });
    for (const item of contents) { const target = containedPath(temporary, item.relative); await mkdir(path.dirname(target), { recursive: true }); await writeFile(target, item.output); }
    await writeFile(containedPath(temporary, sidecarName), stableJson(sidecar));
    if (await exists(outputRoot)) fail("partial-materialization", `Template 目标已在物化期间出现，拒绝覆盖：${assetId}。`, { assetId });
    await rename(temporary, outputRoot);
    temporary = null;
  } catch (error) {
    if (temporary) await rm(temporary, { recursive: true, force: true });
    if (!existingPageAssets) await rmdir(pageAssetsRoot).catch(() => {});
    throw error;
  }
  return { schemaVersion: 1, status: "materialized", assetId, contentHashes, written: targets.map((item) => path.relative(projectRoot, item.destination).split(path.sep).join("/")).sort(), provenanceFiles, imports, editPolicy: projection.editPolicy, customizationSurfaces };
}

export async function protectedSnapshotImportPlugin(snapshotRoot) {
  const manifest = await requireUsableSnapshot(snapshotRoot);
  const imports = new Map(manifest.publicSurface.map((item) => [item.specifier, containedPath(snapshotRoot, item.entry)]));
  return { name: "ux-proto-snapshot-public-surface", setup(build) { build.onResolve({ filter: /^@ux-proto\/assets\// }, (args) => imports.has(args.path) ? { path: imports.get(args.path) } : { errors: [{ text: `Public asset import is outside the resolved snapshot: ${args.path}` }] }); } };
}

export async function snapshotExecutionRecords(snapshotRoot) {
  const manifest = await requireUsableSnapshot(snapshotRoot);
  return new Map(manifest.publicSurface.map((item) => [containedPath(snapshotRoot, item.entry), item.assetId]));
}
