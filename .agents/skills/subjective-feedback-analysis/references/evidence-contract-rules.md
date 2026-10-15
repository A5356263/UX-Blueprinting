read_frequency: on_demand
execution_critical: true

# 主观证据与交接契约

## Findings 与 Evidence

`findings` 是样本内分析发现，可以是有限结论、相关信号或待验证假设。`evidence_items` 是允许进入证据标准化链的主观证据，必须满足追溯、脱敏、样本边界、置信度和用途限制。

只有 `evidence_items` 能进入 `evidence-govern` 的 Phase 1。Findings 可以被 `business-impact` 当作低成熟度 problem signal，或在用户明确要求时被可视化，但不得自动升级为证据。

## 统一标识

- 标准反馈：`item_id`
- 主题：`cluster_id`
- 发现：`finding_id`
- 证据：`evidence_id`
- 客观验证请求：`objective_request_id`
- 知识候选：`knowledge_candidate_id`

统一使用 `source_item_ids`、`representative_quote_refs`、`sample_count`、`sample_share`、`affected_pages`、`affected_flows`、`affected_journey_steps` 和 `reason`。

## 正式证据

`claim_type` 只允许：

```text
user_report
perception_signal
service_signal
sentiment_signal
reported_error
```

假设不得成为正式 evidence claim type。每条 evidence 必须引用一个 `evidence_eligible=true` 的 finding，并包含 statement、cluster ref、source refs、样本信息、置信度、scene descriptor、允许/禁止用途和 lineage。

涉及规则、权限、配置、资格、预期流程或校验要求时，按 `shared-workflow/data-analysis/references/business-rule-basis-rules.md` 附带 `business_rule_basis`。Subjective 只能使用用户确认、正式上游、Knowledge Wiki 命中或材料推断等来源标注规则线索；未确认内容必须 `needs_confirmation` 或 `inferred_only`，不得验证规则真伪。

固定禁止用途至少包含：`prevalence_claim`、`causal_claim`、`final_root_cause`、`objective_impact_scale`、`intervention_effectiveness` 和 `knowledge_publish`。

## 场景描述符

允许字段：`where`、`what`、`operation`、`who`、`when`、`source_attribution` 和 `evidence_form`。

`who` 只能含角色、业务分群和稳定脱敏实体引用。用户或客服引用的报错分别使用 `user_quoted_system_message` 或 `support_quoted_system_message`；不得标成真正的 `system_log`。

缺少 where、what、operation 时降低跨源匹配置信度；完全缺失时标记 `scene_descriptor_missing`，不得补造。

## 客观验证请求

只为重要且确需客观验证的发现生成，可请求漏斗、路径、行为、错误、咨询量、分群或时间比较。请求必须说明相关 finding/evidence、假设、所需信号、范围、时间窗、优先程度和原因。

请求不等于读取授权。用户已明确提供数据并要求分析时，Objective 可在该范围内查看 schema、表头和必要少量样例；新增数据源、额外敏感范围或关键业务歧义仍需确认。

## 下游权限

- Evidence Govern：只读正式 Evidence 及其来源、范围、限制和用途边界。
- Business Impact：可读 evidence；finding 仅作低成熟度 problem signal。
- Data Visualization：显式请求时只展示 analysis results、finding 和 evidence。
- Knowledge Wiki：治理放行或用户明确审阅时只读 knowledge candidates。
- Outcome Validation：具备根因与干预契约时读取 comparison。
- Evidence Archive：满足治理门禁后归档正式包。
