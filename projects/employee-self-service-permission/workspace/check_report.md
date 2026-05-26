# Check Report｜人读说明版

> 本文件是 `projects/employee-self-service-permission/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: failed
- has_blocker: true
- blocker_count: 1
- warning_count: 5
- info_count: 2

## Output Status

- projects/employee-self-service-permission/workspace/facts.md: present
- projects/employee-self-service-permission/workspace/business_blueprint.md: present
- projects/employee-self-service-permission/workspace/experience_blueprint.md: present
- projects/employee-self-service-permission/workspace/gap_list.md: present
- projects/employee-self-service-permission/workspace/check_report.md: present
- projects/employee-self-service-permission/workspace/check_status.json: present

## Blockers

- experience_blueprint.md 缺少栏目：## 1.5 旅程图

## Warnings

- experience_blueprint.md 缺少正式旅程图，或旅程图还没有形成可解析结构
- 承接检查：business_blueprint.md 明确要求主流程闭环包含“员工查看申请记录 → 详情和状态 → 撤销或重新...”，但 experience_blueprint.md 还没有把这一段转成清晰的用户流程、系统反馈或结果去向。
- 承接检查：business_blueprint.md 要求解释“管理模式的开启/未开启两个状态”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。
- 承接检查：business_blueprint.md 要求解释“每个状态的可见性、可操作性和下一步”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。
- experience gate 状态为 warning

## Infos

- facts gate 状态：passed
- business gate 状态：passed

## 自然语言承接检查

- 角色路径覆盖：3/3
- 主流程闭环覆盖：3/4
- 异常与阻断覆盖：7/7
- 状态与反馈覆盖：1/3
- 风险保护承接：3/3
- 设计指南装配：2 条

## Machine Status

- 机器可读状态文件：`projects/employee-self-service-permission/workspace/check_status.json`
