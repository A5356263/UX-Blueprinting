# Check Report｜人读说明版

> 本文件是 `projects/uxb-qc-005-self-service-permission-tricky/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 9
- info_count: 7

## Output Status

- projects/uxb-qc-005-self-service-permission-tricky/workspace/facts.md: present
- projects/uxb-qc-005-self-service-permission-tricky/workspace/business_blueprint.md: present
- projects/uxb-qc-005-self-service-permission-tricky/workspace/experience_blueprint.md: present
- projects/uxb-qc-005-self-service-permission-tricky/workspace/gap_list.md: present
- projects/uxb-qc-005-self-service-permission-tricky/workspace/check_report.md: present
- projects/uxb-qc-005-self-service-permission-tricky/workspace/check_status.json: present

## Blockers

- none

## Warnings

- business gate 状态为 warning
- business_blueprint.md 价值/成本/认知负担评估检测不到结构化内容，请确认已在自然语言中覆盖
- business_blueprint.md 方案承接要求覆盖不足，建议至少覆盖角色/流程/状态/异常/风险中的 3 类
- business_blueprint.md 附录没有自然说明主要依据来自 facts 的哪些章节，判断依据承接仍偏弱
- experience gate 状态为 warning
- experience_blueprint.md 待确认问题为空，建议显式标注不确定项
- experience_blueprint.md 核心区包含表格，建议改为节点化 Markdown 层级表达
- experience_blueprint.md 附录：依据与追踪内容偏少
- gap_list.md 仍包含占位内容

## Infos

- facts gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：0/0
- 自然语言承接检查：异常与阻断覆盖：0/0
- 自然语言承接检查：状态与反馈覆盖：0/0
- 自然语言承接检查：角色路径覆盖：2/2
- 自然语言承接检查：设计指南装配：5 条
- 自然语言承接检查：风险保护承接：5/5

## 自然语言承接检查

- 角色路径覆盖：2/2
- 主流程闭环覆盖：0/0
- 异常与阻断覆盖：0/0
- 状态与反馈覆盖：0/0
- 风险保护承接：5/5
- 设计指南装配：5 条

## Machine Status

- 机器可读状态文件：`projects/uxb-qc-005-self-service-permission-tricky/workspace/check_status.json`
