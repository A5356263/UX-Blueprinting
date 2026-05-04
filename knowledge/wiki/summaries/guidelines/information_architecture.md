# 信息架构与可发现性原则

- page_id: PG-SUMMARY-GUIDELINES-GUIDELINES-INFORMATION_ARCHITECTURE
- page_type: summary
- source_path: knowledge/raw/guidelines/information_architecture.md
- source_group: guidelines
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-04
- updated_at: 2026-05-04
- source_refs: [knowledge/raw/guidelines/information_architecture.md]
- related_summaries:
  - knowledge/wiki/summaries/guidelines/README.md
  - knowledge/wiki/summaries/guidelines/accessibility.md
  - knowledge/wiki/summaries/guidelines/cognition.md
  - knowledge/wiki/summaries/guidelines/flow_mode.md
  - knowledge/wiki/summaries/guidelines/governance.md

## 1. 知识定位

提供信息架构与可发现性的设计原则，帮助判断导航命名是否可预测、信息分组是否服务任务顺序、同一概念是否存在多套定义导致理解漂移。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要评估导航命名、列表摘要、搜索结果、配置入口的可预测性
- 需要判断长表单、规则说明、配置页的信息分组是否按任务语义而非数据结构
- 需要检查跨模块、多端、多人协作场景下同一概念的定义是否一致
- 需要识别"入口名含糊""字段散落""各模块自行解释"等信息架构反模式

## 3. 覆盖内容

本 raw 覆盖：

- 原则：IA-01 信息气味（Information Scent）、IA-02 分块（Chunking）、IA-03 单一语义源（Single Source of Meaning）

不涉及：

- 本 raw 未显式覆盖的内容需回查其他相关 raw 或补充来源

## 4. 可直接使用的稳定结论

- 入口命名必须可预测，用户能在点击前判断内容是否匹配预期；线索太多会噪音，优先关键线索
- 信息分组按任务与语义而非数据结构，同组强相关、组间边界清晰、标题表达组意图
- 同一概念的定义与解释应一致可复用，通过术语表与规则表引用，避免各模块自行解释产生漂移

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

> summary_path: knowledge/wiki/summaries/guidelines/information_architecture.md
