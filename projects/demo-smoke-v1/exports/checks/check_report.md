# Check Report

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 2
- info_count: 8

## Output Status

- projects/demo-smoke-v1/workspace/facts.md: present
- projects/demo-smoke-v1/workspace/business_blueprint.md: present
- projects/demo-smoke-v1/workspace/experience_blueprint.md: present
- projects/demo-smoke-v1/workspace/gap_list.md: present
- projects/demo-smoke-v1/workspace/check_report.md: present
- projects/demo-smoke-v1/workspace/check_status.json: present

## Blockers

- none

## Warnings

- experience gate 状态为 warning
- 存在未被体验层消费的业务判断：J-03, J-04, J-05, POS-02

## Infos

- business gate 状态：passed
- coverage: business_judgments_consumed_by_experience: 3
- coverage: facts_covered_by_business: 6
- coverage: facts_covered_by_experience: 5
- coverage: orphan_fact_count: 0
- coverage: orphan_judgment_count: 4
- coverage: orphan_page_count: 0
- facts gate 状态：passed

## Coverage Check

- facts_covered_by_business: 6
- facts_covered_by_experience: 5
- business_judgments_consumed_by_experience: 3
- orphan_fact_count: 0
- orphan_judgment_count: 4
- orphan_page_count: 0

## Machine Status

- 机器可读状态文件：`projects/demo-smoke-v1/workspace/check_status.json`
