# 10_capability_map

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-10_CAPABILITY_MAP
- page_type: summary
- source_path: knowledge/raw/business/permission/10_capability_map.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-07
- updated_at: 2026-05-07
- source_refs: [knowledge/raw/business/permission/10_capability_map.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

从“能力域 -> 页面承载”的角度说明权限页面仍然如何分工，同时补充它们在平台组织重构后与组织底座之间的依赖关系。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要判断某类权限治理能力由哪个页面承载时
- 需要理解组织底座变更会如何传导到权限页面输入时
- 需要区分“权限页面本身”和“权限页面引用的组织维度来源”时

## 3. 覆盖内容

本 raw 覆盖：

- 权限域既有六类能力与页面承载关系
- 平台组织重构后的上游依赖：成员主体、组织视图、组织范围会进入数据范围、查询排障、可见范围等能力
- 权限页与组织底座之间的边界说明

不涉及：

- 组织视图进入权限配置时的完整字段映射

## 4. 可直接使用的稳定结论

- 权限域页面分工本身没有被组织域替代
- 但权限页面的部分输入已经依赖新的组织底座结果
- 数据范围、子管理上限、可见范围和排障解释都会受到组织维度与组织范围影响
- 组织底座提供的是输入，不是权限页面本体

## 5. 必须回查 raw 的情况

以下情况不能只读 summary：

- 需要完整规则细节或精确条款时
- 需要正式证据或原文引用时
- 需要页面或流程的完整描述时
- 涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时
- summary 无法覆盖当前判断点或信息量不足时

## 6. 缺口 / 冲突 / 不确定项

- [GAP] 按权限查 / 按功能点查的现状承载仍待进一步核实
- [GAP] 当前资料未展开组织视图进入具体权限页面配置时的完整字段映射

## 7. 邻近阅读

弱指向 3-5 个相关 summary。

- knowledge/wiki/summaries/business/permission/00_domain_overview.md
- knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
- knowledge/wiki/summaries/business/permission/02_glossary.md
- knowledge/wiki/summaries/business/permission/03_business_objects.md
- knowledge/wiki/summaries/business/permission/04_object_relations.md

> summary_path: knowledge/wiki/summaries/business/permission/10_capability_map.md
