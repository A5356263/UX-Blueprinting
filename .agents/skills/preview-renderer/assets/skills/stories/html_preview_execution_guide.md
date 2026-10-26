# 用户故事 HTML 预览执行说明

## 输入

- Markdown：`spark-output/stories.md`
- 公共壳：`.agents/skills/preview-renderer/assets/shell/preview_shell.html`
- 内容模板：`.agents/skills/preview-renderer/assets/skills/stories/preview_template.html`
- 生成脚本：`.agents/skills/preview-renderer/assets/skills/stories/generate_preview.js`

## 输出

- 默认输出：`spark-output/preview/stories_preview.html`

## 渲染规则

- 只结构化展示正式 Markdown 中已经存在的信息。
- 不把 Story 强行改成旅程阶段。
- 不新增 Story，不改写优先级，不补写验收标准，不把关键假设渲染成事实。
- 按正式 Markdown 的标题、列表和表格投影章节，不另行推导分组或统计。
- 预览只从正式 Markdown 投影。

## 展示结构

- 按正式 Markdown 顺序展示来源与方向、Story 索引、全部 Story 详情、不进入 Story 的内容和待确认问题。
- 左侧导航由实际章节标题生成。
