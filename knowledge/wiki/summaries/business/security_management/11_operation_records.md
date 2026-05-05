# 11_operation_records

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-SECURITY_MANAGEMENT-11_OPERATION_RECORDS
- page_type: summary
- source_path: knowledge/raw/business/security_management/11_operation_records.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-05
- updated_at: 2026-05-05
- source_refs: [knowledge/raw/business/security_management/11_operation_records.md]
- related_summaries:
  - knowledge/wiki/summaries/business/security_management/00_domain_overview.md
  - knowledge/wiki/summaries/business/security_management/10_security_watermark.md
  - knowledge/wiki/summaries/business/security_management/12_security_settings.md
  - knowledge/wiki/summaries/business/security_management/README.md
  - knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/11_enterprise_creation_and_certification.md

## 1. 知识定位

描述操作记录的审计追溯能力，回答「如何查询和追溯用户在系统中的关键操作」这一判断问题。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要查询或追溯用户操作记录时
- 涉及审计、合规留痕或故障排查需求时
- 需要了解操作记录的覆盖范围时
- 需要按操作人、操作模块或关键字筛选记录时

## 3. 覆盖内容

本 raw 覆盖：

- 作用：审计、故障排查、合规留痕、数据变更追溯
- 记录内容：用户身份、操作时间、操作类型、操作对象
- 支持能力：按操作人筛选、按操作模块筛选、关键字搜索、查看详情
- 覆盖范围：管理后台、薪资代发、电子工资单、考勤管理、账号登录等业务中的新增、修改、删除行为

不涉及：

- 操作记录的数据存储策略和保留期限
- 操作记录的具体日志格式

## 4. 可直接使用的稳定结论

- 操作记录用于审计、故障排查、合规留痕和数据变更追溯
- 维护入口：管理后台 -> 安全管理 -> 操作记录
- 支持按操作人、操作模块筛选和关键字搜索
- 记录内容包括用户身份、操作时间、操作类型、操作对象
- 覆盖管理后台、薪资代发、电子工资单、考勤管理、账号登录等多个业务模块

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

- knowledge/wiki/summaries/business/security_management/00_domain_overview.md
- knowledge/wiki/summaries/business/security_management/10_security_watermark.md
- knowledge/wiki/summaries/business/security_management/12_security_settings.md
- knowledge/wiki/summaries/business/security_management/README.md
- knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/11_enterprise_creation_and_certification.md

> summary_path: knowledge/wiki/summaries/business/security_management/11_operation_records.md
