# Check Report

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 9
- info_count: 8

## Output Status

- projects/employee-self-permission/workspace/facts.md: present
- projects/employee-self-permission/workspace/business_blueprint.md: present
- projects/employee-self-permission/workspace/experience_blueprint.md: present
- projects/employee-self-permission/workspace/gap_list.md: present
- projects/employee-self-permission/workspace/check_report.md: present
- projects/employee-self-permission/workspace/check_status.json: present

## Blockers

- none

## Warnings

- business gate 状态为 warning
- business_blueprint.md 价值/成本/认知负担评估检测不到结构化内容，请确认已在自然语言中覆盖
- business_blueprint.md 判断依据未覆盖足够的核心判断
- business_blueprint.md 未形成显式业务判断，建议明确各项判断的结论和依据
- experience_blueprint.md 未发现明确的页面/弹窗/抽屉设计，页面级消费不足
- facts gate 状态为 warning
- facts.md 未使用显式编号体系（当前已是自然语言规范，此检查仅作兼容保留）
- final validate：business_blueprint.md 的判断依据仍需补充，建议明确判断与事实的承接关系
- gap_list.md 仍包含占位内容

## Infos

- coverage: business_judgments_consumed_by_experience: 0
- coverage: facts_covered_by_business: 0
- coverage: facts_covered_by_experience: 0
- coverage: orphan_fact_count: 0
- coverage: orphan_judgment_count: 0
- coverage: orphan_page_count: 1
- experience gate 状态：passed
- facts.md 使用自然语言表达（未使用旧版编号体系），覆盖检查将以章节级承接为准

## Coverage Check

- facts_covered_by_business: 0
- facts_covered_by_experience: 0
- business_judgments_consumed_by_experience: 0
- orphan_fact_count: 0
- orphan_judgment_count: 0
- orphan_page_count: 1

## Machine Status

- 机器可读状态文件：`projects/employee-self-permission/workspace/check_status.json`
