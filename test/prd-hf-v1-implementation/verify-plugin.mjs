import assert from 'node:assert/strict'
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createWorkbench } from './plugin-bundle/runtime/workbench.js'
import { nameOf, readsOf, skillCatalog } from './plugin-bundle/runtime/orchestration.js'

const here = fileURLToPath(new URL('./', import.meta.url))
const app = mkdtempSync(join(here, 'plugin-runtime-'))
const sessionId = 'fixture-session-0001'
const taskId = 'T-hf-v1-smoke'
const ws = { id: 'fixture-workspace', title: 'Fixture', path: app, sessionIds: [sessionId] }
const workbenchDir = join(app, 'spark-output', 'design-workbench')
const taskDir = join(workbenchDir, taskId)
mkdirSync(taskDir, { recursive: true })
writeFileSync(join(workbenchDir, 'tasks.json'), JSON.stringify({
  version: 1, next: 2,
  tasks: [{ id: taskId, title: '测试正式基线交接', sessionId, status: 'active', skills: [] }],
}))
const bridge = { workspaceRegistry: { list: () => [ws] } }
const host = createWorkbench(bridge, { list: skillCatalog, name: nameOf, reads: readsOf })
const inputs = join(here, 'only-plugin')
const baseline = readFileSync(join(inputs, 'prd-review.md'), 'utf8')
const page = readFileSync(join(inputs, 'page-spec.md'), 'utf8')
const send = (skill, markdown) => host.submit({ taskId, skill, markdown }, sessionId)
const review = [
  '# PRD 审核记录', '', '- 状态：waiting_response', '',
  '## 需求初识', '', '门禁回归样本。', '', '## 审核结论', '',
  '### 待产品确认', '', '- Q-001：需明确是否在本期启用。', '',
  '## 你还需要补充什么吗？', '',
].join('\n')
await assert.rejects(() => send('prd-review', review.replace('waiting_response','invalid')), /新版格式/)
await assert.rejects(() => send('prd-review', baseline.replace(/formal/, 'draft')), /formal 标记/)
await assert.rejects(() => send('prd-review', baseline.replace(/## §4[^\r\n]+/, '## §4 非法标题')), /formal 标记/)
await assert.rejects(() => send('page-spec', page.replace('## 3. 跨实体任务流程','## 3. 非法标题')), /页面规格缺少/)
const recorded = await send('prd-review', review)
assert.equal(recorded.artifactKind, 'review-record')
assert.equal(recorded.reviewStatus, 'waiting_response')
const withExperience = baseline.includes('## §10 体验定案') ? baseline :
  baseline.replace('## §11 做成后应该看到什么结果', '## §10 体验定案\n\n用于登记格式回归。\n\n## §11 做成后应该看到什么结果')
assert.equal((await send('prd-review', withExperience)).reviewStatus, 'formal')
const legacy = withExperience.replace('## §1 背景与目标', '## §0 这份基线依据什么生成\n\n用于登记格式回归。\n\n## §1 背景与目标') +
  '\n\n## §12 这些结论来自哪里\n\n用于登记格式回归。\n'
assert.equal((await send('prd-review', legacy)).reviewStatus, 'formal')
const formal = await send('prd-review', baseline)
assert.equal(formal.artifactKind, 'baseline')
assert.equal(formal.reviewStatus, 'formal')
const rendered = await send('page-spec', page)
assert.equal(rendered.artifactKind, 'artifact')
assert.deepEqual(readdirSync(taskDir).sort(), ['manifest.json','page-spec.md','prd-review-record.md','prd-review.md'])
assert.equal(readFileSync(join(taskDir, 'prd-review.md'), 'utf8'), baseline)
assert.equal(readFileSync(join(taskDir, 'page-spec.md'), 'utf8'), page)
assert.equal(existsSync(join(app,'spark-output','page-generation-handoff.md')), false)
console.log('workbench.submit: 5 valid submissions including current, §10 and legacy; 4 invalid inputs rejected; contents identical; no HF output')
