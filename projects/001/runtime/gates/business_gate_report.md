# Stage Gate Report

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 3
- info_count: 1

- project_id: 001
- stage: business
- next_stage: experience
- can_proceed: true

## Checked Files

- projects/001/workspace/facts.md
- projects/001/workspace/business_blueprint.md
- projects/001/runtime/provenance.json
- projects/001/runtime/gates/facts_gate_status.json

## Blockers

- none

## Warnings

- business_blueprint.md 未形成显式业务判断，建议明确各项判断的结论和依据
- facts.md 未使用显式编号体系（当前已是自然语言规范，此检查仅作兼容保留）
- business_blueprint.md 判断依据未覆盖足够的核心判断

## Infos

- facts 阶段状态：passed
