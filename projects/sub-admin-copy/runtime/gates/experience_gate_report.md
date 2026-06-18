# Stage Gate Report

## 1. 检查结果

- status: failed
- 是否阻断: 是
- has_blocker: true
- blocker_count: 3
- warning_count: 1
- info_count: 0

- project_id: sub-admin-copy
- stage: experience
- next_stage: final-validate
- can_proceed: false

## 2. 问题列表

- blocker: provenance: provenance.command_chain 缺少：generate-business, generate-experience
- blocker: business 阶段未通过，不能进入体验蓝图阶段
- blocker: 缺少 business_blueprint.md
- warning: experience_blueprint.md 主流程、异常或页面设计核心区包含表格，建议优先使用节点化 Markdown 层级表达

## 3. 检查范围

- projects/sub-admin-copy/workspace/facts.md
- projects/sub-admin-copy/workspace/business_blueprint.md
- projects/sub-admin-copy/workspace/experience_blueprint.md
- projects/sub-admin-copy/runtime/provenance.json
- projects/sub-admin-copy/runtime/gates/business_gate_status.json

## 4. 建议处理

- 存在 blocker，请先修复对应正式产物后再重跑当前检查。
