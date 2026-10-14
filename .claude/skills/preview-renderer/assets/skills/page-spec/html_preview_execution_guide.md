# Page Spec HTML 预览执行细则

## 目标

本文件说明 `page-spec` 的页面设计文档如何在 `preview-renderer` 内生成 HTML 预览。`page-spec` 自身只负责正式 Markdown 产出。

## 输入与输出

- 输入 Markdown：`spark-output/page_spec.md`
- 输出 HTML：`spark-output/preview/page_spec_preview.html`

## 结构要求

- 复用体验蓝图使用的公共阅读壳和视觉风格。
- 左侧章节导航和右侧正文均从正式 Markdown 投影。
- 页面实体、结构草图、流程、校验、状态、异常、结果态和文案必须保留，不得摘要化或补造内容。

## 脚本入口

默认执行：

```text
node ".claude/skills/preview-renderer/assets/skills/page-spec/generate_preview.js"
```

显式参数执行：

```text
node ".claude/skills/preview-renderer/assets/skills/page-spec/generate_preview.js" "<公共壳>" "<内容模板>" "<正式 Markdown>" "<输出 HTML>"
```

## 红线

- 不得修改页面设计文档、页面生成范围或主链状态。
- ASCII 草图必须以代码块形式保留。
- 生成前检查必需插槽；生成后不得遗留未替换占位符。
