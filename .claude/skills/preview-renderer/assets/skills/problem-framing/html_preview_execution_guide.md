# 问题框定 HTML 预览执行说明

## 输入

- Markdown：`spark-output/problem_framing.md`
- Context JSON：`spark-output/context/problem-framing.json`（可选，仅作存在状态展示或兼容输入，不得阻断预览）
- 公共壳：`.claude/skills/preview-renderer/assets/shell/preview_shell.html`
- 内容模板：`.claude/skills/preview-renderer/assets/skills/problem-framing/preview_template.html`
- 生成脚本：`.claude/skills/preview-renderer/assets/skills/problem-framing/generate_preview.js`

## 输出

- 默认输出：`spark-output/preview/problem_framing_preview.html`

## 渲染规则

- 只结构化展示正式 Markdown 中已经存在的信息。
- 不新增业务结论，不改写推荐方向、优先级、承接契约、边界或待确认问题。
- 不补写缺失的角色、场景、约束、知识锚定或下游承接信息。
- 允许把已有字段投影成摘要卡片、章节列表和表格。
- Context JSON 缺失或不可读时不得阻断 HTML 预览生成。

## 展示结构

- 顶部摘要卡片展示推荐方向、核心问题、目标角色和关键约束。
- 正文区展示输入摘要、问题定义、目标用户与场景、当前替代做法、机会点、候选方向、推荐方向、承接契约、约束、待确认问题和知识锚定。
- 左侧章节导航由脚本根据实际渲染章节生成。
