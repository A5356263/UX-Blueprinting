# 21_source_model

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-21_SOURCE_MODEL
- page_type: summary
- source_path: knowledge/raw/business/permission/21_source_model.md
- source_group: business
- status: active
- confidence: medium
- updated_at: 2026-05-04
- source_refs: [knowledge/raw/business/permission/21_source_model.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

统一“权限从哪里来”的解释口径，避免多入口叠加后不可解释。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要理解或使用本业务域的知识进行方案设计或判断时

## 3. 覆盖内容

本 raw 覆盖：

- 章节：1) 目的, 2) source_enum, 2.5) effect_modifier, 3) source_priority, 4) source_of_truth

不涉及：

- 本 raw 未显式覆盖的内容需回查其他相关 raw 或补充来源

## 4. 可直接使用的稳定结论

- `ACL_DIRECT`：用户授权，个人直授
- `RBAC_ROLE`：角色管理，角色授予
- `APP_VISIBILITY`：应用管理的可见/不可见
- `COLLAB_VISIBILITY`：成员协作权限，仅在协作可见性场景作为来源
- `GOVERNANCE_MODE`：权限管理模式、审批互审、子管理员隔离
- `APP_VISIBILITY` 决定用户在工作台是否看得到应用，`ACL_DIRECT` / `RBAC_ROLE` 决定看得到后是否还能继续使用、操作其中功能，两者是同时存在的解释层

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
