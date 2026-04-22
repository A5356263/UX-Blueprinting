# Stage Gate Report

## Summary

- status: failed
- has_blocker: true
- blocker_count: 3
- warning_count: 1
- info_count: 1

- project_id: _template
- stage: business
- next_stage: experience
- can_proceed: false

## Checked Files

- projects/_template/workspace/facts.md
- projects/_template/workspace/business_blueprint.md
- projects/_template/runtime/provenance.json
- projects/_template/runtime/gates/facts_gate_status.json

## Blockers

- provenance: provenance.source_hash 缺失
- provenance: provenance.task_card_hash 缺失
- facts 阶段未通过，不能进入业务蓝图阶段

## Warnings

- business_blueprint.md 可能越过阶段边界：包含 高保真视觉

## Infos

- business_blueprint.md 已承接 12 条事实
