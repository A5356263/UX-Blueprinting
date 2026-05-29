# Repair Summary｜人读说明版

> 本文件是以下机器状态文件的人读说明版：
>
> - `projects/self-service-permission/runtime/remediation/issue_index.json`
> - `projects/self-service-permission/runtime/remediation/remediation_plan.json`
> - `projects/self-service-permission/runtime/remediation/retry_scope.json`
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

- issue_count: 9
- open_issue_count: 9
- blocker_count: 0
- warning_count: 9
- info_count: 0

## 本轮修复单元

### repair-unit-001
- target: projects/self-service-permission/workspace/business_blueprint.md
- goal: 修复 business_blueprint.md 中的 experience_state_feedback_gap 问题
- mode: patch_current_artifact
- issue_ids: BIZ-E82D3888

### repair-unit-002
- target: projects/self-service-permission/workspace/business_blueprint.md
- goal: 修复 business_blueprint.md 中的 experience_business_consumption_gap, experience_role_path_gap, experience_state_feedback_gap 问题
- mode: patch_current_artifact
- issue_ids: EXP-2A2704F7, EXP-2F8FC9A8, EXP-6A0EB9DE, EXP-940C7303, EXP-A64ACA4C

### repair-unit-003
- target: projects/self-service-permission/workspace/experience_blueprint.md
- goal: 修复 experience_blueprint.md 中的 structure_missing 问题
- mode: patch_current_artifact
- issue_ids: EXP-966EE99F

### repair-unit-004
- target: projects/self-service-permission/runtime/gate_metrics.json
- goal: 修复 gate_metrics.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-A9035CC0

### repair-unit-005
- target: projects/self-service-permission/runtime/trace_index.json
- goal: 修复 trace_index.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-75BBD743

## 推荐重跑

```bash
python -m packages gate-business self-service-permission
python -m packages gate-experience self-service-permission
python -m packages validate self-service-permission
python -m packages coverage self-service-permission
```

## 未关闭问题

- BIZ-E82D3888 | warning | business | experience_state_feedback_gap | sources=business_gate, validate | business 阶段发现 experience_state_feedback_gap 问题：business_blueprint.md 正文疑似直接复制知识库字段名、枚举值、英文状态或模型名，请转译为业务方能理解的话；如确需保留原始术语，请移动到附录“事实、知识与判断追踪”。
- EXP-2A2704F7 | warning | experience | experience_role_path_gap | sources=coverage | experience 阶段发现 experience_role_path_gap 问题：承接检查：business_blueprint.md 已点名角色要求“管理者端：自助申请配置页”，但 experience_blueprint.md 还没有给出对应的清晰路径、页面或职责承接。
- EXP-2F8FC9A8 | warning | experience | experience_role_path_gap | sources=coverage | experience 阶段发现 experience_role_path_gap 问题：承接检查：business_blueprint.md 已点名角色要求“审批端：审批处理页（复用审批中台）”，但 experience_blueprint.md 还没有给出对应的清晰路径、页面或职责承接。
- EXP-6A0EB9DE | warning | experience | experience_business_consumption_gap | sources=coverage | experience 阶段发现 experience_business_consumption_gap 问题：承接检查：business_blueprint.md 已把“超管角色不进入白名单”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- EXP-940C7303 | warning | experience | experience_state_feedback_gap | sources=coverage | experience 阶段发现 experience_state_feedback_gap 问题：承接检查：business_blueprint.md 已把“白名单为空时的空状态和提示”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- EXP-966EE99F | warning | experience | structure_missing | sources=experience_gate, validate | experience 阶段发现 structure_missing 问题：experience_blueprint.md 主交互流程缺少可对应的节点详情标题
- EXP-A64ACA4C | warning | experience | experience_business_consumption_gap | sources=coverage | experience 阶段发现 experience_business_consumption_gap 问题：承接检查：business_blueprint.md 已把“服务人员不开放”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- RUN-75BBD743 | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/self-service-permission/runtime/trace_index.json
- RUN-A9035CC0 | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/self-service-permission/runtime/gate_metrics.json

## 已接受 warning

- none

## 已延期问题

- none
