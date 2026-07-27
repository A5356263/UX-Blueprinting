import { randomUUID } from "node:crypto";
import { lstat, mkdir, mkdtemp, readFile, readdir, readlink, rename, rm, rmdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { assertCanonicalAssetId, containedPath, digestObject, exists, fail, readJson, stableJson, UxProtoError } from "./common.mjs";
import { resolveSources } from "./source-resolver.mjs";
import { validateSnapshot, writeSnapshot } from "./snapshot.mjs";
import { authoringContextFromSnapshot, contextAuthoringFromSnapshot, contextReviewFromSnapshot, inspectFromSnapshot, materializeFromSnapshot } from "./workflow.mjs";
import { assessBuildCurrentness, buildWorkspace, collectMaterializedAssets, computeBuildArtifactDigest, computeBuildSourceDigest } from "./build-workspace.mjs";

const currentLayout = { schemaVersion: 1, id: "ux-proto-workspace", layoutVersion: "1.0" };
const coreVersion = JSON.parse(await readFile(new URL("./version.json", import.meta.url), "utf8")).version;

const commandHelp = {
  status: "status [--json]：只读汇总当前 workspace 状态与可用命令。",
  "workspace init": "workspace init [--json]：内部初始化固定 bundled Pack snapshot。",
  "workspace update": "workspace update [--json]：原子刷新固定 bundled Pack snapshot；不覆盖 page-owned 文件。",
  "context authoring": "context authoring [--json]：只读返回完整 baseline。",
  "context review": "context review [--json]：只读返回 Pack 声明的 review Knowledge。",
  inspect: "inspect --asset <asset-id> [--json]：按 exact ID 返回规范化资产合同。",
  materialize: "materialize --asset <template-id> [--json]：从当前 snapshot 物化 page-owned Template。",
  "materialization repair": "materialization repair --asset <template-id> [--json]：显式隔离当前 snapshot 中损坏的固定 Template target。",
  build: "build [--json]：构建 runtime/static preview 并写入确定性 build report。"
};
const commandNames = Object.keys(commandHelp);
const arg = (args, name, required = false) => {
  const index = args.indexOf(name);
  if (index === -1) { if (required) fail("missing-argument", `缺少必要参数 ${name}。`, { argument: name }); return null; }
  if (!args[index + 1] || args[index + 1].startsWith("--")) fail("missing-argument-value", `${name} 缺少参数值。`, { argument: name });
  return args[index + 1];
};
const envelope = (command, ok, data, error) => ({ schemaVersion: 1, command, ok, ...(ok ? { data } : { error }) });
const publicCommand = (command) => `npm run ux-proto -- ${command} --json`;

export function projectBuildEvidence(report, { proof = ".ux-proto/build-report.json", proofWriteFailure = null } = {}) {
  return {
    completionStatus: report.completionStatus,
    runtimePreview: report.runtimePreview,
    staticPreview: report.staticPreview,
    executionSafety: report.executionSafety,
    snapshotDigest: report.snapshotDigest,
    sourceDigest: report.sourceDigest,
    materializedAssets: report.materializedAssets ?? [],
    observedReusableAssets: report.observedReusableAssets ?? [],
    warnings: report.warnings ?? [],
    proof,
    ...(proofWriteFailure ? { proofWriteFailure } : {})
  };
}

function textList(items, render) {
  return items.length ? items.map((item) => `- ${render(item)}`).join("\n") : "[]";
}

export function formatBuildOutput(data, { headline = "成功：build" } = {}) {
  const observed = textList(data.observedReusableAssets ?? [], (item) => {
    const provenance = item.provenance ? ` (${item.provenance})` : "";
    return `${item.id}${provenance}`;
  });
  const warnings = textList(data.warnings ?? [], (item) => item.assetId ? `${item.category}: ${item.assetId}` : item.category);
  const output = [
    headline,
    `completionStatus: ${data.completionStatus}`,
    `runtimePreview: ${data.runtimePreview}`,
    `staticPreview: ${data.staticPreview}`,
    `executionSafety: ${data.executionSafety}`,
    `snapshotDigest: ${data.snapshotDigest}`,
    `sourceDigest: ${data.sourceDigest}`,
    "materializedAssets:",
    textList(data.materializedAssets ?? [], (item) => item),
    "observedReusableAssets:",
    observed,
    "warnings:",
    warnings,
    `proof: ${data.proof ?? "unavailable"}`
  ];
  if (data.proofWriteFailure) output.push(`proofWriteFailure: ${data.proofWriteFailure.category}: ${data.proofWriteFailure.message}`);
  return output.join("\n") + "\n";
}

const managedInternalDisclosure = /(?:^|[\\/])(?:runtime[\\/](?:core|packs)|assets[\\/](?:core|packs))(?:[\\/]|$)/i;
const containsManagedInternalDisclosure = (value) => typeof value === "string"
  ? managedInternalDisclosure.test(value)
  : Array.isArray(value)
    ? value.some(containsManagedInternalDisclosure)
    : Boolean(value && typeof value === "object" && Object.entries(value).some(([key, item]) => containsManagedInternalDisclosure(key) || containsManagedInternalDisclosure(item)));

function normalizePublicError(error) {
  if (error instanceof UxProtoError) return error;
  if (/Forbidden AntD subpath|forbidden AntD subpath/i.test(String(error?.message ?? ""))) {
    return new UxProtoError("unsupported-antd-subpath", "AntD value/type imports must use the antd package root.", { recovery: "Replace antd/* imports with root imports from antd before building again.", nextActions: [{ kind: "edit-source", rule: "antd-root-only" }] });
  }
  return new UxProtoError("internal-error", "UX Proto could not complete the public command.", {});
}

function projectPublicFailure(error) {
  const normalized = normalizePublicError(error);
  const failure = { category: normalized.category, message: normalized.message, context: normalized.context };
  if (!containsManagedInternalDisclosure(failure)) return { normalized, failure };
  return {
    normalized,
    failure: {
      category: normalized.category,
      message: "Managed UX Proto Core/Pack data is invalid or unavailable.",
      context: {}
    }
  };
}

function paths(workspaceRoot) {
  const state = path.join(workspaceRoot, ".ux-proto");
  return {
    state,
    snapshot: path.join(state, "resolved-assets"),
    report: path.join(state, "build-report.json"),
    layout: path.join(state, "layout.json"),
    packs: path.join(workspaceRoot, "runtime", "packs")
  };
}

async function bundledPackAt(locations) {
  const entries = (await readdir(locations.packs, { withFileTypes: true })).filter((entry) => entry.isDirectory() && !entry.isSymbolicLink());
  if (entries.length !== 1) fail("bundled-pack-slot-invalid", "runtime 必须包含且只包含一个固定 bundled Pack。", { count: entries.length });
  return path.join(locations.packs, entries[0].name);
}

async function requireCurrentSnapshot(locations) {
  const snapshot = await validateSnapshot(locations.snapshot);
  if (!snapshot.valid) fail(snapshot.error?.category ?? "snapshot-unusable", snapshot.error?.message ?? "resolved snapshot 不可用。", { state: snapshot.state });
  return snapshot.manifest;
}

async function requireCurrentLayout(locations) {
  const layout = await readJson(locations.layout, "unknown-workspace-layout");
  if (layout?.schemaVersion !== 1 || layout?.id !== "ux-proto-workspace" || layout?.layoutVersion !== "1.0" || Object.keys(layout).length !== 3) fail("unknown-workspace-layout", "当前命令只支持 UX Proto 1.0 current workspace layout；请创建 fresh workspace。", { expected: currentLayout, actual: layout });
  return layout;
}

async function runtimeFor(workspaceRoot) {
  const module = await import(pathToFileURL(path.join(workspaceRoot, "scripts/runtime.mjs")));
  return module.loadSkillRuntime({ workspaceRoot });
}

async function resolutionFor(workspaceRoot, locations) {
  const [bundledPack, runtime] = await Promise.all([bundledPackAt(locations), runtimeFor(workspaceRoot)]);
  return resolveSources({ bundledPack, esbuild: runtime.esbuild });
}

async function initWorkspace(workspaceRoot, locations) {
  await mkdir(locations.state, { recursive: true });
  const resolution = await resolutionFor(workspaceRoot, locations);
  const manifest = await writeSnapshot({ resolution, destination: locations.snapshot, generatorVersion: coreVersion });
  return { initialized: true, ...await authoringContextFromSnapshot(locations.snapshot), snapshotDigest: manifest.contentDigest, pageOwnedFilesChanged: [] };
}

export function packChanges(previous, current) {
  if (!previous || previous.contentDigest === current.contentDigest) return { added: [], removed: [], guidanceChanged: [], implementationChanged: [], templateSourceChanged: [] };
  const before = new Map(previous.records.map((record) => [record.id, record]));
  const after = new Map(current.records.map((record) => [record.id, record]));
  const added = [...after.keys()].filter((id) => !before.has(id)).sort();
  const removed = [...before.keys()].filter((id) => !after.has(id)).sort();
  const guidanceChanged = [];
  const implementationChanged = [];
  const templateSourceChanged = [];
  for (const [id, record] of after) {
    const prior = before.get(id);
    if (!prior) continue;
    if (prior.guidanceDigest !== record.guidanceDigest) guidanceChanged.push(id);
    if (record.kind === "Template" && prior.templateSourceDigest !== record.templateSourceDigest) templateSourceChanged.push(id);
    if (record.kind === "Pack Component" && prior.componentContractDigest !== record.componentContractDigest) implementationChanged.push(id);
  }
  if (previous.baseline.id !== current.baseline.id || previous.baseline.digest !== current.baseline.digest) {
    for (const id of new Set([previous.baseline.id, current.baseline.id])) guidanceChanged.push(`baseline:${id}`);
  }
  const beforeRecommendations = new Map(previous.recommendations.map((item) => [item.id, item]));
  const afterRecommendations = new Map(current.recommendations.map((item) => [item.id, item]));
  for (const id of new Set([...beforeRecommendations.keys(), ...afterRecommendations.keys()])) {
    if (digestObject(beforeRecommendations.get(id) ?? null) !== digestObject(afterRecommendations.get(id) ?? null)) guidanceChanged.push(`recommendation:${id}`);
  }
  const beforeReview = new Set(previous.review.assets);
  const afterReview = new Set(current.review.assets);
  for (const id of new Set([...beforeReview, ...afterReview])) if (beforeReview.has(id) !== afterReview.has(id)) guidanceChanged.push(`review:${id}`);
  const beforeTheme = new Map(previous.runtimeTheme.artifacts.map((item) => [item.name, item.sha256]));
  const afterTheme = new Map(current.runtimeTheme.artifacts.map((item) => [item.name, item.sha256]));
  for (const name of new Set([...beforeTheme.keys(), ...afterTheme.keys()])) if (beforeTheme.get(name) !== afterTheme.get(name)) implementationChanged.push(`runtime-theme:${name}`);
  const result = {
    added,
    removed,
    guidanceChanged: [...new Set(guidanceChanged)].sort(),
    implementationChanged: [...new Set(implementationChanged)].sort(),
    templateSourceChanged: [...new Set(templateSourceChanged)].sort()
  };
  if (![...Object.values(result)].some((items) => items.length)) result.guidanceChanged.push(`pack:${current.pack.id}`);
  return result;
}

async function updateWorkspace(workspaceRoot, locations) {
  await requireCurrentLayout(locations);
  const previous = (await validateSnapshot(locations.snapshot)).manifest ?? null;
  const resolution = await resolutionFor(workspaceRoot, locations);
  const manifest = await writeSnapshot({ resolution, destination: locations.snapshot, generatorVersion: coreVersion });
  return { initialized: true, ...await authoringContextFromSnapshot(locations.snapshot), packChanges: packChanges(previous, manifest), snapshotDigest: manifest.contentDigest, pageOwnedFilesChanged: [], updated: true, status: "applied" };
}

async function status(workspaceRoot, locations) {
  const [snapshot, report] = await Promise.all([
    validateSnapshot(locations.snapshot), (await exists(locations.report)) ? readJson(locations.report) : null
  ]);
  let runtime = { status: "ready" };
  try { await runtimeFor(workspaceRoot); }
  catch (error) { runtime = { status: "invalid", error: { category: error.category ?? "runtime-unavailable", message: error.message } }; }
  const allowed = snapshot.valid ? ["status", "workspace update", "inspect", "context authoring", "context review", "materialize", "materialization repair", "build"] : ["workspace init", "status"];
  const availableCommands = allowed.map((name) => ({ command: name, required: ["inspect", "materialize", "materialization repair"].includes(name) ? ["--asset"] : [] }));
  let build = { status: "absent" };
  if (report) {
    const [currentSource, currentArtifacts] = await Promise.all([
      computeBuildSourceDigest(workspaceRoot).catch(() => ({ sourceDigest: null })),
      computeBuildArtifactDigest(workspaceRoot).catch(() => ({ artifactDigest: null, complete: false }))
    ]);
    const currentness = assessBuildCurrentness({ report, currentSource, currentArtifacts });
    build = { status: currentness.completionStatus, fresh: currentness.fresh, completionStatus: currentness.completionStatus, proof: ".ux-proto/build-report.json", ...(report.warnings?.length ? { warnings: report.warnings } : {}) };
  }
  const guidance = authorGuidance({ snapshot, runtime });
  return {
    core: { version: coreVersion, schemaVersion: 1 },
    pack: snapshot.manifest?.pack ?? null,
    runtime,
    snapshot: { state: snapshot.state, valid: snapshot.valid, contentDigest: snapshot.manifest?.contentDigest ?? null, proof: ".ux-proto/resolved-assets/manifest.json" },
    build,
    availableCommands,
    ...guidance
  };
}

function authorGuidance({ snapshot, runtime = { status: "ready" } }) {
  const blockingReasons = [];
  const nextActions = [];
  if (runtime.status !== "ready") {
    blockingReasons.push({ category: runtime.error?.category ?? "runtime-unavailable" });
  } else if (!snapshot.valid) {
    const category = snapshot.error?.category ?? "snapshot-unavailable";
    blockingReasons.push({ category });
    nextActions.push({ kind: "workspace-update", command: publicCommand("workspace update") });
  }
  return { readyToAuthor: blockingReasons.length === 0, blockingReasons, nextActions };
}

async function assertRealDirectory(file, category) {
  const info = await lstat(file);
  if (info.isSymbolicLink() || !info.isDirectory()) fail(category, "Materialization recovery path must be a real directory without a symlink boundary.", { path: file });
  return info;
}

async function recoveryObjectProof(root, relative = "") {
  const absolute = path.join(root, relative);
  const info = await lstat(absolute);
  const normalized = relative.split(path.sep).join("/");
  if (info.isSymbolicLink()) return [{ path: normalized, type: "symlink", target: await readlink(absolute) }];
  if (info.isFile()) return [{ path: normalized, type: "file", bytes: info.size, sha256: digestObject((await readFile(absolute)).toString("base64")) }];
  if (!info.isDirectory()) return [{ path: normalized, type: "other", mode: info.mode, size: info.size }];
  const proof = [{ path: normalized, type: "directory" }];
  for (const entry of (await readdir(absolute)).sort()) proof.push(...await recoveryObjectProof(root, path.join(relative, entry)));
  return proof;
}

export async function repairMaterialization({ workspaceRoot, locations = paths(path.resolve(workspaceRoot)), assetId, beforeRename = null, recoveryIdFactory = randomUUID }) {
  assertCanonicalAssetId(assetId);
  const record = await inspectFromSnapshot(locations.snapshot, assetId);
  if (record.kind !== "Template") fail("materialization-repair-invalid-asset", "Materialization repair only accepts a Template from the current snapshot.", { assetId });
  const projectRoot = path.resolve(workspaceRoot);
  const pageAssets = containedPath(projectRoot, "page-assets");
  await assertRealDirectory(projectRoot, "materialization-repair-boundary");
  await assertRealDirectory(locations.state, "materialization-repair-boundary");
  await assertRealDirectory(pageAssets, "materialization-repair-boundary");
  const target = containedPath(pageAssets, assetId);
  let targetInfo;
  try { targetInfo = await lstat(target); }
  catch (error) { if (error?.code === "ENOENT") fail("materialization-repair-target-missing", `Template target is missing; use ordinary materialize: ${assetId}.`, { assetId }); throw error; }
  const targetProof = await recoveryObjectProof(target);

  const recovery = containedPath(locations.state, "recovery");
  const materializations = containedPath(recovery, "materializations");
  const assetRecovery = containedPath(materializations, assetId);
  const createdParents = [];
  const ensureRecoveryDirectory = async (directory) => {
    try { await assertRealDirectory(directory, "materialization-repair-boundary"); }
    catch (error) {
      if (error?.code !== "ENOENT") throw error;
      await mkdir(directory);
      createdParents.push(directory);
    }
  };
  let recoveryRoot = null;
  try {
    await ensureRecoveryDirectory(recovery);
    await ensureRecoveryDirectory(materializations);
    await ensureRecoveryDirectory(assetRecovery);
    const recoveryId = recoveryIdFactory();
    if (!/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(recoveryId)) fail("materialization-repair-id-invalid", "Generated materialization recovery ID is invalid.", {});
    const candidateRecoveryRoot = containedPath(assetRecovery, recoveryId);
    await mkdir(candidateRecoveryRoot);
    recoveryRoot = candidateRecoveryRoot;
    const original = path.join(recoveryRoot, "original");
    await writeFile(path.join(recoveryRoot, "recovery.json"), stableJson({ schemaVersion: 1, kind: "ux-proto-materialization-recovery", assetId, originalPath: `page-assets/${assetId}`, recoveredPath: `.ux-proto/recovery/materializations/${assetId}/${recoveryId}/original` }));
    if (beforeRename) await beforeRename({ target, recoveryRoot, original });
    const currentInfo = await lstat(target);
    const currentProof = await recoveryObjectProof(target);
    if (currentInfo.dev !== targetInfo.dev || currentInfo.ino !== targetInfo.ino || currentInfo.mode !== targetInfo.mode || digestObject(currentProof) !== digestObject(targetProof)) fail("materialization-repair-target-changed", "Template target changed during repair; no object was quarantined.", { assetId });
    await rename(target, original);
    const objectType = targetInfo.isSymbolicLink() ? "symlink" : targetInfo.isDirectory() ? "directory" : targetInfo.isFile() ? "file" : "other";
    return { schemaVersion: 1, status: "quarantined", recoverable: true, assetId, objectType, originalPath: `page-assets/${assetId}`, recoveredPath: `.ux-proto/recovery/materializations/${assetId}/${recoveryId}/original` };
  } catch (error) {
    if (recoveryRoot) await rm(recoveryRoot, { recursive: true, force: true }).catch(() => {});
    for (const directory of createdParents.reverse()) await rmdir(directory).catch(() => {});
    throw error;
  }
}

async function dispatch(command, args, workspaceRoot, locations) {
  if (command === "status") return status(workspaceRoot, locations);
  if (command === "workspace init") return initWorkspace(workspaceRoot, locations);
  if (command === "workspace update") return updateWorkspace(workspaceRoot, locations);
  if (["inspect", "context authoring", "context review", "materialize", "materialization repair", "build"].includes(command)) await requireCurrentSnapshot(locations);
  if (command === "inspect") return inspectFromSnapshot(locations.snapshot, arg(args, "--asset", true));
  if (command === "context authoring") return contextAuthoringFromSnapshot(locations.snapshot);
  if (command === "context review") return contextReviewFromSnapshot(locations.snapshot);
  if (command === "materialize") {
    const materialization = await materializeFromSnapshot({ snapshotRoot: locations.snapshot, projectRoot: workspaceRoot, assetId: arg(args, "--asset", true) });
    return { status: materialization.status, assetId: materialization.assetId, target: `page-assets/${materialization.assetId}`, imports: materialization.imports, editPolicy: "page-owned", customizationSurfaces: materialization.customizationSurfaces, proof: materialization.provenanceFiles[0], readyToAuthor: true, nextActions: [] };
  }
  if (command === "materialization repair") {
    if (args.length !== 2 || args[0] !== "--asset") fail("invalid-arguments", "materialization repair only accepts --asset <current-template-id>.", { allowed: ["--asset"] });
    const repaired = await repairMaterialization({ workspaceRoot, locations, assetId: arg(args, "--asset", true) });
    return { ...repaired, readyToAuthor: true, nextActions: [{ kind: "materialize", assetId: repaired.assetId, command: publicCommand(`materialize --asset ${repaired.assetId}`) }] };
  }
  if (command === "build") {
    const runtime = await runtimeFor(workspaceRoot);
    const [antd, runtimeHelpers, staticPreview] = await Promise.all([
      import(pathToFileURL(path.join(workspaceRoot, "scripts/antd-boundary.mjs"))),
      import(pathToFileURL(path.join(workspaceRoot, "scripts/runtime.mjs"))),
      import(pathToFileURL(path.join(workspaceRoot, "scripts/build-static-preview.mjs")))
    ]);
    const result = await buildWorkspace({ workspaceRoot, runtime, snapshotRoot: locations.snapshot, helpers: { ...antd, ...runtimeHelpers, ...staticPreview } });
    return { ...projectBuildEvidence(result.report), nextActions: result.error ? result.error.context?.nextActions ?? [] : [], ...(result.error ? { error: result.error } : {}) };
  }
  fail("unknown-command", `未知命令：${command || "（空）"}。`, { availableCommands: commandNames });
}

export async function runCli({ argv = process.argv.slice(2), workspaceRoot = process.cwd(), stdout = process.stdout, stderr = process.stderr } = {}) {
  const jsonMode = argv.includes("--json");
  const args = argv.filter((item) => item !== "--json");
  const nested = new Set(["workspace", "context", "materialization"]);
  const command = nested.has(args[0]) ? `${args[0]} ${args[1] ?? ""}`.trim() : args[0] ?? "";
  const commandArgs = nested.has(args[0]) ? args.slice(2) : args.slice(1);
  if (args.includes("--help") || args[0] === "help") {
    const help = commandHelp[command] ?? `UX Proto 公共命令：\n${commandNames.map((name) => `  ${commandHelp[name]}`).join("\n")}`;
    const result = envelope(command || "help", true, { help });
    stdout.write(jsonMode ? stableJson(result) : `${help}\n`);
    return 0;
  }
  try {
    const data = await dispatch(command, commandArgs, path.resolve(workspaceRoot), paths(path.resolve(workspaceRoot)));
    const degraded = command === "build" && data.completionStatus === "degraded";
    const result = degraded ? { schemaVersion: 1, command, ok: false, completionStatus: "degraded", data, error: data.error } : { ...envelope(command, true, data), ...(command === "build" ? { completionStatus: "normal" } : {}) };
    stdout.write(jsonMode ? stableJson(result) : command === "build" ? formatBuildOutput(data) : `成功：${command}\n`);
    return degraded ? 2 : 0;
  } catch (error) {
    const projected = projectPublicFailure(error);
    const normalized = projected.normalized;
    if (command === "materialize" && ["partial-materialization", "materialization-provenance-mismatch"].includes(normalized.category)) {
      const assetId = arg(commandArgs, "--asset", false);
      normalized.context = { ...normalized.context, recovery: "Quarantine the invalid governed target, then materialize it again from the current snapshot.", nextActions: [{ kind: "repair-materialization", assetId, command: publicCommand(`materialization repair --asset ${assetId}`) }] };
    }
    const failure = containsManagedInternalDisclosure({ message: normalized.message, context: normalized.context })
      ? projected.failure
      : { category: normalized.category, message: normalized.message, context: normalized.context };
    let failedBuildEvidence = null;
    if (command === "build") {
      const workspace = path.resolve(workspaceRoot); const locations = paths(workspace);
      const source = await computeBuildSourceDigest(workspace).catch(() => ({ sourceDigest: null }));
      const snapshot = await validateSnapshot(locations.snapshot).catch(() => ({ manifest: null }));
      const materializedAssets = await collectMaterializedAssets({ workspaceRoot: workspace, snapshotRoot: locations.snapshot }).catch(() => []);
      const report = {
        schemaVersion: 1,
        completionStatus: "failed",
        runtimePreview: "unavailable",
        staticPreview: "unavailable",
        executionSafety: "unverified",
        snapshotDigest: snapshot.manifest?.contentDigest ?? null,
        sourceDigest: source.sourceDigest,
        materializedAssets,
        observedReusableAssets: [],
        warnings: [],
        error: failure
      };
      let proof = null;
      let proofWriteFailure = null;
      try {
        await mkdir(locations.state, { recursive: true });
        await writeFile(locations.report, stableJson(report));
        proof = ".ux-proto/build-report.json";
      } catch {
        proofWriteFailure = {
          category: "build-report-write-failed",
          message: "Build proof could not be written."
        };
      }
      failedBuildEvidence = projectBuildEvidence(report, { proof, proofWriteFailure });
    }
    const result = command === "build"
      ? { schemaVersion: 1, command, ok: false, completionStatus: "failed", data: failedBuildEvidence, error: failure }
      : envelope(command, false, null, failure);
    if (jsonMode) stdout.write(stableJson(result));
    else if (command === "build") stderr.write(`${formatBuildOutput(failedBuildEvidence, { headline: "失败：build" })}error: ${failure.message}\n`);
    else stderr.write(`${failure.message}\n`);
    return 1;
  }
}
