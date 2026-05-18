# Route Decision

- Project: `input-validation-full-permission-query-multidimension`
- Version: `route-decision@1.0`
- Rules version: `route-decision-rules@1.0`
- Route: `full`
- Confidence: `high`
- Demand type: 权限与治理风险
- Business depth: `full`
- Should control mainline: `true`

## Reason

初判为权限与治理风险，主要压力在业务能力、业务规则、权限治理，涉及核心能力、治理或模型边界，需走完整链路。

## Evidence

- source/task_card.md: Task Name: 权限维度多维查询
- source/requirement.md: input 需求集合：权限查询
- source/background.md: 本样本来自 input 目录中的 权限查询 需求族，用于阶段三 run-routed-main 严格验收。
- runtime/task_card_resolved.json: {"task_id": "input-validation-full-permission-query-multidimension", "protocol_name": "UXB Test Task", "protocol_version

## Design Pressure

- 业务能力
- 业务规则
- 权限治理
- 流程承接
- 信息结构

## Escalation Signals

- 当前已建议 full，不建议自动降级。
- 如果后续事实证明范围更小，也应由人工确认后再调整，不自动改为 fast 或 standard。

## Dimension Judgment

- `business_capability_change`: `major` - 业务能力发生变化或扩展：本需求是功能新增和权限治理能力建设，涉及权限模型、数据范围、敏感查询、导出审计、对象关系重构、状态异常和跨维度结果解释
- `business_rule_change`: `medium` - 存在业务规则、校验或条件变化：管理员需要从不同业务对象反查权限来源、可见范围、审批链路和导出依据
- `permission_governance_risk`: `high` - 涉及权限、审批、数据范围、导出或治理风险：本需求是功能新增和权限治理能力建设，涉及权限模型、数据范围、敏感查询、导出审计、对象关系重构、状态异常和跨维度结果解释
- `task_flow_change`: `medium` - 用户任务路径、结果回写或角色协同可能变化：交互流程总览
- `information_structure_pressure`: `medium` - 存在概念、入口、层级或模块边界压力：本需求是功能新增和权限治理能力建设，涉及权限模型、数据范围、敏感查询、导出审计、对象关系重构、状态异常和跨维度结果解释
- `state_exception_pressure`: `medium` - 状态、异常、阻断或校验会影响方案：本需求是功能新增和权限治理能力建设，涉及权限模型、数据范围、敏感查询、导出审计、对象关系重构、状态异常和跨维度结果解释
- `copy_comprehension_pressure`: `low` - 用户理解主要依赖文案、说明或提示：本需求是功能新增和权限治理能力建设，涉及权限模型、数据范围、敏感查询、导出审计、对象关系重构、状态异常和跨维度结果解释
- `layout_interaction_pressure`: `low` - 未发现布局交互是主要压力
- `review_risk`: `medium` - 存在评审误解、边界争议或待确认风险：产物必须承接当前需求正文中的关键边界，不外扩判断维度
