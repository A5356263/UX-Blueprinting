# Stage Gate Report

## Summary

- status: failed
- has_blocker: true
- blocker_count: 3
- warning_count: 4
- info_count: 0

- project_id: uxb-qc-002-permission-query
- stage: experience
- next_stage: final-validate
- can_proceed: false

## Checked Files

- projects/uxb-qc-002-permission-query/workspace/facts.md
- projects/uxb-qc-002-permission-query/workspace/business_blueprint.md
- projects/uxb-qc-002-permission-query/workspace/experience_blueprint.md
- projects/uxb-qc-002-permission-query/runtime/provenance.json
- projects/uxb-qc-002-permission-query/runtime/gates/business_gate_status.json

## Blockers

- provenance: provenance.command_chain 缺少：generate-business
- 缺少 business 阶段 gate 结果，请先运行 gate-business
- experience_blueprint.md 仅覆盖 happy path，未显式覆盖异常态 / 阻断态

## Warnings

- experience_blueprint.md 页面设计检测不到结构化内容，请确认已用自然语言写清各页面
- experience_blueprint.md 待确认问题为空，建议显式标注不确定项
- experience_blueprint.md 附录：依据与追踪内容偏少
- experience_blueprint.md 核心区包含表格，建议改为节点化 Markdown 层级表达

## Infos

- none
