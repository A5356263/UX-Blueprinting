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
- business_blueprint.md `## 9. 待确认问题` 建议使用“问题标题 + 影响 + 建议确认方”的分块结构
- business_blueprint.md 方案承接要求覆盖不足，建议至少覆盖角色/流程/状态/异常/风险中的 3 类
- experience gate 状态为 warning
- experience_blueprint.md `## 8. 待确认问题` 建议使用“问题标题 + 影响 + 建议确认方”的分块结构

## Infos

- facts gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：0/0
- 自然语言承接检查：异常与阻断覆盖：0/0
- 自然语言承接检查：状态与反馈覆盖：0/0
- 自然语言承接检查：角色路径覆盖：not_declared
- 自然语言承接检查：设计指南装配：1 条
- 自然语言承接检查：风险保护承接：0/0

## 自然语言承接检查

- 角色路径覆盖：not_declared
- 主流程闭环覆盖：0/0
- 异常与阻断覆盖：0/0
- 状态与反馈覆盖：0/0
- 风险保护承接：0/0
- 设计指南装配：1 条

## Machine Status

- 机器可读状态文件：`projects/self-permission-apply/workspace/check_status.json`
