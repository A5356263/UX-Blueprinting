# 14_actor_boundary

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-14_ACTOR_BOUNDARY
- page_type: summary
- source_path: knowledge/raw/business/permission/14_actor_boundary.md
- source_group: business
- status: active
- confidence: medium
- updated_at: 2026-04-24
- source_refs: [knowledge/raw/business/permission/14_actor_boundary.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 这份原始资料讲什么

本摘要对应原始资料《14_actor_boundary》，用于提供快速理解入口。

## 2. 适用范围 / 不适用范围

### 适用范围
- 适用于快速判断该原始资料是否与当前任务相关。
- 适用于构建 business 领域的背景理解与阅读入口。

### 不适用范围
- 不适用于替代原文证据、细节条款或最终业务裁决。

## 3. 关键事实

- 超级管理员：可见完整权限域；新任超级管理员默认自动继承系统级全量功能权限（除代发付款权限）与表单审批管理员权限
- 子管理员：可见与可操作范围取决于超管配置，包括组织管辖范围与应用管辖范围
- 普通管理员：能力边界以产品配置为准，不假设全能
- 员工：默认由所属角色或默认全员可见应用决定可见性
- 可见边界与可操作边界不必然一致
- 子管理员范围隔离会影响谁能看、谁能改、谁能授予；其授权动作必须同时落在组织范围与应用范围内

## 4. 关键术语 / 关键对象

- 角色视角
- 边界说明

## 5. 当前缺口 / 冲突 / 问题

- none

## 6. 相关摘要 / 建议继续阅读

- knowledge/wiki/summaries/business/permission/00_domain_overview.md
- knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
- knowledge/wiki/summaries/business/permission/02_glossary.md
- knowledge/wiki/summaries/business/permission/03_business_objects.md
- knowledge/wiki/summaries/business/permission/04_object_relations.md

> summary_path: knowledge/wiki/summaries/business/permission/14_actor_boundary.md
