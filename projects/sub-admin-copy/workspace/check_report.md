# Check Report｜人读说明版

> 本文件是 `projects/sub-admin-copy/workspace/check_status.json` 的人读说明版。
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

- projects/sub-admin-copy/workspace/facts.md: present
- projects/sub-admin-copy/workspace/business_note.md: missing
- projects/sub-admin-copy/workspace/business_blueprint_lite.md: present
- projects/sub-admin-copy/workspace/experience_blueprint.md: present

## Blockers

- none

## Warnings

- coverage-lite: experience 未明显承接轻量业务产物中的维度：边界
- experience_lite gate 状态为 warning

## Infos

- business_lite gate 状态：passed
- 轻量承接检查：covered_signals=5 missing_signals=1

## 自然语言承接检查

- covered_signals=5 missing_signals=1

## Machine Status

- 机器可读状态文件：`projects/sub-admin-copy/workspace/check_status.json`
