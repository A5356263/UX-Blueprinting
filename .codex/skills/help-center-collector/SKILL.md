---
name: help-center-collector
description: Collect product help-center knowledge from public documentation sites using Codex browser capabilities. Use when the user wants to traverse a help center, preserve its original information structure, capture article content instead of summaries, analyze images or videos embedded in docs, and output a structured Markdown help knowledge base.
---

# 帮助中心采集

把帮助中心内容采成产品知识，不要把它做成摘要、营销摘录或采集过程流水账。

## 使用流程

1. 开始前先读 [references/collection-scope.md](references/collection-scope.md)，确认工具能力、采集边界和硬约束。
2. 进入任何模块前先读 [references/traversal-method.md](references/traversal-method.md)。没有完整清单前，不要开始正文采集。
3. 采集叶子页面、图片或视频时，读 [references/page-collection-guide.md](references/page-collection-guide.md)。
4. 页面出现前置条件、下游影响或跨模块依赖时，读 [references/module-relations.md](references/module-relations.md)。
5. 写文件前和收尾前都读一次 [references/output-organization.md](references/output-organization.md)，确保输出结构、索引和采集日志完整。

默认页面采集模板见 [assets/page-collection.template.md](assets/page-collection.template.md)。

## 核心规则

- 尽量保留原帮助中心的结构。
- 按原始信息粒度记录文章内容，不压缩成摘要。
- 只记录页面明确写出的规则。
- 图片和视频解析结果必须回填到原文上下文里，不要单独堆成附录。
- 采集失败、工具限制和覆盖率日志不要写进正文。

## 禁止事项

- 不要采集无关的营销、法律、页脚或品牌信息。
- 不要在没有完整模块清单时就开始采集。
- 不要只建 README 壳，不下钻实际文章内容。
- 不要把 FAQ 列表、版本动态列表、手册列表误当成终点页面。
- 不要编造页面没写出的规则、依赖或流程步骤。
