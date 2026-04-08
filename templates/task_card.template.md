# Task Card

## Protocol

- Protocol Name：Cross-AI Task Card
- Protocol Version：v0.1
- Task ID：{{TASK_ID}}
- Task Name：{{TASK_NAME}}
- Domain：{{DOMAIN}}

## Task Goal

- 用一句话说明本任务要解决什么问题

## Task Scenario

- 描述本次任务场景
- 说明这是新建、补充、校对、重构还是审查任务

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

## Read Order

1. 先读本文件
2. 再读 `Required Inputs`
3. 再读 `Wiki`
4. 再读 `Knowledge`
5. 最后按 `Templates` 产出结果并按 `Checks` 自检

## Constraints

- 不得臆造业务事实
- 信息不足处保留 `[GAP]`
- 正式产出必须写入 `workspace/`
- 不得用聊天回复替代正式文档产物

## Knowledge

- knowledge/business/{{DOMAIN}}/
- knowledge/guidelines/

## Wiki

- knowledge/wiki/indices/{{DOMAIN}}-domain.md

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

## Platform Optimizations

- skills/skill_requirements_refine.md
- skills/skill_blueprint_build.md

## Result Locations

- 执行中结果：projects/{{TASK_ID}}/workspace/
- 归档结果：projects/{{TASK_ID}}/exports/final/

## Completion Criteria

- 必需输出文件全部存在
- `check_report.md` 已生成
- 无 blocker

## Notes

- 当前为模板占位，可按任务补充
