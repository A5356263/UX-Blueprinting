# Stage Gate Report

## 1. 检查结果

- status: warning
- 是否阻断: 否
- has_blocker: false
- blocker_count: 0
- warning_count: 1
- info_count: 1

- project_id: emp-self-permission-apply
- stage: experience
- next_stage: final-validate
- can_proceed: true

## 2. 问题列表

- warning: experience_blueprint.md 主流程、异常或页面设计核心区包含表格，建议优先使用节点化 Markdown 层级表达
- info: business 阶段状态：warning

## 3. 检查范围

- projects/emp-self-permission-apply/workspace/facts.md
- projects/emp-self-permission-apply/workspace/business_blueprint.md
- projects/emp-self-permission-apply/workspace/experience_blueprint.md
- projects/emp-self-permission-apply/runtime/provenance.json
- projects/emp-self-permission-apply/runtime/gates/business_gate_status.json

## 4. 建议处理

- 当前为 warning，可复核后接受，或补强对应内容后重跑。
