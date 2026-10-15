# 分析规则

## 固定漏斗与实际旅程

固定漏斗按声明步骤顺序查找每个任务的首次命中，输出逐步转化、整体转化、绝对流失、步骤时长和报错任务数。不得从数据中自动挑选一条“看起来最好”的漏斗替代业务定义。

实际旅程按任务和时间构造路径，连续重复步骤折叠；输出成功/未成功路径、循环、报错后事件类别，以及缺步、绕行、乱序、回退、重复步骤、意外终止等预期旅程偏差、节点、流向和终态。偏差只表示与已确认蓝图不同，不直接等于问题或根因。任务总数必须与终态总数对账。

旅程来源依次为完整节点明细、任务汇总完整路径、具备任务/时间/节点的通用事件。报错上下文不得作为完整路径或任务终态来源。分支蓝图必须声明适用条件、必经/可选/替代节点、允许终态和正式依据；没有正式蓝图时不执行偏差判断。

## 有业务依据的有限分群

只允许以下依据：

- user_confirmed
- uxb
- business_config
- upstream_requirement

分群按顺序匹配并强制：

- 规则重叠检查；
- 未命中进入 UNKNOWN；
- 每个任务只计入一个分群；
- 总体与分群任务数对账；
- 分群完成数与总体完成数对账，并复用同一归一化完成状态；
- 最小样本量和低样本风险；
- 保留规则依据与引用。

任一任务同时命中多个分群时，整个分群结果标记 not_evaluable，不按规则顺序强行分配。任务内分群字段默认 require_consistent；需要 first_non_empty 或 last_non_empty 时必须显式声明。

不得运行 K-means 或无业务依据的探索聚类，不得生成“高价值用户”“流失用户”等未经确认的策略标签。

只有至少两个样本充足的业务群体时才生成群体差异结论；覆盖整个范围的单一条件只是筛选，不包装成分群比较。

企业类型、行业、规模或活跃层级等外部维表必须显式声明关联来源、目标键、查找键和值字段。关联键冲突或多对多时失败关闭；保留覆盖率，未匹配任务进入 UNKNOWN。维表时间窗与任务窗口不一致时只能作为受限切片，不能静默解释为当前状态。

## 多来源指标核对

每个指标来源保留实际时间窗、总体、粒度、分子、分母和来源。相同 `scope_fingerprint` 的结果超出声明容差时标记 `source_conflict` 并阻断正式指标证据；不同总体或时间窗并列展示，不强行合并。正式汇总值缺少分母时只作为报告值，不反推计数。

## 功能使用

功能采用分析必须声明主体粒度、入口事件和使用事件；曝光、资格、完成事件可选。资格只能来自明确资格事件、字段条件或已确认名单，禁止用最终使用结果反推资格。每个比例保留分子、分母，且分子必须与分母集合求交，防止跨人群误算。

## 历史基线

- 当前窗口必须严格排除在历史窗口之外。
- 多行同周期时优先汇总分子/分母重算；否则必须声明 sum/mean/median/latest 聚合，latest 还需顺序字段。不得默认取最后一行或简单平均。
- 最少历史点默认 8 个；不足时 not_evaluable。
- 支持 median_quantile、mean_sd 和 same_period。
- same_period 必须提供业务周期键。
- 强异常仅在历史点不少于 100 时启用。
- 共享 baseline store 只允许按明确 baseline_id/version 精确读取。
- 校验 metric_contract_ref、grain、scenario_key 和 comparison_fingerprint。
- 无兼容基线时可生成符合共享 Baseline Item 的 `proposed/pending` candidate，但不得自动写 Store。

## 发现与正式证据

findings 是父技能汇总的客观发现；evidence_items 是允许跨技能消费的正式客观证据。每条 evidence_item 必须包含：

- 稳定 evidence_id 和 finding_ref；
- statement、claim_type、metric_refs；
- scene_descriptor 的 where、what、operation、source_attribution、evidence_form；
- allowed_uses、forbidden_uses；
- run_id 和 input_fingerprint 血缘。

每个完成且口径已确认的分析维度至少生成一条描述性 finding。只有样本量、影响规模、可靠性和口径确认状态齐全时才能生成 evidence_item；Top 1、分群差异或路径偏差没有明确阈值/基线/规则时只能作为描述性事实。

禁止把异常、分群差异或报错相关性写成根因。正常下一站是 evidence-govern；business-impact 只可将其作为对应成熟度的问题影响输入。
