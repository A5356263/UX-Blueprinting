import { randomUUID } from 'node:crypto'

const oldKinds = {
  baseline: 'prd-review',
  uxb: 'uxb',
  uxbDraft: 'uxb',
  journey: 'journey-analysis',
  journeyDraft: 'journey-analysis',
  pageSpec: 'page-spec',
}

export function newTask(workspaceId, title, input) {
  if (!workspaceId || !title?.trim() || !input?.path || !input?.sha256) {
    throw new Error('请确认工作区、任务名和已登记的输入材料')
  }
  return { id: randomUUID(), workspaceId, title: title.trim(), input, revision: 0,
    flowVersion: 2, state: 'ready', questions: [], questionHistory: {}, replies: {}, artifacts: {},
    operations: {}, executionHistory: [] }
}

export function migrate(task) {
  if (task.flowVersion === 2) return task
  const artifacts = {}
  for (const [kind, artifact] of Object.entries(task.artifacts ?? {})) {
    const skill = oldKinds[kind] ?? kind
    if (artifact?.path) artifacts[skill] = { ...artifact, kind: skill, skill }
  }
  const state = ['draft'].includes(task.state) ? 'ready'
    : ['uxb-review', 'journey-review', 'completed'].includes(task.state) ? 'ready' : task.state
  return { ...task, flowVersion: 2, state, questions: [], artifacts }
}

export function actions(task, available = []) {
  if (task.state === 'waiting') return ['reply']
  if (task.state === 'running') return ['cancel']
  if (['failed', 'cancelled', 'interrupted'].includes(task.state)) return ['retry']
  if (task.state === 'ready') return available.map(id => 'start:' + id)
  return []
}

export function dispatch(task, request, available = []) {
  const { action, operationId, revision, replies } = request
  if (!/^[0-9a-f-]{36}$/i.test(operationId ?? '')) throw new Error('缺少有效操作标识')
  const signature = JSON.stringify([action, revision, replies ?? null])
  if (Object.hasOwn(task.operations, operationId)) {
    if (task.operations[operationId] !== signature) throw new Error('操作标识已用于其他请求')
    return task
  }
  if (revision !== task.revision) throw new Error('任务状态已变化，请刷新')
  if (!actions(task, available).includes(action)) throw new Error('当前状态不允许此操作')
  const next = { ...task, revision: task.revision + 1,
    operations: { ...task.operations, [operationId]: signature }, error: null }
  if (action === 'cancel') return { ...next, state: 'cancelling' }
  if (action === 'reply') {
    const items = Object.entries(replies ?? {})
    if (!items.length || items.some(([id, value]) =>
      !task.questions.some(question => question.id === id) || typeof value !== 'string' || !value.trim() || value.length > 8000)) {
      throw new Error('请回复当前问题单中的至少一个问题')
    }
    next.replies = { ...task.replies, ...Object.fromEntries(items.map(([id, value]) => [id, value.trim()])) }
    return { ...next, state: 'running', execution: { id: randomUUID(), skill: task.execution?.skill ?? 'prd-review', startedAt: new Date().toISOString() } }
  }
  if (action === 'retry') {
    if (!task.execution?.skill) throw new Error('没有可重试的阶段')
    return { ...next, state: 'running', execution: { id: randomUUID(), skill: task.execution.skill, startedAt: new Date().toISOString() } }
  }
  const skill = action.slice('start:'.length)
  return { ...next, state: 'running', execution: { id: randomUUID(), skill, startedAt: new Date().toISOString() } }
}

function finish(task, state, error = null) {
  return { ...task, revision: task.revision + 1, state, error,
    executionHistory: [...(task.executionHistory ?? []), { ...task.execution, state, error, endedAt: new Date().toISOString() }] }
}

export function settle(task, executionId, result) {
  if (task.execution?.id !== executionId || !['running', 'cancelling'].includes(task.state)) return task
  if (task.state === 'cancelling') return finish(task, 'cancelled')
  if (result.error) return finish(task, 'failed', result.error)
  const skill = task.execution.skill
  if (Array.isArray(result.questions) && result.questions.length) {
    if (typeof result.markdown === 'string' && result.markdown.trim()) throw new Error('阻断问题与正式产物不能同时登记')
    if (new Set(result.questions.map(question => question.id)).size !== result.questions.length ||
        result.questions.some(question => !/^Q-[0-9]{3,}$/.test(question.id) || typeof question.text !== 'string' || !question.text.trim())) {
      throw new Error('问题单不符合产物契约')
    }
    if (task.questions.some(question => !Object.hasOwn(task.replies, question.id) &&
        !result.questions.some(open => open.id === question.id))) {
      throw new Error('未收到回复的问题仍需保留在问题单')
    }
    return { ...finish(task, 'waiting'), questions: result.questions,
      questionHistory: { ...task.questionHistory, ...Object.fromEntries(result.questions.map(q => [q.id, q.text])) } }
  }
  if (skill === 'prd-review' && task.questions.some(question => !Object.hasOwn(task.replies, question.id))) {
    throw new Error('问题单尚未全部回复，不能登记基线')
  }
  if (!result.artifact?.path || !/^[a-f0-9]{64}$/.test(result.artifact.sha256 ?? '') ||
      result.artifact.taskId !== task.id || result.artifact.executionId !== executionId || result.artifact.skill !== skill) {
    throw new Error('阶段未返回本轮有效的正式产物')
  }
  return { ...finish(task, 'ready'), questions: [],
    artifacts: { ...task.artifacts, [skill]: result.artifact } }
}

export function recover(task) {
  return ['running', 'cancelling'].includes(task.state)
    ? finish(task, 'interrupted', '上次执行未确认结束，请显式重试')
    : task
}
