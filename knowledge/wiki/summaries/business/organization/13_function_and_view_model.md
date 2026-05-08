# 13_function_and_view_model

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-ORGANIZATION-13_FUNCTION_AND_VIEW_MODEL
- page_type: summary
- source_path: knowledge/raw/business/organization/13_function_and_view_model.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-08
- updated_at: 2026-05-08
- source_refs: [knowledge/raw/business/organization/13_function_and_view_model.md]
- related_summaries:
  - knowledge/wiki/summaries/business/organization/00_domain_overview.md
  - knowledge/wiki/summaries/business/organization/10_organization_architecture.md
  - knowledge/wiki/summaries/business/organization/11_legal_entities.md
  - knowledge/wiki/summaries/business/organization/12_cost_centers.md
  - knowledge/wiki/summaries/business/organization/14_member_binding_and_scope_generation.md

## 1. 知识定位

定义平台组织底座中的核心抽象，回答“多维组织、职能、视图分别是什么，它们如何构成新的组织内核”。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要判断职能和视图的层级关系时
- 需要理解旧对象为何不再作为顶层菜单语义时
- 需要确认平台默认视图与业务自定义视图的边界时
- 需要把后端底座模型映射到前端页面逻辑时

## 3. 覆盖内容

本 raw 覆盖：

- 核心对象定义：多维组织、职能、视图
- 两条默认映射：组织架构 -> 行政职能/组织架构视图，法人公司 -> 核算职能/法人公司视图
- 稳定聚合关系：多维组织供给职能，职能下承载多个视图，视图参与授权和业务消费
- 平台默认视图与业务自定义视图并存的事实

不涉及：

- 平台默认视图与业务视图的完整字段差异

## 4. 可直接使用的稳定结论

- 视图是职能下的维度承载层，一个职能可以对应多个视图
- 多维组织是新的组织数据底座，旧对象会被纳入其中再通过职能/视图组织出去
- 新模型不仅影响后端数据结构，也会影响前端导航、控件和配置流
- 当前材料已明确行政职能、核算职能及业务自定义维度的存在

## 5. 必须回查 raw 的情况

以下情况不能只读 summary：

- 需要完整规则细节或精确条款时
- 需要正式证据或原文引用时
- 需要页面或流程的完整描述时
- 涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时
- summary 无法覆盖当前判断点或信息量不足时

## 6. 缺口 / 冲突 / 不确定项

- [GAP] 当前资料未明确平台默认视图与业务自定义视图在数据结构上的完整字段差异

## 7. 邻近阅读

弱指向 3-5 个相关 summary。

- knowledge/wiki/summaries/business/organization/00_domain_overview.md
- knowledge/wiki/summaries/business/organization/10_organization_architecture.md
- knowledge/wiki/summaries/business/organization/11_legal_entities.md
- knowledge/wiki/summaries/business/organization/12_cost_centers.md
- knowledge/wiki/summaries/business/organization/14_member_binding_and_scope_generation.md

> summary_path: knowledge/wiki/summaries/business/organization/13_function_and_view_model.md
