# Check Report

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 6
- info_count: 9

## Output Status

- projects/001/workspace/facts.md: present
- projects/001/workspace/business_blueprint.md: present
- projects/001/workspace/experience_blueprint.md: present
- projects/001/workspace/gap_list.md: present
- projects/001/workspace/check_report.md: present
- projects/001/workspace/check_status.json: present

## Blockers

- none

## Warnings

- experience gate 状态为 warning
- experience 追踪映射未承接任何状态/异常/治理/依赖类业务判断，建议补充关键判断的页面/流程/状态/文案落点
- experience_blueprint.md 核心区包含表格，建议改为节点化 Markdown 层级表达
- experience_blueprint.md 核心区存在明显机器化表达
- experience_blueprint.md 核心区页面名重复较多，建议继续语义去重
- 存在未被后续消费的事实：F-AC01, F-AC02, F-AC03, F-AC04, F-AC05, F-AC06

## Infos

- business gate 状态：passed
- business_blueprint.md 已承接 12 条事实
- coverage: business_judgments_consumed_by_experience: 4
- coverage: facts_covered_by_business: 12
- coverage: facts_covered_by_experience: 3
- coverage: orphan_fact_count: 45
- coverage: orphan_judgment_count: 0
- coverage: orphan_page_count: 0
- facts gate 状态：passed

## Coverage Check

- facts_covered_by_business: 12
- facts_covered_by_experience: 3
- business_judgments_consumed_by_experience: 4
- orphan_fact_count: 45
- orphan_judgment_count: 0
- orphan_page_count: 0

## Machine Status

- 机器可读状态文件：`projects/001/workspace/check_status.json`
