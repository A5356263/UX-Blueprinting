import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(fileURLToPath(new URL('..', import.meta.url)))
const manifestPath = join(root, 'package.json')
const outDir = join(root, 'out')
const args = new Set(process.argv.slice(2))

if (args.has('--help') || args.has('-h')) {
  console.log('Usage: npm run pack:plugin [-- --patch|--minor|--major|--no-bump]')
  console.log('Default: patch version bump, then npm pack into ./out')
  process.exit(0)
}

const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'))
const original = { ...manifest }
const bump = args.has('--major') ? 'major' : args.has('--minor') ? 'minor' : args.has('--no-bump') ? null : 'patch'

if (bump) {
  const match = String(manifest.version).match(/^(\d+)\.(\d+)\.(\d+)/)
  if (!match) throw new Error('package.json version 不是可递增的 semver: ' + manifest.version)
  let [, major, minor, patch] = match.map(Number)
  if (bump === 'major') { major += 1; minor = 0; patch = 0 }
  else if (bump === 'minor') { minor += 1; patch = 0 }
  else patch += 1
  manifest.version = `${major}.${minor}.${patch}`
  writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + '\n')
}

mkdirSync(outDir, { recursive: true })
const result = spawnSync('npm', ['pack', '--pack-destination', outDir], {
  cwd: root,
  shell: true,
  encoding: 'utf8',
})

if (result.status !== 0) {
  writeFileSync(manifestPath, JSON.stringify(original, null, 2) + '\n')
  process.stderr.write(result.stderr || 'npm pack 失败\n')
  process.exit(result.status || 1)
}

const tgz = join(outDir, `${manifest.name}-${manifest.version}.tgz`)
if (!existsSync(tgz)) {
  writeFileSync(manifestPath, JSON.stringify(original, null, 2) + '\n')
  throw new Error('npm pack 成功但没有找到预期产物: ' + tgz)
}

process.stdout.write((result.stdout || '') + (result.stderr || ''))
console.log('\nPacked: ' + tgz)
console.log('Version: ' + manifest.version)
