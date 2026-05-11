# Repair Summary｜人读说明版

> 本文件是以下机器状态文件的人读说明版：
>
> - `projects/employee-permission-apply/runtime/remediation/issue_index.json`
> - `projects/employee-permission-apply/runtime/remediation/remediation_plan.json`
> - `projects/employee-permission-apply/runtime/remediation/retry_scope.json`
>
> 它只用于帮助理解修复任务，不作为 repair loop 的机器判断依据。
> 机器判断请以上述 JSON 文件为准。

## 当前状态

- repair_loop_status: planned
- open issues: 6
- blocker: 0
- warning: 6
- info: 0

## 问题统计

- issue_count: 7
- open_issue_count: 6
- blocker_count: 0
- warning_count: 6
- info_count: 0

## 本轮修复单元

### repair-unit-001
- target: projects/employee-permission-apply/workspace/business_blueprint.md
- goal: 修复 business_blueprint.md 中的 experience_business_consumption_gap 问题
- mode: patch_current_artifact
- issue_ids: BIZ-3DC7E33A

### repair-unit-002
- target: projects/employee-permission-apply/workspace/business_blueprint.md
- goal: 修复 business_blueprint.md 中的 experience_state_feedback_gap 问题
- mode: patch_current_artifact
- issue_ids: EXP-7274D601, EXP-E59C49D9

### repair-unit-003
- target: projects/employee-permission-apply/workspace/check_status.json
- goal: 修复 check_status.json 中的 experience_guideline_consumption_gap 问题
- mode: rerun_checks_only
- issue_ids: CHK-1B10D647

### repair-unit-004
- target: projects/employee-permission-apply/runtime/gate_metrics.json
- goal: 修复 gate_metrics.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-1C9A809E

### repair-unit-005
- target: projects/employee-permission-apply/runtime/trace_index.json
- goal: 修复 trace_index.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-2A30C5A7

## 推荐重跑

```bash
python -m packages gate-business employee-permission-apply
python -m packages gate-experience employee-permission-apply
python -m packages validate employee-permission-apply
python -m packages coverage employee-permission-apply
```

## 未关闭问题

- BIZ-3DC7E33A | warning | business | experience_business_consumption_gap | sources=business_gate, validate | business 阶段发现 experience_business_consumption_gap 问题：business_blueprint.md 风险与保护策略内容偏少
- EXP-7274D601 | warning | experience | experience_state_feedback_gap | sources=coverage | experience 阶段发现 experience_state_feedback_gap 问题：承接检查：business_blueprint.md 已把“关闭模式时在途流程阻断”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- EXP-E59C49D9 | warning | experience | experience_state_feedback_gap | sources=coverage | experience 阶段发现 experience_state_feedback_gap 问题：承接检查：business_blueprint.md 要求解释“权限生效结果”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。
- CHK-1B10D647 | warning | final | experience_guideline_consumption_gap | sources=coverage | final 阶段发现 experience_guideline_consumption_gap 问题：设计指南消费检查：knowledge_usage_report.json 未记录 experience 阶段实际消费的 design guideline。
- RUN-1C9A809E | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/employee-permission-apply/runtime/gate_metrics.json
- RUN-2A30C5A7 | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/employee-permission-apply/runtime/trace_index.json

## 已接受 warning

- none

## 已延期问题

- none
