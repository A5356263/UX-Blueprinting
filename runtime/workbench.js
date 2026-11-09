import { createHash, randomUUID } from 'node:crypto'
import { lstatSync, mkdirSync, readFileSync, readdirSync, realpathSync, renameSync, writeFileSync } from 'node:fs'
import { isAbsolute, join, relative, resolve, sep } from 'node:path'
import { actions, dispatch, migrate, newTask, recover, settle } from './state.js'
import { validateMarkdown } from './artifacts.js'
import { renderPreview } from './preview.js'

const limit = 320_000
const idPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/
const digest = data => createHash('sha256').update(data).digest('hex')
const view = (task, catalog) => ({ ...task, actions: actions(task, catalog.available(Object.keys(task.artifacts))) })

function contained(root, path) {
  const local = relative(root, path)
  if (!local || local === '..' || local.startsWith('..' + sep) || isAbsolute(local)) {
    throw new Error('文件必须位于已选工作区')
  }
  return local
}

function readMaterial(root, path) {
  if (typeof path !== 'string' || !path.trim() || !/\.(md|txt)$/i.test(path)) {
    throw new Error('请指定工作区内的 Markdown 或纯文本文件')
  }
  const requested = resolve(root, path)
  contained(root, requested)
  let real
  try { real = realpathSync(requested) } catch { throw new Error('找不到指定的材料') }
  const local = contained(root, real)
  const info = lstatSync(real)
  if (!info.isFile() || !info.size || info.size > limit) throw new Error('材料必须是非空文本，且不超过 320 KB')
  const bytes = readFileSync(real)
  let content
  try { content = new TextDecoder('utf-8', { fatal: true }).decode(bytes) } catch {
    throw new Error('材料必须使用 UTF-8 编码')
  }
  if (!content.trim() || content.includes('\0')) throw new Error('指定的材料不是有效文本')
  return { path: local.split(sep).join('/'), sha256: digest(bytes), content }
}

function readArtifact(workspace, task, skill) {
  const artifact = task.artifacts[skill]
  if (!artifact) return undefined
  const material = readMaterial(workspace.path, artifact.path)
  if (artifact.taskId !== task.id || artifact.sha256 !== material.sha256) {
    throw new Error('本轮已登记产物版本无效，请重新生成')
  }
  return material.content
}

function readBoundMaterial(workspace, task, catalog) {
  const skill = task.execution.skill
  if (skill === 'prd-review') {
    const material = readMaterial(workspace.path, task.input.path)
    if (task.input.sha256 !== material.sha256) throw new Error('登记的材料已被修改，请恢复原版本后重试')
    return { baseline: material.content, materials: [] }
  }
  const baseline = readArtifact(workspace, task, 'prd-review')
  if (!baseline) throw new Error('缺少本轮已登记的正式需求基线')
  const materials = []
  for (const id of catalog.reads(skill)) {
    if (id === 'prd-review') continue
    const content = readArtifact(workspace, task, id)
    if (content !== undefined) materials.push({ skill: id, name: catalog.name(id), content })
  }
  return { baseline, materials }
}

function directory(root, parts, create) {
  let current = root
  for (const part of parts) {
    current = join(current, part)
    if (create) {
      try { mkdirSync(current) } catch (error) { if (error.code !== 'EEXIST') throw error }
    }
    const info = lstatSync(current)
    if (!info.isDirectory() || info.isSymbolicLink()) throw new Error('工作台目录不能是文件或链接')
    contained(root, realpathSync(current))
  }
  return current
}

export function createWorkbench(registry, runStage, cancelStage = () => {}, catalog) {
  const active = new Map()
  let disposed = false
  const folder = (workspace, id, create) => directory(workspace.path, ['spark-output', 'design-workbench', id], create)
  function save(workspace, task) {
    const dir = folder(workspace, task.id, true)
    const temporary = join(dir, randomUUID() + '.tmp')
    writeFileSync(temporary, JSON.stringify(task), { flag: 'wx' })
    renameSync(temporary, join(dir, 'task.json'))
    return task
  }
  function load(workspace, id) {
    if (!idPattern.test(id)) throw new Error('无效的任务标识')
    const file = join(folder(workspace, id, false), 'task.json')
    if (!lstatSync(file).isFile()) throw new Error('无法读取任务记录')
    const stored = JSON.parse(readFileSync(file, 'utf8'))
    if (stored.id !== id || stored.workspaceId !== workspace.id) throw new Error('任务不属于已选工作区')
    const migrated = migrate(stored)
    if (migrated !== stored) return save(workspace, migrated)
    if (!active.has(id)) {
      const recovered = recover(migrated)
      if (recovered !== migrated) return save(workspace, recovered)
    }
    return migrated
  }
  function list(workspace) {
    let items
    try { items = readdirSync(directory(workspace.path, ['spark-output', 'design-workbench'], false), { withFileTypes: true }) }
    catch (error) { if (error.code === 'ENOENT') return []; throw error }
    return items.filter(item => item.isDirectory() && idPattern.test(item.name))
      .map(item => view(load(workspace, item.name), catalog))
  }
  function publish(workspace, task, result) {
    if (task.state === 'cancelling') return settle(task, task.execution.id, {})
    if (!Array.isArray(result.questions) || typeof result.markdown !== 'string') throw new Error('阶段返回格式无效')
    if (result.questions.length) {
      if (result.markdown.trim()) throw new Error('阻断问题与正式产物不能同时登记')
      return settle(task, task.execution.id, result)
    }
    const { id: executionId, skill } = task.execution
    const bytes = Buffer.from(result.markdown)
    if (!bytes.length || bytes.length > limit) throw new Error('阶段未返回有效的 Markdown 产物')
    validateMarkdown(skill, result.markdown)
    const name = skill + '.md'
    const dir = folder(workspace, task.id, false)
    const file = join(dir, executionId + '-' + name)
    const artifact = { kind: skill, skill, path: contained(workspace.path, file).split(sep).join('/'),
      sha256: digest(bytes), taskId: task.id, executionId, version: task.revision }
    const next = settle(task, executionId, { artifact })
    writeFileSync(file, bytes, { flag: 'wx' })
    return next
  }
  function launch(workspace, task) {
    const controller = new AbortController()
    const { id } = task.execution
    active.set(task.id, controller)
    void (async () => {
      let result
      try {
        result = await runStage(task, workspace, readBoundMaterial(workspace, task, catalog), controller.signal)
      } catch (error) {
        result = { error: error?.message || '阶段执行失败，请检查工作区或 Harness 模型配置' }
      }
      try {
        if (disposed) return
        const current = load(workspace, task.id)
        if (current.execution.id !== id) return
        let next
        try {
          if (!result?.error && current.state === 'running') readBoundMaterial(workspace, current, catalog)
          next = result?.error ? settle(current, id, result) : publish(workspace, current, result)
        }
        catch (error) { next = settle(current, id, { error: error.message }) }
        save(workspace, next)
      } finally {
        active.delete(task.id)
      }
    })().catch(error => console.error('设计工作台无法持久化阶段回执：' + (error.code ?? '存储错误')))
  }
  return {
    dispose() {
      disposed = true
      for (const [taskId, controller] of active) { controller.abort(); cancelStage(taskId) }
    },
    async fetch(request) {
      const json = (data, status = 200) => Response.json(data, { status, headers: { 'Cache-Control': 'no-store' } })
      const url = new URL(request.url)
      try {
        if (request.method === 'GET' && !url.searchParams.has('workspace')) {
          return json({
            workspaces: registry.list().map(({ id, title, path }) => ({ id, title, path })),
            catalog: catalog.list(),
          })
        }
        let body
        if (request.method === 'POST') {
          if (!/^application\/json(?:;|$)/i.test(request.headers.get('content-type') ?? '')) return json({ error: '请求格式无效' }, 415)
          body = await request.json()
        }
        const workspace = registry.get(body?.workspaceId ?? url.searchParams.get('workspace'))
        if (!workspace) throw new Error('请选择已在 Harness 登记的工作区')
        if (request.method === 'GET') {
          if (!url.searchParams.has('task')) return json({ tasks: list(workspace) })
          const task = load(workspace, url.searchParams.get('task'))
          const kind = url.searchParams.get('artifact')
          if (!kind || !task.artifacts[kind]) throw new Error('该产物尚未登记')
          const material = readMaterial(workspace.path, task.artifacts[kind].path)
          if (material.sha256 !== task.artifacts[kind].sha256) throw new Error('已登记产物被修改')
          if (url.searchParams.get('preview')) {
            return new Response(renderPreview(material.content, task.title + ' · ' + catalog.name(kind)), {
              headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' },
            })
          }
          return json({ content: material.content })
        }
        if (body.action === 'create') {
          if (typeof body.title !== 'string' || !body.title.trim() || body.title.length > 200) throw new Error('请输入不超过 200 字的任务名')
          const { content, ...input } = readMaterial(workspace.path, body.path)
          return json({ task: view(save(workspace, newTask(workspace.id, body.title, input)), catalog) })
        }
        const current = load(workspace, body.taskId)
        const next = dispatch(current, body, catalog.available(Object.keys(current.artifacts)))
        if (next !== current) {
          save(workspace, next)
          if (next.state === 'running') launch(workspace, next)
          if (next.state === 'cancelling') {
            active.get(next.id)?.abort()
            cancelStage(next.id)
          }
        }
        return json({ task: view(next, catalog) })
      } catch (error) {
        return json({ error: error?.message || '工作台请求失败' }, 400)
      }
    },
  }
}
