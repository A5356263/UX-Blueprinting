const baselineSections = [
  '这份基线依据什么生成', '背景与目标', '功能与变更清单', '谁能做什么', '每件事怎么完成', '要遵守什么规则',
  '会出现哪些状态', '遇到特殊情况怎么办', '会影响哪些记录和系统', '这次明确不做什么', '体验定案',
  '做成后应该看到什么结果', '这些结论来自哪里',
]

export function validateMarkdown(stage, markdown) {
  const lines = markdown.trim().split(/\r?\n/)
  const sections = lines.filter(line => line.startsWith('## ')).map(line => line.slice(3).trim())
  if (stage === 'prd-review') {
    if (lines[0].trim() !== '# 正式需求基线' ||
        baselineSections.some((title, i) => sections[i] !== '§' + i + ' ' + title) ||
        !/^\s*[-*]?\s*基线状态[：:]\s*`?formal`?\s*$/m.test(markdown)) {
      throw new Error('正式需求基线缺少规定的章节或 formal 标记')
    }
  } else if (stage === 'uxb') {
    if (!/^# (UXB )?体验策略[：:]\s*\S/.test(lines[0]) ||
        !sections.includes('策略前提与范围') || !sections.includes('来源') ||
        !sections.some(title => title === '整体主推方向' || title === '结论')) {
      throw new Error('体验策略稿缺少范围、方向或来源')
    }
  } else if (stage === 'journey-analysis') {
    const grade = lines.filter(line => /^\s*[-*]?\s*结果等级[：:]\s*`?(完整旅程|补全后旅程|旅程骨架)`?\s*$/.test(line))
    if (!/^# .+/.test(lines[0]) || grade.length !== 1 || !sections.length) throw new Error('用户旅程缺少标题、结果等级或正文')
    return !grade[0].includes('旅程骨架')
  } else if (stage === 'page-spec') {
    if (!/^# 页面生成规格[：:]\s*\S/.test(lines[0]) ||
        !['1. 页面摘要', '2. 生成范围', '3. 跨实体任务流程'].every((title, i) => sections[i] === title) ||
        sections.length < 4) {
      throw new Error('页面规格缺少摘要、生成范围、任务流程或页面实体')
    }
  } else throw new Error('当前阶段没有产物契约')
}
