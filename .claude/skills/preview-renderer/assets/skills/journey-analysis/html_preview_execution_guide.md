# 角色旅程 HTML 预览执行说明

## 输入

- Markdown：`spark-output/journey_analysis.md`
- Context JSON：`spark-output/context/journey-analysis.json`（可选，仅作存在状态展示或兼容输入，不得阻断预览）
- 公共壳：`.claude/skills/preview-renderer/assets/shell/preview_shell.html`
- 内容模板：`.claude/skills/preview-renderer/assets/skills/journey-analysis/journey_preview_template.html`
- 生成脚本：`.claude/skills/preview-renderer/assets/skills/journey-analysis/generate_preview.js`

## 输出

- 默认输出：`spark-output/preview/journey_analysis_preview.html`

## 渲染规则

- 只结构化展示正式 Markdown 中已经存在的信息。
- 不新增业务结论，不改写阶段、角色、痛点、风险、机会或下游提示。
- 不补写缺失的阶段、触点、用户心声、痛点或设计机会。
- 允许把已有字段投影成旅程图表格、人物卡片、阶段转折与状态标签。
- Context JSON 缺失或不可读时不得阻断 HTML 预览生成。

## 展示结构

- 顶部展示项目名、生成时间、模式和来源。
- 人物卡片展示角色与旅程摘要。
- `JTBD` 区域优先展示 `start_condition`，无值时展示旅程摘要。
- 主体采用旅程图矩阵，行包括用户目标、用户行动、触点、用户心声、信心与风险、痛点、设计机会。
- 阶段转折区域展示 `key_transitions`。
