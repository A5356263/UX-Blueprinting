# 设计策略生成 HTML 预览执行说明

## 输入

- Markdown：`spark-output/problem_framing.md`
- 公共壳：`.agents/skills/preview-renderer/assets/shell/preview_shell.html`
- 内容模板：`.agents/skills/preview-renderer/assets/skills/problem-framing/preview_template.html`
- 生成脚本：`.agents/skills/preview-renderer/assets/skills/problem-framing/generate_preview.js`

调用参数按顺序为公共壳、内容模板、正式 Markdown、输出 HTML；不传 Context 路径。

## 输出

- 默认输出：`spark-output/preview/problem_framing_preview.html`

## 渲染规则

- 只结构化展示正式 Markdown 中已经存在的信息。
- 不新增业务结论，不改写主推荐方案、推荐依据、承接要求、边界或待确认事项。
- 不补写缺失的角色、场景、约束、知识锚定或下游承接信息。
- 允许把已有字段投影成摘要卡片、章节列表和表格。
- 预览只从正式 Markdown 投影。

## 展示结构

- 顶部摘要卡片展示主推荐业务方案、正式问题、目标角色和关键约束。
- 按 Markdown 正文渲染完整正式产物。
- 左侧章节导航由脚本根据实际渲染章节生成。
