# 流程模式选择原则

- page_id: PG-SUMMARY-GUIDELINES-GUIDELINES-FLOW_MODE
- page_type: summary
- source_path: knowledge/raw/guidelines/flow_mode.md
- source_group: guidelines
- status: active
- confidence: medium
- updated_at: 2026-05-04
- source_refs: [knowledge/raw/guidelines/flow_mode.md]
- related_summaries:
  - knowledge/wiki/summaries/guidelines/README.md
  - knowledge/wiki/summaries/guidelines/accessibility.md
  - knowledge/wiki/summaries/guidelines/cognition.md
  - knowledge/wiki/summaries/guidelines/governance.md
  - knowledge/wiki/summaries/guidelines/information_architecture.md

## 1. 知识定位

定义并阐述「BFM-01 默认非步骤化（B 端专家场景）」相关的设计原则、触发条件、推导输出与自检标准。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要理解业务流程或任务场景的完整路径
- 评估信息架构、导航结构或内容可发现性

## 3. 覆盖内容

本 raw 覆盖：

- 风险：BFM-02 步骤条使用门禁（强依赖/不可逆/高风险）
- 章节：BFM-01 默认非步骤化（B 端专家场景）, BFM-03 单页长表单 + 锚点导航（步骤条替代模式）

不涉及：

- 本 raw 未显式覆盖的内容需回查其他相关 raw 或补充来源

## 4. 可直接使用的稳定结论

- 来源：B 端专家用户特征 + 流程效率原则
- 定义：对 B 端高频录入/编辑型任务，默认优先单页表单，不因“字段多/表单长/看起来复杂”直接使用步骤条。
- 触发：长表单、复杂配置页、二次编辑频繁、资料分批补录。
- 推导输出：先评估 `single_page_form` 是否可完成；优先从任务依赖而非字段数量决定流程模式。
- 文档落点：流程模式决策｜信息结构
- 自检问句：如果取消步骤条，用户是否更容易全局查看、补录与修改？

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
