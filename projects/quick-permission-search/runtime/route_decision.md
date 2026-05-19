# Route Decision

- Project: `quick-permission-search`
- Version: `route-decision@2.0`
- Status: `needs_uxb_judgment`
- Source: `missing_uxb_route_decision`
- Confirmed by user: `false`
- Can execute mainline: `false`
- Route: `pending`
- Demand type: 不确定
- Business depth: `pending`

## Reason

缺少 UXB 已确认的需求类型判断，当前只能给出风险提示，不能自动决定执行路线。

## Evidence

- source/task_card.md: Task Name: 功能权限全局关键词命中高亮
- source/requirement.md: Task Name: 功能权限全局关键词命中高亮
- source/background.md: 功能权限设置页面承载了企业权限管理员的核心配置工作。随着系统功能增加，末级菜单约 1100+、操作功能点约 1200+，管理员需要滚动约 35 屏才能完整浏览全部权限项。
- runtime/task_card_resolved.json: {"task_id": "quick-permission-search", "protocol_name": "Cross-AI Task Card", "protocol_version": "v0.2", "task_name": "
- runtime/context_manifest.json: {"task_id": "quick-permission-search", "resolved_from": "projects/quick-permission-search/runtime/task_card_resolved.jso

## Design Pressure

- 业务能力
- 业务规则
- 权限治理
- 信息结构
- 评审风险

## Validation Errors

- 缺少 runtime/uxb_route_decision.json

## Risk Notes

- 当前需求可能涉及权限、数据范围、审批或治理边界，不应被直接当作纯局部体验优化。
- 当前需求可能改变业务规则、限制或校验，建议先确认规则边界。
- 当前需求存在明显待确认边界，UXB 需要先和用户确认关键问题。

## Guardrail Hints

- `business_capability_change`: `major` - 业务能力发生变化或扩展：说明本次输出主要服务于哪类评审、设计或重构工作
- `business_rule_change`: `medium` - 存在业务规则、校验或限制变化：摘要页未覆盖当前任务需要的对象、规则或路径
- `permission_governance_risk`: `high` - 涉及权限、审批、数据范围、导出或治理风险：经分析，"筛选已勾选"解决的是核对/审计场景（系统性查看某个角色已被授权了什么），而当前最真实的痛点是"已知功能名、快速定位到它在树里的位置"的查找场景
- `task_flow_change`: `none` - 未发现任务路径变化
- `information_structure_pressure`: `medium` - 存在概念、入口、层级或模块边界压力：功能权限模块，页面结构为左侧锚点 + 右侧类表格数据展示，无分页
- `state_exception_pressure`: `none` - 未发现明显的状态或异常压力
- `copy_comprehension_pressure`: `low` - 用户理解主要依赖文案、说明或提示：每个交互节点写清用户动作、系统反馈、前置解释、具体文案、下一步
- `layout_interaction_pressure`: `low` - 局部布局、展示或交互细节是明显压力：文案必须是可直接展示的文本，禁止元指令
- `review_risk`: `medium` - 存在边界争议、误解风险或待确认项：facts 阶段不得把引用知识提升为当前任务的已确认事实
