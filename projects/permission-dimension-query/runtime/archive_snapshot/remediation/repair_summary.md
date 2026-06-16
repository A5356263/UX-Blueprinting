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
- target: projects/permission-dimension-query/workspace/business_blueprint.md
- goal: 修复 business_blueprint.md 中的 depth_insufficient, experience_business_consumption_gap 问题
- mode: patch_current_artifact
- issue_ids: BIZ-5B16494A, BIZ-6FA63013, BIZ-A2868A58

### repair-unit-002
- target: projects/permission-dimension-query/workspace/business_blueprint.md
- goal: 修复 business_blueprint.md 中的 experience_business_consumption_gap, experience_state_feedback_gap 问题
- mode: patch_current_artifact
- issue_ids: EXP-0B19AFD4, EXP-463D4523, EXP-AC8D0013

### repair-unit-003
- target: projects/permission-dimension-query/workspace/experience_blueprint.md
- goal: 修复 experience_blueprint.md 中的 experience_exception_handling_gap 问题
- mode: patch_current_artifact
- issue_ids: EXP-298A6AAE

### repair-unit-004
- target: projects/permission-dimension-query/runtime/gate_metrics.json
- goal: 修复 gate_metrics.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-07F6D6AB

### repair-unit-005
- target: projects/permission-dimension-query/runtime/trace_index.json
- goal: 修复 trace_index.json 中的 structure_missing 问题
- mode: rerun_checks_only
- issue_ids: RUN-F655398D

## 推荐重跑

```bash
python -m packages gate-business permission-dimension-query
python -m packages gate-experience permission-dimension-query
python -m packages validate permission-dimension-query
python -m packages coverage permission-dimension-query
```

## 未关闭问题

- BIZ-5B16494A | warning | business | depth_insufficient | sources=business_gate, validate | business 阶段发现 depth_insufficient 问题：business_blueprint.md 附录没有自然说明主要依据来自 facts 的哪些章节，判断依据承接仍偏弱
- BIZ-6FA63013 | warning | business | experience_business_consumption_gap | sources=business_gate, validate | business 阶段发现 experience_business_consumption_gap 问题：business_blueprint.md 规则与边界描述偏少
- BIZ-A2868A58 | warning | business | experience_business_consumption_gap | sources=business_gate, validate | business 阶段发现 experience_business_consumption_gap 问题：business_blueprint.md 风险与保护策略内容偏少
- EXP-0B19AFD4 | warning | experience | experience_state_feedback_gap | sources=coverage | experience 阶段发现 experience_state_feedback_gap 问题：承接检查：business_blueprint.md 要求解释“如果是通过角色获得的，标注来源角色名称”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。
- EXP-298A6AAE | warning | experience | experience_exception_handling_gap | sources=experience_gate, validate | experience 阶段发现 experience_exception_handling_gap 问题：experience_blueprint.md 主流程、异常或页面设计核心区包含表格，建议优先使用节点化 Markdown 层级表达
- EXP-463D4523 | warning | experience | experience_business_consumption_gap | sources=coverage | experience 阶段发现 experience_business_consumption_gap 问题：承接检查：business_blueprint.md 已把“查询范围的二次校验：即使入口可见，查询特定对象时...”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- EXP-AC8D0013 | warning | experience | experience_state_feedback_gap | sources=coverage | experience 阶段发现 experience_state_feedback_gap 问题：承接检查：business_blueprint.md 已把“数据加载失败：系统异常时提供重试入口”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- RUN-07F6D6AB | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/permission-dimension-query/runtime/gate_metrics.json
- RUN-F655398D | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/permission-dimension-query/runtime/trace_index.json

## 已接受 warning

- none

## 已延期问题

- none
