# 20_decision_chain_contract

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-20_DECISION_CHAIN_CONTRACT
- page_type: summary
- source_path: knowledge/raw/business/permission/20_decision_chain_contract.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-07
- updated_at: 2026-05-07
- source_refs: [knowledge/raw/business/permission/20_decision_chain_contract.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

将权限域的核心业务事实固化为可复用的四层判定链路（L0 可见性 -> L1 功能权限 -> L2 数据权限 -> L3 治理与生效），并定义最终生效规则表达式（final_effective_rule），使蓝图能系统性地回答”为什么有/没有权限、来自哪里、谁改的、何时生效”。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要系统性判断一个权限结果的完整生效逻辑
- 需要理解可见性、功能权限、数据权限、治理状态之间的判定顺序和短路规则
- 需要构造或解释 final_effective_rule 表达式
- 需要为排障或审计场景确定每一层的证据要求（命中的规则标识、授予来源清单、scope_expression、state_model 当前态）

## 3. 覆盖内容

本 raw 覆盖：

- 四层判定链路：L0 可见性门槛（不可见即不可达，具有覆盖性，可短路但需输出被短路层配置摘要）、L1 功能权限（以末级菜单或操作点为粒度）、L2 数据权限（全部/部分/无三种范围类型，部分时组内交集组间并集，至少 1 组且组内至少 1 条件）、L3 治理与生效（输出是否已生效与卡点）
- final_effective_rule 表达式及其 7 种结果场景
- 各层的证据要求

不涉及：

- 具体的来源枚举和优先级（在 21_source_model 中定义）、原因码详情（在 22_conflict_reason_codes 中定义）

## 4. 可直接使用的稳定结论

- 判定原则：先判断是否可达/可见，再判断是否可操作，再判断数据范围，最后叠加治理与生效
- L0 不可见具有覆盖性，可短路为不可达，但排障时仍需输出被短路层的配置摘要
- final_effective_rule = VisibilityGate AND FunctionGrant AND DataScope AND GovernanceState；DataScope 是多值结果非纯布尔，GovernanceState 是状态节点非纯布尔
- 部分数据权限下执行条件组内交集、组间并集，且必须满足最小约束（至少 1 组且组内至少 1 条件）

## 5. 必须回查 raw 的情况

以下情况不能只读 summary：

- 需要完整规则细节或精确条款时
- 需要正式证据或原文引用时
- 需要页面或流程的完整描述时
- 涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时
- summary 无法覆盖当前判断点或信息量不足时

## 6. 缺口 / 冲突 / 不确定项

- none

## 7. 邻近阅读

弱指向 3-5 个相关 summary。

- knowledge/wiki/summaries/business/permission/00_domain_overview.md
- knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
- knowledge/wiki/summaries/business/permission/02_glossary.md
- knowledge/wiki/summaries/business/permission/03_business_objects.md
- knowledge/wiki/summaries/business/permission/04_object_relations.md

> summary_path: knowledge/wiki/summaries/business/permission/20_decision_chain_contract.md
