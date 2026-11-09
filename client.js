window.__ModuleLoader__.load({
  id: 'dsh-ux-blueprinting',
  factory(require) {
    const { createElement: h, useEffect, useRef, useState, useSyncExternalStore } = require('react')

    const id = 'ux-blueprinting'
    const endpoint = '/api/ux-blueprinting/workbench'
    const NS = 'ux-blueprinting'
    const STORAGE_KEY = 'uxbp:workbench:v1'

    function readSavedState() {
      try {
        if (typeof localStorage === 'undefined') return null
        const value = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? 'null')
        if (!value || typeof value !== 'object') return null
        if (typeof value.workspace !== 'string' || typeof value.sessionId !== 'string') return null
        return {
          workspace: value.workspace,
          sessionId: value.sessionId,
          anchorSeq: Number.isSafeInteger(value.anchorSeq) ? value.anchorSeq : null,
        }
      } catch { return null }
    }

    function writeSavedState(value) {
      try {
        if (typeof localStorage === 'undefined') return
        localStorage.setItem(STORAGE_KEY, JSON.stringify(value))
      } catch {}
    }

    function clearSavedState() {
      try { if (typeof localStorage !== 'undefined') localStorage.removeItem(STORAGE_KEY) } catch {}
    }

    const en = {
      title: 'Design workbench',
      intro: 'Tell the conversation what to do; the timeline and next steps stay here.',
      workspace: 'Workspace',
      workspaceHint: 'Choose a workspace before attaching files or starting a conversation.',
      session: 'Conversation',
      flow: 'Task activity',
      side: 'Skills & next steps',
      chooseSession: 'Workspace conversations',
      chooseWorkspace: 'Choose workspace',
      reset: 'Reset workbench',
      newSession: 'New conversation',
      execute: 'Run task',
      stop: 'Stop',
      enter: 'Open conversation',
      skills: 'Skills',
      next: 'Next',
      artifacts: 'Artifacts',
      noArtifacts: 'No artifact yet.',
      notStarted: 'Not started. Run a task to get started.',
      inProgress: 'Running…',
      noNext: 'No suggested follow-up yet.',
      continue: 'Continue with',
      also: 'Other options',
      view: 'View',
      remove: 'Remove',
      done: 'Done',
      ready: 'Ready',
      locked: 'Needs',
      empty: 'I’m your AI design assistant. Share a requirement, an idea, data, or feedback. I can review requirements, analyze experience issues, shape a strategy, or turn your inputs into design deliverables such as page specs and journey maps.',
      placeholder: '描述要做的事，路径或 URL 直接写在这里……',
      upload: 'Attach files',
    }

    const zh = {
      title: '设计工作台',
      intro: '把要做的事告诉会话；进度和下一步留在这里。',
      workspace: '工作区',
      workspaceHint: '请先选择工作区，再上传附件或新建会话。',
      session: '会话',
      flow: '任务动态',
      side: '技能与下一步',
      chooseSession: '工作区会话',
      chooseWorkspace: '请选择工作区',
      reset: '重置工作台',
      newSession: '新会话',
      execute: '执行任务',
      stop: '停止',
      enter: '进入会话',
      skills: '技能',
      next: '下一步',
      artifacts: '产物',
      noArtifacts: '还没有产物。',
      notStarted: '尚未开始。执行任务后，进度会显示在这里。',
      inProgress: '正在执行…',
      noNext: '暂无后续建议。',
      continue: '建议继续',
      also: '也可以做',
      view: '查看',
      remove: '移除',
      done: '已完成',
      ready: '可执行',
      locked: '先完成',
      empty: '我是你的 AI 设计助手。你可以发来需求让我审核，给我一个问题或想法一起梳理策略，也可以让我分析数据和反馈，或根据已有材料生成页面规格、用户旅程等设计文档。',
      placeholder: '描述要做的事，路径或 URL 直接写在这里……',
      upload: '上传附件',
    }


    const styles = `
      .uxbp-page {
        --uxbp-bg: #f7f6f3;
        --uxbp-paper: #fff;
        --uxbp-soft: #f4f3f0;
        --uxbp-line: #e6e1da;
        --uxbp-ink: #27231f;
        --uxbp-muted: #686159;
        --uxbp-accent: #a8481e;
        --uxbp-accent-hover: #893818;
        --uxbp-orange: #fff1e5;
        --uxbp-green: #216b51;
        --uxbp-green-bg: #edf7f1;
        --uxbp-danger: #a52c28;
        box-sizing: border-box;
        height: 100%;
        min-height: 0;
        min-width: 0;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        padding: 20px clamp(12px, 2vw, 28px) 16px;
        gap: 14px;
        background: var(--uxbp-bg);
        color: var(--uxbp-ink);
        color-scheme: light;
        font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
        container-type: inline-size;
      }
      .uxbp-page *, .uxbp-page *::before, .uxbp-page *::after { box-sizing: border-box; }
      .uxbp-page :is(button, select, textarea):focus-visible { outline: 2px solid var(--uxbp-accent); outline-offset: 2px; }
      .uxbp-header { display: flex; flex: none; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; }
      .uxbp-brand { display: flex; align-items: center; gap: 12px; min-width: 0; }
      .uxbp-brand-mark { display: grid; place-items: center; width: 42px; height: 42px; flex: none; color: var(--uxbp-accent); background: var(--uxbp-orange); border: 1px solid #f3d5be; border-radius: 13px; }
      .uxbp-workspace { display: flex; align-items: center; gap: 8px; min-width: 0; }
      .uxbp-anchor { position: relative; min-width: 0; }
      .uxbp-grid { flex: 1; min-height: 0; display: grid; grid-template-columns: minmax(0, 1fr) minmax(285px, 34%); grid-template-rows: minmax(0, 1fr); gap: 14px; }
      .uxbp-card { min-height: 0; min-width: 0; overflow: hidden; display: flex; flex-direction: column; border: 1px solid var(--uxbp-line); border-radius: 16px; background: var(--uxbp-paper); box-shadow: 0 3px 12px #3b2c1d09; }
      .uxbp-card-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; flex: none; min-height: 52px; padding: 10px 16px; border-bottom: 1px solid var(--uxbp-line); }
      .uxbp-card-head h2 { margin: 0; font-size: 14px; font-weight: 650; }
      .uxbp-scroll { flex: 1; min-height: 0; min-width: 0; overflow: auto; overscroll-behavior: contain; padding: 14px 16px; }
      .uxbp-timeline { display: grid; align-content: start; gap: 6px; }
      .uxbp-empty { margin: 0; color: var(--uxbp-muted); font-size: 14px; line-height: 1.7; }
      .uxbp-node { padding: 9px 2px; border-bottom: 1px solid var(--uxbp-line); overflow-wrap: anywhere; }
      .uxbp-output { padding: 12px 14px; border: 1px solid #cde3d6; border-radius: 12px; background: var(--uxbp-green-bg); }
      .uxbp-output[data-latest="true"] { margin-bottom: 8px; }
      .uxbp-composer { position: relative; flex: none; margin: 0 12px 12px; padding: 8px; border: 1px solid var(--uxbp-line); border-radius: 14px; background: var(--uxbp-paper); box-shadow: 0 2px 9px #3b2c1d0a; }
      .uxbp-composer:focus-within { border-color: #c28c70; box-shadow: 0 0 0 3px #a8481e12; }
      .uxbp-composer textarea:focus-visible { outline: none; }
      .uxbp-files { max-height: min(72px, 12vh); overflow: auto; padding: 3px; }
      .uxbp-toolbar { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 6px; }
      .uxbp-btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; min-height: 32px; padding: 5px 10px; border: 1px solid var(--uxbp-line); border-radius: 8px; background: var(--uxbp-paper); color: var(--uxbp-ink); font: inherit; font-size: 12px; font-weight: 600; cursor: pointer; white-space: nowrap; }
      .uxbp-btn:hover:not(:disabled) { background: var(--uxbp-soft); }
      .uxbp-btn:disabled { opacity: .5; cursor: not-allowed; }
      .uxbp-btn[data-active="true"] { color: var(--uxbp-accent); background: var(--uxbp-orange); border-color: #f3d5be; }
      .uxbp-btn[data-primary="true"] { background: var(--uxbp-accent); border-color: var(--uxbp-accent); color: white; }
      .uxbp-btn[data-primary="true"]:hover:not(:disabled) { background: var(--uxbp-accent-hover); }
      .uxbp-icon-btn { width: 32px; padding: 0; }
      .uxbp-upload { position: relative; }
      .uxbp-upload:focus-within { outline: 2px solid var(--uxbp-accent); outline-offset: 2px; }
      .uxbp-upload[aria-disabled="true"] { opacity: .5; cursor: not-allowed; }
      .uxbp-picker { max-width: min(200px, 100%); }
      .uxbp-picker > span { min-width: 0; overflow: hidden; text-overflow: ellipsis; }
      .uxbp-picker > svg { flex: none; }
      .uxbp-workspace .uxbp-picker { max-width: min(230px, calc(100cqw - 60px)); padding-right: 12px; }
      .uxbp-popover { position: absolute; z-index: 2; bottom: calc(100% + 5px); left: 0; width: min(280px, calc(100cqw - 120px)); max-height: min(280px, 32vh); overflow: auto; overscroll-behavior: contain; border: 1px solid var(--uxbp-line); border-radius: 12px; padding: 6px; background: var(--uxbp-paper); box-shadow: 0 12px 28px #30221726; }
      .uxbp-workspace .uxbp-popover { top: calc(100% + 5px); right: 0; bottom: auto; left: auto; width: min(280px, 100cqw); }
      .uxbp-skill-chip { display: flex; align-items: center; gap: 8px; width: fit-content; max-width: 100%; margin: 0 0 6px 3px; padding: 2px 5px 2px 8px; border: 1px solid #f3d5be; border-radius: 7px; background: var(--uxbp-orange); color: var(--uxbp-accent); font-size: 12px; }
      .uxbp-skill-chip > span { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      .uxbp-skill-chip button { display: grid; place-items: center; flex: none; width: 20px; height: 20px; padding: 0; border: 0; border-radius: 4px; background: transparent; color: inherit; cursor: pointer; }
      .uxbp-skill-chip button:hover:not(:disabled) { background: #f5d9c5; }
      .uxbp-skill-chip button:disabled { opacity: .5; cursor: not-allowed; }
      .uxbp-skill-chip svg { width: 13px; height: 13px; }
      .uxbp-option { display: flex; justify-content: space-between; align-items: center; gap: 8px; width: 100%; padding: 8px 10px; border: 0; border-radius: 7px; background: transparent; color: var(--uxbp-ink); font: inherit; font-size: 13px; text-align: left; cursor: pointer; overflow-wrap: anywhere; }
      .uxbp-option:hover:not(:disabled), .uxbp-option[aria-pressed="true"] { background: var(--uxbp-orange); color: var(--uxbp-accent); }
      .uxbp-option:disabled { opacity: .5; cursor: not-allowed; }
      .uxbp-tabs, .uxbp-switcher { display: flex; gap: 4px; padding: 3px; border-radius: 10px; background: var(--uxbp-soft); }
      .uxbp-tabs .uxbp-btn, .uxbp-switcher .uxbp-btn { border-color: transparent; background: transparent; }
      .uxbp-tabs .uxbp-btn[data-active="true"], .uxbp-switcher .uxbp-btn[data-active="true"] { background: var(--uxbp-paper); box-shadow: 0 1px 3px #3b2c1d12; }
      .uxbp-switcher { display: none; }
      .uxbp-group { margin: 0 0 16px; }
      .uxbp-group:last-child { margin-bottom: 0; }
      .uxbp-group-title { display: flex; justify-content: space-between; align-items: center; gap: 8px; margin: 0 0 8px; color: var(--uxbp-muted); font-size: 12px; font-weight: 650; }
      .uxbp-skill-card { width: 100%; padding: 9px 10px; border-radius: 10px; border: 1px solid var(--uxbp-line); background: var(--uxbp-paper); color: var(--uxbp-ink); font: inherit; font-size: 13px; text-align: left; cursor: pointer; overflow-wrap: anywhere; }
      .uxbp-skill-card:hover:not(:disabled) { border-color: #cf9a7c; }
      .uxbp-skill-card:disabled { cursor: not-allowed; opacity: .6; }
      .uxbp-skill-card[data-status="locked"] { background: #f6f5f3; }
      .uxbp-skill-card[data-status="done"] { background: var(--uxbp-green-bg); border-color: #cde3d6; }
      .uxbp-skill-card[data-status="primary"] { background: var(--uxbp-orange); border-color: #efc6aa; padding: 12px; }
      .uxbp-status { display: inline-flex; flex: none; align-items: center; gap: 4px; color: var(--uxbp-muted); font-size: 11px; }
      .uxbp-status::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
      [data-status="done"] > div > .uxbp-status { color: var(--uxbp-green); }
      [data-status="ready"] > div > .uxbp-status, .uxbp-next-title { color: var(--uxbp-accent); }
      .uxbp-meta { padding: 1px 6px; border-radius: 6px; background: var(--uxbp-soft); font-variant-numeric: tabular-nums; }
      .uxbp-note { margin: 0 0 10px; padding: 10px 12px; border-radius: 9px; background: var(--uxbp-soft); color: var(--uxbp-muted); font-size: 12px; }
      .uxbp-preview { margin: 12px 0 0; border: 1px solid var(--uxbp-line); border-radius: 10px; padding: 10px; }
      @container (max-width: 760px) {
        .uxbp-switcher { display: flex; align-self: flex-start; flex: none; }
        .uxbp-grid { grid-template-columns: minmax(0, 1fr); }
        .uxbp-grid[data-pane="flow"] > aside, .uxbp-grid[data-pane="side"] > section { display: none; }
      }
      @media (max-height: 550px) {
        .uxbp-page { gap: 8px; padding-block: 8px; }
        .uxbp-card-head { min-height: 40px; padding-block: 5px; }
        .uxbp-composer { margin-bottom: 6px; }
      }
    `

    const ui = {
      title: { margin: 0, fontSize: 23, lineHeight: 1.25, fontWeight: 700, letterSpacing: '-.025em' },
      intro: { margin: '4px 0 0', color: 'var(--uxbp-muted)', fontSize: 12 },
      row: { display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap', minWidth: 0 },
      muted: { color: 'var(--uxbp-muted)', fontSize: 12, overflowWrap: 'anywhere' },
      error: { margin: 0, padding: '6px 10px', maxHeight: 52, overflow: 'auto', borderRadius: 8, background: '#fae9e8', color: 'var(--uxbp-danger)', fontSize: 12 },
      textarea: { display: 'block', width: '100%', minHeight: 54, height: 60, maxHeight: 'min(140px, 25vh)', resize: 'vertical', padding: '6px 8px', font: 'inherit', border: 0, background: 'transparent', color: 'var(--uxbp-ink)' },
      chip: { display: 'inline-flex', alignItems: 'center', gap: 4, padding: '2px 6px', borderRadius: 7, background: 'var(--uxbp-soft)', fontSize: 12, minWidth: 0 },
      gridSkills: { display: 'grid', gap: 6 },
      artifactRow: { display: 'flex', justifyContent: 'space-between', gap: 8, alignItems: 'center', fontSize: 12, overflowWrap: 'anywhere' },
      nodeHead: { display: 'flex', alignItems: 'baseline', gap: 7, flexWrap: 'wrap' },
      dot: { flex: '0 0 14px', textAlign: 'center', fontSize: 12 },
      outputText: { margin: '8px 0 0', whiteSpace: 'pre-wrap', overflowWrap: 'anywhere', fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace', fontSize: 12, lineHeight: 1.65 },
    }

    function PanelIcon() {
      return h('svg', { viewBox: '0 0 24 24', width: 18, height: 18, 'aria-hidden': true, style: { display: 'block' } },
        h('path', { d: 'M12 2.5 21.5 12 12 21.5 2.5 12Z', fill: 'none', stroke: 'currentColor', strokeWidth: 1.7, strokeLinejoin: 'round' }),
        h('circle', { cx: 12, cy: 12, r: 2.1, fill: 'currentColor' }))
    }

    function ComposerIcon({ path }) {
      return h('svg', { viewBox: '0 0 24 24', width: 16, height: 16, 'aria-hidden': true, style: { display: 'block' } },
        h('path', { d: path, fill: 'none', stroke: 'currentColor', strokeWidth: 1.7, strokeLinecap: 'round', strokeLinejoin: 'round' }))
    }

    async function uploadFile(sessionId, file) {
      const query = new URLSearchParams({ sessionId, name: file.name })
      if (['image/png', 'image/jpeg', 'image/webp', 'image/gif'].includes(file.type)) query.set('mediaType', file.type)
      const url = new URL('api/session/uploadFileBinary', document.baseURI)
      url.search = query.toString()
      const response = await fetch(url, {
        method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: file, credentials: 'include',
      })
      if (!response.ok) throw new Error(file.name + ' · HTTP ' + response.status)
      const result = await response.json()
      if (!result.ok || !result.value?.receiptId) throw new Error(file.name + ' · ' + (result.error?.message || '上传失败'))
      return { type: 'file', receiptId: result.value.receiptId }
    }

    async function api(query, body, signal) {
      const response = await fetch(endpoint + (query ? '?' + new URLSearchParams(query) : ''), body ? {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal,
      } : { signal })
      const raw = await response.text()
      let data = {}
      try { data = raw ? JSON.parse(raw) : {} } catch { data = {} }
      if (!response.ok) throw new Error(data.error || ('HTTP ' + response.status))
      return data
    }

    function collect(value, acc, depth = 0) {
      if (value == null || depth > 6) return
      if (typeof value === 'string') { if (value.trim()) acc.texts.push(value); return }
      if (Array.isArray(value)) { for (const item of value) collect(item, acc, depth + 1); return }
      if (typeof value !== 'object') return
      if (value.type === 'tool-call') { acc.tools.push({ name: value.name, args: value.arguments }); return }
      if (value.type === 'tool-result') { acc.tools.push({ name: value.name, text: value.content ?? value.result }); return }
      if (value.type === 'file' || value.type === 'image') {
        acc.texts.push('\n📎 ' + (value.name || value.file?.name || value.image?.name || value.type) + '\n')
        return
      }
      if (typeof value.text === 'string') { acc.texts.push(value.text); return }
      for (const key of ['data', 'content', 'chunk', 'message', 'delta', 'blocks', 'value', 'toolResult']) {
        if (key in value) collect(value[key], acc, depth + 1)
      }
    }

    function rowsOf(entry) {
      const rows = []
      if (entry.type === 'transient') {
        if (entry.event?.type !== 'assistant/live-chunk') return rows
        const acc = { texts: [], tools: [] }
        collect(entry.event.data?.chunk, acc)
        const text = acc.texts.join('')
        return text ? [{ kind: 'assistant', text }] : rows
      }
      const e = entry.event
      if (!e || !['user/message', 'assistant/message', 'tool/result'].includes(e.type)) return rows
      if (e.type === 'user/message') {
        const kind = e.data?.source?.kind
        if (kind && kind !== 'user' && kind !== 'user-question-reply') return rows
      }
      const acc = { texts: [], tools: [] }
      collect(e.data, acc)
      const text = acc.texts.join('')
      if (text.trim()) rows.push({ kind: e.type === 'user/message' ? 'user' : e.type === 'tool/result' ? 'tool' : 'assistant', text })
      for (const tool of acc.tools) {
        rows.push({
          kind: 'tool',
          text: tool.name + (tool.args ? '\n' + String(tool.args).slice(0, 400) : '') + (tool.text ? '\n' + String(tool.text).slice(0, 400) : ''),
        })
      }
      return rows
    }

    function argsOf(call) {
      const value = call?.arguments ?? call?.input
      if (typeof value === 'string') {
        try { return JSON.parse(value) } catch { return {} }
      }
      return value && typeof value === 'object' ? value : {}
    }

    function short(value, limit = 80) {
      const text = String(value ?? '').replace(/\s+/g, ' ').trim()
      return text.length > limit ? text.slice(0, limit - 1) + '…' : text
    }

    function baseName(value) {
      const text = String(value ?? '')
      const parts = text.split(/[\\/]/)
      return parts[parts.length - 1] || text
    }

    function textOf(value) {
      const acc = { texts: [], tools: [] }
      collect(value, acc)
      return acc.texts.join('\n').trim()
    }

    function toolCallsOf(value, out = [], depth = 0) {
      if (value == null || depth > 8) return out
      if (Array.isArray(value)) {
        for (const item of value) toolCallsOf(item, out, depth + 1)
        return out
      }
      if (typeof value !== 'object') return out
      if (value.type === 'tool-call') {
        out.push(value)
        return out
      }
      for (const key of ['data', 'message', 'content', 'blocks']) {
        if (key in value) toolCallsOf(value[key], out, depth + 1)
      }
      return out
    }

    function callNode(call) {
      const name = String(call?.name ?? 'tool')
      const args = argsOf(call)
      if (name === 'submit_design_artifact') {
        return {
          kind: 'output', label: '当前阶段输出', detail: short(args.skill, 60),
          markdown: typeof args.markdown === 'string' ? args.markdown : '', status: 'running',
        }
      }
      if (name === 'skill') return { kind: 'skill', label: '加载技能', detail: short(args.name, 60), status: 'running' }
      if (name === 'read') return { kind: 'read', label: '阅读材料', detail: baseName(args.file_path), status: 'running' }
      if (name === 'glob' || name === 'grep') return { kind: 'read', label: '查找材料', detail: short(args.pattern, 60), status: 'running' }
      if (name === 'read_design_reference') return { kind: 'knowledge', label: '查知识', detail: baseName(args.path), status: 'running' }
      if (name === 'web_search') return { kind: 'knowledge', label: '查资料', detail: short(args.query, 60), status: 'running' }
      if (name === 'web_fetch') return { kind: 'knowledge', label: '查资料', detail: short(args.url, 60), status: 'running' }
      if (name === 'design_next_steps') return { kind: 'next', label: '计算下一步', detail: '', status: 'running' }
      if (name === 'write' || name === 'edit') return { kind: 'write', label: '写入文件', detail: baseName(args.file_path), status: 'running' }
      if (name === 'pwsh') return { kind: 'tool', label: '执行命令', detail: short(args.description, 60), status: 'running' }
      if (name === 'office' || name.startsWith('office-')) return { kind: 'tool', label: '处理文档', detail: short(args.operation, 60), status: 'running' }
      return { kind: 'tool', label: '执行工具', detail: name, status: 'running' }
    }

    function buildFlow(entries, anchor) {
      const nodes = []
      const byCall = new Map()
      const push = node => { nodes.push(node); return nodes.length - 1 }
      for (const entry of entries) {
        const seq = entry.event?.seq ?? 0
        if (seq <= anchor) continue
        const event = entry.event
        if (!event) continue
        if (event.type === 'user/message') {
          const kind = event.data?.source?.kind
          if (kind && kind !== 'user' && kind !== 'user-question-reply') continue
          const text = textOf(event.data)
          if (text) {
            const clean = text.replace(/^【技能：[^\n]*】\s*/, '')
            push({ kind: 'task', label: '接收任务', detail: short(clean || text), status: 'done' })
          }
        } else if (event.type === 'assistant/message') {
          const calls = toolCallsOf(event.data)
          if (calls.length) {
            for (const call of calls) {
              const index = push(callNode(call))
              if (call.id) byCall.set(call.id, index)
            }
          } else {
            const text = textOf(event.data)
            if (text) push({ kind: 'assistant', label: '生成结果', detail: short(text), text: text.slice(0, 3000), status: 'done' })
          }
        } else if (event.type === 'tool/result') {
          const toolCallId = event.data?.toolCallId ?? event.data?.message?.toolCallId
          const index = byCall.get(toolCallId)
          if (index === undefined) continue
          const node = nodes[index]
          const text = textOf(event.data)
          node.status = /error|failed|失败|拒绝/i.test(text.slice(0, 200)) ? 'failed' : 'done'
        }
      }
      const merged = []
      for (const node of nodes) {
        const previous = merged[merged.length - 1]
        if (previous && previous.kind === node.kind && node.kind === 'assistant') {
          previous.text = node.text
          previous.detail = node.detail
          continue
        }
        if (previous && previous.kind === node.kind && ['read', 'knowledge', 'skill'].includes(node.kind)) {
          previous.count = (previous.count ?? 1) + 1
          previous.detail = previous.count + ' 项'
          continue
        }
        merged.push(node)
      }
      let latestOutput = -1
      merged.forEach((node, index) => { if (node.kind === 'output') latestOutput = index })
      merged.forEach((node, index) => { node.latest = index === latestOutput })
      return merged
    }

    function Workbench({ translate: t, locale, sessions, uiWorkspace }) {
      const subscribe = callback => locale.subscribe(callback)
      const snapshot = () => locale.getSnapshot()
      useSyncExternalStore(subscribe, snapshot, snapshot)

      const [workspaces, setWorkspaces] = useState([])
      const [catalog, setCatalog] = useState([])
      const [workspace, setWorkspace] = useState('')
      const [conversations, setConversations] = useState([])
      const [manifest, setManifest] = useState(null)
      const [handoff, setHandoff] = useState(null)
      const [sessionId, setSessionId] = useState('')
      const [tab, setTab] = useState(2)
      const [text, setText] = useState('')
      const [files, setFiles] = useState([])
      const [skill, setSkill] = useState('')
      const [openPicker, setOpenPicker] = useState('')
      const [pane, setPane] = useState('flow')
      const [error, setError] = useState('')
      const [sending, setSending] = useState(false)
      const [timeline, setTimeline] = useState([])
      const [running, setRunning] = useState(false)
      const [pending, setPending] = useState([])
      const [preview, setPreview] = useState(null)
      const binding = useRef(null)
      const submitting = useRef(false)
      const freshSessions = useRef(new Set())
      const workspaceTrigger = useRef(null)
      const sessionTrigger = useRef(null)
      const skillTrigger = useRef(null)
      const picker = useRef(null)
      const savedState = useRef(readSavedState())
      const restored = useRef(false)
      const anchor = useRef({ sessionId: '', seq: null })

      function persist(state) {
        savedState.current = state
        writeSavedState(state)
      }

      const nameOf = value => catalog.find(item => item.id === value)?.name ?? value
      const artifacts = manifest?.skills ?? {}
      const completed = Object.keys(artifacts)
      const next = handoff?.sessionId === sessionId ? handoff.items : []

      useEffect(() => {
        if (!openPicker) return
        const trigger = { workspace: workspaceTrigger, session: sessionTrigger, skill: skillTrigger }[openPicker]
        const contains = target => trigger.current?.contains(target) || picker.current?.contains(target)
        function closeOutside(event) {
          if (!contains(event.target)) setOpenPicker('')
        }
        function closeOnEscape(event) {
          if (event.key !== 'Escape' || !contains(event.target)) return
          event.preventDefault()
          setOpenPicker('')
          trigger.current?.focus()
        }
        const first = picker.current?.querySelector('[aria-pressed="true"]:not(:disabled)')
          ?? picker.current?.querySelector('button:not(:disabled)')
        first?.focus()
        document.addEventListener('pointerdown', closeOutside)
        document.addEventListener('keydown', closeOnEscape)
        return () => {
          document.removeEventListener('pointerdown', closeOutside)
          document.removeEventListener('keydown', closeOnEscape)
        }
      }, [openPicker])

      useEffect(() => {
        const controller = new AbortController()
        api(null, null, controller.signal).then(data => {
          const list = data.workspaces ?? []
          const saved = savedState.current
          const preferred = saved?.workspace && list.some(item => item.id === saved.workspace)
            ? saved.workspace
            : list[0]?.id
          setWorkspaces(list)
          setCatalog(data.catalog ?? [])
          setWorkspace(current => current || preferred || '')
        }).catch(e => { if (!controller.signal.aborted) setError(e.message) })
        return () => controller.abort()
      }, [])

      useEffect(() => {
        if (!workspace) return
        const controller = new AbortController()
        let loading = false
        async function load() {
          if (loading || document.visibilityState === 'hidden') return
          loading = true
          try {
            const data = await api({ workspace, session: sessionId }, null, controller.signal)
            if (controller.signal.aborted) return
            const sessions = data.sessions ?? []
            setConversations(sessions)
            setManifest(data.manifest ?? null)
            setHandoff({ sessionId, items: data.next ?? [] })
            if (!restored.current) {
              restored.current = true
              const saved = savedState.current
              const restoredSession = saved?.workspace === workspace && saved.sessionId &&
                sessions.some(item => item.id === saved.sessionId)
              if (restoredSession && !sessionId) {
                anchor.current = {
                  sessionId: saved.sessionId,
                  seq: Number.isSafeInteger(saved.anchorSeq) ? saved.anchorSeq : null,
                }
                setSessionId(saved.sessionId)
              } else if (saved?.sessionId) {
                persist({ workspace, sessionId: '', anchorSeq: null })
              }
            }
          } catch (e) { if (!controller.signal.aborted) setError(e.message) }
          finally { loading = false }
        }
        void load()
        const timer = setInterval(() => { void load() }, 3000)
        return () => { controller.abort(); clearInterval(timer) }
      }, [workspace, sessionId])

      useEffect(() => {
        setTimeline([])
        setRunning(false)
        setPending([])
        binding.current = null
        if (!sessionId) return
        let disposed = false
        let offEvents
        let offSession
        let ref
        let anchorSeq = freshSessions.current.has(sessionId)
          ? 0
          : anchor.current.sessionId === sessionId ? anchor.current.seq : null
        freshSessions.current.delete(sessionId)
        if (anchorSeq === 0) persist({ workspace, sessionId, anchorSeq: 0 })
        try { ref = sessions.retain(sessionId, { source: 'controllerOperation' }) } catch (e) { setError(e.message); return }
        ref.ready.then(value => {
          if (disposed) return
          binding.current = value
          const update = () => {
            if (disposed) return
            const windowValue = value.eventSource.getSnapshot()
            const entries = windowValue.entries ?? []
            if (anchorSeq === null) {
              anchorSeq = entries.reduce((max, entry) => Math.max(max, entry.event?.seq ?? 0), 0)
              anchor.current = { sessionId, seq: anchorSeq }
              persist({ workspace, sessionId, anchorSeq })
            }
            setTimeline(buildFlow(entries, anchorSeq).slice(-80))
            const snap = value.session.getSnapshot()
            setRunning(Boolean(snap.running))
            setPending(snap.pendingSubmissions ?? [])
          }
          offEvents = value.eventSource.subscribe(update)
          offSession = value.session.subscribe(update)
          update()
        }).catch(e => { if (!disposed) setError(e.message) })
        return () => {
          disposed = true
          if (offEvents) offEvents()
          if (offSession) offSession()
          binding.current = null
          try { ref?.release() } catch {}
        }
      }, [sessionId])

      function newSession() {
        setSessionId('')
        setManifest(null)
        setHandoff(null)
        setPreview(null)
        setTimeline([])
        setPending([])
        setRunning(false)
        setError('')
        setSkill('')
        setOpenPicker('')
        anchor.current = { sessionId: '', seq: null }
      }

      function reset() {
        newSession()
        setConversations([])
        setManifest(null)
        setHandoff(null)
        setText('')
        setFiles([])
        setError('')
      }

      function selectSession(id) {
        if (id === sessionId) return
        const saved = savedState.current
        const reuse = saved?.workspace === workspace && saved.sessionId === id &&
          Number.isSafeInteger(saved.anchorSeq)
        const seq = freshSessions.current.has(id) ? 0 : reuse ? saved.anchorSeq : null
        anchor.current = { sessionId: id, seq }
        setSessionId(id)
        setManifest(null)
        setHandoff(null)
        setPreview(null)
        setTimeline([])
        setPending([])
        setRunning(false)
        setError('')
        persist({ workspace, sessionId: id, anchorSeq: seq })
      }

      function resetAll() {
        clearSavedState()
        savedState.current = null
        restored.current = true
        anchor.current = { sessionId: '', seq: null }
        setWorkspace('')
        setConversations([])
        setManifest(null)
        setHandoff(null)
        newSession()
        setText('')
        setFiles([])
        setError('')
        setTab(2)
        setPane('flow')
      }

      function statusOf(item) {
        if (completed.includes(item.id)) return 'done'
        const requiredOk = (item.required ?? []).every(done => completed.includes(done))
        const anyOk = !(item.requiredAny ?? []).length || item.requiredAny.some(done => completed.includes(done))
        return requiredOk && anyOk ? 'ready' : 'locked'
      }

      async function send() {
        if (submitting.current || !workspace || (!text.trim() && !files.length)) return
        submitting.current = true
        setSending(true)
        setError('')
        const message = ((skill ? '【技能：' + nameOf(skill) + '（' + skill + '）】\n' : '') + text.trim()).trim()
        let ref
        try {
          let target = sessionId
          if (!target) {
            const data = await api(null, { action: 'create-session', workspaceId: workspace })
            target = data.sessionId
            freshSessions.current.add(target)
            selectSession(target)
          }
          ref = sessions.retain(target, { source: 'controllerOperation' })
          const { session } = await ref.ready
          const content = []
          for (const file of files) content.push(await uploadFile(target, file))
          if (message) content.push({ type: 'text', text: message })
          const result = await session.prompt(content, 'queue')
          if (result?.ok === false) throw new Error(result.error?.message || '执行失败')
          setText('')
          setFiles([])
        } catch (e) { setError(e.message) } finally {
          submitting.current = false
          setSending(false)
          ref?.release()
        }
      }

      async function stop() {
        try { await binding.current?.session.cancel() } catch (e) { setError(e.message) }
      }

      function enter() {
        if (sessionId) uiWorkspace.openSession(sessionId)
      }

      async function viewArtifact(skill) {
        setError('')
        try {
          const data = await api({ workspace, session: sessionId, skill })
          setPreview(data)
          setTab(2)
        } catch (e) { setError(e.message) }
      }

      const groups = [
        { phase: 1, label: '探索与定义' },
        { phase: 2, label: '设计与交付' },
        { phase: 3, label: '分析与证据' },
      ]


      const conversation = conversations.find(item => item.id === sessionId)
      const sessionTitle = conversation?.title ?? t(sessionId ? 'session' : 'newSession')
      const workspaceTitle = workspaces.find(item => item.id === workspace)?.title ?? t('chooseWorkspace')
      const togglePicker = name => setOpenPicker(current => current === name ? '' : name)
      const flow = timeline.map((node, index) => ({ node, index }))
      const currentOutput = flow.findIndex(item => item.node.latest)
      if (currentOutput > 0) flow.unshift(flow.splice(currentOutput, 1)[0])

      return h('main', { className: 'uxbp-page' },
        h('style', null, styles),
        h('header', { className: 'uxbp-header' },
          h('div', { className: 'uxbp-brand' },
            h('span', { className: 'uxbp-brand-mark' }, h(PanelIcon)),
            h('div', null,
              h('h1', { style: ui.title }, t('title')),
              h('p', { style: ui.intro }, t('intro')))),
          h('div', { className: 'uxbp-workspace' },
            h('button', {
              type: 'button', className: 'uxbp-btn uxbp-icon-btn', title: t('reset'), 'aria-label': t('reset'),
              onClick: resetAll,
            }, h(ComposerIcon, { path: 'M20 12a8 8 0 1 1-2.3-5.7M20 4v6h-6' })),
            h('span', { style: { ...ui.muted, whiteSpace: 'nowrap' } }, t('workspace')),
            h('div', { className: 'uxbp-anchor' },
              h('button', {
                type: 'button', ref: workspaceTrigger, className: 'uxbp-btn uxbp-picker',
                'data-active': openPicker === 'workspace', 'aria-expanded': openPicker === 'workspace',
                'aria-label': t('workspace') + ' · ' + workspaceTitle, title: workspaceTitle, disabled: sending,
                onClick: () => togglePicker('workspace'),
              },
              h(ComposerIcon, { path: 'M3 6h7l2 2h9v11H3z' }),
              h('span', null, workspaceTitle),
              h(ComposerIcon, { path: 'm7 10 5 5 5-5' })),
              openPicker === 'workspace' && h('div', { className: 'uxbp-popover', ref: picker, role: 'group', 'aria-label': t('chooseWorkspace') },
                ...[{ id: '', title: t('chooseWorkspace') }, ...workspaces].map(item => h('button', {
                  key: item.id, type: 'button', className: 'uxbp-option', disabled: sending, 'aria-pressed': item.id === workspace,
                  onClick: () => {
                    const next = item.id
                    setOpenPicker('')
                    if (next !== workspace) {
                      setWorkspace(next)
                      reset()
                      persist({ workspace: next, sessionId: '', anchorSeq: null })
                    }
                    workspaceTrigger.current?.focus()
                  },
                }, item.title, item.id === workspace && h('span', { 'aria-hidden': true }, '✓'))))))),

        error && h('p', { role: 'alert', style: ui.error }, error),
        !workspace && h('p', { className: 'uxbp-note', style: { margin: 0 } }, t('workspaceHint')),

        h('div', { className: 'uxbp-switcher', role: 'group', 'aria-label': t('title') },
          h('button', {
            type: 'button', className: 'uxbp-btn', 'data-active': pane === 'flow', 'aria-pressed': pane === 'flow',
            onClick: () => setPane('flow'),
          }, t('flow')),
          h('button', {
            type: 'button', className: 'uxbp-btn', 'data-active': pane === 'side', 'aria-pressed': pane === 'side',
            onClick: () => { setOpenPicker(''); setPane('side') },
          }, t('side'))),

        h('div', { className: 'uxbp-grid', 'data-pane': pane },
          h('section', { className: 'uxbp-card', 'aria-label': t('flow') },
            h('div', { className: 'uxbp-card-head' },
              h('h2', null, t('flow')),
              (running || sending) && h('span', { className: 'uxbp-status', style: { color: 'var(--uxbp-accent)' } }, t('inProgress'))),
            h('div', { className: 'uxbp-scroll uxbp-timeline', 'aria-live': 'polite', tabIndex: 0 },
              timeline.length === 0 && h('p', { className: 'uxbp-empty' }, t(running ? 'inProgress' : 'empty')),
              ...flow.map(({ node, index }) => h('div', {
                key: index,
                className: node.kind === 'output' ? 'uxbp-node uxbp-output' : 'uxbp-node',
                'data-latest': Boolean(node.latest),
              },
              h('div', { style: ui.nodeHead },
                h('span', {
                  'aria-hidden': true,
                  style: { ...ui.dot, color: node.status === 'failed' ? 'var(--uxbp-danger)' : node.status === 'running' ? 'var(--uxbp-accent)' : 'var(--uxbp-green)' },
                }, node.status === 'running' ? '●' : node.status === 'failed' ? '✕' : '✓'),
                h('strong', { style: { fontSize: 13 } }, node.label),
                node.detail && h('span', { style: ui.muted }, node.detail)),
              node.markdown && node.latest && h('pre', { style: ui.outputText }, node.markdown),
              node.markdown && !node.latest && h('p', { style: { ...ui.muted, margin: '6px 0 0' } }, '历史输出（当前阶段输出中查看）'),
              node.text && h('div', { style: { marginTop: 6, fontSize: 13, whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' } }, node.text))),
              ...pending.map((item, index) => h('div', { key: 'p' + index, className: 'uxbp-node' },
                h('div', { style: ui.nodeHead },
                  h('span', { style: ui.dot, 'aria-hidden': true }, '○'),
                  h('strong', { style: { fontSize: 13 } }, '排队中'),
                  h('span', { style: ui.muted }, item.text))))),

            h('div', { className: 'uxbp-composer' },
              files.length > 0 && h('div', { className: 'uxbp-files', style: ui.row }, ...files.map((file, index) =>
                h('span', { key: index, style: { ...ui.chip, overflowWrap: 'anywhere' } },
                  file.name,
                  h('button', {
                    type: 'button', className: 'uxbp-btn', style: { minHeight: 22, padding: '0 5px' }, disabled: sending,
                    'aria-label': t('remove') + ' ' + file.name,
                    onClick: () => setFiles(current => current.filter((_, i) => i !== index)),
                  }, '×')))),
              h('textarea', {
                style: ui.textarea, placeholder: t('placeholder'), 'aria-label': t('placeholder'), value: text, disabled: sending,
                onChange: e => setText(e.target.value),
                onKeyDown: e => {
                  if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing && e.keyCode !== 229) {
                    e.preventDefault()
                    void send()
                  }
                },
              }),
              skill && h('div', { className: 'uxbp-skill-chip' },
                h('span', { title: nameOf(skill) }, h('strong', null, 'Skill:'), ' ' + nameOf(skill)),
                h('button', {
                  type: 'button', disabled: sending, 'aria-label': t('remove') + ' · ' + nameOf(skill),
                  onClick: () => { setSkill(''); skillTrigger.current?.focus() },
                }, h(ComposerIcon, { path: 'm6 6 12 12M18 6 6 18' }))),
              h('div', { className: 'uxbp-toolbar' },
                h('div', { style: ui.row },
                  h('label', {
                    className: 'uxbp-btn uxbp-icon-btn uxbp-upload',
                    title: !workspace ? t('workspaceHint') : t('upload'),
                    'aria-label': t('upload'),
                    'aria-disabled': !workspace || sending,
                    tabIndex: !workspace || sending ? -1 : 0,
                    onClick: e => { if (!workspace || sending) e.preventDefault() },
                    onKeyDown: e => {
                      if ((e.key === 'Enter' || e.key === ' ') && workspace && !sending) {
                        e.preventDefault()
                        e.currentTarget.querySelector('input')?.click()
                      }
                    },
                  },
                  h('input', {
                    type: 'file', multiple: true, disabled: !workspace || sending, 'aria-label': t('upload'),
                    style: { position: 'absolute', width: 1, height: 1, opacity: 0 },
                    onChange: e => {
                      const selected = Array.from(e.currentTarget.files ?? [])
                      setFiles(current => [...current, ...selected])
                      e.currentTarget.value = ''
                    },
                  }),
                  h(ComposerIcon, { path: 'M20 11 11 20a5 5 0 0 1-7-7l9-9a3.5 3.5 0 0 1 5 5l-9 9a2 2 0 0 1-3-3l8-8' })),
                  h('div', { className: 'uxbp-anchor' },
                    h('button', {
                      type: 'button', ref: skillTrigger, className: 'uxbp-btn uxbp-icon-btn', 'data-active': Boolean(skill) || openPicker === 'skill',
                      title: skill ? nameOf(skill) : t('skills'), 'aria-label': skill ? t('skills') + ' · ' + nameOf(skill) : t('skills'),
                      'aria-expanded': openPicker === 'skill', disabled: sending, onClick: () => togglePicker('skill'),
                    }, h(ComposerIcon, { path: 'M12 2 14.5 9.5 22 12 14.5 14.5 12 22 9.5 14.5 2 12 9.5 9.5Z' })),
                    openPicker === 'skill' && h('div', { className: 'uxbp-popover', ref: picker, role: 'group', 'aria-label': t('skills') },
                      ...groups.map(group => h('div', { key: group.phase },
                        h('p', { style: { ...ui.muted, margin: '7px 10px 2px' } }, group.label),
                        ...catalog.filter(item => item.phase === group.phase).map(item => {
                          const status = statusOf(item)
                          return h('button', {
                            key: item.id, type: 'button', className: 'uxbp-option', disabled: sending, 'aria-pressed': skill === item.id,
                            onClick: () => { setSkill(item.id); setOpenPicker(''); skillTrigger.current?.focus() },
                          }, h('span', null, item.name), h('span', { className: 'uxbp-status' }, t(status)))
                        }))))),
                  h('div', { className: 'uxbp-anchor' },
                    h('button', {
                      type: 'button', ref: sessionTrigger, className: 'uxbp-btn uxbp-picker', 'data-active': openPicker === 'session',
                      title: !workspace ? t('workspaceHint') : sessionTitle, 'aria-label': t('session') + ' · ' + sessionTitle,
                      'aria-expanded': openPicker === 'session', disabled: !workspace || sending, onClick: () => togglePicker('session'),
                    },
                    h(ComposerIcon, { path: 'M4 5h16v11H9l-5 4V5Z M8 9h8 M8 12h5' }),
                    h('span', null, sessionTitle),
                    h(ComposerIcon, { path: 'm7 10 5 5 5-5' })),
                    openPicker === 'session' && h('div', { className: 'uxbp-popover', ref: picker, role: 'group', 'aria-label': t('chooseSession') },
                      h('button', {
                        type: 'button', className: 'uxbp-option', disabled: sending,
                        onClick: () => { newSession(); persist({ workspace, sessionId: '', anchorSeq: null }); sessionTrigger.current?.focus() },
                      }, '＋ ' + t('newSession')),
                      conversations.length > 0 && h('p', { style: { ...ui.muted, margin: '6px 10px 2px' } }, t('chooseSession')),
                      ...conversations.map(item => h('button', {
                        key: item.id, type: 'button', className: 'uxbp-option', disabled: sending, 'aria-pressed': item.id === sessionId,
                        onClick: () => { setOpenPicker(''); selectSession(item.id); sessionTrigger.current?.focus() },
                      }, item.title, item.id === sessionId && h('span', { 'aria-hidden': true }, '✓')))))),
                h('div', { style: { ...ui.row, marginLeft: 'auto', justifyContent: 'flex-end' } },
                  running && h('button', { type: 'button', className: 'uxbp-btn', onClick: () => void stop() }, t('stop')),
                  h('button', { type: 'button', className: 'uxbp-btn', disabled: !sessionId || sending, onClick: enter }, t('enter')),
                  h('button', {
                    type: 'button', className: 'uxbp-btn', 'data-primary': true,
                    disabled: !workspace || sending || (!text.trim() && !files.length), onClick: () => void send(),
                  }, t('execute')))))),

          h('aside', { className: 'uxbp-card', 'aria-label': t('side') },
            h('div', { className: 'uxbp-card-head' },
              h('div', { className: 'uxbp-tabs', role: 'group', 'aria-label': t('side') },
                h('button', { type: 'button', className: 'uxbp-btn', 'data-active': tab === 1, 'aria-pressed': tab === 1, onClick: () => setTab(1) }, t('skills')),
                h('button', { type: 'button', className: 'uxbp-btn', 'data-active': tab === 2, 'aria-pressed': tab === 2, onClick: () => setTab(2) }, t('next')))),
            h('div', { className: 'uxbp-scroll', key: tab, tabIndex: 0 },
              tab === 1
                ? groups.map(group => {
                  const items = catalog.filter(item => item.phase === group.phase)
                  const done = items.filter(item => completed.includes(item.id)).length
                  return h('section', { key: group.phase, className: 'uxbp-group' },
                    h('h3', { className: 'uxbp-group-title' }, group.label, h('span', { className: 'uxbp-meta' }, done + ' / ' + items.length)),
                    h('div', { style: ui.gridSkills }, ...items.map(item => {
                      const status = statusOf(item)
                      return h('button', {
                        key: item.id, type: 'button', className: 'uxbp-skill-card', 'data-status': status, disabled: sending,
                        onClick: () => {
                          if (status === 'done') void viewArtifact(item.id)
                          else setSkill(item.id)
                        },
                      },
                      h('div', { style: { display: 'flex', justifyContent: 'space-between', gap: 6 } },
                        h('strong', null, item.name), h('span', { className: 'uxbp-status' }, t(status))),
                      h('div', { style: ui.muted }, '/' + item.id + (artifacts[item.id]?.stale ? ' · 可能过期' : '') + (status === 'locked' && item.required?.length ? ' · ' + item.required.join('/') : '')))
                    })))
                })
                : h('div', null,
                  (running || sending || pending.length > 0)
                    ? h('p', { className: 'uxbp-note' }, t('inProgress'))
                    : !completed.length && h('p', { className: 'uxbp-note' }, t(timeline.length ? 'noArtifacts' : 'notStarted')),
                  ...next.map((item, index) => h('div', { key: item.id, style: { marginBottom: 8 } },
                    index < 2 && h('h3', { className: index === 0 ? 'uxbp-group-title uxbp-next-title' : 'uxbp-group-title' }, t(index === 0 ? 'continue' : 'also')),
                    h('button', {
                      type: 'button', className: 'uxbp-skill-card', 'data-status': index === 0 ? 'primary' : undefined,
                      disabled: sending, onClick: () => setSkill(item.id),
                    },
                    h('strong', null, item.name),
                    h('div', { style: { ...ui.muted, marginTop: 4 } }, item.reason)))),
                  completed.length > 0 && !next.length && h('p', { className: 'uxbp-note' }, t('noNext')),
                  completed.length > 0 && h('div', { style: { ...ui.gridSkills, marginTop: 16 } },
                    h('h3', { className: 'uxbp-group-title' }, t('artifacts')),
                    ...Object.values(artifacts).map(entry => h('div', { key: entry.skill, style: ui.artifactRow },
                      h('span', null, nameOf(entry.skill) + (entry.stale ? ' · 可能过期' : '')),
                      h('button', { type: 'button', className: 'uxbp-btn', onClick: () => void viewArtifact(entry.skill) }, t('view'))))),
                  preview && h('div', { className: 'uxbp-preview' },
                    h('h3', { className: 'uxbp-group-title' }, nameOf(preview.artifact?.skill)),
                    h('pre', { style: ui.outputText }, preview.content)))))))

    }

    return {
      inject: ['slots', 'locale', 'sessions', 'uiWorkspace'],
      apply(ctx) {
        const disposers = [
          ctx.locale.register(NS, 'en', en),
          ctx.locale.register(NS, 'zh', zh),
        ]
        ctx.effect(() => () => { for (const dispose of disposers) dispose() })
        const t = ctx.locale.bind(NS)
        ctx.slots.inject('sidebar.panellist', () =>
          ctx.slots.register({ name: 'sidebar.panellist', id, order: 20, label: () => t('title') }, PanelIcon))
        ctx.slots.inject('main', () =>
          ctx.slots.register({ name: 'main', key: id }, (props) =>
            h(Workbench, {
              ...props, translate: t, locale: ctx.locale,
              sessions: ctx.sessions, uiWorkspace: ctx.uiWorkspace,
            })))
      },
    }
  },
})
