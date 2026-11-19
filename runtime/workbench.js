import { createHash, randomUUID } from 'node:crypto'
import { cpSync, existsSync, lstatSync, mkdirSync, readFileSync, readdirSync, realpathSync, renameSync, unlinkSync, writeFileSync } from 'node:fs'
import { isAbsolute, join, relative, resolve, sep } from 'node:path'
import { completedFor, emptyManifest, normalizeSkillId } from './state.js'
import { validateMarkdown } from './artifacts.js'
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
  const knownSkills = new Set(catalog.list().map(skill => skill.id))
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
        legacyMigrated: parsed.legacyMigrated === true,
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

  async function listSessions(workspace) {
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
      .filter(row => row.id && row.origin !== 'subagent' && !row.blank && !archived.has(row.id) &&
        (workspace.sessionIds?.includes(row.id) ?? false))
      .sort((a, b) => (Number(b.updatedAt) || Date.parse(b.updatedAt) || 0) - (Number(a.updatedAt) || Date.parse(a.updatedAt) || 0))
  }

  async function createSession(workspace) {
    const value = await ctx.sessionController.create({ workspaceId: workspace.id })
    const created = value?.ok === true ? value.value : value
    if (!created?.sessionId) throw new Error(value?.error?.message || '无法创建会话')
    return created.sessionId
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

  function migrateLegacy(workspace, index) {
    if (index.legacyMigrated) return false
    let changed = false
    let entries
    try { entries = readdirSync(baseDir(workspace, false), { withFileTypes: true }) }
    catch { index.legacyMigrated = true; return true }
    for (const entry of entries) {
      if (!entry.isDirectory() || taskPattern.test(entry.name)) continue
      const legacyId = 'T-legacy-' + createHash('sha1').update(entry.name).digest('hex').slice(0, 8)
      if (index.tasks.some(task => task.id === legacyId)) continue
      const source = join(baseDir(workspace, false), entry.name)
      const target = taskDir(workspace, legacyId, true)
      try {
        for (const child of readdirSync(source, { withFileTypes: true })) {
          cpSync(join(source, child.name), join(target, child.name), { recursive: true, force: true })
        }
      } catch { continue }
      const manifestFile = join(target, 'manifest.json')
      const manifest = emptyManifest(workspace.id, legacyId, entry.name)
      let files = []
      try { files = readdirSync(target).filter(name => name.endsWith('.md')) } catch {}
      if (existsSync(manifestFile)) {
        try {
          const parsed = JSON.parse(readFileSync(manifestFile, 'utf8'))
          if (parsed && typeof parsed.skills === 'object') {
            for (const [oldSkill, value] of Object.entries(parsed.skills)) {
              const skill = normalizeSkillId(oldSkill)
              if (oldSkill === 'uxb' && parsed.skills.uxs) continue
              if (!knownSkills.has(skill) || !value?.path) continue
              const name = String(value.path).split(/[\\/]/).pop()
              const file = join(target, name)
              if (!existsSync(file)) continue
              const bytes = readFileSync(file)
              manifest.skills[skill] = {
                skill,
                path: relative(workspace.path, file).split(sep).join('/'),
                sha256: digest(bytes),
                title: value.title ?? '',
                updatedAt: value.updatedAt ?? new Date().toISOString(),
                stale: false,
                staleSince: null,
              }
            }
          }
        } catch {}
      }
      for (const name of files) {
        if (name === 'uxb.md' && files.includes('uxs.md')) continue
        const skill = normalizeSkillId(name.replace(/\.md$/, ''))
        if (!knownSkills.has(skill) || manifest.skills[skill]) continue
        const bytes = readFileSync(join(target, name))
        manifest.skills[skill] = {
          skill,
          path: relative(workspace.path, join(target, name)).split(sep).join('/'),
          sha256: digest(bytes),
          title: '',
          updatedAt: new Date().toISOString(),
          stale: false,
          staleSince: null,
        }
      }
      saveManifest(workspace, legacyId, manifest)
      const skills = Object.keys(manifest.skills)
      index.tasks.push({
        id: legacyId,
        title: '历史任务 · ' + entry.name.slice(-8),
        status: 'completed',
        sessionId: entry.name,
        segments: [{ startSeq: 0, endSeq: 0 }],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        skills,
        lastSkill: latestSkill(manifest) ?? null,
      })
      changed = true
    }
    index.legacyMigrated = true
    return true
  }

  function loadIndex(workspace) {
    let index = readIndexFile(workspace)
    if (!index) index = { version: 1, next: 1, legacyMigrated: false, tasks: [] }
    const changed = migrateLegacy(workspace, index)
    if (changed) saveIndex(workspace, index)
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
      '',
      String(text ?? '').trim() || '请按该 Skill 的规则继续本轮任务。',
      '',
      '完成后必须调用 submit_design_artifact 登记产物：',
      '  taskId: ' + task.id,
      '  skill: ' + skill,
      '  markdown: 完整 Markdown 正文',
    ].join('\n')
  }

  async function createTask(workspace, body) {
    const skill = normalizeSkillId(String(body.skill ?? ''))
    if (!knownSkills.has(skill)) throw new Error('请选择有效的 Skill')
    const sessionId = String(body.sessionId ?? '')
    if (!sessionPattern.test(sessionId)) throw new Error('请选择会话')
    const sessions = await listSessions(workspace)
    if (!sessions.some(session => session.id === sessionId)) throw new Error('所选会话不属于当前工作区')
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
      title: String(body.title ?? '').trim().slice(0, 80) || catalog.name(skill),
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
      const bytes = Buffer.from(markdown)
      if (!bytes.length || bytes.length > limit) throw new Error('产物为空或超过 320 KB')
      const file = taskPath(workspace, taskId, skill)
      atomicWrite(taskDir(workspace, taskId, true), skill + '.md', bytes)
      const manifest = loadManifest(workspace, taskId)
      const sha256 = digest(bytes)
      const previous = manifest.skills[skill]
      const changed = !previous || previous.sha256 !== sha256
      const now = new Date().toISOString()
      manifest.skills[skill] = {
        skill,
        path: relative(workspace.path, file).split(sep).join('/'),
        sha256,
        title: title?.trim() || previous?.title || '',
        updatedAt: now,
        stale: false,
        staleSince: null,
      }
      if (changed) {
        const affected = new Set([skill])
        for (const [id, entry] of Object.entries(manifest.skills)) {
          if (id !== skill && entry.stale) affected.add(id)
        }
        let found = true
        while (found) {
          found = false
          for (const [id, entry] of Object.entries(manifest.skills)) {
            if (id === skill || entry.stale) continue
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
        path: manifest.skills[skill].path,
        stale: Object.entries(manifest.skills).filter(([, entry]) => entry.stale).map(([id]) => id),
        next: recommendHandoff(completedFor(manifest), skill),
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
        if (url.searchParams.has('skill')) {
          const entry = manifest.skills[normalizeSkillId(url.searchParams.get('skill'))]
          if (!entry) throw new Error('该 Skill 尚未登记产物')
          const requested = resolve(workspace.path, entry.path)
          contained(workspace.path, requested)
          const real = realpathSync(requested)
          contained(workspace.path, real)
          const info = lstatSync(real)
          if (!info.isFile() || info.isSymbolicLink()) throw new Error('产物必须是普通文件')
          const bytes = readFileSync(real)
          if (digest(bytes) !== entry.sha256) throw new Error('产物被修改')
          return json({ content: bytes.toString('utf8'), artifact: entry })
        }
        return json({
          task: summary(task),
          manifest,
          next: task.lastSkill ? recommendHandoff(completedFor(manifest), task.lastSkill) : [],
        })
      }
      return json({ sessions: await listSessions(workspace), tasks: loadIndex(workspace).tasks.map(summary) })
    } catch (error) {
      return json({ error: error?.message || '工作台请求失败' }, 400)
    }
  }

  return { fetch, submit, dispose() {} }
}
