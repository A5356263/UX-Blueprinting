# Check Report｜人读说明版

> 本文件是 `projects/self-service-permission/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 2
- info_count: 9

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

- gap_list.md 仍包含占位内容
- 设计指南消费检查：experience_blueprint.md 缺少「设计指南消费说明」附录。

## Infos

- business gate 状态：passed
- experience gate 状态：passed
- facts gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：4/4
- 自然语言承接检查：异常与阻断覆盖：6/6
- 自然语言承接检查：状态与反馈覆盖：4/4
- 自然语言承接检查：角色路径覆盖：3/3
- 自然语言承接检查：设计指南消费：3 条
- 自然语言承接检查：风险保护承接：3/3

## 自然语言承接检查

- 角色路径覆盖：3/3
- 主流程闭环覆盖：4/4
- 异常与阻断覆盖：6/6
- 状态与反馈覆盖：4/4
- 风险保护承接：3/3
- 设计指南消费：3 条

## Machine Status

- 机器可读状态文件：`projects/self-service-permission/workspace/check_status.json`
