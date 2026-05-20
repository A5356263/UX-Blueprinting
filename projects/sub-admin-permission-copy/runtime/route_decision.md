# Route Decision

- Project: `sub-admin-permission-copy`
- Version: `route-decision@2.0`
- Status: `confirmed`
- Source: `uxb_ai_judgment`
- Confirmed by user: `true`
- Can execute mainline: `true`
- Route: `standard`
- Demand type: 既有能力扩展
- Business depth: `lite`

## Reason

在现有子管理员管理能力上新增复制操作，不改变底层业务对象关系。核心业务对象（子管理员、权限、组织、功能）不做结构性变更。新增业务规则包括叠加不覆盖和普通用户转子管理员。双管理员互审模式可能引入审批状态流，但该部分规则尚未明确，需在业务判断阶段单独标注。体验设计压力主要在异常分支处理。

## Evidence

- 集团型企业使用子管理员模式下放权限管理能力，当前配置需逐个子管理员单独勾选相同功能权限，实施工作量大
- 复制对象原本已是子管理员时，在其原有配置基础上叠加可授权功能、可授权组织
- 复制对象原本不是子管理员时，复制后成为子管理员
- 双管理员互审模式下，复制完成时需要生成一条审批，但审批规则尚未明确
- 存在10余条不明确事项，包括校验失败处理策略、去重、上限、审批时序等

## Design Pressure

- 业务能力
- 业务规则
- 流程承接
- 状态异常
- 信息结构

## Validation Errors

- none

## Risk Notes

- 双管理员互审的审批时序、生效机制和回滚策略未定，可能影响复制方案的完整形态
- 部分校验失败时的处理策略（全部阻断/跳过失败用户）会显著影响交互方案
- 复制来源是否允许部分复制、去重逻辑和上限处理需在业务判断中明确
- 加入状态口径未统一（已启用/已加入），需产品侧最终确定

## Guardrail Hints

- `business_capability_change`: `major` - 业务能力发生变化或扩展：说明本次输出主要服务于哪类评审、设计或重构工作
- `business_rule_change`: `medium` - 存在业务规则、校验或限制变化：摘要页未覆盖当前任务需要的对象、规则或路径
- `permission_governance_risk`: `high` - 涉及权限、审批、数据范围、导出或治理风险：部分客户子管理员数量较多（如广西交投 200+），这些子管理员的「可授权功能」通常一致，但「可授权组织」不同
- `task_flow_change`: `medium` - 用户任务路径、结果回写或角色协同可能变化：7. 双管理员互审模式下，审批通过前权限是否生效
- `information_structure_pressure`: `medium` - 存在概念、入口、层级或模块边界压力：复制入口：子管理员模式列表操作列新增「复制」
- `state_exception_pressure`: `high` - 状态、异常、阻断或校验会影响方案：双管理员互审模式可能引入审批状态流，但该部分规则尚未明确，需在业务判断阶段单独标注
- `copy_comprehension_pressure`: `low` - 用户理解主要依赖文案、说明或提示：每个交互节点写清用户动作、系统反馈、前置解释、具体文案、下一步
- `layout_interaction_pressure`: `low` - 局部布局、展示或交互细节是明显压力：文案必须是可直接展示的文本，禁止元指令
- `review_risk`: `medium` - 存在边界争议、误解风险或待确认项：facts 阶段不得把引用知识提升为当前任务的已确认事实
