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

- repair_loop_status: blocked
- open issues: 6
- blocker: 4
- warning: 2
- info: 0

## 问题统计

- issue_count: 6
- open_issue_count: 6
- blocker_count: 4
- warning_count: 2
- info_count: 0

## 本轮修复单元

### repair-unit-001
- target: projects/sub-admin-copy/runtime/context_manifest.json
- goal: 修复 context_manifest.json 中的 copy_contract_gap 问题
- mode: patch_current_artifact
- issue_ids: FACT-2B7CC743

### repair-unit-002
- target: projects/sub-admin-copy/runtime/gate_metrics.json
- goal: 修复 gate_metrics.json 中的 structure_missing 问题
- mode: patch_current_artifact
- issue_ids: FACT-1E9339D1

### repair-unit-003
- target: projects/sub-admin-copy/runtime/context_manifest.json
- goal: 修复 context_manifest.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-FF0894F4

### repair-unit-004
- target: projects/sub-admin-copy/runtime/gate_metrics.json
- goal: 修复 gate_metrics.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-5CF0E79F

### repair-unit-005
- target: projects/sub-admin-copy/runtime/trace_index.json
- goal: 修复 trace_index.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-9B36895F

### repair-unit-006
- target: projects/sub-admin-copy/workspace/check_status.json
- goal: 修复 check_status.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-9D7FEAC5

## 推荐重跑

```bash
python -m packages gate-facts sub-admin-copy
python -m packages gate-business sub-admin-copy
python -m packages gate-experience sub-admin-copy
python -m packages validate sub-admin-copy
python -m packages coverage sub-admin-copy
```

## 未关闭问题

- FACT-1E9339D1 | blocker | facts | structure_missing | sources=facts_gate | facts 阶段发现 structure_missing 问题：provenance: 缺少 runtime/provenance.json
- FACT-2B7CC743 | blocker | facts | copy_contract_gap | sources=facts_gate | facts 阶段发现 copy_contract_gap 问题：缺少文件:projects/sub-admin-copy/runtime/context_manifest.json
- RUN-5CF0E79F | blocker | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/sub-admin-copy/runtime/gate_metrics.json
- RUN-9D7FEAC5 | blocker | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/sub-admin-copy/workspace/check_status.json
- RUN-9B36895F | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/sub-admin-copy/runtime/trace_index.json
- RUN-FF0894F4 | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/sub-admin-copy/runtime/context_manifest.json

## 已接受 warning

- none

## 已延期问题

- none
