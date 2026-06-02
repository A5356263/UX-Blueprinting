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
- blocker: 1
- warning: 4
- info: 0

## 问题统计

- issue_count: 5
- open_issue_count: 5
- blocker_count: 1
- warning_count: 4
- info_count: 0

## 本轮修复单元

### repair-unit-001
- target: projects/self-permission-apply/workspace/experience_blueprint.md
- goal: 修复 experience_blueprint.md 中的 experience_exception_handling_gap, skeleton_content, structure_missing 问题
- mode: patch_current_artifact
- issue_ids: EXP-8A59FF45, EXP-E18EEB74, EXP-F366C9E2

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
python -m packages gate-experience self-permission-apply
python -m packages validate self-permission-apply
python -m packages coverage self-permission-apply
```

## 未关闭问题

- EXP-8A59FF45 | blocker | experience | skeleton_content | sources=experience_gate | experience 阶段发现 skeleton_content 问题：experience_blueprint.md 仍包含模板提示语，请先替换为真实内容
- EXP-E18EEB74 | warning | experience | structure_missing | sources=experience_gate | experience 阶段发现 structure_missing 问题：experience_blueprint.md 主交互流程缺少可对应的节点详情标题
- EXP-F366C9E2 | warning | experience | experience_exception_handling_gap | sources=experience_gate | experience 阶段发现 experience_exception_handling_gap 问题：experience_blueprint.md 主流程、异常或页面设计核心区包含表格，建议优先使用节点化 Markdown 层级表达
- RUN-A3AFE22C | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/self-permission-apply/runtime/trace_index.json
- RUN-FCB57B57 | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/self-permission-apply/runtime/gate_metrics.json

## 已接受 warning

- none

## 已延期问题

- none
