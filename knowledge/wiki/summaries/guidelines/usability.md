# 可用性、交互控制与效率原则

- page_id: PG-SUMMARY-GUIDELINES-GUIDELINES-USABILITY
- page_type: summary
- source_path: knowledge/raw/guidelines/usability.md
- source_group: guidelines
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-05
- updated_at: 2026-05-05
- source_refs: [knowledge/raw/guidelines/usability.md]
- related_summaries:
  - knowledge/wiki/summaries/guidelines/README.md
  - knowledge/wiki/summaries/guidelines/accessibility.md
  - knowledge/wiki/summaries/guidelines/cognition.md
  - knowledge/wiki/summaries/guidelines/flow_mode.md
  - knowledge/wiki/summaries/guidelines/governance.md

## 1. 知识定位

提供最全面的交互可用性原则库，覆盖 Nielsen 10 条启发式、ISO 9241-110 7 条交互原则和 3 条交互效率定律，帮助在方案评审时系统性地自检是否存在可用性反模式，并指导在原则冲突时的取舍决策。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 评估交互方案的可用性、效率或操作合理性，进行系统性自检
- 需要将设计原则转化为具体的设计决策或自检问句
- 评审方案是否存在可用性反模式（操作后无反馈、术语混用、强制不可退、先错后罚等）
- 需要在原则之间做取舍（如安全 vs 效率、灵活 vs 简洁）
- 需要为异步/审批/批量/高风险操作设计状态反馈、错误恢复或风险控制机制
- 需要为新手与专家设计双通道操作路径

## 3. 覆盖内容

本 raw 覆盖：

- 原则：U 系列 10 条 Nielsen 启发式（U-01 系统状态可见至 U-10 就地帮助）、ISO 系列 7 条 ISO 9241-110 原则（ISO-01 适合任务至 ISO-07 可个性化）、I 系列 3 条交互效率定律（I-01 指向效率 Fitts / I-02 约束与防呆 Constraints / I-03 新手专家双通道）

不涉及：

- 本 raw 未显式覆盖的内容需回查其他相关 raw 或补充来源

## 4. 可直接使用的稳定结论

- 系统应持续告知状态与进展（U-01），操作后必须有反馈，不能只给"成功/失败"不解释
- 用业务语义表达规则与对象（U-02），避免内部字段直出；同概念同命名同规则（U-04）
- 关键动作必须可撤销/可回滚（U-03），不可撤销时需加强确认与审计
- 优先通过约束与提示在事前预防错误（U-05），而非先允许执行再泛化报错
- 错误信息必须可理解、可定位、可行动（U-09）：原因+影响+修复路径
- 兼容新手保底与专家提速（U-07/I-03）：默认值/批量/快捷入口，但不破坏可控与安全
- 高频目标应更易触达（I-01），危险操作避免太易触达；约束不可选时应解释原因（I-02）

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

- knowledge/wiki/summaries/guidelines/README.md
- knowledge/wiki/summaries/guidelines/accessibility.md
- knowledge/wiki/summaries/guidelines/cognition.md
- knowledge/wiki/summaries/guidelines/flow_mode.md
- knowledge/wiki/summaries/guidelines/governance.md

> summary_path: knowledge/wiki/summaries/guidelines/usability.md
