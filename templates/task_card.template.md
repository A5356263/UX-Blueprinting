# 任务卡片

> 说明：以下 `## Protocol`、`## Required Inputs` 等 section 名，以及 `Protocol Name`、`Task ID` 等字段名，当前仍作为执行器稳定解析结构保留，不建议随意改名。

## Protocol

- Protocol Name: Cross-AI Task Card
- Protocol Version: v0.3
- Task ID: {{TASK_ID}}
- Task Name: {{TASK_NAME}}
- Domain: {{DOMAIN}}

## Required Inputs

- projects/{{TASK_ID}}/source/requirement.md
- projects/{{TASK_ID}}/source/background.md

## Required Outputs

- projects/{{TASK_ID}}/workspace/facts.md
- projects/{{TASK_ID}}/workspace/business_blueprint.md
- projects/{{TASK_ID}}/workspace/experience_blueprint.md
- projects/{{TASK_ID}}/workspace/gap_list.md
- projects/{{TASK_ID}}/workspace/check_report.md
- projects/{{TASK_ID}}/workspace/check_status.json

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
