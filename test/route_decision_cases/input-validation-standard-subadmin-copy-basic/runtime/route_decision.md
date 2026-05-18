# Route Decision

- Project: `input-validation-standard-subadmin-copy-basic`
- Version: `route-decision@1.0`
- Rules version: `route-decision-rules@1.0`
- Route: `standard`
- Confidence: `high`
- Demand type: 权限与治理风险
- Business depth: `lite`
- Should control mainline: `true`

## Reason

初判为权限与治理风险，主要压力在业务能力、业务规则、权限治理，需要保留业务边界判断后再转体验方案。

## Evidence

- source/task_card.md: Task Name: 子管理员权限复制基础能力
- source/requirement.md: input 需求集合：子管理员权限复制
- source/background.md: 本样本来自 input 目录中的 子管理员权限复制 需求族，用于阶段三 run-routed-main 严格验收。
- runtime/task_card_resolved.json: {"task_id": "input-validation-standard-subadmin-copy-basic", "protocol_name": "UXB Test Task", "protocol_version": "1.0"

## Design Pressure

- 业务能力
- 业务规则
- 权限治理
- 流程承接
- 状态异常

## Escalation Signals

- 后续发现新增核心业务能力、重构既有模块或改变业务对象关系时，需升级 full。
- 后续发现多角色协作闭环、权限模型、审批模式或状态机变化时，需升级 full。
- 后续 facts/business 出现关键 GAP，无法支撑体验方案时，需升级 full 或暂停确认。

## Dimension Judgment

- `business_capability_change`: `minor` - 业务能力发生变化或扩展：在既有子管理员授权能力上扩展复制能力，涉及批量选择、复制预览、目标用户校验、部分成功和失败反馈
- `business_rule_change`: `medium` - 存在业务规则、校验或条件变化：在既有子管理员授权能力上扩展复制能力，涉及批量选择、复制预览、目标用户校验、部分成功和失败反馈
- `permission_governance_risk`: `high` - 涉及权限、审批、数据范围、导出或治理风险：支持把一个子管理员的可授权组织和功能权限复制给多个目标用户
- `task_flow_change`: `medium` - 用户任务路径、结果回写或角色协同可能变化：交互流程总览
- `information_structure_pressure`: `none` - 未发现明显信息结构或概念澄清压力
- `state_exception_pressure`: `medium` - 状态、异常、阻断或校验会影响方案：在既有子管理员授权能力上扩展复制能力，涉及批量选择、复制预览、目标用户校验、部分成功和失败反馈
- `copy_comprehension_pressure`: `low` - 未发现文案理解是主要压力
- `layout_interaction_pressure`: `low` - 未发现布局交互是主要压力
- `review_risk`: `medium` - 存在评审误解、边界争议或待确认风险：产物必须承接当前需求正文中的关键边界，不外扩判断维度
