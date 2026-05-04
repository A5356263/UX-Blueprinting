# 22_conflict_reason_codes

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-22_CONFLICT_REASON_CODES
- page_type: summary
- source_path: knowledge/raw/business/permission/22_conflict_reason_codes.md
- source_group: business
- status: active
- confidence: medium
- updated_at: 2026-05-04
- source_refs: [knowledge/raw/business/permission/22_conflict_reason_codes.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

把“被覆盖、不生效、不可用”变成可枚举、可定位的原因码，并与判定链路层级对应。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要理解或使用本业务域的知识进行方案设计或判断时

## 3. 覆盖内容

本 raw 覆盖：

- 章节：1) 目的, 2) 原因域, 3) 最小原因码集合, 4) 定位字段

不涉及：

- 本 raw 未显式覆盖的内容需回查其他相关 raw 或补充来源

## 4. 可直接使用的稳定结论

- `VISIBILITY`：不可见、不可达
- `GRANT`：未授予、不可操作
- `SCOPE`：数据范围为空或条件不命中
- `GOVERNANCE`：待审批、未生效、被拒绝、撤销
- `BOUNDARY`：子管理员管辖范围外
- `VISIBILITY.APP_NOT_VISIBLE`：应用维度不可见覆盖个人维度权限

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
