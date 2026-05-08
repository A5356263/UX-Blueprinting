# 14_member_binding_and_scope_generation

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-ORGANIZATION-14_MEMBER_BINDING_AND_SCOPE_GENERATION
- page_type: summary
- source_path: knowledge/raw/business/organization/14_member_binding_and_scope_generation.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-08
- updated_at: 2026-05-08
- source_refs: [knowledge/raw/business/organization/14_member_binding_and_scope_generation.md]
- related_summaries:
  - knowledge/wiki/summaries/business/organization/00_domain_overview.md
  - knowledge/wiki/summaries/business/organization/10_organization_architecture.md
  - knowledge/wiki/summaries/business/organization/11_legal_entities.md
  - knowledge/wiki/summaries/business/organization/12_cost_centers.md
  - knowledge/wiki/summaries/business/organization/13_function_and_view_model.md

## 1. 知识定位

说明成员作为独立主体如何挂载到平台组织底座，并解释组织管辖范围如何成为后续过滤和授权结果的上游输入。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要确认“组织”和“成员”为什么要拆成两个模块时
- 需要理解成员与多维组织之间的关系时
- 需要解释组织管辖范围从哪里来、被谁消费时
- 需要判断组织域和权限域在“范围”问题上的边界时

## 3. 覆盖内容

本 raw 覆盖：

- 组织与成员分治后的领域边界
- 成员作为权限主体，与视图和多维组织发生挂载关系的事实
- 组织管辖范围作为结果层参与业务过滤与标准组织组件消费
- 组织域和权限域在范围问题上的边界说明

不涉及：

- 挂载关系的完整字段设计
- 具体授权规则和审批规则

## 4. 可直接使用的稳定结论

- 成员是独立模块，不再并入组织菜单语义
- 成员会通过挂载关系接入多维组织，并影响组织范围结果
- 组织管辖范围不是静态字段，而是成员、视图、组织底座共同参与形成的结果层
- 标准组织组件、组织过滤、业务过滤、业务提醒定义都会消费范围结果

## 5. 必须回查 raw 的情况

以下情况不能只读 summary：

- 需要完整规则细节或精确条款时
- 需要正式证据或原文引用时
- 需要页面或流程的完整描述时
- 涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时
- summary 无法覆盖当前判断点或信息量不足时

## 6. 缺口 / 冲突 / 不确定项

- [GAP] 当前资料未展开成员挂载关系的字段结构、唯一性约束和变更规则

## 7. 邻近阅读

弱指向 3-5 个相关 summary。

- knowledge/wiki/summaries/business/organization/00_domain_overview.md
- knowledge/wiki/summaries/business/organization/10_organization_architecture.md
- knowledge/wiki/summaries/business/organization/11_legal_entities.md
- knowledge/wiki/summaries/business/organization/12_cost_centers.md
- knowledge/wiki/summaries/business/organization/13_function_and_view_model.md

> summary_path: knowledge/wiki/summaries/business/organization/14_member_binding_and_scope_generation.md
