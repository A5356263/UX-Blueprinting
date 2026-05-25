# Task Card

## Protocol

- Protocol Name: Cross-AI Task Card
- Protocol Version: v0.3
- Task ID: uxb-qc-003-permission-search-in-page
- Task Name: 页面内查找定位
- Domain: 权限管理

## Task Goal

- 用一句话说明本次任务要解决什么问题
- 说明本次输出主要服务于哪类评审、设计或重构工作

## Task Scenario

- 描述本次任务场景
- 说明这是新建、补充、校对、重构还是审查任务
- 说明本次任务主要落在 facts / business / experience 的哪一层，或覆盖全链路

## Required Inputs

- projects/uxb-qc-003-permission-search-in-page/source/requirement.md
- projects/uxb-qc-003-permission-search-in-page/source/background.md

## Required Outputs

- projects/uxb-qc-003-permission-search-in-page/workspace/facts.md
- projects/uxb-qc-003-permission-search-in-page/workspace/business_blueprint.md
- projects/uxb-qc-003-permission-search-in-page/workspace/experience_blueprint.md
- projects/uxb-qc-003-permission-search-in-page/workspace/gap_list.md
- projects/uxb-qc-003-permission-search-in-page/workspace/check_report.md
- projects/uxb-qc-003-permission-search-in-page/workspace/check_status.json

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

- 执行中结果: projects/uxb-qc-003-permission-search-in-page/workspace/
- 归档结果: projects/uxb-qc-003-permission-search-in-page/exports/final/

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

- UXB 应在执行前写好 `projects/uxb-qc-003-permission-search-in-page/runtime/uxb_route_decision.json`
- 如任务只做到某一阶段，可在 `Task Scenario` 和 `Required Outputs` 中明确裁剪
