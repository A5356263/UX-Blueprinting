# 01_scope_and_boundary

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-01_SCOPE_AND_BOUNDARY
- page_type: summary
- source_path: knowledge/raw/business/permission/01_scope_and_boundary.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-07
- updated_at: 2026-05-07
- source_refs: [knowledge/raw/business/permission/01_scope_and_boundary.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md
  - knowledge/wiki/summaries/business/permission/10_capability_map.md

## 1. 知识定位

划定权限域的职责边界，明确权限域负责和不负责什么，以及权限域与组织域、应用域、审批域、协作域之间的分界线，同时定义了五个入口分区的语义和平台侧与业务侧的数据权限职责分工。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要判断某个业务语义或规则是否应归入权限域管理
- 需要理解权限域与相邻业务域（组织、应用、审批、协作）的边界和引用关系
- 需要区分数据权限的平台侧计算职责与业务侧语义职责
- 需要理解五大入口分区（People-centric/Role-centric/App-centric/Collaboration Visibility/Governance）的用途和边界
- 需要确认权限域不吸收哪些内容为本域规则真源

## 3. 覆盖内容

本 raw 覆盖：

- 职责边界：权限域负责的 5 类内容（对象定义、判定链路、权限关系、来源覆盖语义、查询配置审计合同），不直接负责的 5 类内容（页面结构、视觉交互文案、组织树定义、流程引擎实现、应用配置实现）
- 相邻域边界：与组织域（引用组织范围但不定义组织树）、与应用域（关心可见性与管理员但不定义应用生命周期）、与审批域（关心审批对生效的影响但不定义审批节点）、与协作域（保留协作可见性边界但协作规则不在此展开）
- 数据权限职责分工：平台侧负责统一计算模型（全部/部分/无 + 组内交集组间并集），业务侧负责提供维度和值域
- 入口分区语义：People-centric（按人配置与排障）、Role-centric（按角色治理）、App-centric（按应用可见性）、Collaboration Visibility（协作可见性模型）、Governance（治理与隔离）

不涉及：

- 具体权限页面的详细语义描述、判定链路细则、原因码体系

## 4. 可直接使用的稳定结论

- 权限域不吸收页面结构、视觉方案、组织树定义、审批引擎实现、应用配置实现为本域规则真源，但可引用这些外部信息
- 数据权限采用统一计算模型：先选范围类型（全部/部分/无），当为”部分”时条件组内取交集、组间取并集，至少保留 1 个条件组且组内至少 1 个条件；平台侧负责计算，业务侧不负责改写算法
- 应用可见不等于可操作，应用不可见具有覆盖性；协作可见性是独立于功能权限与数据范围的第三套模型
- 治理入口影响生效与责任，但不改变授权事实本身

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
- knowledge/wiki/summaries/business/permission/02_glossary.md
- knowledge/wiki/summaries/business/permission/03_business_objects.md
- knowledge/wiki/summaries/business/permission/04_object_relations.md
- knowledge/wiki/summaries/business/permission/10_capability_map.md

> summary_path: knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
