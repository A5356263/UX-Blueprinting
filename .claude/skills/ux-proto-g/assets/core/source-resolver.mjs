import { lstat, readFile, readdir, realpath, stat } from "node:fs/promises";
import path from "node:path";
import { digestObject, exists, fail, posixPath, readJson, sha256, uniqueSorted } from "./common.mjs";
import { validateAssetDescriptor, validateSourceManifest } from "./contracts.mjs";
import { extractTypeScriptPublicContract, validatePackComponentApi } from "./typescript-public-contract.mjs";

const jsExtensions = ["", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json", ".css"];
const codeExtensions = new Set([".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"]);
const cssExtensions = new Set([".css"]);
const runtimeImports = new Set(["react", "react/jsx-runtime", "react/jsx-dev-runtime", "react-dom", "react-dom/client", "antd"]);
const publicPrefix = "@ux-proto/assets/";

function lexModuleReferences(source, file, chain) {
  const tokens = [];
  let index = 0;
  const push = (type, value) => tokens.push({ type, value });
  const regexPrefixKeywords = new Set(["await", "case", "delete", "do", "else", "in", "instanceof", "new", "return", "throw", "typeof", "void", "yield"]);
  const regexPrefixPunctuators = new Set(["(", "[", "{", ",", ";", ":", "=", "!", "?", "&", "|", "+", "-", "*", "%", "^", "~", "<", ">"]);
  const regexAllowed = () => {
    const previous = tokens.at(-1);
    return !previous || (previous.type === "identifier" ? regexPrefixKeywords.has(previous.value) : regexPrefixPunctuators.has(previous.value));
  };
  const skipQuoted = (quote, emit) => {
    let value = "";
    index += 1;
    while (index < source.length && source[index] !== quote) {
      if (source[index] === "\\" && index + 1 < source.length) { value += source[index + 1]; index += 2; }
      else { value += source[index]; index += 1; }
    }
    if (index < source.length) index += 1;
    if (emit) push("string", value);
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
      let end = index + 1;
      while (end < source.length && /[A-Za-z0-9_$-]/.test(source[end])) end += 1;
      push("identifier", source.slice(index, end));
      index = end;
      continue;
    }
    if (templateExpression && char === "}") {
      if (braceDepth === 0) { index += 1; return; }
      braceDepth -= 1;
    } else if (templateExpression && char === "{") braceDepth += 1;
    push("punctuator", char);
    index += 1;
    }
  };
  scanCode();
  const findFrom = (cursor) => {
    for (let look = cursor; look < tokens.length; look += 1) {
      if (tokens[look].value === ";") return null;
      if (tokens[look].value === "from" && tokens[look + 1]?.type === "string") return tokens[look + 1].value;
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
  const add = (specifier, kind) => references.push({ specifier, kind });
  for (let cursor = 0; cursor < tokens.length; cursor += 1) {
    const token = tokens[cursor];
    if (token.type !== "identifier") continue;
    if (isMemberAccess(cursor) || isMethodKey(cursor)) continue;
    if (token.value === "require" && tokens[cursor + 1]?.value === "(") add(tokens[cursor + 2]?.type === "string" ? tokens[cursor + 2].value : "<nonliteral>", "require-call");
    if (token.value === "import") {
      if (tokens[cursor + 1]?.value === "(") {
        if (tokens[cursor + 2]?.type !== "string" || tokens[cursor + 3]?.value !== ")") fail("nonliteral-dynamic-import", `不允许非字面量 dynamic import：${file}。`, { file, chain });
        add(tokens[cursor + 2].value, "dynamic-import");
        continue;
      }
      if (tokens[cursor + 1]?.type === "string") add(tokens[cursor + 1].value, "import-statement");
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

async function parseCode(file, esbuild, chain) {
  if (!esbuild?.build) fail("runtime-unavailable", "固定 runtime 中缺少 JS/TS parser。", { chain });
  const source = await readFile(file, "utf8");
  const lexicalImports = lexModuleReferences(source, file, chain);
  let result;
  try {
    result = await esbuild.build({
      stdin: { contents: source, sourcefile: path.basename(file), resolveDir: path.dirname(file), loader: path.extname(file).slice(1).replace("mjs", "js").replace("cjs", "js") || "js" },
      bundle: true,
      format: "esm",
      write: false,
      metafile: true,
      logLevel: "silent",
      treeShaking: false,
      plugins: [{ name: "ux-proto-scan-only", setup(build) { build.onResolve({ filter: /.*/ }, (args) => args.kind === "entry-point" ? undefined : ({ path: args.path, external: true })); } }]
    });
  } catch (error) {
    fail("source-parse-error", `无法解析 ${file}：${error.errors?.[0]?.text ?? error.message}。`, { file, chain });
  }
  const input = Object.values(result.metafile.inputs)[0];
  const outputs = Object.values(result.metafile.outputs ?? {});
  const output = outputs.find((item) => item.exports?.length) ?? outputs.find((item) => item.entryPoint) ?? outputs[0];
  const runtimeImports = (input?.imports ?? []).map(({ path: specifier, kind }) => ({ specifier, kind }));
  return {
    imports: [...new Map([...lexicalImports, ...runtimeImports].map((item) => [`${item.kind}\0${item.specifier}`, item])).values()],
    exports: Array.isArray(output?.exports) ? [...output.exports].sort() : null
  };
}

function parseCss(source, file, chain) {
  const imports = [];
  for (const match of source.matchAll(/@import\s+(?:url\(\s*)?["']([^"']+)["']/g)) imports.push(match[1]);
  for (const match of source.matchAll(/url\(\s*["']?([^"')]+)["']?\s*\)/g)) if (!match[1].startsWith("data:") && !match[1].startsWith("#")) imports.push(match[1]);
  for (const specifier of imports) if (/^(?:https?:)?\/\//.test(specifier)) fail("external-artifact", `CSS 不允许外部 URL：${specifier}。`, { file, chain });
  return uniqueSorted(imports);
}

async function scanAssetFiles(asset, source, esbuild, declaredEntries) {
  const descriptorDirectory = path.dirname(asset.descriptorFile);
  const pending = uniqueSorted([asset.entry, ...(asset.artifacts ?? [])].filter(Boolean)).map((relative) => path.resolve(descriptorDirectory, relative));
  const visited = new Set();
  const files = [];
  const importedAssets = new Set();
  let entryRuntimeExports = null;
  while (pending.length) {
    const candidate = pending.shift();
    const file = await containedRealPath(source.root, candidate, { assetId: asset.id, chain: [asset.id, posixPath(path.relative(source.root, candidate))] });
    if (visited.has(file)) continue;
    const otherOwner = declaredEntries.get(file);
    if (otherOwner && otherOwner !== asset.id) fail("cross-asset-relative-import", `${asset.id} 不能通过相对路径导入 ${otherOwner}。`, { chain: [asset.id, otherOwner], file });
    visited.add(file);
    const relativeToDescriptor = posixPath(path.relative(descriptorDirectory, file));
    const relativeToSource = posixPath(path.relative(source.root, file));
    const contents = await readFile(file);
    files.push({ sourcePath: relativeToSource, snapshotPath: `files/${asset.id}/${relativeToDescriptor}`, sha256: sha256(contents), contents });
    const extension = path.extname(file).toLowerCase();
    let imports = [];
    if (codeExtensions.has(extension)) {
      const parsed = await parseCode(file, esbuild, [asset.id, relativeToDescriptor]);
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
  return { files: files.sort((a, b) => a.snapshotPath.localeCompare(b.snapshotPath)), importedAssets: uniqueSorted([...importedAssets]), entryRuntimeExports };
}

const reservedDescriptor = /^(knowledge|pattern|template|component)\.[a-z0-9]+(?:-[a-z0-9]+)*\.json$/;

async function discoverDescriptors(root, directory = root) {
  const discovered = [];
  for (const entry of (await readdir(directory, { withFileTypes: true })).sort((a, b) => a.name.localeCompare(b.name))) {
    const absolute = path.join(directory, entry.name);
    if (entry.isSymbolicLink()) fail("symlink-escape", `Pack 不允许符号链接：${absolute}。`, { path: absolute });
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
  if (record.kind === "Template") {
    const publicProps = new Set(contract.properties.map((row) => row.name));
    for (const surface of record.authoring.customizationSurfaces) {
      if (!publicProps.has(surface.binding.name)) fail("template-prop-binding-mismatch", `${record.id} 的 prop binding 不属于 mainExport 公开输入：${surface.binding.name}。`, { assetId: record.id, mainExport, propsType: contract.propsType, prop: surface.binding.name });
    }
  }
  if (record.kind === "Pack Component") validatePackComponentApi({ assetId: record.id, descriptorApi: record.api, contract });
  record.publicExports = contract.exports;
  record.publicRuntimeExports = contract.valueExports;
}

export async function resolveSources({ bundledPack, esbuild }) {
  const root = await realpath(path.resolve(bundledPack));
  const manifestFile = path.join(root, "manifest.json");
  if (!(await exists(manifestFile))) fail("source-unavailable", "固定 bundled Pack 不可用。", { root });
  const manifest = validateSourceManifest(await readJson(manifestFile, "invalid-source"), manifestFile);
  if (manifest.type !== "pack") fail("source-identity-mismatch", "固定 bundled source 必须是 Pack。", { actual: manifest.type });
  const source = { reference: `pack:${manifest.id}`, root, manifest, manifestFile };
  const records = new Map();
  const declaredEntries = new Map();
  for (const descriptorFile of await discoverDescriptors(root)) {
    const descriptor = validateAssetDescriptor(await readJson(descriptorFile, "invalid-asset"), descriptorFile);
    if (path.basename(descriptorFile, ".json") !== descriptor.id) fail("descriptor-identity-mismatch", `descriptor basename 与内部 ID 不一致：${descriptorFile}。`, { id: descriptor.id });
    if (records.has(descriptor.id)) fail("asset-id-collision", `资产 ID 冲突：${descriptor.id}。`, { assetId: descriptor.id });
    const record = { ...descriptor, descriptorFile, descriptorPath: posixPath(path.relative(root, descriptorFile)), source };
    record.descriptorSha256 = sha256(await readFile(descriptorFile));
    records.set(record.id, record);
    for (const relative of [record.entry, ...(record.artifacts ?? [])].filter(Boolean)) {
      const absolute = path.resolve(path.dirname(descriptorFile), relative);
      const real = await realpath(absolute).catch(() => absolute);
      const owner = declaredEntries.get(real);
      if (owner && owner !== record.id) fail("artifact-ownership-collision", `文件同时属于 ${owner} 与 ${record.id}。`, { file: real });
      declaredEntries.set(real, record.id);
    }
  }

  for (const record of records.values()) {
    await validatePublicContract(record);
    const scan = await scanAssetFiles(record, record.source, esbuild, declaredEntries);
    if (scan.entryRuntimeExports && JSON.stringify(scan.entryRuntimeExports) !== JSON.stringify(record.publicRuntimeExports)) {
      fail("public-export-mismatch", `${record.id} 的 public entry runtime exports 与 TypeScript contract 不一致。`, { assetId: record.id, expected: record.publicRuntimeExports, actual: scan.entryRuntimeExports });
    }
    record.files = scan.files;
    record.publicImportDependencies = scan.importedAssets;
    record.hardDependencies = uniqueSorted([
      ...record.requires,
      ...record.relations.filter((relation) => relation.type === "requires").map((relation) => relation.target),
      ...scan.importedAssets
    ]);
    record.softRelations = record.relations.filter((relation) => relation.type !== "requires");
    const fileProjection = record.files.map(({ snapshotPath, sha256: digest }) => ({ snapshotPath, sha256: digest }));
    record.identityDigest = digestObject({ id: record.id, kind: record.kind, lifecycle: record.lifecycle, hardDependencies: record.hardDependencies });
    record.semanticDigest = digestObject({ summary: record.summary, content: record.content ?? null, selection: record.selection, relations: record.softRelations, authoring: record.authoring ?? null, api: record.api ?? null, usage: record.usage ?? null });
    record.implementationDigest = digestObject(fileProjection);
    record.guidanceDigest = digestObject({ summary: record.summary, selection: record.selection, relations: record.softRelations, requires: record.hardDependencies, content: record.content ?? null });
    record.templateSourceDigest = record.kind === "Template" ? digestObject({ authoring: record.authoring, files: fileProjection }) : null;
    record.componentContractDigest = record.kind === "Pack Component" ? digestObject({ api: record.api, usage: record.usage, files: fileProjection }) : null;
    record.recordDigest = digestObject({ descriptorSha256: record.descriptorSha256, identityDigest: record.identityDigest, semanticDigest: record.semanticDigest, implementationDigest: record.implementationDigest });
  }

  for (const record of records.values()) for (const dependency of record.publicImportDependencies) {
    const target = records.get(dependency);
    if (!target || target.kind !== "Pack Component") fail("invalid-public-import", `${record.id} 的 public import 必须指向 Pack Component：${dependency}。`, { chain: [record.id, dependency] });
  }

  const validatePackAsset = (record, chain = [], visiting = new Set()) => {
    if (visiting.has(record.id)) fail("dependency-cycle", `Pack 硬依赖形成循环：${[...chain, record.id].join(" → ")}。`, { chain: [...chain, record.id] });
    const next = new Set(visiting); next.add(record.id);
    for (const dependencyId of record.hardDependencies) {
      const dependency = records.get(dependencyId);
      if (!dependency) fail("broken-closure", `Pack 依赖链缺少资产 ${dependencyId}：${[...chain, record.id, dependencyId].join(" → ")}。`, { chain: [...chain, record.id, dependencyId] });
      if (dependency.lifecycle === "deprecated") fail("deprecated-in-closure", `Pack 新闭包不能依赖 deprecated 资产：${[...chain, record.id, dependencyId].join(" → ")}。`, { chain: [...chain, record.id, dependencyId] });
      if (record.lifecycle === "active" && dependency.lifecycle === "draft") fail("active-depends-on-draft", `active Pack 资产不能依赖 draft：${[...chain, record.id, dependencyId].join(" → ")}。`, { chain: [...chain, record.id, dependencyId] });
      validatePackAsset(dependency, [...chain, record.id], next);
    }
  };
  for (const record of records.values()) validatePackAsset(record);

  for (const recommendation of manifest.consumption.recommendations) {
    const target = records.get(recommendation.assetId);
    if (!target || target.lifecycle !== "active") fail("invalid-recommendation-target", `${recommendation.id} 指向不存在或非 active 的资产。`, recommendation);
  }
  const reviewIds = manifest.consumption.review.assets;
  if (new Set(reviewIds).size !== reviewIds.length) fail("invalid-review-target", "review Knowledge ID 必须唯一。");
  for (const id of reviewIds) {
    const target = records.get(id);
    if (!target || target.lifecycle !== "active" || target.kind !== "Knowledge") fail("invalid-review-target", `review 只能引用 active Knowledge：${id}。`, { assetId: id });
  }
  const baselineFile = await containedRealPath(root, path.join(root, manifest.consumption.baseline.artifact), { artifact: manifest.consumption.baseline.artifact });
  const baselineContent = await readFile(baselineFile, "utf8");
  const baseline = { id: manifest.consumption.baseline.id, content: baselineContent, digest: `sha256:${sha256(baselineContent)}` };

  const requiredThemeBasenames = ["alias-vars.generated.css", "antd.generated.css", "theme-config.generated.mjs"];
  const runtimeThemeArtifacts = [];
  if (manifest.runtimeTheme) {
    const declaredThemeBasenames = manifest.runtimeTheme.artifacts.map((artifact) => path.posix.basename(artifact)).sort();
    if (JSON.stringify(declaredThemeBasenames) !== JSON.stringify(requiredThemeBasenames)) fail("invalid-runtime-theme", "runtimeTheme 若存在，必须且只能声明三个 canonical generated artifacts。", { expected: requiredThemeBasenames, actual: declaredThemeBasenames });
    for (const artifact of manifest.runtimeTheme.artifacts) {
      const file = await containedRealPath(root, path.join(root, artifact), { artifact });
      const info = await lstat(file);
      if (info.isSymbolicLink() || !info.isFile()) fail("invalid-runtime-theme", `runtimeTheme artifact 必须是 contained regular file：${artifact}。`, { artifact });
      const contents = await readFile(file);
      runtimeThemeArtifacts.push({ path: posixPath(artifact), name: path.basename(artifact), sha256: sha256(contents), contents });
    }
  }
  runtimeThemeArtifacts.sort((a, b) => a.name.localeCompare(b.name));

  const explicitRoots = [...records.values()].filter((record) => record.lifecycle === "active").map((record) => record.id).sort();
  const roots = explicitRoots;
  const closure = [];
  const visited = new Set();
  const visiting = new Set();
  const visit = (id, chain, explicit = false) => {
    const record = records.get(id);
    if (!record) fail("broken-closure", `依赖链缺少资产 ${id}：${[...chain, id].join(" → ")}。`, { chain: [...chain, id] });
    if (record.lifecycle === "deprecated") fail("deprecated-in-closure", `新闭包不能包含 deprecated 资产：${[...chain, id].join(" → ")}。`, { chain: [...chain, id] });
    if (record.lifecycle === "draft" && !explicit) {
      const parent = records.get(chain.at(-1));
      if (parent?.lifecycle === "active") fail("active-depends-on-draft", `active 资产不能依赖 draft：${[...chain, id].join(" → ")}。`, { chain: [...chain, id] });
    }
    if (visiting.has(id)) fail("dependency-cycle", `硬依赖形成循环：${[...chain, id].join(" → ")}。`, { chain: [...chain, id] });
    if (visited.has(id)) return;
    visiting.add(id); closure.push(id);
    for (const dependency of record.hardDependencies) visit(dependency, [...chain, id], false);
    visiting.delete(id);
    visited.add(id);
  };
  for (const root of roots) {
    const record = records.get(root);
    if (!record) fail("missing-root", `Scope root 不存在：${root}。`, { chain: [root] });
    if (record.lifecycle === "draft" && !explicitRoots.includes(root)) fail("draft-not-explicit", `draft 资产只能作为显式 root 试用：${root}。`, { root });
    visit(root, [], explicitRoots.includes(root));
  }
  const closureIds = uniqueSorted(closure);
  const closureSet = new Set(closureIds);
  const projection = [...records.values()].flatMap((record) => closureSet.has(record.id) ? record.softRelations.filter((relation) => closureSet.has(relation.target)).map((relation) => ({ source: record.id, ...relation })) : []).sort((a, b) => a.source.localeCompare(b.source) || a.target.localeCompare(b.target) || a.type.localeCompare(b.type));
  const selectedRecords = closureIds.map((id) => records.get(id));
  const catalog = [...records.values()].map((record) => ({ id: record.id, kind: record.kind, lifecycle: record.lifecycle, recordDigest: record.recordDigest })).sort((a, b) => a.id.localeCompare(b.id));
  const reachableRecords = selectedRecords.filter((record) => record.lifecycle === "active");
  const reachable = new Set([
    "manifest.json",
    posixPath(manifest.consumption.baseline.artifact),
    ...runtimeThemeArtifacts.map((artifact) => artifact.path),
    ...reachableRecords.map((record) => record.descriptorPath),
    ...reachableRecords.flatMap((record) => record.files.map((file) => file.sourcePath))
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
  if (unreachable.length) fail("unreachable-pack-file", `正式 Pack 包含公共消费不可达文件：${unreachable.join("、")}。`, { files: unreachable });
  const packFiles = {};
  for (const file of [...reachable].sort()) packFiles[file] = sha256(await readFile(path.join(root, file)));
  const packDigest = digestObject(packFiles);
  return {
    schemaVersion: 2,
    pack: { id: manifest.id, version: manifest.version, digest: packDigest },
    sources: [{ id: manifest.id, type: "pack", reference: source.reference, version: manifest.version, digest: packDigest, available: true }],
    roots: explicitRoots,
    closure: closureIds,
    draftTrials: explicitRoots.filter((id) => records.get(id)?.lifecycle === "draft"),
    projection,
    records: selectedRecords,
    catalog,
    consumption: {
      baseline,
      recommendations: manifest.consumption.recommendations,
      review: { assets: reviewIds }
    },
    runtimeTheme: { artifacts: runtimeThemeArtifacts },
    packFiles,
    report: { schemaVersion: 2, status: "resolved", roots: explicitRoots, closure: closureIds, diagnostics: [] }
  };
}
