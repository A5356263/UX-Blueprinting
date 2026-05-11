# Check Report｜人读说明版

> 本文件是 `projects/employee-permission-apply/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 6
- info_count: 7

## Output Status

- projects/employee-permission-apply/workspace/facts.md: present
- projects/employee-permission-apply/workspace/business_blueprint.md: present
- projects/employee-permission-apply/workspace/experience_blueprint.md: present
- projects/employee-permission-apply/workspace/gap_list.md: present
- projects/employee-permission-apply/workspace/check_report.md: present
- projects/employee-permission-apply/workspace/check_status.json: present

## Blockers

- none

## Warnings

- business gate 状态为 warning
- business_blueprint.md 风险与保护策略内容偏少
- experience gate 状态为 warning
- 承接检查：business_blueprint.md 已把“关闭模式时在途流程阻断”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- 承接检查：business_blueprint.md 要求解释“权限生效结果”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。
- 设计指南消费检查：knowledge_usage_report.json 未记录 experience 阶段实际消费的 design guideline。

## Infos

- facts gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：6/6
- 自然语言承接检查：异常与阻断覆盖：1/2
- 自然语言承接检查：状态与反馈覆盖：1/2
- 自然语言承接检查：角色路径覆盖：3/3
- 自然语言承接检查：设计指南消费：0 条
- 自然语言承接检查：风险保护承接：0/0

## 自然语言承接检查

- 角色路径覆盖：3/3
- 主流程闭环覆盖：6/6
- 异常与阻断覆盖：1/2
- 状态与反馈覆盖：1/2
- 风险保护承接：0/0
- 设计指南消费：0 条

## Machine Status

- 机器可读状态文件：`projects/employee-permission-apply/workspace/check_status.json`
