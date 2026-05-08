# 25_audit_contract

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-25_AUDIT_CONTRACT
- page_type: summary
- source_path: knowledge/raw/business/permission/25_audit_contract.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-08
- updated_at: 2026-05-08
- source_refs: [knowledge/raw/business/permission/25_audit_contract.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

定义权限审计的最低字段集合（9 个必填字段），确保按变更查的闭环可用，支持追溯”谁在何时对谁做了什么、是否审批、何时生效”，为审计功能和合规检查提供数据模型基础。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 设计权限审计功能的数据模型或日志结构
- 需要追溯某个权限变更的完整历史链路
- 评估现有系统的审计能力是否满足最低字段要求
- 需要确定操作类型（grant/revoke/edit/batch）和审批状态应如何记录

## 3. 覆盖内容

本 raw 覆盖：

- 审计目的：支持追溯”谁在何时对谁做了什么、是否审批、何时生效”
- 9 个最低审计字段：who/ to_whom/ what/ where/ when/ why/ approval/ outcome/ snapshot

不涉及：

- 审计日志的存储实现、具体审计查询页面设计

## 4. 可直接使用的稳定结论

- 最低审计字段 9 个：who（操作者）、to_whom（被操作对象）、what（操作类型 grant/revoke/edit/batch）、where（作用域）、when（发生时间与生效时间）、why（原因或备注）、approval（是否需要审批+实例 id+当前状态）、outcome（结果+conflict_reason_code）、snapshot（evaluatable_snapshot）
- 审计必须覆盖操作结果和冲突原因码（outcome + conflict_reason_code），不仅是操作记录
- 审计必须包含可验算快照（evaluatable_snapshot），支持事后追溯验证

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
