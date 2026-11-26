import { lstat, readFile, readdir, realpath, stat } from "node:fs/promises";
import path from "node:path";
import { digestObject, exists, fail, posixPath, readJson, sha256, uniqueSorted } from "./common.mjs";
import {
  canonicalRuntimeThemeArtifactBasenames,
  collectAssetLinks,
  isCanonicalAssetId,
  projectContentGfm,
  validateAssetDescriptor,
  validateSourceManifest
} from "./contracts.mjs";
import {
  extractTypeScriptPublicContract,
  projectTypeScriptPublicApi,
  validatePackComponentApi,
  validateTemplatePublicContract
} from "./typescript-public-contract.mjs";

const jsExtensions = ["", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json", ".css"];
const codeExtensions = new Set([".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"]);
const cssExtensions = new Set([".css"]);
const runtimeImports = new Set(["react", "react/jsx-runtime", "react/jsx-dev-runtime", "react-dom", "react-dom/client", "antd", "@ant-design/icons", "dayjs"]);
const publicPrefix = "@ux-proto/assets/";

function lexNormalizedModuleReferences(source, file, chain) {
  const tokens = [];
  let index = 0;
  const push = (type, value, start) => tokens.push({ type, value, start });
  const location = (start) => {
    const before = source.slice(0, start);
    const line = before.split("\n").length;
    const lastBreak = before.lastIndexOf("\n");
    return { line, column: start - lastBreak };
  };
  const regexPrefixKeywords = new Set(["await", "case", "delete", "do", "else", "in", "instanceof", "new", "return", "throw", "typeof", "void", "yield"]);
  const regexPrefixPunctuators = new Set(["(", "[", "{", ",", ";", ":", "=", "!", "?", "&", "|", "+", "-", "*", "%", "^", "~", "<", ">"]);
  const regexAllowed = () => {
    const previous = tokens.at(-1);
    return !previous || (previous.type === "identifier" ? regexPrefixKeywords.has(previous.value) : regexPrefixPunctuators.has(previous.value));
  };
  const skipQuoted = (quote, emit) => {
    const start = index;
    let value = "";
    index += 1;
    while (index < source.length && source[index] !== quote) {
      if (source[index] === "\\" && index + 1 < source.length) { value += source[index + 1]; index += 2; }
      else { value += source[index]; index += 1; }
    }
    if (index < source.length) index += 1;
    if (emit) push("string", value, start + 1);
  };
  const scanCode = (templateExpression = false) => {
    let braceDepth = 0;
    while (index < source.length) {
    const char = source[index];
    if (/\s/.test(char)) { index += 1; continue; }
    if (char === "/" && source[index + 1] === "/") { index = source.indexOf("\n", index + 2); if (index === -1) break; continue; }
    if (char === "/" && source[index + 1] === "*") { const end = source.indexOf("*/", index + 2); index = end === -1 ? source.length : end + 2; continue; }
    if (char === '"' || char === "'") {
      skipQuoted(char, true);
      continue;
    }
    if (char === "`") {
      index += 1;
      while (index < source.length) {
        if (source[index] === "\\") { index += 2; continue; }
        if (source[index] === "`") { index += 1; break; }
        if (source[index] === "$" && source[index + 1] === "{") { index += 2; scanCode(true); continue; }
        index += 1;
      }
      continue;
    }
    if (char === "/" && regexAllowed()) {
      index += 1;
      let characterClass = false;
      while (index < source.length) {
        if (source[index] === "\\") { index += 2; continue; }
        if (source[index] === "[") characterClass = true;
        else if (source[index] === "]") characterClass = false;
        else if (source[index] === "/" && !characterClass) { index += 1; while (/[A-Za-z]/.test(source[index] ?? "")) index += 1; break; }
        index += 1;
      }
      continue;
    }
    if (/[A-Za-z_$]/.test(char)) {
      const start = index;
      let end = index + 1;
      while (end < source.length && /[A-Za-z0-9_$-]/.test(source[end])) end += 1;
      push("identifier", source.slice(index, end), start);
      index = end;
      continue;
    }
    if (templateExpression && char === "}") {
      if (braceDepth === 0) { index += 1; return; }
      braceDepth -= 1;
    } else if (templateExpression && char === "{") braceDepth += 1;
    push("punctuator", char, index);
    index += 1;
    }
  };
  scanCode();
  const findFrom = (cursor) => {
    for (let look = cursor; look < tokens.length; look += 1) {
      if (tokens[look].value === ";") return null;
      if (tokens[look].value === "from" && tokens[look + 1]?.type === "string") return tokens[look + 1];
    }
    return null;
  };
  const matchingBrace = (cursor) => {
    let depth = 0;
    for (let look = cursor; look < tokens.length; look += 1) {
      if (tokens[look].value === "{") depth += 1;
      if (tokens[look].value === "}" && --depth === 0) return look;
    }
    return tokens.length;
  };
  const matchingParen = (cursor) => {
    let depth = 0;
    for (let look = cursor; look < tokens.length; look += 1) {
      if (tokens[look].value === "(") depth += 1;
      if (tokens[look].value === ")" && --depth === 0) return look;
    }
    return tokens.length;
  };
  const isMemberAccess = (cursor) => tokens[cursor - 1]?.value === ".";
  const isMethodKey = (cursor) => {
    if (tokens[cursor + 1]?.value !== "(") return false;
    const closing = matchingParen(cursor + 1);
    return tokens[closing + 1]?.value === "{";
  };
  const references = [];
  const add = (token, kind) => {
    if (!token) return;
    references.push({ specifier: token.value, kind, sourceLocation: location(token.start) });
  };
  for (let cursor = 0; cursor < tokens.length; cursor += 1) {
    const token = tokens[cursor];
    if (token.type !== "identifier") continue;
    if (isMemberAccess(cursor) || isMethodKey(cursor)) continue;
    if (token.value === "require" && tokens[cursor + 1]?.value === "." && tokens[cursor + 2]?.value === "resolve" && tokens[cursor + 3]?.value === "(") {
      add(tokens[cursor + 4]?.type === "string" ? tokens[cursor + 4] : { value: "<nonliteral>", start: token.start }, "require-resolve");
      continue;
    }
    if (token.value === "require" && tokens[cursor + 1]?.value === "(") {
      add(tokens[cursor + 2]?.type === "string" ? tokens[cursor + 2] : { value: "<nonliteral>", start: token.start }, "require-call");
    }
    if (token.value === "import") {
      if (tokens[cursor + 1]?.value === "(") {
        if (tokens[cursor + 2]?.type !== "string" || tokens[cursor + 3]?.value !== ")") fail("nonliteral-dynamic-import", `不允许非字面量 dynamic import：${file}。`, { file, chain });
        add(tokens[cursor + 2], "dynamic-import");
        continue;
      }
      if (tokens[cursor + 1]?.type === "string") add(tokens[cursor + 1], "import-statement");
      else { const specifier = findFrom(cursor + 1); if (specifier) add(specifier, "import-statement"); }
    }
    if (token.value === "export") {
      let start = cursor + 1;
      if (tokens[start]?.value === "type") start += 1;
      if (tokens[start]?.value === "{") start = matchingBrace(start) + 1;
      if (tokens[start]?.value === "*" || tokens[start]?.value === "from" || tokens[start - 1]?.value === "}") {
        const specifier = findFrom(start);
        if (specifier) add(specifier, "export-from");
      }
    }
  }
  return references;
}

function loaderFor(file) {
  return path.extname(file).slice(1).replace("mjs", "js").replace("cjs", "js") || "js";
}

async function rawCodeProjection({ source, file, esbuild, chain }) {
  let transformed;
  let result;
  try {
    [transformed, result] = await Promise.all([
      esbuild.transform(source, {
        loader: loaderFor(file),
        jsx: "transform",
        legalComments: "none",
        sourcefile: path.basename(file),
        treeShaking: false
      }),
      esbuild.build({
        stdin: { contents: source, sourcefile: path.basename(file), resolveDir: path.dirname(file), loader: loaderFor(file) },
        bundle: true,
        format: "esm",
        write: false,
        metafile: true,
        logLevel: "silent",
        treeShaking: false,
        plugins: [{ name: "ux-proto-scan-only", setup(build) { build.onResolve({ filter: /.*/ }, (args) => args.kind === "entry-point" ? undefined : ({ path: args.path, external: true })); } }]
      })
    ]);
  } catch (error) {
    fail("source-parse-error", `无法解析 ${file}：${error.errors?.[0]?.text ?? error.message}。`, { file, chain });
  }
  const input = Object.values(result.metafile.inputs ?? {})[0];
  const outputs = Object.values(result.metafile.outputs ?? {});
  const output = outputs.find((item) => item.exports?.length) ?? outputs.find((item) => item.entryPoint) ?? outputs[0];
  const normalizedImports = lexNormalizedModuleReferences(transformed.code, file, chain);
  const normalizedCounts = new Map();
  for (const item of normalizedImports) normalizedCounts.set(item.specifier, (normalizedCounts.get(item.specifier) ?? 0) + 1);
  const parserCounts = new Map();
  const parserOnly = [];
  for (const item of input?.imports ?? []) {
    if (item.path.startsWith("<") && item.path.endsWith(">")) continue;
    const seen = parserCounts.get(item.path) ?? 0;
    parserCounts.set(item.path, seen + 1);
    if (seen >= (normalizedCounts.get(item.path) ?? 0)) parserOnly.push({ specifier: item.path, kind: item.kind });
  }
  return {
    imports: [...normalizedImports, ...parserOnly],
    exports: Array.isArray(output?.exports) ? [...output.exports].sort() : null
  };
}

function sourceLocation(source, start) {
  const before = source.slice(0, start);
  const lastBreak = before.lastIndexOf("\n");
  return { line: before.split("\n").length, column: start - lastBreak };
}

function mutationFor(specifier) {
  return specifier.replace(/[A-Za-z0-9]/g, (value) => value === "x" ? "y" : "x");
}

function occurrences(source, value) {
  const result = [];
  let start = 0;
  while (value && start < source.length) {
    const found = source.indexOf(value, start);
    if (found === -1) break;
    result.push(found);
    start = found + value.length;
  }
  return result;
}

function decodeStringBody(body) {
  let decoded = "";
  for (let index = 0; index < body.length; index += 1) {
    if (body[index] !== "\\") {
      decoded += body[index];
      continue;
    }
    index += 1;
    if (index >= body.length) return null;
    const escaped = body[index];
    const simple = { n: "\n", r: "\r", t: "\t", b: "\b", f: "\f", v: "\v", 0: "\0" };
    if (escaped in simple) decoded += simple[escaped];
    else if (escaped === "x") {
      const digits = body.slice(index + 1, index + 3);
      if (!/^[a-f0-9]{2}$/i.test(digits)) return null;
      decoded += String.fromCodePoint(Number.parseInt(digits, 16));
      index += 2;
    } else if (escaped === "u") {
      const braced = body[index + 1] === "{";
      const end = braced ? body.indexOf("}", index + 2) : index + 5;
      const digits = braced ? body.slice(index + 2, end) : body.slice(index + 1, end);
      if (end === -1 || !(braced ? /^[a-f0-9]{1,6}$/i : /^[a-f0-9]{4}$/i).test(digits)) return null;
      decoded += String.fromCodePoint(Number.parseInt(digits, 16));
      index = braced ? end : end - 1;
    } else if (escaped === "\n") {
      // JavaScript line continuation contributes no character.
    } else decoded += escaped;
  }
  return decoded;
}

function stringLiteralOccurrences(source, value) {
  const result = [];
  for (let index = 0; index < source.length; index += 1) {
    const quote = source[index];
    if (quote !== '"' && quote !== "'") continue;
    const start = index;
    let body = "";
    let escaped = false;
    for (index += 1; index < source.length; index += 1) {
      const character = source[index];
      if (!escaped && character === quote) break;
      body += character;
      if (escaped) escaped = false;
      else if (character === "\\") escaped = true;
    }
    if (index >= source.length) break;
    if (decodeStringBody(body) === value) {
      result.push({ start: start + 1, replaceStart: start, replaceEnd: index + 1 });
    }
  }
  return result;
}

async function locateParserReferences({ source, file, esbuild, chain, imports }) {
  const groups = new Map();
  for (const item of imports) {
    const key = `${item.kind}\0${item.specifier}`;
    groups.set(key, [...(groups.get(key) ?? []), item]);
  }
  const located = [];
  for (const [key, references] of groups) {
    const { kind, specifier } = references[0];
    const candidates = [
      ...occurrences(source, specifier).map((start) => ({ start, replaceStart: start, replaceEnd: start + specifier.length })),
      ...stringLiteralOccurrences(source, specifier)
    ].filter((candidate, index, all) => all.findIndex((item) => item.replaceStart === candidate.replaceStart && item.replaceEnd === candidate.replaceEnd) === index);
    const valid = [];
    for (const candidate of candidates) {
      const replacement = mutationFor(specifier);
      const original = source.slice(candidate.replaceStart, candidate.replaceEnd);
      const mutatedReplacement = original.startsWith('"') || original.startsWith("'") ? JSON.stringify(replacement) : replacement;
      const mutated = `${source.slice(0, candidate.replaceStart)}${mutatedReplacement}${source.slice(candidate.replaceEnd)}`;
      const projection = await rawCodeProjection({ source: mutated, file, esbuild, chain });
      const remaining = projection.imports.filter((item) => `${item.kind}\0${item.specifier}` === key).length;
      if (remaining < references.length) valid.push(candidate.start);
    }
    if (valid.length < references.length) {
      fail("source-location-unavailable", `无法确定真实 module specifier 的来源位置：${specifier}。`, { file, chain, kind, specifier });
    }
    for (let index = 0; index < references.length; index += 1) {
      located.push({ specifier, kind, sourceLocation: sourceLocation(source, valid[index]) });
    }
  }
  return located;
}

async function containedRealPath(root, candidate, context) {
  const [rootReal, candidateReal] = await Promise.all([realpath(root), realpath(candidate).catch(() => null)]);
  if (!candidateReal) fail("missing-artifact", `找不到本地依赖：${candidate}。`, context);
  const relative = path.relative(rootReal, candidateReal);
  if (relative.startsWith("..") || path.isAbsolute(relative)) fail("source-escape", `路径逃逸来源边界：${candidate}。`, context);
  const info = await lstat(candidate);
  if (info.isSymbolicLink()) fail("symlink-escape", `来源资产不允许符号链接：${candidate}。`, context);
  return candidateReal;
}

async function resolveRelative(importer, specifier, sourceRoot, context) {
  const base = path.resolve(path.dirname(importer), specifier);
  const candidates = jsExtensions.flatMap((extension) => [base + extension, path.join(base, `index${extension}`)]);
  for (const candidate of candidates) {
    if ((await stat(candidate).catch(() => null))?.isFile()) return containedRealPath(sourceRoot, candidate, context);
  }
  fail("missing-artifact", `无法解析本地 import：${specifier}。`, context);
}

export async function projectCodeModuleReferences({ file, esbuild, chain = [] }) {
  if (!esbuild?.build || !esbuild?.transform) fail("runtime-unavailable", "固定 runtime 中缺少 JS/TS parser。", { chain });
  const source = await readFile(file, "utf8");
  const projection = await rawCodeProjection({ source, file, esbuild, chain });
  const imports = await locateParserReferences({ source, file, esbuild, chain, imports: projection.imports });
  imports.sort((a, b) => a.sourceLocation.line - b.sourceLocation.line || a.sourceLocation.column - b.sourceLocation.column || a.kind.localeCompare(b.kind));
  return {
    imports,
    exports: projection.exports
  };
}

function parseCss(source, file, chain) {
  let projected = "";
  let quote = null;
  for (let index = 0; index < source.length; index += 1) {
    const character = source[index];
    if (quote) {
      projected += character;
      if (character === "\\") {
        index += 1;
        if (index < source.length) projected += source[index];
      } else if (character === quote) quote = null;
      continue;
    }
    if (character === '"' || character === "'") {
      quote = character;
      projected += character;
      continue;
    }
    if (character === "/" && source[index + 1] === "*") {
      projected += "  ";
      index += 2;
      while (index < source.length && !(source[index] === "*" && source[index + 1] === "/")) {
        projected += source[index] === "\n" ? "\n" : " ";
        index += 1;
      }
      if (index < source.length) {
        projected += "  ";
        index += 1;
      }
      continue;
    }
    projected += character;
  }
  const imports = [];
  for (const match of projected.matchAll(/@import\s+(?:url\(\s*)?["']([^"']+)["']/g)) imports.push(match[1]);
  for (const match of projected.matchAll(/url\(\s*["']?([^"')]+)["']?\s*\)/g)) if (!match[1].startsWith("data:") && !match[1].startsWith("#")) imports.push(match[1]);
  for (const specifier of imports) if (/^(?:https?:)?\/\//.test(specifier)) fail("external-artifact", `CSS 不允许外部 URL：${specifier}。`, { file, chain });
  return uniqueSorted(imports);
}

async function scanAssetFiles(asset, source, esbuild, declaredEntries) {
  const descriptorDirectory = path.dirname(asset.descriptorFile);
  const pending = uniqueSorted([asset.entry, ...(asset.artifacts ?? [])].filter(Boolean)).map((relative) => path.resolve(descriptorDirectory, relative));
  const visited = new Set();
  const files = [];
  const importedAssets = new Set();
  const publicImports = [];
  let entryRuntimeExports = null;
  while (pending.length) {
    const candidate = pending.shift();
    const file = await containedRealPath(source.root, candidate, { assetId: asset.id, chain: [asset.id, posixPath(path.relative(source.root, candidate))] });
    if (visited.has(file)) continue;
    const otherOwner = declaredEntries.get(file);
    if (otherOwner && otherOwner.assetId !== asset.id && otherOwner.rootType === "entry") fail("cross-asset-relative-import", `${asset.id} 不能通过相对路径导入 ${otherOwner.assetId}。`, { chain: [asset.id, otherOwner.assetId], file });
    visited.add(file);
    const relativeToDescriptor = posixPath(path.relative(descriptorDirectory, file));
    const relativeToSource = posixPath(path.relative(source.root, file));
    const contents = await readFile(file);
    files.push({ sourcePath: relativeToSource, snapshotPath: `files/${asset.id}/${relativeToDescriptor}`, sha256: sha256(contents), contents });
    const extension = path.extname(file).toLowerCase();
    let imports = [];
    if (codeExtensions.has(extension)) {
      const parsed = await projectCodeModuleReferences({ file, esbuild, chain: [asset.id, relativeToDescriptor] });
      imports = parsed.imports;
      if (asset.entry && relativeToDescriptor === asset.entry) entryRuntimeExports = parsed.exports;
    }
    else if (cssExtensions.has(extension)) imports = parseCss(contents.toString("utf8"), file, [asset.id, relativeToDescriptor]).map((specifier) => ({ specifier, kind: "css-import" }));
    for (const item of imports) {
      const { specifier, kind } = item;
      if (kind === "require-call" || kind === "require-resolve") fail("unsupported-require", `不允许 require()：${relativeToDescriptor}。`, { chain: [asset.id, relativeToDescriptor, specifier] });
      if (specifier.startsWith(publicPrefix)) {
        const target = specifier.slice(publicPrefix.length);
        if (!target) fail("invalid-public-import", `public import 缺少资产 ID：${specifier}。`, { assetId: asset.id });
        importedAssets.add(target);
        publicImports.push({
          target,
          sourcePath: relativeToSource,
          kind,
          sourceLocation: item.sourceLocation ?? null
        });
      } else if (specifier.startsWith(".")) {
        if (specifier.split(/[\\/]/).includes("..")) fail("path-traversal", `本地 import 不允许路径上跳：${specifier}。`, { chain: [asset.id, relativeToDescriptor, specifier] });
        pending.push(await resolveRelative(file, specifier.split("?")[0].split("#")[0], source.root, { assetId: asset.id, chain: [asset.id, relativeToDescriptor, specifier] }));
      } else if (specifier.startsWith("antd/")) {
        fail("forbidden-antd-subpath", `不允许 AntD subpath import：${specifier}。`, { chain: [asset.id, relativeToDescriptor, specifier] });
      } else if (!runtimeImports.has(specifier)) {
        fail("arbitrary-package", `资产不能携带或使用 runtime policy 外的包：${specifier}。`, { chain: [asset.id, relativeToDescriptor, specifier] });
      }
    }
  }
  return {
    files: files.sort((a, b) => a.snapshotPath.localeCompare(b.snapshotPath)),
    importedAssets: uniqueSorted([...importedAssets]),
    publicImports: publicImports.sort((a, b) => a.sourcePath.localeCompare(b.sourcePath) || a.target.localeCompare(b.target) || a.kind.localeCompare(b.kind)),
    entryRuntimeExports
  };
}

export function implementationPreviewDigest({ asset, files }) {
  const fileProjection = files.map(({ snapshotPath, sha256: digest }) => ({ snapshotPath, sha256: digest }));
  if (asset.kind === "Template") return digestObject({ authoring: asset.authoring, files: fileProjection });
  if (asset.kind === "Pack Component") return digestObject({ api: asset.api, usage: asset.usage, files: fileProjection });
  return null;
}

export async function projectAssetImplementationClosures({ packRoot, assets, esbuild, tolerant = false }) {
  const root = await realpath(path.resolve(packRoot));
  const source = { root };
  const normalizedAssets = await Promise.all(assets.map(async (asset) => ({
    ...asset,
    descriptorFile: asset.descriptorPath
      ? path.join(root, asset.descriptorPath)
      : await realpath(asset.descriptorFile).catch(() => path.resolve(asset.descriptorFile))
  })));
  const declaredEntries = new Map();
  const diagnostics = [];
  for (const asset of normalizedAssets) {
    for (const [index, relative] of [asset.entry, ...(asset.artifacts ?? [])].filter(Boolean).entries()) {
      const absolute = path.resolve(path.dirname(asset.descriptorFile), relative);
      const real = await realpath(absolute).catch(() => absolute);
      const owner = declaredEntries.get(real);
      if (owner && owner.assetId !== asset.id) {
        const error = new Error(`文件同时属于 ${owner.assetId} 与 ${asset.id}：${real}。`);
        error.category = "artifact-ownership-collision";
        error.context = { file: real, assetIds: [owner.assetId, asset.id] };
        if (!tolerant) throw error;
        diagnostics.push({ assetId: asset.id, error });
      } else declaredEntries.set(real, { assetId: asset.id, rootType: index === 0 ? "entry" : "artifact" });
    }
  }
  const projections = new Map();
  const configuratorProjections = new Map();
  for (const asset of normalizedAssets) {
    try {
      const projection = await scanAssetFiles({ ...asset, source }, source, esbuild, declaredEntries);
      projections.set(asset.id, {
        ...projection,
        previewDigest: implementationPreviewDigest({ asset, files: projection.files })
      });
      if (asset.kind === "Template" && asset.configuration) {
        const configurator = await scanAssetFiles({ ...asset, entry: asset.configuration.configurator.entry, artifacts: [], source }, source, esbuild, declaredEntries);
        if (configurator.publicImports.length || configurator.importedAssets.length) fail("invalid-configurator-import", `${asset.id} 的 configurator 不得导入 Pack public asset。`, { assetId: asset.id });
        configuratorProjections.set(asset.id, configurator);
      }
    } catch (error) {
      if (!tolerant) throw error;
      diagnostics.push({ assetId: asset.id, error });
    }
  }
  const closureOwners = new Map();
  for (const asset of normalizedAssets) {
    const projection = projections.get(asset.id);
    if (!projection) continue;
    for (const file of projection.files) {
      const owner = closureOwners.get(file.sourcePath);
      if (owner && owner !== asset.id) {
        const error = new Error(`文件同时属于 ${owner} 与 ${asset.id}：${file.sourcePath}。`);
        error.category = "artifact-ownership-collision";
        error.context = { file: file.sourcePath, assetIds: [owner, asset.id] };
        if (!tolerant) throw error;
        diagnostics.push({ assetId: asset.id, error });
      } else closureOwners.set(file.sourcePath, asset.id);
    }
  }
  return { projections, configuratorProjections, diagnostics };
}

const reservedDescriptor = /^(knowledge|pattern|template|component)\.[a-z0-9]+(?:-[a-z0-9]+)*\.json$/;

const migrationReferenceDirectory = /^(?:migration-reference|migration-reference-v\d+|migration-reference-.+)$/;

async function discoverDescriptors(root, directory = root) {
  const discovered = [];
  for (const entry of (await readdir(directory, { withFileTypes: true })).sort((a, b) => a.name.localeCompare(b.name))) {
    const absolute = path.join(directory, entry.name);
    if (entry.isSymbolicLink()) fail("symlink-escape", `Pack 不允许符号链接：${absolute}。`, { path: absolute });
    if (entry.isDirectory() && migrationReferenceDirectory.test(entry.name)) fail("forbidden-migration-reference", `Pack root 内不允许 migration reference：${posixPath(path.relative(root, absolute))}。`, { path: posixPath(path.relative(root, absolute)) });
    if (entry.isDirectory()) discovered.push(...await discoverDescriptors(root, absolute));
    else if (entry.isFile() && reservedDescriptor.test(entry.name)) discovered.push(absolute);
  }
  return discovered.sort();
}

async function validatePublicContract(record) {
  if (!record.entry) return;
  const entryFile = path.resolve(path.dirname(record.descriptorFile), record.entry);
  const containedEntry = await containedRealPath(record.source.root, entryFile, { assetId: record.id, entry: record.entry });
  const mainExport = record.kind === "Template" ? record.authoring.mainExport : record.api.mainExport;
  const contract = await extractTypeScriptPublicContract({ entryFile: containedEntry, mainExport, sourceRoot: record.source.root });
  if (record.kind === "Template") validateTemplatePublicContract({ assetId: record.id, descriptorFile: record.descriptorPath, authoring: record.authoring, contract });
  if (record.kind === "Pack Component") validatePackComponentApi({ assetId: record.id, descriptorFile: record.descriptorPath, descriptorApi: record.api, contract });
  record.publicApi = projectTypeScriptPublicApi({ mainExport, contract });
  record.publicExports = contract.exports;
  record.publicRuntimeExports = contract.valueExports;
}

function errorDiagnostic(error, fallback = {}) {
  return {
    category: error?.category ?? "resolution-error",
    message: error?.message ?? String(error),
    context: { ...fallback, ...(error?.context ?? {}) }
  };
}

function descriptorPlaceholder({ id, descriptorPath, diagnostic }) {
  const prefix = typeof id === "string" ? id.split(".")[0] : null;
  const kind = new Map([["knowledge", "Knowledge"], ["pattern", "Pattern"], ["template", "Template"], ["component", "Pack Component"]]).get(prefix) ?? "Unknown";
  return {
    id: isCanonicalAssetId(id) ? id : null,
    kind,
    title: id ?? path.basename(descriptorPath, ".json"),
    abstract: "Invalid candidate asset.",
    descriptorPath,
    placeholder: true,
    valid: false,
    diagnostic
  };
}

function abstractProjection(record) {
  return { id: record.id, kind: record.kind, title: record.title, abstract: record.abstract };
}

function fullProjection(record) {
  const common = abstractProjection(record);
  if (record.kind === "Pattern" || record.kind === "Knowledge") return { ...common, content: record.content };
  if (record.kind === "Template") return {
    ...common,
    entry: record.entry,
    artifacts: [...record.artifacts],
    authoring: record.authoring,
    ...(record.configuration ? { configuration: record.configuration } : {}),
    publicApi: record.publicApi
  };
  return { ...common, entry: record.entry, artifacts: [...record.artifacts], api: record.api, usage: record.usage };
}

function validateManifestBindings({ manifest, records, tolerant = false, diagnostics = [], placeholders = new Map() }) {
  for (const [index, binding] of manifest.entrypoints.entries()) {
    const id = binding.assetLink;
    const target = records.get(id);
    if (target && !target.placeholder && target.kind === "Pattern") continue;
    const error = new Error(`entrypoint 只能引用当前 Pack Pattern：${id}。`);
    error.category = "invalid-entrypoint-target";
    error.context = { assetId: id, targetAssetId: id, targetKind: "Pattern", file: "manifest.json", pointer: `/entrypoints/${index}/assetLink` };
    if (!tolerant) throw error;
    const projected = errorDiagnostic(error);
    diagnostics.push(projected);
    if (isCanonicalAssetId(id) && !records.has(id) && !placeholders.has(id)) placeholders.set(id, descriptorPlaceholder({ id, descriptorPath: null, diagnostic: projected }));
  }
  for (const [index, binding] of manifest.review.entries()) {
    const id = binding.assetLink;
    const target = records.get(id);
    if (target && !target.placeholder && ["Pattern", "Knowledge"].includes(target.kind)) continue;
    const error = new Error(`review 只能引用当前 Pack Pattern 或 Knowledge：${id}。`);
    error.category = "invalid-review-target";
    error.context = { assetId: id, targetAssetId: id, targetKinds: ["Pattern", "Knowledge"], file: "manifest.json", pointer: `/review/${index}/assetLink` };
    if (!tolerant) throw error;
    const projected = errorDiagnostic(error);
    diagnostics.push(projected);
    if (isCanonicalAssetId(id) && !records.has(id) && !placeholders.has(id)) placeholders.set(id, descriptorPlaceholder({ id, descriptorPath: null, diagnostic: projected }));
  }
}

async function manifestProjection(manifestFile, tolerant) {
  let authored = null;
  try {
    authored = JSON.parse(await readFile(manifestFile, "utf8"));
  } catch (cause) {
    if (!tolerant) return { manifest: validateSourceManifest(await readJson(manifestFile, "invalid-source"), "manifest.json"), authored: null, diagnostic: null };
    const error = new Error(`manifest.json is not valid JSON: ${cause.message}`);
    error.category = "invalid-json";
    error.context = { file: "manifest.json", pointer: "" };
    return { manifest: null, authored: null, diagnostic: errorDiagnostic(error) };
  }
  try {
    return { manifest: validateSourceManifest(authored, "manifest.json"), authored, diagnostic: null };
  } catch (error) {
    if (!tolerant) throw error;
    return { manifest: null, authored, diagnostic: errorDiagnostic(error, { file: "manifest.json" }) };
  }
}

function tolerantManifest(authored, root) {
  const strings = (value) => Array.isArray(value) ? value.filter((item) => typeof item === "string") : [];
  const bindings = (value, prefixes) => {
    if (!Array.isArray(value)) return [];
    const seen = new Set();
    return value.flatMap((item) => {
      if (!item || typeof item !== "object" || Array.isArray(item) || typeof item.assetLink !== "string" || !isCanonicalAssetId(item.assetLink)) return [];
      if (!prefixes.some((prefix) => item.assetLink.startsWith(`${prefix}.`)) || (Object.hasOwn(item, "load") && item.load !== "full") || seen.has(item.assetLink)) return [];
      seen.add(item.assetLink);
      return [{ assetLink: item.assetLink, ...(item.load === "full" ? { load: "full" } : {}) }];
    });
  };
  return {
    schemaVersion: authored?.schemaVersion ?? null,
    id: typeof authored?.id === "string" ? authored.id : path.basename(root),
    version: typeof authored?.version === "string" ? authored.version : null,
    entrypoints: bindings(authored?.entrypoints, ["pattern"]),
    review: bindings(authored?.review, ["pattern", "knowledge"]),
    runtimeTheme: { artifacts: strings(authored?.runtimeTheme?.artifacts) }
  };
}

function projectManifestBindingRecords(authored, stage, allowedPrefixes) {
  if (!Array.isArray(authored?.[stage])) return [];
  const seen = new Map();
  return authored[stage].map((rawBinding, index) => {
    const pointer = `/${stage}/${index}`;
    const context = { file: "manifest.json", pointer };
    let category = null;
    let message = null;
    let assetLink = null;
    let load = null;
    if (!rawBinding || typeof rawBinding !== "object" || Array.isArray(rawBinding)) {
      category = stage === "entrypoints" ? "invalid-entrypoints" : "invalid-review-target";
      message = `${stage}[${index}] 必须是 binding object。`;
    } else {
      const extra = Object.keys(rawBinding).filter((key) => !["assetLink", "load"].includes(key));
      if (extra.length) {
        category = "unknown-field";
        message = `${stage}[${index}] 包含未知字段：${extra.join("、")}。`;
        context.pointer = `${pointer}/${extra[0]}`;
      } else if (typeof rawBinding.assetLink !== "string" || !isCanonicalAssetId(rawBinding.assetLink)) {
        category = stage === "entrypoints" ? "invalid-entrypoints" : "invalid-review-target";
        message = `${stage}[${index}].assetLink 无效。`;
        context.pointer = `${pointer}/assetLink`;
      } else {
        assetLink = rawBinding.assetLink;
        if (!allowedPrefixes.some((prefix) => assetLink.startsWith(`${prefix}.`))) {
          category = stage === "entrypoints" ? "invalid-entrypoints" : "invalid-review-target";
          message = `${stage}[${index}] target kind 无效：${assetLink}。`;
          context.pointer = `${pointer}/assetLink`;
        } else if (Object.hasOwn(rawBinding, "load") && rawBinding.load !== "full") {
          category = stage === "entrypoints" ? "invalid-entrypoints" : "invalid-review-target";
          message = `${stage}[${index}].load 只允许 full。`;
          context.pointer = `${pointer}/load`;
        } else if (seen.has(assetLink)) {
          category = stage === "entrypoints" ? "invalid-entrypoints" : "invalid-review-target";
          message = `${stage} 重复 target：${assetLink}。`;
          context.pointer = `${pointer}/assetLink`;
          context.duplicateOf = seen.get(assetLink);
        } else {
          seen.set(assetLink, index);
          load = rawBinding.load === "full" ? "full" : null;
        }
      }
    }
    const valid = category === null;
    return {
      stage,
      index,
      pointer,
      rawBinding,
      ...(assetLink ? { assetLink } : {}),
      ...(load ? { load } : {}),
      valid,
      resolutionEligible: valid,
      ...(valid ? {} : { diagnostic: { category, message, context: { ...context, ...(assetLink ? { targetAssetId: assetLink } : {}) } } })
    };
  });
}

function resolveSemanticLinks({ records, tolerant, diagnostics, placeholders }) {
  const links = [];
  for (const record of records.values()) {
    if (record.placeholder) continue;
    record.assetLinks = collectAssetLinks(record, record.descriptorPath);
    for (const link of record.assetLinks) {
      const target = records.get(link.target);
      if (target && !target.placeholder) {
        links.push(link);
        continue;
      }
      const error = new Error(`${record.id} 的 assetLink 在当前 Pack 中缺少目标：${link.target}。`);
      error.category = "broken-asset-link";
      error.context = { assetId: record.id, file: record.descriptorPath, pointer: link.pointer, targetAssetId: link.target };
      if (!tolerant) throw error;
      const diagnostic = errorDiagnostic(error);
      diagnostics.push(diagnostic);
      if (!placeholders.has(link.target)) placeholders.set(link.target, descriptorPlaceholder({ id: link.target, descriptorPath: null, diagnostic }));
      links.push(link);
    }
  }
  return links;
}

export function projectContextClosure({ records: recordValues = [], fullAssetIds: configuredFullIds = [], abstractAssetIds: configuredAbstractIds = [], includeUnresolved = false } = {}) {
  const records = new Map(recordValues.filter((record) => record?.id).map((record) => [record.id, record]));
  const fullIds = [];
  const fullSet = new Set();
  const queue = [];
  const enqueueFull = (id) => {
    if (fullSet.has(id) || (!includeUnresolved && !records.has(id))) return;
    fullSet.add(id);
    fullIds.push(id);
    queue.push(id);
  };
  const abstractIds = [];
  const abstractSet = new Set();
  const enqueueAbstract = (id) => {
    if (fullSet.has(id) || abstractSet.has(id) || (!includeUnresolved && !records.has(id))) return;
    abstractSet.add(id);
    abstractIds.push(id);
  };
  for (const id of configuredFullIds) enqueueFull(id);
  for (const id of configuredAbstractIds) enqueueAbstract(id);
  while (queue.length) {
    const sourceId = queue.shift();
    const record = records.get(sourceId);
    for (const link of record?.assetLinks ?? []) {
      if (link.load === "full") enqueueFull(link.target);
      else enqueueAbstract(link.target);
    }
  }
  return {
    fullAssetIds: fullIds,
    linkedAbstractAssetIds: abstractIds.filter((id) => !fullSet.has(id))
  };
}

export function projectDisclosureClosure({ records = [], assetIds = [], includeUnresolved = false } = {}) {
  return projectContextClosure({ records, fullAssetIds: assetIds, includeUnresolved });
}

export function resolveStageContextPacket({ resolution, bindings = [] }) {
  if (resolution?.report?.status !== "resolved") fail("pack-authority-invalid", "Stage Context Packet requires one strictly resolved current Pack.", { status: resolution?.report?.status ?? null });
  const records = new Map((resolution.records ?? []).filter((record) => record?.id && !record.placeholder).map((record) => [record.id, record]));
  const fullRoots = bindings.filter((binding) => binding.load === "full").map((binding) => binding.assetLink);
  const abstractRoots = bindings.filter((binding) => binding.load !== "full").map((binding) => binding.assetLink);
  const { fullAssetIds, linkedAbstractAssetIds } = projectContextClosure({ records: [...records.values()], fullAssetIds: fullRoots, abstractAssetIds: abstractRoots });
  return {
    fullAssets: fullAssetIds.map((id) => fullProjection(records.get(id))),
    linkedAbstracts: linkedAbstractAssetIds.map((id) => abstractProjection(records.get(id)))
  };
}

export function resolveContextPacket({ resolution, assetIds }) {
  if (resolution?.report?.status !== "resolved") fail("pack-authority-invalid", "Context Packet requires one strictly resolved current Pack.", { status: resolution?.report?.status ?? null });
  const records = new Map((resolution.records ?? []).filter((record) => record?.id && !record.placeholder).map((record) => [record.id, record]));
  const requested = Array.isArray(assetIds) ? assetIds : [];
  const seenRequests = new Set();
  const active = [];
  const failures = [];
  for (const [requestIndex, requestedAssetId] of requested.entries()) {
    if (seenRequests.has(requestedAssetId)) continue;
    seenRequests.add(requestedAssetId);
    if (!isCanonicalAssetId(requestedAssetId)) {
      failures.push({ requestIndex, requestedAssetId, category: "invalid-asset-id", message: "The requested asset ID is invalid." });
      continue;
    }
    if (!records.has(requestedAssetId)) {
      failures.push({ requestIndex, requestedAssetId, category: "missing-asset", message: "The requested asset does not exist in the current Pack." });
      continue;
    }
    active.push(requestedAssetId);
  }
  if (!active.length) fail("expand-no-valid-requests", "No requested asset can be expanded.", { failures });

  const { fullAssetIds, linkedAbstractAssetIds } = projectContextClosure({ records: [...records.values()], fullAssetIds: active });
  return {
    status: failures.length ? "partial" : "success",
    fullAssets: fullAssetIds.map((id) => fullProjection(records.get(id))),
    linkedAbstracts: linkedAbstractAssetIds.map((id) => abstractProjection(records.get(id))),
    ...(failures.length ? { failures } : {})
  };
}

export async function resolveSources({ bundledPack, esbuild, tolerant = false }) {
  const root = await realpath(path.resolve(bundledPack));
  const manifestFile = path.join(root, "manifest.json");
  if (!(await exists(manifestFile))) fail("source-unavailable", "Installed Pack manifest is unavailable.", { root });
  const manifestResult = await manifestProjection(manifestFile, tolerant);
  const manifest = manifestResult.manifest ?? tolerantManifest(manifestResult.authored, root);
  const source = { reference: `pack:${manifest.id}`, root, manifest, manifestFile };
  const records = new Map();
  const diagnostics = manifestResult.diagnostic ? [manifestResult.diagnostic] : [];
  const manifestBindingRecords = {
    entrypoints: projectManifestBindingRecords(manifestResult.authored ?? manifest, "entrypoints", ["pattern"]),
    review: projectManifestBindingRecords(manifestResult.authored ?? manifest, "review", ["pattern", "knowledge"])
  };
  if (tolerant) diagnostics.push(...Object.values(manifestBindingRecords).flat().filter((record) => !record.valid).map((record) => record.diagnostic));
  const placeholders = new Map();
  for (const descriptorFile of await discoverDescriptors(root)) {
    const descriptorPath = posixPath(path.relative(root, descriptorFile));
    try {
      const descriptor = validateAssetDescriptor(await readJson(descriptorFile, "invalid-json"), descriptorPath);
      if (path.basename(descriptorFile, ".json") !== descriptor.id) fail("descriptor-identity-mismatch", `descriptor basename 与内部 ID 不一致：${descriptorPath}。`, { id: descriptor.id, file: descriptorPath, pointer: "/id" });
      if (records.has(descriptor.id)) fail("asset-id-collision", `资产 ID 冲突：${descriptor.id}。`, { assetId: descriptor.id, file: descriptorPath });
      const record = { ...descriptor, descriptorFile, descriptorPath, source, valid: true };
      record.descriptorSha256 = sha256(await readFile(descriptorFile));
      records.set(record.id, record);
    } catch (error) {
      if (!tolerant) throw error;
      const basenameId = path.basename(descriptorFile, ".json");
      const diagnostic = errorDiagnostic(error, { assetId: isCanonicalAssetId(basenameId) ? basenameId : null, file: descriptorPath });
      diagnostics.push(diagnostic);
      const placeholder = descriptorPlaceholder({ id: basenameId, descriptorPath, diagnostic });
      if (placeholder.id) {
        records.set(placeholder.id, placeholder);
        placeholders.set(placeholder.id, placeholder);
      }
    }
  }

  validateManifestBindings({ manifest, records, tolerant, diagnostics, placeholders });
  const links = resolveSemanticLinks({ records, tolerant, diagnostics, placeholders });

  for (const record of records.values()) {
    if (record.placeholder || !record.entry) continue;
    try { await validatePublicContract(record); }
    catch (error) {
      if (!tolerant) throw error;
      diagnostics.push(errorDiagnostic(error, { assetId: record.id, file: record.descriptorPath }));
      record.valid = false;
    }
  }
  for (const record of records.values()) {
    if (!record.placeholder && (record.kind === "Pattern" || record.kind === "Knowledge")) record.contentRenderProjection = projectContentGfm(record.content);
  }
  const implementations = await projectAssetImplementationClosures({
    packRoot: root,
    assets: [...records.values()].filter((record) => !record.placeholder && record.entry),
    esbuild,
    tolerant
  });
  diagnostics.push(...implementations.diagnostics.map(({ assetId, error }) => errorDiagnostic(error, { assetId })));
  for (const record of records.values()) {
    if (record.placeholder) continue;
    const scan = implementations.projections.get(record.id);
    if (!record.entry) {
      record.files = [];
      record.configuratorFiles = [];
      record.publicImports = [];
      record.publicImportDependencies = [];
    } else if (!scan) {
      record.files = [];
      record.publicImports = [];
      record.publicImportDependencies = [];
      record.valid = false;
      continue;
    } else {
      if (scan.entryRuntimeExports && JSON.stringify(scan.entryRuntimeExports) !== JSON.stringify(record.publicRuntimeExports)) {
        const error = new Error(`${record.id} 的 public entry runtime exports 与 TypeScript contract 不一致。`);
        error.category = "public-export-mismatch";
        error.context = { assetId: record.id, expected: record.publicRuntimeExports, actual: scan.entryRuntimeExports };
        if (!tolerant) throw error;
        diagnostics.push(errorDiagnostic(error));
        record.valid = false;
      }
      record.files = scan.files;
      record.publicImports = scan.publicImports;
      record.publicImportDependencies = scan.importedAssets;
      record.configuratorFiles = record.configuration ? (implementations.configuratorProjections.get(record.id)?.files ?? []) : [];
      if (record.configuration && !implementations.configuratorProjections.has(record.id)) {
        record.valid = false;
        continue;
      }
    }
    record.implementationDependencies = [...record.publicImportDependencies];
    const fileProjection = record.files.map(({ snapshotPath, sha256: digest }) => ({ snapshotPath, sha256: digest }));
    record.identityDigest = digestObject({ id: record.id, kind: record.kind });
    record.semanticDigest = digestObject({ title: record.title, abstract: record.abstract, content: record.content ?? null, authoring: record.authoring ?? null, api: record.api ?? null, usage: record.usage ?? null });
    record.implementationDigest = digestObject({ files: fileProjection, configuratorFiles: record.configuratorFiles?.map(({ snapshotPath, sha256: digest }) => ({ snapshotPath, sha256: digest })) ?? [] });
    record.guidanceDigest = digestObject({ abstract: record.abstract, content: record.content ?? null });
    record.templateSourceDigest = record.kind === "Template" ? digestObject({ source: scan?.previewDigest ?? null, configuration: record.configuration ?? null, configuratorFiles: record.configuratorFiles?.map(({ snapshotPath, sha256: digest }) => ({ snapshotPath, sha256: digest })) ?? [] }) : null;
    record.componentContractDigest = record.kind === "Pack Component" ? scan?.previewDigest ?? null : null;
    record.recordDigest = digestObject({ descriptorSha256: record.descriptorSha256, identityDigest: record.identityDigest, semanticDigest: record.semanticDigest, implementationDigest: record.implementationDigest });
  }

  for (const record of records.values()) for (const dependency of record.publicImportDependencies ?? []) {
    const target = records.get(dependency);
    if (!target || target.placeholder || target.kind !== "Pack Component") {
      const error = new Error(`${record.id} 的 public import 必须指向当前 Pack Component：${dependency}。`);
      error.category = "invalid-public-import";
      error.context = { assetId: record.id, targetAssetId: dependency, chain: [record.id, dependency] };
      if (!tolerant) throw error;
      diagnostics.push(errorDiagnostic(error));
      record.valid = false;
    }
  }

  const requiredThemeBasenames = [...canonicalRuntimeThemeArtifactBasenames].sort();
  const runtimeThemeArtifacts = [];
  const declaredThemeBasenames = manifest.runtimeTheme.artifacts.map((artifact) => path.posix.basename(artifact)).sort();
  if (JSON.stringify(declaredThemeBasenames) !== JSON.stringify(requiredThemeBasenames)) {
    const error = new Error("runtimeTheme 必须且只能声明三个 canonical generated artifacts。");
    error.category = "invalid-runtime-theme";
    error.context = { file: "manifest.json", pointer: "/runtimeTheme/artifacts", expected: requiredThemeBasenames, actual: declaredThemeBasenames };
    if (!tolerant) throw error;
    diagnostics.push(errorDiagnostic(error));
  }
  for (const [index, artifact] of manifest.runtimeTheme.artifacts.entries()) {
    try {
      const file = await containedRealPath(root, path.join(root, artifact), { file: "manifest.json", pointer: `/runtimeTheme/artifacts/${index}`, artifact });
      const info = await lstat(file);
      if (info.isSymbolicLink() || !info.isFile()) fail("invalid-runtime-theme", `runtimeTheme artifact 必须是 contained regular file：${artifact}。`, { file: "manifest.json", pointer: `/runtimeTheme/artifacts/${index}`, artifact });
      const contents = await readFile(file);
      runtimeThemeArtifacts.push({ path: posixPath(artifact), name: path.basename(artifact), sha256: sha256(contents), contents });
    } catch (error) {
      if (!tolerant) throw error;
      diagnostics.push(errorDiagnostic(error, { file: "manifest.json", pointer: `/runtimeTheme/artifacts/${index}`, artifact }));
    }
  }
  runtimeThemeArtifacts.sort((a, b) => a.name.localeCompare(b.name));

  let uiConfig = null;
  if (manifest.uiConfig) {
    const stylesheet = manifest.uiConfig.stylesheet;
    try {
      const file = await containedRealPath(root, path.join(root, stylesheet), { file: "manifest.json", pointer: "/uiConfig/stylesheet", stylesheet });
      const info = await lstat(file);
      if (info.isSymbolicLink() || !info.isFile()) fail("invalid-ui-config", `uiConfig.stylesheet 必须是 Pack 内普通文件：${stylesheet}。`, { file: "manifest.json", pointer: "/uiConfig/stylesheet", stylesheet });
      const contents = await readFile(file);
      uiConfig = { stylesheet: posixPath(stylesheet), antdVersion: manifest.uiConfig.antdVersion, sha256: sha256(contents), contents };
    } catch (error) {
      if (!tolerant) throw error;
      diagnostics.push(errorDiagnostic(error, { file: "manifest.json", pointer: "/uiConfig/stylesheet", stylesheet }));
    }
  }

  const selectedRecords = [...records.values()].filter((record) => !record.placeholder).sort((a, b) => a.id.localeCompare(b.id));
  const closureIds = selectedRecords.map((record) => record.id);
  const projection = [
    ...links.map((link) => ({ source: link.source, target: link.target, type: "assetLink", load: link.load, pointer: link.pointer })),
    ...selectedRecords.flatMap((record) => (record.publicImportDependencies ?? []).map((target) => ({ source: record.id, target, type: "public-import" })))
  ];
  const catalog = [...selectedRecords.map((record) => ({ ...abstractProjection(record), recordDigest: record.recordDigest })), ...placeholders.values()].sort((a, b) => a.kind.localeCompare(b.kind) || (a.id ?? a.title).localeCompare(b.id ?? b.title));
  const reachable = new Set([
    "manifest.json",
    ...runtimeThemeArtifacts.map((artifact) => artifact.path),
    ...(uiConfig ? [uiConfig.stylesheet] : []),
    ...selectedRecords.map((record) => record.descriptorPath),
    ...selectedRecords.flatMap((record) => record.files.map((file) => file.sourcePath)),
    ...selectedRecords.flatMap((record) => (record.configuratorFiles ?? []).map((file) => file.sourcePath))
  ]);
  const formalFiles = [];
  const collectFiles = async (directory = root) => {
    for (const entry of (await readdir(directory, { withFileTypes: true })).sort((a, b) => a.name.localeCompare(b.name))) {
      const absolute = path.join(directory, entry.name);
      if (entry.isSymbolicLink()) fail("symlink-escape", `Pack 不允许符号链接：${absolute}。`, { path: absolute });
      if (entry.isDirectory()) await collectFiles(absolute);
      else if (entry.isFile()) formalFiles.push(posixPath(path.relative(root, absolute)));
      else fail("invalid-pack-object", `Pack 包含不支持的对象：${absolute}。`, { path: absolute });
    }
  };
  await collectFiles();
  const unreachable = formalFiles.filter((file) => !reachable.has(file));
  if (unreachable.length && !tolerant) fail("unreachable-pack-file", `正式 Pack 包含公共消费不可达文件：${unreachable.join("、")}。`, { files: unreachable });
  if (unreachable.length && tolerant) diagnostics.push({ category: "unreachable-pack-file", message: `Candidate Pack 包含不可达文件：${unreachable.join("、")}。`, context: { files: unreachable } });
  const packFiles = {};
  for (const file of [...reachable].sort()) if (await exists(path.join(root, file))) packFiles[file] = sha256(await readFile(path.join(root, file)));
  const packDigest = digestObject(packFiles);
  const manifestBindings = {
    entrypoints: manifestBindingRecords.entrypoints.filter((record) => record.resolutionEligible).map(({ assetLink, load, pointer }) => ({ assetLink, ...(load ? { load } : {}), pointer })),
    review: manifestBindingRecords.review.filter((record) => record.resolutionEligible).map(({ assetLink, load, pointer }) => ({ assetLink, ...(load ? { load } : {}), pointer }))
  };
  return {
    schemaVersion: 3,
    manifest: manifestResult.manifest ? { ...manifest, valid: true, placeholder: false } : { ...manifest, valid: false, placeholder: true, diagnostic: manifestResult.diagnostic },
    pack: { id: manifest.id, version: manifest.version, digest: packDigest },
    sources: [{ id: manifest.id, type: "pack", reference: source.reference, version: manifest.version, digest: packDigest, available: true }],
    roots: manifestBindings.entrypoints.map((binding) => binding.assetLink),
    closure: closureIds,
    projection,
    manifestBindings,
    manifestBindingRecords,
    records: selectedRecords,
    catalog,
    placeholders: [...placeholders.values()],
    entrypoints: manifestBindings.entrypoints,
    review: manifestBindings.review,
    runtimeTheme: { artifacts: runtimeThemeArtifacts },
    ...(uiConfig ? { uiConfig } : {}),
    packFiles,
    report: { schemaVersion: 3, status: diagnostics.length ? "editing" : "resolved", roots: manifestBindings.entrypoints.map((binding) => binding.assetLink), closure: closureIds, diagnostics }
  };
}
