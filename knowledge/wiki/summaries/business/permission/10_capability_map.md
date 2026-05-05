# 10_capability_map

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-10_CAPABILITY_MAP
- page_type: summary
- source_path: knowledge/raw/business/permission/10_capability_map.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-05
- updated_at: 2026-05-05
- source_refs: [knowledge/raw/business/permission/10_capability_map.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

从"能力域 -> 页面承载"角度，说明权限域中 6 个关键能力域分别由哪些页面承载，用于快速定位某个权限能力对应的页面入口。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 判断某个权限能力（如给用户开权限、配角色模板、开启子管理员）由哪个页面承载
- 评估能力覆盖与页面承载的对应关系是否完整
- 确认查询排障、协作可见性、应用级治理的能力边界
- 需要区分不同能力域的页面职责（配置 vs 查询 vs 治理）

## 3. 覆盖内容

本 raw 覆盖：

- 6 个能力域及其页面承载：用户直授（用户授权/功能授权/数据授权/权限详情）、角色授权（角色管理/授权规则）、全局治理（权限管理模式/子管理配置/双管理员模式/审批模式配置）、协作可见性（成员协作权限）、查询排障（权限查询/按用户查询结果）、应用级治理（应用管理/应用设置页）
- 边界规则：应用可见性不等于功能权限、功能权限不等于数据权限、协作可见性不等于管理授权、查询页不负责配置

不涉及：

- 各页面的详细语义描述（在 15_page_carrier_semantics 中定义）
- 任务场景的具体操作路径（在 11_task_scenarios 中定义）

## 4. 可直接使用的稳定结论

- 权限域共 6 个能力域：用户直授、角色授权、全局治理、协作可见性、查询排障、应用级治理
- 查询排障页负责解释与排障，不负责配置；协作可见性不等于管理授权
- 当前缺口：按权限查/按功能点查的现状承载仍待进一步核实

## 5. 必须回查 raw 的情况

以下情况不能只读 summary：

- 需要完整规则细节或精确条款时
- 需要正式证据或原文引用时
- 需要页面或流程的完整描述时
- 涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时
- summary 无法覆盖当前判断点或信息量不足时

## 6. 缺口 / 冲突 / 不确定项

- [GAP] 按权限查 / 按功能点查的现状承载仍待进一步核实

## 7. 邻近阅读

弱指向 3-5 个相关 summary。

- knowledge/wiki/summaries/business/permission/00_domain_overview.md
- knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
- knowledge/wiki/summaries/business/permission/02_glossary.md
- knowledge/wiki/summaries/business/permission/03_business_objects.md
- knowledge/wiki/summaries/business/permission/04_object_relations.md

> summary_path: knowledge/wiki/summaries/business/permission/10_capability_map.md
