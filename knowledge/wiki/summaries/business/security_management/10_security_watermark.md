# 10_security_watermark

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-SECURITY_MANAGEMENT-10_SECURITY_WATERMARK
- page_type: summary
- source_path: knowledge/raw/business/security_management/10_security_watermark.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-08
- updated_at: 2026-05-08
- source_refs: [knowledge/raw/business/security_management/10_security_watermark.md]
- related_summaries:
  - knowledge/wiki/summaries/business/security_management/00_domain_overview.md
  - knowledge/wiki/summaries/business/security_management/11_operation_records.md
  - knowledge/wiki/summaries/business/security_management/12_security_settings.md
  - knowledge/wiki/summaries/business/security_management/README.md
  - knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/10_enablement_paths.md

## 1. 知识定位

描述安全水印的配置参数、内容规则和启用方式，回答「如何配置全局安全水印以防止信息泄露」这一判断问题。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要启用或配置安全水印时
- 需要了解水印支持的动态参数和配置项时
- 需要区分网页版和移动端水印设置时
- 涉及水印权限（仅超级管理员可配置）的判断时

## 3. 覆盖内容

本 raw 覆盖：

- 默认权限：仅超级管理员可设置
- 初始状态：默认关闭，需手动启用
- 可配置参数：水印内容、文字大小、透明度、样式、角度、密度
- 水印内容规则：支持动态参数 `$name` 和 `$date`，也支持固定文字如企业名称
- 网页版和移动端可分别设置字号，支持预览后保存

不涉及：

- 水印生效后的具体视觉效果
- 水印被截屏绕过的情况

## 4. 可直接使用的稳定结论

- 安全水印默认关闭，需由超级管理员手动启用
- 维护入口：管理后台 -> 安全管理 -> 安全水印
- 水印内容支持动态变量 `$name` 和 `$date`，也可输入固定文字
- 可配置参数：内容、文字大小、透明度、样式、角度、密度
- 网页版和移动端可分别设置水印字号，保存后全企业生效

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
- knowledge/wiki/summaries/business/security_management/11_operation_records.md
- knowledge/wiki/summaries/business/security_management/12_security_settings.md
- knowledge/wiki/summaries/business/security_management/README.md
- knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/10_enablement_paths.md

> summary_path: knowledge/wiki/summaries/business/security_management/10_security_watermark.md
