# 输出、交接与风险规则

## 1. 唯一事实源

独立或链式调用均交付 `spark-output/outcome-validation-recheck.md`。报告内记录来源、判断、限制和允许下游使用的条目；对话摘要与报告一致。

## 2. 交接白名单

Outcome 只能交给：

- `evidence-govern`
- `objective-data-analysis`
- `subjective-feedback-analysis`
- `experience-heuristic-analysis`
- `business-impact`
- `data-visualization`
- `evidence-archive`

不得直接交给 Root Cause。根因反馈必须先交 Evidence Govern 吸收。人工审核写入 `manual_review_requests[]`，不能伪装成技能交接。

Archive 交接必须含 `persist_in_archive` 和显式授权审核。Business Impact 只能消费 Pilot 以后可评估的效果，不能消费 pre-launch/demo 或 `not_evaluable`。

## 3. 引用与隐私

只输出结构化汇总或脱敏引用。禁止复制原始服务日志、逐条工单、明细用户/企业 ID、原始反馈正文或敏感字段。无法安全脱敏的错误信息可保留原始报错文本，但必须移除身份标识、令牌、密钥、联系方式、账户、设备、网络地址、完整请求体和其他可回溯参数。

## 4. Knowledge Wiki

Outcome 不直接发布知识。可沉淀的长期结论必须先经 Govern、Root Cause 跨案例学习和人工发布审核。单次效果、单次回归和未经复核的机制不能进入 Wiki。

