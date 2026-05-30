# Check Report｜人读说明版

> 本文件是 `projects/self-service-permission/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 4
- info_count: 1

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

- business_blueprint.md 正文疑似直接复制知识库字段名、枚举值、英文状态或模型名，请转译为业务方能理解的话；如确需保留原始术语，请移动到附录“事实、知识与判断追踪”。
- experience_blueprint.md 主交互流程缺少可对应的节点详情标题
- business gate 状态为 warning
- experience gate 状态为 warning

## Infos

- facts gate 状态：passed

## 自然语言承接检查

- not_run

## Machine Status

- 机器可读状态文件：`projects/self-service-permission/workspace/check_status.json`
