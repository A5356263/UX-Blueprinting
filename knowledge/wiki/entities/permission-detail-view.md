# 权限明细视图

- page_id: PG-ENTITY-0001
- page_type: entity
- canonical_name: 权限明细视图
- aliases: [权限明细]
- status: stable
- confidence: medium
- source_refs: [SRC-BIZ-0009, SRC-BIZ-0010, SRC-BIZ-0012, SRC-BIZ-0021]
- related_pages:
  - knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md
  - knowledge/wiki/topics/permission-domain-index.md
- created_at: 2026-04-05
- updated_at: 2026-04-09

## 0. 文件定位

- 页面类型：Entity Page
- 对象名称：权限明细视图
- 对象类型：解释型下钻视图
- 适用范围：查询结果或详情页继续下钻时，用于查看更细粒度权限构成的视图
- 不处理内容：不承担配置提交，不替代 `权限查询` 或 `权限详情` 的入口职责

## 1. 结论

- 权限明细视图是解释链路中的下钻层，不是新的主配置页
- 在当前仓库语义中，它至少被两条链路引用：
  - `按用户查询结果 -> 权限明细`
  - `权限详情` 中的明细查阅区
- 它的目标是把应用级聚合结果进一步拆到菜单、功能点、数据范围等更细颗粒
- 当前仓库已明确其存在，但尚未补齐独立页面承载语义

## 2. 适用范围与边界

- 覆盖内容：明细下钻、只读解释、结果核对、审计查看
- 不覆盖内容：不直接改配置，不承担查询条件输入，不承担应用入口治理
- 易混淆对象：
  - `权限详情`
  - `按用户查询结果`
  - `功能授权`

## 3. 主体内容

### 3.1 对象职责

- 将按应用聚合的权限结果继续拆解为更细粒度的构成项
- 支持解释“这个应用里具体有哪些菜单、按钮、范围”
- 为审计、排障和结果核对提供最终只读证据层

### 3.2 关键状态

- [GAP] 当前未明确其独立页面类型、布局状态与关键交互状态
- 可合理推定其至少需要支持：
  - 当前应用上下文
  - 当前终端上下文
  - 当前权限身份或来源上下文

### 3.3 关键入口与出口

- 上游：
  - `按用户查询结果`
  - `权限详情`
- 下游：
  - [GAP] 暂未发现更深一级已明确的标准下钻对象

### 3.4 结构语义摘要

- 这是解释型而非配置型视图，Header 与 Info 区承担前置解释职责。
- 顶部先通过 Tab / Sub-Tab 切换权限身份与终端视角，再进入主体内容。
- Menu Left 承担业务模块导航，Main Content Right 承担权限明细解释，属于稳定的左右主从结构。
- Footer 仅承担关闭返回，不承接新的治理动作。

### 3.5 原始区块关系图保留

```text
Header
-> Info
-> Tab / Sub-Tab
-> Menu Left / Main Content Right
-> Footer
```

## 4. 关键关系

- 依赖对象：`权限查询`、`按用户查询结果`、`权限详情`
- 影响对象：体验蓝图中的解释链路、审计链路
- 相邻页面：
  - `knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md`
  - `knowledge/wiki/topics/permission-domain-index.md`

## 5. 证据与来源

- `knowledge/raw/business/permission/12_query_and_configuration_paths.md`
- `knowledge/raw/business/permission/13_route_map.md`
- `knowledge/raw/business/permission/15_page_carrier_semantics.md`
- `knowledge/raw/business/permission/32_copy_and_explanation_strategy.md`

## 6. 关联页面

- `knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md`
- `knowledge/wiki/topics/permission-domain-index.md`

## 7. 缺口与冲突

- [GAP] 独立页面语义尚未在现有事实中完整展开
- [GAP] 页面类型、模块结构、关键状态、导出能力尚待补齐
- [CONFLICT] 暂未发现直接冲突

## 8. 变更记录

- 日期：2026-04-05
- 变更：新增首版实体页
- 原因：补齐解释链路中被多次引用但未单独命名的下钻对象
