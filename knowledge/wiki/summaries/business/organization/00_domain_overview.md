# 00_domain_overview

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-ORGANIZATION-00_DOMAIN_OVERVIEW
- page_type: summary
- source_path: knowledge/raw/business/organization/00_domain_overview.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-07
- updated_at: 2026-05-07
- source_refs: [knowledge/raw/business/organization/00_domain_overview.md]
- related_summaries:
  - knowledge/wiki/summaries/business/organization/10_organization_architecture.md
  - knowledge/wiki/summaries/business/organization/11_legal_entities.md
  - knowledge/wiki/summaries/business/organization/12_cost_centers.md
  - knowledge/wiki/summaries/business/organization/13_function_and_view_model.md
  - knowledge/wiki/summaries/business/organization/14_member_binding_and_scope_generation.md

## 1. 知识定位

定义组织域已经从“静态企业结构主数据”升级为“平台组织底座”的职责边界，回答多维组织、职能、视图、组织范围、成员挂载分别归谁管理。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要判断某个概念是否属于平台组织底座时
- 需要区分组织域、成员域、权限域的边界时
- 需要理解组织架构、法人公司在新模型中的归位方式时
- 需要确认“组织”和“成员”菜单拆分后的领域划分时

## 3. 覆盖内容

本 raw 覆盖：

- 组织域的新核心对象：多维组织、职能、视图、组织管辖范围、多维组织组件
- 两个已明确的默认迁移：组织架构 -> 行政职能/组织架构视图，法人公司 -> 核算职能/法人公司视图
- 组织域与成员域、权限域之间的职责边界

不涉及：

- 人事领域组织治理
- 成员生命周期细节
- 具体授权规则与审批合同

## 4. 可直接使用的稳定结论

- 组织域现在承载的是平台组织底座，而不是单纯的结构主数据目录
- 视图是职能下的维度承载层，一个职能可以建立多个视图
- 组织模块负责组织底座，成员模块负责成员主体，二者已按菜单结构拆分
- 成员通过挂载关系接入多维组织，权限域消费组织范围结果但不由组织域定义授权规则

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

- knowledge/wiki/summaries/business/organization/10_organization_architecture.md
- knowledge/wiki/summaries/business/organization/11_legal_entities.md
- knowledge/wiki/summaries/business/organization/12_cost_centers.md
- knowledge/wiki/summaries/business/organization/13_function_and_view_model.md
- knowledge/wiki/summaries/business/organization/14_member_binding_and_scope_generation.md

> summary_path: knowledge/wiki/summaries/business/organization/00_domain_overview.md
