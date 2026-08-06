import { mkdir, readFile, rename, rm, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { antdBoundaryPlugin, validateAntdSourceBoundary } from "./antd-boundary.mjs";
import { buildStaticPreview } from "./build-static-preview.mjs";
import { loadSkillRuntime, reservedRuntimePlugin } from "./runtime.mjs";
import { validatePagePlan } from "./validate-page-plan.mjs";

const runtime = await loadSkillRuntime();
let plan;
try {
  plan = await validatePagePlan();
} catch (error) {
  await mkdir(".ux-proto", { recursive: true });
  await writeFile(".ux-proto/build-report.json", `${JSON.stringify({ schemaVersion: 1, planStatus: "invalid", knowledgeDelivery: "invalid", executionClosure: "not-run", error: { message: error instanceof Error ? error.message : String(error) } }, null, 2)}\n`);
  throw error;
}
await validateAntdSourceBoundary();

const productRegistry = JSON.parse(await readFile("registries/product-specific-components.registry.json", "utf8"));
const productPaths = new Map(productRegistry.records.map((record) => [record.productSpecificComponent.implementation.importPath.replace(/^\.\//, ""), record.id]));
const build = await runtime.esbuild.build({
  entryPoints: ["page.tsx"], bundle: true, outfile: "page.bundle.js", write: false, metafile: true,
  format: "iife", platform: "browser", target: ["es2020"], sourcemap: true, minify: false,
  jsx: "automatic", plugins: [antdBoundaryPlugin(), reservedRuntimePlugin(runtime)],
  define: { "process.env.NODE_ENV": '"production"' }
});

const observed = new Map();
for (const input of Object.keys(build.metafile.inputs)) {
  const normalized = input.split(path.sep).join("/").replace(/^\.\//, "");
  const template = normalized.match(/(?:^|\/)page-assets\/(template\.[a-z0-9-]+(?:\.[a-z0-9-]+)?)\//)?.[1];
  if (template) {
    const paths = observed.get(template) ?? [];
    paths.push(normalized); observed.set(template, paths);
  }
  for (const [importPath, id] of productPaths) if (normalized === `${importPath}.tsx` || normalized.startsWith(`${importPath}.`)) {
    const paths = observed.get(id) ?? [];
    paths.push(normalized); observed.set(id, paths);
  }
}
const observedReusableAssets = [...observed].sort(([a], [b]) => a.localeCompare(b)).map(([id, sourcePaths]) => ({ id, sourcePaths: [...new Set(sourcePaths)].sort() }));
const actual = observedReusableAssets.map((item) => item.id);
const expected = plan.executionAssetIds ?? [];
const undeclared = actual.filter((id) => !expected.includes(id));
const unreachable = expected.filter((id) => !actual.includes(id));
const report = {
  schemaVersion: 1,
  planStatus: plan.planStatus,
  knowledgeDelivery: plan.knowledgeDelivery,
  executionClosure: plan.status === "absent" ? "skipped" : undeclared.length || unreachable.length ? "failed" : "verified",
  observedReusableAssets,
  ...(plan.knowledgeIndexStats ? { knowledgeIndexStats: plan.knowledgeIndexStats } : {}),
  ...(plan.knowledgeGuidanceStats ? { knowledgeGuidanceStats: plan.knowledgeGuidanceStats } : {}),
  planningDrift: plan.planningDrift,
  requestDrift: plan.requestDrift,
  closure: { authorizedAssetIds: expected, actualAssetIds: actual, undeclared, unreachable }
};
await mkdir(".ux-proto", { recursive: true });
if (plan.status !== "absent" && (undeclared.length || unreachable.length)) {
  await writeFile(".ux-proto/build-report.json", `${JSON.stringify(report, null, 2)}\n`);
  throw new Error(`UX Proto execution closure failed: undeclared=[${undeclared.join(", ")}], unreachable=[${unreachable.join(", ")}]. Replan when selection changed; otherwise align source imports with receipt actions.`);
}

const staged = [];
for (const output of build.outputFiles) {
  const name = path.basename(output.path);
  const temporary = `.${name}.tmp-${process.pid}`;
  await writeFile(temporary, output.contents);
  staged.push([temporary, name]);
}
if (!staged.some(([, name]) => name === "page.bundle.css")) {
  const temporary = `.page.bundle.css.tmp-${process.pid}`;
  await writeFile(temporary, "/* No imported component CSS. */\n", "utf8"); staged.push([temporary, "page.bundle.css"]);
}
for (const [source, destination] of staged) await rename(source, destination);
for (const [source, destination] of [["theme/antd.generated.css", "antd.css"], ["theme/alias-vars.generated.css", "alias-vars.css"]]) {
  const temporary = `.${destination}.tmp-${process.pid}`;
  await writeFile(temporary, await readFile(source)); await rename(temporary, destination);
}
await writeFile(".ux-proto/build-report.json", `${JSON.stringify(report, null, 2)}\n`);

let staticPreviewBuilt = false;
try {
  await buildStaticPreview({ esbuild: runtime.esbuild, plugins: [antdBoundaryPlugin(), reservedRuntimePlugin(runtime)] });
  const staticHtml = await readFile("index.static.html", "utf8");
  if (/<script\b/i.test(staticHtml)) throw new Error("Static preview must remain JavaScript-free.");
  if (!staticHtml.includes('data-od-source="page.bundle.css"')) throw new Error("Static preview must include imported component CSS.");
  staticPreviewBuilt = true;
} catch (error) {
  await rm("index.static.html", { force: true });
  console.warn(`[ux-proto] Static preview warning: ${error instanceof Error ? error.message : String(error)}`);
}
await Promise.all(["page.bundle.js", "page.bundle.js.map", "page.bundle.css", "antd.css", "alias-vars.css"].map((file) => stat(file)));
const runtimeHtml = await readFile("index.html", "utf8");
if (!runtimeHtml.includes("page.bundle.js") || !runtimeHtml.includes("styles.css") || !runtimeHtml.includes("page.bundle.css")) throw new Error("Runtime preview must load local bundle, page styles, and imported component styles.");
console.log(staticPreviewBuilt ? "Runtime/static preview and UX Proto closure validation passed." : "Runtime preview and UX Proto closure validation passed; static preview is unavailable.");
