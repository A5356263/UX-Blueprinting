import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";

const sha256 = (value) => createHash("sha256").update(value).digest("hex");

function runtimeRoot(workspaceRoot) {
  if (process.env.UX_PROTO_RUNTIME_ROOT) return path.resolve(process.env.UX_PROTO_RUNTIME_ROOT);
  const projectsRoot = path.dirname(workspaceRoot);
  if (path.basename(projectsRoot) === "projects") {
    return path.join(path.dirname(projectsRoot), "skill-runtimes", "ux-proto", "current");
  }
  throw new Error("UX Proto shared runtime is not discoverable. Run the Skill setup command, or set UX_PROTO_RUNTIME_ROOT for an isolated fixture.");
}

export async function loadSkillRuntime({ workspaceRoot = process.cwd() } = {}) {
  const root = runtimeRoot(path.resolve(workspaceRoot));
  try {
    const [manifestText, lockText, receiptText] = await Promise.all([
      readFile(path.join(workspaceRoot, "runtime/runtime-dependencies.json"), "utf8"),
      readFile(path.join(workspaceRoot, "runtime/runtime-lock.json"), "utf8"),
      readFile(path.join(root, "runtime-receipt.json"), "utf8")
    ]);
    const manifest = JSON.parse(manifestText);
    const receipt = JSON.parse(receiptText);
    const lockHash = sha256(lockText);
    if (receipt.skillVersion !== manifest.skillVersion) {
      throw new Error(`runtime receipt targets UX Proto ${receipt.skillVersion ?? "unknown"}, but this workspace requires ${manifest.skillVersion}`);
    }
    if (receipt.runtimeLockHash !== lockHash) {
      throw new Error("runtime receipt does not match this workspace runtime lock");
    }
    const runtimeRequire = createRequire(path.join(root, "package.json"));
    for (const [name, version] of Object.entries(manifest.dependencies)) {
      const actual = runtimeRequire(`${name}/package.json`).version;
      if (actual !== version) throw new Error(`${name} must be ${version}; found ${actual}`);
    }
    return { root, manifest, receipt, require: runtimeRequire, esbuild: runtimeRequire("esbuild") };
  } catch (error) {
    throw new Error(`UX Proto shared runtime is unavailable or invalid (${error.message}). Run node <installed-skill-root>/assets/scripts/setup-runtime.mjs.`);
  }
}

export function reservedRuntimePlugin(runtime) {
  const names = runtime.manifest.reservedPackages.map((name) => name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const filter = new RegExp(`^(?:${names.join("|")})(?:/.*)?$`);
  return {
    name: "ux-proto-reserved-runtime",
    setup(build) {
      build.onResolve({ filter }, (args) => ({ path: runtime.require.resolve(args.path) }));
    }
  };
}
