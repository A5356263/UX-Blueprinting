# 22_conflict_reason_codes

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-22_CONFLICT_REASON_CODES
- page_type: summary
- source_path: knowledge/raw/business/permission/22_conflict_reason_codes.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-04
- updated_at: 2026-05-04
- source_refs: [knowledge/raw/business/permission/22_conflict_reason_codes.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

将”被覆盖、不生效、不可用”等权限失败结果转化为可枚举、可定位到判定链路层级的原因码体系，使排障和审计场景能精确定位失败原因和阻塞来源。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要对权限失败结果进行原因定位和分类
- 设计排障或审计功能时需要标准化的原因码枚举
- 需要将某个失败结果对应到判定链路的特定层级
- 需要确定排障信息应包含的定位字段

## 3. 覆盖内容

本 raw 覆盖：

- 5 个原因域：VISIBILITY（不可见/不可达）、GRANT（未授予/不可操作）、SCOPE（数据范围为空或条件不命中）、GOVERNANCE（待审批/未生效/被拒绝/撤销）、BOUNDARY（子管理员管辖范围外）
- 7 个最小原因码：VISIBILITY.APP_NOT_VISIBLE、GRANT.NO_FUNCTION_GRANT、SCOPE.DATA_SCOPE_EMPTY、SCOPE.CONDITION_GROUP_REQUIRED、SCOPE.CONDITION_REQUIRED、GOVERNANCE.PENDING_APPROVAL、BOUNDARY.OUT_OF_ADMIN_SCOPE
- 5 个定位字段：reason_code/failed_layer/blocking_source/blocking_modifier/rule_ref

不涉及：

- 具体规则条款和判定链路细节（在 20_decision_chain_contract 和 23_rule_contracts 中定义）

## 4. 可直接使用的稳定结论

- 5 个原因域覆盖权限失败的所有层级：VISIBILITY/GRANT/SCOPE/GOVERNANCE/BOUNDARY
- 当范围类型为”部分数据权限”时，未保留条件组返回 SCOPE.CONDITION_GROUP_REQUIRED，条件组存在但组内无有效条件返回 SCOPE.CONDITION_REQUIRED
- 子管理员超出管辖范围的操作应返回 BOUNDARY.OUT_OF_ADMIN_SCOPE
- 排障定位需同时输出 reason_code、failed_layer、blocking_source、blocking_modifier、rule_ref 五个字段

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

> summary_path: knowledge/wiki/summaries/business/permission/22_conflict_reason_codes.md
