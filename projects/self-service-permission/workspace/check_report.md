# Check Report｜人读说明版

> 本文件是 `projects/self-service-permission/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 6
- info_count: 7

## Output Status

- projects/self-service-permission/workspace/facts.md: present
- projects/self-service-permission/workspace/business_blueprint.md: present
- projects/self-service-permission/workspace/experience_blueprint.md: present
- projects/self-service-permission/workspace/gap_list.md: present
- projects/self-service-permission/workspace/check_report.md: present
- projects/self-service-permission/workspace/check_status.json: present

## Blockers

- none

## Warnings

- business gate 状态为 warning
- business_blueprint.md 规则与边界描述偏少
- experience gate 状态为 warning
- experience_blueprint.md 核心区包含表格，建议改为节点化 Markdown 层级表达
- 承接检查：business_blueprint.md 要求解释“权限生效结果”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。
- 设计指南消费检查：knowledge_usage_report.json 未记录 experience 阶段实际消费的 design guideline。

## Infos

- facts gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：5/5
- 自然语言承接检查：异常与阻断覆盖：4/4
- 自然语言承接检查：状态与反馈覆盖：2/3
- 自然语言承接检查：角色路径覆盖：3/3
- 自然语言承接检查：设计指南消费：0 条
- 自然语言承接检查：风险保护承接：0/0

## 自然语言承接检查

- 角色路径覆盖：3/3
- 主流程闭环覆盖：5/5
- 异常与阻断覆盖：4/4
- 状态与反馈覆盖：2/3
- 风险保护承接：0/0
- 设计指南消费：0 条

## Machine Status

- 机器可读状态文件：`projects/self-service-permission/workspace/check_status.json`
