# 设计准则

- page_id: PG-SUMMARY-GUIDELINE-设计准则-README
- page_type: summary
- source_path: knowledge/raw/设计准则/README.md
- source_group: guideline
- status: draft
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-28
- updated_at: 2026-05-28
- related_summaries:
  - knowledge/wiki/summaries/设计准则/信息架构.md
  - knowledge/wiki/summaries/设计准则/可用性.md
  - knowledge/wiki/summaries/设计准则/可读性.md
  - knowledge/wiki/summaries/设计准则/无障碍.md
  - knowledge/wiki/summaries/设计准则/治理.md
- source_refs: [knowledge/raw/设计准则/README.md]

## 1. 知识定位

设计准则域的总入口路由卡。解决"面对具体设计方案时，从哪些设计维度进行体验判断"的问题——当需要对一个功能、页面或流程做出体验评估时，本域提供跨业务、跨产品复用的通用设计原则体系，覆盖信息架构、可用性、可读性、无障碍、治理、流程模式、视觉、认知、质量九个主题维度。本域不定义业务规则，只提供可复用的设计判断依据。

## 2. 任务触发线索

在以下设计任务中触发：
- 设计评审或方案评估，需要确定应查阅哪些设计原则主题
- 体验自检或风险识别，需要系统性地扫查设计维度
- 设计推导，需要引用通用原则作为判断依据
- 新增设计知识，需要确定该知识应归入哪个原则主题

## 3. 覆盖内容

覆盖 9 个主题文件、40+ 条原则卡。每条原则卡固定包含八个字段：**来源**（理论出处）、**定义**（核心含义）、**触发**（适用设计场景）、**推导输出**（设计决策方向）、**文档落点**（产物中的位置）、**自检问句**（验证问题）、**反模式**（常见错误做法）、**取舍提示**（两难权衡建议）。按主题域分布：
- 信息架构（3条）：IA-01 信息气味、IA-02 分块、IA-03 单一语义源
- 可用性（20条）：U-01~U-10（Nielsen 10条）+ ISO-01~ISO-07（ISO 9241-110 7条）+ I-01~I-03（交互效率 3条）
- 可读性（2条）：R-01 朴素语言、R-02 术语一致
- 无障碍（2条）：A11Y-01 POUR四原则、A11Y-02 通用设计7原则
- 治理（4条）：G-01 最小惊讶、G-02 可解释性、G-03 可追溯、G-04 最小授权
- 流程模式（3条）：BFM-01 默认非步骤化、BFM-02 步骤条门禁、BFM-03 单页长表单+锚点
- 视觉（3条）：V-01 视觉层级、V-02 接近性、V-03 相似性
- 认知（7条）：C-01~C-07（Hick/工作记忆/认知负荷/渐进披露/默认效应/损失厌恶/峰终定律）
- 质量（2条）：Q-01 有效性效率满意度、Q-02 UX蜂巢

## 4. 可直接使用的稳定结论

- 本域按主题文件维护，不维护 task/trigger 路由索引；新增主题时直接新增 `<topic>.md`
- 使用流程：先通过 Wiki 命中机制定位相关 guideline 主题，再回查 raw 正文真源
- 输出体验要求、风险点、自检问句时，只引用当前任务真正相关的原则，不做原则堆叠
- 放通用设计原则，不放业务规则；放原则级转译，不放视觉规范与组件方案；放设计推导依据，不放实现细节

## 场景路由

本段只用于帮助 AI 从 facts.md 与 business_blueprint.md 中识别体验场景，并选择应优先读取的 guideline summary。summary 只负责路由；命中后必须继续读取其 source_refs 指向的 raw，最终判断仍以 facts 与 business_blueprint 为准。

- 信息组织、页面结构、模块分组：优先读信息架构、视觉、认知。
- 操作流程、步骤拆分、任务闭环：优先读流程模式、可用性、认知。
- 报错、阻断、校验、权限不足：优先读反馈与报错、可用性、可读性。
- 审批、延迟生效、后台任务、状态流转：优先读可用性、治理、反馈与报错。
- 批量操作、高风险配置、权限变更：优先读可用性、治理、认知。
- 表格操作列、列表状态、空状态、结果明细：优先读信息架构、可用性、视觉、反馈与报错。
- 弹窗、抽屉、详情承载、二次确认：优先读信息架构、流程模式、可用性、认知。
- 术语、文案、用户可理解性：优先读可读性、可用性、治理。
- 复杂配置、高认知负担、渐进披露：优先读认知、信息架构、流程模式、视觉。
- 视觉层级、信息密度、可扫读：优先读视觉、信息架构、可读性。
- 无障碍、可感知、可操作：优先读无障碍、可用性、可读性。
- 体验质量评估、有效性、效率、满意度：优先读质量、可用性、认知。

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

- knowledge/wiki/summaries/设计准则/信息架构.md
- knowledge/wiki/summaries/设计准则/可用性.md
- knowledge/wiki/summaries/设计准则/可读性.md
- knowledge/wiki/summaries/设计准则/无障碍.md
- knowledge/wiki/summaries/设计准则/治理.md

> summary_path: knowledge/wiki/summaries/设计准则/README.md
