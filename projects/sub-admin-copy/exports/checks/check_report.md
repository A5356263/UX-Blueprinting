# Check Report｜人读说明版

> 本文件是 `projects/sub-admin-copy/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 9
- info_count: 7

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
- business_blueprint.md 价值/成本/认知负担评估检测不到结构化内容，请确认已在自然语言中覆盖
- experience gate 状态为 warning
- experience_blueprint.md 附录：依据与追踪内容偏少
- gap_list.md 仍包含占位内容
- 承接检查：business_blueprint.md 已把“批量误操作 → experience 需在确认前...”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“无互审模式下缺乏二次确认 → experienc...”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“部分成功反馈不清晰 → experience 需...”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 设计指南消费检查：knowledge_usage_report.json 未记录 experience 阶段实际消费的 design guideline。

## Infos

- facts gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：1/1
- 自然语言承接检查：异常与阻断覆盖：7/7
- 自然语言承接检查：状态与反馈覆盖：5/5
- 自然语言承接检查：角色路径覆盖：3/3
- 自然语言承接检查：设计指南消费：0 条
- 自然语言承接检查：风险保护承接：0/3

## 自然语言承接检查

- 角色路径覆盖：3/3
- 主流程闭环覆盖：1/1
- 异常与阻断覆盖：7/7
- 状态与反馈覆盖：5/5
- 风险保护承接：0/3
- 设计指南消费：0 条

## Machine Status

- 机器可读状态文件：`projects/sub-admin-copy/workspace/check_status.json`
