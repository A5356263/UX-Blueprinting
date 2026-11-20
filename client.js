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
      idle: 'Not started',
      progress: 'Progress',
      outputs: 'outputs',
      total: 'Total',
      items: 'items',
      board: 'Board',
      list: 'List',
      searchTasks: 'Search tasks',
      noSessions: 'No conversations yet.',
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
      idle: '未开始',
      progress: '任务进度',
      outputs: '产物',
      total: '共',
      items: '条',
      board: '看板',
      list: '表格',
      searchTasks: '搜索任务',
      noSessions: '还没有会话。',
      running: '执行中…',
      openTask: '打开',
      view: '查看',
      remove: '移除',
      history: '历史任务',
    }

    const styles = `
      @font-face {
        font-family: "UXBP Source Han Medium";
        src: local("Source Han Sans SC Medium"), local("SourceHanSansSC-Medium"), local("思源黑体 Medium");
        font-style: normal;
        font-weight: 500;
        font-display: swap;
      }
      .uxbp-root {
        --bg: var(--dsw-alias-bg-base, #f7f6f3);
        --card: var(--dsw-alias-bg-layer-2, #fff);
        --line: var(--dsw-alias-border-l2, #e6e1da);
        --line-strong: var(--dsw-alias-border-l4, #d4cec6);
        --ink: var(--dsw-alias-label-primary, #27231f);
        --muted: var(--dsw-alias-label-secondary, #686159);
        --faint: var(--dsw-alias-label-tertiary, #8a8279);
        --accent: var(--dsw-alias-link, #a8481e);
        --soft: var(--dsw-alias-interactive-bg-hover, #f4f3f0);
        --glass: color-mix(in srgb, var(--card) 72%, transparent);
        --radius: var(--dsw-radius-xl, 20px);
        --radius-md: var(--dsw-radius-md, 12px);
        --radius-sm: var(--dsw-radius-sm, 8px);
        --uxbp-card-width: 160px;
        --shadow: var(--dsw-elevation-soft, 0 3px 12px rgb(59 44 29 / .06));
        --serif: var(--sans);
        --sans: "UXBP Source Han Medium", -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif;
        --ease: cubic-bezier(.2, .8, .2, 1);
        position: relative; height: 100%; min-height: 0; box-sizing: border-box; display: flex; flex-direction: column;
        overflow: hidden; color: var(--ink); background: var(--bg);
        font: 500 14px/1.5 var(--sans);
        font-synthesis: none;
        container-type: inline-size;
      }
      .uxbp-root *, .uxbp-root *::before, .uxbp-root *::after { box-sizing: border-box; }
      .uxbp-root, .uxbp-root * { scrollbar-width: none; }
      .uxbp-root::-webkit-scrollbar, .uxbp-root *::-webkit-scrollbar { display: none; width: 0; height: 0; }
      .uxbp-root button, .uxbp-root input, .uxbp-root textarea, .uxbp-root select, .uxbp-root code, .uxbp-root pre { font-family: var(--sans); }
      .uxbp-top {
        position: absolute; z-index: 30; top: 14px; left: 18px; right: 325px;
        display: flex; align-items: center; justify-content: space-between; gap: 12px;
        padding: 0; background: transparent; border: 0; box-shadow: none; backdrop-filter: none; pointer-events: none;
      }
      .uxbp-top > * { pointer-events: auto; }
      .uxbp-brand { display: flex; align-items: center; gap: 10px; min-width: 0; background: transparent; border: 0; box-shadow: none; }
      .uxbp-mark { display: grid; place-items: center; width: 34px; height: 34px; flex: none; border-radius: 11px;
        color: var(--accent); background: color-mix(in srgb, var(--accent) 12%, var(--card)); }
      .uxbp-title { margin: 0; font-family: var(--serif); font-size: 17px; font-weight: 600; letter-spacing: .01em; white-space: nowrap; }
      .uxbp-tabs { display: flex; box-sizing: border-box; height: 34px; min-height: 34px; max-height: 34px; flex-shrink: 0;
        align-items: stretch; gap: 2px; padding: 3px; border-radius: 12px; background: color-mix(in srgb, var(--card) 92%, transparent);
        border: .5px solid var(--line); backdrop-filter: blur(24px) saturate(160%); box-shadow: var(--shadow); }
      .uxbp-tabs > .uxbp-tab { box-sizing: border-box; height: 100%; min-height: 0; max-height: 100%; display: inline-flex;
        align-items: center; justify-content: center; margin: 0; border: 0; border-radius: 8px; padding: 0 14px; background: transparent; color: var(--muted);
        font: inherit; font-size: 13px; line-height: 20px; font-weight: 500; cursor: pointer; transition: background .18s var(--ease), color .18s var(--ease); }
      .uxbp-tab:hover:not([data-on="true"]) { background: var(--soft); color: var(--ink); }
      .uxbp-tab[data-on="true"] { background: var(--ink); color: var(--card); box-shadow: none; }
      .uxbp-right-top { display: flex; align-items: center; gap: 6px; min-width: 0; }
      .uxbp-top .uxbp-btn { box-sizing: border-box; height: 34px; min-height: 34px; max-height: 34px;
        background: var(--glass); backdrop-filter: blur(24px) saturate(160%); box-shadow: var(--shadow); }
      .uxbp-btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; min-height: 34px;
        padding: 0 13px; border: .5px solid var(--line); border-radius: var(--radius-md); background: var(--card);
        color: var(--ink); font: inherit; font-size: 13px; cursor: pointer; white-space: nowrap; transition: background .15s, transform .25s var(--ease); }
      .uxbp-btn:hover:not(:disabled) { background: var(--soft); }
      .uxbp-btn:active:not(:disabled) { transform: scale(.97); }
      .uxbp-btn:disabled { opacity: .5; cursor: not-allowed; }
      .uxbp-icon { width: 34px; padding: 0; }
      .uxbp-primary { background: var(--dsw-alias-button-primary-fill, var(--accent)); border-color: transparent; color: var(--dsw-alias-label-primary-inverted, #fff); }
      .uxbp-picker { position: relative; }
      .uxbp-picker > span { min-width: 0; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      .uxbp-menu { position: absolute; z-index: 40; top: calc(100% + 5px); right: 0; min-width: 220px; max-height: 300px;
        overflow: auto; padding: 5px; border-radius: var(--radius-md); background: var(--card);
        backdrop-filter: blur(24px) saturate(160%); box-shadow: 0 16px 40px rgb(20 14 8 / .18); }
      .uxbp-wsmenu { width: 400px; max-width: calc(100vw - 36px); display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 4px; padding: 6px; overflow: hidden; }
      .uxbp-wspane, .uxbp-sessionpane { min-width: 0; max-height: 320px; overflow: auto; overflow-wrap: anywhere; }
      .uxbp-wspane { border-right: .5px solid var(--line); padding-right: 6px; }
      .uxbp-sessionpane { padding-left: 6px; }
      .uxbp-menu-title { padding: 6px 9px; color: var(--faint); font-size: 11px; }
      .uxbp-new-session { color: var(--accent); }
      .uxbp-option:disabled { opacity: .42; cursor: not-allowed; }
      .uxbp-option:disabled:hover { background: transparent; color: var(--ink); }
      .uxbp-option { display: flex; justify-content: space-between; gap: 8px; width: 100%; padding: 8px 10px;
        border: 0; border-radius: 8px; background: transparent; color: var(--ink); font: inherit; font-size: 13px;
        text-align: left; cursor: pointer; }
      .uxbp-option:hover, .uxbp-option[data-on="true"] { background: var(--soft); color: var(--accent); }
      .uxbp-body { flex: 1; min-height: 0; display: grid; grid-template-columns: minmax(0, 1fr) 1px 306px; grid-template-rows: minmax(0, 1fr); gap: 0; }
      .uxbp-left { position: relative; min-width: 0; min-height: 0; display: flex; flex-direction: column; gap: 12px; padding: 0 0 16px 18px; }
      .uxbp-divider { min-width: 0; min-height: 0; background: var(--line); }
      .uxbp-canvas { flex: 1; min-height: 0; overflow: auto; border-radius: var(--radius) 0 0 var(--radius);
        background-color: transparent; background-image: radial-gradient(circle, color-mix(in srgb, var(--line) 65%, transparent) 1px, transparent 1px);
        background-size: 18px 18px; cursor: grab; touch-action: none; user-select: none; }
      .uxbp-canvas[data-drag="true"] { cursor: grabbing; user-select: none; }
      .uxbp-plane { padding: 72px 40px 160px; width: max-content; min-width: 100%; min-height: calc(100% + 96px); }
      .uxbp-group { margin-bottom: 34px; }
      .uxbp-group:last-child { margin-bottom: 0; }
      .uxbp-group h2 { margin: 0 0 12px; color: var(--muted); font-size: 12px; font-weight: 650; letter-spacing: .02em; }
      .uxbp-cards { display: grid; grid-template-columns: repeat(6, var(--uxbp-card-width)); gap: 24px;
        align-items: start; width: calc(6 * var(--uxbp-card-width) + 120px); }
      .uxbp-card { position: relative; width: var(--uxbp-card-width); min-height: 184px; padding: 0; overflow: hidden; display: flex;
        flex-direction: column; border: 0; border-radius: var(--radius); background: var(--card);
        color: var(--ink); text-align: left; box-shadow: var(--shadow); cursor: pointer;
        transform: rotate(var(--rot, 0deg)) translateY(var(--off, 0px));
        transition: transform .5s cubic-bezier(.2, 1.3, .4, 1), box-shadow .3s var(--ease); }
      .uxbp-card:hover, .uxbp-card:focus-visible { transform: rotate(0deg) translateY(-4px) scale(1.025);
        box-shadow: 0 24px 48px -16px rgb(0 0 0 / .28); outline: none; }
      .uxbp-card[data-selected="true"] { transform: rotate(0deg); box-shadow: 0 22px 54px -14px rgb(0 0 0 / .28); }
      .uxbp-card[data-shake="true"] { animation: uxbp-shake .22s ease; }
      .uxbp-art { flex: none; aspect-ratio: 2 / 1; margin: 6px 6px 0; border-radius: 14px; position: relative; overflow: hidden; }
      .uxbp-art svg { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
      .uxbp-art::after { content: ''; position: absolute; inset: 0; background: linear-gradient(180deg, transparent 45%, rgb(255 255 255 / .18)); pointer-events: none; }
      .uxbp-card-body { flex: 1; min-height: 0; padding: 6px 10px 0; display: flex; flex-direction: column; gap: 3px; }
      .uxbp-card-body strong { font-size: 12.5px; line-height: 17px; font-weight: 600; display: -webkit-box;
        -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
      .uxbp-card-body p { margin: 0; color: var(--muted); font-size: 10px; line-height: 15px;
        white-space: normal; overflow-wrap: anywhere; }
      .uxbp-card-foot { margin-top: auto; min-height: 30px; padding: 5px 10px 8px; display: flex; align-items: center; justify-content: space-between; gap: 6px; }
      .uxbp-card-foot code { min-width: 0; color: var(--muted); font-size: 10px; line-height: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      .uxbp-use { flex-shrink: 0; white-space: nowrap; border: .5px solid var(--line); border-radius: 999px; padding: 2px 6px; background: var(--card);
        color: var(--muted); font: inherit; font-size: 10px; font-weight: 600; cursor: pointer; transition: background .18s, color .18s; }
      .uxbp-use:hover { background: var(--soft); color: var(--ink); }
      .uxbp-card:hover .uxbp-use, .uxbp-card[data-selected="true"] .uxbp-use { background: var(--dsw-alias-button-primary-fill, var(--accent));
        border-color: transparent; color: var(--dsw-alias-label-primary-inverted, #fff); }
      @keyframes uxbp-shake { 0%,100% { transform: rotate(0) translateX(0); } 35% { transform: rotate(0) translateX(-2px); }
        70% { transform: rotate(0) translateX(2px); } }
      .uxbp-composer { position: absolute; z-index: 8; left: 50%; transform: translateX(-50%); width: min(520px, calc(100% - 32px));
        bottom: 12px; margin: 0; padding: 6px 8px; border: .5px solid var(--line);
        border-radius: 20px; background: var(--glass); backdrop-filter: blur(24px) saturate(160%);
        box-shadow: 0 12px 34px -10px rgb(0 0 0 / .16); }
      .uxbp-composer:focus-within { border-color: var(--line-strong); }
      .uxbp-composer .uxbp-menu { top: auto; bottom: calc(100% + 6px); }
      .uxbp-input { display: block; width: 100%; min-height: 36px; max-height: 84px; resize: none; padding: 4px 6px;
        border: 0; background: transparent; color: var(--ink); font: inherit; font-size: 12.5px; line-height: 19px; outline: none; }
      .uxbp-tools { display: flex; align-items: center; justify-content: space-between; gap: 6px; flex-wrap: wrap; }
      .uxbp-tools-left, .uxbp-tools-right { display: flex; align-items: center; gap: 4px; min-width: 0; }
      .uxbp-composer .uxbp-btn { min-height: 30px; padding: 0 9px; font-size: 11.5px; border-radius: 9px; }
      .uxbp-composer .uxbp-tools-right .uxbp-primary { padding: 0 12px; }
      .uxbp-chip { position: relative; display: inline-flex; align-items: center; gap: 6px; max-width: 100%; padding: 4px 8px; border-radius: 8px;
        background: var(--soft); color: var(--ink); font-size: 11px; }
      .uxbp-chip span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      .uxbp-chip button { position: absolute; top: -5px; right: -5px; display: grid; place-items: center; width: 14px; height: 14px;
        padding: 0; border: .5px solid var(--line); border-radius: 50%; background: var(--card); color: var(--muted);
        font: 10px/1 var(--sans); cursor: pointer; }
      .uxbp-chip button:hover { background: var(--soft); color: var(--ink); }
      .uxbp-file { display: inline-flex; align-items: center; gap: 4px; padding: 3px 6px; border-radius: 6px; background: var(--soft); font-size: 11px; }
      .uxbp-up { position: relative; overflow: hidden; }
      .uxbp-up input { position: absolute; width: 1px; height: 1px; opacity: 0; }
      .uxbp-error { margin: 0 2px; padding: 8px 10px; border-radius: 10px; color: var(--dsw-alias-state-error-primary, #a52c28);
        background: color-mix(in srgb, var(--dsw-alias-state-error-primary, #a52c28) 9%, var(--card)); font-size: 12px; }
      .uxbp-aside { min-width: 0; min-height: 0; height: 100%; display: flex; flex-direction: column; gap: 10px;
        padding: 14px 18px 16px 16px; }
      .uxbp-panel { min-height: 0; height: 100%; display: flex; flex-direction: column; border: 0; border-radius: 0;
        background: transparent; box-shadow: none; overflow: hidden; }
      .uxbp-panel-head { flex: none; padding: 0 0 12px; border-bottom: .5px solid var(--line); }
      .uxbp-taskline { display: flex; align-items: baseline; justify-content: space-between; gap: 6px; }
      .uxbp-taskline strong { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 14px; font-weight: 600; }
      .uxbp-meta { color: var(--muted); font-size: 11px; font-variant-numeric: tabular-nums; }
      .uxbp-actions { display: flex; gap: 5px; margin-top: 8px; flex-wrap: wrap; }
      .uxbp-actions .uxbp-btn { min-height: 27px; padding: 0 8px; font-size: 11px; border-radius: 8px; }
      .uxbp-subtabs { display: flex; gap: 3px; margin-top: 9px; }
      .uxbp-subtab { height: 28px; border: 0; border-radius: 7px; padding: 0 9px; background: transparent; color: var(--muted);
        font: inherit; font-size: 12px; cursor: pointer; }
      .uxbp-subtab[data-on="true"] { background: var(--soft); color: var(--ink); font-weight: 650; }
      .uxbp-subtab:hover:not([data-on="true"]) { background: var(--soft); color: var(--ink); }
      .uxbp-scroll { flex: 1 1 auto; min-height: 160px; overflow: auto; padding: 10px 0; }
      .uxbp-node { padding: 9px 0; border-bottom: .5px solid color-mix(in srgb, var(--line) 65%, transparent); }
      .uxbp-node:last-child { border-bottom: 0; }
      .uxbp-node-head { display: flex; align-items: baseline; gap: 7px; flex-wrap: wrap; }
      .uxbp-node-head strong { font-size: 12.5px; font-weight: 600; }
      .uxbp-node pre { margin: 7px 0 0; max-height: 260px; overflow: auto; white-space: pre-wrap; overflow-wrap: anywhere;
        font: 11.5px/1.65 ui-monospace, SFMono-Regular, Menlo, monospace; color: var(--ink); }
      .uxbp-msg { padding: 7px 0; font-size: 12.5px; line-height: 20px; white-space: pre-wrap; overflow-wrap: anywhere; }
      .uxbp-msg b { color: var(--muted); font-size: 11px; font-weight: 650; }
      .uxbp-next { flex: 0 0 26%; min-height: 120px; overflow: auto; padding: 12px 0 0; border-top: .5px solid var(--line); }
      .uxbp-next h3 { margin: 0 0 8px; color: var(--muted); font-size: 12px; font-weight: 650; }
      .uxbp-next-main { width: 100%; text-align: left; padding: 11px; border: .5px solid color-mix(in srgb, var(--accent) 40%, var(--line));
        border-radius: 11px; background: color-mix(in srgb, var(--accent) 8%, var(--card)); color: var(--ink);
        font: inherit; cursor: pointer; }
      .uxbp-next-main:hover { background: color-mix(in srgb, var(--accent) 13%, var(--card)); }
      .uxbp-next-main strong { display: block; font-size: 13px; font-weight: 600; }
      .uxbp-next-main span { display: block; margin-top: 4px; color: var(--muted); font-size: 11.5px; line-height: 18px; }
      .uxbp-next-alt { width: 100%; text-align: left; padding: 8px 4px; border: 0; border-bottom: .5px solid var(--line);
        background: transparent; color: var(--ink); font: inherit; font-size: 12px; cursor: pointer; }
      .uxbp-next-alt:hover { background: var(--soft); }
      .uxbp-next-alt span { display: block; color: var(--muted); font-size: 11px; line-height: 17px; }
      .uxbp-empty { margin: 12px 0; color: var(--muted); font-size: 12.5px; line-height: 1.7; }
      .uxbp-sediment { flex: 1; min-height: 0; overflow: auto; padding: 12px 14px; display: grid; gap: 10px; align-content: start; }
      .uxbp-sediment-overlay { position: absolute; z-index: 20; top: 14px; left: 18px; right: 320px; bottom: 16px;
        display: flex; flex-direction: column; padding: 52px 18px 16px; background: var(--bg); overflow: hidden; }
      .uxbp-sediment-head { flex: none; display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: 20px;
        padding: 0 0 18px; border-bottom: .5px solid var(--line); }
      .uxbp-sediment-heading h1 { margin: 0; font-size: 34px; line-height: 1.15; font-weight: 500; letter-spacing: -.02em; }
      .uxbp-sediment-heading p { margin: 6px 0 0; color: var(--muted); font-size: 12.5px; }
      .uxbp-sediment-tools { display: flex; align-items: center; gap: 8px; flex: none; }
      .uxbp-search { display: flex; align-items: center; gap: 7px; width: 280px; height: 38px; padding: 0 11px;
        border: .5px solid var(--line); border-radius: 10px; background: var(--card); color: var(--muted); }
      .uxbp-search:focus-within { border-color: var(--line-strong); }
      .uxbp-search input { width: 100%; min-width: 0; border: 0; outline: 0; background: transparent; color: var(--ink); font: inherit; font-size: 13px; }
      .uxbp-search input::placeholder { color: var(--faint); }
      .uxbp-seg { display: inline-flex; gap: 2px; padding: 3px; border-radius: 10px; background: var(--soft); }
      .uxbp-seg button { height: 30px; padding: 0 12px; border: 0; border-radius: 8px; background: transparent; color: var(--muted);
        font: inherit; font-size: 12px; cursor: pointer; transition: background .18s, color .18s; }
      .uxbp-seg button:hover { color: var(--ink); background: color-mix(in srgb, var(--card) 55%, transparent); }
      .uxbp-seg button[data-on="true"] { background: var(--card); color: var(--ink); box-shadow: var(--shadow); }
      .uxbp-sediment-board { flex: 1; min-height: 0; overflow: auto; padding: 16px 0; display: grid; gap: 14px;
        grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); align-content: start; }
      .uxbp-sediment-card { display: flex; flex-direction: column; gap: 8px; min-height: 150px; padding: 15px;
        border: 0; border-radius: 16px; background: var(--card); box-shadow: var(--shadow); color: var(--ink);
        text-align: left; font: inherit; cursor: pointer; transition: background .18s, box-shadow .18s; }
      .uxbp-sediment-card:hover { background: color-mix(in srgb, var(--soft) 62%, var(--card)); box-shadow: 0 14px 34px -16px rgb(0 0 0 / .24); }
      .uxbp-sediment-card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; }
      .uxbp-sediment-card-head strong { font-size: 14px; line-height: 21px; font-weight: 600; }
      .uxbp-sediment-skills { margin-top: auto; color: var(--muted); font-size: 12px; line-height: 18px; }
      .uxbp-taskcard { display: flex; align-items: center; gap: 12px; padding: 13px 16px; border: 0;
        border-radius: 16px; background: var(--card); box-shadow: var(--shadow); cursor: pointer; text-align: left; }
      .uxbp-taskcard:hover { background: var(--soft); box-shadow: none; }
      .uxbp-taskcard-main { flex: 1; min-width: 0; }
      .uxbp-taskcard-main strong { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 13px; }
      .uxbp-taskcard-main span { display: block; margin-top: 3px; color: var(--muted); font-size: 11px; }
      .uxbp-status { flex: none; padding: 3px 8px; border-radius: 999px; background: var(--soft); color: var(--muted); font-size: 11px; }
      .uxbp-status[data-status="active"] { color: var(--accent); background: color-mix(in srgb, var(--accent) 10%, var(--card)); }
      .uxbp-status[data-status="completed"] { color: #216b51; background: #edf7f1; }
      .uxbp-progress { padding: 10px 0 12px; border-bottom: .5px solid var(--line); }
      .uxbp-progress-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; }
      .uxbp-progress-head strong { font-size: 11px; font-weight: 650; color: var(--muted); }
      .uxbp-progress-track { height: 4px; margin: 7px 0 5px; overflow: hidden; border-radius: 999px; background: var(--soft); }
      .uxbp-progress-fill { height: 100%; border-radius: inherit; background: var(--accent); transition: width .3s var(--ease); }
      .uxbp-progress-meta { color: var(--faint); font-size: 10.5px; }
      @container (max-width: 760px) {
        .uxbp-top { right: 18px; }
        .uxbp-body { grid-template-columns: minmax(0, 1fr); grid-template-rows: minmax(0, 1fr) 1px minmax(0, 42%); padding-top: 74px; }
        .uxbp-left { padding: 0 18px 12px; }
        .uxbp-plane { padding-top: 24px; }
        .uxbp-aside { padding: 12px 18px 16px; }
        .uxbp-sediment-overlay { right: 18px; }
      }
      @container (max-width: 700px) {
        .uxbp-left { --uxbp-card-width: 148px; }
        .uxbp-top { position: relative; top: auto; left: auto; right: auto; margin: 10px 10px 0; }
        .uxbp-body { padding-top: 10px; }
        .uxbp-left { padding-inline: 10px; }
        .uxbp-aside { padding-inline: 10px; }
        .uxbp-left { padding-top: 0; }
        .uxbp-title { display: none; }
        .uxbp-card { min-height: 178px; }
        .uxbp-plane { padding: 16px 20px 120px; }
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

    const skillArt = {
      uxs: {
        background: '#ece9df', ink: '#5c5743',
        scene: () => [
          h('path', { d: 'M26 105c35-13 25-48 67-48s35 35 76 13M93 57c23 0 26-27 64-27', stroke: '#b9b39a', strokeDasharray: '3 4' }),
          h('circle', { cx: 91, cy: 67, r: 38, fill: '#dbd5bf', stroke: 'none' }),
          h('circle', { cx: 86, cy: 61, r: 34, fill: '#fffdf5' }),
          h('path', { d: 'M86 32v7m0 44v7M57 61h7m44 0h7M65 40l5 5m33 33 5 5', stroke: '#b8ae91' }),
          h('path', { d: 'm99 46-8 23-23 8 8-23z', fill: '#8e9268' }),
          h('path', { d: 'm99 46-8 23-15-15z', fill: '#d3d7b5', stroke: 'none' }),
          h('circle', { cx: 28, cy: 105, r: 5, fill: '#8e9268' }),
          h('rect', { x: 146, y: 19, width: 30, height: 22, rx: 4, fill: '#faf8ef' }),
          h('path', { d: 'm154 30 5 4 9-9M149 91h25m-25 6h18' }),
        ],
      },
      stories: {
        background: '#e5eee7', ink: '#385145',
        scene: () => [
          h('path', { d: 'M48 57h22m35 0h20M48 95h22', stroke: '#91b09f' }),
          h('circle', { cx: 35, cy: 45, r: 12, fill: '#fffdf7' }),
          h('circle', { cx: 35, cy: 41, r: 4, fill: '#9cb6a4', stroke: 'none' }),
          h('path', { d: 'M28 52c0-9 14-9 14 0', fill: '#cbded3' }),
          h('rect', { x: 62, y: 30, width: 50, height: 65, rx: 5, fill: '#cbded3', transform: 'rotate(-7 62 30)' }),
          h('rect', { x: 68, y: 35, width: 50, height: 65, rx: 5, fill: '#fffdf7' }),
          h('rect', { x: 75, y: 44, width: 21, height: 8, rx: 3, fill: '#aac5b1', stroke: 'none' }),
          h('path', { d: 'M76 63h31m-31 7h25m-25 12h19' }),
          h('rect', { x: 130, y: 53, width: 47, height: 60, rx: 5, fill: '#f8eee0' }),
          h('path', { d: 'm138 67 3 3 5-6m-8 19 3 3 5-6M151 67h18m-18 16h13M34 88v14m-7-7h14' }),
        ],
      },
      'journey-analysis': {
        background: '#f0e8df', ink: '#67513f',
        scene: () => [
          h('rect', { x: 23, y: 25, width: 154, height: 89, rx: 6, fill: '#fffaf3' }),
          h('path', { d: 'M35 46h130M71 46v57m44-57v57', stroke: '#d8c6b4', strokeDasharray: '3 4' }),
          h('path', { d: 'M36 87c14-26 25-24 38-10s20 17 36-10 32-14 52-26', stroke: '#b77d54', strokeWidth: 2.5 }),
          h('circle', { cx: 39, cy: 82, r: 5, fill: '#e4bf96' }),
          h('circle', { cx: 94, cy: 81, r: 5, fill: '#c8b8a8' }),
          h('circle', { cx: 150, cy: 48, r: 5, fill: '#8f9e78' }),
          h('path', { d: 'M34 35h22m24 0h20m25 0h26M35 102h19m24 0h20m26 0h24', strokeOpacity: .5 }),
          h('rect', { x: 123, y: 90, width: 54, height: 29, rx: 4, fill: '#e7d5bf' }),
          h('path', { d: 'M132 101h34m-34 7h23' }),
        ],
      },
      'solution-swimlane': {
        background: '#eae5e0', ink: '#5f5247',
        scene: () => [
          h('rect', { x: 23, y: 26, width: 153, height: 89, rx: 5, fill: '#fffaf5' }),
          h('path', { d: 'M23 55h153M23 85h153M47 26v89', stroke: '#c8bcb0' }),
          h('circle', { cx: 35, cy: 40, r: 5, fill: '#d6c5b5' }),
          h('circle', { cx: 35, cy: 70, r: 5, fill: '#b8c8bd' }),
          h('circle', { cx: 35, cy: 100, r: 5, fill: '#c7c3d4' }),
          h('path', { d: 'M81 41h26v30h22m14 9v20h-28m-32 0H62', stroke: '#94775c' }),
          h('rect', { x: 57, y: 33, width: 25, height: 16, rx: 3, fill: '#e8cfb3' }),
          h('rect', { x: 129, y: 63, width: 30, height: 16, rx: 3, fill: '#cbded3' }),
          h('rect', { x: 84, y: 92, width: 31, height: 16, rx: 3, fill: '#ddd4e6' }),
          h('path', { d: 'm123 67 5 4-5 4m-3 21-5 4 5 4M63 41h12m62 30h14m-60 29h17' }),
        ],
      },
      edge: {
        background: '#e9ecdf', ink: '#535d43',
        scene: () => [
          h('path', { d: 'M24 43h36q15 0 15 15v30q0 13 16 13h64', stroke: '#9aab86', strokeWidth: 2 }),
          h('path', { d: 'M89 42h68m-6-5 6 5-6 5', stroke: '#b7bda9', strokeDasharray: '3 4' }),
          h('rect', { x: 28, y: 31, width: 32, height: 25, rx: 4, fill: '#fffdf6' }),
          h('rect', { x: 99, y: 20, width: 67, height: 58, rx: 5, fill: '#fffdf6' }),
          h('path', { d: 'm132 30 9 17h-18z', fill: '#e7cea6', stroke: '#8a7654' }),
          h('path', { d: 'M132 36v4m0 3v1M111 56h42m-36 6h28' }),
          h('circle', { cx: 158, cy: 101, r: 13, fill: '#8b9b71' }),
          h('path', { d: 'M153 96a7 7 0 1 1-1 8m0-6v6h6', stroke: '#fffdf6', strokeWidth: 2 }),
          h('path', { d: 'M31 96h23m-23 6h16', strokeOpacity: .5 }),
        ],
      },
      board: {
        background: '#e5ebf3', ink: '#394f69',
        scene: () => [
          h('rect', { x: 32, y: 25, width: 112, height: 87, rx: 5, fill: '#c7d4e5', transform: 'rotate(-5 32 25)', stroke: 'none' }),
          h('rect', { x: 42, y: 22, width: 112, height: 88, rx: 5, fill: '#fffdf8' }),
          h('rect', { x: 51, y: 31, width: 40, height: 45, rx: 3, fill: '#cdd9e7', stroke: 'none' }),
          h('path', { d: 'm51 69 16-18 13 11 11-9v23H51z', fill: '#8ca5bc', stroke: 'none' }),
          h('circle', { cx: 79, cy: 42, r: 5, fill: '#fff7e4', stroke: 'none' }),
          h('path', { d: 'M103 40h38m-38 8h27m-27 13h32m-32 6h18' }),
          h('rect', { x: 54, y: 87, width: 21, height: 13, rx: 2, fill: '#9caf9c', stroke: 'none' }),
          h('rect', { x: 80, y: 87, width: 21, height: 13, rx: 2, fill: '#d5b999', stroke: 'none' }),
          h('rect', { x: 106, y: 87, width: 21, height: 13, rx: 2, fill: '#b6a7c2', stroke: 'none' }),
          h('path', { d: 'm143 80 27 6-8 30-27-6z', fill: '#e4d7c2' }),
          h('path', { d: 'm146 100 9-10 3 13m-11-5 10 3' }),
        ],
      },
      'knowledge-wiki': {
        background: '#eee9dd', ink: '#635a43',
        scene: () => [
          h('rect', { x: 119, y: 28, width: 44, height: 67, rx: 4, fill: '#d9d0b7', transform: 'rotate(8 119 28)' }),
          h('rect', { x: 124, y: 25, width: 40, height: 65, rx: 4, fill: '#fbf7ec' }),
          h('path', { d: 'M132 38h23m-23 7h18' }),
          h('path', { d: 'M28 48q32-12 64 2 32-14 64-2v61q-32-11-64 2-32-13-64-2z', fill: '#fffdf6' }),
          h('path', { d: 'M92 50v61M39 62q21-6 42 1m-42 11q21-6 42 1m-42 11q21-6 31-1M104 63q21-6 40-1m-40 12q21-6 40-1m-40 12q21-6 31-3', stroke: '#a99d7f' }),
          h('path', { d: 'M67 44v25l7-5 7 7V44', fill: '#a5b69a', stroke: 'none' }),
          h('circle', { cx: 156, cy: 103, r: 15, fill: '#b5c1a5' }),
          h('path', { d: 'M150 103h12m-6-6v12' }),
        ],
      },
      'journey-metrics': {
        background: '#e5ecec', ink: '#3d5c60',
        scene: () => [
          h('path', { d: 'M24 44h151M43 44v26m54-26v26m59-26v26', stroke: '#9bb9b9' }),
          ...[43,97,156].map(cx => h('circle', { key: cx, cx, cy: 44, r: 6, fill: '#789f9f' })),
          h('rect', { x: 29, y: 77, width: 141, height: 35, rx: 5, fill: '#fffdf7' }),
          h('path', { d: 'M39 102h118', stroke: '#c4d7d3' }),
          h('path', { d: 'm42 95 19-7 19 4 22-12 20 5 30-16', stroke: '#487b80', strokeWidth: 2 }),
          h('rect', { x: 32, y: 20, width: 24, height: 11, rx: 3, fill: '#c2d7cf', stroke: 'none' }),
          h('rect', { x: 85, y: 20, width: 24, height: 11, rx: 3, fill: '#e1c8ab', stroke: 'none' }),
          h('rect', { x: 144, y: 20, width: 24, height: 11, rx: 3, fill: '#c4cddd', stroke: 'none' }),
          h('circle', { cx: 152, cy: 69, r: 5, fill: '#f7eee0' }),
        ],
      },
      'objective-data-analysis': {
        background: '#e5ebf3', ink: '#394f69',
        scene: () => [
          h('rect', { x: 27, y: 31, width: 107, height: 81, rx: 5, fill: '#cad7e6', stroke: 'none' }),
          h('rect', { x: 22, y: 25, width: 107, height: 81, rx: 5, fill: '#fbfcff' }),
          h('path', { d: 'M22 41h107M33 33h34M35 91h79', stroke: '#9eafc5' }),
          ...[22,40,31,51].map((height, index) => h('rect', { key: index, x: 39 + index * 19, y: 91 - height, width: 11, height, rx: 2, fill: index === 3 ? '#6386b1' : '#becfe3', stroke: 'none' })),
          h('rect', { x: 139, y: 43, width: 37, height: 49, rx: 4, fill: '#f8f1e5' }),
          h('path', { d: 'M145 54h24m-24 9h24m-24 9h24m-24 9h24m-12-29v31', stroke: '#b3a58d' }),
          h('path', { d: 'M142 103h30m-30 6h21', strokeOpacity: .5 }),
        ],
      },
      'subjective-feedback-analysis': {
        background: '#eee7ef', ink: '#5a4968',
        scene: () => [
          h('path', { d: 'M70 54h24q10 0 10 14v21m32-30h-22q-10 0-10 30', stroke: '#af9bb8', strokeDasharray: '3 4' }),
          h('path', { d: 'M25 27h57v35H56l-12 10v-10H25z', fill: '#fffaf7' }),
          h('path', { d: 'M118 30h55v36h-11v9l-13-9h-31z', fill: '#dfd1e9' }),
          h('path', { d: 'M35 39h34m-34 9h22m72-5h33m-33 9h22' }),
          h('rect', { x: 62, y: 85, width: 85, height: 30, rx: 5, fill: '#fffaf7' }),
          h('circle', { cx: 76, cy: 100, r: 6, fill: '#b7c8b5', stroke: 'none' }),
          h('circle', { cx: 96, cy: 100, r: 6, fill: '#e4c3a3', stroke: 'none' }),
          h('circle', { cx: 116, cy: 100, r: 6, fill: '#b8a3cb', stroke: 'none' }),
          h('path', { d: 'M131 96v8m-4-4h8' }),
        ],
      },
      'experience-heuristic-analysis': {
        background: '#ece9df', ink: '#5c5743',
        scene: () => [
          h('rect', { x: 26, y: 27, width: 102, height: 79, rx: 5, fill: '#fffdf6' }),
          h('path', { d: 'M26 43h102M36 35h18M37 54h29m-29 9h21', strokeOpacity: .55 }),
          h('rect', { x: 37, y: 75, width: 45, height: 20, rx: 3, fill: '#d3d9c4', stroke: 'none' }),
          h('circle', { cx: 123, cy: 68, r: 27, fill: '#f7f5ec', fillOpacity: .95, strokeWidth: 2 }),
          h('path', { d: 'm143 88 24 24', stroke: '#8b9273', strokeWidth: 9 }),
          h('path', { d: 'm143 88 24 24', strokeWidth: 1.4 }),
          h('rect', { x: 109, y: 59, width: 27, height: 17, rx: 3, fill: '#ecd1ad' }),
          h('path', { d: 'M123 63v5m0 4v1M37 114h46', strokeOpacity: .6 }),
        ],
      },
      'evidence-govern': {
        background: '#e5eee7', ink: '#385145',
        scene: () => [
          h('rect', { x: 28, y: 29, width: 56, height: 70, rx: 4, fill: '#c8dbcf', transform: 'rotate(-8 28 29)' }),
          h('rect', { x: 37, y: 32, width: 56, height: 70, rx: 4, fill: '#fffdf7' }),
          h('path', { d: 'M47 45h34m-34 8h23M47 67h34m-34 8h23m-23 14h20', strokeOpacity: .65 }),
          h('path', { d: 'M97 68h18m-5-4 5 4-5 4', stroke: '#8daa96' }),
          h('path', { d: 'm144 37 29 10v25q0 23-29 34-29-11-29-34V47z', fill: '#d0e2d5' }),
          h('path', { d: 'm144 44 22 8v20q0 17-22 27-22-10-22-27V52z', stroke: '#8baa94' }),
          h('path', { d: 'm132 70 8 8 16-20', stroke: '#427761', strokeWidth: 3 }),
          h('rect', { x: 43, y: 109, width: 44, height: 7, rx: 3, fill: '#e2c8a7', stroke: 'none' }),
        ],
      },
      'root-cause-synthesis': {
        background: '#eee7ef', ink: '#5a4968',
        scene: () => [
          h('path', { d: 'M40 41h31l28 32m59-32h-31L99 73m-59 1h59m59 0H99m0 0v24', stroke: '#ab95b8', strokeWidth: 2 }),
          ...[[25,28],[144,28],[21,61],[148,61]].map(([x,y], index) => h('rect', { key: index, x, y, width: 30, height: 24, rx: 4, fill: index % 2 ? '#dfd1e9' : '#fffaf6' })),
          h('circle', { cx: 99, cy: 73, r: 15, fill: '#fffaf6', stroke: '#8c72a4', strokeWidth: 2 }),
          h('circle', { cx: 99, cy: 73, r: 5, fill: '#a58ab9', stroke: 'none' }),
          h('rect', { x: 72, y: 101, width: 54, height: 18, rx: 4, fill: '#d4c2e1' }),
          h('path', { d: 'M83 110h31M33 39h14m105 0h14M29 73h14m113 0h14' }),
          h('path', { d: 'M51 117h10m76 0h13', strokeOpacity: .4 }),
        ],
      },
      'business-impact': {
        background: '#f0e8df', ink: '#67513f',
        scene: () => [
          h('rect', { x: 28, y: 28, width: 118, height: 80, rx: 5, fill: '#fffaf3' }),
          h('path', { d: 'M41 94h92M41 43v51', stroke: '#bba58c' }),
          h('rect', { x: 52, y: 75, width: 15, height: 19, rx: 2, fill: '#dccaaf', stroke: 'none' }),
          h('rect', { x: 78, y: 62, width: 15, height: 32, rx: 2, fill: '#c6b18e', stroke: 'none' }),
          h('rect', { x: 104, y: 49, width: 15, height: 45, rx: 2, fill: '#b38d66', stroke: 'none' }),
          h('path', { d: 'm51 67 28-17 24 1 21-15m-8 0h8v8', stroke: '#92704d', strokeWidth: 2 }),
          h('circle', { cx: 151, cy: 93, r: 21, fill: '#d8c29a' }),
          h('circle', { cx: 151, cy: 93, r: 14, stroke: '#f8efdc' }),
          h('path', { d: 'm147 86 4 6 4-6m-4 6v9m-5-7h10m-10 4h10' }),
          h('path', { d: 'M40 117h78', strokeOpacity: .4 }),
        ],
      },
      'outcome-validation-recheck': {
        background: '#e5ecec', ink: '#3d5c60',
        scene: () => [
          h('rect', { x: 24, y: 37, width: 63, height: 65, rx: 5, fill: '#fffdf7' }),
          h('rect', { x: 114, y: 37, width: 63, height: 65, rx: 5, fill: '#f7faf6' }),
          h('path', { d: 'M34 49h31m-31 7h20m90-7h20m-40 7h31', strokeOpacity: .55 }),
          h('path', { d: 'm34 87 12-7 12 4 18-12', stroke: '#b7a58a', strokeWidth: 2 }),
          h('path', { d: 'm124 87 12-10 12 2 18-15', stroke: '#5b8d80', strokeWidth: 2 }),
          h('path', { d: 'M88 66h21m-5-4 5 4-5 4' }),
          h('path', { d: 'M53 29c26-21 58-21 88-2m-7-9 7 9-11 1', stroke: '#9bb9b4' }),
          h('circle', { cx: 148, cy: 105, r: 14, fill: '#6f9a88' }),
          h('path', { d: 'm141 105 5 5 9-11', stroke: '#fffdf7', strokeWidth: 2 }),
        ],
      },
      'evidence-archive': {
        background: '#ece9df', ink: '#5c5743',
        scene: () => [
          h('rect', { x: 51, y: 22, width: 49, height: 65, rx: 4, fill: '#d5c7b1', transform: 'rotate(-10 51 22)' }),
          h('rect', { x: 72, y: 19, width: 49, height: 64, rx: 4, fill: '#fffdf6' }),
          h('path', { d: 'M81 32h28m-28 8h21m-21 8h26', strokeOpacity: .6 }),
          h('path', { d: 'M41 71h111v44H41z', fill: '#c8d0b4' }),
          h('rect', { x: 35, y: 63, width: 123, height: 14, rx: 4, fill: '#e2e5d5' }),
          h('rect', { x: 75, y: 85, width: 43, height: 17, rx: 3, fill: '#fffdf6' }),
          h('path', { d: 'M84 94h25M162 37v19m-5-5 5 5 5-5' }),
          h('path', { d: 'M26 121h147', strokeOpacity: .3 }),
        ],
      },
      'data-visualization': {
        background: '#e5ebf3', ink: '#394f69',
        scene: () => [
          h('rect', { x: 25, y: 25, width: 150, height: 90, rx: 5, fill: '#fbfcff' }),
          h('path', { d: 'M25 40h150M36 32h29', stroke: '#a7b8cd' }),
          h('circle', { cx: 64, cy: 76, r: 24, fill: '#d5dfed', stroke: 'none' }),
          h('path', { d: 'M64 52a24 24 0 0 1 24 24H64z', fill: '#7593b8', stroke: 'none' }),
          h('circle', { cx: 64, cy: 76, r: 12, fill: '#fbfcff', stroke: 'none' }),
          h('rect', { x: 105, y: 53, width: 52, height: 7, rx: 3, fill: '#c0cddf', stroke: 'none' }),
          h('rect', { x: 105, y: 66, width: 36, height: 7, rx: 3, fill: '#d9c6ab', stroke: 'none' }),
          h('path', { d: 'M105 101h54M105 88l13 7 14-13 13 3 13-10', stroke: '#7392b7', strokeWidth: 2 }),
          h('path', { d: 'M44 106h15m10 0h15', stroke: '#a7b8cd' }),
        ],
      },
      'prd-review': {
        background: '#e5eee7',
        ink: '#385145',
        scene: () => [
          h('path', { d: 'M16 101H182M33 108H165M49 115H151', stroke: '#c5d6cc' }),
          h('rect', { x: 54, y: 29, width: 74, height: 87, rx: 5, fill: '#cbded3', transform: 'rotate(-12 54 29)' }),
          h('rect', { x: 69, y: 21, width: 75, height: 90, rx: 5, fill: '#f8fbf5', transform: 'rotate(7 69 21)' }),
          h('rect', { x: 57, y: 27, width: 77, height: 89, rx: 5, fill: '#fffdf7' }),
          h('path', { d: 'M69 41H107M69 47H92M84 62h35M84 78h27M84 94h31', strokeOpacity: .55 }),
          h('rect', { x: 66, y: 69, width: 59, height: 16, rx: 3, fill: '#e5eee3', stroke: 'none' }),
          h('path', { d: 'M70 62l2 2 5-5m-7 19 2 2 5-5m-8 22h7v-7h-7zM84 78h27', stroke: '#427761' }),
          h('path', { d: 'M143 53h18v24l-5-4h-13z', fill: '#f3d9aa' }),
          h('path', { d: 'M148 60h8m-8 5h5' }),
          h('circle', { cx: 144, cy: 102, r: 15, fill: '#427761', stroke: '#e5eee7', strokeWidth: 3 }),
          h('path', { d: 'm137 102 5 5 8-9', stroke: '#fffdf7', strokeWidth: 2.5 }),
        ],
      },
      'problem-framing': {
        background: '#eee7ef',
        ink: '#5a4968',
        scene: () => [
          h('path', { d: 'M24 23h151M24 117h151', stroke: '#d6c9dd', strokeDasharray: '2 5' }),
          h('path', { d: 'M60 45c30 0 19 25 43 25M62 69h41M61 94c29 0 16-24 42-24', stroke: '#9c88ad' }),
          h('rect', { x: 24, y: 32, width: 35, height: 23, rx: 4, fill: '#f9e2d6', transform: 'rotate(-8 24 32)' }),
          h('rect', { x: 22, y: 58, width: 40, height: 22, rx: 4, fill: '#fffaf5' }),
          h('rect', { x: 28, y: 85, width: 34, height: 22, rx: 4, fill: '#ded3ea', transform: 'rotate(6 28 85)' }),
          h('path', { d: 'M33 39l14-2m-12 7 9-1m-12 22h12m-12 6h21m-15 24 14 2' }),
          h('path', { d: 'm95 65 6 5-6 5' }),
          h('rect', { x: 115, y: 38, width: 63, height: 69, rx: 6, fill: '#d6c9df', stroke: 'none' }),
          h('rect', { x: 109, y: 33, width: 64, height: 69, rx: 6, fill: '#fdf9fb' }),
          h('path', { d: 'M109 49h64', strokeOpacity: .55 }),
          h('rect', { x: 121, y: 58, width: 40, height: 11, rx: 3, fill: '#a28cb4', stroke: 'none' }),
          h('path', { d: 'M141 69v8m-13 6v-6h26v6' }),
          h('rect', { x: 120, y: 82, width: 16, height: 10, rx: 2, fill: '#e7dbea' }),
          h('rect', { x: 146, y: 82, width: 16, height: 10, rx: 2, fill: '#f6e3d8' }),
        ],
      },
      'page-spec': {
        background: '#e5ebf3',
        ink: '#394f69',
        scene: () => [
          h('path', { d: 'M25 31v82m-4-76h8m-8 69h8M37 121h96m-93-4v8m89-8v8', stroke: '#8298b5' }),
          h('rect', { x: 44, y: 34, width: 112, height: 76, rx: 6, fill: '#c7d4e5', stroke: 'none' }),
          h('rect', { x: 38, y: 28, width: 112, height: 76, rx: 6, fill: '#fbfcff' }),
          h('path', { d: 'M38 42h112M66 42v62', strokeOpacity: .6 }),
          h('path', { d: 'M46 35h1m5 0h1m5 0h1m-13 19h12m-12 9h9m-9 9h10m18-19h29' }),
          h('rect', { x: 74, y: 62, width: 60, height: 30, rx: 3, fill: '#e9eff7', stroke: '#7892b4', strokeDasharray: '3 3' }),
          h('path', { d: 'M112 67l16-13m-16 36 16 7', stroke: '#6f8bad' }),
          h('rect', { x: 126, y: 51, width: 56, height: 49, rx: 6, fill: '#fffdf8', stroke: '#5275a8', strokeWidth: 2 }),
          h('rect', { x: 133, y: 58, width: 42, height: 14, rx: 3, fill: '#d3e0f2', stroke: 'none' }),
          h('path', { d: 'M134 79h29m-29 5h20', strokeOpacity: .7 }),
          h('rect', { x: 154, y: 88, width: 19, height: 6, rx: 2, fill: '#5275a8', stroke: 'none' }),
        ],
      },
    }

    function SkillArt({ skillId }) {
      const art = Object.hasOwn(skillArt, skillId) ? skillArt[skillId] : skillArt.uxs
      return h('svg', {
        viewBox: '0 0 200 140',
        'aria-hidden': true,
        preserveAspectRatio: 'xMidYMid meet',
        style: { background: art.background },
      },
        h('rect', { width: 200, height: 140, fill: art.background }),
        h('g', { fill: 'none', stroke: art.ink, strokeWidth: 1.4, strokeLinecap: 'round', strokeLinejoin: 'round' },
          ...art.scene()),
      )
    }

    function groupOf(item) {
      if (item.displayGroup === 'foundation') return 3
      if (item.phase === 1) return 0
      if (item.phase === 2) return 1
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
      const [search, setSearch] = useState('')
      const [filter, setFilter] = useState('all')
      const [openMenu, setOpenMenu] = useState('')
      const [menuWorkspace, setMenuWorkspace] = useState('')
      const [menuSessions, setMenuSessions] = useState([])
      const [menuLoading, setMenuLoading] = useState(false)
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

      const nameOf = value => catalog.find(item => item.id === (value === 'uxb' ? 'uxs' : value))?.name ?? value
      const taskId = task?.id ?? ''
      const statusLabel = status => status === 'active' ? t('active') : status === 'paused' ? t('paused') : t('completed')
      const segmentKey = JSON.stringify(task?.segments ?? [])
      const groups = [
        { label: '探索与定义', items: catalog.filter(item => groupOf(item) === 0) },
        { label: '设计与交付', items: catalog.filter(item => groupOf(item) === 1) },
        { label: '分析与证据', items: catalog.filter(item => groupOf(item) === 2) },
        { label: '基础能力', items: catalog.filter(item => groupOf(item) === 3) },
      ]
      const filteredTasks = tasks.filter(item => {
        if (filter !== 'all' && item.status !== filter) return false
        const query = search.trim().toLowerCase()
        return !query || item.title.toLowerCase().includes(query) || item.id.toLowerCase().includes(query)
      })
      const counts = {
        all: tasks.length,
        active: tasks.filter(item => item.status === 'active').length,
        paused: tasks.filter(item => item.status === 'paused').length,
        completed: tasks.filter(item => item.status === 'completed').length,
      }
      const sedimentStats = [
        counts.all ? t('total') + ' ' + counts.all + ' ' + t('items') : '',
        counts.active ? counts.active + ' ' + t('active') : '',
        counts.paused ? counts.paused + ' ' + t('paused') : '',
        counts.completed ? counts.completed + ' ' + t('completed') : '',
      ].filter(Boolean)

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

      useEffect(() => {
        if (openMenu !== 'workspace' || !menuWorkspace) return
        let disposed = false
        setMenuLoading(true)
        api({ workspace: menuWorkspace }).then(data => {
          if (disposed) return
          setMenuSessions(data.sessions ?? [])
          setMenuLoading(false)
        }).catch(() => {
          if (!disposed) { setMenuSessions([]); setMenuLoading(false) }
        })
        return () => { disposed = true }
      }, [openMenu, menuWorkspace])

      function openWorkspaceMenu() {
        if (openMenu === 'workspace') { setOpenMenu(''); return }
        const target = workspace || workspaces[0]?.id || ''
        setMenuWorkspace(target)
        setMenuSessions(target === workspace ? conversations : [])
        setOpenMenu('workspace')
      }

      function previewWorkspace(id) {
        setMenuWorkspace(id)
        if (id === workspace) setMenuSessions(conversations)
      }

      function chooseSession(wsId, sid) {
        if (!wsId) return
        if (task && (wsId !== workspace || sid !== task.sessionId)) return
        setOpenMenu('')
        if (wsId !== workspace) {
          setWorkspace(wsId)
          setTask(null); setManifest(null); setNext([]); setTasks([]); setConversations([])
          setSessionId(sid || '')
          save({ workspace: wsId, sessionId: sid || '', activeTaskId: '' })
        } else {
          setSessionId(sid || '')
          save({ workspace, sessionId: sid || '', activeTaskId: task?.id ?? '' })
        }
      }

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
          if (!canvas.hasPointerCapture(event.pointerId)) canvas.setPointerCapture(event.pointerId)
          event.preventDefault()
          canvas.scrollLeft = drag.current.left - dx
          canvas.scrollTop = drag.current.top - dy
        }
      }

      function onPointerUp(event) {
        if (!drag.current.down) return
        drag.current.down = false
        const canvas = canvasRef.current
        if (canvas) {
          delete canvas.dataset.drag
          if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId)
        }
      }

      function cardClick(item) {
        if (drag.current.moved) return
        shakeCard(item.id)
        useSkill(item.id)
        setArt({})
      }

      const sessionTitle = conversations.find(item => item.id === sessionId)?.title ?? (sessionId ? t('session') : t('newSession'))
      const status = task ? statusLabel(task.status) : ''
      const outputCount = Object.keys(manifest?.skills ?? {}).length
      const progress = !task ? 0 : task.status === 'completed' ? 100 : task.status === 'paused' ? 50 : outputCount ? 78 : flow.length ? 48 : 22

      return h('main', { className: 'uxbp-root' },
        h('style', null, styles),
        h('header', { className: 'uxbp-top' },
          h('div', { className: 'uxbp-brand' },
            h('div', { className: 'uxbp-tabs', role: 'group' },
              h('button', { type: 'button', className: 'uxbp-tab', 'data-on': tab === 'task', onClick: () => setTab('task') }, t('task')),
              h('button', { type: 'button', className: 'uxbp-tab', 'data-on': tab === 'sediment', onClick: () => setTab('sediment') }, t('sediment')))),
          h('div', { className: 'uxbp-right-top' },
            h('div', { className: 'uxbp-picker' },
              h('button', { type: 'button', className: 'uxbp-btn', 'aria-expanded': openMenu === 'workspace', title: sessionTitle, onClick: openWorkspaceMenu },
                h(Icon, { path: 'M3 7V5a1 1 0 0 1 1-1h5l2 3h9a1 1 0 0 1 1 1v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z M3 9h18' }),
                h('span', null, workspaces.find(item => item.id === workspace)?.title ?? t('workspace')),
                h(Icon, { path: 'm7 10 5 5 5-5' })),
              openMenu === 'workspace' && h('div', { className: 'uxbp-menu uxbp-wsmenu' },
                h('div', { className: 'uxbp-wspane' },
                  h('div', { className: 'uxbp-menu-title' }, t('workspace')),
                  ...workspaces.map(item => h('button', {
                    key: item.id, type: 'button', className: 'uxbp-option', 'data-on': item.id === menuWorkspace,
                    onMouseEnter: () => previewWorkspace(item.id),
                    onClick: () => previewWorkspace(item.id),
                  }, item.title))),
                h('div', { className: 'uxbp-sessionpane' },
                  h('div', { className: 'uxbp-menu-title' }, t('session')),
                  h('button', {
                    type: 'button', className: 'uxbp-option uxbp-new-session', disabled: Boolean(task),
                    onClick: () => chooseSession(menuWorkspace, ''),
                  }, '+ ' + t('newSession')),
                  menuLoading && h('p', { className: 'uxbp-empty' }, '…'),
                  !menuLoading && menuSessions.length === 0 && h('p', { className: 'uxbp-empty' }, t('noSessions')),
                  ...menuSessions.map(item => h('button', {
                    key: item.id, type: 'button', className: 'uxbp-option',
                    'data-on': menuWorkspace === workspace && item.id === sessionId,
                    disabled: Boolean(task) && (menuWorkspace !== workspace || item.id !== task.sessionId),
                    onClick: () => chooseSession(menuWorkspace, item.id),
                  }, item.title))))),
            h('button', { type: 'button', className: 'uxbp-btn uxbp-icon', title: t('reset'), 'aria-label': t('reset'), onClick: resetAll },
              h(Icon, { path: 'M20 12a8 8 0 1 1-2.3-5.7M20 4v6h-6' })))),

        error && h('p', { className: 'uxbp-error', role: 'alert' }, error),

        h('div', { className: 'uxbp-body' },
            h('section', { className: 'uxbp-left' },
              h('div', {
                ref: canvasRef, className: 'uxbp-canvas',
                onPointerDown, onPointerMove, onPointerUp, onPointerCancel: onPointerUp,
                onClickCapture: event => {
                  if (!drag.current.moved) return
                  drag.current.moved = false
                  event.preventDefault()
                  event.stopPropagation()
                },
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
                      'data-selected': skill === item.id,
                      onClick: () => cardClick(item),
                      onFocus: () => shakeCard(item.id),
                      onDoubleClick: () => useSkill(item.id),
                    },
                    h('span', { className: 'uxbp-art' }, h(SkillArt, { skillId: item.id })),
                    h('span', { className: 'uxbp-card-body' },
                      h('strong', null, item.name),
                      h('p', null, item.description)),
                    h('span', { className: 'uxbp-card-foot' },
                      h('code', null, '/' + item.id),
                      h('span', { className: 'uxbp-use', role: 'button', tabIndex: 0, onClick: event => { event.stopPropagation(); shakeCard(item.id); useSkill(item.id) } }, t('useSkill'))))
                  }))))),
              h('div', { className: 'uxbp-composer' },
                files.length > 0 && h('div', { style: { display: 'flex', gap: 4, flexWrap: 'wrap', padding: '2px 4px' } },
                  ...files.map((file, index) => h('span', { key: index, className: 'uxbp-file' }, file.name,
                    h('button', { type: 'button', 'aria-label': t('remove'), onClick: () => setFiles(items => items.filter((_, i) => i !== index)) }, '×')))),
                skill && h('div', { style: { padding: '2px 4px 0' } },
                  h('span', { className: 'uxbp-chip' },
                    h('span', null, t('skill') + ': ' + nameOf(skill)),
                    h('button', { type: 'button', 'aria-label': t('remove'), title: t('remove'), onClick: () => setSkill('') }, '×'))),
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
                    h('label', { className: 'uxbp-btn uxbp-up', title: t('attach'), 'aria-label': t('attach') },
                      h('input', { type: 'file', multiple: true, onChange: event => {
                        const picked = Array.from(event.currentTarget.files ?? [])
                        setFiles(items => [...items, ...picked])
                        event.currentTarget.value = ''
                      } }),
                      h(Icon, { path: 'M20 11 11 20a5 5 0 0 1-7-7l9-9a3.5 3.5 0 0 1 5 5l-9 9a2 2 0 0 1-3-3l8-8' }),
                      h('span', null, t('attach')))),
                  h('div', { className: 'uxbp-tools-right' },
                    running && h('button', { type: 'button', className: 'uxbp-btn', onClick: () => binding.current?.session.cancel() }, t('stop')),
                    h('button', { type: 'button', className: 'uxbp-btn', disabled: !sessionId, onClick: () => sessionId && uiWorkspace.openSession(sessionId) }, t('enter')),
                    h('button', { type: 'button', className: 'uxbp-btn uxbp-primary', disabled: sending || !skill || (!text.trim() && !files.length), onClick: () => void execute() }, t('execute'))))))
            ),
            h('div', { className: 'uxbp-divider', 'aria-hidden': true }),
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
                        h('button', { className: 'uxbp-btn', onClick: () => void newTask() }, t('newTask'))),
                      h('div', { className: 'uxbp-progress' },
                        h('div', { className: 'uxbp-progress-head' },
                          h('strong', null, t('progress'))),
                        h('div', { className: 'uxbp-progress-track' },
                          h('div', { className: 'uxbp-progress-fill', style: { width: progress + '%' } })),
                        h('div', { className: 'uxbp-progress-meta' },
                          (task.skills?.length ?? 0) + ' Skill · ' + outputCount + ' ' + t('outputs'))))
                    : h('div', null,
                      h('div', { className: 'uxbp-taskline' },
                        h('strong', null, t('task')),
                        h('span', { className: 'uxbp-status' }, t('idle'))))),
                !task && h('div', { className: 'uxbp-progress' },
                  h('div', { className: 'uxbp-progress-track' },
                    h('div', { className: 'uxbp-progress-fill', style: { width: '0%' } }))),
                h('div', { className: 'uxbp-subtabs' },
                  h('button', { className: 'uxbp-subtab', 'data-on': rightTab === 'dynamics', onClick: () => setRightTab('dynamics') }, t('dynamics')),
                  h('button', { className: 'uxbp-subtab', 'data-on': rightTab === 'dialogue', onClick: () => setRightTab('dialogue') }, t('dialogue'))),
                h('div', { className: 'uxbp-scroll' },
                  task && rightTab === 'dynamics' && (flow.length
                    ? flow.map((node, index) => h('div', { key: index, className: 'uxbp-node' },
                      h('div', { className: 'uxbp-node-head' },
                        h('span', { 'aria-hidden': true, style: { color: node.status === 'failed' ? 'var(--dsw-alias-state-error-primary, #a52c28)' : 'var(--muted)' } }, node.status === 'running' ? '●' : node.status === 'failed' ? '✕' : '✓'),
                        h('strong', null, node.label),
                        node.detail && h('span', { className: 'uxbp-meta' }, node.detail)),
                      node.markdown && node.latest && h('pre', null, node.markdown),
                      node.text && h('div', { className: 'uxbp-msg' }, node.text)))
                    : null),
                  task && rightTab === 'dialogue' && (dialogue.length
                    ? dialogue.map((row, index) => h('div', { key: index, className: 'uxbp-msg' },
                        h('b', null, row.role === 'user' ? '你' : 'AI'), ' ', row.text))
                    : h('p', { className: 'uxbp-empty' }, t('noDialogue'))))),
                h('div', { className: 'uxbp-next' },
                  h('h3', null, t('next')),
                  task && next.length === 0 && h('p', { className: 'uxbp-empty' }, t('noNext')),
                  ...(task ? next.slice(0, 3) : []).map((item, index) => index === 0
                    ? h('button', { key: item.id, className: 'uxbp-next-main', onClick: () => useSkill(item.id) },
                        h('strong', null, item.name), h('span', null, item.reason))
                    : h('button', { key: item.id, className: 'uxbp-next-alt', onClick: () => useSkill(item.id) },
                        item.name, h('span', null, item.reason)))),
                art.content && h('div', { className: 'uxbp-next' },
                  h('h3', null, nameOf(art.skill)),
                  h('pre', { style: { maxHeight: 180, overflow: 'auto', whiteSpace: 'pre-wrap', fontSize: 11 } }, art.content))))
          , tab === 'sediment' && h('section', { className: 'uxbp-sediment-overlay' },
            h('div', { className: 'uxbp-sediment-head' },
              h('div', { className: 'uxbp-sediment-heading' },
                h('h1', null, t('sediment')),
                sedimentStats.length > 0 && h('p', null, sedimentStats.join(' · '))),
              h('div', { className: 'uxbp-sediment-tools' },
                h('label', { className: 'uxbp-search' },
                  h(Icon, { path: 'M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm10 2-4.4-4.4' }),
                  h('input', { placeholder: t('searchTasks'), value: search, onChange: event => setSearch(event.target.value) })),
                h('div', { className: 'uxbp-seg' },
                  ...['all', 'active', 'paused', 'completed'].map(item => h('button', {
                    key: item, type: 'button', 'data-on': filter === item, onClick: () => setFilter(item),
                  }, item === 'all' ? t('all') : statusLabel(item)))))),
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
