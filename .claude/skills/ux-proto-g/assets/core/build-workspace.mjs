import { createHash } from "node:crypto";
import { cp, mkdir, readFile, readdir, rename, rm, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { fail, stableJson, uniqueSorted } from "./common.mjs";
import { protectedSnapshotImportPlugin, snapshotExecutionRecords, validateMaterializedTemplate } from "./workflow.mjs";
import { requireUsableSnapshot } from "./snapshot.mjs";

const sha256 = (value) => createHash("sha256").update(value).digest("hex");
const exists = (file) => stat(file).then(() => true, (error) => error?.code === "ENOENT" ? false : Promise.reject(error));

async function recursiveFiles(root, relative = "") {
  if (!(await exists(root))) return [];
  const entries = await readdir(path.join(root, relative), { withFileTypes: true });
  const output = [];
  for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
    const child = path.join(relative, entry.name);
    if (entry.isDirectory()) output.push(...await recursiveFiles(root, child));
    else if (entry.isFile()) output.push(child.split(path.sep).join("/"));
  }
  return output;
}

export async function computeBuildSourceDigest(workspaceRoot) {
  const roots = [
    "page.tsx", "styles.css", "index.html", "package.json", "package-lock.json",
    "page-assets", "mock-data", "scripts", "theme", "runtime/core",
    ".ux-proto/resolved-assets"
  ];
  const managedOutputs = new Set(["page.bundle.js", "page.bundle.js.map", "page.bundle.css", "antd.css", "alias-vars.css"]);
  const files = [];
  for (const relative of roots) {
    const absolute = path.join(workspaceRoot, relative);
    if (!(await exists(absolute))) continue;
    const info = await stat(absolute);
    if (info.isFile()) files.push(relative);
    else for (const child of await recursiveFiles(absolute)) files.push(`${relative}/${child}`);
  }
  for (const entry of await readdir(workspaceRoot, { withFileTypes: true })) {
    if (entry.isFile() && /\.(?:[cm]?[jt]sx?)$/i.test(entry.name) && !managedOutputs.has(entry.name) && !files.includes(entry.name)) files.push(entry.name);
  }
  const records = [];
  for (const relative of uniqueSorted(files)) {
    const bytes = await readFile(path.join(workspaceRoot, relative));
    records.push({ path: relative, bytes: bytes.length, sha256: sha256(bytes) });
  }
  return { sourceDigest: `sha256:${sha256(stableJson(records))}`, sourceFiles: records };
}

const requiredBuildArtifacts = ["alias-vars.css", "antd.css", "index.static.html", "page.bundle.css", "page.bundle.js", "page.bundle.js.map"];
const runtimeBuildArtifacts = requiredBuildArtifacts.filter((file) => file !== "index.static.html");

export async function computeBuildArtifactDigest(workspaceRoot) {
  const artifacts = [];
  for (const relative of requiredBuildArtifacts) {
    const absolute = path.join(workspaceRoot, relative);
    if (!(await exists(absolute))) {
      artifacts.push({ path: relative, present: false });
      continue;
    }
    const bytes = await readFile(absolute);
    artifacts.push({ path: relative, present: true, bytes: bytes.length, sha256: sha256(bytes) });
  }
  return {
    artifacts,
    complete: artifacts.every((artifact) => artifact.present),
    artifactDigest: `sha256:${sha256(stableJson(artifacts))}`
  };
}

export function assessBuildCurrentness({ report, currentSource, currentArtifacts }) {
  const sourceFresh = Boolean(report.sourceDigest && currentSource.sourceDigest === report.sourceDigest);
  let artifactsFresh = false;
  if (report.completionStatus === "normal") {
    artifactsFresh = Boolean(currentArtifacts.complete && report.artifactDigest && currentArtifacts.artifactDigest === report.artifactDigest);
  } else if (report.completionStatus === "degraded") {
    const declared = new Map((report.artifacts ?? []).map((artifact) => [artifact.path, artifact]));
    const actual = new Map((currentArtifacts.artifacts ?? []).map((artifact) => [artifact.path, artifact]));
    const runtimeUsable = report.runtimePreview === "usable" && runtimeBuildArtifacts.every((file) => declared.get(file)?.present === true && actual.get(file)?.present === true);
    artifactsFresh = Boolean(runtimeUsable && report.artifactDigest && currentArtifacts.artifactDigest === report.artifactDigest);
  } else if (report.completionStatus === "failed") {
    artifactsFresh = true;
  }
  const fresh = sourceFresh && artifactsFresh;
  return { sourceFresh, artifactsFresh, fresh, completionStatus: fresh ? report.completionStatus : "stale" };
}

export async function collectMaterializedAssets({ workspaceRoot, snapshotRoot }) {
  const materializedAssets = [];
  const pageAssets = path.join(workspaceRoot, "page-assets");
  if (!(await exists(pageAssets))) return materializedAssets;
  for (const entry of (await readdir(pageAssets, { withFileTypes: true })).sort((a, b) => a.name.localeCompare(b.name))) {
    if (!entry.name.startsWith("template.")) continue;
    try {
      await validateMaterializedTemplate({ snapshotRoot, projectRoot: workspaceRoot, assetId: entry.name });
      materializedAssets.push(entry.name);
    } catch {
      // Invalid unobserved objects are handled by explicit repair; observed ones fail during build.
    }
  }
  return materializedAssets;
}

async function validatePageEntry(workspaceRoot) {
  const file = path.join(workspaceRoot, "page.tsx");
  let source;
  try { source = await readFile(file, "utf8"); }
  catch { fail("missing-page-export", "page.tsx 必须存在并 default export 一个普通 React component。", { file: "page.tsx" }); }
  const withoutComments = source.replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
  if (!/\bexport\s+default\b/.test(withoutComments)) fail("missing-page-export", "page.tsx 必须 default export 一个普通 React component。", { file: "page.tsx", expected: "export default function Page()" });
  if (/\bcreateRoot\s*\(|document\s*\.\s*getElementById\s*\(/.test(withoutComments)) fail("forbidden-page-root", "page.tsx 只能导出 component；browser/static root 由 UX Proto Core 管理。", { file: "page.tsx" });
}

export async function buildWorkspace({ workspaceRoot, runtime, snapshotRoot, helpers }) {
  const { antdBoundaryPlugin, validateAntdSourceBoundary, reservedRuntimePlugin, buildStaticPreview } = helpers;
  await validatePageEntry(workspaceRoot);
  await validateAntdSourceBoundary({ root: workspaceRoot });
  const snapshotPlugin = await protectedSnapshotImportPlugin(snapshotRoot);
  const browserEntry = `
    import React from "react";
    import { createRoot } from "react-dom/client";
    import Page from "./page.tsx";
    const root = document.getElementById("root");
    if (!root) throw new Error("Preview root #root was not found.");
    createRoot(root).render(React.createElement(Page));
  `;
  let build;
  try {
    build = await runtime.esbuild.build({
      absWorkingDir: workspaceRoot,
      stdin: { contents: browserEntry, resolveDir: workspaceRoot, sourcefile: "ux-proto-browser-entry.tsx", loader: "tsx" },
      bundle: true, outfile: "page.bundle.js", write: false, metafile: true, format: "iife", platform: "browser", target: ["es2020"], sourcemap: true, minify: false, jsx: "automatic",
      plugins: [snapshotPlugin, antdBoundaryPlugin(), reservedRuntimePlugin(runtime)],
      loader: { ".svg": "dataurl", ".png": "file", ".jpg": "file", ".jpeg": "file", ".gif": "file", ".woff": "file", ".woff2": "file" },
      define: { "process.env.NODE_ENV": '"production"' }, logLevel: "silent"
    });
  } catch (error) {
    if (/No matching export.*default|No matching export in .* for import "default"/i.test(error.message)) fail("missing-page-export", "page.tsx 缺少可导入的 default component export。", { file: "page.tsx" });
    if (/Public asset import is outside the resolved snapshot/i.test(error.message)) fail("snapshot-public-import-outside-surface", "A managed Pack Component import is outside the current snapshot public surface.", { recovery: "Remove the import or replace it with a specifier returned by current inspect output.", nextActions: [{ kind: "edit-source", rule: "current-public-surface-only" }] });
    throw error;
  }

  const publicEntries = await snapshotExecutionRecords(snapshotRoot);
  const observed = new Map();
  for (const input of Object.keys(build.metafile.inputs)) {
    const absolute = path.resolve(workspaceRoot, input);
    const publicAsset = publicEntries.get(absolute);
    const materialized = input.split(path.sep).join("/").match(/(?:^|\/)page-assets\/(template\.[a-z0-9]+(?:-[a-z0-9]+)*)\//)?.[1];
    const id = publicAsset ?? materialized;
    if (id) observed.set(id, [...(observed.get(id) ?? []), input.split(path.sep).join("/")]);
  }
  const observedReusableAssets = [...observed].sort(([a], [b]) => a.localeCompare(b)).map(([id, sourcePaths]) => ({ id, sourcePaths: uniqueSorted(sourcePaths) }));
  const actual = observedReusableAssets.map((item) => item.id);
  for (const item of observedReusableAssets.filter((entry) => entry.id.startsWith("template."))) {
    try { await validateMaterializedTemplate({ snapshotRoot, projectRoot: workspaceRoot, assetId: item.id }); item.provenance = "verified"; }
    catch (error) { fail(error.category ?? "materialization-provenance-mismatch", error.message, { ...(error.context ?? {}), assetId: item.id, observedSourcePaths: item.sourcePaths, recovery: "Quarantine the invalid governed target, then materialize it again from the current snapshot.", nextActions: [{ kind: "repair-materialization", assetId: item.id, command: `npm run ux-proto -- materialization repair --asset ${item.id} --json` }] }); }
  }
  for (const item of observedReusableAssets.filter((entry) => entry.id.startsWith("component."))) item.provenance = "snapshot-public-surface";
  const materializedAssets = await collectMaterializedAssets({ workspaceRoot, snapshotRoot });
  const warnings = materializedAssets.filter((id) => !actual.includes(id)).map((assetId) => ({ category: "unused-materialized-asset", assetId }));
  const snapshot = await requireUsableSnapshot(snapshotRoot);
  const source = await computeBuildSourceDigest(workspaceRoot);
  const report = {
    schemaVersion: 1,
    completionStatus: "failed",
    sourceDigest: source.sourceDigest,
    sourceFiles: source.sourceFiles,
    executionSafety: "verified",
    runtimePreview: "usable",
    staticPreview: "unavailable",
    snapshotDigest: snapshot.contentDigest,
    materializedAssets,
    observedReusableAssets,
    warnings
  };
  await mkdir(path.join(workspaceRoot, ".ux-proto"), { recursive: true });
  const staged = [];
  for (const output of build.outputFiles) { const name = path.basename(output.path); const temporary = path.join(workspaceRoot, `.${name}.tmp-${process.pid}`); await writeFile(temporary, output.contents); staged.push([temporary, path.join(workspaceRoot, name)]); }
  if (!staged.some(([, destination]) => destination.endsWith("page.bundle.css"))) { const temporary = path.join(workspaceRoot, `.page.bundle.css.tmp-${process.pid}`); await writeFile(temporary, "/* No imported component CSS. */\n"); staged.push([temporary, path.join(workspaceRoot, "page.bundle.css")]); }
  for (const [temporary, destination] of staged) await rename(temporary, destination);
  await cp(path.join(workspaceRoot, "theme/antd.generated.css"), path.join(workspaceRoot, "antd.css"));
  await cp(path.join(workspaceRoot, "theme/alias-vars.generated.css"), path.join(workspaceRoot, "alias-vars.css"));

  let degradedError = null;
  try {
    await buildStaticPreview({
      output: path.join(workspaceRoot, "index.static.html"), page: path.join(workspaceRoot, "page.tsx"),
      antdCssFile: path.join(workspaceRoot, "antd.css"), aliasCssFile: path.join(workspaceRoot, "alias-vars.css"), pageCssFile: path.join(workspaceRoot, "styles.css"), bundleCssFile: path.join(workspaceRoot, "page.bundle.css"),
      esbuild: runtime.esbuild, plugins: [snapshotPlugin, antdBoundaryPlugin(), reservedRuntimePlugin(runtime)]
    });
    const staticHtml = await readFile(path.join(workspaceRoot, "index.static.html"), "utf8");
    if (/<script\b/i.test(staticHtml)) throw new Error("static preview contains JavaScript");
    report.staticPreview = "usable";
  } catch (error) {
    await rm(path.join(workspaceRoot, "index.static.html"), { force: true });
    degradedError = { category: "static-render-failed", message: error.message, context: { output: "index.static.html" } };
  }
  report.completionStatus = degradedError ? "degraded" : "normal";
  if (degradedError) report.error = degradedError;
  const artifactState = await computeBuildArtifactDigest(workspaceRoot);
  report.artifacts = artifactState.artifacts;
  report.artifactDigest = artifactState.artifactDigest;
  await writeFile(path.join(workspaceRoot, ".ux-proto/build-report.json"), stableJson(report));
  await Promise.all(["page.bundle.js", "page.bundle.js.map", "page.bundle.css"].map((file) => stat(path.join(workspaceRoot, file))));
  return { completionStatus: report.completionStatus, report, runtimePreview: report.runtimePreview, staticPreview: report.staticPreview, ...(degradedError ? { error: degradedError } : {}) };
}
