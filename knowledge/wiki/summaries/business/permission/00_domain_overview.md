# 00_domain_overview

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-00_DOMAIN_OVERVIEW
- page_type: summary
- source_path: knowledge/raw/business/permission/00_domain_overview.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-07
- updated_at: 2026-05-07
- source_refs: [knowledge/raw/business/permission/00_domain_overview.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md
  - knowledge/wiki/summaries/business/permission/10_capability_map.md

## 1. 知识定位

定义权限域的核心判断命题，并补充说明在平台组织底座重构后，权限域需要显式接住哪些来自组织域和成员域的上游输入。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要理解权限域为什么独立存在时
- 需要判断组织范围、成员主体、视图与权限域的关系时
- 需要确认哪些内容是权限域自身规则，哪些只是上游依赖事实时

## 3. 覆盖内容

本 raw 覆盖：

- 权限域的核心定义、要解决的问题、独立成域原因、目标、使用对象
- 平台组织重构后新增的上游依赖事实：成员主体、视图、组织管辖范围

不涉及：

- 具体授权规则、原因码或审批流细节

## 4. 可直接使用的稳定结论

- 权限域仍然是独立业务域，负责权限结果语义和判断链路
- 在新模型中，成员主体来自成员域，视图与组织范围来自组织域
- 组织域提供的是上游输入事实，不直接替代权限规则本身

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

- knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
- knowledge/wiki/summaries/business/permission/02_glossary.md
- knowledge/wiki/summaries/business/permission/03_business_objects.md
- knowledge/wiki/summaries/business/permission/04_object_relations.md
- knowledge/wiki/summaries/business/permission/10_capability_map.md

> summary_path: knowledge/wiki/summaries/business/permission/00_domain_overview.md
