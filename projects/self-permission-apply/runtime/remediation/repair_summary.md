# Repair Summary｜人读说明版

> 本文件是以下机器状态文件的人读说明版：
>
> - `projects/self-permission-apply/runtime/remediation/issue_index.json`
> - `projects/self-permission-apply/runtime/remediation/remediation_plan.json`
> - `projects/self-permission-apply/runtime/remediation/retry_scope.json`
>
> 它只用于帮助理解修复任务，不作为 repair loop 的机器判断依据。
> 机器判断请以上述 JSON 文件为准。

## 当前状态

- repair_loop_status: blocked
- open issues: 7
- blocker: 3
- warning: 4
- info: 0

## 问题统计

- issue_count: 7
- open_issue_count: 7
- blocker_count: 3
- warning_count: 4
- info_count: 0

## 本轮修复单元

### repair-unit-001
- target: projects/self-permission-apply/workspace/business_blueprint.md
- goal: 修复 business_blueprint.md 中的 depth_insufficient 问题
- mode: patch_current_artifact
- issue_ids: BIZ-DF47DF30

### repair-unit-002
- target: projects/self-permission-apply/workspace/experience_blueprint.md
- goal: 修复 experience_blueprint.md 中的 experience_exception_handling_gap 问题
- mode: patch_current_artifact
- issue_ids: EXP-F366C9E2

### repair-unit-003
- target: projects/self-permission-apply/workspace/check_report.md
- goal: 修复 check_report.md 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: CHK-ECDAC940

### repair-unit-004
- target: projects/self-permission-apply/workspace/check_status.json
- goal: 修复 check_status.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: CHK-B59BC6FA

### repair-unit-005
- target: projects/self-permission-apply/workspace/gap_list.md
- goal: 修复 gap_list.md 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: CHK-0A8D2325

### repair-unit-006
- target: projects/self-permission-apply/runtime/gate_metrics.json
- goal: 修复 gate_metrics.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-FCB57B57

### repair-unit-007
- target: projects/self-permission-apply/runtime/trace_index.json
- goal: 修复 trace_index.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-A3AFE22C

## 推荐重跑

```bash
python -m packages gate-business self-permission-apply
python -m packages gate-experience self-permission-apply
python -m packages validate self-permission-apply
python -m packages coverage self-permission-apply
```

## 未关闭问题

- CHK-0A8D2325 | blocker | final | structure_missing | sources=validate | final 阶段发现 structure_missing 问题：必需输出缺失：projects/self-permission-apply/workspace/gap_list.md
- CHK-B59BC6FA | blocker | final | structure_missing | sources=validate | final 阶段发现 structure_missing 问题：必需输出缺失：projects/self-permission-apply/workspace/check_status.json
- CHK-ECDAC940 | blocker | final | structure_missing | sources=validate | final 阶段发现 structure_missing 问题：必需输出缺失：projects/self-permission-apply/workspace/check_report.md
- BIZ-DF47DF30 | warning | business | depth_insufficient | sources=business_gate, validate | business 阶段发现 depth_insufficient 问题：business_blueprint.md 附录没有自然说明主要依据来自 facts 的哪些章节，判断依据承接仍偏弱
- EXP-F366C9E2 | warning | experience | experience_exception_handling_gap | sources=experience_gate, validate | experience 阶段发现 experience_exception_handling_gap 问题：experience_blueprint.md 主流程、异常或页面设计核心区包含表格，建议优先使用节点化 Markdown 层级表达
- RUN-A3AFE22C | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/self-permission-apply/runtime/trace_index.json
- RUN-FCB57B57 | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/self-permission-apply/runtime/gate_metrics.json

## 已接受 warning

- none

## 已延期问题

- none
