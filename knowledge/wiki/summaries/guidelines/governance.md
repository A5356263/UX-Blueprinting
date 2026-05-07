# 治理、信任与可解释性原则

- page_id: PG-SUMMARY-GUIDELINES-GUIDELINES-GOVERNANCE
- page_type: summary
- source_path: knowledge/raw/guidelines/governance.md
- source_group: guidelines
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-07
- updated_at: 2026-05-07
- source_refs: [knowledge/raw/guidelines/governance.md]
- related_summaries:
  - knowledge/wiki/summaries/guidelines/README.md
  - knowledge/wiki/summaries/guidelines/accessibility.md
  - knowledge/wiki/summaries/guidelines/cognition.md
  - knowledge/wiki/summaries/guidelines/flow_mode.md
  - knowledge/wiki/summaries/guidelines/information_architecture.md

## 1. 知识定位

提供治理、信任与可解释性的设计原则，帮助判断方案在覆盖规则、默认值、审批生效、授权共享等场景下是否暗改用户预期、缺乏原因解释或缺少追溯与回收能力。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要设计多来源规则叠加、优先级覆盖、自动生效等场景的行为解释机制
- 需要为权限/策略/批量操作设计审计追溯链路
- 需要确定授权/共享/可见性/导出的默认范围与回收路径
- 需要评估方案是否存在”覆盖规则隐藏””只展示结果不展示原因”等反模式

## 3. 覆盖内容

本 raw 覆盖：

- 原则：G-01 最小惊讶（Least Surprise）、G-02 可解释性（Explainability）、G-03 可追溯（Traceability）、G-04 最小授权（Least Privilege）

不涉及：

- 本 raw 未显式覆盖的内容需回查其他相关 raw 或补充来源

## 4. 可直接使用的稳定结论

- 系统行为必须符合承诺与直觉，任何覆盖/自动行为必须可解释、可追溯，不暗改结果
- 对多来源叠加/优先级覆盖/审批生效的结果，必须提供来源、优先级、冲突原因与判定链路
- 高风险变更（权限/策略/批量/导出）必须记录谁/何时/对谁/做了什么/影响范围/原因
- 默认授权范围应收敛，扩大范围需要更强解释与确认，且必须可撤销

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
- knowledge/wiki/summaries/guidelines/flow_mode.md
- knowledge/wiki/summaries/guidelines/information_architecture.md

> summary_path: knowledge/wiki/summaries/guidelines/governance.md
