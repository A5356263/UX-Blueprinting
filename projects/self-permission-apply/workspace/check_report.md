# Check Report｜人读说明版

> 本文件是 `projects/self-permission-apply/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 8
- info_count: 8

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
- 承接检查：business_blueprint.md 已把“提交时审批流程不可用”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- 承接检查：business_blueprint.md 已把“申请时角色已被管理员直接授予（重复授权）”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- 承接检查：business_blueprint.md 已把“管理员忘记标记角色 → 能力开启后若无可申请角色...”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“角色权限说明不清晰导致员工误申请 → 角色列表需...”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 明确要求主流程闭环包含“员工查看结果 → 确认权限生效”，但 experience_blueprint.md 还没有把这一段转成清晰的用户流程、系统反馈或结果去向。
- 承接检查：business_blueprint.md 要求解释“能力开启和关闭对员工端的不同影响”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。

## Infos

- business gate 状态：passed
- facts gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：4/5
- 自然语言承接检查：异常与阻断覆盖：5/7
- 自然语言承接检查：状态与反馈覆盖：3/4
- 自然语言承接检查：角色路径覆盖：3/3
- 自然语言承接检查：设计指南装配：0 条
- 自然语言承接检查：风险保护承接：2/4

## 自然语言承接检查

- 角色路径覆盖：3/3
- 主流程闭环覆盖：4/5
- 异常与阻断覆盖：5/7
- 状态与反馈覆盖：3/4
- 风险保护承接：2/4
- 设计指南装配：0 条

## Machine Status

- 机器可读状态文件：`projects/self-permission-apply/workspace/check_status.json`
