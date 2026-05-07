# 12_security_settings

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-SECURITY_MANAGEMENT-12_SECURITY_SETTINGS
- page_type: summary
- source_path: knowledge/raw/business/security_management/12_security_settings.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-07
- updated_at: 2026-05-07
- source_refs: [knowledge/raw/business/security_management/12_security_settings.md]
- related_summaries:
  - knowledge/wiki/summaries/business/security_management/00_domain_overview.md
  - knowledge/wiki/summaries/business/security_management/10_security_watermark.md
  - knowledge/wiki/summaries/business/security_management/11_operation_records.md
  - knowledge/wiki/summaries/business/security_management/README.md
  - knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/12_enterprise_status_and_change.md

## 1. 知识定位

描述登录安全、导出短信验证和截屏保护三项安全设置的具体规则，回答「如何提升企业账号安全和数据安全」这一判断问题。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要启用登录双重验证时
- 需要配置高风险导出场景的短信验证时
- 需要了解截屏保护功能时
- 涉及安全设置的权限管理（仅超级管理员可配置）时
- 需要设置导出短信验证的间隔时间时

## 3. 覆盖内容

本 raw 覆盖：

- 登录安全设置：开启后登录必须双重验证（密码 + 短信验证码）
- 导出短信验证：高风险导出场景（组织导出、员工导出、架构图下载、花名册数据导出）必须短信验证，支持设置验证间隔
- 截屏保护：开启后掌上薪福通 App 截屏/录屏时弹出警告
- 默认权限：仅超级管理员可配置安全设置

不涉及：

- 双重验证的具体技术实现
- 截屏保护的具体技术方案

## 4. 可直接使用的稳定结论

- 安全设置权限默认授予超级管理员，维护入口：管理后台 -> 安全管理 -> 安全设置
- 登录安全开启后，登录企业必须进行密码和短信验证码双重验证
- 高风险导出（组织、员工、架构图、花名册）场景需要短信验证码验证
- 导出短信验证支持设置验证间隔时间以应对频繁导出场景
- 截屏保护开启后，掌上薪福通 App 截屏或录屏时弹出警告

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
- knowledge/wiki/summaries/business/security_management/11_operation_records.md
- knowledge/wiki/summaries/business/security_management/README.md
- knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/12_enterprise_status_and_change.md

> summary_path: knowledge/wiki/summaries/business/security_management/12_security_settings.md
