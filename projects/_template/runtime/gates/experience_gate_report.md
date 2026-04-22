# Stage Gate Report

## Summary

- status: failed
- has_blocker: true
- blocker_count: 3
- warning_count: 0
- info_count: 3

- project_id: _template
- stage: experience
- next_stage: final-validate
- can_proceed: false

## Checked Files

- projects/_template/workspace/facts.md
- projects/_template/workspace/business_blueprint.md
- projects/_template/workspace/experience_blueprint.md
- projects/_template/runtime/provenance.json
- projects/_template/runtime/gates/business_gate_status.json

## Blockers

- provenance: provenance.source_hash 缺失
- provenance: provenance.task_card_hash 缺失
- business 阶段未通过，不能进入体验蓝图阶段

## Warnings

- none

## Infos

- experience_blueprint.md 已承接 3 条事实
- experience_blueprint.md 已承接 2 条业务判断
- experience_blueprint.md 已引用 3 个设计原则 ID
