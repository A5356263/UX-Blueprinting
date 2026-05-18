# Route Decision

- Project: `standard-batch-partial-failure`
- Version: `route-decision@1.0`
- Rules version: `route-decision-rules@1.0`
- Route: `standard`
- Confidence: `medium`
- Demand type: 既有能力扩展
- Business depth: `lite`
- Should control mainline: `true`

## Reason

初判为既有能力扩展，主要压力在状态异常，需要保留业务边界判断后再转体验方案。

## Evidence

- source/requirement.md: 成员批量禁用时，如果部分成员因状态或权限原因失败，当前只提示“操作失败”，用户不知道哪些成功、哪些失败。

## Design Pressure

- 状态异常

## Escalation Signals

- 后续发现新增核心业务能力、重构既有模块或改变业务对象关系时，需升级 full。
- 后续发现多角色协作闭环、权限模型、审批模式或状态机变化时，需升级 full。
- 后续 facts/business 出现关键 GAP，无法支撑体验方案时，需升级 full 或暂停确认。

## Dimension Judgment

- `business_capability_change`: `none` - 需求未表现出新增或重构能力，主要是既有能力内调整
- `business_rule_change`: `none` - 未发现明确业务规则变化信号
- `permission_governance_risk`: `none` - 未发现权限、审批、数据范围或治理变化
- `task_flow_change`: `none` - 未发现主任务路径变化
- `information_structure_pressure`: `none` - 未发现明显信息结构或概念澄清压力
- `state_exception_pressure`: `medium` - 状态、异常、阻断或校验会影响方案：成员批量禁用时，如果部分成员因状态或权限原因失败，当前只提示“操作失败”，用户不知道哪些成功、哪些失败
- `copy_comprehension_pressure`: `low` - 用户理解主要依赖文案、说明或提示：成员批量禁用时，如果部分成员因状态或权限原因失败，当前只提示“操作失败”，用户不知道哪些成功、哪些失败
- `layout_interaction_pressure`: `low` - 局部布局、展示或交互细节是明显压力：批量操作完成后展示成功数量、失败数量和失败明细，并给出可继续处理的下一步
- `review_risk`: `low` - 当前信息未暴露明显评审风险
