import { runCli } from "../runtime/core/cli.mjs";

const code = await runCli({ argv: ["build"], workspaceRoot: process.cwd() });
if (code !== 0) process.exitCode = code;
