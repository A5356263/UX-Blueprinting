# 25_audit_contract

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-25_AUDIT_CONTRACT
- page_type: summary
- source_path: knowledge/raw/business/permission/25_audit_contract.md
- source_group: business
- status: active
- confidence: medium
- updated_at: 2026-05-04
- source_refs: [knowledge/raw/business/permission/25_audit_contract.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

确保按变更查的闭环可用，支持追溯“谁在何时对谁做了什么、是否审批、何时生效”。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要理解或引用正式规则、判定链路或决策合同
- 判断权限、配置或状态裁决的生效逻辑与优先级
- 涉及治理模式、审批链路或审计追溯

## 3. 覆盖内容

本 raw 覆盖：

- 章节：1) 目的, 2) 最低审计字段集合

不涉及：

- 本 raw 未显式覆盖的内容需回查其他相关 raw 或补充来源

## 4. 可直接使用的稳定结论

- `who`：操作者，如 `operator_id`、`operator_role`
- `to_whom`：被操作对象，如 `subject_id`、`target_user_id`
- `what`：操作类型，如 `grant`、`revoke`、`edit`、`batch`
- `where`：作用域，如 `app_id`、`role_id`、`org_scope`
- `when`：发生时间与生效时间
- `approval`：是否需要审批、实例 id、当前状态

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

> summary_path: knowledge/wiki/summaries/business/permission/25_audit_contract.md
