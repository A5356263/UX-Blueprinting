# Experience Blueprint HTML 预览执行细则

## 目标

本文件只说明 `experience-blueprint` 的 HTML 预览如何在 `preview-renderer` 内稳定生成。
`experience-blueprint` 自身只负责正式 Markdown 与 Context JSON 产出，不再持有 HTML 预览职责。

## 输入

- `spark-output/experience_blueprint.md`
- `spark-output/context/experience-blueprint.json`（如存在）
- `.claude/skills/preview-renderer/assets/shell/preview_shell.html`
- `.claude/skills/preview-renderer/assets/skills/experience-blueprint/preview_template.html`
- `.claude/skills/preview-renderer/assets/skills/experience-blueprint/generate_preview.js`

## 输出

- `spark-output/preview/experience_blueprint_preview.html`

## 结构要求

- 公共壳负责左侧产物选择器、章节导航和右侧容器。
- 当前模板只承接 `体验蓝图` 右侧内容片段。
- 左侧章节导航由公共壳注入，不在本模板内维护。
- 表格、ASCII 图、附录、待确认问题必须保留。
- `§2 交互流程总览` 中可稳定识别的箭头流程代码块，可以投影为横向流程图展示。
- `§2` 流程节点、顺序和文案必须来自原 Markdown；无法稳定识别时保留原 Markdown 渲染。

## 执行顺序

1. 调用 `.claude/skills/preview-renderer/assets/skills/experience-blueprint/generate_preview.js`。
2. 读取 `experience_blueprint.md`。
3. 读取 `experience-blueprint.json`（如存在，仅用于元信息，不补业务正文）。
4. 提取 `体验蓝图` 的正式章节。
5. 生成左侧章节导航并注入公共壳。
6. 将章节内容注入体验蓝图内容片段。
7. 将内容片段注入公共壳。
8. 输出到 `spark-output/preview/experience_blueprint_preview.html`。

## 脚本入口

默认执行：

```powershell
node ".claude/skills/preview-renderer/assets/skills/experience-blueprint/generate_preview.js"
```

显式参数执行：

```powershell
node ".claude/skills/preview-renderer/assets/skills/experience-blueprint/generate_preview.js" ".claude/skills/preview-renderer/assets/shell/preview_shell.html" ".claude/skills/preview-renderer/assets/skills/experience-blueprint/preview_template.html" "spark-output/context/experience-blueprint.json" "spark-output/experience_blueprint.md" "spark-output/preview/experience_blueprint_preview.html"
```

## 红线

- 不把公共壳重新写回体验蓝图内容片段。
- 不删除正式章节。
- 不把正文压缩成摘要卡片。
- 不为预览临时改写 Markdown 标题。
- 不根据 `experience-blueprint.json` 重新生成业务结论。
- 不为了 `§2` 视觉效果新增、删除、合并或重排流程节点。
