# 数据授权页

- page_id: PG-ENTITY-0002
- page_type: entity
- canonical_name: 数据授权页
- aliases: [数据权限配置页]
- status: draft
- confidence: low
- source_refs: [SRC-BIZ-0008, SRC-BIZ-0009, SRC-BIZ-0015]
- related_pages:
  - knowledge/wiki/concepts/data-permission.md
  - knowledge/wiki/topics/permission-domain-index.md
  - knowledge/wiki/synthesis/permission-configuration-chain-synthesis.md
- created_at: 2026-04-09
- updated_at: 2026-04-09

## 0. 文件定位

- 页面类型：Entity Page
- 对象名称：数据授权页
- 对象类型：配置型页面实体
- 适用范围：数据权限规则的配置、变更与治理
- 不处理内容：不承担查询结果解释，不替代功能授权配置

## 1. 当前结论

- 数据授权页属于配置链路的核心承载对象。
- 当前仓库对其入口、字段、策略类型、保存流程尚未形成完整事实。
- 本页先作为骨架承接，等待 Raw 补充后再升级到 stable。

## 2. 骨架结构

### 2.1 页面职责骨架

- 配置数据可见范围
- 配置组织/角色/人员的数据访问条件
- 提供变更提交与审计关联入口

### 2.2 待补字段骨架

- 数据对象类型
- 授权作用域
- 条件表达式
- 生效周期
- 冲突处理策略

### 2.3 待补流程骨架

- 进入入口
- 配置步骤
- 审批路径
- 生效反馈
- 回滚策略

## 3. 证据与来源

- `knowledge/raw/business/permission/11_task_scenarios.md`
- `knowledge/raw/business/permission/12_query_and_configuration_paths.md`
- `knowledge/raw/business/permission/15_page_carrier_semantics.md`

## 4. 缺口与冲突

- [GAP] 缺少数据授权页的完整原始事实描述
- [GAP] 缺少字段级与策略级真源样例
- [CONFLICT] 暂未发现直接冲突
