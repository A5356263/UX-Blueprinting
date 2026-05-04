# 32_copy_and_explanation_strategy

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-32_COPY_AND_EXPLANATION_STRATEGY
- page_type: summary
- source_path: knowledge/raw/business/permission/32_copy_and_explanation_strategy.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-04
- updated_at: 2026-05-04
- source_refs: [knowledge/raw/business/permission/32_copy_and_explanation_strategy.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

定义权限域中向用户解释权限结果时的策略体系，包括 3 条通用解释原则、3 个关键解释时机、8 种典型结果的文案口径、状态说明原则和错误解释原则，确保权限解释业务语义优先、层次清晰、可追溯。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要为权限页面设计解释性文案时
- 需要确定在不同场景（配置完成/查询详情/异常状态）下应解释什么内容
- 需要为可见但不可操作、可操作但无数据、待审批等典型结果设计口径时
- 需要确保错误解释可定位到判定层级且不引入新权限概念

## 3. 覆盖内容

本 raw 覆盖：

- 3 条解释原则：先结果再原因再来源与责任、优先使用业务语义不暴露技术实现、对高误解结果给出明确说明
- 3 个解释时机：配置完成后（是否已生效/卡在哪）、查询详情中（来源/范围/失败层级/原因码）、错误或异常状态下（当前结果/阻塞因素/下一步可行动作）
- 8 种文案口径策略：可见但不可操作、可操作但无数据、全部数据权限、部分数据权限、无数据权限、条件组约束失败、待审批、不可见覆盖
- 状态说明原则（覆盖当前态+责任人+下一步动作）和错误解释原则（可定位到判定层级+不引入新概念+使用标准原因码）

不涉及：

- 具体的文案措辞和 UI 文本

## 4. 可直接使用的稳定结论

- 解释顺序：先解释结果 -> 再解释原因 -> 再解释来源与责任；优先使用业务语义，不直接暴露技术实现细节
- 三种解释时机各有侧重：配置完成后解释生效状态和卡点，查询详情中解释来源和失败层级，异常状态下解释阻塞因素和可行动作
- 对覆盖、互斥、待审、范围为空等 4 类高误解风险结果，必须给出明确说明
- 错误解释必须可定位到判定层级（对应 conflict_reason_code），且避免引入新的权限概念

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

- knowledge/wiki/summaries/business/permission/00_domain_overview.md
- knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
- knowledge/wiki/summaries/business/permission/02_glossary.md
- knowledge/wiki/summaries/business/permission/03_business_objects.md
- knowledge/wiki/summaries/business/permission/04_object_relations.md

> summary_path: knowledge/wiki/summaries/business/permission/32_copy_and_explanation_strategy.md
