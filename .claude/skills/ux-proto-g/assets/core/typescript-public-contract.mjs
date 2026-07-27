import path from "node:path";
import { lstat, readFile, realpath } from "node:fs/promises";
import { fail } from "./common.mjs";

const identifierPattern = /^[A-Za-z_$][A-Za-z0-9_$]*$/;

function tokenize(source, file) {
  const tokens = [];
  let cursor = 0;
  const push = (value, start, end, kind = "punctuator") => tokens.push({ value, start, end, kind });
  while (cursor < source.length) {
    const start = cursor;
    const char = source[cursor];
    if (/\s/.test(char)) { cursor += 1; continue; }
    if (char === "/" && source[cursor + 1] === "/") {
      cursor = source.indexOf("\n", cursor + 2);
      if (cursor === -1) break;
      continue;
    }
    if (char === "/" && source[cursor + 1] === "*") {
      const end = source.indexOf("*/", cursor + 2);
      if (end === -1) fail("unsupported-typescript-contract", `Unterminated comment in ${file}.`, { file });
      cursor = end + 2;
      continue;
    }
    if (char === "'" || char === '"') {
      cursor += 1;
      while (cursor < source.length && source[cursor] !== char) {
        if (source[cursor] === "\\") cursor += 2;
        else cursor += 1;
      }
      if (cursor >= source.length) fail("unsupported-typescript-contract", `Unterminated string in ${file}.`, { file });
      cursor += 1;
      push(source.slice(start, cursor), start, cursor, "string");
      continue;
    }
    if (char === "`") {
      cursor += 1;
      while (cursor < source.length && source[cursor] !== "`") {
        if (source[cursor] === "\\") cursor += 2;
        else cursor += 1;
      }
      if (cursor >= source.length) fail("unsupported-typescript-contract", `Unterminated template literal in ${file}.`, { file });
      cursor += 1;
      push(source.slice(start, cursor), start, cursor, "string");
      continue;
    }
    if (/[A-Za-z_$]/.test(char)) {
      cursor += 1;
      while (cursor < source.length && /[A-Za-z0-9_$]/.test(source[cursor])) cursor += 1;
      push(source.slice(start, cursor), start, cursor, "identifier");
      continue;
    }
    if (/[0-9]/.test(char)) {
      cursor += 1;
      while (cursor < source.length && /[0-9.eE_+-]/.test(source[cursor])) cursor += 1;
      push(source.slice(start, cursor), start, cursor, "number");
      continue;
    }
    for (const operator of ["...", "=>", "?.", "??", "||", "&&", "===", "!==", "<=", ">="]) {
      if (source.startsWith(operator, cursor)) {
        cursor += operator.length;
        push(operator, start, cursor);
        break;
      }
    }
    if (cursor !== start) continue;
    cursor += 1;
    push(char, start, cursor);
  }
  return tokens;
}

function matching(tokens, start, open, close, file) {
  let depth = 0;
  for (let index = start; index < tokens.length; index += 1) {
    if (tokens[index].value === open) depth += 1;
    else if (tokens[index].value === close && --depth === 0) return index;
  }
  fail("unsupported-typescript-contract", `Unbalanced ${open}${close} in ${file}.`, { file });
}

function splitTopLevel(tokens, separators) {
  const result = [];
  let start = 0;
  const depth = { "(": 0, "[": 0, "{": 0, "<": 0 };
  const pairs = { ")": "(", "]": "[", "}": "{", ">": "<" };
  for (let index = 0; index < tokens.length; index += 1) {
    const value = tokens[index].value;
    if (value in depth) depth[value] += 1;
    else if (value in pairs && depth[pairs[value]] > 0) depth[pairs[value]] -= 1;
    if (Object.values(depth).every((value) => value === 0) && separators.has(value)) {
      if (index > start) result.push(tokens.slice(start, index));
      start = index + 1;
    }
  }
  if (start < tokens.length) result.push(tokens.slice(start));
  return result.filter((part) => part.length);
}

function typeText(tokens) {
  let output = "";
  for (const [index, token] of tokens.entries()) {
    const value = token.value;
    if (!output) output = value;
    else if ([")", "]", "}", ",", ";", "?", ".", "["].includes(value)) output += value;
    else if (["(", "[", "{", "."].includes(tokens[index - 1]?.value)) output += value;
    else if (value === ":" || value === "=>") output += value === ":" ? ": " : " => ";
    else if (["|", "&", "="].includes(value)) output += ` ${value} `;
    else output += ` ${value}`;
  }
  return output.replace(/\s+/g, " ").replace(/\[\s+\]/g, "[]").replace(/,\s*/g, ", ").trim();
}

function findTopLevel(tokens, value) {
  let round = 0; let square = 0; let brace = 0; let angle = 0;
  for (let index = 0; index < tokens.length; index += 1) {
    const current = tokens[index].value;
    if (current === "(") round += 1;
    else if (current === ")") round -= 1;
    else if (current === "[") square += 1;
    else if (current === "]") square -= 1;
    else if (current === "{") brace += 1;
    else if (current === "}") brace -= 1;
    else if (current === "<") angle += 1;
    else if (current === ">" && angle) angle -= 1;
    if (!round && !square && !brace && !angle && current === value) return index;
  }
  return -1;
}

function parseProperties(tokens, file, typeName) {
  const rows = [];
  for (const member of splitTopLevel(tokens, new Set([";", ","]))) {
    let cursor = member[0]?.value === "readonly" ? 1 : 0;
    const name = member[cursor]?.value;
    if (!identifierPattern.test(name ?? "")) fail("unsupported-typescript-contract", `${typeName} contains an unsupported property declaration in ${file}.`, { file, typeName });
    cursor += 1;
    const optional = member[cursor]?.value === "?";
    if (optional) cursor += 1;
    if (member[cursor]?.value !== ":") fail("unsupported-typescript-contract", `${typeName}.${name} must be a property signature in ${file}.`, { file, typeName, property: name });
    const typeTokens = member.slice(cursor + 1);
    if (!typeTokens.length) fail("unsupported-typescript-contract", `${typeName}.${name} has no public type in ${file}.`, { file, typeName, property: name });
    rows.push({ name, type: typeText(typeTokens), required: !optional, default: null });
  }
  return rows;
}

function literalValue(tokens, file, property) {
  if (tokens.length !== 1) fail("unsupported-typescript-contract", `Default for ${property} must be a JSON scalar literal in ${file}.`, { file, property });
  const token = tokens[0];
  if (token.kind === "string") {
    try { return JSON.parse(token.value[0] === "'" ? `"${token.value.slice(1, -1).replaceAll('"', '\\"')}"` : token.value); }
    catch { fail("unsupported-typescript-contract", `Default for ${property} is not a supported string literal in ${file}.`, { file, property }); }
  }
  if (token.kind === "number") {
    const number = Number(token.value.replaceAll("_", ""));
    if (!Number.isFinite(number)) fail("unsupported-typescript-contract", `Default for ${property} is not finite in ${file}.`, { file, property });
    return number;
  }
  if (token.value === "true") return true;
  if (token.value === "false") return false;
  if (token.value === "null") return null;
  fail("unsupported-typescript-contract", `Default for ${property} must be a JSON scalar literal in ${file}.`, { file, property });
}

function parseParameter(tokens, file, exportName) {
  if (!tokens.length) fail("unsupported-typescript-contract", `${exportName} must expose one typed props input in ${file}.`, { file, exportName });
  const parameters = splitTopLevel(tokens, new Set([","]));
  if (parameters.length !== 1) fail("unsupported-typescript-contract", `${exportName} must expose exactly one props parameter in ${file}.`, { file, exportName, parameterCount: parameters.length });
  const first = parameters[0];
  const defaults = new Map();
  if (first[0]?.value !== "{") fail("unsupported-typescript-contract", `${exportName} must destructure its only props parameter so defaults are mechanically provable in ${file}.`, { file, exportName });
  const close = matching(first, 0, "{", "}", file);
  for (const binding of splitTopLevel(first.slice(1, close), new Set([","]))) {
    const name = binding[0]?.value;
    if (!identifierPattern.test(name ?? "") || binding[1]?.value === ":") fail("unsupported-typescript-contract", `${exportName} uses an unsupported destructured prop in ${file}.`, { file, exportName });
    const equal = findTopLevel(binding, "=");
    if (equal !== -1) defaults.set(name, literalValue(binding.slice(equal + 1), file, name));
  }
  if (first[close + 1]?.value !== ":" || !identifierPattern.test(first[close + 2]?.value ?? "") || first.length !== close + 3) fail("unsupported-typescript-contract", `${exportName} must annotate its destructured props with a named public type in ${file}.`, { file, exportName });
  const typeName = first[close + 2].value;
  return { typeName, defaults };
}

function parseModule(source, file) {
  const tokens = tokenize(source, file);
  const objectTypes = new Map();
  const declarations = new Map();
  const exported = new Set();
  const valueExports = new Set();
  const functions = new Map();
  const imports = [];
  let depth = 0;
  for (let index = 0; index < tokens.length; index += 1) {
    const value = tokens[index].value;
    if (value === "{") { depth += 1; continue; }
    if (value === "}") { depth -= 1; continue; }
    if (depth !== 0) continue;
    if (value === "import") {
      const from = tokens.findIndex((token, cursor) => cursor > index && token.value === "from");
      if (from !== -1 && tokens[from + 1]?.kind === "string") {
        const specifier = tokens[from + 1].value.slice(1, -1);
        if (specifier.startsWith(".")) imports.push(specifier);
      }
      continue;
    }
    let cursor = index;
    const isExported = tokens[cursor]?.value === "export";
    if (isExported) cursor += 1;
    if (tokens[cursor]?.value === "declare") cursor += 1;
    const kind = tokens[cursor]?.value;
    const name = tokens[cursor + 1]?.value;
    const supportedDeclaration = ["interface", "type", "function", "class", "enum", "const", "let", "var"].includes(kind) && identifierPattern.test(name ?? "");
    if (isExported && !supportedDeclaration) fail("unsupported-typescript-contract", `Unsupported top-level export syntax in ${file}; public exports must be direct named declarations.`, { file, token: tokens[cursor]?.value ?? null });
    if (!supportedDeclaration) continue;
    if (declarations.has(name)) fail("unsupported-typescript-contract", `Duplicate top-level declaration ${name} in ${file}; declaration merging, overloads and cross-kind aliases are unsupported.`, { file, name, firstKind: declarations.get(name), duplicateKind: kind });
    declarations.set(name, kind);
    if (isExported) {
      exported.add(name);
      if (!["interface", "type"].includes(kind)) valueExports.add(name);
    }
    if (kind === "interface") {
      if (tokens[cursor + 2]?.value !== "{") fail("unsupported-typescript-contract", `Interface ${name} must use a direct object body in ${file}.`, { file, typeName: name });
      const close = matching(tokens, cursor + 2, "{", "}", file);
      objectTypes.set(name, parseProperties(tokens.slice(cursor + 3, close), file, name));
      index = close;
    } else if (kind === "type") {
      if (tokens[cursor + 2]?.value !== "=") fail("unsupported-typescript-contract", `Type ${name} is malformed in ${file}.`, { file, typeName: name });
      if (tokens[cursor + 3]?.value === "{") {
        const close = matching(tokens, cursor + 3, "{", "}", file);
        objectTypes.set(name, parseProperties(tokens.slice(cursor + 4, close), file, name));
        index = close;
      } else {
        const terminator = findTopLevel(tokens.slice(cursor + 3), ";");
        if (terminator === -1) fail("unsupported-typescript-contract", `Non-object type ${name} must use an explicit terminator in ${file}.`, { file, typeName: name });
        index = cursor + 3 + terminator;
      }
    } else if (kind === "function") {
      if (tokens[cursor + 2]?.value !== "(") fail("unsupported-typescript-contract", `Function ${name} has an unsupported signature in ${file}.`, { file, exportName: name });
      const close = matching(tokens, cursor + 2, "(", ")", file);
      functions.set(name, parseParameter(tokens.slice(cursor + 3, close), file, name));
      index = close;
    }
  }
  return { objectTypes, exported, valueExports, functions, imports };
}

async function resolveModule(importer, specifier, sourceRoot) {
  if (specifier.split(/[\\/]/).includes("..")) fail("path-traversal", `Public type import cannot traverse upward from ${importer}.`, { file: importer, specifier });
  const base = path.resolve(path.dirname(importer), specifier);
  for (const candidate of [base, `${base}.ts`, `${base}.tsx`, path.join(base, "index.ts"), path.join(base, "index.tsx")]) {
    try {
      const candidateReal = await realpath(candidate);
      const relative = path.relative(sourceRoot, candidateReal);
      if (relative.startsWith("..") || path.isAbsolute(relative)) fail("source-escape", `Public type import escapes the Pack root from ${importer}.`, { file: importer, specifier });
      const info = await lstat(candidate);
      if (info.isSymbolicLink()) fail("symlink-escape", `Public type import cannot be a symbolic link: ${candidate}.`, { file: importer, specifier });
      if (!info.isFile()) continue;
      return { file: candidateReal, source: await readFile(candidateReal, "utf8") };
    }
    catch (error) { if (error?.code !== "ENOENT") throw error; }
  }
  fail("unsupported-typescript-contract", `Cannot resolve public type module ${specifier} from ${importer}.`, { file: importer, specifier });
}

export async function extractTypeScriptPublicContract({ entryFile, mainExport, sourceRoot }) {
  const rootReal = await realpath(sourceRoot);
  const modules = new Map();
  const visit = async (file, source) => {
    const absolute = path.resolve(file);
    if (modules.has(absolute)) return;
    const parsed = parseModule(source, absolute);
    modules.set(absolute, parsed);
    for (const specifier of parsed.imports) {
      const imported = await resolveModule(absolute, specifier, rootReal);
      await visit(imported.file, imported.source);
    }
  };
  await visit(entryFile, await readFile(entryFile, "utf8"));
  const entry = modules.get(path.resolve(entryFile));
  if (!entry.exported.has(mainExport)) fail("public-export-mismatch", `${mainExport} is not exported by the public entry.`, { entryFile, mainExport, exports: [...entry.exported].sort() });
  const signature = entry.functions.get(mainExport);
  if (!signature) fail("unsupported-typescript-contract", `${mainExport} must be an exported function with one named typed props input.`, { entryFile, mainExport });
  const objectTypes = new Map();
  for (const module of modules.values()) for (const [name, rows] of module.objectTypes) {
    if (objectTypes.has(name)) fail("unsupported-typescript-contract", `Public type ${name} is ambiguous across the implementation closure.`, { entryFile, typeName: name });
    objectTypes.set(name, rows);
  }
  const properties = objectTypes.get(signature.typeName);
  if (!properties) fail("unsupported-typescript-contract", `${mainExport} props type ${signature.typeName} must be a direct interface or object type alias.`, { entryFile, mainExport, propsType: signature.typeName });
  const propertyNames = new Set(properties.map((row) => row.name));
  for (const name of signature.defaults.keys()) if (!propertyNames.has(name)) fail("unsupported-typescript-contract", `${mainExport} declares a default for unknown prop ${name}.`, { entryFile, mainExport, property: name });
  const withDefaults = properties.map((row) => ({ ...row, default: signature.defaults.has(row.name) ? signature.defaults.get(row.name) : null }));
  return {
    exports: [...entry.exported].sort(),
    valueExports: [...entry.valueExports].sort(),
    propsType: signature.typeName,
    properties: withDefaults,
    objectTypes
  };
}

function referencedNames(type) {
  return [...type.matchAll(/\b[A-Z][A-Za-z0-9_$]*\b/g)].map((match) => match[0]);
}

function comparableRows(rows) {
  return rows.map(({ name, type, required, default: defaultValue }) => ({ name, type, required, default: defaultValue }));
}

export function validatePackComponentApi({ assetId, descriptorApi, contract }) {
  const actualProperties = comparableRows(contract.properties);
  const declaredProperties = comparableRows(descriptorApi.properties);
  if (JSON.stringify(declaredProperties) !== JSON.stringify(actualProperties)) fail("component-api-mismatch", `${assetId} API properties do not exactly match the main export public input.`, { assetId, expected: actualProperties, actual: declaredProperties });
  const reachable = new Set();
  const pending = actualProperties.flatMap((row) => referencedNames(row.type));
  while (pending.length) {
    const name = pending.shift();
    if (reachable.has(name) || name === contract.propsType || !contract.objectTypes.has(name)) continue;
    reachable.add(name);
    for (const row of contract.objectTypes.get(name)) pending.push(...referencedNames(row.type));
  }
  const expectedTypes = [...reachable].sort().map((name) => ({ name, properties: comparableRows(contract.objectTypes.get(name)) }));
  const actualTypes = descriptorApi.types.map((item) => ({ name: item.name, properties: comparableRows(item.properties) })).sort((a, b) => a.name.localeCompare(b.name));
  if (JSON.stringify(actualTypes) !== JSON.stringify(expectedTypes)) fail("component-api-mismatch", `${assetId} named API types do not exactly match the public type closure.`, { assetId, expected: expectedTypes, actual: actualTypes });
}
