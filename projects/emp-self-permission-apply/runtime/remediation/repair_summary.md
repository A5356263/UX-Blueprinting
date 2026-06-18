# Repair Summary｜人读说明版

> 本文件是以下机器状态文件的人读说明版：
>
> - `projects/emp-self-permission-apply/runtime/remediation/issue_index.json`
> - `projects/emp-self-permission-apply/runtime/remediation/remediation_plan.json`
> - `projects/emp-self-permission-apply/runtime/remediation/retry_scope.json`
>
> 它只用于帮助理解修复任务，不作为 repair loop 的机器判断依据。
> 机器判断请以上述 JSON 文件为准。

## 当前状态

- repair_loop_status: blocked
- open issues: 5
- blocker: 3
- warning: 2
- info: 0

## 问题统计

- issue_count: 5
- open_issue_count: 5
- blocker_count: 3
- warning_count: 2
- info_count: 0

## 本轮修复单元

### repair-unit-001
- target: projects/emp-self-permission-apply/workspace/business_blueprint.md
- goal: 修复 business_blueprint.md 中的 depth_insufficient, skeleton_content 问题
- mode: patch_current_artifact
- issue_ids: BIZ-805341F0, BIZ-7B6CBB22

### repair-unit-002
- target: projects/emp-self-permission-apply/runtime/gate_metrics.json
- goal: 修复 gate_metrics.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-36CBADC5

### repair-unit-003
- target: projects/emp-self-permission-apply/runtime/trace_index.json
- goal: 修复 trace_index.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-E0D70618

### repair-unit-004
- target: projects/emp-self-permission-apply/workspace/check_status.json
- goal: 修复 check_status.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-C791EFEB

## 推荐重跑

```bash
python -m packages gate-business emp-self-permission-apply
python -m packages gate-experience emp-self-permission-apply
python -m packages validate emp-self-permission-apply
python -m packages coverage emp-self-permission-apply
```

## 未关闭问题

- BIZ-805341F0 | blocker | business | skeleton_content | sources=business_gate | business 阶段发现 skeleton_content 问题：business_blueprint.md 仍包含模板提示语,请先替换为真实内容
- RUN-36CBADC5 | blocker | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/emp-self-permission-apply/runtime/gate_metrics.json
- RUN-C791EFEB | blocker | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/emp-self-permission-apply/workspace/check_status.json
- BIZ-7B6CBB22 | warning | business | depth_insufficient | sources=business_gate | business 阶段发现 depth_insufficient 问题：business_blueprint.md 附录没有自然说明主要依据来自 facts 的哪些章节,判断依据承接仍偏弱
- RUN-E0D70618 | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/emp-self-permission-apply/runtime/trace_index.json

## 已接受 warning

- none

## 已延期问题

- none
