# 用户故事 HTML 预览执行说明

## 输入

- Markdown：`spark-output/stories.md`
- Context JSON：`spark-output/context/stories.json`（可选，仅作存在状态展示或兼容输入，不得阻断预览）
- 公共壳：`.claude/skills/preview-renderer/assets/shell/preview_shell.html`
- 内容模板：`.claude/skills/preview-renderer/assets/skills/stories/preview_template.html`
- 生成脚本：`.claude/skills/preview-renderer/assets/skills/stories/generate_preview.js`

## 输出

- 默认输出：`spark-output/preview/stories_preview.html`

## 渲染规则

- 只结构化展示正式 Markdown 中已经存在的信息。
- 不把 Story 强行改成旅程阶段。
- 不新增 Story，不改写优先级，不补写验收标准，不把关键假设渲染成事实。
- 允许把已有字段投影成故事概览、角色分组、Story 卡片、主链与假设清单。
- Context JSON 缺失或不可读时不得阻断 HTML 预览生成。

## 展示结构

- 顶部展示故事概览，包括来源、故事数量、P0 主链数量和关键假设数量。
- 正文按角色分组展示 Story 卡片。
- Story 卡片保留角色、目标、场景、Story 主体、完成标准、设计触点、来源依据、风险和关键假设。
- 底部展示 P0 主链清单、辅助能力清单和假设项清单。
