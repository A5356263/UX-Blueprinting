read_frequency: on_demand
execution_critical: true

# 知识候选规则

## 触发条件

只有出现稳定重复问题、多个相近问法、稳定答复、冲突答案、过期风险、临时 workaround 或值得复用的用户困惑时生成候选。普通主题分析不机械生成知识候选。

## 统一候选

使用一个 `knowledge_candidates[]`，通过 `candidate_type` 区分：

- `qa_candidate`
- `answer_pattern`
- `guidance_seed`

候选至少包含：`knowledge_candidate_id`、`candidate_type`、`source_item_ids`、`canonical_question`、`answer_summary`、`applicable_context`、`required_conditions`、`official_rule_confidence`、`conflict_risk`、`staleness_risk`、`privacy_risk`、`workaround_flag`、`recommended_action` 和 `manual_review_required=true`。

“运营复核完成”只表示经过人工整理，不证明答案正确、仍然有效或获得官方确认。必须检查来源角色、适用版本、业务规则依据、冲突、过期和 workaround。

## 知识核对

正式事实须对应候选涉及的对象、动作、范围及例外。线索只有在正式来源和关键条件得到核实后才能支持答案。证据不足时记录缺口，不补造答案。

## 审阅请求

不输出会被误解为已发生正式交接的 `knowledge_wiki_handoff`。使用 `handoff.knowledge_review_request` 表达候选数量、candidate refs、阻断风险和门禁状态。

候选只在证据治理明确放行，或用户明确要求审阅或沉淀本次候选时，交由知识维护人员审阅。

## 禁止

- 不输出 approved knowledge、正式 FAQ、最终引导文案或客服话术。
- 不把 workaround 包装成正式规则。
- 候选只随主观分析报告交付，正式知识写入由维护者按审阅结果处理。
- 不让“流程已完成”代替事实有效性校验。

