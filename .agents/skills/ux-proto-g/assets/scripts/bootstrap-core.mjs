import path from "node:path";
import { bootstrapWorkspace } from "./bootstrap-workspace.mjs";
import { stableJson } from "../core/common.mjs";

const managedInternalDisclosure = /(?:^|[\\/])(?:\.ux-proto|runtime[\\/](?:core|packs)|assets[\\/](?:core|packs))(?:[\\/]|$)/i;

function parseArguments(argv) {
  const values = new Map();
  for (let index = 0; index < argv.length; index += 1) {
    const item = argv[index];
    if (!["--output", "--json", "--allow-packless"].includes(item)) throw new Error(`Unknown argument ${item}.`);
    if (values.has(item)) throw new Error(`${item} may be provided only once.`);
    if (["--json", "--allow-packless"].includes(item)) { values.set(item, true); continue; }
    const value = argv[++index];
    if (!value || value.startsWith("--")) throw new Error(`${item} requires a value.`);
    values.set(item, value);
  }
  if (!values.has("--output")) throw new Error("--output is required.");
  return values;
}

export async function runBootstrapLauncher({ argv, distributionRoot, mode, runtimeRoot = null, expectedOutput = null, preservedEntries = [] }) {
  const jsonMode = argv.includes("--json");
  try {
    const options = parseArguments(argv);
    if (!jsonMode) throw new Error("Bootstrap requires --json.");
    const output = path.resolve(options.get("--output"));
    if (expectedOutput && output !== expectedOutput) throw new Error("Bootstrap output differs from the validated Open Design project root.");
    const result = await bootstrapWorkspace({ output, mode, runtimeRoot, distributionRoot, preservedEntries, allowPackless: options.has("--allow-packless") });
    const data = { fullAssets: result.fullAssets, linkedAbstracts: result.linkedAbstracts };
    process.stdout.write(stableJson({ schemaVersion: 2, command: "bootstrap", status: "success", data }));
    return 0;
  } catch (error) {
    const category = error.category === "host-runtime-unavailable" ? error.category : "bootstrap-failed";
    const context = category === "host-runtime-unavailable" ? { mode, recovery: error.recovery } : { mode };
    const message = managedInternalDisclosure.test(String(error.message))
      ? "Managed UX Proto Core/Pack data is invalid or unavailable."
      : error.message;
    const result = { schemaVersion: 2, command: "bootstrap", status: "failed", error: { category, message, context } };
    if (jsonMode) process.stdout.write(stableJson(result)); else process.stderr.write(`${error.message}\n`);
    return 1;
  }
}
