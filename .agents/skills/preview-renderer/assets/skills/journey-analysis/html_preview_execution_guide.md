# 角色旅程 HTML 预览执行说明

## 输入

- Markdown：`spark-output/journey_analysis.md`
- 公共壳：`.agents/skills/preview-renderer/assets/shell/preview_shell.html`
- 内容模板：`.agents/skills/preview-renderer/assets/skills/journey-analysis/journey_preview_template.html`
- 生成脚本：`.agents/skills/preview-renderer/assets/skills/journey-analysis/generate_preview.js`

## 输出

- 默认输出：`spark-output/preview/journey_analysis_preview.html`

## 渲染规则

- 只结构化展示正式 Markdown 中已经存在的信息。
- 不新增业务结论，不改写阶段、角色、痛点、风险、机会或下游提示。
- 不补写缺失的阶段、触点、用户心声、痛点或设计机会。
- 按正式 Markdown 的标题、列表和表格投影章节，不另行推导旅程矩阵或统计。
- 预览只从正式 Markdown 投影。

## 展示结构

- 按正式 Markdown 顺序展示来源、角色旅程、阶段、转折、缺口和后续建议。
- 左侧导航由实际章节标题生成。
