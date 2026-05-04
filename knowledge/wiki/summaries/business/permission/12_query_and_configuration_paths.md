# 12_query_and_configuration_paths

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-12_QUERY_AND_CONFIGURATION_PATHS
- page_type: summary
- source_path: knowledge/raw/business/permission/12_query_and_configuration_paths.md
- source_group: business
- status: active
- confidence: medium
- updated_at: 2026-05-04
- source_refs: [knowledge/raw/business/permission/12_query_and_configuration_paths.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

> 权限域必须同时说明查询路径与配置路径；即使现状承载分散，也要显式写出当前承载、边界与缺口。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要理解或使用本业务域的知识进行方案设计或判断时

## 3. 覆盖内容

本 raw 覆盖：

- 风险：3. 现状缺口
- 章节：1. 查询路径, 2. 配置路径

不涉及：

- 本 raw 未显式覆盖的内容需回查其他相关 raw 或补充来源

## 4. 可直接使用的稳定结论

- 语义：查询某个用户当前有什么权限、来源是什么、为什么可用或不可用
- `权限查询`：提供按用户的查询入口
- `按用户查询结果`：按应用聚合展示查询结果
- `权限详情`：补充只读明细解释
- 可行性：`feasible`
- 语义：查询某个角色拥有哪些成员、拥有哪些权限模板

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
