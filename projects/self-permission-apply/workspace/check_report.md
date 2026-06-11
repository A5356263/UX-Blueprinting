# Check Report｜人读说明版

> 本文件是 `projects/self-permission-apply/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## 1. 检查结果

- status: warning
- 是否阻断: 否
- has_blocker: false
- blocker_count: 0
- warning_count: 5
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
- experience_blueprint.md 主流程、异常或页面设计核心区包含表格,建议优先使用节点化 Markdown 层级表达
- 承接检查：business_blueprint.md 已把“可申请范围的安全控制”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“员工提交超出范围的申请”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- 承接检查：business_blueprint.md 已把“审批人缺失或无法处理”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。

## Infos

- business gate 状态:passed
- facts gate 状态:passed
- 自然语言承接检查：主流程闭环覆盖：2/2
- 自然语言承接检查：异常与阻断覆盖：2/4
- 自然语言承接检查：状态与反馈覆盖：2/2
- 自然语言承接检查：角色路径覆盖：3/3
- 自然语言承接检查：设计指南装配：0 条
- 自然语言承接检查：风险保护承接：1/2

## 自然语言承接检查

- 角色路径覆盖：3/3
- 主流程闭环覆盖：2/2
- 异常与阻断覆盖：2/4
- 状态与反馈覆盖：2/2
- 风险保护承接：1/2
- 设计指南装配：0 条

## Machine Status

- 机器可读状态文件：`projects/self-permission-apply/workspace/check_status.json`
