# Route Decision

- Project: `input-validation-fast-self-permission-help`
- Version: `route-decision@1.0`
- Rules version: `route-decision-rules@1.0`
- Route: `standard`
- Confidence: `high`
- Demand type: 业务流程调整
- Business depth: `lite`
- Should control mainline: `true`

## Reason

初判为业务流程调整，主要压力在业务规则、流程承接、信息结构，需要保留业务边界判断后再转体验方案。

## Evidence

- source/task_card.md: Task Name: 自助权限申请说明微调
- source/requirement.md: input 需求集合：自助权限申请
- source/background.md: 本样本来自 input 目录中的 自助权限申请 需求族，用于阶段三 run-routed-main 严格验收。
- runtime/task_card_resolved.json: {"task_id": "input-validation-fast-self-permission-help", "protocol_name": "UXB Test Task", "protocol_version": "1.0", "

## Design Pressure

- 业务规则
- 流程承接
- 信息结构
- 评审风险

## Escalation Signals

- 后续发现新增核心业务能力、重构既有模块或改变业务对象关系时，需升级 full。
- 后续发现多角色协作闭环、权限模型、审批模式或状态机变化时，需升级 full。
- 后续 facts/business 出现关键 GAP，无法支撑体验方案时，需升级 full 或暂停确认。

## Dimension Judgment

- `business_capability_change`: `none` - 需求未表现出新增或重构能力，主要是既有能力内调整
- `business_rule_change`: `medium` - 存在业务规则、校验或条件变化：本需求只做入口说明、提示语和空状态微调，不新增自助申请能力，不改变审批范围、审批模式、授权规则、数据范围或状态机
- `permission_governance_risk`: `none` - 未发现权限、审批、数据范围或治理变化
- `task_flow_change`: `medium` - 用户任务路径、结果回写或角色协同可能变化：交互流程总览
- `information_structure_pressure`: `medium` - 存在概念、入口、层级或模块边界压力：在员工自助申请入口补充可申请范围说明
- `state_exception_pressure`: `none` - 未发现明显状态、异常或校验压力
- `copy_comprehension_pressure`: `low` - 用户理解主要依赖文案、说明或提示：Task Name: 自助权限申请说明微调
- `layout_interaction_pressure`: `low` - 局部布局、展示或交互细节是明显压力：说明展示在现有入口附近
- `review_risk`: `medium` - 存在评审误解、边界争议或待确认风险：产物必须承接当前需求正文中的关键边界，不外扩判断维度
