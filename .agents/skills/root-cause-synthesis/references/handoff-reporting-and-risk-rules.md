# 交接、报告与风险规则

## 封闭下游白名单

- `evidence-govern`：补证需求、生命周期 Patch、模式候选；
- `problem-framing`：治理方向、异常状态、设计关注点和验证假设；
- `business-impact`：问题机制、限制和指标方向，不包含估值；
- `outcome-validation-recheck`：候选根因与验证假设；必须另有正式 Intervention Contract；
- `data-visualization`：只展示候选机制链；
- `knowledge-wiki`：仅跨案例模式候选，且 publication review pending；
- `evidence-archive`：显式授权的最小候选快照。

缺客观、主观或启发式证据时只向 Evidence Govern 提交补证需求，不直接回跳来源技能。人工审核放入 `manual_review_requests[]`，不得伪装成 Skill。

## 人工审核

强混杂、强反证、规则/权限/故障判断、准备进入设计、知识发布或归档时生成局部审核请求。审核只阻断受影响候选、用途或交接。

## 报告

独立或链式调用均交付同一份 Markdown，写明候选、治理报告条目、反证、限制与放行范围。对话摘要以报告为准。

## 隐私

只保存 Canonical Evidence ID、脱敏来源引用、聚合场景/分群、机制、反证和限制。不得保存原始反馈、日志、逐用户路径、真实用户/企业/工单标识或敏感故障正文。

## 写入

正式产物为 `spark-output/root-cause-synthesis.md`。完成证据、隐私和交接核对后写入。归档通过证据归档 Skill 的显式授权路径。
