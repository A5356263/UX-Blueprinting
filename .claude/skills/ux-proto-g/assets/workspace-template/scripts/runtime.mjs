import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";

const sha256 = (value) => createHash("sha256").update(value).digest("hex");

async function runtimeContract(workspaceRoot) {
  const [manifestText, lockText] = await Promise.all([
    readFile(path.join(workspaceRoot, "runtime/runtime-dependencies.json"), "utf8"),
    readFile(path.join(workspaceRoot, "runtime/runtime-lock.json"), "utf8")
  ]);
  return { manifest: JSON.parse(manifestText), lockHash: sha256(lockText) };
}

async function runtimeLocation(workspaceRoot, contract) {
  const localRequire = createRequire(path.join(workspaceRoot, "package.json"));
  try {
    for (const [name, version] of Object.entries(contract.manifest.dependencies)) if (localRequire(`${name}/package.json`).version !== version) throw new Error(`${name} mismatch`);
    return { root: workspaceRoot, runtimeRequire: localRequire, mode: "workspace-local" };
  } catch {
    let locator;
    try { locator = JSON.parse(await readFile(path.join(workspaceRoot, ".ux-proto/runtime-locator.json"), "utf8")); }
    catch { throw new Error("No valid workspace-local runtime or explicit runtime locator is available."); }
    if (locator.schemaVersion !== 1 || locator.mode !== "external" || locator.skillVersion !== contract.manifest.skillVersion || locator.runtimeLockHash !== contract.lockHash || !path.isAbsolute(locator.root)) throw new Error("Explicit runtime locator does not match this workspace runtime contract.");
    const runtimeRequire = createRequire(path.join(locator.root, "package.json"));
    const receipt = JSON.parse(await readFile(path.join(locator.root, "runtime-receipt.json"), "utf8"));
    if (receipt.schemaVersion !== 1 || receipt.status !== "ready" || receipt.skillVersion !== contract.manifest.skillVersion || receipt.runtimeLockHash !== contract.lockHash) throw new Error("External runtime receipt does not match this workspace.");
    for (const [name, version] of Object.entries(contract.manifest.dependencies)) if (runtimeRequire(`${name}/package.json`).version !== version) throw new Error(`${name} must be ${version}.`);
    return { root: locator.root, runtimeRequire, mode: "external" };
  }
}

export async function loadSkillRuntime({ workspaceRoot = process.cwd() } = {}) {
  const workspace = path.resolve(workspaceRoot);
  try {
    const contract = await runtimeContract(workspace);
    const location = await runtimeLocation(workspace, contract);
    return { root: location.root, mode: location.mode, manifest: contract.manifest, require: location.runtimeRequire, esbuild: location.runtimeRequire("esbuild") };
  } catch (error) {
    throw new Error(`UX Proto runtime is unavailable or invalid (${error.message}). Re-run the public bootstrap launcher for this current workspace.`);
  }
}

export function reservedRuntimePlugin(runtime) {
  const names = runtime.manifest.reservedPackages.map((name) => name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const filter = new RegExp(`^(?:${names.join("|")})(?:/.*)?$`);
  return { name: "ux-proto-reserved-runtime", setup(build) { build.onResolve({ filter }, (args) => ({ path: runtime.require.resolve(args.path) })); } };
}
