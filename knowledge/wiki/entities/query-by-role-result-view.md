# 按角色查询结果页

- page_id: PG-ENTITY-0003
- page_type: entity
- canonical_name: 按角色查询结果页
- aliases: [按角色查结果页]
- status: draft
- confidence: low
- source_refs: [SRC-BIZ-0009, SRC-BIZ-0012]
- related_pages:
  - knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md
  - knowledge/wiki/entities/permission-detail-view.md
  - knowledge/wiki/topics/permission-domain-index.md
- created_at: 2026-04-09
- updated_at: 2026-04-09

## 0. 文件定位

- 页面类型：Entity Page
- 对象名称：按角色查询结果页
- 对象类型：查询结果型页面实体
- 适用范围：角色维度权限结果解释与下钻
- 不处理内容：不承担配置提交

## 1. 当前结论

- 该页属于查询链路结果承接对象。
- 当前事实仅能确认其应存在，未形成完整页面定义。
- 本页作为骨架用于后续 Raw 回填。

## 2. 骨架结构

- 查询条件回显区
- 结果列表区
- 权限明细下钻入口
- 导出与审计入口

## 3. 证据与来源

- `knowledge/raw/business/permission/12_query_and_configuration_paths.md`
- `knowledge/raw/business/permission/13_route_map.md`

## 4. 缺口与冲突

- [GAP] 结果字段定义缺失
- [GAP] 排序/筛选/分页规则缺失
- [CONFLICT] 暂未发现直接冲突
