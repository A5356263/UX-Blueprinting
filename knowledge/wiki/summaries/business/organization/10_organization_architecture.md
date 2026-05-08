# 10_organization_architecture

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-ORGANIZATION-10_ORGANIZATION_ARCHITECTURE
- page_type: summary
- source_path: knowledge/raw/business/organization/10_organization_architecture.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-08
- updated_at: 2026-05-08
- source_refs: [knowledge/raw/business/organization/10_organization_architecture.md]
- related_summaries:
  - knowledge/wiki/summaries/business/organization/00_domain_overview.md
  - knowledge/wiki/summaries/business/organization/11_legal_entities.md
  - knowledge/wiki/summaries/business/organization/12_cost_centers.md
  - knowledge/wiki/summaries/business/organization/13_function_and_view_model.md
  - knowledge/wiki/summaries/business/organization/14_member_binding_and_scope_generation.md

## 1. 知识定位

说明组织架构在新平台组织底座中的角色，回答“行政组织如何从旧结构主数据迁入多维组织并参与范围生成”。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要理解旧组织架构在新模型中的归位位置时
- 需要确认行政组织如何进入多维组织底座时
- 需要核对组织架构现有维护入口、字段和导入规则时
- 需要判断组织架构与成员模块的边界时

## 3. 覆盖内容

本 raw 覆盖：

- 新定位：组织架构默认归位到 `行政职能 / 组织架构视图`
- 多维组织中的作用：提供行政组织维度、参与视图汇总、成员挂载与范围计算
- 既有维护入口、基础字段、单个新增、全路径导入、普通导入规则

不涉及：

- 人事薪税侧对接细节
- 成员生命周期或授权规则

## 4. 可直接使用的稳定结论

- 组织架构已不再代表整个组织域，只是多维组织中的核心来源之一
- 原组织架构的默认语义位置是 `行政职能 / 组织架构视图`
- 行政组织数据会影响成员挂载、组织范围与业务过滤等后续链路
- 菜单拆分后，组织架构归组织模块，成员主体归成员模块

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

- knowledge/wiki/summaries/business/organization/00_domain_overview.md
- knowledge/wiki/summaries/business/organization/11_legal_entities.md
- knowledge/wiki/summaries/business/organization/12_cost_centers.md
- knowledge/wiki/summaries/business/organization/13_function_and_view_model.md
- knowledge/wiki/summaries/business/organization/14_member_binding_and_scope_generation.md

> summary_path: knowledge/wiki/summaries/business/organization/10_organization_architecture.md
