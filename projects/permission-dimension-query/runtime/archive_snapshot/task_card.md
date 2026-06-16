# Task Card

## Protocol

- Protocol Name: Cross-AI Task Card
- Protocol Version: v0.2
- Task ID: permission-dimension-query
- Task Name: 权限维度统一查询
- Domain: 业务/权限管理

## Required Inputs

- projects/permission-dimension-query/source/requirement.md
- projects/permission-dimension-query/source/background.md

## Required Outputs

- projects/permission-dimension-query/workspace/facts.md
- projects/permission-dimension-query/workspace/business_blueprint.md
- projects/permission-dimension-query/workspace/experience_blueprint.md
- projects/permission-dimension-query/workspace/gap_list.md
- projects/permission-dimension-query/workspace/check_report.md
- projects/permission-dimension-query/workspace/check_status.json

## Constraints

- 不得臆造业务事实
- 信息不足处保留 `[GAP]`
- 正式产出必须写入 `workspace/`
- 不得用聊天回复替代正式文档产物
- facts 阶段不得把引用知识提升为当前任务的已确认事实
- business 阶段不得输出 UI 方案或实现方案
- experience 阶段不得输出高保真视觉稿或研发实现细节
- 阶段门禁：每个阶段必须 gate 通过后才能进入下一阶段

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
