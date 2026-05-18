# Route Decision

- Project: `boundary-extension-state-machine`
- Version: `route-decision@1.0`
- Rules version: `route-decision-rules@1.0`
- Route: `full`
- Confidence: `medium`
- Demand type: 功能重构
- Business depth: `full`
- Should control mainline: `true`

## Reason

初判为功能重构，主要压力在业务规则、信息结构、状态异常，涉及核心能力、治理或模型边界，需走完整链路。

## Evidence

- source/requirement.md: 在审批详情页新增暂缓处理能力，暂缓后申请单保持在当前审批人处，后续可继续审批。

## Design Pressure

- 业务规则
- 信息结构
- 状态异常

## Escalation Signals

- 当前已建议 full，不建议自动降级。
- 如果后续事实证明范围更小，也应由人工确认后再调整，不自动改为 fast 或 standard。

## Dimension Judgment

- `business_capability_change`: `none` - 需求未表现出新增或重构能力，主要是既有能力内调整
- `business_rule_change`: `medium` - 存在业务规则、校验或条件变化：涉及审批状态机变化、审批时效、待办状态和通知规则
- `permission_governance_risk`: `none` - 未发现权限、审批、数据范围或治理变化
- `task_flow_change`: `none` - 未发现主任务路径变化
- `information_structure_pressure`: `medium` - 存在概念、入口、层级或模块边界压力：需要定义暂缓次数、超时规则、申请人是否可见、管理员是否可催办
- `state_exception_pressure`: `high` - 状态、异常、阻断或校验会影响方案：涉及审批状态机变化、审批时效、待办状态和通知规则
- `copy_comprehension_pressure`: `low` - 未发现文案理解是主要压力
- `layout_interaction_pressure`: `low` - 局部布局、展示或交互细节是明显压力：费用审批希望增加“暂缓处理”按钮，让审批人可以先不通过也不驳回
- `review_risk`: `low` - 当前信息未暴露明显评审风险
