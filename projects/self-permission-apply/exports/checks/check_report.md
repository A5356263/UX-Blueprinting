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

- business gate 状态为 warning
- business_blueprint.md 正文疑似直接复制知识库字段名、枚举值、英文状态或模型名，请转译为业务方能理解的话；如确需保留原始术语，请移动到附录“事实、知识与判断追踪”。
- experience gate 状态为 warning
- experience_blueprint.md 主流程、异常或页面设计核心区包含表格，建议优先使用节点化 Markdown 层级表达
- 承接检查：business_blueprint.md 已把“可申请范围过宽 → 通过配置页的默认行为和提示保...”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“可申请角色被管理员在审批中移除 → 在途申请不受...”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- 承接检查：business_blueprint.md 已把“审批链路断裂 → 通过兜底机制和异常提醒保护”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“概念增殖 → 通过界面语言和操作路径保护”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“管理员在审批期间直接给员工分配了同一角色 → 需...”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- 承接检查：business_blueprint.md 已把“能力关闭时员工正在填写申请 → 提示能力已关闭”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- 承接检查：business_blueprint.md 要求解释“权限来源（管理员分配 vs 自助申请）及区分方式”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。
- 承接检查：business_blueprint.md 要求解释“能力开启/关闭状态及对应员工端表现”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。

## Infos

- facts gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：4/4
- 自然语言承接检查：异常与阻断覆盖：2/5
- 自然语言承接检查：状态与反馈覆盖：1/3
- 自然语言承接检查：角色路径覆盖：3/3
- 自然语言承接检查：设计指南装配：0 条
- 自然语言承接检查：风险保护承接：0/3

## 自然语言承接检查

- 角色路径覆盖：3/3
- 主流程闭环覆盖：4/4
- 异常与阻断覆盖：2/5
- 状态与反馈覆盖：1/3
- 风险保护承接：0/3
- 设计指南装配：0 条

## Machine Status

- 机器可读状态文件：`projects/self-permission-apply/workspace/check_status.json`
