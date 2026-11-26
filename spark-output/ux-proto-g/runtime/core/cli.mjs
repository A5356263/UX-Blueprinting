import { randomUUID } from "node:crypto";
import { lstat, mkdir, mkdtemp, readFile, readdir, readlink, rename, rm, rmdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { assertCanonicalAssetId, containedPath, digestObject, exists, fail, readJson, stableJson, UxProtoError } from "./common.mjs";
import { resolveSources } from "./source-resolver.mjs";
import { validateSnapshot, writeSnapshot } from "./snapshot.mjs";
import { authoringContextFromSnapshot, catalogFromSnapshot, contextAuthoringFromSnapshot, contextReviewFromSnapshot, expandFromSnapshot, inspectFromSnapshot, materializeFromSnapshot } from "./workflow.mjs";
import { assessBuildCurrentness, buildWorkspace, collectMaterializedAssets, computeBuildArtifactDigest, computeBuildSourceDigest } from "./build-workspace.mjs";
import { parseMaterializationSelection, serializeMaterializationFailure, serializeMaterializationResult, serializeMaterializationSuccess, validateMaterializationRequest } from "./materialization-contract.mjs";

const currentLayout = { schemaVersion: 1, id: "ux-proto-workspace", layoutVersion: "1.0" };
const coreVersion = JSON.parse(await readFile(new URL("./version.json", import.meta.url), "utf8")).version;

const commandHelp = {
  status: "status [--json]：只读汇总当前 workspace 状态与可用命令。",
  "workspace init": "workspace init [--allow-packless] [--json]：初始化一个已安装 Pack；无 Pack 时需显式一次性确认 packless。",
  "workspace update": "workspace update [--json]：从 Skill instance 的唯一已安装 Pack 原子刷新 resolved-assets；不覆盖 page-owned 文件。",
  catalog: "catalog --json：只读返回当前 Pack 全部资产摘要。",
  expand: "expand --asset <asset-id> [--asset <asset-id> ...] --json：按请求顺序批量展开当前 Pack 资产。",
  "context authoring": "context authoring --json：只读重放当前 entrypoints Packet。",
  "context review": "context review --json：只读返回当前 review Packet。",
  materialize: "materialize --asset <template-id> [--selection <json>] [--reselect] [--json]：配置 Template 先返回只读配置单，再以完整选择物化。",
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
const successEnvelope = (command, data) => ({ schemaVersion: 2, command, status: "success", data });
const partialEnvelope = (command, data, failures) => ({ schemaVersion: 2, command, status: "partial", data, failures });
const failedEnvelope = (command, error, failures = null) => ({ schemaVersion: 2, command, status: "failed", error, ...(failures?.length ? { failures } : {}) });
const publicCommand = (command) => `npm run ux-proto -- ${command} --json`;

function requireNoArguments(command, args) {
  if (args.length) fail("invalid-arguments", `${command} does not accept arguments.`, { command, arguments: args });
}

function repeatedAssetArguments(args) {
  const assetIds = [];
  for (let index = 0; index < args.length; index += 2) {
    if (args[index] !== "--asset") fail("invalid-arguments", "expand only accepts repeated --asset <asset-id> arguments.", { allowed: ["--asset"] });
    const value = args[index + 1];
    if (!value || value.startsWith("--")) fail("missing-argument-value", "--asset requires an asset ID.", { argument: "--asset" });
    assetIds.push(value);
  }
  return assetIds;
}

export function projectBuildEvidence(report, { proof = ".ux-proto/build-report.json", proofWriteFailure = null } = {}) {
  return {
    completionStatus: report.completionStatus,
    runtimePreview: report.runtimePreview,
    staticPreview: report.staticPreview,
    executionSafety: report.executionSafety,
    snapshotDigest: report.snapshotDigest,
    ...(report.uiConfig ? { uiConfig: report.uiConfig } : {}),
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

const managedInternalDisclosure = /(?:^|[\\/])(?:\.ux-proto|runtime[\\/](?:core|packs)|assets[\\/](?:core|packs))(?:[\\/]|$)/i;
const containsManagedInternalDisclosure = (value) => typeof value === "string"
  ? managedInternalDisclosure.test(value)
  : Array.isArray(value)
    ? value.some(containsManagedInternalDisclosure)
    : Boolean(value && typeof value === "object" && Object.entries(value).some(([key, item]) => containsManagedInternalDisclosure(key) || containsManagedInternalDisclosure(item)));

function normalizePublicError(error) {
  if (error instanceof UxProtoError) return error;
  if (typeof error?.category === "string" && typeof error?.message === "string") return new UxProtoError(error.category, error.message, error.context && typeof error.context === "object" ? error.context : {});
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
    installation: path.join(state, "installation.json")
  };
}

async function installedPackAt(locations) {
  const locator = await readJson(locations.installation, "installation-locator-invalid");
  if (locator?.schemaVersion !== 1 || locator?.kind !== "ux-proto-skill-installation" || !path.isAbsolute(locator.root ?? "") || Object.keys(locator).sort().join(",") !== "kind,root,schemaVersion") fail("installation-locator-invalid", "Skill installation locator is invalid.", {});
  const root = path.join(locator.root, "assets", "packs");
  const entries = await readdir(root, { withFileTypes: true }).catch((error) => error?.code === "ENOENT" ? [] : Promise.reject(error));
  if (entries.some((entry) => entry.isSymbolicLink() || !entry.isDirectory())) fail("installed-pack-slot-invalid", "Installed Pack slot may contain only one real Pack directory.", { count: entries.length });
  if (entries.length > 1) fail("installed-pack-slot-invalid", "Installed Pack slot may contain at most one Pack.", { count: entries.length });
  return entries.length ? path.join(root, entries[0].name) : null;
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
  const [installedPack, runtime] = await Promise.all([installedPackAt(locations), runtimeFor(workspaceRoot)]);
  if (!installedPack) fail("installed-pack-missing", "No Pack is installed. Place one complete promoted Pack at assets/packs/<packId>, then run workspace update; or confirm one-time packless init with --allow-packless.", {});
  return resolveSources({ bundledPack: installedPack, esbuild: runtime.esbuild });
}

async function installResolvedTheme(workspaceRoot, resolution) {
  const destination = path.join(workspaceRoot, "theme");
  const temporary = await mkdtemp(path.join(workspaceRoot, ".ux-proto-theme-"));
  try {
    for (const artifact of resolution.runtimeTheme.artifacts) await writeFile(path.join(temporary, artifact.name), artifact.contents);
    await writeFile(path.join(temporary, "runtime-theme-receipt.json"), stableJson({ schemaVersion: 1, kind: "ux-proto-runtime-theme-receipt", source: "pack", pack: { id: resolution.pack.id, version: resolution.pack.version }, artifacts: resolution.runtimeTheme.artifacts.map(({ name, sha256 }) => ({ name, sha256 })) }));
    const backup = `${destination}.previous-${process.pid}`;
    if (await exists(destination)) await rename(destination, backup);
    try { await rename(temporary, destination); }
    catch (error) { if (await exists(backup)) await rename(backup, destination); throw error; }
    await rm(backup, { recursive: true, force: true });
  } catch (error) {
    await rm(temporary, { recursive: true, force: true });
    throw error;
  }
}

async function initWorkspace(workspaceRoot, locations, { allowPackless = false } = {}) {
  await mkdir(locations.state, { recursive: true });
  const pack = await installedPackAt(locations);
  if (!pack) {
    if (!allowPackless) fail("installed-pack-missing", "No Pack is installed. Re-run with --allow-packless only after the user explicitly confirms minimal React/AntD mode.", { nextActions: [{ kind: "confirm-packless", command: publicCommand("workspace init --allow-packless") }] });
    await rm(locations.snapshot, { recursive: true, force: true });
    return { mode: "packless", readyToAuthor: true, fullAssets: 0, linkedAbstracts: 0, availableCapabilities: ["react", "antd", "runtime", "preview", "build"] };
  }
  const resolution = await resolutionFor(workspaceRoot, locations);
  await writeSnapshot({ resolution, destination: locations.snapshot, generatorVersion: coreVersion });
  await installResolvedTheme(workspaceRoot, resolution);
  return authoringContextFromSnapshot(locations.snapshot);
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
  if (digestObject(previous.entrypoints) !== digestObject(current.entrypoints)) guidanceChanged.push("entrypoints");
  if (digestObject(previous.review) !== digestObject(current.review)) guidanceChanged.push("review");
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
  const previousStatus = await validateSnapshot(locations.snapshot);
  const previous = previousStatus.valid ? previousStatus.manifest : null;
  const resolution = await resolutionFor(workspaceRoot, locations);
  const manifest = await writeSnapshot({ resolution, destination: locations.snapshot, generatorVersion: coreVersion });
  await installResolvedTheme(workspaceRoot, resolution);
  return { ...await authoringContextFromSnapshot(locations.snapshot), packChanges: packChanges(previous, manifest), updated: true };
}

async function status(workspaceRoot, locations) {
  const [snapshot, report] = await Promise.all([
    validateSnapshot(locations.snapshot), (await exists(locations.report)) ? readJson(locations.report) : null
  ]);
  let runtime = { status: "ready" };
  try { await runtimeFor(workspaceRoot); }
  catch (error) { runtime = { status: "invalid", error: { category: error.category ?? "runtime-unavailable", message: error.message } }; }
  const installedPack = await installedPackAt(locations);
  const allowed = snapshot.valid
    ? ["status", "workspace update", "catalog", "expand", "context authoring", "context review", "materialize", "materialization repair", "build"]
    : installedPack
      ? ["workspace update", "status"]
      : ["workspace init", "workspace update", "status", "build"];
  const availableCommands = allowed.map((name) => ({ command: name, required: ["expand", "materialize", "materialization repair"].includes(name) ? ["--asset"] : [] }));
  let build = { status: "absent" };
  if (report) {
    const [currentSource, currentArtifacts] = await Promise.all([
      computeBuildSourceDigest(workspaceRoot).catch(() => ({ sourceDigest: null })),
      computeBuildArtifactDigest(workspaceRoot).catch(() => ({ artifactDigest: null, complete: false }))
    ]);
    const currentness = assessBuildCurrentness({ report, currentSource, currentArtifacts });
    build = { status: currentness.completionStatus, fresh: currentness.fresh, completionStatus: currentness.completionStatus, proof: ".ux-proto/build-report.json", ...(report.warnings?.length ? { warnings: report.warnings } : {}) };
  }
  const guidance = authorGuidance({ snapshot, runtime, packless: !snapshot.valid && !installedPack });
  return {
    core: { version: coreVersion, schemaVersion: 1 },
    pack: snapshot.manifest?.pack ?? null,
    mode: snapshot.valid ? "pack-enabled" : installedPack ? "update-required" : "packless",
    installedPackPresent: Boolean(installedPack),
    runtime,
    snapshot: { state: snapshot.state, valid: snapshot.valid, contentDigest: snapshot.manifest?.contentDigest ?? null, proof: ".ux-proto/resolved-assets/manifest.json" },
    build,
    availableCommands,
    ...guidance
  };
}

function authorGuidance({ snapshot, runtime = { status: "ready" }, packless = false }) {
  const blockingReasons = [];
  const nextActions = [];
  if (runtime.status !== "ready") {
    blockingReasons.push({ category: runtime.error?.category ?? "runtime-unavailable" });
  } else if (!snapshot.valid && !packless) {
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
  if (command === "status") { requireNoArguments(command, args); return status(workspaceRoot, locations); }
  if (command === "workspace init") {
    if (args.length > 1 || (args.length === 1 && args[0] !== "--allow-packless")) fail("invalid-arguments", "workspace init only accepts --allow-packless.", { allowed: ["--allow-packless"] });
    return initWorkspace(workspaceRoot, locations, { allowPackless: args.includes("--allow-packless") });
  }
  if (command === "workspace update") { requireNoArguments(command, args); return updateWorkspace(workspaceRoot, locations); }
  if (["catalog", "expand", "context authoring", "context review", "materialize", "materialization repair"].includes(command)) await requireCurrentSnapshot(locations);
  if (command === "catalog") { requireNoArguments(command, args); return catalogFromSnapshot(locations.snapshot); }
  if (command === "expand") return expandFromSnapshot(locations.snapshot, repeatedAssetArguments(args));
  if (command === "context authoring") { requireNoArguments(command, args); return contextAuthoringFromSnapshot(locations.snapshot); }
  if (command === "context review") { requireNoArguments(command, args); return contextReviewFromSnapshot(locations.snapshot); }
  if (command === "materialize") {
    const allowed = new Set(["--asset", "--selection", "--reselect"]);
    for (let index = 0; index < args.length; index += 1) {
      if (!allowed.has(args[index])) fail("invalid-arguments", "materialize only accepts --asset, --selection and --reselect.", { allowed: [...allowed] });
      if (args[index] === "--reselect") continue;
      if (!args[index + 1] || args[index + 1].startsWith("--")) fail("missing-argument-value", `${args[index]} requires a value.`, { argument: args[index] });
      index += 1;
    }
    if (!arg(args, "--asset", true)) fail("missing-argument", "materialize requires --asset.", {});
    let selection = null;
    if (arg(args, "--selection")) selection = parseMaterializationSelection(arg(args, "--selection"));
    const request = validateMaterializationRequest({ assetId: arg(args, "--asset", true), selection, reselect: args.includes("--reselect") });
    return serializeMaterializationResult(await materializeFromSnapshot({ snapshotRoot: locations.snapshot, projectRoot: workspaceRoot, ...request }));
  }
  if (command === "materialization repair") {
    if (args.length !== 2 || args[0] !== "--asset") fail("invalid-arguments", "materialization repair only accepts --asset <current-template-id>.", { allowed: ["--asset"] });
    const repaired = await repairMaterialization({ workspaceRoot, locations, assetId: arg(args, "--asset", true) });
    return { ...repaired, readyToAuthor: true, nextActions: [{ kind: "materialize", assetId: repaired.assetId, command: publicCommand(`materialize --asset ${repaired.assetId}`) }] };
  }
  if (command === "build") {
    requireNoArguments(command, args);
    const installedPack = await installedPackAt(locations);
    const snapshot = await validateSnapshot(locations.snapshot);
    if (installedPack && !snapshot.valid) {
      fail("installed-pack-update-required", "An installed Pack is present, but resolved-assets is missing or invalid. Run workspace update before building.", {
        snapshotState: snapshot.state,
        nextActions: [{ kind: "workspace-update", command: publicCommand("workspace update") }]
      });
    }
    const runtime = await runtimeFor(workspaceRoot);
    const [antd, runtimeHelpers, staticPreview] = await Promise.all([
      import(pathToFileURL(path.join(workspaceRoot, "scripts/antd-boundary.mjs"))),
      import(pathToFileURL(path.join(workspaceRoot, "scripts/runtime.mjs"))),
      import(pathToFileURL(path.join(workspaceRoot, "scripts/build-static-preview.mjs")))
    ]);
    const result = await buildWorkspace({ workspaceRoot, runtime, snapshotRoot: snapshot.valid ? locations.snapshot : null, helpers: { ...antd, ...runtimeHelpers, ...staticPreview } });
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
  try {
    if (argv.filter((item) => item === "--json").length > 1) fail("invalid-arguments", "--json may be provided only once.", { argument: "--json" });
    const rootHelp = args.length === 1 && ["help", "--help"].includes(args[0]);
    const commandHelpRequested = commandNames.includes(command) && commandArgs.length === 1 && commandArgs[0] === "--help";
    if (rootHelp || commandHelpRequested) {
      const help = commandHelpRequested
        ? commandHelp[command]
        : `UX Proto 公共命令：\n${commandNames.map((name) => `  ${commandHelp[name]}`).join("\n")}`;
      const result = successEnvelope(commandHelpRequested ? command : "help", { help });
      stdout.write(jsonMode ? stableJson(result) : `${help}\n`);
      return 0;
    }
    if (args.includes("--help") || args[0] === "help") fail("invalid-arguments", "--help must be used alone or as the only argument to a known command.", { argument: "--help" });
    if (["catalog", "expand", "context authoring", "context review"].includes(command) && !jsonMode) fail("json-required", `${command} requires --json.`, { command });
    const data = await dispatch(command, commandArgs, path.resolve(workspaceRoot), paths(path.resolve(workspaceRoot)));
    let result;
    if (command === "expand") {
      const { status, failures, ...packet } = data;
      result = status === "partial" ? partialEnvelope(command, packet, failures) : successEnvelope(command, packet);
    } else if (command === "build" && data.completionStatus === "degraded") {
      const { error, ...buildData } = data;
      const failure = projectPublicFailure(error).failure;
      result = partialEnvelope(command, buildData, [failure]);
    } else result = command === "materialize" ? serializeMaterializationSuccess(data) : successEnvelope(command, data);
    stdout.write(jsonMode ? stableJson(result) : command === "build" ? formatBuildOutput(data) : `成功：${command}\n`);
    return 0;
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
    if (command === "materialize") {
      const result = serializeMaterializationFailure(failure);
      stdout.write(jsonMode ? stableJson(result) : `失败：${failure.category}: ${failure.message}\n`);
      return 1;
    }
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
    const requestFailures = command === "expand" && Array.isArray(failure.context?.failures) ? failure.context.failures : null;
    const publicFailure = requestFailures
      ? { ...failure, context: Object.fromEntries(Object.entries(failure.context).filter(([key]) => key !== "failures")) }
      : command === "build"
        ? { ...failure, context: { ...failure.context, buildEvidence: failedBuildEvidence } }
        : failure;
    const result = failedEnvelope(command, publicFailure, requestFailures);
    if (jsonMode) stdout.write(stableJson(result));
    else if (command === "build") stderr.write(`${formatBuildOutput(failedBuildEvidence, { headline: "失败：build" })}error: ${failure.message}\n`);
    else stderr.write(`${failure.message}\n`);
    return 1;
  }
}
