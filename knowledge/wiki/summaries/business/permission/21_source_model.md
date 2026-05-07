# 21_source_model

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-21_SOURCE_MODEL
- page_type: summary
- source_path: knowledge/raw/business/permission/21_source_model.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-07
- updated_at: 2026-05-07
- source_refs: [knowledge/raw/business/permission/21_source_model.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

统一”权限从哪里来”的解释口径，定义 4 种授予来源枚举（source_enum）和 1 种治理修饰因子（effect_modifier），说明来源优先级和每种来源的事实源承载位置，避免多入口叠加后不可解释。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要解释某个权限结果来自哪个授予来源
- 判断 APP_VISIBILITY 和 ACL_DIRECT/RBAC_ROLE 如何在同一个权限结果中同时存在
- 需要确定修改某个来源授权应该去哪个页面
- 需要区分来源（source）和修饰因子（modifier）的不同作用

## 3. 覆盖内容

本 raw 覆盖：

- 4 种授予来源枚举：ACL_DIRECT（用户授权/个人直授）、RBAC_ROLE（角色管理/角色授予）、APP_VISIBILITY（应用管理的可见/不可见）、COLLAB_VISIBILITY（成员协作权限）
- 1 种修饰因子：GOVERNANCE_MODE（不改变授予事实，只影响生效/谁能改/何时生效）
- 来源优先级：APP_VISIBILITY 的不可见对可达性有覆盖性；ACL_DIRECT 和 RBAC_ROLE 在功能权限层共同参与解释
- 每种来源的事实源承载位置

不涉及：

- 具体判定链路（在 20_decision_chain_contract 中定义）

## 4. 可直接使用的稳定结论

- APP_VISIBILITY 决定用户在工作台是否看得到应用，ACL_DIRECT/RBAC_ROLE 决定看得到后是否还能使用操作其中功能，两者是同时存在的解释层
- ACL_DIRECT 和 RBAC_ROLE 在功能权限层共同参与解释；COLLAB_VISIBILITY 默认不并入功能权限来源叠加
- GOVERNANCE_MODE 作为修饰因子，不改变授予事实，只影响是否生效、谁能改、何时生效
- 如需修改角色来源授权，应回到角色管理页完成，不能在用户授权页修改

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

> summary_path: knowledge/wiki/summaries/business/permission/21_source_model.md
