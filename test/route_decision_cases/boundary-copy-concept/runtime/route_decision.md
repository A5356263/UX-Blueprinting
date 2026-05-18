# Route Decision

- Project: `boundary-copy-concept`
- Version: `route-decision@1.0`
- Rules version: `route-decision-rules@1.0`
- Route: `standard`
- Confidence: `high`
- Demand type: 权限与治理风险
- Business depth: `lite`
- Should control mainline: `true`

## Reason

初判为权限与治理风险，主要压力在业务规则、权限治理、流程承接，需要保留业务边界判断后再转体验方案。

## Evidence

- source/requirement.md: 成员管理页中“外部人员”和“临时员工”的说明经常被用户混淆，业务希望改几句文案解决。

## Design Pressure

- 业务规则
- 权限治理
- 流程承接
- 信息结构
- 评审风险

## Escalation Signals

- 后续发现新增核心业务能力、重构既有模块或改变业务对象关系时，需升级 full。
- 后续发现多角色协作闭环、权限模型、审批模式或状态机变化时，需升级 full。
- 后续 facts/business 出现关键 GAP，无法支撑体验方案时，需升级 full 或暂停确认。

## Dimension Judgment

- `business_capability_change`: `none` - 需求未表现出新增或重构能力，主要是既有能力内调整
- `business_rule_change`: `medium` - 存在业务规则、校验或条件变化：影响成员类型理解、邀请入口选择、权限范围和后续合同/考勤流程
- `permission_governance_risk`: `high` - 涉及权限、审批、数据范围、导出或治理风险：影响成员类型理解、邀请入口选择、权限范围和后续合同/考勤流程
- `task_flow_change`: `medium` - 用户任务路径、结果回写或角色协同可能变化：影响成员类型理解、邀请入口选择、权限范围和后续合同/考勤流程
- `information_structure_pressure`: `medium` - 存在概念、入口、层级或模块边界压力：优化两个概念的页面说明，让管理员知道应该把哪类人员加入外部人员，哪类人员加入临时员工
- `state_exception_pressure`: `none` - 未发现明显状态、异常或校验压力
- `copy_comprehension_pressure`: `low` - 用户理解主要依赖文案、说明或提示：成员管理页中“外部人员”和“临时员工”的说明经常被用户混淆，业务希望改几句文案解决
- `layout_interaction_pressure`: `low` - 未发现布局交互是主要压力
- `review_risk`: `medium` - 存在评审误解、边界争议或待确认风险：如果概念定义不清，单纯改文案可能掩盖业务边界问题
