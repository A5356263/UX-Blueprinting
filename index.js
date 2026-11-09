import { createSkillProvider, readBundledSkills } from './skills-provider.js'
import { createWorkbench } from './runtime/workbench.js'
import { stageRunner } from './runtime/runner.js'

export const name = 'ux-blueprinting'
export const inject = ['connection', 'skills', 'workspaceRegistry', 'sessionController', 'agents']

export function apply(ctx) {
  const entries = readBundledSkills()
  ctx.effect(() => ctx.skills.registerProvider(() => createSkillProvider(entries)))
  const workbench = createWorkbench(ctx.workspaceRegistry, stageRunner(ctx, entries))
  ctx.effect(() => {
    const unregister = ctx.connection.fetch.register({
      path: '/api/ux-blueprinting/workbench', methods: ['GET', 'POST'],
      requestBody: 'buffered', fetch: workbench.fetch,
    })
    return async () => { workbench.dispose(); await unregister() }
  })
}
