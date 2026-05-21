# Check Report｜人读说明版

> 本文件是 `projects/employee-self-service-permission/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 2
- info_count: 6

## Output Status

- none

## Blockers

- none

## Warnings

- 承接检查：business_blueprint.md 明确要求主流程闭环包含“管理员关闭自助申请模式”，但 experience_blueprint.md 还没有把这一段转成清晰的用户流程、系统反馈或结果去向。
- 承接检查：business_blueprint.md 明确要求主流程闭环包含“管理员配置和开启自助申请模式”，但 experience_blueprint.md 还没有把这一段转成清晰的用户流程、系统反馈或结果去向。

## Infos

- 自然语言承接检查：主流程闭环覆盖：2/4
- 自然语言承接检查：异常与阻断覆盖：4/4
- 自然语言承接检查：状态与反馈覆盖：3/3
- 自然语言承接检查：角色路径覆盖：3/3
- 自然语言承接检查：设计指南装配：3 条
- 自然语言承接检查：风险保护承接：3/3

## 自然语言承接检查

- 角色路径覆盖：3/3
- 主流程闭环覆盖：2/4
- 异常与阻断覆盖：4/4
- 状态与反馈覆盖：3/3
- 风险保护承接：3/3
- 设计指南装配：3 条

## Machine Status

- 机器可读状态文件：`projects/employee-self-service-permission/workspace/check_status.json`
