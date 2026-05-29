# Check Report｜人读说明版

> 本文件是 `projects/self-service-permission/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 9
- info_count: 7

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

- business gate 状态为 warning
- business_blueprint.md 正文疑似直接复制知识库字段名、枚举值、英文状态或模型名，请转译为业务方能理解的话；如确需保留原始术语，请移动到附录“事实、知识与判断追踪”。
- experience gate 状态为 warning
- experience_blueprint.md 主交互流程缺少可对应的节点详情标题
- 承接检查：business_blueprint.md 已把“服务人员不开放”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“白名单为空时的空状态和提示”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- 承接检查：business_blueprint.md 已把“超管角色不进入白名单”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已点名角色要求“审批端：审批处理页（复用审批中台）”，但 experience_blueprint.md 还没有给出对应的清晰路径、页面或职责承接。
- 承接检查：business_blueprint.md 已点名角色要求“管理者端：自助申请配置页”，但 experience_blueprint.md 还没有给出对应的清晰路径、页面或职责承接。

## Infos

- facts gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：3/3
- 自然语言承接检查：异常与阻断覆盖：4/5
- 自然语言承接检查：状态与反馈覆盖：3/3
- 自然语言承接检查：角色路径覆盖：1/3
- 自然语言承接检查：设计指南装配：2 条
- 自然语言承接检查：风险保护承接：3/5

## 自然语言承接检查

- 角色路径覆盖：1/3
- 主流程闭环覆盖：3/3
- 异常与阻断覆盖：4/5
- 状态与反馈覆盖：3/3
- 风险保护承接：3/5
- 设计指南装配：2 条

## Machine Status

- 机器可读状态文件：`projects/self-service-permission/workspace/check_status.json`
