# Route Decision

- Project: `boundary-small-data-scope`
- Version: `route-decision@1.0`
- Rules version: `route-decision-rules@1.0`
- Route: `standard`
- Confidence: `medium`
- Demand type: 权限与治理风险
- Business depth: `lite`
- Should control mainline: `true`

## Reason

初判为权限与治理风险，主要压力在业务规则、权限治理，需要保留业务边界判断后再转体验方案。

## Evidence

- source/requirement.md: 权限查询页希望把“仅看我的权限”改成默认勾选“查看我管理范围内所有成员权限”。

## Design Pressure

- 业务规则
- 权限治理

## Escalation Signals

- 后续发现新增核心业务能力、重构既有模块或改变业务对象关系时，需升级 full。
- 后续发现多角色协作闭环、权限模型、审批模式或状态机变化时，需升级 full。
- 后续 facts/business 出现关键 GAP，无法支撑体验方案时，需升级 full 或暂停确认。

## Dimension Judgment

- `business_capability_change`: `none` - 需求未表现出新增或重构能力，主要是既有能力内调整
- `business_rule_change`: `medium` - 存在业务规则、校验或条件变化：权限查询页希望把“仅看我的权限”改成默认勾选“查看我管理范围内所有成员权限”
- `permission_governance_risk`: `high` - 涉及权限、审批、数据范围、导出或治理风险：影响权限查询默认结果、数据范围和页面说明
- `task_flow_change`: `none` - 未发现主任务路径变化
- `information_structure_pressure`: `none` - 未发现明显信息结构或概念澄清压力
- `state_exception_pressure`: `none` - 未发现明显状态、异常或校验压力
- `copy_comprehension_pressure`: `low` - 用户理解主要依赖文案、说明或提示：影响权限查询默认结果、数据范围和页面说明
- `layout_interaction_pressure`: `low` - 局部布局、展示或交互细节是明显压力：管理员进入权限查询页，系统默认展示管理范围内的成员权限
- `review_risk`: `low` - 当前信息未暴露明显评审风险
