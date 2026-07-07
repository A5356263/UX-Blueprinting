# 自动化评测系统

本 skill 支持双层自动化系统：

1. 证据抽取层：读取 DOM、Accessibility Tree、runtime 状态、computed style 与可选截图，生成包含 Page/Flow/Interaction DSL、UCATS 清晰度评分、问题与建议的规范 JSON。
2. 确定性层：验证 JSON 结构、重算清晰度分；只有五维独立证据齐全时才重算完整 UCATS 总分。

## 流水线

```text
browser mode:
  浏览器 DOM/Accessibility/runtime/computed style + 提示词上下文
  -> 判断是完整业务界面还是加载/鉴权壳层
  -> 自动生成 Page/Flow/Interaction DSL
  -> UCATS 清晰度评分
  -> 规范 JSON 报告
  -> scripts/ucats_report.py 校验
  -> pass/review/fail 门禁

screenshot mode:
  截图 + 提示词上下文
  -> 自动生成 Page/Flow/Interaction DSL
  -> UCATS 清晰度评分
  -> 规范 JSON 报告
  -> scripts/ucats_report.py 校验
  -> pass/review/fail 门禁

mixed mode:
  浏览器证据 + 截图 + 提示词上下文
  -> 证据合并与冲突标记
  -> Page/Flow/Interaction DSL
  -> UCATS 清晰度评分
  -> 规范 JSON 报告
  -> scripts/ucats_report.py 校验
  -> pass/review/fail 门禁

behavior data evidence branch:
  前端行为数据/产品看板/埋点日志 + 任务上下文
  -> 校验指标口径、样本、基准线和异常点
  -> 将数据异常关联到页面/任务/步骤/组件事件
  -> 若有关联到界面证据，则作为 browser/screenshot/mixed 报告的补充证据
  -> 为非清晰度 UCATS 维度提供独立产品/行为证据
  -> 若无法关联到界面证据，则只输出产品级诊断和后续定位方向
```

## 评估对象分流

自动化运行前必须先判断评估对象，避免把证据类型误当成业务页面。

- 完整业务界面：截图或渲染 DOM 中已经包含导航、内容、控件、反馈和任务入口。可以做完整信息呈现与操作体验走查。
- 流程/交互状态：多截图、多 DOM 状态、runtime 事件或用户提供顺序。需要生成 Flow DSL 与 Interaction DSL。
- 加载/鉴权壳层：只有 `app-root`、loading、登录跳转脚本、资源引用或 `view-source` 源码。只能评估加载说明、鉴权反馈、失败兜底、无脚本提示和可访问性，不能评估真实业务首页。
- 行为数据异常：只有完成率、点击率、耗时、重复点击、无效点击、PV/UV 等数据。可以证明体验异常；若无界面证据，只能给定位方向，不能生成具体界面改法，也不进入本 skill 的规范界面 JSON 校验。
- 混合证据：同时有行为数据和界面证据。优先形成“数据异常 -> 界面原因 -> 优化建议”的闭环。

## 批量评估

批量评估时，每个 case 生成一个规范 JSON 报告。建议命名：

- `reports/<case_id>.json`
- `snapshots/<case_id>/<order>-dom.json`
- `snapshots/<case_id>/<order>-a11y.json`
- `screenshots/<case_id>/<order>-<state>.png`

每份报告应包含：

- 稳定的 `input.dom_snapshots[].ref`、`input.accessibility_snapshots[].ref`、`input.runtime_events[].ref` 或 `input.screenshots[].ref`。
- 若使用行为数据，稳定的 `input.behavior_metrics[].ref`，并说明指标口径、样本、时间范围、基准线和关联页面/任务/组件事件。
- `input.scenario`、`input.task_goal` 与 `input.task_context`。
- `dsl.pages[].generation`，记录 DSL 是由 browser+prompt、screenshot+prompt 还是 mixed+prompt 自动生成。
- 每个问题的 DSL 证据路径。
- `ucats.walkthrough.*.elements[]` 元素级走查明细；脚本会重算元素分、一级维度分和走查总分。
- 所有评分、问题和扣分项中的 `evidence` 路径必须能在报告 JSON 中实际定位到；除具体行为指标 `input.behavior_metrics[n]` 外，证据路径应来自可观察 DSL，不能指向任务上下文、generation 或 source 元数据。
- UCATS `clarity` 分数与置信度；非清晰度维度只有在有独立产品/行为证据时才填写。
- 映射到问题 id 的建议；每个 issue 必须至少被一个 recommendation 覆盖。
- `input.*[].ref`、`dsl.pages[].page_id`、`issues[].id`、`recommendations[].id` 必须唯一；页面 `source.*_ref` 必须匹配已声明输入来源类型。
- 非 0 `adjustment` 必须带 `adjustment_reason` 和 `adjustment_evidence`，防止无证据改分。

## CLI

验证报告：

```bash
python3 scripts/ucats_report.py validate reports/case_001.json
```

打印清晰度分数、可选综合分与门禁结果：

```bash
python3 scripts/ucats_report.py score reports/case_001.json
```

写入归一化报告，自动重算 `clarity_score`、可选 `overall_score`、`gate` 与校验警告：

```bash
python3 scripts/ucats_report.py normalize reports/case_001.json --output reports/case_001.normalized.json
```

## CI 门禁

使用失败退出码：

- `0`：报告有效。
- `1`：结构或质量门禁失败。
- `2`：文件或 JSON 解析错误。

建议发布门禁：

- `fail`：阻止发布。
- `review`：要求设计复核。
- `pass`：允许发布。

## Benchmark

改版前后设计对比时：

- 分别独立评估改版前与改版后的 DOM/Accessibility/runtime/截图证据。
- 比较清晰度分数、问题数量变化与严重问题变化。
- 当清晰度分数至少提升 5 分，或一个 `High`/`Critical` 问题被解决时，才认为变化有明确价值。
- 如果置信度从 `High` 降为 `Low`，不要声称体验改进。

## 人工复核触发条件

在以下情况转交人工评估：

- 截图模糊、被裁切或不可读。
- browser mode 缺少关键 DOM 或 Accessibility 快照。
- 任务上下文未知，且清晰度结论依赖任务目标。
- 涉及法律、金融、医疗、隐私或安全影响。
- 建议需要改变业务规则，而不仅是界面设计。
