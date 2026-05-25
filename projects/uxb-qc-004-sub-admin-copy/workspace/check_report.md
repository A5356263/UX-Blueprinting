# Check Report｜人读说明版

> 本文件是 `projects/uxb-qc-004-sub-admin-copy/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 11
- info_count: 7

## Output Status

- projects/uxb-qc-004-sub-admin-copy/workspace/facts.md: present
- projects/uxb-qc-004-sub-admin-copy/workspace/business_blueprint.md: present
- projects/uxb-qc-004-sub-admin-copy/workspace/experience_blueprint.md: present
- projects/uxb-qc-004-sub-admin-copy/workspace/gap_list.md: present
- projects/uxb-qc-004-sub-admin-copy/workspace/check_report.md: present
- projects/uxb-qc-004-sub-admin-copy/workspace/check_status.json: present

## Blockers

- none

## Warnings

- business gate 状态为 warning
- business_blueprint.md 价值/成本/认知负担评估检测不到结构化内容，请确认已在自然语言中覆盖
- business_blueprint.md 方案承接要求覆盖不足，建议至少覆盖角色/流程/状态/异常/风险中的 3 类
- experience gate 状态为 warning
- experience_blueprint.md 待确认问题为空，建议显式标注不确定项
- experience_blueprint.md 核心区包含表格，建议改为节点化 Markdown 层级表达
- experience_blueprint.md 附录：依据与追踪内容偏少
- experience_blueprint.md 页面设计检测不到结构化内容，请确认已用自然语言写清各页面
- gap_list.md 仍包含占位内容
- 承接检查：business_blueprint.md 已把“加入状态口径冲突：已启用≠已加入——建议统一为"...”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“操作记录不可读：200个对象全部列出——建议超过...”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。

## Infos

- facts gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：0/0
- 自然语言承接检查：异常与阻断覆盖：0/0
- 自然语言承接检查：状态与反馈覆盖：0/0
- 自然语言承接检查：角色路径覆盖：1/1
- 自然语言承接检查：设计指南装配：3 条
- 自然语言承接检查：风险保护承接：2/4

## 自然语言承接检查

- 角色路径覆盖：1/1
- 主流程闭环覆盖：0/0
- 异常与阻断覆盖：0/0
- 状态与反馈覆盖：0/0
- 风险保护承接：2/4
- 设计指南装配：3 条

## Machine Status

- 机器可读状态文件：`projects/uxb-qc-004-sub-admin-copy/workspace/check_status.json`
