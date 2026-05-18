# Route Decision

- Project: `full-org-module-refactor`
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

- source/requirement.md: 当前组织模块同时承载部门、法律实体、成本中心和虚拟团队，概念混用导致权限、统计和审批范围经常理解不一致。

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

- `business_capability_change`: `major` - 业务能力发生变化或扩展：重构组织模块的信息模型，明确组织、法律实体、成本中心和虚拟团队的对象关系，并调整页面入口
- `business_rule_change`: `medium` - 存在业务规则、校验或条件变化：当前组织模块同时承载部门、法律实体、成本中心和虚拟团队，概念混用导致权限、统计和审批范围经常理解不一致
- `permission_governance_risk`: `high` - 涉及权限、审批、数据范围、导出或治理风险：影响组织管理、成员绑定、权限范围、审批范围和报表统计口径
- `task_flow_change`: `none` - 未发现主任务路径变化
- `information_structure_pressure`: `medium` - 存在概念、入口、层级或模块边界压力：当前组织模块同时承载部门、法律实体、成本中心和虚拟团队，概念混用导致权限、统计和审批范围经常理解不一致
- `state_exception_pressure`: `none` - 未发现明显状态、异常或校验压力
- `copy_comprehension_pressure`: `low` - 未发现文案理解是主要压力
- `layout_interaction_pressure`: `low` - 未发现布局交互是主要压力
- `review_risk`: `medium` - 存在评审误解、边界争议或待确认风险：涉及权限范围、审批范围、数据统计范围和核心概念边界
