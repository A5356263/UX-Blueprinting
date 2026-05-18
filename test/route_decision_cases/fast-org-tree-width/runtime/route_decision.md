# Route Decision

- Project: `fast-org-tree-width`
- Version: `route-decision@2.0`
- Status: `confirmed`
- Source: `uxb_ai_judgment`
- Confirmed by user: `true`
- Can execute mainline: `true`
- Route: `fast`
- Demand type: 布局交互优化
- Business depth: `note`

## Reason

这次主要影响组织树的页面表现和交互边界，不改变权限、审批、数据范围或业务规则，适合按局部体验优化处理。

## Evidence

- 需求只要求支持拖动组织树宽度并记住当前浏览器偏好。
- 约束里明确不新增组织、成员、角色或权限能力。

## Design Pressure

- 布局交互

## Validation Errors

- none

## Risk Notes

- 如果后续发现影响数据范围、权限边界或结果状态，需要重新判断。

## Guardrail Hints

- `business_capability_change`: `none` - 未发现新增或重构能力，更像现有能力内调整
- `business_rule_change`: `none` - 未发现明确的业务规则变化
- `permission_governance_risk`: `none` - 未发现权限、审批或治理风险变化
- `task_flow_change`: `none` - 未发现任务路径变化
- `information_structure_pressure`: `medium` - 存在概念、入口、层级或模块边界压力：需要定义最小宽度、最大宽度、长部门名称展示和窗口缩小时的响应方式
- `state_exception_pressure`: `none` - 未发现明显的状态或异常压力
- `copy_comprehension_pressure`: `low` - 未发现文案理解是主要压力
- `layout_interaction_pressure`: `low` - 局部布局、展示或交互细节是明显压力：测试 fast 路线下局部布局交互优化
- `review_risk`: `medium` - 存在边界争议、误解风险或待确认项：experience 承接宽度调整、边界宽度和刷新恢复
