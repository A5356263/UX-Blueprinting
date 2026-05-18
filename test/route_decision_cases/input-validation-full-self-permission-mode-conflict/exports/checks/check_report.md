# Check Report｜人读说明版

> 本文件是 `projects/input-validation-full-self-permission-mode-conflict/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 12
- info_count: 7

## Output Status

- projects/input-validation-full-self-permission-mode-conflict/workspace/facts.md: present
- projects/input-validation-full-self-permission-mode-conflict/workspace/business_blueprint.md: present
- projects/input-validation-full-self-permission-mode-conflict/workspace/experience_blueprint.md: present
- projects/input-validation-full-self-permission-mode-conflict/workspace/gap_list.md: present
- projects/input-validation-full-self-permission-mode-conflict/workspace/check_report.md: present
- projects/input-validation-full-self-permission-mode-conflict/workspace/check_status.json: present

## Blockers

- none

## Warnings

- business gate 状态为 warning
- business_blueprint.md 价值/成本/认知负担评估检测不到结构化内容，请确认已在自然语言中覆盖
- business_blueprint.md 附录没有自然说明主要依据来自 facts 的哪些章节，判断依据承接仍偏弱
- context_manifest.json.task_contract 缺少 read_order
- experience gate 状态为 warning
- experience_blueprint.md 附录：依据与追踪内容偏少
- knowledge_consumption_plan.facts 缺少 required_wiki_refs
- task_card_resolved.json 缺少 read_order
- 承接检查：business_blueprint.md 要求覆盖“员工”角色路径，但 experience_blueprint.md 还没有给出这类角色的清晰任务路径或页面承接。
- 承接检查：business_blueprint.md 要求覆盖“超管”角色路径，但 experience_blueprint.md 还没有给出这类角色的清晰任务路径或页面承接。
- 设计指南消费检查：experience_blueprint.md 缺少「设计指南消费说明」附录。
- 设计指南消费检查：knowledge_usage_report.json 未记录 experience 阶段实际消费的 design guideline。

## Infos

- facts gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：0/0
- 自然语言承接检查：异常与阻断覆盖：0/0
- 自然语言承接检查：状态与反馈覆盖：0/0
- 自然语言承接检查：角色路径覆盖：1/3
- 自然语言承接检查：设计指南消费：0 条
- 自然语言承接检查：风险保护承接：2/2

## 自然语言承接检查

- 角色路径覆盖：1/3
- 主流程闭环覆盖：0/0
- 异常与阻断覆盖：0/0
- 状态与反馈覆盖：0/0
- 风险保护承接：2/2
- 设计指南消费：0 条

## Machine Status

- 机器可读状态文件：`projects/input-validation-full-self-permission-mode-conflict/workspace/check_status.json`
