# Route Decision

- Project: `fast-org-tree-width`
- Version: `route-decision@1.0`
- Rules version: `route-decision-rules@1.0`
- Route: `fast`
- Confidence: `medium`
- Demand type: 局部体验优化
- Business depth: `note`
- Should control mainline: `true`

## Reason

初判为局部体验优化，主要压力在信息结构、评审风险，未发现会改变核心业务规则的信号。

## Evidence

- source/task_card.md: 优化组织树宽度展示，让长部门名称更容易查看。
- source/requirement.md: 组织架构页面左侧组织树在层级较深时，部门名称经常被截断，用户需要反复悬停查看完整名称。
- source/background.md: 测试 fast 路线下局部布局交互优化。
- runtime/task_card_resolved.json: {"task_id": "fast-org-tree-width", "protocol_name": "UXB Test Task", "protocol_version": "1.0", "task_name": "组织树宽度拖动", 

## Design Pressure

- 信息结构
- 评审风险

## Escalation Signals

- 后续发现权限、审批、数据范围、导出或状态机变化时，需升级 standard。
- 后续发现新增业务规则、校验条件或阻断异常决定方案成败时，需升级 standard。
- 后续发现需求原文存在明显更优解或体验风险时，需重新判断路线。

## Dimension Judgment

- `business_capability_change`: `none` - 需求未表现出新增或重构能力，主要是既有能力内调整
- `business_rule_change`: `none` - 未发现明确业务规则变化信号
- `permission_governance_risk`: `none` - 未发现权限、审批、数据范围或治理变化
- `task_flow_change`: `none` - 未发现主任务路径变化
- `information_structure_pressure`: `medium` - 存在概念、入口、层级或模块边界压力：需要定义最小宽度、最大宽度、长部门名称展示和窗口缩小时的响应方式
- `state_exception_pressure`: `none` - 未发现明显状态、异常或校验压力
- `copy_comprehension_pressure`: `low` - 未发现文案理解是主要压力
- `layout_interaction_pressure`: `low` - 局部布局、展示或交互细节是明显压力：测试 fast 路线下局部布局交互优化
- `review_risk`: `medium` - 存在评审误解、边界争议或待确认风险：experience 承接宽度调整、边界宽度和刷新恢复
