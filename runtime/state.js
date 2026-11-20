export function normalizeSkillId(id) {
  return id === 'uxb' ? 'uxs' : id
}

export function emptyManifest(workspaceId, taskId, sessionId) {
  return {
    version: 1,
    workspaceId,
    taskId,
    sessionId: sessionId || '',
    updatedAt: new Date().toISOString(),
    skills: {},
  }
}

export function completedFor(manifest) {
  return Object.entries(manifest?.skills ?? {})
    .filter(([key, entry]) => key !== 'prd-review-record' && entry?.artifactKind !== 'review-record')
    .map(([key]) => key)
}
