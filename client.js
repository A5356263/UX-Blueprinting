window.__ModuleLoader__.load({
  id: 'dsh-ux-blueprinting',
  factory(require) {
    const { createElement: h, useEffect, useState } = require('react')
    const id = 'ux-blueprinting'
    const title = '设计工作台'
    const endpoint = '/api/ux-blueprinting/workbench'
    const labels = { draft: '待开始', running: '执行中', waiting: '待产品确认', ready: '基线就绪',
      'journey-review': '待查看用户旅程', 'uxb-review': '待确认体验策略', completed: '已完成', cancelling: '正在取消', cancelled: '已取消', failed: '执行失败', interrupted: '执行中断' }
    const commands = { 'start-review': '审查需求', reply: '提交回复', 'start-page': '生成页面规格',
      'start-uxb': '补充体验策略（可选）', 'confirm-uxb': '确认并采用本版策略', 'discard-uxb': '跳过体验策略',
      'start-journey': '分析用户旅程（可选）', 'confirm-journey': '确认并采用本版旅程', 'discard-journey': '跳过用户旅程',
      cancel: '取消执行', retry: '重试本阶段' }
    const stageNames = { 'prd-review': '需求审查', uxb: '体验策略', 'journey-analysis': '用户旅程', 'page-spec': '页面设计' }
    const artifactNames = { baseline: '正式需求基线', uxbDraft: '待确认体验策略稿', uxb: '已确认体验策略', journeyDraft: '本轮用户旅程', journey: '已采用用户旅程', pageSpec: '页面规格' }
    const field = { display: 'block', width: '100%', boxSizing: 'border-box', margin: '6px 0 16px', padding: 8 }
    async function api(query, body, signal) {
      const response = await fetch(endpoint + (query ? '?' + new URLSearchParams(query) : ''), body ? {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal,
      } : { signal })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || '工作台请求失败')
      return data
    }

    function Workbench() {
      const [workspaces, setWorkspaces] = useState([])
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
        api(null, null, controller.signal).then(({ workspaces }) => {
          setWorkspaces(workspaces)
          if (workspaces.length === 1) setWorkspace(workspaces[0].id)
        }).catch(e => { if (!controller.signal.aborted) setError(e.message) })
        return () => controller.abort()
      }, [])
      useEffect(() => {
        if (!workspace) return
        const controller = new AbortController()
        let timer
        async function refresh() {
          try {
            const result = await api({ workspace }, null, controller.signal)
            if (!controller.signal.aborted) setTasks(result.tasks)
          } catch (e) {
            if (!controller.signal.aborted) setError(e.message)
          } finally {
            if (!controller.signal.aborted) timer = setTimeout(refresh, 1600)
          }
        }
        void refresh()
        return () => { controller.abort(); clearTimeout(timer) }
      }, [workspace])
      const task = tasks.find(item => item.id === selected)
      function select(value) {
        setSelected(value)
        setAnswers({})
        setArtifact(null)
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
        const replies = action === 'reply' ? Object.fromEntries(Object.entries(answers).filter(([, value]) => value.trim())) : undefined
        void mutate({ action, taskId: task.id, revision: task.revision, operationId: crypto.randomUUID(), replies })
      }
      async function preview(kind) {
        setError('')
        try { setArtifact({ ...(await api({ workspace, task: task.id, artifact: kind })), kind, taskId: task.id }) }
        catch (e) { setError(e.message) }
      }
      return h('main', { style: { padding: '28px clamp(20px, 5vw, 64px)', overflow: 'auto', height: '100%', boxSizing: 'border-box' } },
        h('h1', null, title),
        h('p', null, '审查需求、确认阻断问题，再使用本轮基线生成页面规格。'),
        h('label', null, '工作区', h('select', { style: field, value: workspace, disabled: busy, onChange: e => {
          setWorkspace(e.target.value); setTasks([]); select(''); setPath(''); setTaskName(''); setError('')
        } }, h('option', { value: '' }, '选择 Harness 中已有的工作区'),
        ...workspaces.map(w => h('option', { key: w.id, value: w.id }, w.title + ' · ' + w.path)))),
        error && h('p', { role: 'alert' }, error),
        workspace && h('div', { style: { display: 'grid', gridTemplateColumns: 'minmax(180px, 1fr) minmax(0, 3fr)', gap: 24 } },
          h('aside', null, h('h2', null, '任务'),
            h('button', { type: 'button', disabled: busy, onClick: () => select('') }, '新建任务'),
            h('ul', null, tasks.map(t => h('li', { key: t.id },
              h('button', { type: 'button', disabled: busy, 'aria-pressed': t.id === selected, onClick: () => select(t.id) }, t.title + ' · ' + labels[t.state]))))),
          task ? h('section', { 'aria-label': '任务详情' },
            h('h2', null, task.title),
            h('p', { role: 'status' }, labels[task.state] + (task.execution ? ' · ' + stageNames[task.execution.stage] : '')),
            h('ol', { 'aria-label': '阶段进度' },
              h('li', { 'aria-current': !task.artifacts.baseline ? 'step' : undefined }, '需求审查' + (task.artifacts.baseline ? ' · 已完成' : '')),
              h('li', { 'aria-current': task.artifacts.baseline && !task.artifacts.pageSpec ? 'step' : undefined },
                '页面设计' + (task.artifacts.pageSpec ? ' · 已完成' : !task.artifacts.baseline ? ' · 等待正式基线' : ''))),
            h('p', null, '需求材料：' + task.input.path),
            task.error && h('p', { role: 'alert' }, task.error),
            task.state === 'waiting' && h('fieldset', null, h('legend', null, '请逐项回复阻断问题'),
              ...task.questions.map(q => h('label', { key: q.id }, q.id + ' · ' + q.text,
                h('textarea', { style: field, rows: 3, maxLength: 8000, value: answers[q.id] ?? '',
                  onChange: e => setAnswers(current => ({ ...current, [q.id]: e.target.value })) })))),
            task.state === 'uxb-review' && h('p', null, '查看本版策略稿后，可确认采用或跳过。'),
            task.state === 'journey-review' && h('p', null, task.artifacts.journeyDraft?.complete ? '查看本版旅程后，可确认采用或跳过。' : '当前结果为旅程骨架，查看缺口后可跳过。'),
            ...task.actions.map(action => h('button', { key: action, type: 'button',
              disabled: busy || (action === 'reply' && !Object.values(answers).some(value => value.trim())) ||
                (action === 'confirm-uxb' && (artifact?.taskId !== task.id || artifact.kind !== 'uxbDraft')) ||
                (action === 'confirm-journey' && (artifact?.taskId !== task.id || artifact.kind !== 'journeyDraft')),
              onClick: () => act(action) }, commands[action])),
            h('h3', null, '正式产物'),
            Object.keys(task.artifacts).length ? h('ul', null, Object.entries(task.artifacts).map(([kind, item]) =>
              h('li', { key: kind }, h('button', { type: 'button', onClick: () => void preview(kind) }, '查看' + artifactNames[kind]),
                h('p', null, item.path)))) : h('p', null, '当前还没有登记产物。'),
            artifact?.taskId === task.id && h('pre', { style: { whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' } }, artifact.content)
          ) : h('form', { onSubmit: e => { e.preventDefault(); void mutate({ action: 'create', title: taskName, path }) } },
            h('h2', null, '新建任务'),
            h('label', null, '任务名', h('input', { style: field, required: true, maxLength: 200, value: taskName, onChange: e => setTaskName(e.target.value) })),
            h('label', null, '需求文件路径', h('input', { style: field, required: true, placeholder: '例如 input/需求.md', value: path, onChange: e => setPath(e.target.value) })),
            h('p', null, '支持工作区内你明确指定的 Markdown 或纯文本文件。'),
            h('button', { type: 'submit', disabled: busy }, '创建任务'))))
    }

    return {
      isPlugin: true,
      inject: ['slots'],
      apply(ctx) {
        ctx.slots.inject('sidebar.panellist', () =>
          ctx.slots.register({ name: 'sidebar.panellist', id, label: () => title }, () =>
            h('span', { 'aria-hidden': true }, '◇')))
        ctx.slots.inject('main', () =>
          ctx.slots.register({ name: 'main', key: id }, Workbench))
      },
    }
  },
})
