# 15_page_carrier_semantics

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-15_PAGE_CARRIER_SEMANTICS
- page_type: summary
- source_path: knowledge/raw/business/permission/15_page_carrier_semantics.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-08
- updated_at: 2026-05-08
- source_refs: [knowledge/raw/business/permission/15_page_carrier_semantics.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

为权限域中 16 个关键页面逐一提供标准化的语义卡片（页面名、类型、入口角色、目标、核心模块、关键操作、关键状态、上下游入口、必须解释点、承载判断），用于判断每个页面在方案中应承担配置、查询、解释还是治理职责。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要理解某个权限页面的完整业务语义（目标、模块、操作、状态、出入口）
- 判断页面应使用 Page/Drawer/Modal 哪种承载形式
- 设计页面跳转关系时需要知道出入口和上下游
- 评估页面的解释能力是否满足用户理解需求
- 需要知道每个页面"必须解释的点"以指导体验设计

## 3. 覆盖内容

本 raw 覆盖：

- 16 个页面的语义卡片：用户授权、功能授权、数据授权、权限详情、角色管理、授权规则、权限管理模式、子管理员模式、子管理配置页、双管理员模式配置页、权限变更审批模式配置页、成员协作权限、权限查询、按用户查询结果、应用管理、应用设置页
- 每个页面包含：页面名、页面类型、菜单/功能位置、谁会进入、页面目标、核心模块、关键操作、关键状态、上游入口、下游跳转、必须解释的点、承载判断

不涉及：

- 视觉样式、组件皮肤、颜色尺寸间距、精确布局规格、容器实现概念、开发实现方案

## 4. 可直接使用的稳定结论

- 权限详情是解释页（Modal），只承担只读解释与核对，不承担配置权；权限查询和按用户查询结果是查询页（Page），负责排障与审计
- 功能授权和数据授权为 Drawer，从用户授权上下文中展开，避免让用户离开原有人员上下文
- 数据授权页的核心机制：平台统一采用"范围类型+条件组"计算模型，左侧索引树与功能授权强耦合（未授权功能点不展示），"仅显示未设置项"开关是防漏检机制
- 当前缺口：权限查询中按角色查/按权限查/按功能点查现状承载未核实，部分治理页下游跳转未明确，权限明细视图独立页面语义未展开

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
