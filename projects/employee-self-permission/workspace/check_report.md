# Check Report｜人读说明版

> 本文件是 `projects/employee-self-permission/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 10
- info_count: 2

## Output Status

- projects/employee-self-permission/workspace/facts.md: present
- projects/employee-self-permission/workspace/business_blueprint.md: present
- projects/employee-self-permission/workspace/experience_blueprint.md: present
- projects/employee-self-permission/workspace/gap_list.md: present
- projects/employee-self-permission/workspace/check_report.md: present
- projects/employee-self-permission/workspace/check_status.json: present

## Blockers

- none

## Warnings

- gap_list.md 仍包含占位内容
- experience_blueprint.md 待确认问题为空，建议显式标注不确定项
- experience_blueprint.md 附录：依据与追踪内容偏少
- 承接检查：business_blueprint.md 明确要求主流程闭环包含“员工：收到审批结果通知 → 查看权限变化（如通过...”，但 experience_blueprint.md 还没有把这一段转成清晰的用户流程、系统反馈或结果去向。
- 承接检查：business_blueprint.md 已把“员工越权访问他人数据时，数据层拦截。”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- 承接检查：business_blueprint.md 已把“可作为设计建议：”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“首版不支持申请附件上传，降低复杂度”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“报错或阻断的业务依据判断：”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 设计指南消费检查：experience_blueprint.md 缺少「设计指南消费说明」附录。
- experience gate 状态为 warning

## Infos

- facts gate 状态：passed
- business gate 状态：passed

## 自然语言承接检查

- 角色路径覆盖：3/3
- 主流程闭环覆盖：4/5
- 异常与阻断覆盖：5/6
- 状态与反馈覆盖：3/3
- 风险保护承接：11/14
- 设计指南消费：3 条

## Machine Status

- 机器可读状态文件：`projects/employee-self-permission/workspace/check_status.json`
