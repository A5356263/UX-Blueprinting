# Check Report｜人读说明版

> 本文件是 `projects/sub-admin-copy/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 10
- info_count: 8

## Output Status

- projects/sub-admin-copy/workspace/facts.md: present
- projects/sub-admin-copy/workspace/business_blueprint.md: present
- projects/sub-admin-copy/workspace/experience_blueprint.md: present
- projects/sub-admin-copy/workspace/gap_list.md: present
- projects/sub-admin-copy/workspace/check_report.md: present
- projects/sub-admin-copy/workspace/check_status.json: present

## Blockers

- none

## Warnings

- business gate 状态为 warning
- business_blueprint.md 风险与保护策略内容偏少
- gap_list.md 仍包含占位内容
- 承接检查：business_blueprint.md 已把“复制对象超过 200 人时的限制提示”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“操作记录必须在复制成功后立即生成，不得遗漏”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“未选择复制信息就确认（提示"请选择复制信息"）”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- 承接检查：business_blueprint.md 已把“未选择复制对象就确认（提示"请选择至少一名复制对...”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- 承接检查：business_blueprint.md 要求解释“复制对象的已选择状态（展示在输入框中）与可编辑状...”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。
- 承接检查：business_blueprint.md 要求解释“弹窗中复制信息的默认状态（全部勾选）与可修改状态”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。
- 设计指南消费检查：knowledge_usage_report.json 未记录 experience 阶段实际消费的 design guideline。

## Infos

- experience gate 状态：passed
- facts gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：2/2
- 自然语言承接检查：异常与阻断覆盖：3/5
- 自然语言承接检查：状态与反馈覆盖：1/3
- 自然语言承接检查：角色路径覆盖：1/1
- 自然语言承接检查：设计指南消费：0 条
- 自然语言承接检查：风险保护承接：2/4

## 自然语言承接检查

- 角色路径覆盖：1/1
- 主流程闭环覆盖：2/2
- 异常与阻断覆盖：3/5
- 状态与反馈覆盖：1/3
- 风险保护承接：2/4
- 设计指南消费：0 条

## Machine Status

- 机器可读状态文件：`projects/sub-admin-copy/workspace/check_status.json`
