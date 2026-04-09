# 数据权限

- page_id: PG-CONCEPT-0003
- page_type: concept
- canonical_name: 数据权限
- aliases: [数据范围权限]
- status: stable
- confidence: medium
- source_refs: [SRC-BIZ-0002, SRC-BIZ-0007, SRC-BIZ-0008, SRC-BIZ-0009, SRC-BIZ-0010, SRC-BIZ-0012, SRC-BIZ-0020]
- related_pages:
  - knowledge/wiki/concepts/functional-permission.md
  - knowledge/wiki/concepts/application-visibility.md
  - knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md
- created_at: 2026-04-05
- updated_at: 2026-04-09

## 0. 文件定位

- 页面类型：Concept Page
- 概念名称：数据权限
- 适用范围：权限域中与数据可见范围、资源作用域、部分/全部/无范围相关的授权语义
- 不处理内容：应用入口治理、成员协作可见性、审批流程引擎实现

## 1. 结论

- 数据权限回答的是“主体能对哪些数据生效”，而不是“主体能做哪些操作”
- 在当前仓库语义中，数据权限通常作为功能权限后的下一层配置，用于限定全量、部分或无数据范围
- 数据权限不能和功能权限合并叙述；二者分别解决“能不能做”和“能作用到哪里”
- 当前仓库已经明确数据权限在主链路中的角色，但数据授权页面本身的承载语义仍存在明显缺口

## 2. 适用范围与边界

- 定义边界：覆盖数据范围、数据作用域、数据访问边界
- 非目标：不覆盖菜单/按钮操作权，不覆盖应用图标是否可见，不覆盖成员间联系人可见性
- 常见误解：
  - 只要有某页面入口，就默认拥有对应数据范围
  - 角色或应用管理员身份天然包含全部数据权限
  - 查询结果页展示的数据覆盖面等于配置入口本身

## 3. 主体内容

### 3.1 概念定义

- 数据权限是对资源范围的授权约束
- 它通常承接在功能权限之后，用来回答主体对哪些组织、人员、记录或业务数据拥有可见、可处理或可管理范围
- 在当前权限域叙述中，数据权限结果至少应能表达全部、部分、无三类差异

### 3.2 判定规则

- 数据权限通常依赖已有功能权限语义；若没有对应功能点，数据范围配置往往没有独立意义
- 数据权限可在多条路径中出现：
  - `用户授权 -> 数据授权`
  - `角色管理 -> 数据权限`
  - `应用设置页 -> 用户授权区 -> 数据权限`
- 数据权限最终结果需要能被解释页或查询页核对，而不是只存在于配置时

### 3.3 与相近概念的区分

- 与功能权限的区分：
  - 功能权限管操作面
  - 数据权限管作用域
- 与应用可见性的区分：
  - 应用可见性管入口出现
  - 数据权限管进入后看多少、管多少
- 与成员协作可见性的区分：
  - 协作可见性管成员互相看见的信息边界
  - 数据权限管业务数据对象的可见和处理范围

## 4. 关键关系

- 上位概念：权限结果、范围约束、资源边界
- 下游对象：`数据授权`、`角色管理`、`应用设置页`、`权限详情`
- 常见组合关系：
  - 功能权限 + 数据权限
  - 角色模板 + 数据权限
  - 查询页/详情页 + 数据权限解释

## 5. 证据与来源

- `knowledge/raw/business/permission/00_domain_overview.md`
- `knowledge/raw/business/permission/10_capability_map.md`
- `knowledge/raw/business/permission/11_task_scenarios.md`
- `knowledge/raw/business/permission/12_query_and_configuration_paths.md`
- `knowledge/raw/business/permission/13_route_map.md`
- `knowledge/raw/business/permission/15_page_carrier_semantics.md`
- `knowledge/raw/business/permission/31_experience_translation_requirements.md`

## 6. 关联页面

- `knowledge/wiki/concepts/functional-permission.md`
- `knowledge/wiki/concepts/application-visibility.md`
- `knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md`
- `knowledge/wiki/topics/permission-domain-index.md`

## 7. 缺口与冲突

- [GAP] `数据授权` 页的页面类型、核心模块、关键状态、下游跳转尚未在现有材料中补齐
- [GAP] 当前知识中已明确数据权限是主链路一部分，但缺少完整页面事实，导致数据权限的具体配置承载还不能被完全结构化
- [CONFLICT] 暂未发现直接冲突，但若后续资料出现“功能权限已经隐含数据范围，无需单独表达”的说法，应视为与当前定义冲突

## 8. 变更记录

- 日期：2026-04-05
- 变更：新增首版概念页
- 原因：为权限域建立可复用的数据权限定义，并显式保留页面事实缺口
