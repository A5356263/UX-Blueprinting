# Route Decision

- Project: `real-input-checked-permission-filter`
- Version: `route-decision@1.0`
- Rules version: `route-decision-rules@1.0`
- Route: `standard`
- Confidence: `high`
- Demand type: 权限与治理风险
- Business depth: `lite`
- Should control mainline: `true`

## Reason

初判为权限与治理风险，主要压力在业务规则、权限治理、流程承接，需要保留业务边界判断后再转体验方案。

## Evidence

- source/requirement.md: 随着系统功能持续增加，功能权限设置页面的信息量越来越大。

## Design Pressure

- 业务规则
- 权限治理
- 流程承接
- 信息结构
- 评审风险

## Escalation Signals

- 后续发现新增核心业务能力、重构既有模块或改变业务对象关系时，需升级 full。
- 后续发现多角色协作闭环、权限模型、审批模式或状态机变化时，需升级 full。
- 后续 facts/business 出现关键 GAP，无法支撑体验方案时，需升级 full 或暂停确认。

## Dimension Judgment

- `business_capability_change`: `none` - 需求未表现出新增或重构能力，主要是既有能力内调整
- `business_rule_change`: `medium` - 存在业务规则、校验或条件变化：点击取消时，权限调整应按原有规则回退或关闭
- `permission_governance_risk`: `high` - 涉及权限、审批、数据范围、导出或治理风险：当权限管理员需要查看、核对或纠正员工已授权的功能权限时，需要在大量权限项中逐屏查找已勾选内容，效率较低，也容易遗漏
- `task_flow_change`: `medium` - 用户任务路径、结果回写或角色协同可能变化：新增筛选能力不改变原有授权流程
- `information_structure_pressure`: `medium` - 存在概念、入口、层级或模块边界压力：避免只展示末级名称导致权限归属不清
- `state_exception_pressure`: `none` - 未发现明显状态、异常或校验压力
- `copy_comprehension_pressure`: `low` - 用户理解主要依赖文案、说明或提示：| 空状态 | 当无已勾选权限时，需要展示空状态提示 |
- `layout_interaction_pressure`: `low` - 局部布局、展示或交互细节是明显压力：| 权限展示筛选 | 在功能权限设置区域支持切换“全部权限”和“已勾选权限” |
- `review_risk`: `medium` - 存在评审误解、边界争议或待确认风险：避免只展示末级名称导致权限归属不清
