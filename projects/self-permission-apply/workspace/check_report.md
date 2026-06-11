# Check Report｜人读说明版

> 本文件是 `projects/self-permission-apply/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## 1. 检查结果

- status: warning
- 是否阻断: 否
- has_blocker: false
- blocker_count: 0
- warning_count: 2
- info_count: 2

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

- experience_blueprint.md 主流程、异常或页面设计核心区包含表格，建议优先使用节点化 Markdown 层级表达
- experience gate 状态为 warning

## Infos

- facts gate 状态：passed
- business gate 状态：passed

## 自然语言承接检查

- not_run

## Machine Status

- 机器可读状态文件：`projects/self-permission-apply/workspace/check_status.json`
