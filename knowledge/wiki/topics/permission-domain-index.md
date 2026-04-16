# 权限域索引

- page_id: PG-INDEX-0001
- page_type: index
- canonical_name: 权限域索引
- aliases: [permission-domain-index]
- status: stable
- confidence: high
- source_refs: [SRC-BIZ-0002, SRC-BIZ-0007, SRC-BIZ-0008, SRC-BIZ-0009, SRC-BIZ-0010, SRC-BIZ-0012, SRC-BIZ-0020]
- related_pages:
  - knowledge/wiki/index.md
  - knowledge/wiki/topics/page-carrier-semantics-map.md
  - knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md
- created_at: 2026-04-05
- updated_at: 2026-04-09

## 0. 文件定位

- 页面类型：Index Page
- 页面名称：权限域索引
- 适用范围：为权限域的 Wiki 页面、业务知识包和阅读路径提供统一导航
- 不处理内容：不作为权限规则真源，不替代业务蓝图或体验蓝图

## 1. 结论

- 权限域是一个同时覆盖可见性、功能权限、数据范围、治理模式、查询解释与审计闭环的复合领域
- 当前仓库最适合把权限域拆成“概念页 + 关系页 + 专题页 + 原始业务知识包”的组合，而不是把所有内容塞进单篇长文
- 后续任务在装配上下文时，应优先从本索引页进入，再按任务目标选择概念页、关系页和业务知识文件

## 2. 适用范围与边界

- 覆盖问题：
  - 权限域有哪些核心主题
  - 哪些页面或文件适合作为入口阅读
  - 当前 Wiki 已经覆盖到哪里
- 不覆盖问题：
  - 不直接定义具体授权规则
  - 不直接承接任务输出
  - 不替代页面承载语义细节
- 相关主题：
  - 功能权限
  - 数据权限
  - 应用可见性
  - 查询与配置边界
  - 页面承载语义

## 3. 主体内容

### 3.1 领域入口

- 领域总览：
  - `knowledge/raw/business/permission/00_domain_overview.md`
- 能力与场景：
  - `knowledge/raw/business/permission/10_capability_map.md`
  - `knowledge/raw/business/permission/11_task_scenarios.md`
  - `knowledge/raw/business/permission/12_query_and_configuration_paths.md`
  - `knowledge/raw/business/permission/13_route_map.md`
  - `knowledge/raw/business/permission/15_page_carrier_semantics.md`
- 体验转译：
  - `knowledge/raw/business/permission/31_experience_translation_requirements.md`

### 3.2 当前 Wiki 页面

- 概念页：
  - `knowledge/wiki/concepts/functional-permission.md`
  - `knowledge/wiki/concepts/data-permission.md`
  - `knowledge/wiki/concepts/application-visibility.md`
  - `knowledge/wiki/concepts/role-template-authorization.md`
  - `knowledge/wiki/concepts/collaboration-visibility.md`
  - `knowledge/wiki/concepts/governance-mode-system.md`
  - `knowledge/wiki/concepts/single-app-admin.md`
- 实体页：
  - `knowledge/wiki/entities/permission-detail-view.md`
- 关系页：
  - `knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md`
- 专题页：
  - `knowledge/wiki/topics/page-carrier-semantics-map.md`
  - `knowledge/wiki/topics/configuration-and-explanation-chains.md`

### 3.3 推荐阅读顺序

- 如果目标是理解权限域总边界：
  - 先读 `00_domain_overview`
  - 再读本索引页
  - 再读三个概念页
- 如果目标是做页面承载或体验转译：
  - 先读 `15_page_carrier_semantics`
  - 再读 `31_experience_translation_requirements`
  - 再读“查询页与配置页边界”关系页
- 如果目标是做任务排障或路由分析：
  - 先读 `12_query_and_configuration_paths`
  - 再读 `13_route_map`
  - 再读相关概念页

### 3.4 当前覆盖与缺口

- 已覆盖：
  - 功能权限定义
  - 数据权限定义
  - 应用可见性定义
  - 角色模板化授权
  - 协作可见性
  - 治理模式体系
  - 单应用管理员治理
  - 权限明细下钻对象
  - 查询页与配置页边界
- 尚待补充：
  - 角色查询闭环
  - 按权限查 / 按功能点查结果承载
  - 数据授权页面事实
  - 更细粒度的原因码与状态示例

### 3.5 页面结构语义入口

- 页面结构语义的正式消费入口是 `knowledge/wiki/topics/page-carrier-semantics-map.md`
- 体验阶段若要判断结构变化 / 结构不变，应优先消费该专题页中的结构语义摘要与原始区块关系图保留
- 当前权限域已至少保留以下结构判断依据：
  - 用户授权：Filter / Action / Main / Footer 的工作台顺序
  - 功能授权：Header / Step / Alert 在上，Menu Left 与 Main Config Right 并列
  - 角色管理：Left 角色索引在左，Right 成员治理主区在右
  - 权限详情：Info / Tab 在上，Menu Left 与 Main Content Right 构成解释型左右布局

## 4. 关键关系

- 关联实体：`用户授权`、`角色管理`、`权限查询`、`应用管理`、`应用设置页`
- 关联概念：功能权限、数据权限、应用可见性
- 关联关系页：查询页与配置页边界

## 5. 证据与来源

- `knowledge/raw/business/permission/README.md`
- `knowledge/raw/business/permission/00_domain_overview.md`
- `knowledge/raw/business/permission/10_capability_map.md`
- `knowledge/raw/business/permission/11_task_scenarios.md`
- `knowledge/raw/business/permission/12_query_and_configuration_paths.md`
- `knowledge/raw/business/permission/13_route_map.md`
- `knowledge/raw/business/permission/15_page_carrier_semantics.md`
- `knowledge/raw/business/permission/31_experience_translation_requirements.md`

## 6. 关联页面

- `knowledge/wiki/concepts/functional-permission.md`
- `knowledge/wiki/concepts/data-permission.md`
- `knowledge/wiki/concepts/application-visibility.md`
- `knowledge/wiki/concepts/role-template-authorization.md`
- `knowledge/wiki/concepts/collaboration-visibility.md`
- `knowledge/wiki/concepts/governance-mode-system.md`
- `knowledge/wiki/concepts/single-app-admin.md`
- `knowledge/wiki/entities/permission-detail-view.md`
- `knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md`
- `knowledge/wiki/topics/page-carrier-semantics-map.md`
- `knowledge/wiki/topics/configuration-and-explanation-chains.md`

## 7. 缺口与冲突

- [GAP] 数据授权页页面语义未补齐，导致“数据权限”相关页仍带结构性缺口
- [GAP] 按角色查、按权限查、按功能点查的结果承载尚未核实完全
- [GAP] 当前 Wiki 已具备首批可用导航，但仍未形成所有查询入口的闭环
- [CONFLICT] 暂未发现直接冲突

## 8. 变更记录

- 日期：2026-04-05
- 变更：新增首版索引页
- 原因：为权限域建立 Wiki 入口与阅读顺序
