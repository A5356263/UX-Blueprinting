import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

function requestedOutput() {
  const index = process.argv.indexOf("--output");
  if (index === -1) return "index.static.html";
  if (!process.argv[index + 1]) throw new Error("--output requires a file path");
  return process.argv[index + 1];
}

export async function buildStaticPreview({
  output = requestedOutput(),
  page = "page.tsx",
  antdCssFile = "antd.css",
  aliasCssFile = "alias-vars.css",
  pageCssFile = "styles.css",
  bundleCssFile = "page.bundle.css",
  esbuild,
  plugins = []
} = {}) {
  if (!esbuild) throw new Error("buildStaticPreview requires the Skill-owned esbuild runtime.");
  const workdir = await mkdtemp(path.join(tmpdir(), "od-static-preview-"));
  const renderer = path.join(workdir, "render.cjs");

  try {
    await esbuild.build({
      stdin: {
        contents: `
          import React from "react";
          import { renderToStaticMarkup } from "react-dom/server";
          import { GeneratedPage } from ${JSON.stringify(path.resolve(page))};
          export const markup = renderToStaticMarkup(React.createElement(GeneratedPage));
        `,
        resolveDir: process.cwd(),
        sourcefile: "static-preview-entry.tsx",
        loader: "tsx"
      },
      bundle: true,
      outfile: renderer,
      format: "cjs",
      platform: "node",
      target: ["node20"],
      jsx: "automatic",
      define: { "process.env.NODE_ENV": '"production"' },
      logLevel: "silent",
      plugins
    });

    const { markup } = createRequire(import.meta.url)(renderer);
    if (!markup || !/<[a-z][^>]*>/i.test(markup)) {
      throw new Error("Static render produced no initial business DOM.");
    }

    const antdCss = (await readFile(antdCssFile, "utf8")).replaceAll("</style", "<\\/style");
    const aliasCss = (await readFile(aliasCssFile, "utf8")).replaceAll("</style", "<\\/style");
    const pageCss = (await readFile(pageCssFile, "utf8")).replaceAll("</style", "<\\/style");
    const bundleCss = (await readFile(bundleCssFile, "utf8")).replaceAll("</style", "<\\/style");
    const html = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="od-source" content="page.tsx" />
    <meta name="od-derived" content="static-design-surface" />
    <title>React Prototype — Static Design Surface</title>
    <style data-od-source="antd.css">${antdCss}</style>
    <style data-od-source="alias-vars.css">${aliasCss}</style>
    <style data-od-source="styles.css">${pageCss}</style>
    <style data-od-source="page.bundle.css">${bundleCss}</style>
  </head>
  <body>
    <!-- Derived output. Edit page.tsx and styles.css, then rebuild. -->
    <div id="root">${markup}</div>
  </body>
</html>
`;

    await writeFile(output, html, "utf8");
    return output;
  } finally {
    await rm(workdir, { recursive: true, force: true });
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [{ antdBoundaryPlugin, validateAntdSourceBoundary }, { loadSkillRuntime, reservedRuntimePlugin }] = await Promise.all([
    import("./antd-boundary.mjs"),
    import("./runtime.mjs")
  ]);
  const runtime = await loadSkillRuntime();
  await validateAntdSourceBoundary();
  const output = await buildStaticPreview({
    esbuild: runtime.esbuild,
    plugins: [antdBoundaryPlugin(), reservedRuntimePlugin(runtime)]
  });
  console.log(`Static design surface written to ${output}`);
}
