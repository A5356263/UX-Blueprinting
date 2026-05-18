# Route Decision

- Project: `full-member-group-role-refactor`
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

- source/requirement.md: 当前成员组既用于组织分组，又用于权限授权范围，和角色关系混杂，导致管理员无法判断成员组变更会影响哪些权限。

## Design Pressure

- 业务能力
- 业务规则
- 权限治理
- 信息结构
- 评审风险

## Escalation Signals

- 当前已建议 full，不建议自动降级。
- 如果后续事实证明范围更小，也应由人工确认后再调整，不自动改为 fast 或 standard。

## Dimension Judgment

- `business_capability_change`: `major` - 业务能力发生变化或扩展：重构成员组与角色的关系，明确成员组用于对象集合，角色用于能力集合，授权关系单独管理
- `business_rule_change`: `medium` - 存在业务规则、校验或条件变化：当前成员组既用于组织分组，又用于权限授权范围，和角色关系混杂，导致管理员无法判断成员组变更会影响哪些权限
- `permission_governance_risk`: `high` - 涉及权限、审批、数据范围、导出或治理风险：涉及权限模型、角色边界、成员范围和审计记录
- `task_flow_change`: `none` - 未发现主任务路径变化
- `information_structure_pressure`: `medium` - 存在概念、入口、层级或模块边界压力：当前成员组既用于组织分组，又用于权限授权范围，和角色关系混杂，导致管理员无法判断成员组变更会影响哪些权限
- `state_exception_pressure`: `none` - 未发现明显状态、异常或校验压力
- `copy_comprehension_pressure`: `low` - 未发现文案理解是主要压力
- `layout_interaction_pressure`: `low` - 未发现布局交互是主要压力
- `review_risk`: `medium` - 存在评审误解、边界争议或待确认风险：涉及权限模型、角色边界、成员范围和审计记录
