import { readFile } from "node:fs/promises";
import path from "node:path";
import { assessBuildCurrentness, computeBuildArtifactDigest, computeBuildSourceDigest } from "./build-workspace.mjs";

export async function reconcileArtifact({ workspaceRoot, artifactManifest = {} }) {
  let report;
  try { report = JSON.parse(await readFile(path.join(workspaceRoot, ".ux-proto/build-report.json"), "utf8")); }
  catch (error) {
    return { ...artifactManifest, status: "incomplete", metadata: { ...(artifactManifest.metadata ?? {}), uxProto: { completionStatus: "failed", fresh: false, error: { category: "missing-build-receipt", message: error.message } } } };
  }
  const [current, artifacts] = await Promise.all([computeBuildSourceDigest(workspaceRoot), computeBuildArtifactDigest(workspaceRoot)]);
  const currentness = assessBuildCurrentness({ report, currentSource: current, currentArtifacts: artifacts });
  const normal = currentness.fresh && report.completionStatus === "normal" && report.runtimePreview === "usable" && report.staticPreview === "usable" && report.executionSafety === "verified";
  return {
    ...artifactManifest,
    status: normal ? "complete" : "incomplete",
    metadata: {
      ...(artifactManifest.metadata ?? {}),
      uxProto: {
        completionStatus: currentness.completionStatus,
        fresh: currentness.fresh,
        sourceFresh: currentness.sourceFresh,
        artifactsFresh: currentness.artifactsFresh,
        sourceDigest: report.sourceDigest ?? null,
        currentSourceDigest: current.sourceDigest,
        artifactDigest: report.artifactDigest ?? null,
        currentArtifactDigest: artifacts.artifactDigest,
        ...(report.error ? { error: report.error } : {})
      }
    }
  };
}
