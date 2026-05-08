# 10_enterprise_information_display

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-ENTERPRISE_SETTINGS-10_ENTERPRISE_INFORMATION_DISPLAY
- page_type: summary
- source_path: knowledge/raw/business/enterprise_settings/10_enterprise_information_display.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-08
- updated_at: 2026-05-08
- source_refs: [knowledge/raw/business/enterprise_settings/10_enterprise_information_display.md]
- related_summaries:
  - knowledge/wiki/summaries/business/enterprise_settings/00_domain_overview.md
  - knowledge/wiki/summaries/business/enterprise_settings/11_enterprise_login_page_customization.md
  - knowledge/wiki/summaries/business/enterprise_settings/12_enterprise_culture.md
  - knowledge/wiki/summaries/business/enterprise_settings/README.md
  - knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/10_enablement_paths.md

## 1. 知识定位

描述企业名称和企业详情信息的展示配置规则，回答「员工在不同场景下看到的企业信息如何被控制」这一判断问题。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要控制在打卡、邀请、日常使用等场景中展示的企业名称时
- 需要对企业敏感信息（社会信用代码、地址、法人信息）进行可见范围控制时
- 需要了解不同企业名称展示方式的依赖条件时
- 需要了解配置规则依赖于哪些基础数据时

## 3. 覆盖内容

本 raw 覆盖：

- 适用场景：员工打卡、邀请加入、日常使用左上角名称展示、敏感信息保密控制
- 企业名称展示规则：支持按认证企业、企业简称、合同公司、法人公司、组织架构展示
- 企业详情展示规则：可对统一社会信用代码、详细地址、法人姓名、法人证件类型、法人身份证号码配置可见范围（全员可见/部分成员可见/全员不展示）
- 规则依赖：按合同公司、法人公司、组织架构展示时依赖企业已维护对应基础数据

不涉及：

- 具体可见范围的人员选择器操作
- 企业基础数据的具体维护方式

## 4. 可直接使用的稳定结论

- 维护入口：管理后台 -> 企业设置 -> 企业信息展示配置
- 企业名称展示支持五种方式：按认证企业、企业简称、合同公司、法人公司、组织架构
- 企业详情信息（社会信用代码、地址、法人信息等）可见范围可设为全员可见、部分可见或全员不展示
- 按合同公司/法人公司/组织架构展示时，依赖对应基础数据已维护
- 适用场景包括打卡、邀请员工、日常使用和企业敏感信息保密控制

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

- knowledge/wiki/summaries/business/enterprise_settings/00_domain_overview.md
- knowledge/wiki/summaries/business/enterprise_settings/11_enterprise_login_page_customization.md
- knowledge/wiki/summaries/business/enterprise_settings/12_enterprise_culture.md
- knowledge/wiki/summaries/business/enterprise_settings/README.md
- knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/10_enablement_paths.md

> summary_path: knowledge/wiki/summaries/business/enterprise_settings/10_enterprise_information_display.md
