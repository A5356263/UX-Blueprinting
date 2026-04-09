# 数据权限缺口待补清单

- page_id: PG-TOPIC-0004
- page_type: topic
- canonical_name: 数据权限缺口待补清单
- aliases: [data-permission-backlog]
- status: draft
- confidence: low
- source_refs: [SRC-BIZ-0008, SRC-BIZ-0009, SRC-BIZ-0012, SRC-BIZ-0015]
- related_pages:
  - knowledge/wiki/entities/data-authorization-page.md
  - knowledge/wiki/entities/query-by-role-result-view.md
  - knowledge/wiki/entities/query-by-permission-result-view.md
  - knowledge/wiki/entities/query-by-feature-result-view.md
  - knowledge/wiki/synthesis/permission-configuration-chain-synthesis.md
- created_at: 2026-04-09
- updated_at: 2026-04-09

## 待补对象

- 数据授权页
- 按角色查询结果页
- 按权限查询结果页
- 按功能点查询结果页

## 当前边界确认

- 数据权限相关概念与关系页已具备可消费基础。
- 当前主要缺口集中在“页面架构层信息”，包括页面结构、字段、交互流程与状态规则。
- 在 Raw 补齐上述真源前，相关实体页维持 `draft` 状态。

## 建议补充到 Raw 的真源项

- 数据授权页完整字段与交互流程
- 三类查询结果页的字段、筛选、排序、分页规则
- 查询结果到权限明细页的下钻规则
- 查询结果与导出/审计的联动规则
- 失败态、空态、无权限态与风险提示文案

## 回填后操作

- 先更新 `knowledge/raw/manifests/source_manifest.md`
- 再更新相关实体页状态为 `stable`
- 最后刷新 `wiki/synthesis/` 综合结论与 `wiki/log.md`
