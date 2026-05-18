# Route Decision

- Project: `standard-approval-status-filter`
- Version: `route-decision@1.0`
- Rules version: `route-decision-rules@1.0`
- Route: `standard`
- Confidence: `medium`
- Demand type: 文案与信息表达优化
- Business depth: `lite`
- Should control mainline: `true`

## Reason

初判为文案与信息表达优化，主要压力在信息结构、状态异常，需要保留业务边界判断后再转体验方案。

## Evidence

- source/requirement.md: 新增审批状态筛选，支持按待处理、处理中、已完成、已失效筛选。

## Design Pressure

- 信息结构
- 状态异常

## Escalation Signals

- 后续发现新增核心业务能力、重构既有模块或改变业务对象关系时，需升级 full。
- 后续发现多角色协作闭环、权限模型、审批模式或状态机变化时，需升级 full。
- 后续 facts/business 出现关键 GAP，无法支撑体验方案时，需升级 full 或暂停确认。

## Dimension Judgment

- `business_capability_change`: `none` - 需求未表现出新增或重构能力，主要是既有能力内调整
- `business_rule_change`: `none` - 未发现明确业务规则变化信号
- `permission_governance_risk`: `none` - 未发现权限、审批、数据范围或治理变化
- `task_flow_change`: `none` - 未发现主任务路径变化
- `information_structure_pressure`: `medium` - 存在概念、入口、层级或模块边界压力：需要定义每个状态的业务含义，以及筛选后无结果时的说明
- `state_exception_pressure`: `medium` - 状态、异常、阻断或校验会影响方案：新增审批状态筛选，支持按待处理、处理中、已完成、已失效筛选
- `copy_comprehension_pressure`: `low` - 用户理解主要依赖文案、说明或提示：影响审批列表筛选条件、状态说明和空状态文案
- `layout_interaction_pressure`: `low` - 未发现布局交互是主要压力
- `review_risk`: `low` - 当前信息未暴露明显评审风险
