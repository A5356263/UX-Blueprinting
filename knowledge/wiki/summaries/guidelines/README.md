# knowledge/raw/guidelines

- page_id: PG-SUMMARY-GUIDELINES-GUIDELINES-README
- page_type: summary
- source_path: knowledge/raw/guidelines/README.md
- source_group: guidelines
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-04
- updated_at: 2026-05-04
- source_refs: [knowledge/raw/guidelines/README.md]
- related_summaries:
  - knowledge/wiki/summaries/guidelines/accessibility.md
  - knowledge/wiki/summaries/guidelines/cognition.md
  - knowledge/wiki/summaries/guidelines/flow_mode.md
  - knowledge/wiki/summaries/guidelines/governance.md
  - knowledge/wiki/summaries/guidelines/information_architecture.md

## 1. 知识定位

定义 guidelines 知识目录的组织方式、使用边界和维护原则，帮助判断哪些内容应放入 guidelines 目录、如何正确引用各主题文件以及如何维护该目录。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要了解 guidelines 目录的整体结构与各主题文件分工
- 需要新增或修改 guideline 主题文件
- 需要确认 guidelines 与业务规则、视觉规范的边界
- 需要了解从 Wiki 命中到回查 raw 正文的正确使用流程

## 3. 覆盖内容

本 raw 覆盖：

- 原则：目录边界（放通用设计原则，不放业务规则；放原则级转译，不放视觉规范与组件方案；放设计推导依据，不放实现细节）、维护原则（按主题文件维护，新增主题直接新增 `<topic>.md`，调整后需同步重建 Wiki summaries）
- 规则：使用方式（先通过 Wiki 命中定位主题，再回查 `<topic>.md` 正文真源）
- 章节：当前结构（9 个主题文件：accessibility / cognition / flow_mode / governance / information_architecture / quality / readability / usability / visual）

不涉及：

- 本 raw 未显式覆盖的内容需回查其他相关 raw 或补充来源

## 4. 可直接使用的稳定结论

- 本目录存放跨业务、跨产品复用的通用设计原则，服务体验推导、自检、风险识别与原则引用，不服务业务规则定义
- 放通用设计原则，不放业务规则；放原则级转译，不放视觉规范与组件方案；放设计推导依据，不放实现细节
- 使用流程：先通过 Wiki 命中机制定位相关 guideline 主题，再回查 `<topic>.md` 正文真源，输出时只引用当前任务真正相关的原则
- 新增主题时直接新增 `<topic>.md` 文件，调整主题内容后需同步重建 Wiki summaries 与 index/overview/questions

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

- knowledge/wiki/summaries/guidelines/accessibility.md
- knowledge/wiki/summaries/guidelines/cognition.md
- knowledge/wiki/summaries/guidelines/flow_mode.md
- knowledge/wiki/summaries/guidelines/governance.md
- knowledge/wiki/summaries/guidelines/information_architecture.md

> summary_path: knowledge/wiki/summaries/guidelines/README.md
