# 23_rule_contracts

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-23_RULE_CONTRACTS
- page_type: summary
- source_path: knowledge/raw/business/permission/23_rule_contracts.md
- source_group: business
- status: active
- confidence: medium
- updated_at: 2026-05-04
- source_refs: [knowledge/raw/business/permission/23_rule_contracts.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

本文件围绕「核心规则总表」组织内容，具体知识定位待从 raw 中进一步确认。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要理解或引用正式规则、判定链路或决策合同
- 判断权限、配置或状态裁决的生效逻辑与优先级

## 3. 覆盖内容

本 raw 覆盖：

- 规则：核心规则总表

不涉及：

- 本 raw 未显式覆盖的内容需回查其他相关 raw 或补充来源

## 4. 可直接使用的稳定结论

- 规则：先判断可见性，再判断功能权限与数据范围
- 规则：应用不可见对最终可达性具有覆盖性
- 失败结果：`VISIBILITY.APP_NOT_VISIBLE`
- 规则：先有功能权限，才允许配置与解释数据范围
- 失败结果：`GRANT.NO_FUNCTION_GRANT`
- 规则：数据范围必须先选择范围类型：`全部数据权限 / 部分数据权限 / 无数据权限`

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
