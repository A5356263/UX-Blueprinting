# Stage Gate Report

## 1. 检查结果

- status: failed
- 是否阻断: 是
- has_blocker: true
- blocker_count: 2
- warning_count: 0
- info_count: 1

- project_id: sub-admin-copy
- stage: business
- next_stage: experience
- can_proceed: false

## 2. 问题列表

- blocker: provenance: provenance.command_chain 缺少：generate-business
- blocker: 缺少 business_blueprint.md
- info: facts 阶段状态：passed

## 3. 检查范围

- projects/sub-admin-copy/workspace/facts.md
- projects/sub-admin-copy/workspace/business_blueprint.md
- projects/sub-admin-copy/runtime/provenance.json
- projects/sub-admin-copy/runtime/gates/facts_gate_status.json

## 4. 建议处理

- 存在 blocker，请先修复对应正式产物后再重跑当前检查。
