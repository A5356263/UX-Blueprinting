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
- open issues: 6
- blocker: 1
- warning: 5
- info: 0

## 问题统计

- issue_count: 6
- open_issue_count: 6
- blocker_count: 1
- warning_count: 5
- info_count: 0

## 本轮修复单元

### repair-unit-001
- target: projects/self-permission-apply/workspace/business_blueprint.md
- goal: 修复 business_blueprint.md 中的 experience_business_consumption_gap, experience_role_path_gap 问题
- mode: patch_current_artifact
- issue_ids: BIZ-54F58B51, BIZ-66583972

### repair-unit-002
- target: projects/self-permission-apply/workspace/experience_blueprint.md
- goal: 修复 experience_blueprint.md 中的 depth_insufficient, experience_guideline_consumption_gap 问题
- mode: patch_current_artifact
- issue_ids: EXP-CC2158D9, EXP-6D585AEF

### repair-unit-003
- target: projects/self-permission-apply/runtime/gate_metrics.json
- goal: 修复 gate_metrics.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-FCB57B57

### repair-unit-004
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

- EXP-CC2158D9 | blocker | experience | experience_guideline_consumption_gap | sources=coverage | experience 阶段发现 experience_guideline_consumption_gap 问题：设计指南消费检查：experience_blueprint.md 声称已消费设计指南，但 context_manifest.json 没有对应记录。
- BIZ-54F58B51 | warning | business | experience_business_consumption_gap | sources=business_gate, validate | business 阶段发现 experience_business_consumption_gap 问题：business_blueprint.md `## 9. 待确认问题` 建议使用“问题标题 + 影响 + 建议确认方”的分块结构
- BIZ-66583972 | warning | business | experience_role_path_gap | sources=business_gate, validate | business 阶段发现 experience_role_path_gap 问题：business_blueprint.md 方案承接要求覆盖不足，建议至少覆盖角色/流程/状态/异常/风险中的 3 类
- EXP-6D585AEF | warning | experience | depth_insufficient | sources=experience_gate, validate | experience 阶段发现 depth_insufficient 问题：experience_blueprint.md `## 8. 待确认问题` 建议使用“问题标题 + 影响 + 建议确认方”的分块结构
- RUN-A3AFE22C | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/self-permission-apply/runtime/trace_index.json
- RUN-FCB57B57 | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/self-permission-apply/runtime/gate_metrics.json

## 已接受 warning

- none

## 已延期问题

- none
