# 15_page_carrier_semantics

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-15_PAGE_CARRIER_SEMANTICS
- page_type: summary
- source_path: knowledge/raw/business/permission/15_page_carrier_semantics.md
- source_group: business
- status: active
- confidence: medium
- updated_at: 2026-05-04
- source_refs: [knowledge/raw/business/permission/15_page_carrier_semantics.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

本文件只补“页面承载语义层”。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 判断某个能力由哪个页面承载
- 判断页面承担配置、查询、解释还是治理职责
- 涉及治理模式、审批链路或审计追溯
- 需要理解页面、对象或规则的语义定义与解释方式

## 3. 覆盖内容

本 raw 覆盖：

- 页面：1. 页面语义卡模板, 2. 用户直授相关页面, 3. 角色授权相关页面, 4. 全局治理相关页面, 5. 协作可见性相关页面
- 风险：8. 当前缺口
- 章节：0. 文件定位

不涉及：

- 本 raw 未显式覆盖的内容需回查其他相关 raw 或补充来源

## 4. 可直接使用的稳定结论

- 它用于说明权限域中的关键页面分别承载了什么业务语义，包括：
- 菜单/功能位置：通用权限管理 -> 用户授权
- 谁会进入：超管、子管理员、拥有用户授权菜单权限的普通用户
- 页面目标：添加指定用户，并为用户配置功能权限、数据权限、角色关联等管理能力
- 模块A：检索过滤区，用于按姓名、手机号、角色等维度定位目标用户
- 模块B：全局批量操作区，用于承载添加用户、批量角色关联、权限设置、移除、导出

## 5. 必须回查 raw 的情况

以下情况不能只读 summary：

- 需要完整规则细节或精确条款时
- 需要正式证据或原文引用时
- 需要页面或流程的完整描述时
- 涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时
- summary 无法覆盖当前判断点或信息量不足时

## 6. 缺口 / 冲突 / 不确定项

- [GAP] 权限查询中的按角色查、按权限查、按功能点查的现状承载尚未核实
- [GAP] 部分治理弹窗和配置页的下游跳转未在现有页面事实中给出
- [GAP] 权限明细视图的独立页面语义尚未在现有材料中展开

## 7. 邻近阅读

弱指向 3-5 个相关 summary。

- knowledge/wiki/summaries/business/permission/00_domain_overview.md
- knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
- knowledge/wiki/summaries/business/permission/02_glossary.md
- knowledge/wiki/summaries/business/permission/03_business_objects.md
- knowledge/wiki/summaries/business/permission/04_object_relations.md

> summary_path: knowledge/wiki/summaries/business/permission/15_page_carrier_semantics.md
