# Route Decision

- Project: `full-permission-self-service`
- Version: `route-decision@1.0`
- Rules version: `route-decision-rules@1.0`
- Route: `full`
- Confidence: `high`
- Demand type: 权限与治理风险
- Business depth: `full`
- Should control mainline: `true`

## Reason

初判为权限与治理风险，主要压力在权限治理、流程承接、信息结构，涉及核心能力、治理或模型边界，需走完整链路。

## Evidence

- source/requirement.md: 员工缺少权限时只能联系管理员线下处理，过程不可追踪，也缺少审批记录。

## Design Pressure

- 权限治理
- 流程承接
- 信息结构
- 状态异常

## Escalation Signals

- 当前已建议 full，不建议自动降级。
- 如果后续事实证明范围更小，也应由人工确认后再调整，不自动改为 fast 或 standard。

## Dimension Judgment

- `business_capability_change`: `none` - 需求未表现出新增或重构能力，主要是既有能力内调整
- `business_rule_change`: `none` - 未发现明确业务规则变化信号
- `permission_governance_risk`: `high` - 涉及权限、审批、数据范围、导出或治理风险：涉及权限模型、审批治理、状态机、审计和敏感能力授权
- `task_flow_change`: `medium` - 用户任务路径、结果回写或角色协同可能变化：需要定义驳回、撤回、超时、审批人离职、权限冲突和权限到期
- `information_structure_pressure`: `medium` - 存在概念、入口、层级或模块边界压力：需要定义驳回、撤回、超时、审批人离职、权限冲突和权限到期
- `state_exception_pressure`: `high` - 状态、异常、阻断或校验会影响方案：涉及权限模型、审批治理、状态机、审计和敏感能力授权
- `copy_comprehension_pressure`: `low` - 未发现文案理解是主要压力
- `layout_interaction_pressure`: `low` - 未发现布局交互是主要压力
- `review_risk`: `low` - 当前信息未暴露明显评审风险
