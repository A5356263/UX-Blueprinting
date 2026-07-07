---
name: ucats-interface-evaluator
description: Evaluate UI clarity with UCATS using browser DOM/Accessibility snapshots, runtime state, screenshots, or mixed evidence. Use when assessing, scoring, auditing, comparing, or optimizing interface clarity; generating Page/Flow/Interaction evidence DSL; diagnosing evidence-backed UI clarity issues; recommending MUI/GenUI patterns; or producing machine-readable reports for automated validation and batch evaluation.
---

# UCATS 界面体验评估 Skill

基于 DOM、Accessibility、runtime、截图或混合证据评估界面清晰度。默认输出面向人阅读的 UCATS 清晰度报告；当用户要求自动化、批量、CI、benchmark、JSON 或可复现评分时，输出可由 `scripts/ucats_report.py` 校验的规范 JSON。

## 核心原则

- 先内部生成 Page/Flow/Interaction DSL，再评分、诊断和建议；默认人类报告不要先展开完整 DSL。
- 只评价证据能证明的内容。提示词上下文只补充用户、任务、能力和预期结果，不能当作界面中已存在的控件、状态或反馈。
- 每个评分、问题和建议都引用可定位证据路径，例如 `dsl.pages[0].components[2]`、`dsl.interactions[0]` 或 `dsl.uncertain[0]`。
- 除具体行为指标可引用 `input.behavior_metrics[n]` 外，不要把 `input.task_context`、`dsl.pages[n].task_context`、`generation`、`source` 或业务描述当作界面证据。
- 对不可见、不可从 DOM/A11Y/runtime/截图证明、截图裁切或推断的信息，写入 `uncertain` 并降低相关置信度。
- 没有行为数据时，不声称真实 PV/UV、点击率、完成率、完成时长、满意度、工单解决率或用户口碑。
- 除非用户明确要求实现，不生成前端代码。

## 输入分流

- `browser`：DOM、Accessibility Tree、可见文本、ARIA/role、表单状态、焦点、路由、computed style 或 runtime 事件。
- `screenshot`：单张或多张截图，可评估可见布局、层级、状态、裁切、遮挡和截图质量。
- `mixed`：browser 证据 + 截图；结构定位优先用 DOM/A11Y/runtime，视觉层级优先用截图。
- 行为数据：产品看板、埋点、日志、反馈工单等只能作为补充证据。若没有 browser/screenshot/mixed 主证据，只输出产品级定位方向，不生成具体界面原因和规范界面 JSON。

先判定评估对象：

- 完整业务界面：可评估信息架构、内容理解、任务路径、反馈、错误恢复和视觉扫读。
- 流程或交互状态：多截图、多 DOM 状态、多路由或 runtime 差异时，生成 Flow/Interaction DSL。
- 加载、鉴权、源码或 SPA 壳层：只评估加载说明、鉴权反馈、无脚本兜底、失败恢复和可访问性占位；不能当作完整业务首页。

## 执行流程

1. 确认输入模式和评估对象；缺失上下文时保守推断并标记 `uncertain`。
2. 读取主证据并生成 DSL。DSL 字段与证据规则见 `kb/DSL_SPEC.md`。
3. 判断信息呈现与操作体验的 11 个检查元素是否涉及当前任务。证据不足不能当作不涉及。
4. 记录 issues、severity、evidence、source_refs 和 recommendations。
5. 按 `kb/UCATS_GUIDE.md` 与 `kb/ASSESSMENT_CRITERIA.md` 计算界面走查分，并只映射到 UCATS `clarity`。
6. 输出报告。默认格式见 `kb/OUTPUT_TEMPLATES.md`：**UCATS 清晰度得分 -> 一句话结论 -> 主要问题 -> 怎么改 -> 评分推导与不确定项**。
7. 若需要 MUI/GenUI，先完成证据和问题诊断，再按 `kb/MUI_PATTERNS.md` 推荐模式。
8. 若需要自动化 JSON，遵循 `schemas/ucats_report.schema.json`，并用 `scripts/ucats_report.py validate|score|normalize` 校验。

## 评分契约

界面走查分：

```text
单题扣分 = 1 / 2^(scale_level - 1)
deductions[].points = problem_count * 单题扣分
元素原始分 = 100 - sum(deductions[].points) + adjustment
元素分 = clamp(元素原始分, 0, 100)
一级维度分 = clamp(sum(元素分 * 元素内部权重) + adjustment, 0, 100)
走查总分 = 信息呈现分 * 0.35 + 操作体验分 * 0.65
```

权重规则：

- 信息呈现和操作体验都涉及：`0.35 / 0.65`。
- 只有一个一级维度涉及：该维度权重为 `1.0`，另一个为 `0` 且 `not_applicable`。
- 涉及元素在所属一级维度内均分权重；不涉及元素权重为 `0`，不扣分。
- 涉及性遵循走查表：涉及填 `1`，不涉及填 `0`；证据不足但任务需要时仍按涉及处理并降低置信度。
- 扣分遵循走查表：问题单元个数乘以档位单题分。`scale_level` 为 1-6 档，1 档每个问题单元扣 1 分，后续每档减半。
- 分数不会小于 0；若原始分小于等于 0，报告显示 0 分并解释触发下限，不视为计算无效。
- 大问题不要只靠多扣分表达；`Critical` 触发 `fail`，`High` 触发 `review`，同一根因影响多个检查目标时可在不同元素下分别计问题单元。

界面走查分只对应 UCATS 清晰度：

```text
ucats.dimensions.clarity.score = ucats.walkthrough.overall_score
```

完整 UCATS 总分只有在五个维度都有独立产品/行为证据时才由脚本按固定权重重算：

```text
overall = usability*0.20 + clarity*0.20 + task_completion*0.25 + acceptance*0.15 + stability*0.20
```

只有界面证据时，不输出完整 `ucats.overall_score`，或写为 `null`。非清晰度维度不得引用界面检查项；若要评分，必须引用 `input.behavior_metrics[n]` 等独立产品/行为证据。扣分值在 JSON 中使用正数 `points`；人工表格里的“-10 分”应写成 `"points": 10`。

门禁由脚本确定：

- `fail`：清晰度分或完整 UCATS 总分 `<65`，或存在 `Critical`，或已评估的 `task_completion.confidence == low`。
- `review`：清晰度分或完整 UCATS 总分 `<80`，或存在 `High`，或任一已评估维度置信度为 `medium`。
- `pass`：不触发以上条件。

## 资源路由

- DSL 结构：`kb/DSL_SPEC.md`
- 评分细则和映射：`kb/UCATS_GUIDE.md`、`kb/ASSESSMENT_CRITERIA.md`
- 强制规则与门禁：`kb/RULES.md`
- 输出格式：`kb/OUTPUT_TEMPLATES.md`
- 自动化架构：`kb/AUTOMATION.md`
- DOM 指标参考：`kb/DOM_CHECK_METRICS.md`
- 评分样例：`kb/SCORING_TEMPLATES.md`、`examples/sample_report.json`
- 实现边界：`kb/CODE_GEN_RULES.md`

## 输出行为

- 默认人类报告必须先展示 UCATS 清晰度得分和 Gate；只有五维证据齐全时才展示完整 UCATS 综合得分。
- `full` 或自动化场景：先给上述人类报告，再给规范 JSON。
- `json` 场景：只输出规范 JSON。
- `comparison` 场景：分别评估改版前后，再比较分数、问题数、严重度和置信度；顺序不确定时标记人工复核。
