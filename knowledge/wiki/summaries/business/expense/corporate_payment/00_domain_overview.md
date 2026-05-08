# 00_domain_overview

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-EXPENSE-CORPORATE_PAYMENT-00_DOMAIN_OVERVIEW
- page_type: summary
- source_path: knowledge/raw/business/expense/corporate_payment/00_domain_overview.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-08
- updated_at: 2026-05-08
- source_refs: [knowledge/raw/business/expense/corporate_payment/00_domain_overview.md]
- related_summaries:
  - knowledge/wiki/summaries/business/expense/corporate_payment/10_corporate_payment.md
  - knowledge/wiki/summaries/business/expense/corporate_payment/README.md
  - knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/00_domain_overview.md
  - knowledge/wiki/summaries/business/app_management/00_domain_overview.md
  - knowledge/wiki/summaries/business/approval_management/00_domain_overview.md

## 1. 知识定位

定义对公报账子域的职责范围和核心能力：回答「对公报账提供哪些能力、支持什么业务场景、覆盖什么管理流程」这一判断问题。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要判断某项能力是否属于对公报账子域时
- 需要了解对公报账的核心能力全景（供应商管理、合同管理、发票核验、费用管控、外币支付、费用分摊、凭证生成）时
- 需要了解对公报账支持的业务场景（预付款支付、先票后款、到票核销、分期支付）时
- 需要确认对公报账的采集缺口时

## 3. 覆盖内容

本 raw 覆盖：

- 对公报账八大核心能力：4种业务场景（预付款支付/先票后款/到票核销/分期支付）、供应商管理（准入/变更审批+档案同步）、合同管理（框架/付款合同+临期提醒）、发票核验+费用政策管控+多维预算管控、外币支付、费用在线分摊、凭证生成推送智能记账

不涉及：

- 对公报账各功能的详细配置和操作流程（需查 10_corporate_payment 和原始产品介绍）

## 4. 可直接使用的稳定结论

- 对公报账覆盖企业基本对公采购及支付场景，实现供应商线上付款全流程管理
- 支持 4 种业务场景：预付款支付、先票后款、到票核销、分期支付，支持表单间核销关联和金额关联
- 供应商信息在单据中完成准入/变更审批后自动同步到供应商档案
- 合同管理支持框架及付款合同，并提供合同到期付款提醒
- 支持外币支付和费用在线分摊

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

- knowledge/wiki/summaries/business/expense/corporate_payment/10_corporate_payment.md
- knowledge/wiki/summaries/business/expense/corporate_payment/README.md
- knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/00_domain_overview.md
- knowledge/wiki/summaries/business/app_management/00_domain_overview.md
- knowledge/wiki/summaries/business/approval_management/00_domain_overview.md

> summary_path: knowledge/wiki/summaries/business/expense/corporate_payment/00_domain_overview.md
