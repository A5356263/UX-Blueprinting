# 04_object_relations

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-04_OBJECT_RELATIONS
- page_type: summary
- source_path: knowledge/raw/business/permission/04_object_relations.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-05
- updated_at: 2026-05-05
- source_refs: [knowledge/raw/business/permission/04_object_relations.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/10_capability_map.md

## 1. 知识定位

定义权限域中六类核心业务对象之间的四种关系类型（前置、覆盖、叠加、边界），解释了 subject-resource-action-scope-source-modifier 之间的联动逻辑，是理解权限判定链路的前置知识。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要理解权限域各对象之间的依赖和联动关系
- 判断某个权限结果为什么被覆盖或不生效时，需要理解对象间的覆盖关系
- 需要解释数据范围的叠加计算逻辑（条件组内交集、组间并集）
- 需要区分功能权限叠加与协作可见性的独立关系

## 3. 覆盖内容

本 raw 覆盖：

- 四种关系类型：核心关系（subject-resource-action-scope 联动）、前置关系（可见性 -> 功能权限 -> 数据范围的前置链）、覆盖关系（应用不可见覆盖/治理状态覆盖生效/子管理员范围隔离覆盖操作边界）、叠加关系（直授与角色在功能权限层叠加、数据范围条件组叠加）、边界关系（协作可见性独立、外部域为上下文）

不涉及：

- 具体规则条款（在 23_rule_contracts 中定义）、判定链路的详细步骤（在 20_decision_chain_contract 中定义）

## 4. 可直接使用的稳定结论

- 权限判断存在明确的前置链：可见性是功能权限和数据范围的前置门槛，功能权限是数据范围配置的前置条件，治理状态是最终生效的前置修饰层
- 覆盖关系中最关键的是：应用不可见对最终可达性具有覆盖性，治理状态不覆盖授予事实但可覆盖生效结果
- 数据范围叠加采用统一模型：全部数据权限直接放行，部分数据权限按条件组内交集、组间并集计算，无数据权限直接得到空范围
- 协作可见性独立于功能权限与数据范围，审批域/组织域/应用域作为外部依赖为权限域提供上下文

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
- knowledge/wiki/summaries/business/permission/10_capability_map.md

> summary_path: knowledge/wiki/summaries/business/permission/04_object_relations.md
