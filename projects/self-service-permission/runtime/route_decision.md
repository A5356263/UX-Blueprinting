# Route Decision

- Project: `self-service-permission`
- Version: `route-decision@2.0`
- Status: `confirmed`
- Source: `uxb_ai_judgment`
- Confirmed by user: `true`
- Can execute mainline: `true`
- Route: `full`
- Demand type: 功能新增
- Business depth: `full`

## Reason

引入新的权限治理模式（员工自助申请），改变业务对象关系（新增申请单对象）、状态机（申请→审批→生效）、生效机制（审批通过自动授权）和数据口径（可申请范围定义）。跨权限管理、协同办公、平台门户三个域，涉及4类角色和3个端。15项待确认事项需在完整业务判断中逐一处理。

## Evidence

- source/requirement.md: 新增员工自助申请权限能力，包含查看权限、申请权限、审批对接、申请记录四大模块
- source/background.md: 引入权限申请单对象，改变 subject→source 关系
- source/background.md: 新增申请单状态流转和自助申请模式开关状态
- source/background.md: 新增审批通过后自动授权这条生效路径
- source/requirement.md: 15项不明确事项涉及模式互斥、范围粒度、审批对接、异常处理等
- source/requirement.md: 与现有权限治理模式可能存在互斥关系

## Design Pressure

- 业务能力
- 业务规则
- 权限治理
- 流程承接
- 信息结构
- 状态异常

## Validation Errors

- none

## Risk Notes

- 自助申请模式与双管理员、子管理员、权限变更审批等已有治理模式存在互斥风险
- 可申请范围粒度不明确，角色级、功能权限级、数据权限级三种口径影响完全不同
- 审批人被默认为空或审批链配置错误时，可能导致申请永久卡在审批中
- 服务人员是否纳入该能力范围未确认，影响主体范围口径
- 管理员关闭能力后已授权限是否保留、审批中申请如何处理，两条分支需同时设计

## Guardrail Hints

- `business_capability_change`: `major` - 业务能力发生变化或扩展：说明本次输出主要服务于哪类评审、设计或重构工作
- `business_rule_change`: `medium` - 存在业务规则、校验或限制变化：摘要页未覆盖当前任务需要的对象、规则或路径
- `permission_governance_risk`: `high` - 涉及权限、审批、数据范围、导出或治理风险：员工可以申请哪些权限范围
- `task_flow_change`: `medium` - 用户任务路径、结果回写或角色协同可能变化：希望通过支持员工自助查看和申请权限，把部分权限申请工作从管理员侧分散到员工侧，同时保留管理员对申请范围和审批流程的控制
- `information_structure_pressure`: `medium` - 存在概念、入口、层级或模块边界压力：组织负责人、管理员，还是自定义审批流程
- `state_exception_pressure`: `high` - 状态、异常、阻断或校验会影响方案：3. **状态机**：引入申请单状态流转（发起→审批中→通过/拒绝→生效/不变），以及自助申请模式的开关状态
- `copy_comprehension_pressure`: `low` - 用户理解主要依赖文案、说明或提示：每个交互节点写清用户动作、系统反馈、前置解释、具体文案、下一步
- `layout_interaction_pressure`: `low` - 局部布局、展示或交互细节是明显压力：文案必须是可直接展示的文本，禁止元指令
- `review_risk`: `medium` - 存在边界争议、误解风险或待确认项：普通管理员：能力边界以产品配置为准
