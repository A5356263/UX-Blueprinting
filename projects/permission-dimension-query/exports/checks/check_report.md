# Check Report｜人读说明版

> 本文件是 `projects/permission-dimension-query/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## 1. 检查结果

- status: warning
- 是否阻断: 否
- has_blocker: false
- blocker_count: 0
- warning_count: 9
- info_count: 7

## Output Status

- projects/permission-dimension-query/workspace/facts.md: present
- projects/permission-dimension-query/workspace/business_blueprint.md: present
- projects/permission-dimension-query/workspace/experience_blueprint.md: present
- projects/permission-dimension-query/workspace/gap_list.md: present
- projects/permission-dimension-query/workspace/check_report.md: present
- projects/permission-dimension-query/workspace/check_status.json: present

## Blockers

- none

## Warnings

- business gate 状态为 warning
- business_blueprint.md 规则与边界描述偏少
- business_blueprint.md 附录没有自然说明主要依据来自 facts 的哪些章节，判断依据承接仍偏弱
- business_blueprint.md 风险与保护策略内容偏少
- experience gate 状态为 warning
- experience_blueprint.md 主流程、异常或页面设计核心区包含表格，建议优先使用节点化 Markdown 层级表达
- 承接检查：business_blueprint.md 已把“数据加载失败：系统异常时提供重试入口”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- 承接检查：business_blueprint.md 已把“查询范围的二次校验：即使入口可见，查询特定对象时...”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 要求解释“如果是通过角色获得的，标注来源角色名称”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。

## Infos

- facts gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：1/1
- 自然语言承接检查：异常与阻断覆盖：3/4
- 自然语言承接检查：状态与反馈覆盖：2/3
- 自然语言承接检查：角色路径覆盖：3/3
- 自然语言承接检查：设计指南装配：4 条
- 自然语言承接检查：风险保护承接：2/3

## 自然语言承接检查

- 角色路径覆盖：3/3
- 主流程闭环覆盖：1/1
- 异常与阻断覆盖：3/4
- 状态与反馈覆盖：2/3
- 风险保护承接：2/3
- 设计指南装配：4 条

## Machine Status

- 机器可读状态文件：`projects/permission-dimension-query/workspace/check_status.json`
