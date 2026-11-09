import { createSkillProvider, readBundledSkills } from './skills-provider.js'
import { createWorkbench } from './runtime/workbench.js'
import { createStageRunner } from './runtime/runner.js'
import { recommendNext, skillCatalog, readsOf, nameOf } from './runtime/orchestration.js'

export const name = 'ux-blueprinting'
export const inject = ['connection', 'skills', 'tools', 'workspaceRegistry', 'sessionController', 'agents']

export function apply(ctx) {
  const entries = readBundledSkills()
  ctx.effect(() => ctx.skills.registerProvider(() => createSkillProvider(entries)))
  ctx.effect(() => ctx.tools.register({
    name: 'design_next_steps',
    description: '查询设计工作流的下一步建议。传入已完成的 Skill id，返回推荐继续的 Skill、原因和当前可执行的 Skill 清单。流程推进由插件计算，不要凭 Skill 正文猜测。',
    parameters: {
      type: 'object',
      properties: { completed: { type: 'array', items: { type: 'string' }, description: '已完成的 Skill id，例如 prd-review、uxb、page-spec' } },
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
      const result = recommendNext(args?.completed ?? [])
      return { ...result, catalog: skillCatalog() }
    },
  }))
  const catalog = {
    list: () => skillCatalog(),
    available: completed => recommendNext(completed).available.map(item => item.id),
    reads: id => readsOf(id),
    name: id => nameOf(id),
  }
  const stages = createStageRunner(ctx, entries)
  const workbench = createWorkbench(ctx.workspaceRegistry, stages.run, stages.cancel, catalog)
  ctx.effect(() => {
    const unregister = ctx.connection.fetch.register({
      path: '/api/ux-blueprinting/workbench', methods: ['GET', 'POST'],
      requestBody: 'buffered', fetch: workbench.fetch,
    })
    return async () => { workbench.dispose(); stages.dispose(); await unregister() }
  })
}
