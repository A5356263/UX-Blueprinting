import path from "node:path";
import { bootstrapWorkspace } from "./bootstrap-workspace.mjs";

function argument(argv, name) {
  const index = argv.indexOf(name);
  if (index === -1 || !argv[index + 1] || argv[index + 1].startsWith("--")) throw new Error(`${name} is required.`);
  return argv[index + 1];
}

export async function runBootstrapLauncher({ argv, distributionRoot, mode, runtimeRoot = null, expectedOutput = null, preservedEntries = [] }) {
  const jsonMode = argv.includes("--json");
  try {
    for (const item of argv.filter((value) => value.startsWith("--"))) if (!["--output", "--json"].includes(item)) throw new Error(`Unknown argument ${item}.`);
    const output = path.resolve(argument(argv, "--output"));
    if (expectedOutput && output !== expectedOutput) throw new Error("Bootstrap output differs from the validated Open Design project root.");
    const data = await bootstrapWorkspace({ output, mode, runtimeRoot, distributionRoot, preservedEntries });
    process.stdout.write(`${JSON.stringify({ schemaVersion: 1, ok: true, data }, null, 2)}\n`);
    return 0;
  } catch (error) {
    const category = error.category === "host-runtime-unavailable" ? error.category : "bootstrap-failed";
    const context = category === "host-runtime-unavailable" ? { mode, recovery: error.recovery } : { mode };
    const result = { schemaVersion: 1, ok: false, error: { category, message: error.message, context } };
    if (jsonMode) process.stdout.write(`${JSON.stringify(result, null, 2)}\n`); else process.stderr.write(`${error.message}\n`);
    return 1;
  }
}
