#!/usr/bin/env node
import { runCli } from "../runtime/core/cli.mjs";

process.exitCode = await runCli();
