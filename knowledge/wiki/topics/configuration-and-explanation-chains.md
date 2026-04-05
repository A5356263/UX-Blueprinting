# 配置链路与解释链路专题

## 0. 文件定位

- 页面类型：Topic Page
- 专题名称：配置链路与解释链路专题
- 适用范围：权限域中的主配置路径、解释路径、外部治理路径及其职责分层
- 不处理内容：审批引擎内部实现、界面视觉细节、数据库路由

## 1. 结论

- 权限域至少存在三条必须拆开的链路：
  - 配置链路
  - 解释链路
  - 外部治理链路
- 配置链路负责改结果，解释链路负责说清结果，外部治理链路负责处理审批和跨模块协同
- 当前权限域最容易出问题的不是规则本身，而是把这三条链路写混

## 2. 适用范围与边界

- 覆盖问题：
  - 路由结构
  - 页面职责
  - 何时应该跳到外部治理模块
- 不覆盖问题：
  - 不定义每个页面的视觉结构
  - 不讨论脚本实现
  - 不替代单页语义文档
- 相关主题：
  - 查询页与配置页边界
  - 治理模式体系
  - 页面承载语义

## 3. 主体内容

### 3.1 专题目标

- 让后续任务在读到“授权”“查询”“审批”“应用设置”时，能快速判断当前处在哪条链路
- 避免体验蓝图把查询入口写成配置入口，或把外部治理链路写成权限域内闭环

### 3.2 结构分解

- 配置链路：
  - `用户授权 -> 功能授权 -> 数据授权`
  - `角色管理 -> 功能权限 / 数据权限 -> 授权规则`
  - `权限管理模式 -> 子管理配置页 / 双管理员模式配置页 / 权限变更审批模式配置页`
  - `应用管理 -> 应用设置页`
- 解释链路：
  - `用户授权 -> 权限详情`
  - `权限查询 -> 按用户查询结果 -> 权限明细`
- 外部治理链路：
  - `权限变更审批模式配置页 -> 审批管理 / 协同办公审批列表`
  - `应用设置页 -> 通用审批`
  - `功能授权 -> 应用中心`

### 3.3 关键结论

- 用户直授链路和角色模板链路都是配置链路，但面向对象不同
- `权限查询` 系列页面属于解释链路，不负责改配置
- 审批相关配置不在权限域内重造流程引擎，而是通过外部治理链路复用其他模块能力
- 某些页面会同时接触两条链路，例如 `应用设置页`，因此更需要语义拆分

### 3.4 适用与非适用场景

- 适用：
  - 做路由图
  - 做蓝图消费整理
  - 做页面职责核对
- 非适用：
  - 用来替代具体页面说明
  - 用来替代概念页

## 4. 关键关系

- 关联实体：
  - `knowledge/wiki/entities/permission-detail-view.md`
- 关联概念：
  - `knowledge/wiki/concepts/functional-permission.md`
  - `knowledge/wiki/concepts/governance-mode-system.md`
  - `knowledge/wiki/concepts/single-app-admin.md`
- 关联关系页：
  - `knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md`

## 5. 证据与来源

- `knowledge/business/permission/11_task_scenarios.md`
- `knowledge/business/permission/12_query_and_configuration_paths.md`
- `knowledge/business/permission/13_route_map.md`
- `knowledge/business/permission/15_page_carrier_semantics.md`

## 6. 关联页面

- `knowledge/wiki/topics/page-carrier-semantics-map.md`
- `knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md`
- `knowledge/wiki/indices/permission-domain.md`

## 7. 缺口与冲突

- [GAP] `数据授权` 链路仍因页面事实不足而存在结构性空白
- [GAP] 按角色查、按权限查、按功能点查的解释链路尚未补成完整闭环
- [CONFLICT] 暂未发现直接冲突

## 8. 变更记录

- 日期：2026-04-05
- 变更：新增首版专题页
- 原因：把权限域三类链路拆清，支撑后续上下文装配与蓝图消费
