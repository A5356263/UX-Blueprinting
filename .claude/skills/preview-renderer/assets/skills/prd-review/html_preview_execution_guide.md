# PRD Review HTML 预览执行细则

## 目标

本文件说明 `prd-review` 的需求基线如何在 `preview-renderer` 内生成 HTML 预览。`prd-review` 自身只负责正式 Markdown 与 Context JSON 产出。

## 输入与输出

- 输入 Markdown：`spark-output/requirements_baseline.md`
- 可选 Context：`spark-output/context/requirements-baseline.json`
- 输出 HTML：`spark-output/preview/requirements_baseline_preview.html`

## 结构要求

- 复用体验蓝图使用的公共阅读壳和视觉风格。
- 左侧章节导航和右侧正文均从正式 Markdown 投影。
- 业务规则、状态、待定案事项、表格和附录必须保留，不得摘要化或补造内容。

## 脚本入口

默认执行：

```text
node ".claude/skills/preview-renderer/assets/skills/prd-review/generate_preview.js"
```

显式参数执行：

```text
node ".claude/skills/preview-renderer/assets/skills/prd-review/generate_preview.js" "<公共壳>" "<内容模板>" "<Context JSON>" "<正式 Markdown>" "<输出 HTML>"
```

## 红线

- Context JSON 缺失不得阻断预览生成，也不得决定正文内容。
- 不得修改需求基线、问题单、Context JSON 或主链状态。
- 生成前检查必需插槽；生成后不得遗留未替换占位符。
