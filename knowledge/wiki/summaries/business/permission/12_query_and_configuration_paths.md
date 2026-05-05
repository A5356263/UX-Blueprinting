# 12_query_and_configuration_paths

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-12_QUERY_AND_CONFIGURATION_PATHS
- page_type: summary
- source_path: knowledge/raw/business/permission/12_query_and_configuration_paths.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-05
- updated_at: 2026-05-05
- source_refs: [knowledge/raw/business/permission/12_query_and_configuration_paths.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

同时说明权限域的查询路径和配置路径，显式写出每种路径的语义、现状承载页面和可行性级别，即使现状承载分散也如实标注缺口，用于判断某个查询或配置需求当前是否有页面支撑。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要确认某个查询维度（按用户/按角色/按应用/按变更/按功能点）当前是否有承载页面
- 需要了解权限域的 5 条配置路径及其页面流程
- 需要评估查询能力的可行性现状（feasible/partial/GAP）
- 需要了解按变更查、按功能点查等维度的已知缺口

## 3. 覆盖内容

本 raw 覆盖：

- 5 条查询路径：按用户查（feasible）、按角色查（partial）、按应用查（feasible）、按变更查（partial）、按权限查/按功能点查（GAP）
- 5 条配置路径：用户配置（用户授权->功能授权->数据授权）、角色配置（角色管理->功能权限/数据权限->授权规则）、治理配置（3 条子路径）、协作配置（成员协作权限）、应用配置（应用管理->应用设置页）
- 现状缺口 3 项

不涉及：

- 页面内部的详细交互语义（在 15_page_carrier_semantics 中定义）
- 路由关系（在 13_route_map 中定义）

## 4. 可直接使用的稳定结论

- 按用户查是唯一完全可行的查询维度（feasible），走权限查询->按用户查询结果->权限详情链路
- 按角色查为 partial（角色管理可查成员但无独立查询页），按变更查为 partial（分散在权限域与审批域之间）
- 按权限查/按功能点查现状为 GAP，对应结果承载页尚未核实
- 治理配置路径（权限管理模式->子管理/双管理员/审批模式配置）承载的是系统级规则，不属于普通功能授权页的局部配置

## 5. 必须回查 raw 的情况

以下情况不能只读 summary：

- 需要完整规则细节或精确条款时
- 需要正式证据或原文引用时
- 需要页面或流程的完整描述时
- 涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时
- summary 无法覆盖当前判断点或信息量不足时

## 6. 缺口 / 冲突 / 不确定项

- [GAP] 按权限查 / 按功能点查现状承载待进一步核实
- [GAP] 按角色查虽有角色管理承载，但独立查询语义与结果视图仍未完全明确
- [GAP] 按变更查当前分散在权限域与审批域之间，权限域内缺少统一变更台账页

## 7. 邻近阅读

弱指向 3-5 个相关 summary。

- knowledge/wiki/summaries/business/permission/00_domain_overview.md
- knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
- knowledge/wiki/summaries/business/permission/02_glossary.md
- knowledge/wiki/summaries/business/permission/03_business_objects.md
- knowledge/wiki/summaries/business/permission/04_object_relations.md

> summary_path: knowledge/wiki/summaries/business/permission/12_query_and_configuration_paths.md
