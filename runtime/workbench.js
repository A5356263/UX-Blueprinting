import { createHash, randomUUID } from 'node:crypto'
import { existsSync, lstatSync, mkdirSync, readFileSync, realpathSync, renameSync, unlinkSync, writeFileSync } from 'node:fs'
import { isAbsolute, join, relative, resolve, sep } from 'node:path'
import { completedFor, emptyManifest, normalizeSkillId } from './state.js'
import { classifyPrdReview, validateMarkdown } from './artifacts.js'
import { recommendHandoff } from './orchestration.js'

const limit = 320_000
const sessionPattern = /^[A-Za-z0-9._-]{8,120}$/
const taskPattern = /^T-[A-Za-z0-9-]{4,100}$/
const digest = data => createHash('sha256').update(data).digest('hex')

function contained(root, path) {
  const local = relative(root, path)
  if (!local || local === '..' || local.startsWith('..' + sep) || isAbsolute(local)) {
    throw new Error('文件必须位于已选工作区')
  }
  return local
}

function sameDirectory(root, path) {
  const local = relative(resolve(root), resolve(path))
  return local === '' || (local !== '..' && !local.startsWith('..' + sep) && !isAbsolute(local))
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

export function createWorkbench(ctx, catalog) {
  const registry = ctx.workspaceRegistry
  const skills = catalog.list()
  const knownSkills = new Set(skills.map(skill => skill.id))
  const skillNames = new Set(skills.map(skill => skill.name))
  const queues = new Map()

  function serialize(key, task) {
    const previous = queues.get(key) ?? Promise.resolve()
    const current = previous.then(task, task)
    queues.set(key, current.then(() => {}, () => {}))
    return current
  }

  const baseDir = (workspace, create) => directory(workspace.path, ['spark-output', 'design-workbench'], create)
  const taskDir = (workspace, taskId, create) => {
    if (!taskPattern.test(taskId)) throw new Error('无效的任务标识')
    return directory(workspace.path, ['spark-output', 'design-workbench', taskId], create)
  }
  const indexFile = workspace => join(baseDir(workspace, false), 'tasks.json')

  function atomicWrite(dir, name, bytes) {
    const target = join(dir, name)
    try {
      const info = lstatSync(target)
      if (info.isSymbolicLink() || !info.isFile()) throw new Error('目标必须是普通文件')
    } catch (error) {
      if (error.code !== 'ENOENT') throw error
    }
    const temporary = join(dir, '.' + name + '-' + randomUUID() + '.tmp')
    writeFileSync(temporary, bytes, { flag: 'wx' })
    try { renameSync(temporary, target) } catch (error) {
      try { unlinkSync(temporary) } catch {}
      throw error
    }
  }

  function readIndexFile(workspace) {
    try {
      const file = indexFile(workspace)
      const info = lstatSync(file)
      if (info.isSymbolicLink() || !info.isFile()) return null
      const parsed = JSON.parse(readFileSync(file, 'utf8'))
      if (!parsed || parsed.version !== 1 || !Array.isArray(parsed.tasks)) return null
      return {
        version: 1,
        next: Number.isSafeInteger(parsed.next) && parsed.next > 0 ? parsed.next : 1,
        tasks: parsed.tasks.filter(task => task && taskPattern.test(task.id)).map(task => ({
          ...task,
          skills: [...new Set((task.skills ?? []).map(normalizeSkillId))],
          lastSkill: normalizeSkillId(task.lastSkill),
        })),
      }
    } catch { return null }
  }

  function saveIndex(workspace, index) {
    atomicWrite(baseDir(workspace, true), 'tasks.json', JSON.stringify(index))
  }

  async function listSessions(workspace, includeBlank = false) {
    const controller = ctx.sessionController
    if (typeof controller?.list !== 'function') return []
    let value
    try { value = await controller.list({}, AbortSignal.timeout(5000)) } catch { return [] }
    if (value?.ok === true) value = value.value
    if (value?.ok === false) return []
    const rows = value?.items ?? value?.rows ?? value?.sessions ?? (Array.isArray(value) ? value : [])
    const archived = new Set(registry.archivedSessionIds ?? [])
    return rows
      .map(row => ({
        id: row?.sessionId ?? row?.id,
        title: row?.projections?.values?.title || '未命名会话',
        cwd: row?.cwd ?? null,
        updatedAt: row?.updatedAt ?? row?.time ?? null,
        origin: row?.origin ?? null,
        blank: row?.blank === true,
      }))
      .filter(row => row.id && row.origin !== 'subagent' && (includeBlank || !row.blank) && !archived.has(row.id) &&
        (workspace.sessionIds?.includes(row.id) ||
          Boolean(row.cwd && sameDirectory(workspace.path, row.cwd))))
      .sort((a, b) => (Number(b.updatedAt) || Date.parse(b.updatedAt) || 0) - (Number(a.updatedAt) || Date.parse(a.updatedAt) || 0))
  }

  async function createSession(workspace) {
    const value = await ctx.sessionController.create({ workspaceId: workspace.id })
    const created = value?.ok === true ? value.value : value
    if (!created?.sessionId) throw new Error(value?.error?.message || '无法创建会话')
    return created.sessionId
  }

  async function sessionBelongs(workspace, sessionId) {
    if (workspace.sessionIds?.includes(sessionId)) return true
    const live = ctx.sessions?.get?.(sessionId)
    const cwd = live?.header?.cwd ?? live?.cwd
    if (cwd && sameDirectory(workspace.path, cwd)) return true
    const sessions = await listSessions(workspace, true)
    return sessions.some(session => session.id === sessionId)
  }

  async function workspaceForSession(sessionId) {
    const workspaces = registry.list()
    const registered = workspaces.find(item => item.sessionIds?.includes(sessionId))
    if (registered) return registered
    const live = ctx.sessions?.get?.(sessionId)
    const cwd = live?.header?.cwd ?? live?.cwd
    if (cwd) {
      const workspace = workspaces.find(item => sameDirectory(item.path, cwd))
      if (workspace) return workspace
    }
    for (const workspace of workspaces) {
      const sessions = await listSessions(workspace)
      if (sessions.some(session => session.id === sessionId)) return workspace
    }
    throw new Error('该会话不属于任何已登记工作区')
  }

  function seqOf(sessionId) {
    const live = ctx.sessions?.get?.(sessionId)
    return Number.isSafeInteger(live?.seq) ? live.seq : 0
  }

  function taskPath(workspace, taskId, skill) {
    const dir = taskDir(workspace, taskId, true)
    return join(dir, skill + '.md')
  }

  function loadManifest(workspace, taskId) {
    try {
      const file = join(taskDir(workspace, taskId, false), 'manifest.json')
      const info = lstatSync(file)
      if (info.isSymbolicLink() || !info.isFile()) return emptyManifest(workspace.id, taskId)
      const parsed = JSON.parse(readFileSync(file, 'utf8'))
      if (!parsed || parsed.taskId !== taskId || typeof parsed.skills !== 'object' || parsed.skills === null) {
        return emptyManifest(workspace.id, taskId)
      }
      const skills = { ...parsed.skills }
      if (skills.uxb) {
        if (!skills.uxs) skills.uxs = { ...skills.uxb, skill: 'uxs' }
        delete skills.uxb
      }
      return {
        version: 1,
        workspaceId: workspace.id,
        taskId,
        sessionId: parsed.sessionId ?? '',
        updatedAt: parsed.updatedAt ?? new Date().toISOString(),
        skills,
      }
    } catch { return emptyManifest(workspace.id, taskId) }
  }

  function saveManifest(workspace, taskId, manifest) {
    manifest.updatedAt = new Date().toISOString()
    atomicWrite(taskDir(workspace, taskId, true), 'manifest.json', JSON.stringify(manifest))
  }

  function latestSkill(manifest) {
    return Object.values(manifest.skills).sort((a, b) => String(b.updatedAt).localeCompare(String(a.updatedAt)))[0]?.skill
  }

  function nextForTask(task, manifest) {
    const record = manifest.skills['prd-review-record']
    if (!manifest.skills['prd-review'] && record &&
        ['waiting_response', 'no_confirmation_required'].includes(record.reviewStatus)) {
      return [{
        id: 'prd-review',
        name: catalog.name('prd-review'),
        reason: record.reviewStatus === 'waiting_response'
          ? '先回复并关闭审核记录中的待确认项，再复核生成正式基线。'
          : '审核记录已无阻断，复核后生成正式基线。',
      }]
    }
    return task?.lastSkill ? recommendHandoff(completedFor(manifest), task.lastSkill) : []
  }

  function summary(task) {
    return {
      id: task.id,
      title: task.title,
      status: task.status,
      sessionId: task.sessionId,
      segments: task.segments,
      createdAt: task.createdAt,
      updatedAt: task.updatedAt,
      skills: [...new Set((task.skills ?? []).map(normalizeSkillId))],
      lastSkill: task.lastSkill ? normalizeSkillId(task.lastSkill) : null,
    }
  }

  function artifactLabel(key, entry) {
    if (key === 'prd-review-record') return '需求审核记录'
    if (key === 'prd-review') return '正式需求基线'
    return catalog.name(entry.skill ?? key)
  }

  function artifactEditable(task, manifest, key, entry) {
    return task.status === 'active' &&
      key === 'prd-review-record' &&
      entry.artifactKind === 'review-record' &&
      !manifest.skills['prd-review']
  }

  function artifactMeta(workspace, task, manifest, key, entry) {
    return {
      key,
      skill: entry.skill ?? key,
      label: artifactLabel(key, entry),
      artifactKind: entry.artifactKind ?? 'artifact',
      reviewStatus: entry.reviewStatus ?? '',
      editable: artifactEditable(task, manifest, key, entry),
      manualLock: entry.manualLock === true,
      origin: entry.origin ?? 'model',
      stale: entry.stale === true,
      updatedAt: entry.updatedAt ?? '',
      sha256: entry.sha256 ?? '',
      title: entry.title ?? '',
    }
  }

  function artifactList(workspace, task, manifest) {
    return Object.entries(manifest.skills)
      .filter(([, entry]) => {
        try {
          const file = resolve(workspace.path, entry.path)
          contained(workspace.path, file)
          return lstatSync(file).isFile()
        } catch { return false }
      })
      .map(([key, entry]) => ({ ...artifactMeta(workspace, task, manifest, key, entry), key }))
      .sort((a, b) => {
        const rank = key => key === 'prd-review-record' ? 0 : key === 'prd-review' ? 1 : 2
        return rank(a.key) - rank(b.key) || String(b.updatedAt).localeCompare(String(a.updatedAt))
      })
  }

  function loadIndex(workspace) {
    baseDir(workspace, true)
    const index = readIndexFile(workspace) ?? { version: 1, next: 1, tasks: [] }
    if (migrateTaskTitles(index)) saveIndex(workspace, index)
    return index
  }

  function pauseOthers(workspace, index, exceptId) {
    let changed = false
    const now = new Date().toISOString()
    for (const task of index.tasks) {
      if (task.id === exceptId || task.status !== 'active') continue
      const last = task.segments?.[task.segments.length - 1]
      if (last && last.endSeq === null) last.endSeq = seqOf(task.sessionId)
      task.status = 'paused'
      task.updatedAt = now
      changed = true
    }
    return changed
  }

  function promptFor(task, skill, text) {
    return [
      '【设计工作台任务 ' + task.id + '】',
      '任务：' + task.title,
      '本轮 Skill：' + skill + '（' + catalog.name(skill) + '）',
      '任务目录：spark-output/design-workbench/' + task.id + '/',
      '禁止直接写 spark-output/ 根目录；正式产物只能通过 submit_design_artifact 登记。',
      '读取上游时优先读任务目录内文件，不要读写 spark-output/ 根目录副本。',
      '',
      String(text ?? '').trim() || '请按该 Skill 的规则继续本轮任务。',
      '',
      '完成任务后必须调用 submit_design_artifact 登记产物：',
      '  taskId: ' + task.id,
      '  skill: ' + skill,
      '  markdown: 完整 Markdown 正文',
      '  title: 当前产物的名称（可省略）',
      skill === 'prd-review' ? '若存在阻断或建议，按「PRD 审核记录」格式提交；工作台会保存为 prd-review-record.md，正式基线仍写入 prd-review.md。' : '',
    ].join('\n')
  }

  function stripLegacySkillTitle(value) {
    const title = typeof value === 'string' ? value.trim() : ''
    if (skillNames.has(title)) return ''
    const separator = title.indexOf(' · ')
    if (separator >= 0 && skillNames.has(title.slice(0, separator))) {
      return title.slice(separator + 3).trim()
    }
    return title
  }

  function migrateTaskTitles(index) {
    let changed = false
    for (const task of index.tasks) {
      if (task.titleSource !== 'auto' && task.titleSource !== 'ai') continue
      task.title = stripLegacySkillTitle(task.title) || task.id
      task.titleSource = 'legacy'
      changed = true
    }
    return changed
  }

  function titleFromInput(body, taskId) {
    const firstLine = typeof body.text === 'string' ? body.text.trim().split(/\r\n?|\n/, 1)[0].trim().replace(/\s+/g, ' ') : ''
    const fileName = typeof body.fileName === 'string' ? body.fileName.trim() : ''
    const title = firstLine || fileName || stripLegacySkillTitle(body.title) || taskId
    const chars = Array.from(title)
    return chars.length > 36 ? chars.slice(0, 35).join('') + '…' : title
  }

  async function createTask(workspace, body) {
    const skill = normalizeSkillId(String(body.skill ?? ''))
    if (!knownSkills.has(skill)) throw new Error('请选择有效的 Skill')
    const sessionId = String(body.sessionId ?? '')
    if (!sessionPattern.test(sessionId)) throw new Error('请选择会话')
    if (!await sessionBelongs(workspace, sessionId)) throw new Error('所选会话不属于当前工作区')
    const index = loadIndex(workspace)
    pauseOthers(workspace, index, '')
    const now = new Date().toISOString()
    const date = now.slice(0, 10).replace(/-/g, '')
    let id = `T-${date}-${String(index.next).padStart(2, '0')}`
    while (existsSync(join(baseDir(workspace, false), id))) {
      index.next += 1
      id = `T-${date}-${String(index.next).padStart(2, '0')}`
    }
    index.next += 1
    const task = {
      id,
      title: titleFromInput(body, id),
      titleSource: 'input',
      status: 'active',
      sessionId,
      segments: [{ startSeq: seqOf(sessionId), endSeq: null }],
      createdAt: now,
      updatedAt: now,
      skills: [skill],
      lastSkill: skill,
    }
    taskDir(workspace, id, true)
    saveManifest(workspace, id, emptyManifest(workspace.id, id, sessionId))
    index.tasks.push(task)
    saveIndex(workspace, index)
    return { task: summary(task), prompt: promptFor(task, skill, body.text) }
  }

  function findTask(index, taskId) {
    const task = index.tasks.find(item => item.id === taskId)
    if (!task) throw new Error('找不到该任务')
    return task
  }

  async function changeTask(workspace, body, action) {
    const index = loadIndex(workspace)
    const task = findTask(index, String(body.taskId ?? ''))
    const now = new Date().toISOString()
    if (action === 'pause') {
      const last = task.segments?.[task.segments.length - 1]
      if (last && last.endSeq === null) last.endSeq = seqOf(task.sessionId)
      task.status = 'paused'
    } else if (action === 'complete') {
      const last = task.segments?.[task.segments.length - 1]
      if (last && last.endSeq === null) last.endSeq = seqOf(task.sessionId)
      task.status = 'completed'
    } else if (action === 'resume') {
      pauseOthers(workspace, index, task.id)
      task.segments = Array.isArray(task.segments) ? task.segments : []
      task.segments.push({ startSeq: seqOf(task.sessionId), endSeq: null })
      task.status = 'active'
    } else if (action === 'rename') {
      const title = String(body.title ?? '').trim().slice(0, 80)
      if (!title) throw new Error('任务名不能为空')
      task.title = title
      task.titleSource = 'manual'
    }
    task.updatedAt = now
    saveIndex(workspace, index)
    return summary(task)
  }

  async function promptTask(workspace, body) {
    const index = loadIndex(workspace)
    const task = findTask(index, String(body.taskId ?? ''))
    if (task.status !== 'active') throw new Error('任务当前不是进行中，请先恢复')
    const skill = normalizeSkillId(String(body.skill ?? ''))
    if (!knownSkills.has(skill)) throw new Error('请选择有效的 Skill')
    task.skills = [...new Set((Array.isArray(task.skills) ? task.skills : []).map(normalizeSkillId))]
    if (!task.skills.includes(skill)) {
      task.skills.push(skill)
      task.lastSkill = skill
      task.updatedAt = new Date().toISOString()
      saveIndex(workspace, index)
    }
    return { prompt: promptFor(task, skill, body.text) }
  }

  async function updateArtifact(workspace, body) {
    const index = loadIndex(workspace)
    const task = findTask(index, String(body.taskId ?? ''))
    if (task.status !== 'active') throw Object.assign(new Error('任务不是进行中，不能编辑产物'), { status: 400 })
    const manifest = loadManifest(workspace, task.id)
    const key = String(body.artifactKey ?? '')
    const entry = manifest.skills[key]
    if (!entry) throw Object.assign(new Error('找不到该产物'), { status: 404 })
    if (!artifactEditable(task, manifest, key, entry)) {
      throw Object.assign(new Error('该产物当前不可编辑'), { status: 400 })
    }
    if (!body.baseSha || body.baseSha !== entry.sha256) {
      throw Object.assign(new Error('产物已被更新，请重新加载后再保存'), { status: 409 })
    }
    const skill = normalizeSkillId(entry.skill ?? key)
    validateMarkdown(skill, body.markdown)
    const review = skill === 'prd-review' ? classifyPrdReview(body.markdown) : null
    if (entry.artifactKind === 'review-record' && review?.kind !== 'review-record') {
      throw Object.assign(new Error('审核记录必须保持「PRD 审核记录」格式'), { status: 400 })
    }
    const bytes = Buffer.from(body.markdown)
    if (!bytes.length || bytes.length > limit) throw new Error('产物为空或超过 320 KB')
    const file = taskPath(workspace, task.id, key)
    atomicWrite(taskDir(workspace, task.id, true), key + '.md', bytes)
    const now = new Date().toISOString()
    manifest.skills[key] = {
      ...entry,
      sha256: digest(bytes),
      updatedAt: now,
      origin: 'user',
      editedAt: now,
      manualLock: true,
      reviewStatus: review?.status ?? entry.reviewStatus ?? '',
      path: relative(workspace.path, file).split(sep).join('/'),
      stale: false,
      staleSince: null,
    }
    saveManifest(workspace, task.id, manifest)
    task.skills = [...new Set([...(task.skills ?? []).map(normalizeSkillId), skill])]
    task.lastSkill = skill
    task.updatedAt = now
    saveIndex(workspace, index)
    return { artifact: artifactMeta(workspace, task, manifest, key, manifest.skills[key]), next: nextForTask(task, manifest) }
  }

  async function message(workspace, body) {
    const index = loadIndex(workspace)
    const task = findTask(index, String(body.taskId ?? ''))
    if (task.status !== 'active') throw new Error('任务不是进行中，不能发送消息')
    const key = String(body.artifactKey ?? '')
    if (key) {
      const manifest = loadManifest(workspace, task.id)
      const entry = manifest.skills[key]
      if (entry?.manualLock) {
        entry.manualLock = false
        saveManifest(workspace, task.id, manifest)
        task.updatedAt = new Date().toISOString()
        saveIndex(workspace, index)
      }
    }
    return { ok: true }
  }

  async function submit({ taskId, skill, markdown, title }, callerSessionId) {
    skill = normalizeSkillId(skill)
    if (!callerSessionId) throw new Error('无法确认调用会话')
    if (!knownSkills.has(skill)) throw new Error('未知 Skill：' + skill)
    const workspace = await workspaceForSession(callerSessionId)
    return serialize(workspace.id + ':' + taskId, () => {
      const index = loadIndex(workspace)
      const task = findTask(index, taskId)
      if (task.status !== 'active') throw new Error('任务不是进行中，不能登记产物')
      if (task.sessionId !== callerSessionId) throw new Error('产物必须由任务绑定的会话登记')
      validateMarkdown(skill, markdown)
      const review = skill === 'prd-review' ? classifyPrdReview(markdown) : null
      const artifactKind = review?.kind === 'review-record' ? 'review-record' : review?.kind === 'baseline' ? 'baseline' : 'artifact'
      const artifactKey = artifactKind === 'review-record' ? 'prd-review-record' : skill
      const manifest = loadManifest(workspace, taskId)
      const previous = manifest.skills[artifactKey]
      if (previous?.manualLock) {
        throw new Error('该产物已被人工编辑，请先通过任务页底部输入框发送下一条消息，再继续')
      }
      const bytes = Buffer.from(markdown)
      if (!bytes.length || bytes.length > limit) throw new Error('产物为空或超过 320 KB')
      const file = taskPath(workspace, taskId, artifactKey)
      atomicWrite(taskDir(workspace, taskId, true), artifactKey + '.md', bytes)
      const sha256 = digest(bytes)
      const changed = !previous || previous.sha256 !== sha256
      const now = new Date().toISOString()
      manifest.skills[artifactKey] = {
        skill,
        artifactKind,
        reviewStatus: review?.status ?? '',
        origin: 'model',
        manualLock: false,
        editedAt: null,
        path: relative(workspace.path, file).split(sep).join('/'),
        sha256,
        title: title?.trim() || previous?.title || '',
        updatedAt: now,
        stale: false,
        staleSince: null,
      }
      if (changed) {
        const affected = new Set([artifactKey])
        for (const [id, entry] of Object.entries(manifest.skills)) {
          if (id !== artifactKey && entry.stale) affected.add(id)
        }
        let found = true
        while (found) {
          found = false
          for (const [id, entry] of Object.entries(manifest.skills)) {
            if (id === artifactKey || entry.stale) continue
            const reads = typeof catalog.reads === 'function' ? (catalog.reads(id) ?? []) : []
            if (reads.some(dep => affected.has(dep))) {
              entry.stale = true
              entry.staleSince = now
              affected.add(id)
              found = true
            }
          }
        }
      }
      saveManifest(workspace, taskId, manifest)
      task.skills = [...new Set([...(task.skills ?? []).map(normalizeSkillId), skill])]
      task.lastSkill = skill
      task.updatedAt = now
      saveIndex(workspace, index)
      return {
        registered: true,
        taskId,
        skill,
        artifactKind,
        reviewStatus: review?.status ?? '',
        path: manifest.skills[artifactKey].path,
        stale: Object.entries(manifest.skills).filter(([, entry]) => entry.stale).map(([id]) => id),
        next: nextForTask(task, manifest),
      }
    })
  }

  async function fetch(request) {
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
      if (request.method === 'POST') {
        if (body.action === 'create-session') return json({ sessionId: await createSession(workspace) })
        if (body.action === 'create-task') return json(await createTask(workspace, body))
        if (body.action === 'prompt') return json(await promptTask(workspace, body))
        if (body.action === 'update-artifact') return json(await updateArtifact(workspace, body))
        if (body.action === 'message') return json(await message(workspace, body))
        if (['pause', 'complete', 'resume', 'rename'].includes(body.action)) {
          return json({ task: await changeTask(workspace, body, body.action) })
        }
        throw new Error('未知操作')
      }
      const taskId = url.searchParams.get('task') ?? ''
      if (taskId) {
        const index = loadIndex(workspace)
        const task = findTask(index, taskId)
        const manifest = loadManifest(workspace, taskId)
        if (url.searchParams.has('artifact') || url.searchParams.has('skill')) {
          const requestedKey = url.searchParams.get('artifact') ?? normalizeSkillId(url.searchParams.get('skill'))
          const entry = manifest.skills[requestedKey]
          if (!entry) throw new Error('该产物尚未登记')
          const requested = resolve(workspace.path, entry.path)
          contained(workspace.path, requested)
          const real = realpathSync(requested)
          contained(workspace.path, real)
          const info = lstatSync(real)
          if (!info.isFile() || info.isSymbolicLink()) throw new Error('产物必须是普通文件')
          const bytes = readFileSync(real)
          if (digest(bytes) !== entry.sha256) throw new Error('产物被修改')
          return json({ content: bytes.toString('utf8'), artifact: artifactMeta(workspace, task, manifest, requestedKey, entry) })
        }
        return json({
          task: summary(task),
          manifest,
          artifacts: artifactList(workspace, task, manifest),
          next: nextForTask(task, manifest),
        })
      }
      return json({ sessions: await listSessions(workspace), tasks: loadIndex(workspace).tasks.map(summary) })
    } catch (error) {
      return json({ error: error?.message || '工作台请求失败' }, error?.status || 400)
    }
  }

  return { fetch, submit, dispose() {} }
}
