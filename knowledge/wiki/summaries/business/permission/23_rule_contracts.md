# 23_rule_contracts

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-23_RULE_CONTRACTS
- page_type: summary
- source_path: knowledge/raw/business/permission/23_rule_contracts.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-05
- updated_at: 2026-05-05
- source_refs: [knowledge/raw/business/permission/23_rule_contracts.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

将权限域的 10 条核心规则固化为合同化表达，每条规则包含规则类型（前置/覆盖/计算/约束/修饰/边界/互斥）、失败结果和处理要求，是蓝图进行权限判定时必须遵守的规则合同。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要确认权限判定的规则优先级和执行顺序
- 判断某个操作是否会触发覆盖、互斥或边界限制
- 需要了解数据权限的条件组计算和最小约束规则
- 设计蓝图时需要保证治理模式互斥等规则被显式声明

## 3. 覆盖内容

本 raw 覆盖：

- 10 条核心规则：R-001 可见性前置、R-002 不可见覆盖、R-003 功能权限前置数据权限、R-004 数据范围范围类型前置、R-005 条件组计算规则、R-006 条件组最小约束、R-007 治理影响生效、R-008 子管理员边界限制、R-009 治理模式互斥、R-010 协作模型独立
- 每条规则包含：规则描述、类型、失败结果/处理要求

不涉及：

- 规则的判定链路执行顺序（在 20_decision_chain_contract 中定义）
- 失败结果的原因码详情（在 22_conflict_reason_codes 中定义）

## 4. 可直接使用的稳定结论

- R-001 到 R-003 定义了权限判定的前置链：可见性 -> 功能权限 -> 数据权限，必须按序判定
- R-005 和 R-006 定义了数据权限的核心计算逻辑：部分数据权限时组内交集、组间并集，且至少 1 个条件组、组内至少 1 个条件
- R-007 明确治理模式不改变授予事实，但改变是否已生效、何时生效、谁能改
- R-009 要求子管理员模式与双管理员模式不可同时开启，蓝图必须显式声明该互斥关系
- R-010 要求协作可见性模型不并入功能权限与数据范围模型，蓝图必须声明适用与不适用范围

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

> summary_path: knowledge/wiki/summaries/business/permission/23_rule_contracts.md
