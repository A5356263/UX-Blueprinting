# 10_corporate_payment

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-EXPENSE-CORPORATE_PAYMENT-10_CORPORATE_PAYMENT
- page_type: summary
- source_path: knowledge/raw/business/expense/corporate_payment/10_corporate_payment.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-07
- updated_at: 2026-05-07
- source_refs: [knowledge/raw/business/expense/corporate_payment/10_corporate_payment.md]
- related_summaries:
  - knowledge/wiki/summaries/business/expense/corporate_payment/00_domain_overview.md
  - knowledge/wiki/summaries/business/expense/corporate_payment/README.md
  - knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/10_enablement_paths.md
  - knowledge/wiki/summaries/business/app_management/10_application_management.md
  - knowledge/wiki/summaries/business/approval_management/10_approval_management.md

## 1. 知识定位

描述薪福通对公报账的完整产品能力体系，包括多场景业务支持、供应商管理、合同管理、发票核验、费用管控、外币支付、费用分摊、凭证生成与支付，回答「对公报账提供哪些能力、如何实现企业采购及支付场景规范化透明化管理」这一判断问题。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要了解对公报账的完整能力清单和产品定位时
- 涉及四种业务场景（预付款支付、先票后款、到票核销、分期支付）及其核销关联时
- 涉及供应商管理和合同管理的线上化流程时
- 涉及对公报账的费用管控（费用政策+预算管控+合同条款约束）时
- 涉及外币支付和费用在线分摊时
- 需要了解凭证生成和付款台账管理时

## 3. 覆盖内容

本 raw 覆盖：

- 业务场景：预付款支付、先票后款、到票核销、分期支付，支持表单间核销关联和金额关联
- 供应商管理：单据中完成供应商准入/变更审批，供应商信息自动同步到档案
- 合同管理：支持框架及付款合同，合同金额和付款条款在线查看，提供到期付款提醒
- 发票核验：在线查重验真，对接税局验证，对公付款单可关联供应商、合同信息及付款条款
- 费用管控：费用政策管控支付上限、多维度预算管控、合同条款约束不超额支付
- 外币支付：支持外币支付
- 费用在线分摊：按不同维度在线分摊费用
- 凭证生成与支付：凭证一键生成推送智能记账，财务可调整付款进度，付款日期临期提醒，预付款和合同台账随时查看

不涉及：

- 四种场景对公报账单的具体配置字段和规则
- 管理员和员工的具体操作步骤

## 4. 可直接使用的稳定结论

- 对公报账覆盖 8 大能力块：多场景业务、供应商管理、合同管理、发票核验、费用管控、外币支付、费用分摊、凭证生成与支付
- 支持预付款支付、先票后款、到票核销、分期支付四种场景，表单间可实现核销关联
- 供应商准入/变更审批在单据中完成，信息自动同步到供应商档案
- 付款需符合合同条款约定金额，确保不超额支付
- 财务可调整付款进度，提供预付款和合同台账随时查看付款情况

## 5. 必须回查 raw 的情况

以下情况不能只读 summary：

- 需要完整规则细节或精确条款时
- 需要正式证据或原文引用时
- 需要页面或流程的完整描述时
- 涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时
- summary 无法覆盖当前判断点或信息量不足时

## 6. 缺口 / 冲突 / 不确定项

- [GAP] 对公报账常见问题7条未采集

## 7. 邻近阅读

弱指向 3-5 个相关 summary。

- knowledge/wiki/summaries/business/expense/corporate_payment/00_domain_overview.md
- knowledge/wiki/summaries/business/expense/corporate_payment/README.md
- knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/10_enablement_paths.md
- knowledge/wiki/summaries/business/app_management/10_application_management.md
- knowledge/wiki/summaries/business/approval_management/10_approval_management.md

> summary_path: knowledge/wiki/summaries/business/expense/corporate_payment/10_corporate_payment.md
