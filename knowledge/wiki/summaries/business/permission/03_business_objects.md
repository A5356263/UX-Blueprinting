# 03_business_objects

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-03_BUSINESS_OBJECTS
- page_type: summary
- source_path: knowledge/raw/business/permission/03_business_objects.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-07
- updated_at: 2026-05-07
- source_refs: [knowledge/raw/business/permission/03_business_objects.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md
  - knowledge/wiki/summaries/business/permission/10_capability_map.md

## 1. 知识定位

定义权限域中六类核心业务对象（主体、资源、动作、范围、来源、治理因子、状态）的最小属性集合，为判定链路和规则合同提供标准化的对象定义基础。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要明确权限域中各业务对象的准确定义和最小属性字段
- 设计权限判定链路时需要知道输入对象的结构
- 需要区分来源对象（source）和治理修饰因子（modifier）的属性差异
- 为权限审计或追溯功能定义数据模型字段

## 3. 覆盖内容

本 raw 覆盖：

- 六类核心业务对象：subject（主体）、resource（资源）、action（动作）、scope（范围）、source（来源）、modifier（治理因子）、state（状态）
- 每类对象包含定义、典型实例和最小属性集合

不涉及：

- 对象之间的具体关系规则（在 04_object_relations 中定义）
- 判定链路中如何使用这些对象（在 20_decision_chain_contract 中定义）

## 4. 可直接使用的稳定结论

- 六类核心对象及其最小属性：subject（subject_id/subject_type/org_scope/role_refs）、resource（resource_id/resource_type/parent_resource_id/app_id）、action（action_code/action_name/action_level）、scope（scope_type/scope_expression/scope_result）、source（source_enum/source_ref/source_priority）、modifier（modifier_type/modifier_state/modifier_ref）、state（state_code/effective_flag/actor_responsibility）
- source 是参与解释权限结果的授予来源，modifier 是影响生效与边界的修饰因子，二者必须区分
- 典型实例：subject=用户/成员/子管理员，resource=应用/菜单/操作点/数据对象，action=查看/编辑/导出/审批

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
- knowledge/wiki/summaries/business/permission/04_object_relations.md
- knowledge/wiki/summaries/business/permission/10_capability_map.md

> summary_path: knowledge/wiki/summaries/business/permission/03_business_objects.md
