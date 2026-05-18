# Route Decision

- Project: `input-validation-standard-self-permission-low`
- Version: `route-decision@1.0`
- Rules version: `route-decision-rules@1.0`
- Route: `full`
- Confidence: `high`
- Demand type: 权限与治理风险
- Business depth: `full`
- Should control mainline: `true`

## Reason

初判为权限与治理风险，主要压力在业务能力、业务规则、权限治理，涉及核心能力、治理或模型边界，需走完整链路。

## Evidence

- source/task_card.md: Task Name: 低完整度自助权限申请澄清
- source/requirement.md: input 需求集合：自助权限申请
- source/background.md: 本样本来自 input 目录中的 自助权限申请 需求族，用于阶段三 run-routed-main 严格验收。
- runtime/task_card_resolved.json: {"task_id": "input-validation-standard-self-permission-low", "protocol_name": "UXB Test Task", "protocol_version": "1.0"

## Design Pressure

- 业务能力
- 业务规则
- 权限治理
- 流程承接
- 状态异常

## Escalation Signals

- 当前已建议 full，不建议自动降级。
- 如果后续事实证明范围更小，也应由人工确认后再调整，不自动改为 fast 或 standard。

## Dimension Judgment

- `business_capability_change`: `major` - 业务能力发生变化或扩展：需要先输出轻量业务蓝图澄清规则和待确认问题，不直接进入完整新增能力设计
- `business_rule_change`: `medium` - 存在业务规则、校验或条件变化：需要先输出轻量业务蓝图澄清规则和待确认问题，不直接进入完整新增能力设计
- `permission_governance_risk`: `high` - 涉及权限、审批、数据范围、导出或治理风险：可申请权限范围、审批人和生效时机缺失
- `task_flow_change`: `medium` - 用户任务路径、结果回写或角色协同可能变化：交互流程总览
- `information_structure_pressure`: `none` - 未发现明显信息结构或概念澄清压力
- `state_exception_pressure`: `medium` - 状态、异常、阻断或校验会影响方案：需求只说明员工希望自助申请权限，但审批人、可申请范围和生效方式不清楚
- `copy_comprehension_pressure`: `low` - 用户理解主要依赖文案、说明或提示：需求只说明员工希望自助申请权限，但审批人、可申请范围和生效方式不清楚
- `layout_interaction_pressure`: `low` - 未发现布局交互是主要压力
- `review_risk`: `medium` - 存在评审误解、边界争议或待确认风险：需求只说明员工希望自助申请权限，但审批人、可申请范围和生效方式不清楚
