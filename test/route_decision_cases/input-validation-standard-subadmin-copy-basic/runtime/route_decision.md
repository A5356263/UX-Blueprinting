# Route Decision

- Project: `input-validation-standard-subadmin-copy-basic`
- Version: `route-decision@2.0`
- Status: `confirmed`
- Source: `uxb_ai_judgment`
- Confirmed by user: `true`
- Can execute mainline: `true`
- Route: `standard`
- Demand type: 子管理员权限复制
- Business depth: `lite`

## Reason

支持把一个子管理员的可授权组织和功能权限复制给多个目标用户。

## Evidence

- 复制来源是已有子管理员。
- 目标用户可以多选。
- 复制结果需要区分成功、失败和跳过。

## Design Pressure

- 业务能力
- 业务规则
- 权限治理
- 流程承接
- 状态异常

## Validation Errors

- none

## Risk Notes

- 当前需求可能涉及权限、数据范围、审批或治理边界，不应被直接当作纯局部体验优化。
- 当前需求可能改变业务规则、限制或校验，建议先确认规则边界。
- 当前需求可能改变状态、异常或阻断逻辑，建议先确认状态含义和失败处理。
- 当前需求存在明显待确认边界，UXB 需要先和用户确认关键问题。

## Guardrail Hints

- `business_capability_change`: `minor` - 业务能力发生变化或扩展：在既有子管理员授权能力上扩展复制能力，涉及批量选择、复制预览、目标用户校验、部分成功和失败反馈
- `business_rule_change`: `medium` - 存在业务规则、校验或限制变化：在既有子管理员授权能力上扩展复制能力，涉及批量选择、复制预览、目标用户校验、部分成功和失败反馈
- `permission_governance_risk`: `high` - 涉及权限、审批、数据范围、导出或治理风险：支持把一个子管理员的可授权组织和功能权限复制给多个目标用户
- `task_flow_change`: `medium` - 用户任务路径、结果回写或角色协同可能变化：交互流程总览
- `information_structure_pressure`: `none` - 未发现明显的信息结构压力
- `state_exception_pressure`: `medium` - 状态、异常、阻断或校验会影响方案：在既有子管理员授权能力上扩展复制能力，涉及批量选择、复制预览、目标用户校验、部分成功和失败反馈
- `copy_comprehension_pressure`: `low` - 未发现文案理解是主要压力
- `layout_interaction_pressure`: `low` - 未发现布局交互是主要压力
- `review_risk`: `medium` - 存在边界争议、误解风险或待确认项：产物必须承接当前需求正文中的关键边界，不外扩判断维度
