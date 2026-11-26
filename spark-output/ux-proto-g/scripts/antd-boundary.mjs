import { readFile, readdir } from "node:fs/promises";
import path from "node:path";

async function sourceFiles(root) {
  const files = [];
  for (const entry of await readdir(root, { withFileTypes: true })) {
    if (["node_modules", ".git", ".od-skills"].includes(entry.name)) continue;
    const file = path.join(root, entry.name);
    if (entry.isDirectory()) files.push(...await sourceFiles(file));
    else if (/\.[cm]?[jt]sx?$/.test(entry.name)) files.push(file);
  }
  return files;
}

export async function validateAntdSourceBoundary({ root = process.cwd() } = {}) {
  const violations = [];
  for (const file of await sourceFiles(path.resolve(root))) {
    const source = await readFile(file, "utf8");
    const moduleSpecifiers = [
      ...source.matchAll(/\b(?:import|export)\s+(?!\s*["'])(?:type\s+)?[\s\S]*?\s+from\s+["'](antd(?:\/[^"']*)?)["']/g),
      ...source.matchAll(/\bimport\s*["'](antd(?:\/[^"']*)?)["']/g),
      ...source.matchAll(/\bimport\s*\(\s*["'](antd(?:\/[^"']*)?)["']\s*\)/g)
    ].map((match) => match[1]);
    for (const specifier of moduleSpecifiers) if (specifier.startsWith("antd/")) violations.push(`${path.relative(root, file)} -> ${specifier}`);
  }
  if (violations.length) throw new Error(`Forbidden AntD subpath import(s):\n${violations.join("\n")}\nImport public APIs from the antd root.`);
}

export function antdBoundaryPlugin({ root = process.cwd() } = {}) {
  return {
    name: "ux-proto-antd-boundary",
    setup(build) {
      build.onResolve({ filter: /^antd(?:\/|$)/ }, (args) => {
        if (args.path === "antd") return;
        return { errors: [{ text: `${args.importer || "entry"} imports forbidden AntD subpath ${args.path}; import public APIs from the antd root.` }] };
      });
      build.onResolve({ filter: /.*/ }, (args) => {
        if (!args.path.startsWith(".")) return;
        const resolved = path.resolve(args.resolveDir, args.path);
        const componentsDir = `${path.resolve(root, "components")}${path.sep}`;
        const approvedProductDirs = ["components/product", "components/product-specific"].map((directory) => `${path.resolve(root, directory)}${path.sep}`);
        const templatesDir = `${path.resolve(root, "templates")}${path.sep}`;
        if (resolved.startsWith(templatesDir)) {
          return { errors: [{ text: `${args.importer} must materialize Templates into page-assets before importing them (found ${args.path}).` }] };
        }
        const approvedProductImport = approvedProductDirs.some((directory) => resolved.startsWith(directory) || `${resolved}${path.sep}` === directory);
        if (resolved.startsWith(componentsDir) && !approvedProductImport) {
          return { errors: [{ text: `${args.importer} imports a protected component path (found ${args.path}).` }] };
        }
      });
    }
  };
}
