# Check Report｜人读说明版

> 本文件是 `projects/self-permission-apply/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 9
- info_count: 7

## Output Status

- projects/self-permission-apply/workspace/facts.md: present
- projects/self-permission-apply/workspace/business_blueprint.md: present
- projects/self-permission-apply/workspace/experience_blueprint.md: present
- projects/self-permission-apply/workspace/gap_list.md: present
- projects/self-permission-apply/workspace/check_report.md: present
- projects/self-permission-apply/workspace/check_status.json: present

## Blockers

- none

## Warnings

- experience gate 状态为 warning
- experience_blueprint.md 缺少正式旅程图，或旅程图还没有形成可解析结构
- experience_blueprint.md 附录内容偏少，建议补充设计指南与业务知识消费说明
- facts gate 状态为 warning
- 承接检查：business_blueprint.md 已把“R1 范围过宽风险：配置页需展示安全默认值”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“R2 审批人配置风险：开启前校验”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已点名角色要求“员工端权限查看和申请页面”，但 experience_blueprint.md 还没有给出对应的清晰路径、页面或职责承接。
- 承接检查：business_blueprint.md 已点名角色要求“审批端申请处理页面”，但 experience_blueprint.md 还没有给出对应的清晰路径、页面或职责承接。
- 承接检查：business_blueprint.md 已点名角色要求“管理员端配置页面”，但 experience_blueprint.md 还没有给出对应的清晰路径、页面或职责承接。

## Infos

- business gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：3/3
- 自然语言承接检查：异常与阻断覆盖：5/5
- 自然语言承接检查：状态与反馈覆盖：2/2
- 自然语言承接检查：角色路径覆盖：0/3
- 自然语言承接检查：设计指南装配：2 条
- 自然语言承接检查：风险保护承接：0/2

## 自然语言承接检查

- 角色路径覆盖：0/3
- 主流程闭环覆盖：3/3
- 异常与阻断覆盖：5/5
- 状态与反馈覆盖：2/2
- 风险保护承接：0/2
- 设计指南装配：2 条

## Machine Status

- 机器可读状态文件：`projects/self-permission-apply/workspace/check_status.json`
