# Task Card

## Protocol

- Protocol Name: Cross-AI Task Card
- Protocol Version: v0.3
- Task ID: employee-self-service-permission-lowdoc
- Task Name: 员工自助申请权限
- Domain: 权限管理

## Task Goal

- 为"员工自助申请权限"这一全新能力输出完整业务蓝图和完整体验蓝图
- 本次输出服务于产品评审、体验设计评审和研发启动前的方案对齐

## Task Scenario

本任务是新建任务，基于低完整度需求文档进行业务判断和体验方案推导。任务覆盖全链路：facts → business_blueprint → experience_blueprint。需求文档中 15 个不确定事项已由 UXB 给出判断建议并纳入正式输入，供业务蓝图消费。

## Required Inputs

- projects/employee-self-service-permission-lowdoc/source/requirement.md
- projects/employee-self-service-permission-lowdoc/source/background.md

## Required Outputs

- projects/employee-self-service-permission-lowdoc/workspace/facts.md
- projects/employee-self-service-permission-lowdoc/workspace/business_blueprint.md
- projects/employee-self-service-permission-lowdoc/workspace/experience_blueprint.md
- projects/employee-self-service-permission-lowdoc/workspace/gap_list.md
- projects/employee-self-service-permission-lowdoc/workspace/check_report.md
- projects/employee-self-service-permission-lowdoc/workspace/check_status.json

## Read Order

1. 先读本文档
2. 再读 `Required Inputs`
3. 生成 facts.md
4. 生成 business 产物
5. 生成 experience_blueprint.md
6. 运行 validate / coverage / archive / preview

## Constraints

- 不得臆造业务事实
- 信息不足处保留 `[GAP]`
- 正式产出必须写入 `workspace/`
- 不得用聊天回复替代正式文档产物
- facts 阶段不得把引用知识提升为当前任务已确认事实
- business 阶段不得输出 UI 方案或实现方案
- experience 阶段不得输出高保真视觉稿或研发实现细节
- `runtime/uxb_route_decision.json` 是执行判断与知识选择唯一来源
- `task_card.md` 不能替代 UXB 做复杂度判断、知识选择或执行深度判断

## Templates

- templates/facts.template.md
- templates/business_blueprint.template.md
- templates/experience_blueprint.template.md
- templates/gap_list.template.md
- templates/check_report.template.md

## Checks

- specs/06_check_contract.md
- specs/08_fact_extraction_contract.md
- specs/09_business_blueprint_contract.md
- specs/10_experience_blueprint_contract.md

## Result Locations

- 执行中结果: projects/employee-self-service-permission-lowdoc/workspace/
- 归档结果: projects/employee-self-service-permission-lowdoc/exports/final/

## Completion Criteria

- 必需输出文件全部存在
- `check_report.md` 已生成
- 无 blocker

## Facts Output Requirements

参考 `specs/08_fact_extraction_contract.md` 和 `templates/facts.template.md`

## Business Output Requirements

参考对应业务合同和模板，不在 task card 中重复写内部判断逻辑

## Experience Output Requirements

参考 `specs/10_experience_blueprint_contract.md` 和 `templates/experience_blueprint.template.md`

## Notes

- UXB 已完成 `runtime/uxb_route_decision.json`，`can_execute_mainline: true`
- 本次输出完整体验蓝图，覆盖员工端、管理端、审批端三侧体验
- 15 个不确定事项的 UXB 建议已写进 `source/requirement.md`
