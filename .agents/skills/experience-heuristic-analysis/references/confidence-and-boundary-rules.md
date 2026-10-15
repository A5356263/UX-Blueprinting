# 置信度、规则依据、补证与用途边界

按需用于 Confidence、业务和设计规范、Validation Requests、Comparison 及下游消费。

## Confidence

`confidence` 只表示观察可靠性：

- `high`：问题可直接观察、位置明确，材料与适用规则一致；
- `medium`：可观察但材料不完整，或动态状态尚未验证；
- `low`：判断依赖上下文、推断或未确认规则。

不按材料类型统一封顶。截图可以高置信证明裁切，不能证明真实点击或键盘行为。DOM/A11Y/runtime 可提高结构和状态判断可靠性，但不能提高因果置信度。

## Evidence 硬边界

Evidence claim type 只允许 `heuristic_observation | risk_hypothesis`，并固定：

```text
can_be_used_as_strong_evidence = false
manual_review_required = true
causal_claim_allowed = false
```

本技能不输出 `validated_evidence`，不读取其他分析包升级证据，不维护跨源 evidence refs。

## 业务规则依据

包级 `business_rule_basis[]` 登记，Finding 使用 `business_rule_basis_refs[]` 引用。来源优先级：

```text
user_confirmed
→ formal_upstream
→ knowledge_wiki
→ explicit_project_rule
→ provided_material
→ evidence_inferred
→ unknown
```

只有确认有效的用户规则、正式上游、Wiki raw 或明确项目规则可以支持确定性业务判断。`provided_material` 只在本轮范围内确认；推断或 unknown 只能支持待确认风险。每条依据只使用一个 `source_type`，不增加自由文本来源类型字段。

## 项目设计规范

项目或设计系统规范通过 `project_rule_refs[]` 指向 Source Manifest；通用启发式通过 `heuristic_rule_ref` 指向本地执行规则。

多规范按硬约束、当前项目正式版本、业务域正式规范、公司通用准则、通用启发式依次评估，同时检查适用产品、业务域、端、角色、状态、版本、批准状态和明确替代关系。无法裁决时使用 `design_rule_conflict_confirmation`，不得判定违反规范。

## Validation Requests

支持：

```text
additional_interface_material
manual_interface_review
business_rule_confirmation
objective_behavior_confirmation
subjective_feedback_confirmation
accessibility_specialist_review
device_or_browser_verification
design_rule_conflict_confirmation
privacy_review
```

`gap_type` 说明缺哪类验证；`required_input` 说明具体补什么；`reason` 说明为什么；`blocks_evidence_promotion` 决定是否阻止 Evidence。用户侧展示通俗内容，不要求理解枚举。

## Comparison

只在 `intervention_recheck` 生成，必须有明确 baseline/current refs 与可比范围。只描述 resolved、persisted、new、severity change 和 scope consistency，固定 `effect_claim=not_claimed`，不转成 Evidence。

## 下游用途

| 下游 | 允许 | 禁止 |
| --- | --- | --- |
| Evidence Govern | promoted Evidence、来源、规则、场景和边界 | Findings、Coverage、Comparison、报告正文 |
| Business Impact | promoted Evidence 作为 preliminary 问题信号 | 未 promotion Finding、真实规模、投入或 ROI 推断 |
| Data Visualization | 用户明确要求时表达可披露的 Findings、Coverage、Comparison | 重判问题、证据强度或优先级；展示受限原文 |
| Root Cause | Govern 放行后的启发式证据 | 直接读取原始包绕过治理 |
| Outcome Validation | 只读取 Root Cause 与 Govern 的正式输入 | 直接消费启发式 Comparison 或把风险变化写成方案有效 |
| Evidence Archive | 只消费 Govern 明确放行的归档 Handoff | 直接归档 Heuristic 原始包、截图或 Findings |

所有用途保留 `source_run_id`、`privacy_status`、`manual_review_required`、`allowed_uses[]` 与 `forbidden_uses[]`。

## 隐私与披露

来源和输出分别判定。来源含隐私信息时，不自动复制原文或截图；Finding 和 Evidence 只有在结论已去标识化且不会反推出个人、企业、单据或凭证时才可标为 `safe`。

- `restricted`：可在受控环境中使用脱敏结论，不能公开展示原文；
- `needs_review`：必须进入 `privacy_review`，在复核前不得扩大用途；
- `blocked`：不得 Promotion、展示、归档或提交知识；
- 任何受限状态都必须在 Govern 中原样继承，不能被下游自行放宽。
