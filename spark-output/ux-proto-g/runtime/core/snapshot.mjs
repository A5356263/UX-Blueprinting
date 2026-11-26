import { mkdir, readFile, readdir, rename, rm, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { assertCanonicalAssetId, containedPath, digestObject, exists, fail, posixPath, readJson, sha256, stableJson } from "./common.mjs";

async function walk(directory, prefix = "") {
  const result = [];
  for (const entry of (await readdir(directory, { withFileTypes: true })).sort((a, b) => a.name.localeCompare(b.name))) {
    const relative = posixPath(path.join(prefix, entry.name));
    if (entry.isSymbolicLink()) fail("snapshot-symlink", `snapshot 不允许符号链接：${relative}。`, { path: relative });
    if (entry.isDirectory()) result.push(...await walk(path.join(directory, entry.name), relative));
    else if (entry.isFile()) result.push(relative);
    else fail("invalid-snapshot-object", `snapshot 包含不支持的对象：${relative}。`, { path: relative });
  }
  return result;
}

async function payloadDigests(root) {
  const files = (await walk(root)).filter((file) => file !== "manifest.json");
  return Object.fromEntries(await Promise.all(files.map(async (file) => [file, sha256(await readFile(path.join(root, file)))])));
}

function recordForSnapshot(record) {
  assertCanonicalAssetId(record.id);
  return {
    id: record.id,
    kind: record.kind,
    title: record.title,
    abstract: record.abstract,
    ...(record.content ? { content: record.content } : {}),
    ...(record.authoring ? { authoring: record.authoring } : {}),
    ...(record.configuration ? { configuration: record.configuration } : {}),
    ...(record.publicApi ? { publicApi: record.publicApi } : {}),
    ...(record.api ? { api: record.api } : {}),
    ...(record.usage ? { usage: record.usage } : {}),
    ...(record.entry ? { entry: record.entry } : {}),
    ...(record.artifacts ? { artifacts: record.artifacts } : {}),
    assetLinks: record.assetLinks ?? [],
    recordDigest: record.recordDigest,
    identityDigest: record.identityDigest,
    semanticDigest: record.semanticDigest,
    implementationDigest: record.implementationDigest,
    guidanceDigest: record.guidanceDigest,
    ...(record.templateSourceDigest ? { templateSourceDigest: record.templateSourceDigest } : {}),
    ...(record.configuratorFiles?.length ? { configuratorFiles: record.configuratorFiles.map(({ snapshotPath, sha256: digest }) => ({ path: snapshotPath, sha256: digest })) } : {}),
    ...(record.componentContractDigest ? { componentContractDigest: record.componentContractDigest } : {}),
    files: record.files.map(({ snapshotPath, sha256: digest }) => ({ path: snapshotPath, sha256: digest }))
  };
}

function publicSurface(records) {
  return records.filter((record) => record.kind === "Pack Component").map((record) => {
    const specifier = `@ux-proto/assets/${record.id}`;
    const mainExport = record.api.mainExport;
    return {
      specifier,
      assetId: record.id,
      entry: record.files.find((file) => file.sourcePath.endsWith(record.entry))?.snapshotPath ?? `files/${record.id}/${record.entry}`,
      mainExport,
      exports: record.publicExports,
      importStatement: `import { ${mainExport} } from "${specifier}";`
    };
  }).sort((a, b) => a.specifier.localeCompare(b.specifier));
}

function assetCatalog(records) {
  return records.map((record) => ({
    id: record.id,
    kind: record.kind,
    title: record.title,
    abstract: record.abstract
  })).sort((a, b) => a.kind.localeCompare(b.kind) || a.id.localeCompare(b.id));
}

function unsignedManifest(manifest) {
  return Object.fromEntries(Object.entries(manifest).filter(([key]) => key !== "contentDigest"));
}

function assertContainedRelative(relative, label) {
  if (typeof relative !== "string" || !relative || path.isAbsolute(relative) || relative.split(/[\\/]/).includes("..") || relative.includes("\\")) fail("invalid-snapshot-reference", `snapshot ${label} 路径无效：${relative}。`, { path: relative, label });
}

export async function writeSnapshot({ resolution, destination, generatorVersion }) {
  const target = path.resolve(destination);
  const parent = path.dirname(target);
  const stage = path.join(parent, `.${path.basename(target)}.tmp-${process.pid}`);
  const backup = path.join(parent, `.${path.basename(target)}.backup-${process.pid}`);
  await rm(stage, { recursive: true, force: true });
  await rm(backup, { recursive: true, force: true });
  await mkdir(stage, { recursive: true });
  try {
    const records = resolution.records.map(recordForSnapshot);
    for (const record of resolution.records) {
      await mkdir(path.join(stage, "records"), { recursive: true });
      await writeFile(path.join(stage, "records", `${record.id}.json`), stableJson(recordForSnapshot(record)));
      for (const file of record.files) {
        const output = path.join(stage, file.snapshotPath);
        await mkdir(path.dirname(output), { recursive: true });
        await writeFile(output, file.contents);
      }
      for (const file of record.configuratorFiles ?? []) {
        const output = path.join(stage, file.snapshotPath);
        await mkdir(path.dirname(output), { recursive: true });
        await writeFile(output, file.contents);
      }
    }
    const surface = publicSurface(resolution.records);
    await mkdir(path.join(stage, "public"), { recursive: true });
    await writeFile(path.join(stage, "public/import-map.json"), stableJson({ schemaVersion: 2, imports: surface }));
    await writeFile(path.join(stage, "resolver-report.json"), stableJson(resolution.report));
    if (resolution.uiConfig) {
      const output = path.join(stage, resolution.uiConfig.stylesheet);
      await mkdir(path.dirname(output), { recursive: true });
      await writeFile(output, resolution.uiConfig.contents);
    }
    const files = await payloadDigests(stage);
    const payload = {
      schemaVersion: resolution.uiConfig ? 4 : 3,
      kind: "ux-proto-resolved-assets",
      generatorVersion,
      pack: resolution.pack,
      entrypoints: resolution.entrypoints,
      review: resolution.review,
      manifestBindingRecords: resolution.manifestBindingRecords,
      runtimeTheme: {
        artifacts: resolution.runtimeTheme.artifacts.map(({ path: artifactPath, name, sha256: digest }) => ({ path: artifactPath, name, sha256: digest }))
      },
      ...(resolution.uiConfig ? { uiConfig: { stylesheet: resolution.uiConfig.stylesheet, antdVersion: resolution.uiConfig.antdVersion, sha256: resolution.uiConfig.sha256 } } : {}),
      scope: { roots: resolution.roots, closure: resolution.closure, draftTrials: resolution.draftTrials },
      projection: resolution.projection,
      records,
      catalog: assetCatalog(resolution.records),
      publicSurface: surface,
      files
    };
    const manifest = { ...payload, contentDigest: digestObject(payload) };
    await writeFile(path.join(stage, "manifest.json"), stableJson(manifest));
    const validation = await validateSnapshot(stage);
    if (!validation.valid) throw validation.error;
    if (await exists(target)) await rename(target, backup);
    try { await rename(stage, target); }
    catch (error) { if (await exists(backup)) await rename(backup, target); throw error; }
    await rm(backup, { recursive: true, force: true });
    return manifest;
  } catch (error) {
    await rm(stage, { recursive: true, force: true });
    throw error;
  }
}

export async function validateSnapshot(directory) {
  const root = path.resolve(directory);
  const manifestFile = path.join(root, "manifest.json");
  if (!(await exists(manifestFile))) return { state: "absent", valid: false };
  let manifest;
  try { manifest = await readJson(manifestFile, "invalid-snapshot"); }
  catch (error) { return { state: "invalid", valid: false, error }; }
  try {
    if (![2, 3, 4].includes(manifest.schemaVersion) || manifest.kind !== "ux-proto-resolved-assets") fail("invalid-snapshot-schema", "snapshot schema 或 kind 无效。", { root });
    if (manifest.schemaVersion < 4 && Object.hasOwn(manifest, "uiConfig")) fail("invalid-snapshot-schema", "旧 snapshot 不允许 uiConfig。", { root });
    if (manifest.schemaVersion === 4 && !manifest.uiConfig) fail("invalid-snapshot-schema", "snapshot schema 4 必须包含 uiConfig。", { root });
    for (const field of ["records", "catalog", "entrypoints", "review", "publicSurface"]) if (!Array.isArray(manifest[field])) fail("invalid-snapshot-schema", `snapshot.${field} 必须是数组。`, { field });
    if (!manifest.pack || !manifest.manifestBindingRecords || !Array.isArray(manifest.manifestBindingRecords.entrypoints) || !Array.isArray(manifest.manifestBindingRecords.review) || !manifest.runtimeTheme || !Array.isArray(manifest.runtimeTheme.artifacts) || !manifest.scope || !Array.isArray(manifest.scope.roots) || !Array.isArray(manifest.scope.closure) || !manifest.files || Array.isArray(manifest.files)) fail("invalid-snapshot-schema", "snapshot Pack/context/theme/scope/files shape 无效。", { root });
    const actualFiles = await payloadDigests(root);
    if (digestObject(unsignedManifest(manifest)) !== manifest.contentDigest) fail("snapshot-digest-mismatch", "snapshot canonical manifest digest 无效，可能被手工修改。", { root });
    if (digestObject(actualFiles) !== digestObject(manifest.files)) fail("snapshot-file-mismatch", "snapshot 文件集合或摘要无效。", { root });
    for (const file of Object.keys(manifest.files)) assertContainedRelative(file, "files");
    if (manifest.uiConfig) {
      const { stylesheet, antdVersion, sha256: digest } = manifest.uiConfig;
      assertContainedRelative(stylesheet, "uiConfig.stylesheet");
      if (!stylesheet.endsWith(".css") || !/^\d+\.\d+\.\d+$/.test(antdVersion ?? "") || manifest.files[stylesheet] !== digest) fail("invalid-snapshot-reference", "snapshot uiConfig 引用无效。", { stylesheet });
    }
    const records = new Map();
    for (const record of manifest.records) {
      assertCanonicalAssetId(record.id);
      if (records.has(record.id)) fail("invalid-snapshot-reference", `snapshot record identity 重复：${record.id}。`, { assetId: record.id });
      const recordPath = `records/${record.id}.json`;
      const diskRecord = await readJson(containedPath(root, recordPath), "invalid-snapshot-record");
      if (digestObject(diskRecord) !== digestObject(record) || !(recordPath in manifest.files)) fail("snapshot-record-mismatch", `snapshot manifest/record 不一致：${record.id}。`, { assetId: record.id });
      for (const file of record.files ?? []) {
        assertContainedRelative(file.path, `${record.id}.files`);
        if (manifest.files[file.path] !== file.sha256) fail("invalid-snapshot-reference", `snapshot record 文件引用无效：${record.id}/${file.path}。`, { assetId: record.id, path: file.path });
      }
      for (const file of record.configuratorFiles ?? []) {
        assertContainedRelative(file.path, `${record.id}.configuratorFiles`);
        if (manifest.files[file.path] !== file.sha256) fail("invalid-snapshot-reference", `snapshot configurator 文件引用无效：${record.id}/${file.path}。`, { assetId: record.id, path: file.path });
      }
      if (!Array.isArray(record.assetLinks)) fail("invalid-snapshot-schema", `snapshot record assetLinks 无效：${record.id}。`, { assetId: record.id });
      records.set(record.id, record);
    }
    if (manifest.scope.closure.length !== records.size || manifest.scope.closure.some((id) => !records.has(id))) fail("invalid-snapshot-reference", "snapshot closure 与 records 不一致。", {});
    if (digestObject(manifest.catalog) !== digestObject(assetCatalog([...records.values()]))) fail("invalid-snapshot-reference", "snapshot Catalog 不是完整稳定的资产摘要集合。", {});
    const validateStageBindings = (bindings, stage, kinds) => {
      const seen = new Set();
      for (const [index, item] of bindings.entries()) {
        const record = records.get(item?.assetLink);
        if (!item || typeof item.assetLink !== "string" || !record || !kinds.includes(record.kind) || (Object.hasOwn(item, "load") && item.load !== "full") || typeof item.pointer !== "string" || seen.has(item.assetLink)) fail("invalid-snapshot-reference", `snapshot ${stage} binding 无效。`, { assetId: item?.assetLink ?? null, requestIndex: index });
        seen.add(item.assetLink);
      }
    };
    validateStageBindings(manifest.entrypoints, "entrypoints", ["Pattern"]);
    validateStageBindings(manifest.review, "review", ["Pattern", "Knowledge"]);
    if (digestObject(manifest.entrypoints.map((item) => item.assetLink)) !== digestObject(manifest.scope.roots)) fail("invalid-snapshot-reference", "snapshot entrypoints roots 顺序无效。", {});
    for (const record of records.values()) for (const link of record.assetLinks) if (!records.has(link.target)) fail("invalid-snapshot-reference", `snapshot assetLink 缺少当前 Pack 目标：${link.target}。`, { assetId: record.id, pointer: link.pointer, targetAssetId: link.target });
    const componentIds = [...records.values()].filter((record) => record.kind === "Pack Component").map((record) => record.id).sort();
    if (digestObject(manifest.publicSurface.map((item) => item.assetId).sort()) !== digestObject(componentIds)) fail("invalid-snapshot-reference", "snapshot public surface 不是 Pack Component 精确集合。", {});
    for (const item of manifest.publicSurface) {
      const record = records.get(item.assetId);
      if (!record || record.kind !== "Pack Component" || item.specifier !== `@ux-proto/assets/${item.assetId}` || !record.files.some((file) => file.path === item.entry)) fail("invalid-snapshot-reference", `snapshot public surface 无效：${item.assetId}。`, { assetId: item.assetId });
      if (!(await stat(path.join(root, item.entry)).catch(() => null))?.isFile()) fail("snapshot-public-entry-missing", `snapshot public entry 缺失：${item.entry}。`, { assetId: item.assetId });
    }
    return { state: "usable", valid: true, manifest };
  } catch (error) {
    return { state: "invalid", valid: false, manifest, error };
  }
}

export async function requireUsableSnapshot(directory) {
  const status = await validateSnapshot(directory);
  if (!status.valid) fail(status.error?.category ?? "snapshot-unusable", status.error?.message ?? "resolved snapshot 不可用。", { state: status.state });
  return status.manifest;
}
