# Check Report｜人读说明版

> 本文件是 `projects/employee-self-service-permission-lowdoc/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 4
- info_count: 8

## Output Status

- projects/employee-self-service-permission-lowdoc/workspace/facts.md: present
- projects/employee-self-service-permission-lowdoc/workspace/business_blueprint.md: present
- projects/employee-self-service-permission-lowdoc/workspace/experience_blueprint.md: present
- projects/employee-self-service-permission-lowdoc/workspace/gap_list.md: present
- projects/employee-self-service-permission-lowdoc/workspace/check_report.md: present
- projects/employee-self-service-permission-lowdoc/workspace/check_status.json: present

## Blockers

- none

## Warnings

- experience gate 状态为 warning
- experience_blueprint.md 页面设计检测不到结构化内容，请确认已用自然语言写清各页面
- 承接检查：business_blueprint.md 已把“前置条件不满足时阻止开启能力”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- 承接检查：business_blueprint.md 明确要求主流程闭环包含“审批人接收待办 → 审查详情 → 做出决定 → ...”，但 experience_blueprint.md 还没有把这一段转成清晰的用户流程、系统反馈或结果去向。

## Infos

- business gate 状态：passed
- facts gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：2/3
- 自然语言承接检查：异常与阻断覆盖：4/5
- 自然语言承接检查：状态与反馈覆盖：2/2
- 自然语言承接检查：角色路径覆盖：3/3
- 自然语言承接检查：设计指南装配：5 条
- 自然语言承接检查：风险保护承接：3/3

## 自然语言承接检查

- 角色路径覆盖：3/3
- 主流程闭环覆盖：2/3
- 异常与阻断覆盖：4/5
- 状态与反馈覆盖：2/2
- 风险保护承接：3/3
- 设计指南装配：5 条

## Machine Status

- 机器可读状态文件：`projects/employee-self-service-permission-lowdoc/workspace/check_status.json`
