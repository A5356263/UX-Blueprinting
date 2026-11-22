import { createSkillProvider, readBundledSkills } from './skills-provider.js'
import { createWorkbench } from './runtime/workbench.js'
import { nameOf, readsOf, recommendNext, skillCatalog } from './runtime/orchestration.js'
import * as referenceReader from './runtime/reference-reader.js'

export const name = 'ux-blueprinting'
export const inject = ['connection', 'skills', 'tools', 'workspaceRegistry', 'sessionController', 'sessions']

export function apply(ctx) {
  const entries = readBundledSkills()
  ctx.effect(() => ctx.skills.registerProvider(() => createSkillProvider(entries)))
  ctx.plugin(referenceReader)
  const catalog = {
    list: () => skillCatalog(),
    name: id => nameOf(id),
    reads: id => readsOf(id),
    recommend: (completed, current) => recommendNext(completed, current),
  }
  const workbench = createWorkbench(ctx, catalog)
  ctx.effect(() => ctx.tools.register({
    name: 'submit_design_artifact',
    description: '登记本轮完成的 Markdown 产物。模型完成产物后调用；插件按任务和 Skill 记录当前产物。prd-review 的审核记录和正式基线都使用 skill=prd-review，插件按 Markdown 类型分别保存。',
    parameters: {
      type: 'object',
      properties: {
        taskId: { type: 'string', description: '任务 ID，来自本轮任务指令' },
        skill: { type: 'string', description: '本轮 Skill id' },
        markdown: { type: 'string', description: '完整 Markdown 产物' },
        title: { type: 'string', description: '当前产物的名称，可省略' },
      },
      required: ['taskId', 'skill', 'markdown'],
      additionalProperties: false,
    },
    output: {
      schema: {
        type: 'object',
        properties: {
          registered: { type: 'boolean' },
          taskId: { type: 'string' },
          skill: { type: 'string' },
          artifactKind: { type: 'string' },
          reviewStatus: { type: 'string' },
          path: { type: 'string' },
          stale: { type: 'array', items: { type: 'string' } },
          next: { type: 'array', items: { type: 'object', additionalProperties: true } },
        },
        required: ['registered', 'taskId', 'skill', 'path', 'next'],
        additionalProperties: false,
      },
      render: (_, value) => [{
        type: 'text',
        text: '已登记任务 ' + value.taskId + ' 的 ' + value.skill + ' 产物：' + value.path +
          (value.reviewStatus ? '（' + value.reviewStatus + '）' : '') +
          (value.stale?.length ? '；下游可能过期：' + value.stale.join('、') : ''),
      }],
    },
    execute(args, exec) {
      return workbench.submit(args, exec?.agent?.id)
    },
  }))
  ctx.effect(() => ctx.tools.register({
    name: 'design_next_steps',
    description: '查询设计工作流的下一步建议。传入已完成的 Skill id 与当前 Skill，返回推荐、可执行清单和目录。',
    parameters: {
      type: 'object',
      properties: {
        completed: { type: 'array', items: { type: 'string' } },
        current: { type: 'string' },
      },
      additionalProperties: false,
    },
    output: {
      schema: {
        type: 'object',
        properties: {
          recommended: { type: 'array', items: { type: 'object', additionalProperties: true } },
          available: { type: 'array', items: { type: 'object', additionalProperties: true } },
          catalog: { type: 'array', items: { type: 'object', additionalProperties: true } },
        },
        required: ['recommended', 'available', 'catalog'],
        additionalProperties: false,
      },
      render: (_, value) => [{
        type: 'text',
        text: value.recommended.length
          ? value.recommended.map(item => '· ' + item.name + '（' + item.id + '）' + (item.reason ? '：' + item.reason : '')).join('\n')
          : '当前没有可推荐的下一步。',
      }],
    },
    execute(args) {
      const result = recommendNext(args?.completed ?? [], args?.current)
      return { ...result, catalog: skillCatalog() }
    },
  }))
  ctx.effect(() => {
    const unregister = ctx.connection.fetch.register({
      path: '/api/ux-blueprinting/workbench', methods: ['GET', 'POST'],
      requestBody: 'buffered', fetch: workbench.fetch,
    })
    return async () => { workbench.dispose(); await unregister() }
  })
}
