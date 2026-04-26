# Check Report

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 1
- info_count: 13

## Output Status

- projects/003/workspace/facts.md: present
- projects/003/workspace/business_blueprint.md: present
- projects/003/workspace/experience_blueprint.md: present
- projects/003/workspace/gap_list.md: present
- projects/003/workspace/check_report.md: present
- projects/003/workspace/check_status.json: present

## Blockers

- none

## Warnings

- 存在未被后续消费的事实：F-AC01, F-AC02, F-AC03, F-AC04, F-AC05, F-AC06

## Infos

- business gate 状态：passed
- business_blueprint.md 已承接 12 条事实
- coverage: business_judgments_consumed_by_experience: 5
- coverage: facts_covered_by_business: 12
- coverage: facts_covered_by_experience: 3
- coverage: orphan_fact_count: 46
- coverage: orphan_judgment_count: 0
- coverage: orphan_page_count: 0
- experience gate 状态：passed
- experience_blueprint.md 已引用 3 个设计原则 ID
- experience_blueprint.md 已承接 3 条事实
- experience_blueprint.md 已承接 5 条业务判断
- facts gate 状态：passed

## Coverage Check

- facts_covered_by_business: 12
- facts_covered_by_experience: 3
- business_judgments_consumed_by_experience: 5
- orphan_fact_count: 46
- orphan_judgment_count: 0
- orphan_page_count: 0

## Machine Status

- 机器可读状态文件：`projects/003/workspace/check_status.json`
