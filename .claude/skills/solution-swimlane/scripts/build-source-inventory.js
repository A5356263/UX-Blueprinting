"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith("--")) continue;
    const key = token.slice(2);
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) {
      throw new Error(`参数 --${key} 缺少值`);
    }
    args[key] = value;
    index += 1;
  }
  return args;
}

function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function portablePath(filePath) {
  const relative = path.relative(process.cwd(), filePath);
  const value = relative && !relative.startsWith("..") ? relative : filePath;
  return value.split(path.sep).join("/");
}

function makeItem(prefix, sourceFile, sourceRef, sourceKind, rawText, context = "") {
  const normalized = String(rawText).replace(/\r\n/g, "\n").trim();
  const contentHash = sha256(normalized);
  return {
    source_item_id: `${prefix}-${sha256(`${sourceRef}\n${sourceKind}\n${contentHash}`).slice(0, 16)}`,
    source_file: sourceFile,
    source_ref: sourceRef,
    source_kind: sourceKind,
    raw_text: normalized,
    context,
    content_hash: contentHash,
  };
}

function parseMarkdown(markdown, sourceFile) {
  const lines = markdown.replace(/^\uFEFF/, "").split(/\r?\n/);
  const items = [];
  const headings = [];
  let paragraph = [];
  let paragraphStart = 0;
  let code = null;

  function context() {
    return headings.map((item) => item.title).join(" > ");
  }

  function add(kind, rawText, startLine, endLine = startLine) {
    const ref = `${sourceFile}:L${startLine}${endLine === startLine ? "" : `-L${endLine}`}`;
    items.push(makeItem("md", sourceFile, ref, kind, rawText, context()));
  }

  function flushParagraph(endLine) {
    if (!paragraph.length) return;
    add("md-paragraph", paragraph.join("\n"), paragraphStart, endLine);
    paragraph = [];
    paragraphStart = 0;
  }

  for (let index = 0; index < lines.length; index += 1) {
    const lineNumber = index + 1;
    const rawLine = lines[index];
    const trimmed = rawLine.trim();

    if (code) {
      if (/^```/.test(trimmed)) {
        add("md-code-block", code.lines.join("\n"), code.start, lineNumber);
        code = null;
      } else {
        code.lines.push(rawLine);
      }
      continue;
    }

    if (/^```/.test(trimmed)) {
      flushParagraph(lineNumber - 1);
      code = { start: lineNumber, lines: [] };
      continue;
    }

    if (!trimmed) {
      flushParagraph(lineNumber - 1);
      continue;
    }

    if (/^---+$/.test(trimmed)) {
      flushParagraph(lineNumber - 1);
      continue;
    }

    const heading = trimmed.match(/^(#{1,6})\s+(.+)$/);
    if (heading) {
      flushParagraph(lineNumber - 1);
      const level = heading[1].length;
      while (headings.length && headings[headings.length - 1].level >= level) {
        headings.pop();
      }
      headings.push({ level, title: heading[2].trim() });
      add("md-heading", heading[2].trim(), lineNumber);
      continue;
    }

    if (/^\s*\|?.+\|.+\|?\s*$/.test(rawLine)) {
      flushParagraph(lineNumber - 1);
      if (!/^\s*\|?\s*:?-{3,}/.test(rawLine)) {
        add("md-table-row", trimmed, lineNumber);
      }
      continue;
    }

    if (/^\s*(?:[-*+]|\d+\.)\s+/.test(rawLine)) {
      flushParagraph(lineNumber - 1);
      add("md-list-item", trimmed.replace(/^\s*(?:[-*+]|\d+\.)\s+/, ""), lineNumber);
      continue;
    }

    if (/^\s*>\s?/.test(rawLine)) {
      flushParagraph(lineNumber - 1);
      add("md-blockquote", trimmed.replace(/^>\s?/, ""), lineNumber);
      continue;
    }

    if (!paragraph.length) paragraphStart = lineNumber;
    paragraph.push(rawLine);
  }

  if (code) add("md-code-block", code.lines.join("\n"), code.start, lines.length);
  flushParagraph(lines.length);
  return items;
}

function jsonPathKey(key) {
  return /^[A-Za-z_$][A-Za-z0-9_$-]*$/.test(key)
    ? `.${key}`
    : `[${JSON.stringify(key)}]`;
}

function describeJson(value) {
  if (Array.isArray(value)) return `[array length=${value.length}]`;
  if (value && typeof value === "object") {
    return `{object keys=${Object.keys(value).join(",")}}`;
  }
  return JSON.stringify(value);
}

function parseJson(value, sourceFile) {
  const items = [];

  function visit(current, pointer) {
    const kind = Array.isArray(current)
      ? "json-array"
      : current && typeof current === "object"
        ? "json-object"
        : "json-value";
    const ref = `${sourceFile}#${pointer}`;
    items.push(makeItem("json", sourceFile, ref, kind, describeJson(current), pointer));

    if (Array.isArray(current)) {
      current.forEach((item, index) => visit(item, `${pointer}[${index}]`));
    } else if (current && typeof current === "object") {
      Object.keys(current).sort().forEach((key) => {
        visit(current[key], `${pointer}${jsonPathKey(key)}`);
      });
    }
  }

  visit(value, "$");
  return items;
}

function buildInventory(mdPath, jsonPath) {
  const resolvedMd = path.resolve(mdPath);
  const resolvedJson = path.resolve(jsonPath);
  const mdBuffer = fs.readFileSync(resolvedMd);
  const jsonBuffer = fs.readFileSync(resolvedJson);
  const mdText = mdBuffer.toString("utf8");
  const jsonText = jsonBuffer.toString("utf8");
  const jsonValue = JSON.parse(jsonText.replace(/^\uFEFF/, ""));
  const mdFile = portablePath(resolvedMd);
  const jsonFile = portablePath(resolvedJson);
  const mdHash = sha256(mdBuffer);
  const jsonHash = sha256(jsonBuffer);
  const items = [
    ...parseMarkdown(mdText, mdFile),
    ...parseJson(jsonValue, jsonFile),
  ];

  const ids = new Set();
  for (const item of items) {
    if (ids.has(item.source_item_id)) {
      throw new Error(`源项 ID 冲突：${item.source_item_id}`);
    }
    ids.add(item.source_item_id);
  }

  return {
    schema_version: "1.0",
    source_hash: sha256(`${mdHash}\n${jsonHash}`),
    files: [
      { path: mdFile, kind: "markdown", sha256: mdHash, bytes: mdBuffer.length },
      { path: jsonFile, kind: "json", sha256: jsonHash, bytes: jsonBuffer.length },
    ],
    source_items_total: items.length,
    items,
  };
}

function main() {
  try {
    const args = parseArgs(process.argv.slice(2));
    if (!args.md || !args.json || !args.out) {
      throw new Error("用法：node build-source-inventory.js --md <file> --json <file> --out <file>");
    }
    const inventory = buildInventory(args.md, args.json);
    const outputPath = path.resolve(args.out);
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, `${JSON.stringify(inventory, null, 2)}\n`, "utf8");
    console.log(`源清单已生成：${outputPath}`);
    console.log(`源项总数：${inventory.source_items_total}`);
    console.log(`来源哈希：${inventory.source_hash}`);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

if (require.main === module) main();

module.exports = {
  buildInventory,
  parseArgs,
  parseJson,
  parseMarkdown,
  sha256,
};
