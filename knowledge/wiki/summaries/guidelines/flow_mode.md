# 流程模式选择原则

- page_id: PG-SUMMARY-GUIDELINES-GUIDELINES-FLOW_MODE
- page_type: summary
- source_path: knowledge/raw/guidelines/flow_mode.md
- source_group: guidelines
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-08
- updated_at: 2026-05-08
- source_refs: [knowledge/raw/guidelines/flow_mode.md]
- related_summaries:
  - knowledge/wiki/summaries/guidelines/README.md
  - knowledge/wiki/summaries/guidelines/accessibility.md
  - knowledge/wiki/summaries/guidelines/cognition.md
  - knowledge/wiki/summaries/guidelines/governance.md
  - knowledge/wiki/summaries/guidelines/information_architecture.md

## 1. 知识定位

提供 B 端场景下流程模式（步骤条 vs 单页表单）的选择判定依据，帮助从任务依赖关系而非字段数量决定是否分步，避免将步骤条当作复杂表单的默认答案。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要为长表单、复杂配置页决策使用步骤条还是单页表单
- 需要判断当前任务是否存在强步骤依赖、不可逆操作或高风险场景
- 需要为步骤条寻找替代模式（锚点导航 + 单页长表单）
- 需要评估二次编辑频繁或资料分批补录场景的流程模式

## 3. 覆盖内容

本 raw 覆盖：

- 原则：BFM-01 默认非步骤化（B 端专家场景优先单页表单）、BFM-02 步骤条使用门禁（强依赖/不可逆/高风险时才用）、BFM-03 单页长表单 + 锚点导航（步骤条替代模式）

不涉及：

- 本 raw 未显式覆盖的内容需回查其他相关 raw 或补充来源

## 4. 可直接使用的稳定结论

- 对 B 端高频录入/编辑型任务，默认优先单页表单，不因”字段多/看起来复杂”直接使用步骤条
- 步骤条仅用于真实分步流程（后续强依赖前步结果、分阶段提交、不可逆任务、低频高风险），不应仅作视觉分组装饰
- 字段多不等于流程多，应先判断任务依赖关系再决定是否分步
- 无强步骤依赖时用单页长表单配合锚点导航，提供全局视角与随机存取能力

## 5. 必须回查 raw 的情况

以下情况不能只读 summary：

- 需要完整规则细节或精确条款时
- 需要正式证据或原文引用时
- 需要页面或流程的完整描述时
- 涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时
- summary 无法覆盖当前判断点或信息量不足时

## 6. 缺口 / 冲突 / 不确定项

- none

## 7. 邻近阅读

弱指向 3-5 个相关 summary。

- knowledge/wiki/summaries/guidelines/README.md
- knowledge/wiki/summaries/guidelines/accessibility.md
- knowledge/wiki/summaries/guidelines/cognition.md
- knowledge/wiki/summaries/guidelines/governance.md
- knowledge/wiki/summaries/guidelines/information_architecture.md

> summary_path: knowledge/wiki/summaries/guidelines/flow_mode.md
