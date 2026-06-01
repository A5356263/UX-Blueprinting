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
- open issues: 5
- blocker: 4
- warning: 1
- info: 0

## 问题统计

- issue_count: 5
- open_issue_count: 5
- blocker_count: 4
- warning_count: 1
- info_count: 0

## 本轮修复单元

### repair-unit-001
- target: projects/self-permission-apply/workspace/facts.md
- goal: 修复 facts.md 中的 skeleton_content, structure_missing 问题
- mode: patch_current_artifact
- issue_ids: FACT-2446D678, FACT-492DDFBE, FACT-59FD36E7

### repair-unit-002
- target: projects/self-permission-apply/runtime/gate_metrics.json
- goal: 修复 gate_metrics.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-FCB57B57

### repair-unit-003
- target: projects/self-permission-apply/runtime/trace_index.json
- goal: 修复 trace_index.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-A3AFE22C

## 推荐重跑

```bash
python -m packages gate-facts self-permission-apply
python -m packages gate-business self-permission-apply
python -m packages gate-experience self-permission-apply
python -m packages validate self-permission-apply
python -m packages coverage self-permission-apply
```

## 未关闭问题

- FACT-2446D678 | blocker | facts | structure_missing | sources=facts_gate | facts 阶段发现 structure_missing 问题：facts.md 未显式承接 requirement/background 输入来源
- FACT-492DDFBE | blocker | facts | skeleton_content | sources=facts_gate | facts 阶段发现 skeleton_content 问题：facts.md 正文长度明显不足，仍像模板骨架
- FACT-59FD36E7 | blocker | facts | skeleton_content | sources=facts_gate | facts 阶段发现 skeleton_content 问题：facts.md 仍包含模板提示语，请先替换为真实内容
- RUN-FCB57B57 | blocker | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/self-permission-apply/runtime/gate_metrics.json
- RUN-A3AFE22C | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/self-permission-apply/runtime/trace_index.json

## 已接受 warning

- none

## 已延期问题

- none
