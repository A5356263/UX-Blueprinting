import path from "node:path";
import { fileURLToPath } from "node:url";

const distributionRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const bootstrap = await import(new URL("../assets/scripts/bootstrap-core.mjs", import.meta.url));
process.exitCode = await bootstrap.runBootstrapLauncher({ argv: process.argv.slice(2), distributionRoot, mode: "generic" });
