const baselineSections = [
  '这份基线依据什么生成', '背景与目标', '功能与变更清单', '谁能做什么', '每件事怎么完成', '要遵守什么规则',
  '会出现哪些状态', '遇到特殊情况怎么办', '会影响哪些记录和系统', '这次明确不做什么', '体验定案',
  '做成后应该看到什么结果', '这些结论来自哪里',
]

const reviewRecordSections = ['需求初识', '审核结论', '场景审核']

export function classifyPrdReview(markdown) {
  if (typeof markdown !== 'string') return { kind: 'unknown', status: '' }
  const lines = markdown.trim().split(/\r?\n/)
  const title = (lines[0] ?? '').trim()
  if (title === '# PRD 审核记录') {
    const status = markdown.match(/^\s*[-*]?\s*状态[：:]\s*`?(waiting_response|no_confirmation_required)`?\s*$/m)?.[1] ?? ''
    return { kind: 'review-record', status }
  }
  if (title === '# 正式需求基线') return { kind: 'baseline', status: 'formal' }
  return { kind: 'unknown', status: '' }
}

export function validateMarkdown(skill, markdown) {
  if (typeof markdown !== 'string') throw new Error('产物必须是 Markdown 文本')
  const lines = markdown.trim().split(/\r?\n/)
  if (!/^# \S/.test(lines[0] ?? '')) throw new Error('产物缺少一级标题')
  if (markdown.trim().length < 20) throw new Error('产物内容过短')
  const sections = lines.filter(line => line.startsWith('## ')).map(line => line.slice(3).trim())
  if (skill === 'prd-review') {
    const review = classifyPrdReview(markdown)
    if (review.kind === 'review-record') {
      if (!review.status ||
          !reviewRecordSections.every(title => sections.includes(title)) ||
          !sections.some(title => title.startsWith('你还需要补充什么吗'))) {
        throw new Error('PRD 审核记录缺少状态、需求初识、审核结论、场景审核或补充入口')
      }
    } else if (review.kind === 'baseline') {
      if (baselineSections.some((title, i) => sections[i] !== '§' + i + ' ' + title) ||
          !/^\s*[-*]?\s*基线状态[：:]\s*`?formal`?\s*$/m.test(markdown)) {
        throw new Error('正式需求基线缺少规定的章节或 formal 标记')
      }
    } else {
      throw new Error('PRD 产物必须是「PRD 审核记录」或「正式需求基线」')
    }
  } else if (skill === 'page-spec') {
    if (!/^# 页面生成规格[：:]\s*\S/.test(lines[0]) ||
        !['1. 页面摘要', '2. 生成范围', '3. 跨实体任务流程'].every((title, i) => sections[i] === title) ||
        sections.length < 4) {
      throw new Error('页面规格缺少摘要、生成范围、任务流程或页面实体')
    }
  }
  return true
}
