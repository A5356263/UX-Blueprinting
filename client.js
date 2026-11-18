window.__ModuleLoader__.load({
  id: 'dsh-ux-blueprinting',
  factory(require) {
    const { createElement: h, useEffect, useRef, useState, useSyncExternalStore } = require('react')

    const id = 'ux-blueprinting'
    const endpoint = '/api/ux-blueprinting/workbench'
    const STORAGE_KEY = 'uxbp:workbench:v2'
    const NS = 'ux-blueprinting'

    const en = {
      title: 'Design workbench',
      task: 'Tasks',
      sediment: 'Recents',
      workspace: 'Workspace',
      reset: 'Reset workbench',
      useSkill: 'Use skill',
      newTask: 'New task',
      pause: 'Pause',
      end: 'Finish',
      resume: 'Resume',
      rename: 'Rename',
      skill: 'Skill',
      session: 'Conversation',
      newSession: 'New conversation',
      attach: 'Attach files',
      placeholder: 'Describe the task, or paste a path / URL…',
      execute: 'Run task',
      enter: 'Open conversation',
      stop: 'Stop',
      dynamics: 'Activity',
      dialogue: 'Conversation',
      next: 'Next',
      noTask: 'Pick a skill card to start.',
      noDialogue: 'No messages in this task yet.',
      noNext: 'No suggestion yet.',
      emptySediment: 'No tasks yet.',
      search: 'Search tasks',
      all: 'All',
      active: 'In progress',
      paused: 'Paused',
      completed: 'Completed',
      running: 'Running…',
      openTask: 'Open',
      view: 'View',
      remove: 'Remove',
      history: 'History',
    }

    const zh = {
      title: '设计工作台',
      task: '任务',
      sediment: '沉淀',
      workspace: '工作区',
      reset: '重置工作台',
      useSkill: '使用 Skill',
      newTask: '新建任务',
      pause: '暂停',
      end: '结束',
      resume: '恢复',
      rename: '重命名',
      skill: '技能',
      session: '会话',
      newSession: '新会话',
      attach: '上传附件',
      placeholder: '描述这次任务，或直接贴路径 / URL……',
      execute: '执行任务',
      enter: '进入会话',
      stop: '停止',
      dynamics: '动态',
      dialogue: '对话',
      next: '下一步',
      noTask: '选择一张技能卡片开始。',
      noDialogue: '这个任务还没有对话。',
      noNext: '暂无后续建议。',
      emptySediment: '还没有沉淀的任务。',
      search: '搜索任务',
      all: '全部',
      active: '进行中',
      paused: '已暂停',
      completed: '已完成',
      running: '执行中…',
      openTask: '打开',
      view: '查看',
      remove: '移除',
      history: '历史任务',
    }

    const styles = `
      .uxbp-root {
        --bg: var(--dsw-alias-bg-base, #f7f6f3);
        --card: var(--dsw-alias-bg-layer-2, #fff);
        --line: var(--dsw-alias-border-l2, #e6e1da);
        --ink: var(--dsw-alias-label-primary, #27231f);
        --muted: var(--dsw-alias-label-secondary, #686159);
        --accent: var(--dsw-alias-link, #a8481e);
        --soft: var(--dsw-alias-interactive-bg-hover, #f4f3f0);
        --radius: var(--dsw-radius-lg, 16px);
        --shadow: var(--dsw-elevation-soft, 0 3px 12px rgb(59 44 29 / .06));
        height: 100%; min-height: 0; box-sizing: border-box; display: flex; flex-direction: column;
        gap: 12px; padding: 16px; overflow: hidden; color: var(--ink); background: var(--bg);
        font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
        container-type: inline-size;
      }
      .uxbp-root *, .uxbp-root *::before, .uxbp-root *::after { box-sizing: border-box; }
      .uxbp-top {
        flex: none; display: flex; align-items: center; justify-content: space-between; gap: 12px;
        padding: 7px 10px; border: 1px solid var(--line); border-radius: var(--radius);
        background: color-mix(in srgb, var(--card) 78%, transparent);
        backdrop-filter: blur(24px) saturate(160%); box-shadow: var(--shadow);
      }
      .uxbp-brand { display: flex; align-items: center; gap: 10px; min-width: 0; }
      .uxbp-mark { display: grid; place-items: center; width: 32px; height: 32px; flex: none; border-radius: 10px;
        color: var(--accent); background: color-mix(in srgb, var(--accent) 12%, var(--card)); }
      .uxbp-title { margin: 0; font-size: 14px; font-weight: 700; white-space: nowrap; }
      .uxbp-tabs { display: flex; gap: 2px; padding: 3px; border-radius: 10px; background: var(--soft); }
      .uxbp-tab { border: 0; border-radius: 7px; padding: 5px 10px; background: transparent; color: var(--muted);
        font: inherit; font-size: 12px; font-weight: 650; cursor: pointer; }
      .uxbp-tab[data-on="true"] { background: var(--card); color: var(--ink); box-shadow: var(--shadow); }
      .uxbp-right-top { display: flex; align-items: center; gap: 6px; min-width: 0; }
      .uxbp-btn { display: inline-flex; align-items: center; justify-content: center; gap: 5px; min-height: 30px;
        padding: 4px 9px; border: 1px solid var(--line); border-radius: 8px; background: var(--card);
        color: var(--ink); font: inherit; font-size: 12px; cursor: pointer; white-space: nowrap; }
      .uxbp-btn:hover:not(:disabled) { background: var(--soft); }
      .uxbp-btn:disabled { opacity: .45; cursor: not-allowed; }
      .uxbp-icon { width: 30px; padding: 0; }
      .uxbp-primary { background: var(--accent); border-color: var(--accent); color: #fff; }
      .uxbp-picker { position: relative; }
      .uxbp-picker > span { min-width: 0; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      .uxbp-menu { position: absolute; z-index: 20; top: calc(100% + 5px); right: 0; min-width: 220px; max-height: 300px;
        overflow: auto; padding: 5px; border: 1px solid var(--line); border-radius: 12px; background: var(--card);
        box-shadow: 0 14px 34px rgb(20 14 8 / .18); }
      .uxbp-option { display: flex; justify-content: space-between; gap: 8px; width: 100%; padding: 7px 9px;
        border: 0; border-radius: 7px; background: transparent; color: var(--ink); font: inherit; font-size: 12px;
        text-align: left; cursor: pointer; }
      .uxbp-option:hover, .uxbp-option[data-on="true"] { background: var(--soft); color: var(--accent); }
      .uxbp-body { flex: 1; min-height: 0; display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 12px; }
      .uxbp-left { min-width: 0; min-height: 0; display: flex; flex-direction: column; gap: 10px; }
      .uxbp-canvas { flex: 1; min-height: 0; overflow: auto; border: 1px solid var(--line); border-radius: var(--radius);
        background: color-mix(in srgb, var(--card) 55%, var(--bg)); box-shadow: var(--shadow); cursor: grab;
        scrollbar-gutter: stable; }
      .uxbp-canvas[data-drag="true"] { cursor: grabbing; user-select: none; }
      .uxbp-plane { padding: 22px; min-width: max-content; }
      .uxbp-group { margin-bottom: 22px; }
      .uxbp-group:last-child { margin-bottom: 0; }
      .uxbp-group h2 { margin: 0 0 10px; color: var(--muted); font-size: 12px; font-weight: 700; letter-spacing: .02em; }
      .uxbp-cards { display: flex; flex-wrap: wrap; gap: 14px; align-items: flex-start; max-width: 1500px; }
      .uxbp-card { position: relative; width: 220px; height: 272px; padding: 0; overflow: hidden; display: flex;
        flex-direction: column; border: 1px solid var(--line); border-radius: var(--radius); background: var(--card);
        color: var(--ink); text-align: left; box-shadow: var(--shadow); cursor: pointer;
        transform: rotate(var(--rot, 0deg)) translateY(var(--off, 0px)); transition: transform .2s ease, box-shadow .2s ease; }
      .uxbp-card:hover, .uxbp-card:focus-visible { transform: rotate(0deg) translateY(-4px);
        box-shadow: 0 16px 30px -12px rgb(20 14 8 / .28); outline: 1px solid color-mix(in srgb, var(--accent) 45%, transparent); }
      .uxbp-card[data-shake="true"] { animation: uxbp-shake .22s ease; }
      .uxbp-art { flex: none; height: 122px; margin: 6px; border-radius: 12px; position: relative; overflow: hidden; }
      .uxbp-art::after { content: ''; position: absolute; inset: 0; background: linear-gradient(180deg, transparent 40%, rgb(255 255 255 / .25)); }
      .uxbp-card-body { flex: 1; min-height: 0; padding: 4px 12px 8px; display: flex; flex-direction: column; gap: 5px; }
      .uxbp-card-body strong { font-size: 14px; line-height: 1.35; }
      .uxbp-card-body p { margin: 0; color: var(--muted); font-size: 11px; line-height: 1.45; overflow: hidden; }
      .uxbp-card-foot { margin-top: auto; display: flex; align-items: center; justify-content: space-between; gap: 6px; }
      .uxbp-card-foot code { color: var(--muted); font-size: 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      .uxbp-use { border: 0; border-radius: 7px; padding: 4px 7px; background: color-mix(in srgb, var(--accent) 12%, var(--card));
        color: var(--accent); font: inherit; font-size: 10px; font-weight: 700; cursor: pointer; }
      @keyframes uxbp-shake { 0%,100% { transform: rotate(0) translateX(0); } 35% { transform: rotate(0) translateX(-2px); }
        70% { transform: rotate(0) translateX(2px); } }
      .uxbp-composer { flex: none; margin: 0 2px 2px; padding: 7px; border: 1px solid var(--line); border-radius: var(--radius);
        background: var(--card); box-shadow: var(--shadow); }
      .uxbp-composer:focus-within { border-color: color-mix(in srgb, var(--accent) 55%, var(--line)); }
      .uxbp-input { display: block; width: 100%; min-height: 46px; max-height: 130px; resize: vertical; padding: 6px 7px;
        border: 0; background: transparent; color: var(--ink); font: inherit; font-size: 13px; outline: none; }
      .uxbp-tools { display: flex; align-items: center; justify-content: space-between; gap: 6px; flex-wrap: wrap; }
      .uxbp-tools-left, .uxbp-tools-right { display: flex; align-items: center; gap: 5px; min-width: 0; }
      .uxbp-chip { display: inline-flex; align-items: center; gap: 5px; max-width: 100%; padding: 3px 6px; border-radius: 7px;
        background: color-mix(in srgb, var(--accent) 10%, var(--card)); color: var(--accent); font-size: 11px; }
      .uxbp-chip span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      .uxbp-chip button { border: 0; background: transparent; color: inherit; cursor: pointer; padding: 0; }
      .uxbp-file { display: inline-flex; align-items: center; gap: 4px; padding: 2px 5px; border-radius: 6px; background: var(--soft); font-size: 10px; }
      .uxbp-up { position: relative; overflow: hidden; }
      .uxbp-up input { position: absolute; width: 1px; height: 1px; opacity: 0; }
      .uxbp-error { margin: 0 2px; padding: 6px 9px; border-radius: 8px; color: var(--dsw-alias-state-error-primary, #a52c28);
        background: color-mix(in srgb, var(--dsw-alias-state-error-primary, #a52c28) 9%, var(--card)); font-size: 11px; }
      .uxbp-aside { min-width: 0; min-height: 0; display: flex; flex-direction: column; gap: 8px; }
      .uxbp-panel { min-height: 0; display: flex; flex-direction: column; border: 1px solid var(--line); border-radius: var(--radius);
        background: var(--card); box-shadow: var(--shadow); overflow: hidden; }
      .uxbp-panel-head { flex: none; padding: 10px 12px; border-bottom: 1px solid var(--line); }
      .uxbp-taskline { display: flex; align-items: baseline; justify-content: space-between; gap: 6px; }
      .uxbp-taskline strong { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 13px; }
      .uxbp-meta { color: var(--muted); font-size: 10px; font-variant-numeric: tabular-nums; }
      .uxbp-actions { display: flex; gap: 4px; margin-top: 7px; flex-wrap: wrap; }
      .uxbp-actions .uxbp-btn { min-height: 25px; padding: 2px 6px; font-size: 10px; }
      .uxbp-subtabs { display: flex; gap: 3px; margin-top: 8px; }
      .uxbp-subtab { border: 0; border-radius: 6px; padding: 3px 7px; background: transparent; color: var(--muted);
        font: inherit; font-size: 11px; cursor: pointer; }
      .uxbp-subtab[data-on="true"] { background: var(--soft); color: var(--ink); font-weight: 650; }
      .uxbp-scroll { flex: 1; min-height: 0; overflow: auto; padding: 8px 10px; }
      .uxbp-node { padding: 7px 0; border-bottom: 1px solid color-mix(in srgb, var(--line) 65%, transparent); }
      .uxbp-node:last-child { border-bottom: 0; }
      .uxbp-node-head { display: flex; align-items: baseline; gap: 6px; flex-wrap: wrap; }
      .uxbp-node-head strong { font-size: 12px; }
      .uxbp-node pre { margin: 6px 0 0; max-height: 260px; overflow: auto; white-space: pre-wrap; overflow-wrap: anywhere;
        font: 11px/1.6 ui-monospace, SFMono-Regular, Menlo, monospace; color: var(--ink); }
      .uxbp-msg { padding: 6px 0; font-size: 12px; white-space: pre-wrap; overflow-wrap: anywhere; }
      .uxbp-msg b { color: var(--muted); font-size: 10px; font-weight: 650; }
      .uxbp-next { flex: none; max-height: 38%; overflow: auto; padding: 9px 11px; }
      .uxbp-next h3 { margin: 0 0 7px; color: var(--muted); font-size: 11px; }
      .uxbp-next-main { width: 100%; text-align: left; padding: 9px; border: 1px solid color-mix(in srgb, var(--accent) 40%, var(--line));
        border-radius: 9px; background: color-mix(in srgb, var(--accent) 9%, var(--card)); color: var(--ink);
        font: inherit; cursor: pointer; }
      .uxbp-next-main strong { display: block; font-size: 12px; }
      .uxbp-next-main span { display: block; margin-top: 3px; color: var(--muted); font-size: 10px; }
      .uxbp-next-alt { width: 100%; text-align: left; padding: 6px 4px; border: 0; border-bottom: 1px solid var(--line);
        background: transparent; color: var(--ink); font: inherit; font-size: 11px; cursor: pointer; }
      .uxbp-next-alt span { display: block; color: var(--muted); font-size: 10px; }
      .uxbp-empty { margin: 12px 0; color: var(--muted); font-size: 12px; line-height: 1.7; }
      .uxbp-sediment { flex: 1; min-height: 0; overflow: auto; padding: 4px; display: grid; gap: 8px; align-content: start; }
      .uxbp-taskcard { display: flex; align-items: center; gap: 12px; padding: 11px 13px; border: 1px solid var(--line);
        border-radius: 12px; background: var(--card); box-shadow: var(--shadow); cursor: pointer; text-align: left; }
      .uxbp-taskcard:hover { border-color: color-mix(in srgb, var(--accent) 40%, var(--line)); }
      .uxbp-taskcard-main { flex: 1; min-width: 0; }
      .uxbp-taskcard-main strong { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 13px; }
      .uxbp-taskcard-main span { display: block; margin-top: 2px; color: var(--muted); font-size: 10px; }
      .uxbp-status { flex: none; padding: 2px 6px; border-radius: 999px; background: var(--soft); color: var(--muted); font-size: 10px; }
      .uxbp-status[data-status="active"] { color: var(--accent); background: color-mix(in srgb, var(--accent) 12%, var(--card)); }
      .uxbp-status[data-status="completed"] { color: #216b51; background: #edf7f1; }
      @container (max-width: 1080px) {
        .uxbp-body { grid-template-columns: minmax(0, 1fr); }
        .uxbp-aside { max-height: 42vh; }
      }
      @container (max-width: 700px) {
        .uxbp-root { padding: 10px; gap: 8px; }
        .uxbp-brand .uxbp-title { display: none; }
        .uxbp-card { width: 180px; height: 238px; }
        .uxbp-art { height: 96px; }
        .uxbp-plane { padding: 12px; }
        .uxbp-picker > span { max-width: 100px; }
      }
    `

    function button(active) {
      return { background: active ? 'var(--accent)' : undefined, color: active ? '#fff' : undefined }
    }

    function PanelIcon() {
      return h('svg', { viewBox: '0 0 24 24', width: 18, height: 18, 'aria-hidden': true },
        h('path', { d: 'M12 2.5 21.5 12 12 21.5 2.5 12Z', fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinejoin: 'round' }),
        h('circle', { cx: 12, cy: 12, r: 2, fill: 'currentColor' }))
    }

    function Icon({ path }) {
      return h('svg', { viewBox: '0 0 24 24', width: 15, height: 15, 'aria-hidden': true },
        h('path', { d: path, fill: 'none', stroke: 'currentColor', strokeWidth: 1.7, strokeLinecap: 'round', strokeLinejoin: 'round' }))
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

    async function uploadFile(sessionId, file) {
      const query = new URLSearchParams({ sessionId, name: file.name })
      if (['image/png', 'image/jpeg', 'image/webp', 'image/gif'].includes(file.type)) query.set('mediaType', file.type)
      const url = new URL('api/session/uploadFileBinary', document.baseURI)
      url.search = query.toString()
      const response = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: file, credentials: 'include' })
      if (!response.ok) throw new Error(file.name + ' · HTTP ' + response.status)
      const result = await response.json()
      if (!result.ok || !result.value?.receiptId) throw new Error(file.name + ' · ' + (result.error?.message || '上传失败'))
      return { type: 'file', receiptId: result.value.receiptId }
    }

    function textOf(value) {
      const out = []
      const walk = (value, depth = 0) => {
        if (value == null || depth > 7) return
        if (typeof value === 'string') { if (value.trim()) out.push(value); return }
        if (Array.isArray(value)) { value.forEach(item => walk(item, depth + 1)); return }
        if (typeof value !== 'object') return
        if (typeof value.text === 'string') { out.push(value.text); return }
        for (const key of ['data', 'content', 'message', 'chunk', 'blocks', 'delta', 'value']) {
          if (key in value) walk(value[key], depth + 1)
        }
      }
      walk(value)
      return out.join('\n').trim()
    }

    function toolCallsOf(value, out = [], depth = 0) {
      if (value == null || depth > 8) return out
      if (Array.isArray(value)) { value.forEach(item => toolCallsOf(item, out, depth + 1)); return out }
      if (typeof value !== 'object') return out
      if (value.type === 'tool-call') { out.push(value); return out }
      for (const key of ['data', 'message', 'content', 'blocks']) if (key in value) toolCallsOf(value[key], out, depth + 1)
      return out
    }

    function argsOf(call) {
      const value = call?.arguments ?? call?.input
      if (typeof value === 'string') { try { return JSON.parse(value) } catch { return {} } }
      return value && typeof value === 'object' ? value : {}
    }

    function short(value, limit = 80) {
      const text = String(value ?? '').replace(/\s+/g, ' ').trim()
      return text.length > limit ? text.slice(0, limit - 1) + '…' : text
    }

    function baseName(value) {
      const parts = String(value ?? '').split(/[\\/]/)
      return parts[parts.length - 1] || String(value ?? '')
    }

    function inSegments(seq, segments) {
      return (segments ?? []).some(segment => seq > segment.startSeq && (segment.endSeq == null || seq <= segment.endSeq))
    }

    const toolLabels = {
      skill: ['加载技能', 'name'], read: ['阅读材料', 'file_path'], glob: ['查找材料', 'pattern'], grep: ['查找材料', 'pattern'],
      read_design_reference: ['查知识', 'path'], web_search: ['查资料', 'query'], web_fetch: ['查资料', 'url'],
      submit_design_artifact: ['当前阶段输出', 'skill'], design_next_steps: ['计算下一步', ''],
      write: ['写入文件', 'file_path'], edit: ['修改文件', 'file_path'], pwsh: ['执行命令', 'description'],
    }

    function callNode(call) {
      const name = String(call?.name ?? 'tool')
      const args = argsOf(call)
      const mapped = toolLabels[name] ?? ['执行工具', '']
      const detail = mapped[1] ? short(args[mapped[1]], 60) : name
      if (name === 'read' || name === 'glob' || name === 'grep') return { kind: 'read', label: mapped[0], detail: baseName(detail), status: 'running' }
      if (name === 'submit_design_artifact') return {
        kind: 'output', label: '当前阶段输出', detail: short(args.skill, 50), status: 'running',
        markdown: typeof args.markdown === 'string' ? args.markdown : '',
      }
      return { kind: 'tool', label: mapped[0], detail, status: 'running' }
    }

    function buildFlow(entries, segments) {
      const nodes = []
      const byCall = new Map()
      const push = node => { nodes.push(node); return nodes.length - 1 }
      for (const entry of entries) {
        const event = entry.event
        if (!event || !inSegments(event.seq ?? 0, segments)) continue
        if (event.type === 'user/message') {
          const kind = event.data?.source?.kind
          if (kind && kind !== 'user' && kind !== 'user-question-reply') continue
          const text = textOf(event.data)
          if (text) push({ kind: 'task', label: '接收任务', detail: short(text.replace(/^【技能：[^\n]*】\s*/, '')), status: 'done' })
        } else if (event.type === 'assistant/message') {
          const calls = toolCallsOf(event.data)
          if (calls.length) {
            for (const call of calls) {
              const index = push(callNode(call))
              if (call.id) byCall.set(call.id, index)
            }
          } else {
            const text = textOf(event.data)
            if (text) push({ kind: 'assistant', label: '生成结果', detail: short(text), text: text.slice(0, 2000), status: 'done' })
          }
        } else if (event.type === 'tool/result') {
          const index = byCall.get(event.data?.toolCallId ?? event.data?.message?.toolCallId)
          if (index === undefined) continue
          const text = textOf(event.data)
          nodes[index].status = /error|failed|失败|拒绝/i.test(text.slice(0, 160)) ? 'failed' : 'done'
        }
      }
      const merged = []
      for (const node of nodes) {
        const prev = merged[merged.length - 1]
        if (prev && prev.kind === node.kind && node.kind === 'assistant') { prev.text = node.text; prev.detail = node.detail; continue }
        if (prev && prev.kind === node.kind && ['read', 'tool'].includes(node.kind)) { prev.count = (prev.count ?? 1) + 1; prev.detail = prev.count + ' 项'; continue }
        merged.push(node)
      }
      let latest = -1
      merged.forEach((node, index) => { if (node.kind === 'output') latest = index })
      merged.forEach((node, index) => { node.latest = index === latest })
      return merged
    }

    function dialogueRows(entries, segments) {
      const rows = []
      for (const entry of entries) {
        const event = entry.event
        if (!event || !inSegments(event.seq ?? 0, segments)) continue
        if (event.type === 'user/message') {
          const kind = event.data?.source?.kind
          if (kind && kind !== 'user' && kind !== 'user-question-reply') continue
          const text = textOf(event.data)
          if (text) rows.push({ role: 'user', text })
        } else if (event.type === 'assistant/message') {
          const text = textOf(event.data)
          if (text) rows.push({ role: 'assistant', text })
        }
      }
      return rows.slice(-120)
    }

    function artStyle(skillId) {
      let hash = 0
      for (const char of skillId) hash = (hash * 31 + char.charCodeAt(0)) >>> 0
      const hue = hash % 360
      return {
        background: `linear-gradient(135deg, hsl(${hue} 48% 86%), hsl(${(hue + 46) % 360} 42% 68%))`,
      }
    }

    function groupOf(phase) {
      if (phase === 1) return 0
      if (phase === 2) return 1
      return 2
    }

    function Workbench({ translate: t, locale, sessions, uiWorkspace }) {
      const subscribe = callback => locale.subscribe(callback)
      const snapshot = () => locale.getSnapshot()
      useSyncExternalStore(subscribe, snapshot, snapshot)

      const [workspaces, setWorkspaces] = useState([])
      const [catalog, setCatalog] = useState([])
      const [workspace, setWorkspace] = useState('')
      const [conversations, setConversations] = useState([])
      const [tasks, setTasks] = useState([])
      const [task, setTask] = useState(null)
      const [manifest, setManifest] = useState(null)
      const [next, setNext] = useState([])
      const [sessionId, setSessionId] = useState('')
      const [tab, setTab] = useState('task')
      const [rightTab, setRightTab] = useState('dynamics')
      const [text, setText] = useState('')
      const [files, setFiles] = useState([])
      const [skill, setSkill] = useState('')
      const [error, setError] = useState('')
      const [sending, setSending] = useState(false)
      const [flow, setFlow] = useState([])
      const [dialogue, setDialogue] = useState([])
      const [running, setRunning] = useState(false)
      const [filter, setFilter] = useState('all')
      const [search, setSearch] = useState('')
      const [openMenu, setOpenMenu] = useState('')
      const [art, setArt] = useState({})
      const [shake, setShake] = useState('')
      const canvasRef = useRef(null)
      const inputRef = useRef(null)
      const binding = useRef(null)
      const submitting = useRef(false)
      const drag = useRef({ down: false, moved: false, x: 0, y: 0, left: 0, top: 0 })
      const refreshRef = useRef(() => {})
      const saved = useRef((() => {
        try { return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? 'null') } catch { return null }
      })())
      const restored = useRef(false)

      const nameOf = value => catalog.find(item => item.id === value)?.name ?? value
      const taskId = task?.id ?? ''
      const statusLabel = status => status === 'active' ? t('active') : status === 'paused' ? t('paused') : t('completed')
      const segmentKey = JSON.stringify(task?.segments ?? [])
      const groups = [
        { label: '探索与定义', items: catalog.filter(item => groupOf(item.phase) === 0) },
        { label: '设计与交付', items: catalog.filter(item => groupOf(item.phase) === 1) },
        { label: '分析与证据', items: catalog.filter(item => groupOf(item.phase) === 2) },
      ]
      const filteredTasks = tasks.filter(item => {
        if (filter !== 'all' && item.status !== filter) return false
        const query = search.trim().toLowerCase()
        return !query || item.title.toLowerCase().includes(query) || item.id.toLowerCase().includes(query)
      })

      function save(value) {
        try { localStorage.setItem(STORAGE_KEY, JSON.stringify(value)) } catch {}
      }

      async function loadWorkspaceData(target = workspace) {
        if (!target) return
        const data = await api({ workspace: target })
        setConversations(data.sessions ?? [])
        setTasks(data.tasks ?? [])
        return data
      }

      async function loadTask(id) {
        if (!id) { setTask(null); setManifest(null); setNext([]); return }
        const data = await api({ workspace, task: id })
        setTask(data.task)
        setManifest(data.manifest)
        setNext(data.next ?? [])
        setSessionId(data.task.sessionId)
        save({ workspace, sessionId: data.task.sessionId, activeTaskId: id })
        return data
      }

      async function refreshTask() {
        if (!task?.id) return
        try { await loadTask(task.id) } catch {}
      }

      useEffect(() => {
        const controller = new AbortController()
        api(null, null, controller.signal).then(data => {
          const list = data.workspaces ?? []
          const stored = saved.current
          const preferred = stored?.workspace && list.some(item => item.id === stored.workspace) ? stored.workspace : list[0]?.id
          setWorkspaces(list)
          setCatalog(data.catalog ?? [])
          setWorkspace(current => current || preferred || '')
        }).catch(e => { if (!controller.signal.aborted) setError(e.message) })
        return () => controller.abort()
      }, [])

      useEffect(() => {
        if (!workspace) return
        let disposed = false
        loadWorkspaceData(workspace).then(async data => {
          if (disposed) return
          if (!restored.current) {
            restored.current = true
            const stored = saved.current
            const target = stored?.activeTaskId && (data.tasks ?? []).some(item => item.id === stored.activeTaskId)
              ? stored.activeTaskId
              : ''
            if (target) {
              try { await loadTask(target) } catch {}
            } else if (stored?.sessionId && (data.sessions ?? []).some(item => item.id === stored.sessionId)) {
              setSessionId(stored.sessionId)
              save({ workspace, sessionId: stored.sessionId, activeTaskId: '' })
            }
          }
        }).catch(e => { if (!disposed) setError(e.message) })
        return () => { disposed = true }
      }, [workspace])

      useEffect(() => {
        if (!sessionId) { setFlow([]); setDialogue([]); setRunning(false); return }
        let disposed = false
        let offEvents
        let offSession
        let ref
        let refreshTimer
        try { ref = sessions.retain(sessionId, { source: 'controllerOperation' }) } catch (e) { setError(e.message); return }
        ref.ready.then(value => {
          if (disposed) return
          binding.current = value
          const update = () => {
            if (disposed) return
            const entries = value.eventSource.getSnapshot().entries ?? []
            setFlow(buildFlow(entries, task?.segments ?? []))
            setDialogue(dialogueRows(entries, task?.segments ?? []))
            setRunning(Boolean(value.session.getSnapshot().running))
            if (entries.some(entry => entry.event?.type === 'tool/result')) {
              clearTimeout(refreshTimer)
              refreshTimer = setTimeout(() => refreshRef.current(), 400)
            }
          }
          offEvents = value.eventSource.subscribe(update)
          offSession = value.session.subscribe(update)
          update()
        }).catch(e => { if (!disposed) setError(e.message) })
        return () => {
          disposed = true
          clearTimeout(refreshTimer)
          if (offEvents) offEvents()
          if (offSession) offSession()
          binding.current = null
          try { ref?.release() } catch {}
        }
      }, [sessionId, taskId, segmentKey])

      refreshRef.current = refreshTask

      useEffect(() => {
        if (!openMenu) return
        const close = event => { if (!event.target.closest('.uxbp-picker')) setOpenMenu('') }
        const esc = event => { if (event.key === 'Escape') setOpenMenu('') }
        document.addEventListener('pointerdown', close)
        document.addEventListener('keydown', esc)
        return () => {
          document.removeEventListener('pointerdown', close)
          document.removeEventListener('keydown', esc)
        }
      }, [openMenu])


      function useSkill(skillId) {
        setSkill(skillId)
        setTab('task')
        inputRef.current?.focus()
      }

      function shakeCard(skillId) {
        setShake(skillId)
        setTimeout(() => setShake(current => current === skillId ? '' : current), 240)
      }

      function selectWorkspace(id) {
        if (id === workspace) return
        setWorkspace(id)
        setTask(null); setManifest(null); setNext([]); setTasks([]); setConversations([]); setSessionId('')
        setArt({}); setOpenMenu('')
        save({ workspace: id, sessionId: '', activeTaskId: '' })
      }

      function resetAll() {
        try { localStorage.removeItem(STORAGE_KEY) } catch {}
        saved.current = null
        setWorkspace(''); setTask(null); setManifest(null); setNext([]); setTasks([]); setConversations([])
        setSessionId(''); setFlow([]); setDialogue([]); setSkill(''); setText(''); setFiles([]); setError('')
        setTab('task'); setOpenMenu('')
      }

      async function ensureSession() {
        if (sessionId) return sessionId
        if (!workspace) throw new Error('请先选择工作区')
        const data = await api(null, { action: 'create-session', workspaceId: workspace })
        setSessionId(data.sessionId)
        setConversations(current => [{ id: data.sessionId, title: t('session'), updatedAt: Date.now() }, ...current])
        return data.sessionId
      }

      async function execute() {
        if (submitting.current || !workspace || !skill || (!text.trim() && !files.length)) return
        submitting.current = true
        setSending(true)
        setError('')
        try {
          const targetSession = task?.sessionId || await ensureSession()
          let current = task
          if (current?.status === 'completed') throw new Error('任务已完成，请先恢复任务再执行')
          if (current?.status === 'paused') {
            const data = await api(null, { action: 'resume', workspaceId: workspace, taskId: current.id })
            current = data.task
            setTask(current)
          }
          let prompt
          if (!current) {
            const data = await api(null, {
              action: 'create-task', workspaceId: workspace, sessionId: targetSession, skill,
              title: text.trim().slice(0, 40), text,
            })
            current = data.task
            prompt = data.prompt
            setTask(current)
            setTasks(items => [current, ...items.filter(item => item.id !== current.id)])
            setSessionId(targetSession)
            save({ workspace, sessionId: targetSession, activeTaskId: current.id })
          } else {
            const data = await api(null, { action: 'prompt', workspaceId: workspace, taskId: current.id, skill, text })
            prompt = data.prompt
          }
          const ref = sessions.retain(targetSession, { source: 'controllerOperation' })
          const value = await ref.ready
          try {
            const content = []
            for (const file of files) content.push(await uploadFile(targetSession, file))
            content.push({ type: 'text', text: prompt })
            const result = await value.session.prompt(content, 'queue')
            if (result?.ok === false) throw new Error(result.error?.message || '执行失败')
          } finally { ref.release() }
          setText('')
          setFiles([])
          await loadTask(current.id)
          await loadWorkspaceData(workspace)
        } catch (e) {
          setError(e.message)
        } finally {
          submitting.current = false
          setSending(false)
        }
      }

      async function action(name, payload = {}) {
        if (!task) return
        try {
          await api(null, { action: name, workspaceId: workspace, taskId: task.id, ...payload })
          if (name === 'complete') {
            setTask(null); setManifest(null); setNext([]); setSessionId('')
            save({ workspace, sessionId: '', activeTaskId: '' })
          } else if (name === 'pause') {
            await loadTask(task.id)
          } else {
            await loadTask(task.id)
          }
          await loadWorkspaceData(workspace)
        } catch (e) { setError(e.message) }
      }

      async function rename() {
        if (!task) return
        const title = window.prompt(t('rename'), task.title)
        if (title && title.trim()) await action('rename', { title: title.trim() })
      }

      async function openTask(item) {
        try {
          if (task && task.id !== item.id && task.status === 'active') {
            await api(null, { action: 'pause', workspaceId: workspace, taskId: task.id })
          }
          if (item.status === 'paused') {
            await api(null, { action: 'resume', workspaceId: workspace, taskId: item.id })
          }
          await loadTask(item.id)
          setTab('task')
          await loadWorkspaceData(workspace)
        } catch (e) { setError(e.message) }
      }

      async function newTask() {
        if (task?.status === 'active') {
          try { await api(null, { action: 'pause', workspaceId: workspace, taskId: task.id }) } catch (e) { setError(e.message); return }
        }
        setTask(null); setManifest(null); setNext([]); setSessionId('')
        save({ workspace, sessionId: '', activeTaskId: '' })
        await loadWorkspaceData(workspace)
      }

      async function viewArtifact(skillId) {
        try {
          const data = await api({ workspace, task: task.id, skill: skillId })
          setArt({ skill: skillId, content: data.content })
          setRightTab('dynamics')
        } catch (e) { setError(e.message) }
      }

      function onPointerDown(event) {
        if (event.button !== 0) return
        const canvas = canvasRef.current
        if (!canvas) return
        drag.current = { down: true, moved: false, x: event.clientX, y: event.clientY, left: canvas.scrollLeft, top: canvas.scrollTop }
        canvas.dataset.drag = 'true'
      }

      function onPointerMove(event) {
        if (!drag.current.down) return
        const canvas = canvasRef.current
        if (!canvas) return
        const dx = event.clientX - drag.current.x
        const dy = event.clientY - drag.current.y
        if (Math.abs(dx) + Math.abs(dy) > 5) drag.current.moved = true
        if (drag.current.moved) {
          canvas.scrollLeft = drag.current.left - dx
          canvas.scrollTop = drag.current.top - dy
        }
      }

      function onPointerUp() {
        if (!drag.current.down) return
        drag.current.down = false
        if (canvasRef.current) delete canvasRef.current.dataset.drag
      }

      function cardClick(item) {
        if (drag.current.moved) return
        shakeCard(item.id)
        useSkill(item.id)
        setArt({})
      }

      const sessionTitle = conversations.find(item => item.id === sessionId)?.title ?? (sessionId ? t('session') : t('newSession'))
      const status = task ? statusLabel(task.status) : ''

      return h('main', { className: 'uxbp-root' },
        h('style', null, styles),
        h('header', { className: 'uxbp-top' },
          h('div', { className: 'uxbp-brand' },
            h('span', { className: 'uxbp-mark' }, h(PanelIcon)),
            h('h1', { className: 'uxbp-title' }, t('title')),
            h('div', { className: 'uxbp-tabs', role: 'group' },
              h('button', { type: 'button', className: 'uxbp-tab', 'data-on': tab === 'task', onClick: () => setTab('task') }, t('task')),
              h('button', { type: 'button', className: 'uxbp-tab', 'data-on': tab === 'sediment', onClick: () => setTab('sediment') }, t('sediment')))),
          h('div', { className: 'uxbp-right-top' },
            h('div', { className: 'uxbp-picker' },
              h('button', { type: 'button', className: 'uxbp-btn', 'aria-expanded': openMenu === 'workspace', onClick: () => setOpenMenu(openMenu === 'workspace' ? '' : 'workspace') },
                h(Icon, { path: 'M4 6h16v12H4z M4 7l8 6 8-6' }),
                h('span', null, workspaces.find(item => item.id === workspace)?.title ?? t('workspace')),
                h(Icon, { path: 'm7 10 5 5 5-5' })),
              openMenu === 'workspace' && h('div', { className: 'uxbp-menu' },
                ...workspaces.map(item => h('button', {
                  key: item.id, type: 'button', className: 'uxbp-option', 'data-on': item.id === workspace,
                  onClick: () => { setOpenMenu(''); selectWorkspace(item.id) },
                }, item.title)))),
            h('button', { type: 'button', className: 'uxbp-btn uxbp-icon', title: t('reset'), 'aria-label': t('reset'), onClick: resetAll },
              h(Icon, { path: 'M20 12a8 8 0 1 1-2.3-5.7M20 4v6h-6' })))),

        error && h('p', { className: 'uxbp-error', role: 'alert' }, error),

        tab === 'task'
          ? h('div', { className: 'uxbp-body' },
            h('section', { className: 'uxbp-left' },
              h('div', {
                ref: canvasRef, className: 'uxbp-canvas',
                onPointerDown, onPointerMove, onPointerUp, onPointerLeave: onPointerUp,
              },
              h('div', { className: 'uxbp-plane' },
                ...groups.map((group, groupIndex) => h('section', { key: group.label, className: 'uxbp-group' },
                  h('h2', null, group.label + '  ' + group.items.length),
                  h('div', { className: 'uxbp-cards' }, ...group.items.map((item, index) => {
                    const rot = ((index % 3) - 1) * 1.6
                    const off = (index % 2) * 10
                    return h('button', {
                      key: item.id, type: 'button', className: 'uxbp-card',
                      style: { '--rot': rot + 'deg', '--off': off + 'px' },
                      'data-shake': shake === item.id,
                      onClick: () => cardClick(item),
                      onFocus: () => shakeCard(item.id),
                      onDoubleClick: () => useSkill(item.id),
                    },
                    h('span', { className: 'uxbp-art', style: artStyle(item.id) }),
                    h('span', { className: 'uxbp-card-body' },
                      h('strong', null, item.name),
                      h('p', null, item.id + ' · ' + (item.phase === 1 ? '探索与定义' : item.phase === 2 ? '设计与交付' : '分析与证据'))),
                    h('span', { className: 'uxbp-card-foot' },
                      h('code', null, '/' + item.id),
                      h('span', { className: 'uxbp-use', role: 'button', tabIndex: 0, onClick: event => { event.stopPropagation(); shakeCard(item.id); useSkill(item.id) } }, t('useSkill'))))
                  }))))),
              h('div', { className: 'uxbp-composer' },
                files.length > 0 && h('div', { style: { display: 'flex', gap: 4, flexWrap: 'wrap', padding: '2px 4px' } },
                  ...files.map((file, index) => h('span', { key: index, className: 'uxbp-file' }, file.name,
                    h('button', { type: 'button', 'aria-label': t('remove'), onClick: () => setFiles(items => items.filter((_, i) => i !== index)) }, '×')))),
                skill && h('div', { style: { padding: '2px 4px 0' } },
                  h('span', { className: 'uxbp-chip' }, h('span', null, 'Skill: ' + nameOf(skill)),
                    h('button', { type: 'button', 'aria-label': t('remove'), onClick: () => setSkill('') }, '×'))),
                h('textarea', {
                  ref: inputRef, className: 'uxbp-input', value: text, placeholder: t('placeholder'), disabled: sending,
                  onChange: event => setText(event.target.value),
                  onKeyDown: event => {
                    if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
                      event.preventDefault(); void execute()
                    }
                  },
                }),
                h('div', { className: 'uxbp-tools' },
                  h('div', { className: 'uxbp-tools-left' },
                    h('label', { className: 'uxbp-btn uxbp-icon uxbp-up', title: t('attach'), 'aria-label': t('attach') },
                      h('input', { type: 'file', multiple: true, onChange: event => {
                        setFiles(items => [...items, ...Array.from(event.currentTarget.files ?? [])])
                        event.currentTarget.value = ''
                      } }),
                      h(Icon, { path: 'M20 11 11 20a5 5 0 0 1-7-7l9-9a3.5 3.5 0 0 1 5 5l-9 9a2 2 0 0 1-3-3l8-8' })),
                    h('div', { className: 'uxbp-picker' },
                      h('button', { type: 'button', className: 'uxbp-btn', 'aria-expanded': openMenu === 'skill', onClick: () => setOpenMenu(openMenu === 'skill' ? '' : 'skill') },
                        h(Icon, { path: 'M12 2 14.5 9.5 22 12 14.5 14.5 12 22 9.5 14.5 2 12 9.5 9.5Z' }),
                        t('skill')),
                      openMenu === 'skill' && h('div', { className: 'uxbp-menu' },
                        ...catalog.map(item => h('button', {
                          key: item.id, type: 'button', className: 'uxbp-option', 'data-on': skill === item.id,
                          onClick: () => { setSkill(item.id); setOpenMenu('') },
                        }, item.name, h('span', { className: 'uxbp-meta' }, '/' + item.id))))),
                    h('div', { className: 'uxbp-picker' },
                      h('button', { type: 'button', className: 'uxbp-btn', 'aria-expanded': openMenu === 'session', disabled: Boolean(task), title: task ? t('session') : sessionTitle, onClick: () => setOpenMenu(openMenu === 'session' ? '' : 'session') },
                        h(Icon, { path: 'M4 5h16v11H9l-5 4V5Z' }),
                        h('span', null, sessionTitle),
                        h(Icon, { path: 'm7 10 5 5 5-5' })),
                      openMenu === 'session' && h('div', { className: 'uxbp-menu' },
                        h('button', { type: 'button', className: 'uxbp-option', 'data-on': !sessionId, onClick: () => { setSessionId(''); setOpenMenu(''); save({ workspace, sessionId: '', activeTaskId: task?.id ?? '' }) } }, t('newSession')),
                        ...conversations.map(item => h('button', {
                          key: item.id, type: 'button', className: 'uxbp-option', 'data-on': item.id === sessionId,
                          onClick: () => { setSessionId(item.id); setOpenMenu(''); save({ workspace, sessionId: item.id, activeTaskId: task?.id ?? '' }) },
                        }, item.title))))),
                  h('div', { className: 'uxbp-tools-right' },
                    running && h('button', { type: 'button', className: 'uxbp-btn', onClick: () => binding.current?.session.cancel() }, t('stop')),
                    h('button', { type: 'button', className: 'uxbp-btn', disabled: !sessionId, onClick: () => sessionId && uiWorkspace.openSession(sessionId) }, t('enter')),
                    h('button', { type: 'button', className: 'uxbp-btn uxbp-primary', disabled: sending || !skill || (!text.trim() && !files.length), onClick: () => void execute() }, t('execute')))))),
            h('aside', { className: 'uxbp-aside' },
              h('section', { className: 'uxbp-panel' },
                h('div', { className: 'uxbp-panel-head' },
                  task
                    ? h('div', null,
                      h('div', { className: 'uxbp-taskline' },
                        h('strong', null, task.title), h('span', { className: 'uxbp-status', 'data-status': task.status }, status)),
                      h('div', { className: 'uxbp-meta' }, task.id),
                      h('div', { className: 'uxbp-actions' },
                        h('button', { className: 'uxbp-btn', onClick: () => void action('pause'), disabled: task.status !== 'active' }, t('pause')),
                        h('button', { className: 'uxbp-btn', onClick: () => void action('resume'), disabled: task.status === 'active' }, t('resume')),
                        h('button', { className: 'uxbp-btn', onClick: () => void action('complete'), disabled: task.status === 'completed' }, t('end')),
                        h('button', { className: 'uxbp-btn', onClick: () => void rename() }, t('rename')),
                        h('button', { className: 'uxbp-btn', onClick: () => void newTask() }, t('newTask'))))
                    : h('div', null, h('strong', null, t('noTask')), h('div', { className: 'uxbp-meta' }, taskId))),
                task && h('div', { className: 'uxbp-subtabs' },
                  h('button', { className: 'uxbp-subtab', 'data-on': rightTab === 'dynamics', onClick: () => setRightTab('dynamics') }, t('dynamics')),
                  h('button', { className: 'uxbp-subtab', 'data-on': rightTab === 'dialogue', onClick: () => setRightTab('dialogue') }, t('dialogue'))),
                h('div', { className: 'uxbp-scroll' },
                  !task && h('p', { className: 'uxbp-empty' }, t('noTask')),
                  task && rightTab === 'dynamics' && (flow.length
                    ? flow.map((node, index) => h('div', { key: index, className: 'uxbp-node' },
                      h('div', { className: 'uxbp-node-head' },
                        h('span', { 'aria-hidden': true, style: { color: node.status === 'failed' ? 'var(--dsw-alias-state-error-primary, #a52c28)' : 'var(--muted)' } }, node.status === 'running' ? '●' : node.status === 'failed' ? '✕' : '✓'),
                        h('strong', null, node.label),
                        node.detail && h('span', { className: 'uxbp-meta' }, node.detail)),
                      node.markdown && node.latest && h('pre', null, node.markdown),
                      node.text && h('div', { className: 'uxbp-msg' }, node.text)))
                    : h('p', { className: 'uxbp-empty' }, t('noTask'))),
                  task && rightTab === 'dialogue' && (dialogue.length
                    ? dialogue.map((row, index) => h('div', { key: index, className: 'uxbp-msg' },
                        h('b', null, row.role === 'user' ? '你' : 'AI'), ' ', row.text))
                    : h('p', { className: 'uxbp-empty' }, t('noDialogue'))))),
                h('div', { className: 'uxbp-next' },
                  h('h3', null, t('next')),
                  next.length === 0 && h('p', { className: 'uxbp-empty' }, t('noNext')),
                  ...next.slice(0, 3).map((item, index) => index === 0
                    ? h('button', { key: item.id, className: 'uxbp-next-main', onClick: () => useSkill(item.id) },
                        h('strong', null, item.name), h('span', null, item.reason))
                    : h('button', { key: item.id, className: 'uxbp-next-alt', onClick: () => useSkill(item.id) },
                        item.name, h('span', null, item.reason)))),
                art.content && h('div', { className: 'uxbp-next' },
                  h('h3', null, nameOf(art.skill)),
                  h('pre', { style: { maxHeight: 180, overflow: 'auto', whiteSpace: 'pre-wrap', fontSize: 11 } }, art.content)))))
          : h('section', { className: 'uxbp-panel', style: { flex: 1, minHeight: 0 } },
            h('div', { className: 'uxbp-panel-head', style: { display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' } },
              h('input', { className: 'uxbp-btn', style: { minWidth: 180, flex: '1 1 200px' }, placeholder: t('search'), value: search, onChange: event => setSearch(event.target.value) }),
              ...['all', 'active', 'paused', 'completed'].map(item => h('button', {
                key: item, type: 'button', className: 'uxbp-btn', 'data-on': filter === item,
                onClick: () => setFilter(item),
              }, item === 'all' ? t('all') : statusLabel(item)))),
            h('div', { className: 'uxbp-sediment' },
              filteredTasks.length === 0 && h('p', { className: 'uxbp-empty' }, t('emptySediment')),
              ...filteredTasks.map(item => h('button', {
                key: item.id, type: 'button', className: 'uxbp-taskcard', onClick: () => void openTask(item),
              },
              h('span', { className: 'uxbp-taskcard-main' },
                h('strong', null, item.title),
                h('span', null, item.id + ' · ' + (item.skills ?? []).map(nameOf).join(' → '))),
              h('span', { className: 'uxbp-status', 'data-status': item.status }, statusLabel(item.status)))))))
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
            h(Workbench, { ...props, translate: t, locale: ctx.locale, sessions: ctx.sessions, uiWorkspace: ctx.uiWorkspace })))
      },
    }
  },
})
