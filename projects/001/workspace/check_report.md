# Check Report

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 4
- info_count: 12

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

- business gate 状态为 warning
- business_blueprint.md 未显式保留开放问题或缺口
- 存在未被体验层消费的业务判断：J-03, J-04
- 存在未被后续消费的事实：F-AC04, F-AC05, F-AC06, F-AC07, F-AC08, F-D01

## Infos

- business_blueprint.md 已承接 12 条事实
- coverage: business_judgments_consumed_by_experience: 2
- coverage: facts_covered_by_business: 12
- coverage: facts_covered_by_experience: 3
- coverage: orphan_fact_count: 34
- coverage: orphan_judgment_count: 2
- coverage: orphan_page_count: 0
- experience gate 状态：passed
- experience_blueprint.md 已引用 6 个设计原则 ID
- experience_blueprint.md 已承接 2 条业务判断
- experience_blueprint.md 已承接 3 条事实
- facts gate 状态：passed

## Coverage Check

- facts_covered_by_business: 12
- facts_covered_by_experience: 3
- business_judgments_consumed_by_experience: 2
- orphan_fact_count: 34
- orphan_judgment_count: 2
- orphan_page_count: 0

## Machine Status

- 机器可读状态文件：`projects/001/workspace/check_status.json`
