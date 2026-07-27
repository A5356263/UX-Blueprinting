import { lstat, mkdir, mkdtemp, readFile, readdir, realpath, rename, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath, pathToFileURL } from "node:url";
import { validateSourceManifest } from "../core/contracts.mjs";
import { sha256, stableJson } from "../core/common.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const canonicalPacksRoot = path.join(here, "../packs");
const requiredArtifactNames = ["alias-vars.generated.css", "antd.generated.css", "theme-config.generated.mjs"];
const runtimeDefaultTheme = new Map([
  ["alias-vars.generated.css", `/* UX Proto deterministic runtime default. */
:root {
  --alias-border-neutral: rgba(0, 0, 0, 0.15);
  --alias-font-size-body: 14px;
  --alias-radius-regular: 6px;
  --alias-space-2: 8px;
  --alias-space-3: 12px;
  --alias-space-4: 16px;
  --alias-space-5: 20px;
  --alias-surface-accent-solid: #1677ff;
  --alias-surface-container-bright: #ffffff;
  --alias-surface-container-muted: #f5f5f5;
  --alias-surface-error-tint: #fff2f0;
  --alias-surface-region-bright: #ffffff;
  --alias-surface-region-muted: #f5f5f5;
  --alias-text-accent: #1677ff;
  --alias-text-default: rgba(0, 0, 0, 0.88);
  --alias-text-inverse: #ffffff;
  --alias-text-secondary: rgba(0, 0, 0, 0.65);
}
`],
  ["antd.generated.css", "/* UX Proto deterministic runtime default; AntD runtime styles are provided by ConfigProvider. */\n"],
  ["theme-config.generated.mjs", "// UX Proto deterministic runtime default.\nexport const themeConfig = { cssVar: true };\n"]
]);

async function solePackRoot(packsRoot) {
  const entries = await readdir(packsRoot, { withFileTypes: true });
  const directories = entries.filter((entry) => entry.isDirectory() && !entry.isSymbolicLink());
  if (directories.length !== 1 || entries.some((entry) => entry.isSymbolicLink())) throw new Error("Runtime must contain exactly one real bundled Pack directory.");
  return path.join(packsRoot, directories[0].name);
}

async function containedRegularFile(root, relative) {
  const rootReal = await realpath(root);
  const candidate = path.resolve(root, relative);
  const candidateReal = await realpath(candidate).catch(() => null);
  if (!candidateReal || !candidateReal.startsWith(`${rootReal}${path.sep}`)) throw new Error(`Runtime theme artifact is missing or escapes the bundled Pack: ${relative}.`);
  let current = root;
  for (const segment of path.relative(root, candidate).split(path.sep)) {
    current = path.join(current, segment);
    const info = await lstat(current);
    if (info.isSymbolicLink()) throw new Error(`Runtime theme artifact crosses a symlink: ${relative}.`);
  }
  const info = await lstat(candidate);
  if (!info.isFile()) throw new Error(`Runtime theme artifact is not a regular file: ${relative}.`);
  return candidate;
}

export async function installRuntimeTheme({ packsRoot = canonicalPacksRoot, outputDir }) {
  const packRoot = await solePackRoot(path.resolve(packsRoot));
  const manifest = validateSourceManifest(JSON.parse(await readFile(path.join(packRoot, "manifest.json"), "utf8")), "bundled Pack manifest");
  const source = manifest.runtimeTheme ? "pack" : "runtime-default";
  const artifacts = [];
  if (manifest.runtimeTheme) {
    const names = manifest.runtimeTheme.artifacts.map((artifact) => path.posix.basename(artifact)).sort();
    if (JSON.stringify(names) !== JSON.stringify(requiredArtifactNames)) throw new Error(`Bundled Pack runtimeTheme must declare exactly: ${requiredArtifactNames.join(", ")}.`);
    for (const relative of manifest.runtimeTheme.artifacts) {
      const artifactFile = await containedRegularFile(packRoot, relative);
      const contents = await readFile(artifactFile);
      artifacts.push({ relative, name: path.basename(relative), contents, sha256: sha256(contents) });
    }
  } else {
    for (const [name, value] of runtimeDefaultTheme) {
      const contents = Buffer.from(value);
      artifacts.push({ relative: null, name, contents, sha256: sha256(contents) });
    }
  }
  artifacts.sort((a, b) => a.name.localeCompare(b.name));
  const tempRoot = await mkdtemp(path.join(tmpdir(), "ux-proto-runtime-theme-"));
  const tempOutput = path.join(tempRoot, "theme");
  try {
    await mkdir(tempOutput);
    for (const artifact of artifacts) await writeFile(path.join(tempOutput, artifact.name), artifact.contents);
    await writeFile(path.join(tempOutput, "runtime-theme-receipt.json"), stableJson({
      schemaVersion: 1,
      kind: "ux-proto-runtime-theme-receipt",
      source,
      pack: { id: manifest.id, version: manifest.version },
      artifacts: artifacts.map(({ name, sha256: digest }) => ({ name, sha256: digest }))
    }));
    await mkdir(path.dirname(outputDir), { recursive: true });
    await rm(outputDir, { recursive: true, force: true });
    await rename(tempOutput, outputDir);
  } finally {
    await rm(tempRoot, { recursive: true, force: true });
  }
  return { source, pack: { id: manifest.id, version: manifest.version }, artifacts: artifacts.map(({ name, sha256: digest }) => ({ name, sha256: digest })) };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const outputIndex = process.argv.indexOf("--output");
  const packsIndex = process.argv.indexOf("--packs-root");
  if (outputIndex === -1 || !process.argv[outputIndex + 1]) throw new Error("--output is required.");
  const result = await installRuntimeTheme({
    packsRoot: packsIndex === -1 ? canonicalPacksRoot : path.resolve(process.argv[packsIndex + 1]),
    outputDir: path.resolve(process.argv[outputIndex + 1])
  });
  console.log(JSON.stringify(result, null, 2));
}
