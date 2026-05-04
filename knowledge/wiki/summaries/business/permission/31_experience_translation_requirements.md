# 31_experience_translation_requirements

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-31_EXPERIENCE_TRANSLATION_REQUIREMENTS
- page_type: summary
- source_path: knowledge/raw/business/permission/31_experience_translation_requirements.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-04
- updated_at: 2026-05-04
- source_refs: [knowledge/raw/business/permission/31_experience_translation_requirements.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

将权限域的业务语义转译为体验蓝图的具体输出要求，定义页面级 10 个必填字段和 14 条权限域重点转译规则，确保业务规则在体验表达中不失真、不混淆。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 构建体验蓝图时需要知道权限页面必须输出哪些字段
- 需要将业务语义（功能权限/数据权限/治理模式）转译为体验表达时，确保不混淆关键概念
- 需要确认页面的解释能力是否满足"为什么有/没有、来自哪里、何时生效"的回答要求
- 需要检查体验输出是否区分了应用可见性与后台管理权限、查询页与配置页、角色页与单人排障页

## 3. 覆盖内容

本 raw 覆盖：

- 10 个页面级必填字段：页面名、页面类型、入口角色、页面目标、核心模块及顺序、关键操作、关键状态、上游入口/下游跳转、必须解释点、与其他页面关系
- 14 条权限域重点转译要求：功能权限与数据权限分开表达、数据权限表达为"范围类型+条件组"模型、三种范围类型、计算规则、最小约束、职责边界、应用可见性与后台权限分开、治理模式为系统级规则、查询页为解释排障入口、角色页为模板化授权入口、应用设置页为双职责页面等

不涉及：

- 具体的视觉效果、交互细节、文案编写

## 4. 可直接使用的稳定结论

- 体验蓝图必须把功能权限与数据权限分开表达，不能合并为一个笼统的"权限配置"
- 必须把数据权限表达为"范围类型 + 条件组"模型，三种范围类型（全部/部分/无），部分时组内交集、组间并集
- 必须把应用可见性与后台管理权限分开表达；必须把治理模式表达为系统级规则而非普通开关
- 当页面涉及失败结果时，必须显性暴露失败层级与原因码；涉及审批/生效/撤销时，必须说明状态、责任人与下一步动作

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

> summary_path: knowledge/wiki/summaries/business/permission/31_experience_translation_requirements.md
