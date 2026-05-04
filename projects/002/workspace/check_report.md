# Check Report

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 12
- info_count: 1

## Output Status

- projects/002/workspace/facts.md: present
- projects/002/workspace/business_blueprint.md: present
- projects/002/workspace/experience_blueprint.md: present
- projects/002/workspace/gap_list.md: present
- projects/002/workspace/check_report.md: present
- projects/002/workspace/check_status.json: present

## Blockers

- none

## Warnings

- business_blueprint.md 未形成显式业务判断，建议明确各项判断的结论和依据
- facts.md 未使用显式编号体系（当前已是自然语言规范，此检查仅作兼容保留）
- business_blueprint.md 备选路径比较检测不到结构化内容，请确认已用自然语言表达
- business_blueprint.md 价值/成本/认知负担评估检测不到结构化内容，请确认已在自然语言中覆盖
- business_blueprint.md 方案承接要求检测不到结构化内容，请确认已用自然语言表达
- business_blueprint.md 判断依据未覆盖足够的核心判断
- final validate：business_blueprint.md 的判断依据仍需补充，建议明确判断与事实的承接关系
- experience_blueprint.md 交互流程检测不到结构化内容，请确认已用自然语言写清各节点
- experience_blueprint.md 页面设计检测不到结构化内容，请确认已用自然语言写清各页面
- experience_blueprint.md 附录：依据与追踪内容偏少
- business gate 状态为 warning
- experience gate 状态为 warning

## Infos

- facts gate 状态：passed

## Coverage Check

- not_run

## Machine Status

- 机器可读状态文件：`projects/002/workspace/check_status.json`
