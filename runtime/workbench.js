import { execFile } from 'node:child_process'
import { createHash, randomUUID } from 'node:crypto'
import { existsSync, lstatSync, mkdirSync, readFileSync, realpathSync, renameSync, unlinkSync, writeFileSync } from 'node:fs'
import { isAbsolute, join, relative, resolve, sep } from 'node:path'
import { promisify } from 'node:util'
import { completedFor, emptyManifest, normalizeSkillId } from './state.js'
import { classifyPrdReview, validateMarkdown } from './artifacts.js'
import { recommendHandoff } from './orchestration.js'
import { inspectPrototype, preparePrototype, rankPrototypes } from './prototype-reuse.js'

const limit = 320_000
const sessionPattern = /^[A-Za-z0-9._-]{8,120}$/
const taskPattern = /^T-[A-Za-z0-9-]{4,100}$/
const digest = data => createHash('sha256').update(data).digest('hex')
const confirmationSkills = new Set(['uxs', 'board'])
const closingSkills = new Set(['uxs', 'ux-proto-g', 'solution-swimlane', 'edge', 'board'])
const swimlanePath = 'solution-swimlane/solution_swimlane.html'
const pendingStatuses = ['waiting_response', 'ready_for_confirmation']
const execFileAsync = promisify(execFile)

function openDesktopPath(path) {
  if (process.platform === 'win32') {
    const executable = join(process.env.SystemRoot ?? 'C:/Windows', 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe')
    // Pass the verified path as data so spaces and special characters stay literal.
    const command = "$ErrorActionPreference = 'Stop'; $launch = [System.Diagnostics.ProcessStartInfo]::new(); " +
      '$launch.FileName = $env:UXBP_PREVIEW_PATH; $launch.UseShellExecute = $true; [System.Diagnostics.Process]::Start($launch) | Out-Null'
    return execFileAsync(executable, ['-NoProfile', '-NonInteractive', '-Command', command], {
      windowsHide: true, timeout: 8000, env: { ...process.env, UXBP_PREVIEW_PATH: path },
    })
  }
  return process.platform === 'darwin'
    ? execFileAsync('/usr/bin/open', ['--', path], { timeout: 8000 })
    : execFileAsync('xdg-open', [path], { timeout: 8000 })
}

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
  const renamedSkillArtifactLabels = new Map([
    ['uxs', '体验策略'],
    ['problem-framing', '问题与业务方案'],
    ['page-spec', '页面规格'],
    ['ux-proto-g', '交互原型'],
  ])
  const skillNames = new Set([...skills.map(skill => skill.name), '需求审核与基线', ...renamedSkillArtifactLabels.values()])
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
      round: task.round ?? null,
    }
  }

  function artifactLabel(key, entry) {
    if (key === 'prd-review-record') return '需求审核记录'
    if (key === 'prd-review') return '正式需求基线'
    const skill = normalizeSkillId(entry.skill ?? key)
    return renamedSkillArtifactLabels.get(skill) ?? catalog.name(skill)
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
      format: entry.format ?? 'markdown',
    }
  }

  function readArtifact(workspace, taskId, entry) {
    const dir = taskDir(workspace, taskId, false)
    const requested = resolve(workspace.path, entry.path)
    contained(dir, realpathSync(requested))
    const info = lstatSync(requested)
    if (!info.isFile() || info.isSymbolicLink()) throw new Error('产物必须是普通文件')
    const bytes = readFileSync(requested)
    if (digest(bytes) !== entry.sha256) throw new Error('产物被修改')
    return bytes
  }

  async function openPrototype(workspace, taskId) {
    if (!process.versions.electron || process.env.ELECTRON_RUN_AS_NODE !== '1') {
      throw new Error('请在本机 Harness 桌面端打开页面原型')
    }
    const task = findTask(loadIndex(workspace), taskId)
    const entry = loadManifest(workspace, task.id).skills['ux-proto-g']
    if (!entry || entry.stale) throw new Error('当前任务没有可打开的页面原型')
    readArtifact(workspace, task.id, entry)
    const folder = directory(taskDir(workspace, task.id, false), ['ux-proto-g'], false)
    const index = join(folder, 'index.html')
    try {
      const info = lstatSync(index)
      if (info.isFile() && !info.isSymbolicLink()) {
        contained(folder, realpathSync(index))
        await openDesktopPath(index)
        return { opened: 'browser' }
      }
    } catch {
      // The folder is still useful when the HTML entry is missing or cannot be opened.
    }
    try {
      await openDesktopPath(folder)
      return { opened: 'folder' }
    } catch {
      throw new Error('无法打开原型文件夹：' + folder)
    }
  }

  function artifactList(workspace, task, manifest) {
    return Object.entries(manifest.skills)
      .filter(([, entry]) => {
        try {
          const file = resolve(workspace.path, entry.path)
          contained(taskDir(workspace, task.id, false), realpathSync(file))
          return lstatSync(file).isFile()
        } catch { return false }
      })
      .map(([key, entry]) => ({ ...artifactMeta(workspace, task, manifest, key, entry), key }))
      .sort((a, b) => {
        const order = task.skills ?? []
        const rank = item => {
          const index = order.indexOf(normalizeSkillId(item.key === 'prd-review-record' ? 'prd-review' : item.skill))
          return index < 0 ? order.length : index
        }
        return rank(a) - rank(b) || Number(b.key === 'prd-review-record') - Number(a.key === 'prd-review-record')
      })
  }

  function taskDetail(workspace, task, manifest) {
    const artifacts = artifactList(workspace, task, manifest)
    const record = artifacts.find(item => item.key === 'prd-review-record')
    let reviewReplyReceived = false
    if (record) {
      try {
        const markdown = readArtifact(workspace, task.id, manifest.skills[record.key]).toString('utf8')
        const fields = markdown.matchAll(/^[ \t]*[-*][ \t]+产品回复[：:][ \t]*([^\r\n]*)((?:\r?\n[ \t]+\d+[.)][ \t]+[^\r\n]+)*)/gm)
        reviewReplyReceived = [...fields].some(([, inline, items]) =>
          [inline, ...items.split(/\r?\n/).map(line => line.replace(/^\s*\d+[.)]\s*/, ''))].some(value => {
            const reply = value.trim().replace(/^[`*_]+|[`*_]+$/g, '').trim()
            return reply && !/^(?:无|(?:待|未|尚未|暂无|没有)(?:产品|用户)?(?:回复|确认|提供)|不适用|(?:未|待)填写|[-—…。\.]+)[。.]?$/.test(reply)
          }))
      } catch {}
    }
    const pending = artifacts.find(item => !item.stale && pendingStatuses.includes(item.reviewStatus) &&
      (item.key !== 'prd-review-record' || !manifest.skills['prd-review'])) ?? null
    const current = artifacts.find(item => item.key === task.round?.skill ||
      (task.round?.skill === 'prd-review' && item.key === 'prd-review-record' && !manifest.skills['prd-review']))
    const entry = current && manifest.skills[current.key]
    let output = null
    if (current && !current.stale && entry?.roundId === task.round?.id) {
      try { readArtifact(workspace, task.id, entry); output = current } catch {}
    }
    const finish = task.status === 'active' && !pending && output && closingSkills.has(output.skill) &&
      (!confirmationSkills.has(output.skill) || output.reviewStatus === 'formal') &&
      (output.skill !== 'solution-swimlane' || output.format === 'html') ? output : null
    return { task: summary(task), manifest, artifacts, pending, output, finish, reviewReplyReceived,
      next: pending ? [] : nextForTask(task, manifest) }
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

  function promptFor(task, skill, text, upstream = []) {
    return [
      '【设计工作台任务 ' + task.id + '】',
      '任务：' + task.title,
      '本轮 Skill：' + skill + '（' + catalog.name(skill) + '）',
      '任务目录：spark-output/design-workbench/' + task.id + '/',
      '禁止直接写 spark-output/ 根目录；正式产物只能通过 submit_design_artifact 登记。',
      '读取上游时优先读任务目录内文件，不要读写 spark-output/ 根目录副本。',
      ...upstream.map(entry => '本轮已登记上游产物：' + entry.path),
      skill === 'ux-proto-g' ? '独立原型工作区固定为本任务目录下的 ux-proto-g/。使用列出的正式页面规格及本轮用户材料；只有用户材料时直接使用，遇到影响设计的关键缺口先确认。按 Skill 的发行流程完成本轮构建，成功或降级后提交构建摘要。' : '',
      task.round?.prototype?.sourceId ? '用户已确认复用 ' + task.round.prototype.sourceId + '。工作台已在本轮 ux-proto-g/ 准备底稿。检查现有页面，保留未受影响的模块，只改本轮需求涉及的部分；不要改动历史任务。' : '',
      skill === 'solution-swimlane' ? '本次工作台任务使用已登记的页面规格作为输入。将泳道图 HTML 与 .work 输出定位到本任务目录下的 solution-swimlane/，保留 Skill 中的渲染和校验。只在 HTML 校验通过后登记产物。' : '',
      '',
      String(text ?? '').trim() || '请按该 Skill 的规则继续本轮任务。',
      '',
      '完成任务后必须调用 submit_design_artifact 登记产物：',
      '  taskId: ' + task.id,
      '  skill: ' + skill,
      '  markdown: 完整 Markdown 正文',
      '  title: 当前产物的名称（可省略）',
      skill === 'prd-review' ? '若存在阻断或建议，按「PRD 审核记录」格式提交；工作台会保存为 prd-review-record.md，正式基线仍写入 prd-review.md。' : '',
      skill === 'uxs' ? '将完整可确认的策略稿登记为 stage=confirmation，待用户在工作台确认；若仍需补资料，使用 stage=proposal。' : '',
      skill === 'board' ? '多方案提案登记为 stage=proposal。用户选定方案且完整设计变量已写入后，登记为 stage=confirmation，由用户在工作台确认。' : '',
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
    if (skill === 'ux-proto-g') return startPrototype(workspace, body)
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
      round: { id: randomUUID(), skill, startedAt: Date.now() },
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

  function prototypeUpstream(workspace, task) {
    if (!task) return null
    const manifest = loadManifest(workspace, task.id)
    if (completedFor(manifest).includes('page-spec')) {
      const entry = manifest.skills['page-spec']
      return { taskId: task.id, entry, content: readArtifact(workspace, task.id, entry) }
    }
    const previous = task.round?.prototype?.upstream
    if (!previous) return null
    const entry = loadManifest(workspace, previous.taskId).skills['page-spec']
    if (!entry || entry.stale || entry.sha256 !== previous.sha256) return null
    return { taskId: previous.taskId, entry, content: readArtifact(workspace, previous.taskId, entry) }
  }

  function prototypeCandidate(workspace, task) {
    const manifest = loadManifest(workspace, task.id)
    const artifact = manifest.skills['ux-proto-g']
    if (!artifact) throw new Error('该任务没有已登记的原型')
    const registered = readArtifact(workspace, task.id, artifact).toString('utf8')
    const root = directory(taskDir(workspace, task.id, false), ['ux-proto-g'], false)
    const info = inspectPrototype(root)
    if (!registered.split(/\r?\n/).some(line => line === '- 源码摘要：' + info.sourceDigest)) {
      throw new Error('构建记录和已登记的原型不一致')
    }
    return { id: task.id, title: task.title, version: info.version, updatedAt: artifact.updatedAt ?? task.updatedAt,
      stale: Boolean(artifact.stale), root }
  }

  async function prototypeOptions(workspace, body, compare) {
    const index = loadIndex(workspace)
    const task = body.taskId ? findTask(index, body.taskId) : null
    const candidates = index.tasks.flatMap(item => {
      try {
        const { root, ...candidate } = prototypeCandidate(workspace, item)
        return [candidate]
      } catch { return [] }
    }).sort((a, b) => Number(b.id === task?.id) - Number(a.id === task?.id) ||
      String(b.updatedAt).localeCompare(String(a.updatedAt)))
    if (!compare) return { candidates, fork: Boolean(task && existsSync(join(taskDir(workspace, task.id, false), 'ux-proto-g'))) }
    const upstream = prototypeUpstream(workspace, task)
    const input = { text: String(body.text ?? '').slice(0, 4000),
      files: (Array.isArray(body.files) ? body.files : []).slice(0, 8).map(file => String(file).slice(0, 180)),
      excerpt: String(body.excerpt ?? '').slice(0, 3000),
      pageSpec: upstream?.content.toString('utf8').slice(0, 4500) }
    // Compare a batch of recent candidates. The full list remains available for manual selection.
    const examples = candidates.slice(0, 8).map(item => {
      const history = findTask(index, item.id)
      let pageSpec
      try { pageSpec = prototypeUpstream(workspace, history)?.content.toString('utf8').slice(0, 1500) } catch {}
      return { id: item.id, title: item.title, pageSpec }
    })
    return { recommendations: examples.length ? await rankPrototypes(ctx, input, examples) : [] }
  }

  function startPrototype(workspace, body) {
    return serialize(workspace.id + ':prototype', async () => {
      const choice = body.prototype
      if (!['new', 'reuse'].includes(choice?.mode)) throw new Error('请先确认原型的起点')
      let index = loadIndex(workspace)
      const original = body.taskId ? findTask(index, body.taskId) : null
      const sessionId = String(original?.sessionId ?? body.sessionId ?? '')
      if (original ? original.status !== 'active' : !sessionPattern.test(sessionId) ||
          !await sessionBelongs(workspace, sessionId)) throw new Error('请使用当前工作区的有效会话和进行中任务')
      if (!original) index = loadIndex(workspace)
      const upstream = prototypeUpstream(workspace, original)
      if (!upstream && !String(body.text ?? '').trim() && !body.fileName) throw new Error('请先提供本轮页面需求')
      const candidate = choice.mode === 'reuse'
        ? prototypeCandidate(workspace, findTask(index, choice.sourceId)) : null
      if (candidate && candidate.version !== choice.version) throw new Error('历史原型已更新，请重新选择')
      const now = new Date().toISOString()
      let task = original
      let allocated = index.next
      const fresh = !original || existsSync(join(taskDir(workspace, original.id, false), 'ux-proto-g'))
      if (fresh) {
        const date = now.slice(0, 10).replace(/-/g, '')
        let id
        do { id = `T-${date}-${String(allocated++).padStart(2, '0')}` }
        while (existsSync(join(baseDir(workspace, false), id)))
        task = { id, title: titleFromInput({ ...body, title: original?.title }, id), titleSource: 'input',
          status: 'active', sessionId, segments: [{ startSeq: seqOf(sessionId), endSeq: null }],
          createdAt: now, skills: [] }
      }
      const dir = taskDir(workspace, task.id, true)
      const target = join(dir, 'ux-proto-g')
      try {
        if (candidate) await preparePrototype(candidate.root, target, candidate.version)
        index = loadIndex(workspace)
        if (original) {
          const live = findTask(index, original.id)
          if (live.round?.id !== original.round?.id || live.status !== 'active' ||
              prototypeUpstream(workspace, live)?.entry.sha256 !== upstream?.entry.sha256) {
            throw new Error('任务或上游页面规格已变化，请重新确认')
          }
          if (!fresh) task = live
        }
        if (fresh) {
          saveManifest(workspace, task.id, emptyManifest(workspace.id, task.id, sessionId))
          task.segments[0].startSeq = seqOf(sessionId)
          pauseOthers(workspace, index, '')
          index.tasks.push(task)
          index.next = Math.max(index.next, allocated)
        }
        task.lastSkill = 'ux-proto-g'
        task.skills = [...new Set([...(task.skills ?? []), task.lastSkill])]
        task.updatedAt = new Date().toISOString()
        task.round = { id: randomUUID(), skill: task.lastSkill, startedAt: Date.now(), prototype: {
          mode: choice.mode, sourceId: candidate?.id,
          upstream: upstream && { taskId: upstream.taskId, sha256: upstream.entry.sha256 },
        } }
        saveIndex(workspace, index)
        return { task: summary(task), prompt: promptFor(task, task.lastSkill, body.text, upstream ? [upstream.entry] : []) }
      } catch (error) {
        if (candidate && existsSync(target)) renameSync(target, join(dir, '.prototype-preparation-failed-' + randomUUID()))
        throw error
      }
    })
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
    const manifest = loadManifest(workspace, task.id)
    const done = completedFor(manifest)
    if (skill === 'ux-proto-g') return startPrototype(workspace, body)
    const upstream = (catalog.reads?.(skill) ?? []).filter(id => done.includes(id)).map(id => {
      const entry = manifest.skills[id]
      readArtifact(workspace, task.id, entry)
      return entry
    })
    task.skills = [...new Set((Array.isArray(task.skills) ? task.skills : []).map(normalizeSkillId))]
    if (!task.skills.includes(skill)) task.skills.push(skill)
    task.lastSkill = skill
    task.round = { id: randomUUID(), skill, startedAt: Date.now() }
    task.updatedAt = new Date().toISOString()
    saveIndex(workspace, index)
    return { prompt: promptFor(task, skill, body.text, upstream) }
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
    const manifest = loadManifest(workspace, task.id)
    const skill = normalizeSkillId(manifest.skills[key]?.skill ?? task.lastSkill)
    if (skill === 'ux-proto-g') return startPrototype(workspace, body)
    if (key) {
      const entry = manifest.skills[key]
      if (entry?.manualLock) {
        entry.manualLock = false
        saveManifest(workspace, task.id, manifest)
      }
    }
    task.round = { id: randomUUID(), skill, startedAt: Date.now() }
    task.lastSkill = skill
    task.updatedAt = new Date().toISOString()
    saveIndex(workspace, index)
    return { prompt: promptFor(task, skill, body.text) }
  }

  async function confirmArtifact(workspace, body) {
    return serialize(workspace.id + ':' + body.taskId, () => {
      const task = findTask(loadIndex(workspace), String(body.taskId ?? ''))
      const manifest = loadManifest(workspace, task.id)
      const entry = manifest.skills[body.artifactKey]
      if (task.status !== 'active' || !confirmationSkills.has(entry?.skill) || entry.stale ||
          entry.reviewStatus !== 'ready_for_confirmation' || entry.sha256 !== body.baseSha) {
        throw Object.assign(new Error('产物状态已变更，请重新打开后再确认'), { status: 409 })
      }
      readArtifact(workspace, task.id, entry)
      entry.reviewStatus = 'formal'
      entry.confirmedAt = new Date().toISOString()
      saveManifest(workspace, task.id, manifest)
      return { ok: true }
    })
  }

  async function submit({ taskId, skill, markdown, title, stage }, callerSessionId) {
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
      const dir = taskDir(workspace, task.id, false)
      let file = taskPath(workspace, taskId, artifactKey)
      let bytes = Buffer.from(markdown)
      let format = 'markdown'
      if (skill === 'ux-proto-g') {
        if (task.round?.skill !== skill || (!task.round.prototype && !completedFor(manifest).includes('page-spec'))) {
          throw new Error('请在本任务的交互原型轮次登记构建结果')
        }
        if (!task.round.prototype) readArtifact(workspace, task.id, manifest.skills['page-spec'])
        const upstream = task.round.prototype?.upstream
        if (upstream) {
          const entry = loadManifest(workspace, upstream.taskId).skills['page-spec']
          if (!entry || entry.stale || entry.sha256 !== upstream.sha256) throw new Error('本轮上游页面规格已变化')
          readArtifact(workspace, upstream.taskId, entry)
        }
        const proofPath = 'ux-proto-g/.ux-proto/build-report.json'
        const proof = join(dir, proofPath)
        if (!existsSync(proof)) throw new Error('找不到本轮原型构建回执')
        contained(dir, realpathSync(proof))
        const info = lstatSync(proof)
        if (!info.isFile() || info.isSymbolicLink() || info.size > limit || info.mtimeMs < task.round.startedAt) {
          throw new Error('请先完成本轮原型构建，再登记产物')
        }
        const report = JSON.parse(readFileSync(proof, 'utf8'))
        if (report.schemaVersion !== 1 || !['normal', 'degraded'].includes(report.completionStatus) ||
            report.runtimePreview !== 'usable' || report.executionSafety !== 'verified' ||
            !/^sha256:[0-9a-f]{64}$/.test(report.sourceDigest) ||
            (report.completionStatus === 'normal' && report.staticPreview !== 'usable')) {
          throw new Error('原型构建回执未确认存在可用预览')
        }
        const list = items => items.length ? items.join('，') : '无'
        bytes = Buffer.from([
          '# 交互原型构建结果',
          '',
          '- 构建：' + report.completionStatus,
          '- 运行时／静态预览：' + report.runtimePreview + '／' + report.staticPreview,
          '- 执行安全：' + report.executionSafety,
          '- Pack 快照：' + (report.snapshotDigest ?? '无'),
          '- 源码摘要：' + report.sourceDigest,
          '- 已实例化资产：' + list(report.materializedAssets ?? []),
          '- 实际引用资产：' + list((report.observedReusableAssets ?? []).map(item => item.id)),
          '- 构建告警：' + list((report.warnings ?? []).map(item => JSON.stringify(item))),
          ...(report.error ? ['- 降级原因：' + report.error.message] : []),
          '- 运行时入口：`ux-proto-g/index.html`',
          ...(report.staticPreview === 'usable' ? ['- 静态入口：`ux-proto-g/index.static.html`'] : []),
          '- 构建回执：`' + proofPath + '`',
          '',
        ].join('\n'))
      }
      if (skill === 'solution-swimlane') {
        file = join(dir, swimlanePath)
        contained(dir, realpathSync(file))
        const info = lstatSync(file)
        if (!info.isFile() || info.size > 2_000_000) throw new Error('泳道图必须是 2 MB 以内的正式 HTML 文件')
        if (task.round?.startedAt && info.mtimeMs < task.round.startedAt) throw new Error('请先生成并校验本轮的泳道图')
        bytes = readFileSync(file)
        if (!/^<!doctype html>/i.test(bytes.toString('utf8').trimStart())) throw new Error('泳道图 HTML 格式无效')
        format = 'html'
      } else {
        if (!bytes.length || bytes.length > limit) throw new Error('产物为空或超过 320 KB')
        atomicWrite(dir, artifactKey + '.md', bytes)
      }
      const sha256 = digest(bytes)
      const reviewStatus = confirmationSkills.has(skill)
        ? stage === 'confirmation' ? 'ready_for_confirmation' : 'waiting_response'
        : review?.status ?? ''
      const changed = !previous || previous.sha256 !== sha256 || previous.reviewStatus !== reviewStatus
      const now = new Date().toISOString()
      manifest.skills[artifactKey] = {
        skill,
        artifactKind,
        reviewStatus,
        format,
        roundId: task.round?.skill === skill ? task.round.id : null,
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
        reviewStatus,
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
        if (body.action === 'prototype-options' || body.action === 'prototype-compare') {
          return json(await prototypeOptions(workspace, body, body.action === 'prototype-compare'))
        }
        if (body.action === 'create-session') return json({ sessionId: await createSession(workspace) })
        if (body.action === 'create-task') return json(await createTask(workspace, body))
        if (body.action === 'prompt') return json(await promptTask(workspace, body))
        if (body.action === 'update-artifact') return json(await updateArtifact(workspace, body))
        if (body.action === 'confirm-artifact') return json(await confirmArtifact(workspace, body))
        if (body.action === 'open-prototype') return json(await openPrototype(workspace, String(body.taskId ?? '')))
        if (body.action === 'message') return json(await message(workspace, body))
        if (['pause', 'complete', 'resume', 'rename'].includes(body.action)) {
          return json({ task: await changeTask(workspace, body, body.action) })
        }
        throw new Error('未知操作')
      }
      if (url.searchParams.has('latest')) {
        const task = loadIndex(workspace).tasks.reduce((latest, item) =>
          !latest || String(item.createdAt) >= String(latest.createdAt) ? item : latest, null)
        return json(task ? taskDetail(workspace, task, loadManifest(workspace, task.id)) : null)
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
          const bytes = readArtifact(workspace, taskId, entry)
          return json({ content: bytes.toString('utf8'), artifact: artifactMeta(workspace, task, manifest, requestedKey, entry) })
        }
        return json(taskDetail(workspace, task, manifest))
      }
      return json({ sessions: await listSessions(workspace), tasks: loadIndex(workspace).tasks.map(summary) })
    } catch (error) {
      return json({ error: error?.message || '工作台请求失败' }, error?.status || 400)
    }
  }

  return { fetch, submit, dispose() {} }
}
