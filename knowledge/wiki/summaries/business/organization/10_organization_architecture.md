# 10_organization_architecture

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-ORGANIZATION-10_ORGANIZATION_ARCHITECTURE
- page_type: summary
- source_path: knowledge/raw/business/organization/10_organization_architecture.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-05
- updated_at: 2026-05-05
- source_refs: [knowledge/raw/business/organization/10_organization_architecture.md]
- related_summaries:
  - knowledge/wiki/summaries/business/organization/00_domain_overview.md
  - knowledge/wiki/summaries/business/organization/11_legal_entities.md
  - knowledge/wiki/summaries/business/organization/12_cost_centers.md
  - knowledge/wiki/summaries/business/organization/README.md
  - knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/10_enablement_paths.md

## 1. 知识定位

描述组织架构的维护方式和导入规则，回答「如何创建和管理企业层级组织」这一判断问题。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要创建或维护组织架构时
- 需要选择导入方式（单个新增/全路径导入/普通导入）时
- 需要了解组织架构的基础字段设置时
- 涉及组织架构的批量导入规则时

## 3. 覆盖内容

本 raw 覆盖：

- 两个维护入口：管理后台（组织->组织架构）、人事薪税侧对接入口
- 组织基础设置：预设字段（组织名称、组织类型、上级组织），支持自定义字段
- 三种新增方式：单个新增（适合简单场景）、全路径导入（使用 `/` 分隔符，自动创建层级，默认部门类型）、普通导入（通过上级组织编码识别层级，根组织编码默认 `0000`）

不涉及：

- 人事薪税侧的具体对接流程
- 组织架构的删除和归档操作

## 4. 可直接使用的稳定结论

- 组织架构用于维护企业层级关系与组织基础属性
- 两个维护入口：管理后台「组织->组织架构」和人事薪税侧对接入口
- 全路径导入时使用 `/` 作为组织分隔符，组织类型不填则默认部门类型
- 普通导入时组织编码、组织名称、上级组织编码为必填
- 根组织编码默认为 `0000`，若已修改则以修改后编码为准

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

- knowledge/wiki/summaries/business/organization/00_domain_overview.md
- knowledge/wiki/summaries/business/organization/11_legal_entities.md
- knowledge/wiki/summaries/business/organization/12_cost_centers.md
- knowledge/wiki/summaries/business/organization/README.md
- knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/10_enablement_paths.md

> summary_path: knowledge/wiki/summaries/business/organization/10_organization_architecture.md
