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

- repair_loop_status: planned
- open issues: 10
- blocker: 0
- warning: 10
- info: 0

## 问题统计

- issue_count: 15
- open_issue_count: 10
- blocker_count: 0
- warning_count: 10
- info_count: 0

## 本轮修复单元

### repair-unit-001
- target: projects/self-permission-apply/workspace/business_blueprint.md
- goal: 修复 business_blueprint.md 中的 experience_state_feedback_gap 问题
- mode: patch_current_artifact
- issue_ids: BIZ-2C46F0CE

### repair-unit-002
- target: projects/self-permission-apply/workspace/business_blueprint.md
- goal: 修复 business_blueprint.md 中的 experience_business_consumption_gap, experience_exception_handling_gap, experience_state_feedback_gap 问题
- mode: patch_current_artifact
- issue_ids: EXP-0C049F45, EXP-449E593B, EXP-7575EA4B, EXP-85AE2E30, EXP-987590DE, EXP-B227C03E, EXP-C10CA364, EXP-ED1E1039

### repair-unit-003
- target: projects/self-permission-apply/workspace/experience_blueprint.md
- goal: 修复 experience_blueprint.md 中的 experience_exception_handling_gap 问题
- mode: patch_current_artifact
- issue_ids: EXP-F366C9E2

## 推荐重跑

```bash
python -m packages gate-business self-permission-apply
python -m packages gate-experience self-permission-apply
python -m packages validate self-permission-apply
python -m packages coverage self-permission-apply
```

## 未关闭问题

- BIZ-2C46F0CE | warning | business | experience_state_feedback_gap | sources=business_gate, validate | business 阶段发现 experience_state_feedback_gap 问题：business_blueprint.md 正文疑似直接复制知识库字段名、枚举值、英文状态或模型名，请转译为业务方能理解的话；如确需保留原始术语，请移动到附录“事实、知识与判断追踪”。
- EXP-0C049F45 | warning | experience | experience_exception_handling_gap | sources=coverage | experience 阶段发现 experience_exception_handling_gap 问题：承接检查：business_blueprint.md 已把“审批链路断裂 → 通过兜底机制和异常提醒保护”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- EXP-449E593B | warning | experience | experience_business_consumption_gap | sources=coverage | experience 阶段发现 experience_business_consumption_gap 问题：承接检查：business_blueprint.md 已把“可申请范围过宽 → 通过配置页的默认行为和提示保...”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- EXP-7575EA4B | warning | experience | experience_state_feedback_gap | sources=coverage | experience 阶段发现 experience_state_feedback_gap 问题：承接检查：business_blueprint.md 已把“能力关闭时员工正在填写申请 → 提示能力已关闭”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- EXP-85AE2E30 | warning | experience | experience_state_feedback_gap | sources=coverage | experience 阶段发现 experience_state_feedback_gap 问题：承接检查：business_blueprint.md 已把“管理员在审批期间直接给员工分配了同一角色 → 需...”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- EXP-987590DE | warning | experience | experience_state_feedback_gap | sources=coverage | experience 阶段发现 experience_state_feedback_gap 问题：承接检查：business_blueprint.md 要求解释“能力开启/关闭状态及对应员工端表现”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。
- EXP-B227C03E | warning | experience | experience_state_feedback_gap | sources=coverage | experience 阶段发现 experience_state_feedback_gap 问题：承接检查：business_blueprint.md 要求解释“权限来源（管理员分配 vs 自助申请）及区分方式”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。
- EXP-C10CA364 | warning | experience | experience_business_consumption_gap | sources=coverage | experience 阶段发现 experience_business_consumption_gap 问题：承接检查：business_blueprint.md 已把“概念增殖 → 通过界面语言和操作路径保护”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- EXP-ED1E1039 | warning | experience | experience_state_feedback_gap | sources=coverage | experience 阶段发现 experience_state_feedback_gap 问题：承接检查：business_blueprint.md 已把“可申请角色被管理员在审批中移除 → 在途申请不受...”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- EXP-F366C9E2 | warning | experience | experience_exception_handling_gap | sources=experience_gate, validate | experience 阶段发现 experience_exception_handling_gap 问题：experience_blueprint.md 主流程、异常或页面设计核心区包含表格，建议优先使用节点化 Markdown 层级表达

## 已接受 warning

- none

## 已延期问题

- RUN-A3AFE22C | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/self-permission-apply/runtime/trace_index.json
- RUN-FCB57B57 | warning | runtime | structure_missing | sources=runtime | 缺少正式产物文件：projects/self-permission-apply/runtime/gate_metrics.json
