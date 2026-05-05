# 14_actor_boundary

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-14_ACTOR_BOUNDARY
- page_type: summary
- source_path: knowledge/raw/business/permission/14_actor_boundary.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-05
- updated_at: 2026-05-05
- source_refs: [knowledge/raw/business/permission/14_actor_boundary.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

定义权限域中四类角色（超级管理员、子管理员、普通管理员、员工）的可见边界和可操作边界，说明不同角色的权限范围差异和约束规则。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要区分不同管理角色的权限边界和能力上限
- 判断某个操作是否在子管理员的管辖范围内
- 需要理解超级管理员的默认权限继承规则
- 设计页面权限控制时需要知道各角色的可见与可操作边界

## 3. 覆盖内容

本 raw 覆盖：

- 四类角色的视角和边界：超级管理员（可见完整权限域，新任自动继承全量功能权限除代发付款）、子管理员（范围取决于超管配置，包括组织管辖范围和应用管辖范围）、普通管理员（能力边界以产品配置为准）、员工（默认由所属角色或全员可见应用决定可见性）
- 边界说明：可见边界与可操作边界不必然一致、子管理员范围隔离影响查看/修改/授予、协作类应用中的员工可见性需额外参考协作可见性模型

不涉及：

- 各页面的角色权限矩阵细节（在具体页面语义中定义）

## 4. 可直接使用的稳定结论

- 超级管理员：新任自动继承系统级全量功能权限（除代发付款权限）与表单审批管理员权限
- 子管理员：组织管辖范围和应用管辖范围由超管配置，授权动作必须同时落在两个范围内
- 可见边界与可操作边界不必然一致，子管理员范围隔离会影响谁能看、谁能改、谁能授予
- 协作类应用中的员工可见性需额外参考协作可见性模型

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

> summary_path: knowledge/wiki/summaries/business/permission/14_actor_boundary.md
