# 40_blueprint_consumption_map

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-40_BLUEPRINT_CONSUMPTION_MAP
- page_type: summary
- source_path: knowledge/raw/business/permission/40_blueprint_consumption_map.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-04
- updated_at: 2026-05-04
- source_refs: [knowledge/raw/business/permission/40_blueprint_consumption_map.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

定义权限域各知识文件分别被业务蓝图和体验蓝图消费的映射关系，以及双向共用的文件清单，用于在构建蓝图时快速定位应读取哪些知识文件。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 构建业务蓝图时需要确定应从权限知识库消费哪些文件
- 构建体验蓝图时需要确定应从权限知识库消费哪些文件
- 需要区分哪些文件仅服务于业务蓝图、哪些仅服务于体验蓝图、哪些双向共用
- 需要评估蓝图所需知识的覆盖完整性

## 3. 覆盖内容

本 raw 覆盖：

- 业务蓝图消费清单（12 个文件）：00_domain_overview、01_scope_and_boundary、03_business_objects、10_capability_map、11_task_scenarios、12_query_and_configuration_paths、20_decision_chain_contract、21_source_model、22_conflict_reason_codes、23_rule_contracts、24_governance_state_model、25_audit_contract
- 体验蓝图消费清单（9 个文件）：01_scope_and_boundary、02_glossary、12_query_and_configuration_paths、14_actor_boundary、20_decision_chain_contract、22_conflict_reason_codes、30_experience_risk_patterns、31_experience_translation_requirements、32_copy_and_explanation_strategy
- 双向共用清单（4 个文件）：13_route_map、21_source_model、24_governance_state_model、25_audit_contract

不涉及：

- 各文件的具体内容和规则细节

## 4. 可直接使用的稳定结论

- 业务蓝图至少需消费 12 个权限知识文件，体验蓝图至少需消费 9 个
- 双向共用的 4 个文件（13_route_map、21_source_model、24_governance_state_model、25_audit_contract）对两种蓝图都是必读
- 业务蓝图侧重消费能力地图、任务场景、判定链路和规则合同（10-25 号文件），体验蓝图侧重消费术语表、角色边界、风险模式和转译要求（02/14/30-32 号文件）

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

> summary_path: knowledge/wiki/summaries/business/permission/40_blueprint_consumption_map.md
