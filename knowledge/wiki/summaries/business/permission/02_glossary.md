# 02_glossary

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-02_GLOSSARY
- page_type: summary
- source_path: knowledge/raw/business/permission/02_glossary.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-04
- updated_at: 2026-05-04
- source_refs: [knowledge/raw/business/permission/02_glossary.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md
  - knowledge/wiki/summaries/business/permission/10_capability_map.md

## 1. 知识定位

定义权限域的统一术语表，解决多入口、多角色协作时因命名不一致导致的沟通歧义，同时明确禁止混用的概念对，确保蓝图和方案中权限概念表达一致。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要统一权限域的核心术语和叫法，避免多团队协作时概念混用
- 判断两个权限概念是否可以混用或需要严格区分
- 需要了解每种权限来源（ACL_DIRECT/RBAC_ROLE/APP_VISIBILITY/COLLAB_VISIBILITY）的准确定义
- 需要确认数据范围计算相关术语（范围类型、条件组、条件）的标准表达

## 3. 覆盖内容

本 raw 覆盖：

- 核心术语（11 个）：subject/resource/action/context/visibility/function grant/data scope/scope mode/condition group/scope condition/governance state
- 来源相关术语（5 个）：ACL_DIRECT/RBAC_ROLE/APP_VISIBILITY/COLLAB_VISIBILITY/GOVERNANCE_MODE
- 关键表达（4 个）：final_effective_rule/conflict_reason_code/source_of_truth/evaluatable_snapshot
- 推荐统一叫法（5 条）和禁止混用的概念（4 条）

不涉及：

- 具体规则定义、判定链路、页面语义

## 4. 可直接使用的稳定结论

- 统一使用"可见性"表示是否可达，统一使用"功能权限"表示是否可操作，统一使用"数据范围"表示访问数据边界
- 数据权限统一使用"范围类型 + 条件组"描述，不回退到"维度 Tab + 业务侧自定义算法"口径
- 四组严禁混用的概念：可见性不等于可操作，授予来源不等于治理修饰因子，协作可见性不等于功能权限，数据范围不等于功能权限
- GOVERNANCE_MODE 是修饰因子（effect_modifier），不作为授予来源（source）

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
- knowledge/wiki/summaries/business/permission/03_business_objects.md
- knowledge/wiki/summaries/business/permission/04_object_relations.md
- knowledge/wiki/summaries/business/permission/10_capability_map.md

> summary_path: knowledge/wiki/summaries/business/permission/02_glossary.md
