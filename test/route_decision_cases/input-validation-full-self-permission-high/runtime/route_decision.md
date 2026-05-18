# Route Decision

- Project: `input-validation-full-self-permission-high`
- Version: `route-decision@2.0`
- Status: `confirmed`
- Source: `uxb_ai_judgment`
- Confirmed by user: `true`
- Can execute mainline: `true`
- Route: `full`
- Demand type: 自助权限申请
- Business depth: `full`

## Reason

设计员工自助申请权限的完整业务和体验闭环。

## Evidence

- 员工是申请方。
- 审批人处理申请。
- 管理员配置可申请范围。

## Design Pressure

- 业务规则
- 权限治理
- 流程承接
- 状态异常
- 评审风险

## Validation Errors

- none

## Risk Notes

- 当前需求可能涉及权限、数据范围、审批或治理边界，不应被直接当作纯局部体验优化。
- 当前需求可能改变业务规则、限制或校验，建议先确认规则边界。
- 当前需求可能改变状态、异常或阻断逻辑，建议先确认状态含义和失败处理。
- 当前需求存在明显待确认边界，UXB 需要先和用户确认关键问题。

## Guardrail Hints

- `business_capability_change`: `none` - 未发现新增或重构能力，更像现有能力内调整
- `business_rule_change`: `medium` - 存在业务规则、校验或限制变化：只依据 source 中的真实需求片段和背景，不引入无来源的新业务范围
- `permission_governance_risk`: `high` - 涉及权限、审批、数据范围、导出或治理风险：本需求是新增核心业务能力，涉及员工申请、管理员配置可申请范围、审批模式、审批状态机、自动授权、生效回写、撤回、拒绝、通知、审计和异常补救
- `task_flow_change`: `medium` - 用户任务路径、结果回写或角色协同可能变化：交互流程总览
- `information_structure_pressure`: `none` - 未发现明显的信息结构压力
- `state_exception_pressure`: `high` - 状态、异常、阻断或校验会影响方案：本需求是新增核心业务能力，涉及员工申请、管理员配置可申请范围、审批模式、审批状态机、自动授权、生效回写、撤回、拒绝、通知、审计和异常补救
- `copy_comprehension_pressure`: `low` - 未发现文案理解是主要压力
- `layout_interaction_pressure`: `low` - 未发现布局交互是主要压力
- `review_risk`: `medium` - 存在边界争议、误解风险或待确认项：可申请范围和审批模式不清会导致越权申请
