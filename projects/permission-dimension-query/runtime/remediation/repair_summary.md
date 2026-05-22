# Repair Summary｜人读说明版

> 本文件是以下机器状态文件的人读说明版：
>
> - `projects/permission-dimension-query/runtime/remediation/issue_index.json`
> - `projects/permission-dimension-query/runtime/remediation/remediation_plan.json`
> - `projects/permission-dimension-query/runtime/remediation/retry_scope.json`
>
> 它只用于帮助理解修复任务，不作为 repair loop 的机器判断依据。
> 机器判断请以上述 JSON 文件为准。

## 当前状态

- repair_loop_status: blocked
- open issues: 3
- blocker: 1
- warning: 2
- info: 0

## 问题统计

- issue_count: 3
- open_issue_count: 3
- blocker_count: 1
- warning_count: 2
- info_count: 0

## 本轮修复单元

### repair-unit-001
- target: projects/permission-dimension-query/runtime/context_manifest.json
- goal: 修复 context_manifest.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-598468B2

### repair-unit-002
- target: projects/permission-dimension-query/runtime/gate_metrics.json
- goal: 修复 gate_metrics.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-07F6D6AB

### repair-unit-003
- target: projects/permission-dimension-query/runtime/trace_index.json
- goal: 修复 trace_index.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-F655398D

## 推荐重跑

```bash
python -m packages validate permission-dimension-query
python -m packages coverage permission-dimension-query
```

## 未关闭问题

- RUN-07F6D6AB | blocker | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/permission-dimension-query/runtime/gate_metrics.json
- RUN-598468B2 | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/permission-dimension-query/runtime/context_manifest.json
- RUN-F655398D | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/permission-dimension-query/runtime/trace_index.json

## 已接受 warning

- none

## 已延期问题

- none
