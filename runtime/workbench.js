import { createHash, randomUUID } from 'node:crypto'
import { lstatSync, mkdirSync, readFileSync, realpathSync, renameSync, unlinkSync, writeFileSync } from 'node:fs'
import { isAbsolute, join, relative, resolve, sep } from 'node:path'
import { completedFor, emptyManifest } from './state.js'
import { validateMarkdown } from './artifacts.js'
import { recommendHandoff } from './orchestration.js'

const limit = 320_000
const sessionPattern = /^[A-Za-z0-9._-]{8,100}$/
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

  function windowDir(workspace, sessionId, create) {
    if (!sessionPattern.test(sessionId)) throw new Error('无效的规划窗口标识')
    return directory(workspace.path, ['spark-output', 'design-workbench', sessionId], create)
  }

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

  function oldRuns(workspace, sessionId) {
    try {
      const file = join(baseDir(workspace, false), 'runs.json')
      const info = lstatSync(file)
      if (info.isSymbolicLink() || !info.isFile()) return []
      const rows = JSON.parse(readFileSync(file, 'utf8'))
      if (!Array.isArray(rows)) return []
      const latest = new Map()
      for (const run of rows) {
        if (run?.sessionId !== sessionId || !run.skill || !run.artifactPath) continue
        const previous = latest.get(run.skill)
        if (!previous || (Number(run.version) || 0) > (Number(previous.version) || 0)) latest.set(run.skill, run)
      }
      return [...latest.values()].map(run => ({
        skill: run.skill,
        path: run.artifactPath,
        sha256: run.sha256,
        title: run.title,
        updatedAt: run.createdAt ?? new Date().toISOString(),
        stale: false,
        staleSince: null,
      }))
    } catch { return [] }
  }

  function loadManifest(workspace, sessionId) {
    try {
      const file = join(windowDir(workspace, sessionId, false), 'manifest.json')
      const info = lstatSync(file)
      if (info.isSymbolicLink() || !info.isFile()) return emptyManifest(workspace.id, sessionId)
      const parsed = JSON.parse(readFileSync(file, 'utf8'))
      if (!parsed || parsed.sessionId !== sessionId || typeof parsed.skills !== 'object' || parsed.skills === null) {
        return emptyManifest(workspace.id, sessionId)
      }
      return {
        version: 1,
        workspaceId: workspace.id,
        sessionId,
        updatedAt: parsed.updatedAt ?? new Date().toISOString(),
        skills: parsed.skills,
      }
    } catch {
      const manifest = emptyManifest(workspace.id, sessionId)
      for (const entry of oldRuns(workspace, sessionId)) manifest.skills[entry.skill] = entry
      return manifest
    }
  }

  function saveManifest(workspace, sessionId, manifest) {
    manifest.updatedAt = new Date().toISOString()
    const dir = windowDir(workspace, sessionId, true)
    atomicWrite(dir, 'manifest.json', JSON.stringify(manifest))
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

  async function submit({ skill, markdown, title }, callerSessionId) {
    if (!callerSessionId) throw new Error('无法确认调用会话')
    if (!knownSkills.has(skill)) throw new Error('未知 Skill：' + skill)
    const workspace = await workspaceForSession(callerSessionId)
    validateMarkdown(skill, markdown)
    const bytes = Buffer.from(markdown)
    if (!bytes.length || bytes.length > limit) throw new Error('产物为空或超过 320 KB')
    return serialize(workspace.id, () => {
      const dir = windowDir(workspace, callerSessionId, true)
      const name = skill + '.md'
      atomicWrite(dir, name, bytes)
      const manifest = loadManifest(workspace, callerSessionId)
      const now = new Date().toISOString()
      const sha256 = digest(bytes)
      const previous = manifest.skills[skill]
      const changed = !previous || previous.sha256 !== sha256
      manifest.skills[skill] = {
        skill,
        path: relative(workspace.path, join(dir, name)).split(sep).join('/'),
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
      saveManifest(workspace, callerSessionId, manifest)
      return {
        registered: true,
        skill,
        path: manifest.skills[skill].path,
        stale: Object.entries(manifest.skills).filter(([, entry]) => entry.stale).map(([id]) => id),
        next: catalog.recommend(completedFor(manifest), skill),
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
        throw new Error('未知操作')
      }
      const sessionId = url.searchParams.get('session') ?? ''
      if (url.searchParams.has('skill')) {
        if (!sessionId) throw new Error('缺少规划窗口')
        const manifest = loadManifest(workspace, sessionId)
        const entry = manifest.skills[url.searchParams.get('skill')]
        if (!entry) throw new Error('该 Skill 尚未在本窗口登记产物')
        const requested = resolve(workspace.path, entry.path)
        contained(workspace.path, requested)
        const real = realpathSync(requested)
        contained(workspace.path, real)
        const info = lstatSync(real)
        if (!info.isFile() || info.isSymbolicLink()) throw new Error('产物必须是普通文件')
        const bytes = readFileSync(real)
        if (digest(bytes) !== entry.sha256) throw new Error('已登记产物被修改')
        return json({ content: bytes.toString('utf8'), artifact: entry })
      }
      const manifest = sessionId ? loadManifest(workspace, sessionId) : null
      const latest = manifest
        ? Object.values(manifest.skills).sort((a, b) => String(b.updatedAt).localeCompare(String(a.updatedAt)))[0]
        : undefined
      const next = latest ? recommendHandoff(completedFor(manifest), latest.skill) : []
      return json({ sessions: await listSessions(workspace), manifest, next })
    } catch (error) {
      return json({ error: error?.message || '工作台请求失败' }, 400)
    }
  }

  return { fetch, submit, dispose() {} }
}
