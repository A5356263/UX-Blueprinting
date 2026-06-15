# Stage Gate Report

## 1. 检查结果

- status: warning
- 是否阻断: 否
- has_blocker: false
- blocker_count: 0
- warning_count: 2
- info_count: 1

- project_id: self-permission-apply
- stage: business
- next_stage: experience
- can_proceed: true

## 2. 问题列表

- warning: business_blueprint.md 方案承接要求覆盖不足，建议至少覆盖角色/流程/状态/异常/风险中的 3 类
- warning: business_blueprint.md `## 9. 待确认问题` 建议使用“问题标题 + 影响 + 建议确认方”的分块结构
- info: facts 阶段状态：passed

## 3. 检查范围

- projects/self-permission-apply/workspace/facts.md
- projects/self-permission-apply/workspace/business_blueprint.md
- projects/self-permission-apply/runtime/provenance.json
- projects/self-permission-apply/runtime/gates/facts_gate_status.json

## 4. 建议处理

- 当前为 warning，可复核后接受，或补强对应内容后重跑。
