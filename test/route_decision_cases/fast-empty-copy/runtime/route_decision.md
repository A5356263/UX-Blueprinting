# Route Decision

- Project: `fast-empty-copy`
- Version: `route-decision@1.0`
- Rules version: `route-decision-rules@1.0`
- Route: `standard`
- Confidence: `medium`
- Demand type: 业务流程调整
- Business depth: `lite`
- Should control mainline: `true`

## Reason

初判为业务流程调整，主要压力在流程承接，需要保留业务边界判断后再转体验方案。

## Evidence

- source/task_card.md: Task Name: 空状态文案微调
- source/requirement.md: 权限查询页面在没有筛选结果时只显示“暂无数据”，用户不知道是没有权限记录，还是筛选条件过窄。
- source/background.md: 当前需求只涉及空状态提示，不涉及核心业务规则变化。
- runtime/task_card_resolved.json: {"task_id": "fast-empty-copy", "protocol_name": "UXB Test Task", "protocol_version": "1.0", "task_name": "空状态文案微调", "dom

## Design Pressure

- 流程承接

## Escalation Signals

- 后续发现新增核心业务能力、重构既有模块或改变业务对象关系时，需升级 full。
- 后续发现多角色协作闭环、权限模型、审批模式或状态机变化时，需升级 full。
- 后续 facts/business 出现关键 GAP，无法支撑体验方案时，需升级 full 或暂停确认。

## Dimension Judgment

- `business_capability_change`: `none` - 需求未表现出新增或重构能力，主要是既有能力内调整
- `business_rule_change`: `none` - 未发现明确业务规则变化信号
- `permission_governance_risk`: `none` - 未发现权限、审批、数据范围或治理变化
- `task_flow_change`: `medium` - 用户任务路径、结果回写或角色协同可能变化：交互流程总览
- `information_structure_pressure`: `none` - 未发现明显信息结构或概念澄清压力
- `state_exception_pressure`: `none` - 未发现明显状态、异常或校验压力
- `copy_comprehension_pressure`: `low` - 用户理解主要依赖文案、说明或提示：Task Name: 空状态文案微调
- `layout_interaction_pressure`: `low` - 局部布局、展示或交互细节是明显压力：优化空状态提示文案，让用户知道当前没有可展示内容
- `review_risk`: `low` - 当前信息未暴露明显评审风险
