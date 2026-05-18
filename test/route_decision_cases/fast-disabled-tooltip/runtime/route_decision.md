# Route Decision

- Project: `fast-disabled-tooltip`
- Version: `route-decision@1.0`
- Rules version: `route-decision-rules@1.0`
- Route: `standard`
- Confidence: `medium`
- Demand type: 业务流程调整
- Business depth: `lite`
- Should control mainline: `true`

## Reason

初判为业务流程调整，主要压力在流程承接、状态异常，需要保留业务边界判断后再转体验方案。

## Evidence

- source/requirement.md: 审批列表中部分“撤回”按钮处于禁用状态，但用户不知道为什么不能点击。

## Design Pressure

- 流程承接
- 状态异常

## Escalation Signals

- 后续发现新增核心业务能力、重构既有模块或改变业务对象关系时，需升级 full。
- 后续发现多角色协作闭环、权限模型、审批模式或状态机变化时，需升级 full。
- 后续 facts/business 出现关键 GAP，无法支撑体验方案时，需升级 full 或暂停确认。

## Dimension Judgment

- `business_capability_change`: `none` - 需求未表现出新增或重构能力，主要是既有能力内调整
- `business_rule_change`: `none` - 未发现明确业务规则变化信号
- `permission_governance_risk`: `none` - 未发现权限、审批、数据范围或治理变化
- `task_flow_change`: `medium` - 用户任务路径、结果回写或角色协同可能变化：审批列表中部分“撤回”按钮处于禁用状态，但用户不知道为什么不能点击
- `information_structure_pressure`: `none` - 未发现明显信息结构或概念澄清压力
- `state_exception_pressure`: `medium` - 状态、异常、阻断或校验会影响方案：用户进入审批列表，鼠标悬停在禁用的撤回按钮上，看到不可操作原因
- `copy_comprehension_pressure`: `low` - 用户理解主要依赖文案、说明或提示：在禁用按钮上补充 tooltip，说明当前审批已进入终审节点，不能再撤回
- `layout_interaction_pressure`: `low` - 局部布局、展示或交互细节是明显压力：审批列表中部分“撤回”按钮处于禁用状态，但用户不知道为什么不能点击
- `review_risk`: `low` - 当前信息未暴露明显评审风险
