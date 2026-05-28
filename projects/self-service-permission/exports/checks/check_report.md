# Check Report｜人读说明版

> 本文件是 `projects/self-service-permission/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 7
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

- 承接检查：business_blueprint.md 已把“可作为设计建议：”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“员工端入口位置和引导方式”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“审批决策的二次确认（避免误操作）”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“审批端的批量处理能力”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“申请列表的排序和筛选建议”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已点名角色要求“管理员的配置体验（能力开关、范围圈定、审批设置、...”，但 experience_blueprint.md 还没有给出对应的清晰路径、页面或职责承接。
- 承接检查：business_blueprint.md 明确要求主流程闭环包含“管理员关闭能力 → 员工端变化 → 已生效权限不...”，但 experience_blueprint.md 还没有把这一段转成清晰的用户流程、系统反馈或结果去向。

## Infos

- business gate 状态：passed
- experience gate 状态：passed
- facts gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：1/2
- 自然语言承接检查：异常与阻断覆盖：5/5
- 自然语言承接检查：状态与反馈覆盖：3/3
- 自然语言承接检查：角色路径覆盖：2/3
- 自然语言承接检查：设计指南装配：3 条
- 自然语言承接检查：风险保护承接：3/8

## 自然语言承接检查

- 角色路径覆盖：2/3
- 主流程闭环覆盖：1/2
- 异常与阻断覆盖：5/5
- 状态与反馈覆盖：3/3
- 风险保护承接：3/8
- 设计指南装配：3 条

## Machine Status

- 机器可读状态文件：`projects/self-service-permission/workspace/check_status.json`
