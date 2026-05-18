# Route Decision

- Project: `input-validation-full-self-permission-mode-conflict`
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

- source/task_card.md: Task Name: 自助权限申请模式冲突
- source/requirement.md: input 需求集合：自助权限申请
- source/background.md: 本样本来自 input 目录中的 自助权限申请 需求族，用于阶段三 run-routed-main 严格验收。
- runtime/task_card_resolved.json: {"task_id": "input-validation-full-self-permission-mode-conflict", "protocol_name": "UXB Test Task", "protocol_version":

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

- `business_capability_change`: `major` - 业务能力发生变化或扩展：本需求涉及功能新增、审批模式冲突、状态机重构、在途申请关闭策略、授权结果回写和审计治理
- `business_rule_change`: `medium` - 存在业务规则、校验或条件变化：需要明确不同模式优先级、关闭后的在途审批处理、失败补救和通知规则
- `permission_governance_risk`: `high` - 涉及权限、审批、数据范围、导出或治理风险：企业可能同时启用多种权限审批方式，员工申请可能与管理员授权流程交叉
- `task_flow_change`: `medium` - 用户任务路径、结果回写或角色协同可能变化：企业可能同时启用多种权限审批方式，员工申请可能与管理员授权流程交叉
- `information_structure_pressure`: `none` - 未发现明显信息结构或概念澄清压力
- `state_exception_pressure`: `high` - 状态、异常、阻断或校验会影响方案：本需求涉及功能新增、审批模式冲突、状态机重构、在途申请关闭策略、授权结果回写和审计治理
- `copy_comprehension_pressure`: `low` - 未发现文案理解是主要压力
- `layout_interaction_pressure`: `low` - 未发现布局交互是主要压力
- `review_risk`: `medium` - 存在评审误解、边界争议或待确认风险：产物必须承接当前需求正文中的关键边界，不外扩判断维度
