# 来源与问题影响规则

## 1. 输入来源与权威顺序

每项正式数值或判断必须登记 `valuation_input`。按以下顺序选择来源：

1. 显式 Handoff 中已放行且版本兼容的结构化结论；
2. 用户明确引用的单源分析结论；
3. 有来源、范围和有效期的正式业务规则；
4. 用户本轮明确提供的结构化事实；
5. 明示的情景假设。

不得扫描 latest 发现输入。Evidence Govern 存在时使用其问题边界；不存在时 Objective、Subjective、Heuristic 分别建立 preliminary Case。Business Impact 不建立跨源候选链接。

## 2. Valuation Input

每项输入至少记录：

- `input_id`、`semantic_role`；
- `source_type`、`source_skill`、精确到字段/JSON Pointer 的 `source_ref`；
- `source_version`、`provenance_status`；
- `population_scope`、`time_window`、`unit`；
- `allowed_uses`、`sensitivity`。

允许的语义角色：problem evidence、population metric、business rule、solution scope、effect estimate、unit value、cost、assumption。一个输入可支持多个 Case，但金额不得因此复制计入。

## 3. 问题 Case

一个 Case 只描述一个可区分问题。稳定 ID 由项目、任务、场景、问题边界生成；文本改写不改变同一问题的 stable key。

- `preliminary`：用户问题或单一未经治理的分析来源；
- `evidence_backed`：Evidence Govern 明确放行的问题边界。

禁止包级成熟度覆盖不同 Case。

## 4. Affected Population

依次区分：

- `eligible_population`：理论上可能遇到问题的总体；
- `observed_sample`：材料实际覆盖样本；
- `observed_affected`：样本中确认受影响对象；
- `estimated_affected_range`：有总体分母和外推依据时的区间；
- `segments`：业务分群与覆盖差异；
- `projection_status`：`measured | derived | assumption | not_evaluable`。

没有总体分母、同口径 ID、相同时间窗口或代表性依据时禁止外推。企业 ID 只能输出企业比例；自然人用户比例需要用户级分母。主观反馈和启发式证据默认只支持 observed impact/risk。

## 5. 影响组件

影响层级为 `user | product | service | business | organization`。每项记录：

- 描述与适用对象；
- `fact | inference | assumption | not_evaluable`；
- 关系类型与置信边界；
- 来源引用、范围/单位和 `dedup_group`。

不强制每层产出结论。相关不得写成因果；同一损失跨层表达时使用同一 dedup group。

## 6. Cost of Inaction 与 Addressable Opportunity

`cost_of_inaction` 描述维持现状在明确窗口内继续发生的损失、风险或机会成本。

`addressable_opportunity` 描述当前问题中可能被干预触达的价值范围，不假设问题全部消失。两者是不同视角，禁止相加。具体方案收益必须从 addressable opportunity 向下收缩；无法量化机会范围时，方案收益只能定性或使用清晰的情景假设。

## 7. 原始数据边界

原始企业状态、任务、日志、工单和方案曝光明细交给 Objective；上线效果所需原始数据交给 Outcome Validation。Business Impact 只读结构化聚合结果及其血缘。原始材料是唯一输入时精确路由，不在本技能内预处理。
