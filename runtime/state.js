import { randomUUID } from 'node:crypto'

export function newTask(workspaceId, title, input) {
  if (!workspaceId || !title?.trim() || !input?.path || !input?.sha256) {
    throw new Error('请确认工作区、任务名和已登记的输入材料')
  }
  return { id: randomUUID(), workspaceId, title: title.trim(), input, revision: 0,
    flowVersion: 1, state: 'draft', questions: [], questionHistory: {}, replies: {}, artifacts: {}, operations: {},
    executionHistory: [] }
}

export function actions(task) {
  if (task.state === 'draft') return ['start-review']
  if (task.state === 'waiting') return ['reply']
  if (task.state === 'ready') return ['start-page', ...(!task.artifacts.uxb ? ['start-uxb'] : []), ...(!task.artifacts.journey ? ['start-journey'] : [])]
  if (task.state === 'journey-review') return task.artifacts.journeyDraft?.complete ? ['confirm-journey', 'discard-journey'] : ['discard-journey']
  if (task.state === 'uxb-review') return ['confirm-uxb', 'discard-uxb']
  if (task.state === 'running') return ['cancel']
  if (['failed', 'cancelled', 'interrupted'].includes(task.state)) {
    if (task.execution?.stage === 'journey-analysis') return ['retry', 'discard-journey']
    return task.execution?.stage === 'uxb' ? ['retry', 'discard-uxb'] : ['retry']
  }
  return []
}

export function dispatch(task, request) {
  const { action, operationId, revision, replies } = request
  if (!/^[0-9a-f-]{36}$/i.test(operationId ?? '')) throw new Error('缺少有效操作标识')
  const signature = JSON.stringify([action, revision, replies ?? null])
  if (Object.hasOwn(task.operations, operationId)) {
    if (task.operations[operationId] !== signature) throw new Error('操作标识已用于其他请求')
    return task
  }
  if (revision !== task.revision) throw new Error('任务状态已变化，请刷新')
  if (!actions(task).includes(action)) throw new Error('当前状态不允许此操作')
  const next = { ...task, revision: task.revision + 1,
    operations: { ...task.operations, [operationId]: signature }, error: null }
  if (action === 'cancel') return { ...next, state: 'cancelling' }
  if (action === 'confirm-uxb' || action === 'discard-uxb') {
    const { uxbDraft, ...artifacts } = task.artifacts
    if (action === 'confirm-uxb') {
      if (!uxbDraft || uxbDraft.taskId !== task.id) throw new Error('缺少本轮待确认的体验策略')
      artifacts.uxb = { ...uxbDraft, kind: 'uxb', confirmedAt: new Date().toISOString(), confirmedRevision: next.revision }
    }
    return { ...next, state: 'ready', artifacts }
  }
  if (action === 'confirm-journey' || action === 'discard-journey') {
    const { journeyDraft, ...artifacts } = task.artifacts
    if (action === 'confirm-journey') {
      if (!journeyDraft?.complete || journeyDraft.taskId !== task.id) throw new Error('只有本轮完整旅程可以采用')
      artifacts.journey = { ...journeyDraft, kind: 'journey', confirmedAt: new Date().toISOString(), confirmedRevision: next.revision }
    }
    return { ...next, state: 'ready', artifacts }
  }
  let stage = action === 'start-page' ? 'page-spec' : action === 'start-uxb' ? 'uxb' : 'prd-review'
  if (action === 'start-journey') stage = 'journey-analysis'
  if (action === 'retry') stage = task.execution.stage
  if (action === 'reply') {
    const items = Object.entries(replies ?? {})
    if (!items.length || items.some(([id, value]) =>
      !task.questions.some(question => question.id === id) || typeof value !== 'string' || !value.trim() || value.length > 8000)) {
      throw new Error('请回复当前问题单中的至少一个问题')
    }
    next.replies = { ...task.replies, ...Object.fromEntries(items.map(([id, value]) => [id, value.trim()])) }
  }
  return { ...next, state: 'running', execution: { id: randomUUID(), stage, startedAt: new Date().toISOString() } }
}

function finish(task, state, error = null) {
  return { ...task, revision: task.revision + 1, state, error,
    executionHistory: [...(task.executionHistory ?? []), { ...task.execution, state, error, endedAt: new Date().toISOString() }] }
}

export function settle(task, executionId, result) {
  if (task.execution?.id !== executionId || !['running', 'cancelling'].includes(task.state)) return task
  if (task.state === 'cancelling') return finish(task, 'cancelled')
  if (result.error) return finish(task, 'failed', result.error)
  const review = task.execution.stage === 'prd-review'
  if (review && Array.isArray(result.questions) && result.questions.length) {
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
  if (review && task.questions.some(question => !Object.hasOwn(task.replies, question.id))) {
    throw new Error('问题单尚未全部回复，不能登记基线')
  }
  const uxb = task.execution.stage === 'uxb'
  const journey = task.execution.stage === 'journey-analysis'
  const kind = review ? 'baseline' : uxb ? 'uxbDraft' : journey ? 'journeyDraft' : 'pageSpec'
  if (!result.artifact?.path || !/^[a-f0-9]{64}$/.test(result.artifact.sha256 ?? '') ||
      result.artifact.taskId !== task.id || result.artifact.executionId !== executionId) {
    throw new Error('阶段未返回本轮有效的正式产物')
  }
  return { ...finish(task, review ? 'ready' : uxb ? 'uxb-review' : journey ? 'journey-review' : 'completed'), questions: [],
    artifacts: { ...task.artifacts, [kind]: result.artifact } }
}

export function recover(task) {
  return ['running', 'cancelling'].includes(task.state)
    ? finish(task, 'interrupted', '上次执行未确认结束，请显式重试')
    : task
}
