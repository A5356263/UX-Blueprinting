export function emptyManifest(workspaceId, sessionId) {
  return {
    version: 1,
    workspaceId,
    sessionId,
    updatedAt: new Date().toISOString(),
    skills: {},
  }
}

export function completedFor(manifest) {
  return Object.keys(manifest?.skills ?? {})
}
