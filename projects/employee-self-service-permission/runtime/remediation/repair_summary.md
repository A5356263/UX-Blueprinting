# Repair Summary｜人读说明版

> 本文件是以下机器状态文件的人读说明版：
>
> - `projects/employee-self-service-permission/runtime/remediation/issue_index.json`
> - `projects/employee-self-service-permission/runtime/remediation/remediation_plan.json`
> - `projects/employee-self-service-permission/runtime/remediation/retry_scope.json`
>
> 它只用于帮助理解修复任务，不作为 repair loop 的机器判断依据。
> 机器判断请以上述 JSON 文件为准。

## 当前状态

- repair_loop_status: planned
- open issues: 7
- blocker: 0
- warning: 7
- info: 0

## 问题统计

- issue_count: 8
- open_issue_count: 7
- blocker_count: 0
- warning_count: 7
- info_count: 0

## 本轮修复单元

### repair-unit-001
- target: projects/employee-self-service-permission/workspace/business_blueprint.md
- goal: 修复 business_blueprint.md 中的 depth_insufficient 问题
- mode: patch_current_artifact
- issue_ids: BIZ-99D07BF7

### repair-unit-002
- target: projects/employee-self-service-permission/workspace/business_blueprint.md
- goal: 修复 business_blueprint.md 中的 experience_state_feedback_gap 问题
- mode: patch_current_artifact
- issue_ids: EXP-20D55EFC, EXP-A28252F3

### repair-unit-003
- target: projects/employee-self-service-permission/workspace/experience_blueprint.md
- goal: 修复 experience_blueprint.md 中的 depth_insufficient 问题
- mode: patch_current_artifact
- issue_ids: EXP-1C138F12, EXP-D94B491B

### repair-unit-004
- target: projects/employee-self-service-permission/runtime/gate_metrics.json
- goal: 修复 gate_metrics.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-6A7C6FDE

### repair-unit-005
- target: projects/employee-self-service-permission/runtime/trace_index.json
- goal: 修复 trace_index.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-69881261

## 推荐重跑

```bash
python -m packages gate-business employee-self-service-permission
python -m packages gate-experience employee-self-service-permission
python -m packages validate employee-self-service-permission
python -m packages coverage employee-self-service-permission
```

## 未关闭问题

- BIZ-99D07BF7 | warning | business | depth_insufficient | sources=business_gate | business 阶段发现 depth_insufficient 问题：business_blueprint.md 附录没有自然说明主要依据来自 facts 的哪些章节，判断依据承接仍偏弱
- EXP-1C138F12 | warning | experience | depth_insufficient | sources=experience_gate | experience 阶段发现 depth_insufficient 问题：experience_blueprint.md 附录：依据与追踪内容偏少
- EXP-20D55EFC | warning | experience | experience_state_feedback_gap | sources=coverage | experience 阶段发现 experience_state_feedback_gap 问题：承接检查：business_blueprint.md 明确要求主流程闭环包含“管理员关闭自助申请模式”，但 experience_blueprint.md 还没有把这一段转成清晰的用户流程、系统反馈或结果去向。
- EXP-A28252F3 | warning | experience | experience_state_feedback_gap | sources=coverage | experience 阶段发现 experience_state_feedback_gap 问题：承接检查：business_blueprint.md 明确要求主流程闭环包含“管理员配置和开启自助申请模式”，但 experience_blueprint.md 还没有把这一段转成清晰的用户流程、系统反馈或结果去向。
- EXP-D94B491B | warning | experience | depth_insufficient | sources=experience_gate | experience 阶段发现 depth_insufficient 问题：experience_blueprint.md 待确认问题为空，建议显式标注不确定项
- RUN-69881261 | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/employee-self-service-permission/runtime/trace_index.json
- RUN-6A7C6FDE | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/employee-self-service-permission/runtime/gate_metrics.json

## 已接受 warning

- none

## 已延期问题

- none
