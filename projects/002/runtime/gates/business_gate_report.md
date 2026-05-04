# Stage Gate Report

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 6
- info_count: 1

- project_id: 002
- stage: business
- next_stage: experience
- can_proceed: true

## Checked Files

- projects/002/workspace/facts.md
- projects/002/workspace/business_blueprint.md
- projects/002/runtime/provenance.json
- projects/002/runtime/gates/facts_gate_status.json

## Blockers

- none

## Warnings

- business_blueprint.md 未形成显式业务判断，建议明确各项判断的结论和依据
- facts.md 未使用显式编号体系（当前已是自然语言规范，此检查仅作兼容保留）
- business_blueprint.md 备选路径比较检测不到结构化内容，请确认已用自然语言表达
- business_blueprint.md 价值/成本/认知负担评估检测不到结构化内容，请确认已在自然语言中覆盖
- business_blueprint.md 方案承接要求检测不到结构化内容，请确认已用自然语言表达
- business_blueprint.md 判断依据未覆盖足够的核心判断

## Infos

- facts 阶段状态：passed
