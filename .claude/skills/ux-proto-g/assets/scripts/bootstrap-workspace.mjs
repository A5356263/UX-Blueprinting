import { createHash } from "node:crypto";
import { execFile as execFileCallback } from "node:child_process";
import { constants } from "node:fs";
import { copyFile, cp, lstat, mkdir, mkdtemp, readFile, readdir, readlink, realpath, rename, rm, rmdir, stat, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { promisify } from "node:util";
import { installRuntimeTheme } from "./install-runtime-theme.mjs";
import { runCli } from "../core/cli.mjs";
import { authoringContextFromSnapshot } from "../core/workflow.mjs";

const execFile = promisify(execFileCallback);
const here = path.dirname(fileURLToPath(import.meta.url));
const assetsRoot = path.resolve(here, "..");
const templateRoot = path.join(assetsRoot, "workspace-template");
const sha256 = (value) => createHash("sha256").update(value).digest("hex");
const stableObject = (value) => Array.isArray(value) ? value.map(stableObject) : value && typeof value === "object" ? Object.fromEntries(Object.keys(value).sort().map((key) => [key, stableObject(value[key])])) : value;
const stableJson = (value) => `${JSON.stringify(stableObject(value), null, 2)}\n`;
export const currentLayout = { schemaVersion: 1, id: "ux-proto-workspace", layoutVersion: "1.0" };

const exists = (file) => stat(file).then(() => true, (error) => error?.code === "ENOENT" ? false : Promise.reject(error));
async function assertCurrentLayout(workspace) {
  let value;
  try { value = JSON.parse(await readFile(path.join(workspace, ".ux-proto/layout.json"), "utf8")); }
  catch (error) { throw new Error(`Workspace is not the current UX Proto 1.0 layout (${error.code ?? "invalid-marker"}); create a fresh workspace.`); }
  if (value?.schemaVersion !== 1 || value?.id !== "ux-proto-workspace" || value?.layoutVersion !== "1.0" || Object.keys(value).length !== 3) throw new Error("Workspace is not the current UX Proto 1.0 layout; create a fresh workspace instead of migrating.");
  return value;
}

async function targetState(workspace, mode, preservedEntries) {
  if (!(await exists(workspace))) return "empty";
  const info = await lstat(workspace);
  if (info.isSymbolicLink() || !info.isDirectory()) throw new Error("Bootstrap output must be a real directory path.");
  const entries = await readdir(workspace);
  if (!entries.length) return "empty";
  if (mode === "open-design" && entries.every((entry) => preservedEntries.includes(entry))) {
    for (const entry of entries) {
      const info = await lstat(path.join(workspace, entry));
      if (info.isSymbolicLink() || !info.isDirectory()) throw new Error(`${entry} must be a real preserved host directory.`);
    }
    return "empty";
  }
  try { await assertCurrentLayout(workspace); return "current"; }
  catch { throw new Error(`Refusing bootstrap into non-empty ${mode} target before any write or dependency installation.`); }
}

async function objectProof(root, relative) {
  const absolute = path.join(root, relative);
  const info = await lstat(absolute);
  const normalized = relative.split(path.sep).join("/");
  if (info.isSymbolicLink()) return [{ path: normalized, type: "symlink", target: await readlink(absolute) }];
  if (info.isFile()) return [{ path: normalized, type: "file", bytes: info.size, sha256: sha256(await readFile(absolute)) }];
  if (!info.isDirectory()) return [{ path: normalized, type: "other", mode: info.mode }];
  const proof = [{ path: normalized, type: "directory" }];
  for (const entry of (await readdir(absolute)).sort()) proof.push(...await objectProof(root, path.join(relative, entry)));
  return proof;
}

async function freshTargetProof(workspace, preservedEntries) {
  try {
    const info = await lstat(workspace);
    if (info.isSymbolicLink() || !info.isDirectory()) throw new Error("Bootstrap output must remain a real directory path.");
  } catch (error) {
    if (error?.code === "ENOENT") return { exists: false, entries: [], preserved: [] };
    throw error;
  }
  const entries = (await readdir(workspace)).sort();
  if (!entries.every((entry) => preservedEntries.includes(entry))) throw new Error("Fresh Open Design target changed after initial validation; refusing governed publish.");
  const preserved = [];
  for (const entry of entries) preserved.push(...await objectProof(workspace, entry));
  return { exists: true, entries, preserved };
}

async function assertFreshTargetUnchanged(workspace, initialProof, applied = []) {
  const entries = (await readdir(workspace)).sort();
  const expectedEntries = [...initialProof.entries, ...applied.map((item) => path.basename(item.destination))].sort();
  if (stableJson(entries) !== stableJson(expectedEntries)) throw new Error("Fresh Open Design target gained a foreign governed destination after initial validation; refusing governed publish.");
  const preserved = [];
  for (const entry of initialProof.entries) preserved.push(...await objectProof(workspace, entry));
  if (stableJson(preserved) !== stableJson(initialProof.preserved)) throw new Error("Preserved Open Design host state changed after initial validation; refusing governed publish.");
  for (const item of applied) {
    const current = await lstat(item.destination);
    if (current.dev !== item.dev || current.ino !== item.ino || current.mode !== item.mode) throw new Error("A transaction-owned governed destination changed during fresh publish.");
  }
}

async function validateRuntimeRoot(runtimeRoot, manifest, lockText) {
  try {
    if (!runtimeRoot) throw new Error("The host did not provide a runtime.");
    const root = await realpath(path.resolve(runtimeRoot));
    const receipt = JSON.parse(await readFile(path.join(root, "runtime-receipt.json"), "utf8"));
    const lockHash = sha256(lockText);
    if (receipt.schemaVersion !== 1 || receipt.status !== "ready" || receipt.skillVersion !== manifest.skillVersion || receipt.runtimeLockHash !== lockHash) throw new Error(`The runtime receipt does not match UX Proto ${manifest.skillVersion}.`);
    if (stableJson(receipt.versions) !== stableJson(manifest.dependencies)) throw new Error(`The runtime receipt dependency versions do not match UX Proto ${manifest.skillVersion}.`);
    const runtimeRequire = createRequire(path.join(root, "package.json"));
    for (const [name, version] of Object.entries(manifest.dependencies)) if (runtimeRequire(`${name}/package.json`).version !== version) throw new Error(`A required runtime dependency does not match UX Proto ${manifest.skillVersion}.`);
    return { root, receipt, lockHash };
  } catch (cause) {
    const error = new Error(`The Open Design namespace runtime is unavailable or does not match UX Proto ${manifest.skillVersion}.`, { cause });
    error.category = "host-runtime-unavailable";
    error.recovery = "Ask the Skill installer or namespace administrator to reinstall and verify the runtime from the installed ux-proto distribution README, then retry the public bootstrap command.";
    throw error;
  }
}

async function installGenericRuntime(stage, manifest, lockText) {
  await writeFile(path.join(stage, "package-lock.json"), lockText);
  await execFile("npm", ["ci", "--no-audit", "--no-fund"], { cwd: stage, maxBuffer: 20 * 1024 * 1024, shell: true });
  const localRequire = createRequire(path.join(stage, "package.json"));
  for (const [name, version] of Object.entries(manifest.dependencies)) if (localRequire(`${name}/package.json`).version !== version) throw new Error(`Local runtime dependency mismatch: ${name}@${version}.`);
  const receipt = { schemaVersion: 1, status: "ready", mode: "workspace-local", skillVersion: manifest.skillVersion, runtimeLockHash: sha256(lockText), versions: manifest.dependencies };
  await writeFile(path.join(stage, ".ux-proto/runtime-receipt.json"), stableJson(receipt));
  return receipt;
}

async function publishGenericRuntime({ workspace, manifest, lockText, failureAfter = null }) {
  const transaction = await mkdtemp(path.join(path.dirname(workspace), ".ux-proto-runtime-recovery-"));
  const stage = path.join(transaction, "stage");
  const backups = path.join(transaction, "backups");
  const replacements = ["package-lock.json", "node_modules", ".ux-proto/runtime-receipt.json"];
  const applied = [];
  try {
    await mkdir(path.join(stage, ".ux-proto"), { recursive: true });
    await cp(path.join(workspace, "package.json"), path.join(stage, "package.json"));
    if (await exists(path.join(workspace, ".npmrc"))) await cp(path.join(workspace, ".npmrc"), path.join(stage, ".npmrc"));
    await installGenericRuntime(stage, manifest, lockText);
    await mkdir(backups);
    for (const [index, relative] of replacements.entries()) {
      const source = path.join(stage, relative);
      const destination = path.join(workspace, relative);
      const backup = path.join(backups, String(index));
      await mkdir(path.dirname(destination), { recursive: true });
      if (await exists(destination)) await rename(destination, backup);
      try {
        await rename(source, destination);
        applied.push({ destination, backup });
      } catch (error) {
        if (await exists(backup)) await rename(backup, destination);
        throw error;
      }
      if (failureAfter === applied.length) throw new Error(`Injected runtime recovery publish failure after ${failureAfter} replacements.`);
    }
    return {
      async commit() { await rm(transaction, { recursive: true, force: true }).catch(() => {}); },
      async rollback() {
        for (const { destination, backup } of applied.reverse()) {
          await rm(destination, { recursive: true, force: true });
          if (await exists(backup)) await rename(backup, destination);
        }
        await rm(transaction, { recursive: true, force: true });
      }
    };
  } catch (error) {
    for (const { destination, backup } of applied.reverse()) {
      await rm(destination, { recursive: true, force: true });
      if (await exists(backup)) await rename(backup, destination);
    }
    await rm(transaction, { recursive: true, force: true });
    throw error;
  }
}

async function canonicalRuntimeContract(workspace) {
  const canonicalManifestPath = path.join(assetsRoot, "runtime/runtime-dependencies.json");
  const canonicalLockPath = path.join(assetsRoot, "runtime/runtime-lock.json");
  const workspaceManifestPath = path.join(workspace, "runtime/runtime-dependencies.json");
  const workspaceLockPath = path.join(workspace, "runtime/runtime-lock.json");
  const [canonicalManifest, canonicalLock, workspaceManifest, workspaceLock, manifestInfo, lockInfo] = await Promise.all([
    readFile(canonicalManifestPath),
    readFile(canonicalLockPath),
    readFile(workspaceManifestPath),
    readFile(workspaceLockPath),
    lstat(workspaceManifestPath),
    lstat(workspaceLockPath)
  ]);
  if (!manifestInfo.isFile() || manifestInfo.isSymbolicLink() || !lockInfo.isFile() || lockInfo.isSymbolicLink() || !workspaceManifest.equals(canonicalManifest) || !workspaceLock.equals(canonicalLock)) {
    throw new Error(`Current workspace runtime metadata does not byte-match this UX Proto ${JSON.parse(canonicalManifest).skillVersion} distribution.`);
  }
  return { manifest: JSON.parse(canonicalManifest.toString("utf8")), lockText: canonicalLock.toString("utf8") };
}

async function stageWorkspace({ stage, mode, runtimeRoot, stageFailure = false, firstStatusFailure = false }) {
  const [runtimeManifest, lockText] = await Promise.all([
    readFile(path.join(assetsRoot, "runtime/runtime-dependencies.json"), "utf8").then(JSON.parse),
    readFile(path.join(assetsRoot, "runtime/runtime-lock.json"), "utf8")
  ]);
  await mkdir(stage, { recursive: true });
  for (const file of ["index.html", "page.tsx", "styles.css", "package.json", "README.md", "AGENTS.md", ".gitignore", ".npmrc"]) await cp(path.join(templateRoot, file), path.join(stage, file));
  await cp(path.join(templateRoot, "scripts"), path.join(stage, "scripts"), { recursive: true });
  await cp(path.join(assetsRoot, "runtime"), path.join(stage, "runtime"), { recursive: true });
  await cp(path.join(assetsRoot, "core"), path.join(stage, "runtime/core"), { recursive: true });
  await cp(path.join(assetsRoot, "packs"), path.join(stage, "runtime/packs"), { recursive: true });
  await writeFile(path.join(stage, "package-lock.json"), lockText);
  await installRuntimeTheme({ packsRoot: path.join(assetsRoot, "packs"), outputDir: path.join(stage, "theme") });
  await mkdir(path.join(stage, ".ux-proto"), { recursive: true });
  await writeFile(path.join(stage, ".ux-proto/layout.json"), stableJson(currentLayout));
  if (stageFailure) throw new Error("Injected fresh staging failure.");
  if (mode === "generic") await installGenericRuntime(stage, runtimeManifest, lockText);
  else {
    const validated = await validateRuntimeRoot(runtimeRoot, runtimeManifest, lockText);
    await writeFile(path.join(stage, ".ux-proto/runtime-locator.json"), stableJson({ schemaVersion: 1, mode: "external", root: validated.root, skillVersion: runtimeManifest.skillVersion, runtimeLockHash: validated.lockHash }));
    await writeFile(path.join(stage, ".ux-proto/runtime-receipt.json"), stableJson({ schemaVersion: 1, status: "ready", mode: "external", skillVersion: runtimeManifest.skillVersion, runtimeLockHash: validated.lockHash, versions: runtimeManifest.dependencies }));
  }
  let initOutput = "";
  const initCode = await runCli({ argv: ["workspace", "init", "--json"], workspaceRoot: stage, stdout: { write(value) { initOutput += value; } }, stderr: { write() {} } });
  if (initCode !== 0 || JSON.parse(initOutput).ok !== true) throw new Error(`Bundled snapshot initialization failed: ${initOutput}`);
  if (firstStatusFailure) throw new Error("Injected first-ready validation failure.");
  let output = "";
  const code = await runCli({ argv: ["status", "--json"], workspaceRoot: stage, stdout: { write(value) { output += value; } }, stderr: { write() {} } });
  if (code !== 0 || JSON.parse(output).ok !== true) throw new Error(`First status validation failed: ${output}`);
  const status = JSON.parse(output);
  if (status.data?.readyToAuthor !== true) throw new Error(`First-ready validation did not produce readyToAuthor: ${output}`);
  const snapshotDigest = status.data?.snapshot?.contentDigest;
  await writeFile(path.join(stage, ".ux-proto/bootstrap-receipt.json"), stableJson({ schemaVersion: 1, status: "ready", mode, layoutVersion: "1.0", runtimeLockHash: sha256(lockText), snapshotDigest }));
  return { snapshotDigest, context: JSON.parse(initOutput).data };
}

async function copyFreshEntryNoClobber(source, destination) {
  const info = await lstat(source);
  if (info.isSymbolicLink() || (!info.isDirectory() && !info.isFile())) throw new Error("Fresh governed stage contains an unsupported object.");
  if (info.isFile()) {
    await copyFile(source, destination, constants.COPYFILE_EXCL);
    return lstat(destination);
  }
  await mkdir(destination);
  try { await cp(source, destination, { recursive: true, force: false, errorOnExist: true }); }
  catch (error) { await rm(destination, { recursive: true, force: true }); throw error; }
  return lstat(destination);
}

async function rollbackFreshOwned(applied) {
  for (const item of applied.reverse()) {
    const current = await lstat(item.destination).catch((error) => error?.code === "ENOENT" ? null : Promise.reject(error));
    if (current && current.dev === item.dev && current.ino === item.ino && current.mode === item.mode) await rm(item.destination, { recursive: true, force: true });
  }
}

async function publishFresh(stage, workspace, mode, failureAfter = null, initialProof = null, publishHook = null) {
  if (mode === "generic") {
    const backup = `${stage}-previous-target`;
    let replacedEmptyTarget = false;
    let published = false;
    try {
      if (publishHook) await publishHook({ phase: "before-first-publish", index: 0, workspace, entries: [path.basename(workspace)] });
      if (initialProof?.exists) {
        await assertFreshTargetUnchanged(workspace, initialProof, []);
        await rename(workspace, backup);
        replacedEmptyTarget = true;
        const movedProof = await freshTargetProof(backup, []);
        if (stableJson(movedProof) !== stableJson(initialProof)) throw new Error("Fresh Generic target changed during publish; refusing governed publish.");
      }
      await rename(stage, workspace);
      published = true;
      if (failureAfter === 1) throw new Error("Injected fresh publish failure after 1 governed workspace.");
      await rm(backup, { recursive: true, force: true });
      return;
    } catch (error) {
      if (published) await rm(workspace, { recursive: true, force: true });
      if (replacedEmptyTarget && await exists(backup)) await rename(backup, workspace);
      throw error;
    }
  }
  const applied = [];
  let workspaceOwned = false;
  let publishProof = initialProof;
  try {
    if (initialProof?.exists) await assertFreshTargetUnchanged(workspace, initialProof, applied);
    else {
      await mkdir(workspace);
      workspaceOwned = true;
      publishProof = { exists: true, entries: [], preserved: [] };
    }
    const entries = (await readdir(stage)).sort((a, b) => a === ".ux-proto" ? 1 : b === ".ux-proto" ? -1 : a.localeCompare(b));
    if (publishHook) await publishHook({ phase: "before-first-publish", index: 0, workspace, entries: [...entries] });
    for (const [index, entry] of entries.entries()) {
      if (index > 0 && publishHook) await publishHook({ phase: "between-publishes", index, workspace, entries: [...entries] });
      await assertFreshTargetUnchanged(workspace, publishProof, applied);
      const destination = path.join(workspace, entry);
      const owned = await copyFreshEntryNoClobber(path.join(stage, entry), destination);
      applied.push({ destination, dev: owned.dev, ino: owned.ino, mode: owned.mode });
      if (failureAfter === applied.length) throw new Error(`Injected fresh publish failure after ${failureAfter} governed entries.`);
    }
    await assertFreshTargetUnchanged(workspace, publishProof, applied);
  } catch (error) {
    await rollbackFreshOwned(applied);
    if (workspaceOwned) await rmdir(workspace).catch(() => {});
    throw error;
  }
}

async function recoverCurrent({ workspace, mode, runtimeRoot, recoveryFailureAfter }) {
  await assertCurrentLayout(workspace);
  const { manifest, lockText } = await canonicalRuntimeContract(workspace);
  let runtimeTransaction = null;
  if (mode === "generic") runtimeTransaction = await publishGenericRuntime({ workspace, manifest, lockText, failureAfter: recoveryFailureAfter });
  else {
    const validated = await validateRuntimeRoot(runtimeRoot, manifest, lockText);
    await writeFile(path.join(workspace, ".ux-proto/runtime-locator.json"), stableJson({ schemaVersion: 1, mode: "external", root: validated.root, skillVersion: manifest.skillVersion, runtimeLockHash: validated.lockHash }));
    await writeFile(path.join(workspace, ".ux-proto/runtime-receipt.json"), stableJson({ schemaVersion: 1, status: "ready", mode: "external", skillVersion: manifest.skillVersion, runtimeLockHash: validated.lockHash, versions: manifest.dependencies }));
  }
  try {
    let output = "";
    const code = await runCli({ argv: ["status", "--json"], workspaceRoot: workspace, stdout: { write(value) { output += value; } }, stderr: { write() {} } });
    if (code !== 0) throw new Error("Current workspace status failed after runtime recovery.");
    if (runtimeTransaction) await runtimeTransaction.commit();
    return { workspace, mode, recovered: true, ...await authoringContextFromSnapshot(path.join(workspace, ".ux-proto/resolved-assets")), firstStatus: JSON.parse(output) };
  } catch (error) {
    if (runtimeTransaction) await runtimeTransaction.rollback();
    throw error;
  }
}

async function updateRuntimeTransaction({ workspace, failureAfter = null }) {
  await assertCurrentLayout(workspace);
  const protectedPaths = ["page.tsx", "styles.css", "page-assets", ".ux-proto/layout.json", ".ux-proto/runtime-locator.json", ".ux-proto/runtime-receipt.json"];
  const transaction = await mkdtemp(path.join(path.dirname(workspace), ".ux-proto-runtime-update-"));
  const replacements = ["package.json", "package-lock.json", "README.md", "AGENTS.md", ".gitignore", ".npmrc", "scripts", "runtime", "theme"];
  const applied = [];
  try {
    for (const relative of replacements) {
      const destination = path.join(transaction, relative); await mkdir(path.dirname(destination), { recursive: true });
      if (relative === "runtime") { await cp(path.join(assetsRoot, "runtime"), destination, { recursive: true }); await cp(path.join(assetsRoot, "core"), path.join(destination, "core"), { recursive: true }); await cp(path.join(assetsRoot, "packs"), path.join(destination, "packs"), { recursive: true }); }
      else if (relative === "scripts") await cp(path.join(templateRoot, "scripts"), destination, { recursive: true });
      else if (relative === "theme") await installRuntimeTheme({ packsRoot: path.join(assetsRoot, "packs"), outputDir: destination });
      else if (relative === "package-lock.json") await cp(path.join(assetsRoot, "runtime/runtime-lock.json"), destination);
      else await cp(path.join(templateRoot, relative), destination);
    }
    for (const relative of replacements) if (protectedPaths.some((item) => relative === item || relative.startsWith(`${item}/`))) throw new Error(`Runtime update includes protected path ${relative}.`);
    const backups = path.join(transaction, ".backups"); await mkdir(backups);
    for (const [index, relative] of replacements.entries()) {
      const destination = path.join(workspace, relative); const backup = path.join(backups, String(index));
      if (await exists(destination)) await rename(destination, backup);
      try {
        await rename(path.join(transaction, relative), destination); applied.push({ destination, backup });
      } catch (error) {
        if (await exists(backup)) await rename(backup, destination);
        throw error;
      }
      if (failureAfter === applied.length) throw new Error(`Injected runtime update failure after ${failureAfter} replacements.`);
    }
    return { managedPathsUpdated: replacements.sort(), pageOwnedPathsUpdated: [] };
  } catch (error) {
    for (const item of applied.reverse()) { await rm(item.destination, { recursive: true, force: true }); if (await exists(item.backup)) await rename(item.backup, item.destination); }
    throw error;
  } finally { await rm(transaction, { recursive: true, force: true }); }
}

export async function bootstrapWorkspace({ output, mode = "generic", runtimeRoot = null, preservedEntries = [], updateRuntime = false, updateFailureAfter = null, recoveryFailureAfter = null, freshPublishFailureAfter = null, freshPublishHook = null, stageFailure = false, firstStatusFailure = false }) {
  const workspace = path.resolve(output);
  if (updateRuntime) return { workspace, updateRuntime: true, update: await updateRuntimeTransaction({ workspace, failureAfter: updateFailureAfter }) };
  if (!["generic", "open-design"].includes(mode)) throw new Error(`Unknown bootstrap mode ${mode}.`);
  const state = await targetState(workspace, mode, preservedEntries);
  if (state === "current") return recoverCurrent({ workspace, mode, runtimeRoot, recoveryFailureAfter });
  const initialFreshProof = await freshTargetProof(workspace, mode === "open-design" ? preservedEntries : []);
  const transaction = await mkdtemp(path.join(path.dirname(workspace), ".ux-proto-bootstrap-"));
  const stage = path.join(transaction, "workspace");
  try {
    const ready = await stageWorkspace({ stage, mode, runtimeRoot, stageFailure, firstStatusFailure });
    await publishFresh(stage, workspace, mode, freshPublishFailureAfter, initialFreshProof, freshPublishHook);
    return { workspace, mode, recovered: false, ...ready.context, nextActions: [] };
  } finally { await rm(transaction, { recursive: true, force: true }); }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) throw new Error("bootstrap-workspace.mjs is internal; use the public distribution launcher.");
