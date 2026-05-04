# 15_page_carrier_semantics

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-15_PAGE_CARRIER_SEMANTICS
- page_type: summary
- source_path: knowledge/raw/business/permission/15_page_carrier_semantics.md
- source_group: business
- status: active
- confidence: medium
- updated_at: 2026-05-04
- source_refs: [knowledge/raw/business/permission/15_page_carrier_semantics.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

为权限域中每个关键页面提供语义卡片，说明页面的目标、模块/功能、操作、状态、入口出口、解释点和页面类型判断，用于判断页面在方案中应承担配置、查询、解释还是治理职责。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要理解某个权限页面的完整业务语义
- 判断页面类型（配置页/查询页/解释页/治理页）
- 设计页面跳转或入口关系时需要知道出入口
- 评估页面的解释能力是否满足用户理解需求

## 3. 覆盖内容

本 raw 覆盖：

- 页面：用户授权、功能授权、数据授权、权限详情、角色管理、授权规则、权限管理模式、子管理员模式、子管理配置、双管理员模式、审批模式、成员协作权限、权限查询、按用户查询结果、应用管理、应用设置
- 规则：每个页面的语义定义（目标、操作、状态、入口/出口、解释点、类型判断）

不涉及：

- 本 raw 未显式覆盖的内容需回查其他相关 raw 或补充来源

## 4. 可直接使用的稳定结论

- 权限页面按职责分为配置页、查询页、解释页、治理页四类
- 用户授权/功能授权/数据授权 为配置页，承担权限授予
- 权限详情 为解释页，承担只读解释与核对
- 权限查询/按用户查询结果 为查询页，负责排障与审计
- 权限管理模式/子管理配置/双管理员模式 为治理页，定义系统级治理范式

## 5. 必须回查 raw 的情况

以下情况不能只读 summary：

- 需要完整规则细节或精确条款时
- 需要正式证据或原文引用时
- 需要页面或流程的完整描述时
- 涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时
- summary 无法覆盖当前判断点或信息量不足时

## 6. 缺口 / 冲突 / 不确定项

- [GAP] 权限查询中的按角色查、按权限查、按功能点查的现状承载尚未核实
- [GAP] 部分治理弹窗和配置页的下游跳转未在现有页面事实中给出
- [GAP] 权限明细视图的独立页面语义尚未在现有材料中展开

## 7. 邻近阅读

弱指向 3-5 个相关 summary。

- knowledge/wiki/summaries/business/permission/00_domain_overview.md
- knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
- knowledge/wiki/summaries/business/permission/02_glossary.md
- knowledge/wiki/summaries/business/permission/03_business_objects.md
- knowledge/wiki/summaries/business/permission/04_object_relations.md

> summary_path: knowledge/wiki/summaries/business/permission/15_page_carrier_semantics.md
