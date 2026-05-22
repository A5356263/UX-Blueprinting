# Stage Gate Report

## Summary

- status: failed
- has_blocker: true
- blocker_count: 3
- warning_count: 2
- info_count: 0

- project_id: permission-dimension-query
- stage: experience
- next_stage: final-validate
- can_proceed: false

## Checked Files

- projects/permission-dimension-query/workspace/facts.md
- projects/permission-dimension-query/workspace/business_blueprint.md
- projects/permission-dimension-query/workspace/experience_blueprint.md
- projects/permission-dimension-query/runtime/provenance.json
- projects/permission-dimension-query/runtime/gates/business_gate_status.json

## Blockers

- provenance: provenance.command_chain 缺少：generate-business
- 缺少 business 阶段 gate 结果，请先运行 gate-business
- experience_blueprint.md 缺少栏目：## 5. 页面 / 弹窗 / 抽屉设计

## Warnings

- experience_blueprint.md 页面设计检测不到结构化内容，请确认已用自然语言写清各页面
- experience_blueprint.md 附录：依据与追踪内容偏少

## Infos

- none
