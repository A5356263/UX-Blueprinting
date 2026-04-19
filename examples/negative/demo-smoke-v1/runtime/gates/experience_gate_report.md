# Stage Gate Report

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 2
- info_count: 4

- project_id: demo-smoke-v1
- stage: experience
- next_stage: final-validate
- can_proceed: true

## Checked Files

- examples/negative/demo-smoke-v1/workspace/facts.md
- examples/negative/demo-smoke-v1/workspace/business_blueprint.md
- examples/negative/demo-smoke-v1/workspace/experience_blueprint.md
- examples/negative/demo-smoke-v1/runtime/context_manifest.json
- examples/negative/demo-smoke-v1/runtime/provenance.json
- examples/negative/demo-smoke-v1/runtime/gates/business_gate_status.json

## Blockers

- none

## Warnings

- context_manifest 未确认页面结构语义来源，体验阶段的结构判断可能依据不足
- context_manifest 警告：任务已引用权限域 Wiki，但未显式命中页面结构语义页，体验阶段可能无法稳定判断结构变化。

## Infos

- business 阶段状态：passed
- experience_blueprint.md 已承接 12 条事实
- experience_blueprint.md 已承接 11 条业务判断
- experience_blueprint.md 已引用 3 个设计原则 ID
