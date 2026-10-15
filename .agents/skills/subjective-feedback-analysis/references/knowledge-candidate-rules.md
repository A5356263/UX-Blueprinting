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

## Knowledge Wiki 消费

按 `index → 必要 README/单一 raw → 命中章节 → 最小充分即停止` 定向核对。index 和 README 只负责路由，raw 是正式事实。未命中时记录知识缺口，不遍历 raw，不补造答案。

## 审阅请求

不输出会被误解为已发生正式交接的 `knowledge_wiki_handoff`。使用 `handoff.knowledge_review_request` 表达候选数量、candidate refs、阻断风险和门禁状态。

只有两种情况 Knowledge Wiki 可以读取候选：`evidence-govern` 明确放行；用户明确要求审阅或沉淀本次候选。

## 禁止

- 不输出 approved knowledge、正式 FAQ、最终引导文案或客服话术。
- 不把 workaround 包装成正式规则。
- 不自动创建或修改 Knowledge Wiki raw。
- 不让“流程已完成”代替事实有效性校验。

