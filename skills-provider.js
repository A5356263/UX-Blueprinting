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
        blocked: body.includes('shared-workflow/data-analysis/'),
        content: body + '\n\n## Harness 插件环境\n\nSkill 资源根：' + dir +
          '\n插件资源根：' + root +
          '\n请从插件资源根读取 .agents/skills/ 和 shared-workflow/ 下的随包资料。运行随包脚本时使用其绝对路径，工作目录保留为用户选定的工作区。用户输入和 spark-output/ 不在插件安装目录。\n',
      }
    })
}

export function createSkillProvider(entries) {
  const active = new Map(entries.filter(entry => !entry.blocked).map(entry => [entry.candidate.name, entry]))
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
