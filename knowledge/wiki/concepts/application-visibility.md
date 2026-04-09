# 应用可见性

- page_id: PG-CONCEPT-0001
- page_type: concept
- canonical_name: 应用可见性
- aliases: [应用入口可见性]
- status: stable
- confidence: medium
- source_refs: [SRC-BIZ-0007, SRC-BIZ-0008, SRC-BIZ-0009, SRC-BIZ-0010, SRC-BIZ-0012, SRC-BIZ-0020]
- related_pages:
  - knowledge/wiki/concepts/functional-permission.md
  - knowledge/wiki/concepts/data-permission.md
  - knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md
- created_at: 2026-04-05
- updated_at: 2026-04-09

## 0. 文件定位

- 页面类型：Concept Page
- 概念名称：应用可见性
- 适用范围：工作台入口、应用启停、端侧入口可见范围、单应用可见/禁用范围语义
- 不处理内容：应用内后台按钮权限、数据范围、成员协作可见性规则

## 1. 结论

- 应用可见性回答的是“某个主体能不能在前台看到并进入某个应用入口”，不是“进入后能管理什么”
- 在当前仓库语义中，应用可见性主要由 `应用管理` 和 `应用设置页` 承载，并可细化到电脑端、移动端及关联子功能
- 应用可见性与功能权限必须拆开表达；前者属于入口治理，后者属于应用内或后台管理能力治理
- 单应用页可以同时承载入口治理和应用管理员治理，因此需要特别防止把两类语义混写

## 2. 适用范围与边界

- 定义边界：覆盖应用是否可见、是否启用、对哪些人群可见、在什么端可见
- 非目标：不覆盖进入应用后的后台菜单操作权，不覆盖数据范围配置，不覆盖审批流本身
- 常见误解：
  - 看得到应用就等于有后台管理权
  - 应用停用只影响某个角色，不影响全员入口
  - 单应用设置页中的“用户授权”就是前台入口可见性

## 3. 主体内容

### 3.1 概念定义

- 应用可见性是对应用入口层的治理
- 它控制主体是否能在企业工作台或门户中看到某个应用及其关联子功能
- 在当前权限域中，它既包含全局台账层的治理，也包含单应用层的精细化可见/禁用范围设置

### 3.2 判定规则

- 应用可见性主要通过以下路径承载：
  - `应用管理`：查看和治理应用台账、启停状态、可见范围
  - `应用设置页`：配置单应用及其关联功能的可见范围和禁用范围
- 应用可见性可带端差异：
  - 电脑端可见
  - 移动端可见
  - 双端不同策略
- 停用应用属于高影响范围动作，会影响全员或大范围前台入口可见性

### 3.3 与相近概念的区分

- 与功能权限的区分：
  - 应用可见性管“能不能看到入口”
  - 功能权限管“进来后能做什么”
- 与数据权限的区分：
  - 应用可见性不回答数据范围
  - 数据权限不回答入口是否出现
- 与协作可见性的区分：
  - 协作可见性解决成员之间信息是否互见
  - 应用可见性解决应用入口对哪些主体暴露

## 4. 关键关系

- 上位概念：入口治理、应用生命周期、端差异
- 下游对象：`应用管理`、`应用设置页`
- 常见组合关系：
  - 应用可见性 + 应用启停
  - 应用可见性 + 单应用管理员治理
  - 应用可见性 + 跨模块引流

## 5. 证据与来源

- `knowledge/raw/business/permission/10_capability_map.md`
- `knowledge/raw/business/permission/11_task_scenarios.md`
- `knowledge/raw/business/permission/12_query_and_configuration_paths.md`
- `knowledge/raw/business/permission/13_route_map.md`
- `knowledge/raw/business/permission/15_page_carrier_semantics.md`
- `knowledge/raw/business/permission/31_experience_translation_requirements.md`

## 6. 关联页面

- `knowledge/wiki/concepts/functional-permission.md`
- `knowledge/wiki/concepts/data-permission.md`
- `knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md`
- `knowledge/wiki/topics/permission-domain-index.md`

## 7. 缺口与冲突

- [GAP] 当前知识已明确应用可见性和后台管理权限分离，但还未沉淀独立的“单应用管理员”概念页
- [GAP] 应用可见性与应用市场/开发者后台之间的边界尚未单独整理为关系页
- [CONFLICT] 暂未发现直接冲突，但若后续材料把“应用设置页中的用户授权”直接等同于“前台入口可见性”，应视为与当前定义冲突

## 8. 变更记录

- 日期：2026-04-05
- 变更：新增首版概念页
- 原因：为权限域建立可复用的应用入口治理定义，并与功能/数据权限解耦
