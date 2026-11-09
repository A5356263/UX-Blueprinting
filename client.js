window.__ModuleLoader__.load({
  id: 'dsh-ux-blueprinting',
  factory(require) {
    const { createElement: h, useEffect, useState, useSyncExternalStore } = require('react')

    const id = 'ux-blueprinting'
    const endpoint = '/api/ux-blueprinting/workbench'

    const en = {
      title: 'Design workbench',
      intro: 'Run any design or analysis skill on a workspace, then continue from the plugin-computed next steps.',
      workspace: 'Workspace',
      workspacePlaceholder: 'Select a workspace registered in Harness',
      tasks: 'Tasks',
      newTask: 'New task',
      taskName: 'Task name',
      taskNamePlaceholder: 'For example: Expense review',
      material: 'Requirement file',
      materialPlaceholder: 'For example: input/requirements.md',
      materialHint: 'Only a Markdown or plain-text file inside the workspace can be bound.',
      create: 'Create task',
      materialPath: 'Requirement file: ',
      replyLegend: 'Reply to each blocking question',
      emptyTasks: 'No task in this workspace yet.',
      artifacts: 'Registered artifacts',
      emptyArtifacts: 'No artifact has been registered yet.',
      preview: 'Preview',
      startPrefix: 'Start · ',
      state: {
        ready: 'Ready', running: 'Running', waiting: 'Waiting for product replies',
        cancelling: 'Cancelling', cancelled: 'Cancelled', failed: 'Failed', interrupted: 'Interrupted',
      },
      command: { reply: 'Submit replies', cancel: 'Cancel run', retry: 'Retry this stage' },
    }

    const zh = {
      title: '设计工作台',
      intro: '在选定工作区运行任意设计或分析 Skill，下一步由插件计算。',
      workspace: '工作区',
      workspacePlaceholder: '选择 Harness 中已有的工作区',
      tasks: '任务',
      newTask: '新建任务',
      taskName: '任务名',
      taskNamePlaceholder: '例如：费用报销审查',
      material: '需求文件',
      materialPlaceholder: '例如：input/需求.md',
      materialHint: '只支持工作区内你明确指定的 Markdown 或纯文本文件。',
      create: '创建任务',
      materialPath: '需求材料：',
      replyLegend: '请逐项回复阻断问题',
      emptyTasks: '当前工作区还没有任务。',
      artifacts: '已登记产物',
      emptyArtifacts: '当前还没有登记产物。',
      preview: '预览',
      startPrefix: '开始 · ',
      state: {
        ready: '就绪', running: '执行中', waiting: '待产品确认',
        cancelling: '正在取消', cancelled: '已取消', failed: '执行失败', interrupted: '执行中断',
      },
      command: { reply: '提交回复', cancel: '取消执行', retry: '重试本阶段' },
    }

    const ui = {
      page: {
        height: '100%', overflow: 'auto', boxSizing: 'border-box',
        padding: '24px clamp(20px, 4vw, 56px)',
        color: 'var(--dsw-alias-label-primary)', background: 'var(--dsw-alias-bg-base)',
      },
      title: { margin: 0, fontSize: 20, fontWeight: 600 },
      intro: { margin: '6px 0 20px', color: 'var(--dsw-alias-label-secondary)', fontSize: 13 },
      muted: { color: 'var(--dsw-alias-label-secondary)', fontSize: 13 },
      error: { color: 'var(--dsw-alias-state-error-primary)' },
      label: { display: 'block', fontSize: 13, color: 'var(--dsw-alias-label-secondary)' },
      field: {
        display: 'block', width: '100%', boxSizing: 'border-box', margin: '6px 0 14px',
        padding: '8px 10px', borderRadius: 8, font: 'inherit', fontSize: 13,
        border: '1px solid var(--dsw-alias-border-l1)',
        background: 'var(--dsw-alias-bg-layer-2)', color: 'var(--dsw-alias-label-primary)',
      },
      columns: {
        display: 'grid', gridTemplateColumns: 'minmax(180px, 1fr) minmax(0, 3fr)',
        gap: 20, marginTop: 16, alignItems: 'start',
      },
      card: {
        border: '1px solid var(--dsw-alias-border-l1)', background: 'var(--dsw-alias-bg-layer-1)',
        borderRadius: 10, padding: 16,
      },
      sectionTitle: { margin: '0 0 8px', fontSize: 14, fontWeight: 600 },
      list: { listStyle: 'none', margin: 0, padding: 0, display: 'grid', gap: 4 },
      artifactList: { listStyle: 'none', margin: '8px 0 0', padding: 0, display: 'grid', gap: 6 },
      row: { display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center', marginTop: 10 },
      pre: {
        whiteSpace: 'pre-wrap', overflowWrap: 'anywhere', marginTop: 12,
        background: 'var(--dsw-alias-bg-layer-2)', border: '1px solid var(--dsw-alias-border-l1)',
        borderRadius: 8, padding: 12, fontSize: 12.5, lineHeight: 1.55,
      },
    }

    function button(active) {
      return {
        font: 'inherit', fontSize: 13, padding: '6px 12px', borderRadius: 8, cursor: 'pointer',
        background: active ? 'var(--dsw-alias-bg-layer-2)' : 'transparent',
        border: '1px solid ' + (active ? 'var(--dsw-alias-brand-primary)' : 'var(--dsw-alias-border-l1)'),
        color: 'var(--dsw-alias-label-primary)',
      }
    }

    function PanelIcon() {
      return h('svg', {
        viewBox: '0 0 24 24', width: 18, height: 18, 'aria-hidden': true, style: { display: 'block' },
      },
      h('path', {
        d: 'M12 2.5 21.5 12 12 21.5 2.5 12Z', fill: 'none',
        stroke: 'currentColor', strokeWidth: 1.7, strokeLinejoin: 'round',
      }),
      h('circle', { cx: 12, cy: 12, r: 2.1, fill: 'currentColor' }))
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

    function Workbench({ translate: t, locale }) {
      const subscribe = callback => locale.subscribe(callback)
      const snapshot = () => locale.getSnapshot()
      useSyncExternalStore(subscribe, snapshot, snapshot)

      const [workspaces, setWorkspaces] = useState([])
      const [catalog, setCatalog] = useState([])
      const [workspace, setWorkspace] = useState('')
      const [tasks, setTasks] = useState([])
      const [selected, setSelected] = useState('')
      const [taskName, setTaskName] = useState('')
      const [path, setPath] = useState('')
      const [answers, setAnswers] = useState({})
      const [artifact, setArtifact] = useState(null)
      const [error, setError] = useState('')
      const [busy, setBusy] = useState(false)

      useEffect(() => {
        const controller = new AbortController()
        api(null, null, controller.signal).then(({ workspaces, catalog }) => {
          setWorkspaces(workspaces)
          setCatalog(catalog ?? [])
          if (workspaces.length === 1) setWorkspace(workspaces[0].id)
        }).catch(e => { if (!controller.signal.aborted) setError(e.message) })
        return () => controller.abort()
      }, [])

      useEffect(() => {
        if (!workspace) return
        const controller = new AbortController()
        let timer
        let disposed = false
        function schedule() {
          if (!disposed) timer = setTimeout(refresh, 2000)
        }
        async function refresh() {
          if (document.visibilityState === 'hidden') { schedule(); return }
          try {
            const result = await api({ workspace }, null, controller.signal)
            if (!controller.signal.aborted) setTasks(result.tasks)
          } catch (e) {
            if (!controller.signal.aborted) setError(e.message)
          } finally {
            schedule()
          }
        }
        void refresh()
        return () => { disposed = true; controller.abort(); clearTimeout(timer) }
      }, [workspace])

      const task = tasks.find(item => item.id === selected)
      const skillName = value => (catalog.find(item => item.id === value)?.name ?? value)

      function select(value) {
        setSelected(value)
        setAnswers({})
        setArtifact(null)
      }
      function changeWorkspace(value) {
        setWorkspace(value)
        setTasks([])
        select('')
        setPath('')
        setTaskName('')
        setError('')
      }
      async function mutate(body) {
        setBusy(true)
        setError('')
        try {
          const { task: updated } = await api(null, { ...body, workspaceId: workspace })
          setTasks(current => [updated, ...current.filter(item => item.id !== updated.id)])
          select(updated.id)
        } catch (e) { setError(e.message) } finally { setBusy(false) }
      }
      function act(action) {
        const replies = action === 'reply'
          ? Object.fromEntries(Object.entries(answers).filter(([, value]) => value.trim()))
          : undefined
        void mutate({ action, taskId: task.id, revision: task.revision, operationId: crypto.randomUUID(), replies })
      }
      function label(action) {
        if (action.startsWith('start:')) return t('startPrefix') + skillName(action.slice(6))
        return t('command.' + action)
      }
      async function preview(kind) {
        setError('')
        try {
          setArtifact({ ...(await api({ workspace, task: task.id, artifact: kind })), kind, taskId: task.id })
        } catch (e) { setError(e.message) }
      }
      function openPreview(kind) {
        const url = endpoint + '?' + new URLSearchParams({ workspace, task: task.id, artifact: kind, preview: '1' })
        window.open(url, '_blank', 'noopener')
      }

      return h('main', { style: ui.page },
        h('h1', { style: ui.title }, t('title')),
        h('p', { style: ui.intro }, t('intro')),
        h('label', { style: ui.label }, t('workspace'),
          h('select', {
            style: ui.field, value: workspace, disabled: busy,
            onChange: e => changeWorkspace(e.target.value),
          },
          h('option', { value: '' }, t('workspacePlaceholder')),
          ...workspaces.map(w => h('option', { key: w.id, value: w.id }, w.title + ' · ' + w.path)))),
        error && h('p', { role: 'alert', style: ui.error }, error),
        workspace && h('div', { style: ui.columns },
          h('aside', { style: ui.card },
            h('h2', { style: ui.sectionTitle }, t('tasks')),
            h('button', { type: 'button', style: button(!task), disabled: busy, onClick: () => select('') }, t('newTask')),
            tasks.length
              ? h('ul', { style: { ...ui.list, marginTop: 8 } }, tasks.map(item => h('li', { key: item.id },
                h('button', {
                  type: 'button', disabled: busy, 'aria-pressed': item.id === selected,
                  style: { ...button(item.id === selected), width: '100%', textAlign: 'left' },
                  onClick: () => select(item.id),
                }, item.title + ' · ' + t('state.' + item.state)))))
              : h('p', { style: { ...ui.muted, marginTop: 8 } }, t('emptyTasks'))),
          task ? h('section', { style: ui.card, 'aria-label': t('tasks') },
            h('h2', { style: { ...ui.sectionTitle, marginBottom: 4 } }, task.title),
            h('p', { role: 'status', style: { ...ui.muted, margin: '0 0 10px' } },
              t('state.' + task.state) + (task.execution ? ' · ' + skillName(task.execution.skill) : '')),
            h('p', { style: { ...ui.muted, margin: '0 0 10px' } }, t('materialPath') + task.input.path),
            task.error && h('p', { role: 'alert', style: ui.error }, task.error),
            task.state === 'waiting' && h('fieldset', { style: { border: '1px solid var(--dsw-alias-border-l1)', borderRadius: 8, padding: 12, margin: '0 0 10px' } },
              h('legend', { style: ui.label }, t('replyLegend')),
              ...task.questions.map(q => h('label', { key: q.id, style: { display: 'block', fontSize: 13 } },
                q.id + ' · ' + q.text,
                h('textarea', {
                  style: ui.field, rows: 3, maxLength: 8000, value: answers[q.id] ?? '',
                  onChange: e => setAnswers(current => ({ ...current, [q.id]: e.target.value })),
                })))),
            h('div', { style: ui.row }, ...task.actions.map(action => h('button', {
              key: action, type: 'button', style: button(action === task.actions[0]), disabled: busy ||
                (action === 'reply' && !Object.values(answers).some(value => value.trim())),
              onClick: () => act(action),
            }, label(action)))),
            h('h3', { style: { ...ui.sectionTitle, marginTop: 18 } }, t('artifacts')),
            Object.keys(task.artifacts).length
              ? h('ul', { style: ui.artifactList }, Object.entries(task.artifacts).map(([kind, item]) =>
                h('li', { key: kind },
                  h('div', { style: { display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' } },
                    h('button', { type: 'button', style: button(false), onClick: () => void preview(kind) }, skillName(kind)),
                    h('button', { type: 'button', style: button(false), onClick: () => openPreview(kind) }, t('preview'))),
                  h('p', { style: { ...ui.muted, margin: '4px 0 0' } }, item.path))))
              : h('p', { style: ui.muted }, t('emptyArtifacts')),
            artifact?.taskId === task.id && h('pre', { style: ui.pre }, artifact.content))
          : h('form', {
            style: ui.card,
            onSubmit: e => { e.preventDefault(); void mutate({ action: 'create', title: taskName, path }) },
          },
          h('h2', { style: ui.sectionTitle }, t('newTask')),
          h('label', { style: ui.label }, t('taskName'),
            h('input', {
              style: ui.field, required: true, maxLength: 200, value: taskName,
              placeholder: t('taskNamePlaceholder'),
              onChange: e => setTaskName(e.target.value),
            })),
          h('label', { style: ui.label }, t('material'),
            h('input', {
              style: ui.field, required: true, value: path,
              placeholder: t('materialPlaceholder'),
              onChange: e => setPath(e.target.value),
            })),
          h('p', { style: { ...ui.muted, marginTop: 0 } }, t('materialHint')),
          h('button', { type: 'submit', style: button(true), disabled: busy }, t('create')))))
    }

    return {
      inject: ['slots', 'locale'],
      apply(ctx) {
        const disposers = [
          ctx.locale.register('ux-blueprinting', 'en', en),
          ctx.locale.register('ux-blueprinting', 'zh', zh),
        ]
        ctx.effect(() => () => { for (const dispose of disposers) dispose() })
        const t = ctx.locale.bind('ux-blueprinting')
        ctx.slots.inject('sidebar.panellist', () =>
          ctx.slots.register({ name: 'sidebar.panellist', id, order: 20, label: () => t('title') }, PanelIcon))
        ctx.slots.inject('main', () =>
          ctx.slots.register({ name: 'main', key: id }, () => h(Workbench, { translate: t, locale: ctx.locale })))
      },
    }
  },
})
