import { spawnSync } from 'node:child_process'
import { cpSync, existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs'
import { basename, dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { randomUUID } from 'node:crypto'

// npm omits two workspace dotfiles. Restore their exact bytes into the task's Skill copy.
const runtime = dirname(fileURLToPath(import.meta.url))
const source = join(runtime, '../.agents/skills/ux-proto-g')
const output = process.argv[2] && resolve(process.argv[2])
if (process.argv.length !== 3 || !output || basename(output) !== 'ux-proto-g' ||
    basename(dirname(dirname(output))) !== 'design-workbench') {
  throw new Error('需要传入当前设计任务下的 ux-proto-g 原型目录')
}
const receipt = readFileSync(join(source, 'distribution-receipt.json'))
const key = JSON.parse(receipt).contentDigest.match(/^sha256:([0-9a-f]{64})$/)?.[1]
if (!key) throw new Error('原型 Skill 发行回执无效')
const installed = join(dirname(output), '.ux-proto-g-' + key)
if (!existsSync(installed)) {
  const staging = installed + '-' + randomUUID()
  mkdirSync(staging)
  cpSync(source, staging, { recursive: true })
  const dotfiles = JSON.parse(readFileSync(join(runtime, 'ux-proto-g-dotfiles.json'), 'utf8'))
  for (const name of ['.gitignore', '.npmrc']) {
    writeFileSync(join(staging, 'assets/workspace-template', name), Buffer.from(dotfiles[name], 'base64'))
  }
  renameSync(staging, installed)
}
const result = spawnSync(process.execPath, [
  join(installed, 'bin/ux-proto-g-bootstrap.mjs'), '--output', output, '--json',
], { stdio: 'inherit' })
if (result.error) throw result.error
process.exitCode = result.status ?? 1
