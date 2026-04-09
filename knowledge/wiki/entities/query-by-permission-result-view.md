# 按权限查询结果页

- page_id: PG-ENTITY-0004
- page_type: entity
- canonical_name: 按权限查询结果页
- aliases: [按权限查结果页]
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
- 对象名称：按权限查询结果页
- 对象类型：查询结果型页面实体
- 适用范围：权限项维度结果解释与定位
- 不处理内容：不承担配置提交

## 1. 当前结论

- 该页用于承接“按权限”维度查询结果。
- 现有事实不足以支撑完整结构定义，先保留骨架。

## 2. 骨架结构

- 查询条件回显区
- 权限项结果区
- 角色/用户关联下钻入口
- 导出与审计入口

## 3. 证据与来源

- `knowledge/raw/business/permission/12_query_and_configuration_paths.md`
- `knowledge/raw/business/permission/13_route_map.md`

## 4. 缺口与冲突

- [GAP] 结果字段与维度映射缺失
- [GAP] 关联对象跳转规则缺失
- [CONFLICT] 暂未发现直接冲突
