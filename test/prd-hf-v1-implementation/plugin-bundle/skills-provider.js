import { readdirSync, readFileSync, existsSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = fileURLToPath(new URL('.', import.meta.url))
const skillRoot = join(root, '.agents', 'skills')
const provider = 'ux-blueprinting'

export function readBundledSkills() {
  return readdirSync(skillRoot, { withFileTypes: true })
    .filter(entry => entry.isDirectory() && existsSync(join(skillRoot, entry.name, 'SKILL.md')))
    .map(entry => {
      const dir = join(skillRoot, entry.name)
      const path = join(dir, 'SKILL.md')
      const text = readFileSync(path, 'utf8').replace(/\r\n/g, '\n')
      const [, header, body] = text.match(/^\uFEFF?---\n([\s\S]*?)\n---\n([\s\S]*)$/) ?? []
      const name = header?.match(/^name:[ \t]*(\S+)[ \t]*$/m)?.[1]
      const description = header?.match(/^description:[ \t]*([^\n]*)(\n(?:[ \t]+[^\n]*(?:\n|$))*)?/m)
      if (name !== entry.name || !description) throw new Error('Skill 清单无效：' + entry.name)
      const summary = /^[>|][-+]?$/.test(description[1].trim())
        ? description[2]?.trim().replace(/\n[ \t]*/g, ' ')
        : description[1].trim()
      if (!summary) throw new Error('Skill 缺少描述：' + name)
      return {
        body,
        candidate: {
          name, description: summary, path, provider, source: 'bundled', rank: 600,
          locator: name, invocation: { modelInvocable: true, userInvocable: true },
          resourceBase: { kind: 'directory', path: dir },
        },
        content: body + '\n\n## Harness 插件环境\n\nSkill 资源根：' + dir +
          '\n插件资源根：' + root +
          '\n随包资料只从上述绝对路径读取；用户工作区里的同名目录不属于随包资料。用户输入和 spark-output/ 位于用户选定的工作区。\n' +
          '\n## 工作台任务输出约定\n\n' +
          '当任务消息包含【设计工作台任务 <taskId>】时：\n' +
          '- 任务目录为 spark-output/design-workbench/<taskId>/；\n' +
          '- 禁止直接写 spark-output/ 根目录；正式产物只能通过 submit_design_artifact 登记；\n' +
          '- 需要读取上游时，优先读取任务目录中的同名产物；不要读取根目录副本；\n' +
          '- PRD 审核记录文件名为 prd-review-record.md，正式需求基线为 prd-review.md；\n' +
          '- 确实需要辅助文件时，只写任务目录，不创建根目录副本。\n',
      }
    })
}

export function createSkillProvider(entries) {
  const active = new Map(entries.map(entry => [entry.candidate.name, entry]))
  return {
    name: provider,
    async list() { return [...active.values()].map(entry => entry.candidate) },
    async get(candidate) {
      const entry = active.get(candidate.name)
      if (!entry || candidate.locator !== candidate.name) return undefined
      const { rank, locator, ...summary } = entry.candidate
      return { ...summary, content: entry.content }
    },
  }
}
