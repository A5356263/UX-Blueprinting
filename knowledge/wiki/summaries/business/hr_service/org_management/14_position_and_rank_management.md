# 14_position_and_rank_management

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-HR_SERVICE-ORG_MANAGEMENT-14_POSITION_AND_RANK_MANAGEMENT
- page_type: summary
- source_path: knowledge/raw/business/hr_service/org_management/14_position_and_rank_management.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-08
- updated_at: 2026-05-08
- source_refs: [knowledge/raw/business/hr_service/org_management/14_position_and_rank_management.md]
- related_summaries:
  - knowledge/wiki/summaries/business/hr_service/org_management/00_domain_overview.md
  - knowledge/wiki/summaries/business/hr_service/org_management/13_headcount_management.md
  - knowledge/wiki/summaries/business/hr_service/org_management/README.md
  - knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/14_account_common_issues.md
  - knowledge/wiki/summaries/business/hr_service/employee_management/14_employee_roster.md

## 1. 知识定位

描述岗位管理和职级管理的核心概念和维护方式，回答「岗位(position)和职位(job)的区别是什么」以及「如何搭建企业职级体系」这两个判断问题。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要区分岗位(position)和职位(job)的概念时
- 需要了解岗位与编制的关系时
- 涉及职级通道（M级/P级）的创建和维护时
- 需要了解职级与在职人数的统计关系时

## 3. 覆盖内容

本 raw 覆盖：

- 岗位与职位的概念区分：岗位=具体工作职责(position)如"人力资源部招聘经理"，职位=关键职责集合(job)如"经理""总经理"
- 岗位维护：支持单条新增和批量导入，可按部门差异化设置
- 岗位与编制的关系：岗位编制需先做岗位与部门关联，总数 ≤ 部门直属编制数
- 职级通道：管理通道（M级）、专业通道（P级），支持自定义通道代码
- 职级维护：为通道添加编码及名称，支持单笔新增和批量导入
- 职级统计：实时统计各职级在职人数

不涉及：

- 岗位与薪资/绩效的关联关系
- 职级通道是否支持 M/P 之外的自定义类型

## 4. 可直接使用的稳定结论

- 岗位(position) = 具体工作职责（如"人力资源部招聘经理"）
- 职位(job) = 关键职责集合（如"经理"、"总经理"）
- 职级通道支持管理通道（M级）和专业通道（P级）
- 岗位编制需先做岗位与部门关联
- 岗位和职级均支持单条新增和批量导入

## 5. 必须回查 raw 的情况

以下情况不能只读 summary：

- 需要完整规则细节或精确条款时
- 需要正式证据或原文引用时
- 需要页面或流程的完整描述时
- 涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时
- summary 无法覆盖当前判断点或信息量不足时

## 6. 缺口 / 冲突 / 不确定项

- [GAP] 职级通道类型除 M/P 外是否支持自定义通道未明确
- [GAP] 岗位与薪资/绩效的关联关系未在帮助文档中展开

## 7. 邻近阅读

弱指向 3-5 个相关 summary。

- knowledge/wiki/summaries/business/hr_service/org_management/00_domain_overview.md
- knowledge/wiki/summaries/business/hr_service/org_management/13_headcount_management.md
- knowledge/wiki/summaries/business/hr_service/org_management/README.md
- knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/14_account_common_issues.md
- knowledge/wiki/summaries/business/hr_service/employee_management/14_employee_roster.md

> summary_path: knowledge/wiki/summaries/business/hr_service/org_management/14_position_and_rank_management.md
