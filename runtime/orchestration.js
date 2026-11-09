import { readFileSync } from 'node:fs'

const graph = JSON.parse(readFileSync(new URL('../shared-workflow/skill-graph.json', import.meta.url), 'utf8'))
const byId = new Map(graph.skills.map(skill => [skill.id, skill]))
const chain = graph.main_chain ?? []
const chainIndex = new Map(chain.map((id, index) => [id, index]))

export function skillCatalog() {
  return graph.skills.map(skill => ({
    id: skill.id,
    name: skill.name_zh ?? skill.id,
    phase: skill.phase ?? null,
    required: [...(skill.required ?? [])],
    reads: [...(skill.reads ?? [])],
    standalone: skill.standalone_usable !== false,
  }))
}

function isAvailable(skill, done) {
  const position = chainIndex.get(skill.id)
  if (position !== undefined) return position === 0 || done.has(chain[position - 1])
  return (skill.required ?? []).every(id => done.has(id))
}

export function recommendNext(completed = []) {
  const done = new Set(completed.filter(id => byId.has(id)))
  const available = graph.skills
    .filter(skill => !done.has(skill.id) && isAvailable(skill, done))
    .map(skill => ({ id: skill.id, name: skill.name_zh ?? skill.id, reason: skill.next_hint?.reason ?? '' }))
  const preferred = new Set()
  for (const id of done) {
    for (const next of byId.get(id)?.next_hint?.preferred ?? []) preferred.add(next)
  }
  const recommended = available.filter(item => preferred.has(item.id))
  return { recommended: recommended.length ? recommended : available.slice(0, 3), available }
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
