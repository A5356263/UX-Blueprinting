# 查询页与配置页边界

- page_id: PG-RELATION-0001
- page_type: relation
- canonical_name: 查询页与配置页边界
- aliases: [查询配置边界]
- status: stable
- confidence: high
- source_refs: [SRC-BIZ-0007, SRC-BIZ-0008, SRC-BIZ-0009, SRC-BIZ-0010, SRC-BIZ-0012, SRC-BIZ-0020]
- related_pages:
  - knowledge/wiki/concepts/functional-permission.md
  - knowledge/wiki/concepts/data-permission.md
  - knowledge/wiki/concepts/application-visibility.md
- created_at: 2026-04-05
- updated_at: 2026-04-09

## 0. 文件定位

- 页面类型：Relation Page
- 关系主题：查询页与配置页的职责边界
- 适用范围：权限域中“解释/排障”与“实际配置/治理”两类页面的区分
- 不处理内容：具体视觉布局、交互控件皮肤、查询引擎实现方式

## 1. 结论

- 查询页负责解释和排障，配置页负责改变权限结果；两者不能混写
- 在当前权限域中，`权限查询`、`按用户查询结果`、`权限详情` 的主职责是解释当前结果，而 `用户授权`、`角色管理`、`权限管理模式`、`应用设置页` 的主职责是改动配置
- 查询链路可以下钻到更细明细，但不应直接承担高风险治理动作
- 当体验蓝图或页面语义层描述权限域时，必须显式区分“结果解释入口”和“配置入口”

## 2. 适用范围与边界

- 关系双方：
  - 查询页：`权限查询`、`按用户查询结果`、`权限详情`
  - 配置页：`用户授权`、`角色管理`、`权限管理模式`、`成员协作权限`、`应用管理`、`应用设置页`
- 关系类型：职责边界、信息流上下游、风险分层
- 不讨论内容：查询接口设计、数据库索引、权限计算引擎

## 3. 主体内容

### 3.1 联系点

- 二者都围绕“最终权限结果”工作
- 配置页负责生成或改变结果
- 查询页负责解释、核对、排障、审计当前结果
- 典型链路会形成“配置 -> 生效 -> 查询/解释”的前后关系

### 3.2 差异点

- 职责差异：
  - 查询页回答“为什么有/为什么没有/来自哪里/何时生效”
  - 配置页回答“要给谁改什么/在哪改/通过什么治理模式改”
- 风险差异：
  - 查询页以只读、穿透、核对为主
  - 配置页承载授权、移除、启停、治理模式切换等高风险动作
- 承载差异：
  - 查询页偏向检索、聚合、下钻、解释
  - 配置页偏向编辑、选择、确认、提交

### 3.3 选择条件

- 当用户任务是“查原因、查结果、做审计、做排障”时，应优先进入查询页链路
- 当用户任务是“授予、移除、修改、启停、切换治理模式”时，应优先进入配置页链路
- 当用户需要先查再改时，应保持两个页面角色清晰，不在查询页中偷渡配置职责

### 3.4 常见混淆与纠偏

- 混淆一：把 `权限详情` 当作配置页
  - 纠偏：`权限详情` 是只读解释页，承担核对和教育作用
- 混淆二：把 `权限查询` 当作统一配置入口
  - 纠偏：`权限查询` 负责穿透式检索，不承担授权修改
- 混淆三：把 `应用设置页` 误当成纯查询页
  - 纠偏：`应用设置页` 虽有说明性信息，但本质是单应用治理页

## 4. 关键关系

- 上游概念：功能权限、数据权限、应用可见性
- 下游影响：体验蓝图中的页面定位、页面类型选择、风险提示设计
- 相邻关系页：
  - `knowledge/wiki/concepts/functional-permission.md`
  - `knowledge/wiki/concepts/data-permission.md`
  - `knowledge/wiki/concepts/application-visibility.md`

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
- `knowledge/wiki/concepts/application-visibility.md`
- `knowledge/wiki/topics/permission-domain-index.md`

## 7. 缺口与冲突

- [GAP] 按角色查、按权限查、按功能点查的结果页承载尚未完全核实，因此查询页体系还不完整
- [GAP] `权限明细视图` 目前只作为下钻对象被提及，尚未沉淀独立页面语义
- [CONFLICT] 暂未发现直接冲突，但若后续有页面试图把查询结果页与配置页合并为一个统一工作台，需要重新核实是否违背当前权限域边界

## 8. 变更记录

- 日期：2026-04-05
- 变更：新增首版关系页
- 原因：为权限域明确查询链路与配置链路的职责分层
