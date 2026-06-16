# Stage Gate Report

## 1. 检查结果

- status: warning
- 是否阻断: 否
- has_blocker: false
- blocker_count: 0
- warning_count: 3
- info_count: 1

- project_id: permission-dimension-query
- stage: business
- next_stage: experience
- can_proceed: true

## 2. 问题列表

- warning: business_blueprint.md 风险与保护策略内容偏少
- warning: business_blueprint.md 规则与边界描述偏少
- warning: business_blueprint.md 附录没有自然说明主要依据来自 facts 的哪些章节，判断依据承接仍偏弱
- info: facts 阶段状态：passed

## 3. 检查范围

- projects/permission-dimension-query/workspace/facts.md
- projects/permission-dimension-query/workspace/business_blueprint.md
- projects/permission-dimension-query/runtime/provenance.json
- projects/permission-dimension-query/runtime/gates/facts_gate_status.json

## 4. 建议处理

- 当前为 warning，可复核后接受，或补强对应内容后重跑。
