# 13_route_map

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-13_ROUTE_MAP
- page_type: summary
- source_path: knowledge/raw/business/permission/13_route_map.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-07
- updated_at: 2026-05-07
- source_refs: [knowledge/raw/business/permission/13_route_map.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

说明权限域内页面之间以及权限域与外部治理模块（审批管理、应用中心等）之间的主要路由关系，区分配置链路、解释链路和外部治理链路，是页面跳转设计的基础参考。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 设计页面跳转关系时需要知道页面间的上下游路由
- 需要理解权限域页面与外部审批系统、应用中心的路由串联
- 需要区分配置链路和解释链路的走向和终点
- 需要确认按人配置、角色管理、系统治理等链路的路由完整性

## 3. 覆盖内容

本 raw 覆盖：

- 配置链路（6 条）：用户授权->功能授权->数据授权、角色管理->授权规则等
- 解释链路（4 条）：权限查询->按用户查询结果->权限明细等
- 外部治理链路（4 条）：权限变更审批模式配置页->审批管理等
- 5 条路由说明：每条核心链路的路由目的和职责

不涉及：

- 页面内部的详细模块和交互（在 15_page_carrier_semantics 中定义）
- 任务场景级别的操作步骤（在 11_task_scenarios 中定义）

## 4. 可直接使用的稳定结论

- 权限域存在 3 类路由链路：配置链路（如用户授权->功能授权->数据授权是按人配置主链路）、解释链路（如权限查询->按用户查询结果->权限明细是排障链路）、外部治理链路（如权限变更审批模式配置页->审批管理）
- 角色管理->授权规则是角色模板化授权向自动授权扩展的链路
- 权限查询链路不负责配置，应用管理->应用设置页是应用级入口治理与单应用管理员治理链路

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

> summary_path: knowledge/wiki/summaries/business/permission/13_route_map.md
