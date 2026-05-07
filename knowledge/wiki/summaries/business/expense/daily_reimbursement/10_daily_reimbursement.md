# 10_daily_reimbursement

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-EXPENSE-DAILY_REIMBURSEMENT-10_DAILY_REIMBURSEMENT
- page_type: summary
- source_path: knowledge/raw/business/expense/daily_reimbursement/10_daily_reimbursement.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-07
- updated_at: 2026-05-07
- source_refs: [knowledge/raw/business/expense/daily_reimbursement/10_daily_reimbursement.md]
- related_summaries:
  - knowledge/wiki/summaries/business/expense/daily_reimbursement/00_domain_overview.md
  - knowledge/wiki/summaries/business/expense/daily_reimbursement/README.md
  - knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/10_enablement_paths.md
  - knowledge/wiki/summaries/business/app_management/10_application_management.md
  - knowledge/wiki/summaries/business/approval_management/10_approval_management.md

## 1. 知识定位

描述薪福通日常报销的完整产品能力体系，包括发票核验、费用政策、预算管控、代发支付、凭证生成、数据报表和系统连通，回答「日常报销提供哪些能力、如何实现申请-报销-支付-记账一体化」这一判断问题。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要了解日常报销的完整能力清单和产品定位时
- 涉及发票核验（对接国税局查重验真）时
- 涉及费用政策管控和预算方案配置时
- 涉及代发支付流程和招行系统对接时
- 涉及凭证自动生成和智能记账时
- 需要了解日常报销的系统连通架构（招行云直连、CBS、薪资代发、网银）时

## 3. 覆盖内容

本 raw 覆盖：

- 发票核验：对接国税局接口，在线查重验真，确保发票准确性
- 费用政策：提前设置费用政策，管控员工报销费用，减少财务核对成本
- 预算管控：按部门、项目、成本中心等多维度设置预算，超标自动预警或禁止提交
- 代发支付：报销单审批后直接推送代发，一键支付+状态回写，员工秒收款
- 凭证生成：凭证一键生成，推送智能记账
- 数据报表：按部门、人员、费用等多维度统计费用
- 系统连通：对接招行云直连（自动获取出账回单）、薪资代发、网银、云直联，打通 CBS 跨行支付

不涉及：

- 费用政策、预算方案的具体配置字段和规则
- 管理员和员工的具体操作步骤

## 4. 可直接使用的稳定结论

- 日常报销覆盖 7 大能力块：发票核验、费用政策、预算管控、代发支付、凭证生成、数据报表、系统连通
- 发票对接国税局接口实现在线查重验真
- 预算管控支持按部门、项目、成本中心多维度，超标时可预警提醒或禁止提交
- 审批后直接推送代发，支持一键支付并回写支付状态
- 打通财务记账和支付系统，可对接招行云直连、薪资代发、网银、云直联和 CBS 跨行支付

## 5. 必须回查 raw 的情况

以下情况不能只读 summary：

- 需要完整规则细节或精确条款时
- 需要正式证据或原文引用时
- 需要页面或流程的完整描述时
- 涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时
- summary 无法覆盖当前判断点或信息量不足时

## 6. 缺口 / 冲突 / 不确定项

- [GAP] 日常报销常见问题12条未采集

## 7. 邻近阅读

弱指向 3-5 个相关 summary。

- knowledge/wiki/summaries/business/expense/daily_reimbursement/00_domain_overview.md
- knowledge/wiki/summaries/business/expense/daily_reimbursement/README.md
- knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/10_enablement_paths.md
- knowledge/wiki/summaries/business/app_management/10_application_management.md
- knowledge/wiki/summaries/business/approval_management/10_approval_management.md

> summary_path: knowledge/wiki/summaries/business/expense/daily_reimbursement/10_daily_reimbursement.md
