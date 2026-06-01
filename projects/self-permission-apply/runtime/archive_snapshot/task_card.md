# 任务卡片

> 说明：以下 `## Protocol`、`## Required Inputs` 等 section 名，以及 `Protocol Name`、`Task ID` 等字段名，当前仍作为执行器稳定解析结构保留，不建议随意改名。

## Protocol

- Protocol Name: Cross-AI Task Card
- Protocol Version: v0.3
- Task ID: self-permission-apply
- Task Name: 员工自助申请权限
- Domain: 权限管理

## Task Goal

- 为「员工自助申请权限」做完整业务判断和体验蓝图，使员工可以查看已有权限、主动申请角色权限、通过审批后自动授权，同时管理员可控制申请范围和审批流程
- 本次输出服务于产品方案评审和体验设计启动

## Task Scenario

- 基于低完整度需求文档，新增一套员工自助申请权限的完整业务模型和体验方案
- 这是新建任务，覆盖全链路（facts → business → experience）
- 主要压力在业务骨架变化（新对象、新来源、新状态机）和跨角色体验承接（管理端/员工端/审批端）

## Required Inputs

- projects/self-permission-apply/source/requirement.md
- projects/self-permission-apply/source/background.md

## Required Outputs

- projects/self-permission-apply/workspace/facts.md
- projects/self-permission-apply/workspace/business_blueprint.md
- projects/self-permission-apply/workspace/experience_blueprint.md
- projects/self-permission-apply/workspace/gap_list.md
- projects/self-permission-apply/workspace/check_report.md
- projects/self-permission-apply/workspace/check_status.json

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

- 执行中结果: projects/self-permission-apply/workspace/
- 归档结果: projects/self-permission-apply/exports/final/

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

- UXB 应在执行前写好 `projects/self-permission-apply/runtime/uxb_route_decision.json`
- 如任务只做到某一阶段，可在 `Task Scenario` 和 `Required Outputs` 中明确裁剪
