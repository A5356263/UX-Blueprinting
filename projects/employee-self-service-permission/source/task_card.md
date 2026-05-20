# Task Card

## Protocol

- Protocol Name: Cross-AI Task Card
- Protocol Version: v0.3
- Task ID: employee-self-service-permission
- Task Name: 员工自助申请权限
- Domain: permission

## Task Goal

- 在低完整度输入下，为“员工自助申请权限”补出可执行的事实、轻量业务判断和体验蓝图。
- 本次输出主要服务于权限治理能力扩展的方案判断与体验承接验证。

## Task Scenario

- 这是一个新增能力的正式任务样例，输入信息刻意不完整。
- 本次任务不是补齐完整 PRD，而是验证 UXB 是否能先做判断单，再驱动 facts / business / experience 的正式链路。
- 本次任务覆盖 facts、light business 和 experience 三层，但业务判断阶段按 `business_note.md` 处理。

## Required Inputs

- projects/employee-self-service-permission/source/requirement.md
- projects/employee-self-service-permission/source/background.md

## Required Outputs

- projects/employee-self-service-permission/workspace/facts.md
- projects/employee-self-service-permission/workspace/business_note.md
- projects/employee-self-service-permission/workspace/experience_blueprint.md
- projects/employee-self-service-permission/workspace/check_report.md
- projects/employee-self-service-permission/workspace/check_status.json

## Read Order

1. 先读本文档
2. 再读 `Required Inputs`
3. 生成 facts.md
4. 生成 business_note.md
5. 生成 experience_blueprint.md
6. 运行 route-decision / assemble / gate / validate-lite

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
- templates/business_note.template.md
- templates/experience_blueprint.template.md
- templates/check_report.template.md

## Checks

- specs/06_check_contract.md
- specs/08_fact_extraction_contract.md
- specs/16_business_note_contract.md
- specs/10_experience_blueprint_contract.md

## Result Locations

- 执行中结果：projects/employee-self-service-permission/workspace/
- 归档结果：projects/employee-self-service-permission/exports/final/

## Completion Criteria

- 必需输出文件全部存在
- `check_report.md` 已生成
- 无 blocker

## Facts Output Requirements

参考 `specs/08_fact_extraction_contract.md` 和 `templates/facts.template.md`

## Business Output Requirements

参考业务摘要合同和模板，不在 task card 中重复写内部判断逻辑。

## Experience Output Requirements

参考 `specs/10_experience_blueprint_contract.md` 和 `templates/experience_blueprint.template.md`

## Notes

- UXB 应在执行前写好 `projects/employee-self-service-permission/runtime/uxb_route_decision.json`
- 这次是低完整度正式任务，允许保留 `[GAP]`，但不能跳过权限边界、审批边界、状态机和异常处理。
