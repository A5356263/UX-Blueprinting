# Check Report｜人读说明版

> 本文件是 `projects/self-permission-apply/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 12
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
- experience_blueprint.md 主流程、异常或页面设计核心区包含表格，建议优先使用节点化 Markdown 层级表达
- facts gate 状态为 warning
- 承接检查：business_blueprint.md 已把“可申请范围的安全边界需要在界面上清晰表达”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“审批流程异常的兜底提示”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“申请不在可申请范围内”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- 承接检查：business_blueprint.md 已把“申请被驳回后的申诉/重新提交”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- 承接检查：business_blueprint.md 已把“重复申请已拥有的权限”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- 承接检查：business_blueprint.md 已点名角色要求“员工查看权限和发起申请的完整流程”，但 experience_blueprint.md 还没有给出对应的清晰路径、页面或职责承接。
- 承接检查：business_blueprint.md 已点名角色要求“审批人处理申请的完整流程”，但 experience_blueprint.md 还没有给出对应的清晰路径、页面或职责承接。
- 承接检查：business_blueprint.md 已点名角色要求“管理员配置自助申请权限的完整流程”，但 experience_blueprint.md 还没有给出对应的清晰路径、页面或职责承接。
- 承接检查：business_blueprint.md 明确要求主流程闭环包含“回写端：授权成功通知、驳回通知、状态变更通知”，但 experience_blueprint.md 还没有把这一段转成清晰的用户流程、系统反馈或结果去向。

## Infos

- business gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：3/4
- 自然语言承接检查：异常与阻断覆盖：3/6
- 自然语言承接检查：状态与反馈覆盖：2/2
- 自然语言承接检查：角色路径覆盖：0/3
- 自然语言承接检查：设计指南装配：0 条
- 自然语言承接检查：风险保护承接：0/2

## 自然语言承接检查

- 角色路径覆盖：0/3
- 主流程闭环覆盖：3/4
- 异常与阻断覆盖：3/6
- 状态与反馈覆盖：2/2
- 风险保护承接：0/2
- 设计指南装配：0 条

## Machine Status

- 机器可读状态文件：`projects/self-permission-apply/workspace/check_status.json`
