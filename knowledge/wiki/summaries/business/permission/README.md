# permission

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-README
- page_type: summary
- source_path: knowledge/raw/business/permission/README.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-05
- updated_at: 2026-05-05
- source_refs: [knowledge/raw/business/permission/README.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

这是权限业务知识库的结构化入口，定义整个权限域的模块拆分方式、阅读顺序和维护迁移原则，用于指引知识消费者按正确路径进入各编号文件。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要了解权限知识库的整体结构和模块组织方式
- 判断应从哪个编号文件开始阅读权限域知识
- 需要了解权限知识的维护和迁移原则
- 需要确认权限域知识库的编写边界（什么该写、什么不该写）

## 3. 覆盖内容

本 raw 覆盖：

- 章节：知识库定位说明，阅读顺序（5 层：领域总览层 -> 业务能力与场景层 -> 决策与规则层 -> 体验转译层 -> 蓝图消费层）
- 原则：维护原则（只记录业务语义与规则合同、不写页面组件视觉、复用已有概念、新知识按编号落盘），迁移原则（已有知识拆分落盘、未覆盖先保留骨架、其他业务域可复用编号体系）

不涉及：

- 具体的权限规则、页面语义、判定链路或蓝图交接要求（这些内容在对应编号文件中）

## 4. 可直接使用的稳定结论

- 权限知识库按编号分层组织：00-04 为领域基础层，10-15 为业务能力与页面承载层，20-25 为决策与规则层，30-32 为体验转译层，40-50 为蓝图消费与补充层
- 本目录只记录业务语义、规则合同、责任边界与风险约束，不写具体页面、组件、视觉方案
- 新增知识优先落到对应编号模块，不回写为大一统长文
- 推荐阅读顺序：先读 00_domain_overview 了解领域目标，再读 10-12 理解业务承载，再读 20-25 理解规则与治理，最后读 30-42 理解体验转译与蓝图交接

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

> summary_path: knowledge/wiki/summaries/business/permission/README.md
