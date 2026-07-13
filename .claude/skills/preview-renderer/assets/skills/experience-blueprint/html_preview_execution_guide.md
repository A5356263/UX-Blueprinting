# Experience Blueprint HTML 预览执行细则

## 目标

本文件只说明 `experience-blueprint` 的 HTML 预览如何在 `preview-renderer` 内稳定生成。
`experience-blueprint` 自身只负责正式 Markdown 与 Context JSON 产出，不再持有 HTML 预览职责。

## 输入

- `spark-output/experience_blueprint.md`
- `spark-output/context/experience-blueprint.json`（如存在）
- `.claude/skills/preview-renderer/assets/shell/preview_shell.html`
- `.claude/skills/preview-renderer/assets/skills/experience-blueprint/preview_template.html`

## 输出

- `spark-output/preview/experience_blueprint_preview.html`

## 结构要求

- 公共壳负责左侧产物选择器、章节导航和右侧容器。
- 当前模板只承接 `体验蓝图` 右侧内容片段。
- 左侧章节导航由公共壳注入，不在本模板内维护。
- 表格、ASCII 图、附录、待确认问题必须保留。

## 执行顺序

1. 读取 `experience_blueprint.md`。
2. 提取 `体验蓝图` 的正式章节。
3. 生成左侧章节导航并注入公共壳。
4. 将章节内容注入体验蓝图内容片段。
5. 将内容片段注入公共壳。
6. 输出到 `spark-output/preview/experience_blueprint_preview.html`。

## 红线

- 不把公共壳重新写回体验蓝图内容片段。
- 不删除正式章节。
- 不把正文压缩成摘要卡片。
- 不为预览临时改写 Markdown 标题。
