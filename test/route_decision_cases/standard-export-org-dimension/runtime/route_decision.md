# Route Decision

- Project: `standard-export-org-dimension`
- Version: `route-decision@1.0`
- Rules version: `route-decision-rules@1.0`
- Route: `standard`
- Confidence: `high`
- Demand type: 权限与治理风险
- Business depth: `lite`
- Should control mainline: `true`

## Reason

初判为权限与治理风险，主要压力在业务规则、权限治理、状态异常，需要保留业务边界判断后再转体验方案。

## Evidence

- source/requirement.md: 在导出弹窗中增加组织维度选择，支持按当前组织、含下级组织、全部可见组织导出。

## Design Pressure

- 业务规则
- 权限治理
- 状态异常
- 评审风险

## Escalation Signals

- 后续发现新增核心业务能力、重构既有模块或改变业务对象关系时，需升级 full。
- 后续发现多角色协作闭环、权限模型、审批模式或状态机变化时，需升级 full。
- 后续 facts/business 出现关键 GAP，无法支撑体验方案时，需升级 full 或暂停确认。

## Dimension Judgment

- `business_capability_change`: `none` - 需求未表现出新增或重构能力，主要是既有能力内调整
- `business_rule_change`: `medium` - 存在业务规则、校验或条件变化：影响员工列表导出范围、导出弹窗和结果反馈
- `permission_governance_risk`: `high` - 涉及权限、审批、数据范围、导出或治理风险：涉及数据范围和用户可见组织范围，不能导出超出当前权限的数据
- `task_flow_change`: `none` - 未发现主任务路径变化
- `information_structure_pressure`: `none` - 未发现明显信息结构或概念澄清压力
- `state_exception_pressure`: `medium` - 状态、异常、阻断或校验会影响方案：需要处理无权限组织、导出任务失败和大数据量导出延迟
- `copy_comprehension_pressure`: `low` - 未发现文案理解是主要压力
- `layout_interaction_pressure`: `low` - 未发现布局交互是主要压力
- `review_risk`: `medium` - 存在评审误解、边界争议或待确认风险：用户进入员工列表，点击导出，选择组织维度，确认后生成导出任务
