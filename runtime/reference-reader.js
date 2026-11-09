import { readFileSync, realpathSync, statSync } from 'node:fs'
import { isAbsolute, relative, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

export const name = 'ux-blueprinting-reference-reader'
export const inject = ['tools']

const root = fileURLToPath(new URL('../.agents/skills/', import.meta.url))
const allowed = ['prd-review/references', 'page-spec/references', 'uxb/references', 'journey-analysis/references', 'knowledge-wiki/knowledge']
const inside = (dir, file) => {
  const path = relative(dir, file)
  return Boolean(path && path !== '..' && !path.startsWith('..' + sep) && !isAbsolute(path))
}

export function apply(ctx) {
  const roots = allowed.map(dir => realpathSync(resolve(root, dir)))
  ctx.tools.register({
    name: 'read_design_reference',
    description: '读取插件内的专业参考资料。使用 .agents/skills/ 内的相对路径，可用 offset 继续阅读。',
    parameters: { type: 'object', properties: { path: { type: 'string' }, offset: { type: 'integer', minimum: 1 } },
      required: ['path'], additionalProperties: false },
    output: {
      schema: { type: 'object', properties: { content: { type: 'string' }, nextOffset: { type: 'integer' } },
        required: ['content', 'nextOffset'], additionalProperties: false },
      render: (_, value) => [{ type: 'text', text: value.content + (value.nextOffset ? '\n下一段 offset：' + value.nextOffset : '') }],
    },
    async execute(args) {
      if (typeof args.path !== 'string' || !/\.(md|txt|json)$/i.test(args.path)) throw new Error('请选择随包的文本参考资料')
      const offset = args.offset ?? 1
      if (!Number.isSafeInteger(offset) || offset < 1) throw new Error('起始行无效')
      let file
      try { file = realpathSync(resolve(root, args.path.replace(/^\.agents[\\/]skills[\\/]/, ''))) }
      catch { throw new Error('未找到随包参考资料') }
      if (!roots.some(dir => inside(dir, file))) throw new Error('只允许读取设计参考资料和正式知识')
      const info = statSync(file)
      if (!info.isFile() || info.size > 1_000_000) throw new Error('参考资料不是受支持的文本文件')
      const lines = readFileSync(file, 'utf8').split(/\r?\n/)
      const end = Math.min(lines.length, offset - 1 + 120)
      return { content: lines.slice(offset - 1, end).join('\n'), nextOffset: end < lines.length ? end + 1 : 0 }
    },
  })
}
