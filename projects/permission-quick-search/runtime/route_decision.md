# Route Decision

- Project: `permission-quick-search`
- Version: `route-decision@2.0`
- Status: `confirmed`
- Source: `uxb_ai_judgment`
- Confirmed by user: `true`
- Can execute mainline: `true`
- Route: `fast`
- Demand type: 局部体验优化
- Business depth: `note`

## Reason

本次需求是在功能权限设置页面增加页面内关键词查找定位能力（类似 Ctrl+F）。查找行为不改底层业务对象、规则、状态机、生效机制、数据口径和外部回写链路。权限的勾选、取消、保存逻辑完全沿用现有流程。所有权限项始终可见，只增加文字高亮和焦点跳转交互。属于纯展示层体验优化。

## Evidence

- 不改变业务对象关系：查找行为不修改任何权限数据
- 不改变业务规则：权限勾选、保存、取消逻辑完全沿用
- 不改变状态机：全选/半选/未选状态不变
- 不改变生效机制：权限生效流程不变
- 不改变数据口径：展示范围不变，所有权限项始终可见
- 不涉及外部回写链路
- 交互方式已与操作者确认：关键词输入、命中高亮、焦点跳转、多命中切换
- 需求文档已按确认后的交互方式改写

## Design Pressure

- 信息密度高：1100+权限项中查找定位
- 折叠节点内命中需自动展开
- 大量命中时的性能与切换体验

## Validation Errors

- none

## Risk Notes

- 折叠节点内命中时需自动展开对应层级，否则用户看不到高亮
- 关键词较短时可能出现大量命中项，需考虑切换体验和渲染性能
- 查找适用范围（是否覆盖所有授权对象类型）待确认

## Guardrail Hints

- `business_capability_change`: `none` - 未发现新增或重构能力，更像现有能力内调整
- `business_rule_change`: `medium` - 存在业务规则、校验或限制变化：本次是局部体验优化，不改底层业务对象、规则、状态机、生效机制和数据口径
- `permission_governance_risk`: `high` - 涉及权限、审批、数据范围、导出或治理风险：权限管理员：负责为员工、管理员或其他授权对象配置功能权限
- `task_flow_change`: `medium` - 用户任务路径、结果回写或角色协同可能变化：权限的勾选、取消、保存、取消保存逻辑完全沿用现有流程
- `information_structure_pressure`: `medium` - 存在概念、入口、层级或模块边界压力：查找入口：在功能权限设置区域提供查找输入框
- `state_exception_pressure`: `high` - 状态、异常、阻断或校验会影响方案：本次是局部体验优化，不改底层业务对象、规则、状态机、生效机制和数据口径
- `copy_comprehension_pressure`: `low` - 用户理解主要依赖文案、说明或提示：每个交互节点写清用户动作、系统反馈、前置解释、具体文案、下一步
- `layout_interaction_pressure`: `low` - 局部布局、展示或交互细节是明显压力：文案必须是可直接展示的文本，禁止元指令
- `review_risk`: `medium` - 存在边界争议、误解风险或待确认项："]}, "knowledge_consumption_plan": {"mode": "wiki_routed_raw_precision", "facts": {"required_wiki_refs": ["knowledge/wik
