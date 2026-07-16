# UXB HTML 预览执行细则

## 目标

本文件只说明 `uxb` 的 HTML 预览如何在 `preview-renderer` 内稳定生成。
`uxb` 自身只负责正式 Markdown 与 Context JSON 产出，不再持有 HTML 预览职责。

## 输入

- `spark-output/uxb_output.md`
- `spark-output/context/uxb.json`（如存在）
- `.claude/skills/preview-renderer/assets/shell/preview_shell.html`
- `.claude/skills/preview-renderer/assets/skills/uxb/preview_template.html`
- `.claude/skills/preview-renderer/assets/skills/uxb/generate_preview.js`

## 输出

- `spark-output/preview/uxb_preview.html`

## 结构要求

- 公共壳负责左侧章节导航和右侧容器。
- 当前模板只承接 `业务蓝图` 右侧内容片段。
- 左侧章节导航由公共壳注入，不在本模板内维护。
- `§0` 到 `§9` 与附录必须按正式文档落位，不得摘要化。

## 执行顺序

1. 调用 `.claude/skills/preview-renderer/assets/skills/uxb/generate_preview.js`。
2. 读取 `uxb_output.md`。
3. 读取 `uxb.json`（如存在，仅用于元信息，不补业务正文）。
4. 提取 `业务蓝图` 的正式章节。
5. 生成左侧章节导航并注入公共壳。
6. 将章节内容注入业务蓝图内容片段。
7. 将内容片段注入公共壳。
8. 输出到 `spark-output/preview/uxb_preview.html`。

## 脚本入口

默认执行：

```text
node ".claude/skills/preview-renderer/assets/skills/uxb/generate_preview.js"
```

显式参数执行：

```text
node ".claude/skills/preview-renderer/assets/skills/uxb/generate_preview.js" ".claude/skills/preview-renderer/assets/shell/preview_shell.html" ".claude/skills/preview-renderer/assets/skills/uxb/preview_template.html" "spark-output/context/uxb.json" "spark-output/uxb_output.md" "spark-output/preview/uxb_preview.html"
```

## 红线

- 不把公共壳重新写回业务蓝图内容片段。
- 不删除正式章节。
- 不把正文压缩成摘要卡片。
- 不为预览临时改写 Markdown 标题。
- 不根据 `uxb.json` 重新生成业务结论。
