# UCATS Skill 使用指南

本文件是执行入口的短指南。详细评分标准保留在 `ASSESSMENT_CRITERIA.md`、`UCATS_GUIDE.md`、`RULES.md`、`DOM_CHECK_METRICS.md` 和 `SCORING_TEMPLATES.md`。

## 什么时候用

- 评估单个页面、流程、表单、看板、文章页、设置页、弹窗或错误状态。
- 对比改版前后界面体验。
- 需要输出 UCATS 清晰度分、问题、建议和可复现 JSON。
- 需要把 DOM/A11Y/runtime/截图证据转成 Page/Flow/Interaction DSL。

## 最短执行流程

1. **确认输入模式**：`browser`、`screenshot`、`mixed`。行为数据只能作为补充。
2. **判定评估对象**：完整界面、流程状态、加载/鉴权壳层、源码快照或行为数据异常。
3. **生成 DSL**：只记录证据可证明的区域、组件、表单、导航、反馈、交互状态和 uncertain。
4. **判定涉及性**：11 个检查元素先判断 `applicable`、`not_applicable` 或 `evidence_insufficient`。
5. **记录问题与扣分**：每个 issue 必须有 severity、evidence、source_refs，并被 recommendation 覆盖；扣分按问题单元个数和档位计算。
6. **计算分数**：走查分按信息呈现/操作体验计算，并只写入 UCATS `clarity`。
7. **输出报告**：默认先展示 UCATS 清晰度得分；自动化场景输出 JSON 并运行校验。

## 报告默认顺序

```text
UCATS 清晰度得分
一句话结论
主要问题
怎么改
评分推导与不确定项
```

不要把完整 DSL 放在人类报告开头。DSL 是证据底稿，只在问题和评分里短引用证据路径。

## 评分公式速查

```text
单题扣分 = 1 / 2^(档位 - 1)
扣分 = 问题单元个数 * 单题扣分
元素原始分 = 100 - sum(deductions.points) + adjustment
元素分 = clamp(元素原始分, 0, 100)
一级维度分 = clamp(sum(元素分 * 元素权重) + adjustment, 0, 100)
走查总分 = 信息呈现分 * 0.35 + 操作体验分 * 0.65
UCATS clarity = 走查总分
完整 UCATS 总分 = 五维都有独立证据时，usability*0.20 + clarity*0.20 + task_completion*0.25 + acceptance*0.15 + stability*0.20
```

注意：

- JSON 中 `deductions[].points` 使用正数，例如人工说“扣 10 分”，JSON 写 `"points": 10`。
- 推荐同时填写 `problem_count`、`scale_level`、`points_per_problem`；脚本会校验 `points = problem_count * points_per_problem`。
- 使用表格法扣分时必须填写 `criterion_id`、`unit_scope`、`state_scope`、`expected`、`actual`、`evidence_test`，用于证明问题单元颗粒度和客观失败条件。
- `problem_count` 是标准化问题单元数量，不等于 issue 条数；大问题通过 `High/Critical` gate 和跨元素问题单元体现。
- 原始分小于 0 时显示为 0，不代表报告无效；它代表该元素已触发评分下限，需要复核问题计数和档位。
- 只有一个一级维度涉及时，该维度权重为 `1.0`，另一个为 `0`。
- 只有界面证据时，不输出完整 UCATS 总分；非清晰度维度不能引用界面检查项评分。
- 非 0 `adjustment` 必须有 `adjustment_reason` 和 `adjustment_evidence`。

## 可行性和漏洞防护

- **证据不足**：标记 `evidence_insufficient` 或写入 `dsl.uncertain[]`，不能当作不涉及。
- **行为数据误用**：行为数据能证明异常，不能单独证明具体按钮、文案或布局原因。
- **视觉过度推断**：没有截图、bbox、computed style 时，不评价遮挡、颜色、对比度和美观度。
- **重复扣分**：同一根因在同一检查元素内只扣一次；跨元素引用时必须说明不同影响路径。
- **大小问题同分**：单题扣分相同，但 `High` 至少触发 review，`Critical` 触发 fail。
- **路径不可校验**：证据路径必须指向 `dsl.pages[]`、`dsl.flow`、`dsl.interactions[]`、`dsl.uncertain[]` 或具体 `input.behavior_metrics[]`。
- **评分漂移**：自动化 JSON 以 `scripts/ucats_report.py` 的重算结果为准。

## 自动化命令

```bash
python3 scripts/ucats_report.py validate examples/sample_report.json
python3 scripts/ucats_report.py score examples/sample_report.json
python3 scripts/ucats_report.py normalize examples/sample_report.json --output /tmp/sample_report.normalized.json
```

## 详细资料选择

- 想查 DSL 字段：读 `DSL_SPEC.md`。
- 想查检查元素和扣分规则：读 `UCATS_GUIDE.md` 和 `ASSESSMENT_CRITERIA.md`。
- 想做 DOM 半自动检查：读 `DOM_CHECK_METRICS.md`。
- 想看评分案例：读 `SCORING_TEMPLATES.md`。
- 想输出 JSON：读 `OUTPUT_TEMPLATES.md`、`ucats_report.schema.json`，再跑 `ucats_report.py`。
