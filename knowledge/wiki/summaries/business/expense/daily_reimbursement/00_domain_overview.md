# 00_domain_overview

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-EXPENSE-DAILY_REIMBURSEMENT-00_DOMAIN_OVERVIEW
- page_type: summary
- source_path: knowledge/raw/business/expense/daily_reimbursement/00_domain_overview.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-05
- updated_at: 2026-05-05
- source_refs: [knowledge/raw/business/expense/daily_reimbursement/00_domain_overview.md]
- related_summaries:
  - knowledge/wiki/summaries/business/expense/daily_reimbursement/10_daily_reimbursement.md
  - knowledge/wiki/summaries/business/expense/daily_reimbursement/README.md
  - knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/00_domain_overview.md
  - knowledge/wiki/summaries/business/app_management/00_domain_overview.md
  - knowledge/wiki/summaries/business/approval_management/00_domain_overview.md

## 1. 知识定位

定义日常报销子域的职责范围和核心能力：回答「日常报销提供哪些能力、覆盖什么流程、如何进行费用管控」这一判断问题。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要判断某项能力是否属于日常报销子域时
- 需要了解日常报销的核心能力全景（发票核验、费用政策、预算管控、代发支付、凭证生成、数据报表）时
- 需要了解日常报销与外部系统的对接关系（国税局、招行代发、智能记账）时
- 需要确认日常报销的采集缺口时

## 3. 覆盖内容

本 raw 覆盖：

- 日常报销六大核心能力：发票核验（对接国税局查重验真）、费用政策管控、多维度预算管控（部门/项目/成本中心）、代发支付（一键支付+状态回写）、凭证生成（推送智能记账）、数据报表（多维统计）
- 全流程：提单-审批-报销支付-记账

不涉及：

- 日常报销各功能的详细配置和操作流程（需查 10_daily_reimbursement 和原始产品介绍）

## 4. 可直接使用的稳定结论

- 日常报销支持「提单-审批-报销支付-记账」全流程线上操作
- 发票在线查重验真，对接国税局接口，避免重复报销
- 支持按部门、项目、成本中心等多维度设置预算，超标可预警或禁止提交
- 报销单审批后直接推送代发，一键支付并状态回写
- 报销单据自动生成凭证，推送智能记账

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

- knowledge/wiki/summaries/business/expense/daily_reimbursement/10_daily_reimbursement.md
- knowledge/wiki/summaries/business/expense/daily_reimbursement/README.md
- knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/00_domain_overview.md
- knowledge/wiki/summaries/business/app_management/00_domain_overview.md
- knowledge/wiki/summaries/business/approval_management/00_domain_overview.md

> summary_path: knowledge/wiki/summaries/business/expense/daily_reimbursement/00_domain_overview.md
