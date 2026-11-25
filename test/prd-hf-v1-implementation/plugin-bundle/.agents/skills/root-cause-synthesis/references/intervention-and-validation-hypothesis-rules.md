# 治理方向与验证假设规则

## 治理方向

`intervention_direction_candidate` 只描述需要改善或验证的能力方向，不是具体方案。

每个方向必须关联候选根因，记录目标范围、准备度、前置条件、约束、禁止输出、审核状态和建议下游。

准备度：

- `validation_only`：根因较弱或竞争解释未排除；
- `exploration_ready`：可探索治理路径；
- `design_ready_after_review`：审核后可进入方案设计；
- `blocked`：不得进入下游。

低或不足置信候选只能输出 `validation_only` 或 `blocked`。

禁止包含具体组件、布局、按钮、文案、客服话术、频控、灰度、发布范围或上线方案。系统、权限、合规、数据口径和正常业务规则问题应优先进入相应核查，不默认转成体验方案。

## 验证假设

`validation_hypotheses[]` 统一承载过去分散在指标假设、Hypothesis Ledger 和 Validation Plan 中的最小内容：

- 候选根因与治理方向引用；
- 预期机制；
- 目标指标和方向；
- guardrail；
- 必要分群；
- baseline 与观察要求；
- 可证伪条件；
- 登记时机和审核状态。

Root Cause 只定义“验证什么”，不得设计实验执行方式、样本量、上线节奏、统计方法或正式业务成功阈值。

没有具体方案时，假设只能关联治理方向并保持 `draft`。Outcome 只有在假设与正式 Intervention Contract 对齐后才能执行。

禁止输出预期提升百分比、收益、成本、ROI、回收周期或业务优先级。事后补登记必须标记 `registration_timing=retrospective`。
