import { readFileSync } from 'node:fs'

const graph = JSON.parse(readFileSync(new URL('../shared-workflow/skill-graph.json', import.meta.url), 'utf8'))
const byId = new Map(graph.skills.map(skill => [skill.id, skill]))
const fanout = new Map(graph.skills.map(skill => [skill.id, 0]))
for (const skill of graph.skills) {
  for (const read of skill.reads ?? []) fanout.set(read, (fanout.get(read) ?? 0) + 1)
}

export function skillCatalog() {
  return graph.skills.map(skill => ({
    id: skill.id,
    name: skill.name_zh ?? skill.id,
    phase: skill.phase ?? 2,
    anchor: skill.anchor === true,
    required: [...(skill.required ?? [])],
    requiredAny: [...(skill.requiredAny ?? [])],
    reads: [...(skill.reads ?? [])],
    next: {
      preferred: [...(skill.next_hint?.preferred ?? [])],
      alternatives: [...(skill.next_hint?.alternatives ?? [])],
      reason: skill.next_hint?.reason ?? '',
    },
  }))
}

export function readsOf(id) {
  return [...(byId.get(id)?.reads ?? [])]
}

export function nameOf(id) {
  return byId.get(id)?.name_zh ?? id
}

export function completedFromArtifacts(artifacts = {}) {
  return Object.entries(artifacts)
    .filter(([kind, artifact]) => byId.has(kind) && artifact?.path)
    .map(([kind]) => kind)
}

function isReady(skill, done) {
  const required = skill.required ?? []
  const requiredAny = skill.requiredAny ?? []
  if (!required.every(id => done.has(id))) return false
  if (requiredAny.length && !requiredAny.some(id => done.has(id))) return false
  return true
}

export function availableSkills(completed = []) {
  const done = new Set(completed.filter(id => byId.has(id)))
  return graph.skills
    .filter(skill => !done.has(skill.id) && isReady(skill, done))
    .map(skill => ({ id: skill.id, name: skill.name_zh ?? skill.id }))
}

export function recommendHandoff(completed, currentSkill) {
  const current = byId.get(currentSkill)
  const done = new Set(completed)
  if (!current || !done.has(currentSkill)) return []

  const preferred = current.next_hint?.preferred ?? []
  const preferredReason = current.next_hint?.reason ?? ''
  const alternatives = (current.next_hint?.alternatives ?? []).map(entry =>
    typeof entry === 'string' ? { id: entry } : entry)
  const candidates = new Set([
    ...preferred,
    ...alternatives.map(entry => entry.id),
    ...graph.skills.filter(skill => (skill.reads ?? []).includes(currentSkill)).map(skill => skill.id),
  ])
  return [...candidates]
    .map(id => byId.get(id))
    .filter(skill => skill && !done.has(skill.id) && isReady(skill, done))
    .slice(0, 3)
    .map(skill => ({
      id: skill.id,
      name: nameOf(skill.id),
      reason: skill.id === preferred[0]
        ? preferredReason
        : alternatives.find(entry => entry.id === skill.id)?.reason
          ?? ('可承接本会话已登记的「' + nameOf(currentSkill) + '」产物。'),
    }))
}

export function recommendNext(completed = [], currentSkill) {
  const done = new Set(completed.filter(id => byId.has(id)))
  const current = byId.get(currentSkill)
  const preferred = (current?.next_hint?.preferred ?? []).map((id, index) => [id, index])
  const alternatives = (current?.next_hint?.alternatives ?? []).map(entry => {
    const id = typeof entry === 'string' ? entry : entry?.id
    const index = (current?.next_hint?.alternatives ?? []).indexOf(entry)
    return [id, index]
  })
  const preferredIndex = new Map(preferred)
  const alternativeIndex = new Map(alternatives)
  const currentPhase = current?.phase ?? 2
  const ready = graph.skills.filter(skill => !done.has(skill.id) && isReady(skill, done))
  const scored = ready.map(skill => {
    let score = 0
    if (preferredIndex.has(skill.id)) score -= 1000 - preferredIndex.get(skill.id)
    else if (alternativeIndex.has(skill.id)) score -= 500 - alternativeIndex.get(skill.id)
    score += Math.abs((skill.phase ?? 2) - currentPhase) * 10
    if (skill.anchor === true) score -= 20
    score -= (fanout.get(skill.id) ?? 0)
    return { skill, score }
  }).sort((a, b) => a.score - b.score)
  const items = scored.slice(0, 5).map(({ skill }) => ({
    id: skill.id,
    name: skill.name_zh ?? skill.id,
    reason: skill.next_hint?.reason ?? '',
  }))
  return {
    recommended: items,
    available: scored.map(({ skill }) => ({ id: skill.id, name: skill.name_zh ?? skill.id })),
  }
}
