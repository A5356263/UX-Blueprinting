# Repair Summary｜人读说明版

> 本文件是以下机器状态文件的人读说明版：
>
> - `projects/sub-admin-copy/runtime/remediation/issue_index.json`
> - `projects/sub-admin-copy/runtime/remediation/remediation_plan.json`
> - `projects/sub-admin-copy/runtime/remediation/retry_scope.json`
>
> 它只用于帮助理解修复任务，不作为 repair loop 的机器判断依据。
> 机器判断请以上述 JSON 文件为准。

## 当前状态

- repair_loop_status: planned
- open issues: 9
- blocker: 0
- warning: 9
- info: 0

## 问题统计

- issue_count: 10
- open_issue_count: 9
- blocker_count: 0
- warning_count: 9
- info_count: 0

## 本轮修复单元

### repair-unit-001
- target: projects/sub-admin-copy/workspace/business_blueprint.md
- goal: 修复 business_blueprint.md 中的 experience_business_consumption_gap 问题
- mode: patch_current_artifact
- issue_ids: BIZ-E567BD54

### repair-unit-002
- target: projects/sub-admin-copy/workspace/business_blueprint.md
- goal: 修复 business_blueprint.md 中的 experience_business_consumption_gap, experience_state_feedback_gap 问题
- mode: patch_current_artifact
- issue_ids: EXP-95711CFC, EXP-D69BF8F0, EXP-F624169D

### repair-unit-003
- target: projects/sub-admin-copy/workspace/experience_blueprint.md
- goal: 修复 experience_blueprint.md 中的 depth_insufficient 问题
- mode: patch_current_artifact
- issue_ids: EXP-E5A4CBA2

### repair-unit-004
- target: projects/sub-admin-copy/workspace/check_status.json
- goal: 修复 check_status.json 中的 experience_guideline_consumption_gap 问题
- mode: rerun_checks_only
- issue_ids: CHK-ADCB4102

### repair-unit-005
- target: projects/sub-admin-copy/workspace/gap_list.md
- goal: 修复 gap_list.md 中的 placeholder_residue 问题
- mode: patch_current_section
- issue_ids: CHK-F368C50F

### repair-unit-006
- target: projects/sub-admin-copy/runtime/gate_metrics.json
- goal: 修复 gate_metrics.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-5CF0E79F

### repair-unit-007
- target: projects/sub-admin-copy/runtime/trace_index.json
- goal: 修复 trace_index.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-9B36895F

## 推荐重跑

```bash
python -m packages gate-business sub-admin-copy
python -m packages gate-experience sub-admin-copy
python -m packages validate sub-admin-copy
python -m packages coverage sub-admin-copy
```

## 未关闭问题

- BIZ-E567BD54 | warning | business | experience_business_consumption_gap | sources=business_gate, validate | business 阶段发现 experience_business_consumption_gap 问题：business_blueprint.md 价值/成本/认知负担评估检测不到结构化内容，请确认已在自然语言中覆盖
- EXP-95711CFC | warning | experience | experience_business_consumption_gap | sources=coverage | experience 阶段发现 experience_business_consumption_gap 问题：承接检查：business_blueprint.md 已把“批量误操作 → experience 需在确认前...”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- EXP-D69BF8F0 | warning | experience | experience_state_feedback_gap | sources=coverage | experience 阶段发现 experience_state_feedback_gap 问题：承接检查：business_blueprint.md 已把“部分成功反馈不清晰 → experience 需...”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- EXP-E5A4CBA2 | warning | experience | depth_insufficient | sources=experience_gate, validate | experience 阶段发现 depth_insufficient 问题：experience_blueprint.md 附录：依据与追踪内容偏少
- EXP-F624169D | warning | experience | experience_business_consumption_gap | sources=coverage | experience 阶段发现 experience_business_consumption_gap 问题：承接检查：business_blueprint.md 已把“无互审模式下缺乏二次确认 → experienc...”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- CHK-ADCB4102 | warning | final | experience_guideline_consumption_gap | sources=coverage | final 阶段发现 experience_guideline_consumption_gap 问题：设计指南消费检查：knowledge_usage_report.json 未记录 experience 阶段实际消费的 design guideline。
- CHK-F368C50F | warning | final | placeholder_residue | sources=validate | final 阶段发现 placeholder_residue 问题：gap_list.md 仍包含占位内容
- RUN-5CF0E79F | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/sub-admin-copy/runtime/gate_metrics.json
- RUN-9B36895F | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/sub-admin-copy/runtime/trace_index.json

## 已接受 warning

- none

## 已延期问题

- none
