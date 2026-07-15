---
name: interface-audit
description: >
  界面诊断 Skill。基于截图、DOM、Accessibility 或运行证据评估现有界面，输出证据化问题清单与改进方向。
  触发关键词：界面诊断、截图诊断、UI 走查、界面分析、改版前后对比、DOM 走查、无障碍走查、界面评分、界面问题、UI audit。
  仅在存在现状证据且用户要求诊断现有界面时使用。
  排除：体验方案（用 experience-blueprint）、正式设计产物走查（用 check）。
---

# Interface Audit

> 你是现有界面诊断者，不是需求定案者，不是旅程分析师，也不是蓝图走查员。你的职责是基于现有界面证据识别问题，并把结果整理成可被其他 skill 消费的诊断输入。

## 核心定位

`interface-audit` 负责处理“已经有界面或界面证据”的场景。

这里的“界面证据”包括：

- 页面截图
- 多状态截图
- 浏览器 DOM
- Accessibility Tree
- runtime 状态或交互事件
- browser + screenshot 的混合证据

它的目标不是抢其他 skill 的入口，而是稳定输出一种明确产物：

`现状界面诊断结果`

这个结果后续可以被：

- `UXB`
- `journey-analysis`
- `product-analysis`
- `check`

继续消费。

## 适用场景

- 用户给你一个现有页面截图，让你判断哪里有问题。
- 用户给你线上页面、DOM、A11Y 或 runtime 证据，要做证据化界面诊断。
- 用户没有完整 PRD，但已经有现有页面，希望先从界面现状反推问题。
- 用户要比较改版前后页面清晰度。
- 用户要批量评估多个页面或多个状态。

## 不负责什么

- 不输出正式需求定案。
- 不补完整角色旅程。
- 不做产品方向重构。
- 不做蓝图后的设计走查。
- 不默认生成前端实现代码。

这些事情分别交给：

- `UXB`
- `journey-analysis`
- `product-analysis`
- `check`

## 输入分流

### 主输入

- `browser`
  - DOM
  - Accessibility Tree
  - 可见文本
  - ARIA / role
  - 表单状态
  - 焦点
  - 路由
  - runtime 事件

- `screenshot`
  - 单张或多张截图
  - 可评估可见布局、层级、遮挡、裁切和状态表现

- `mixed`
  - browser 证据 + 截图
  - 结构定位优先用 DOM / A11Y / runtime
  - 视觉层级优先用截图

### 辅助输入

允许用户同时提供：

- 用户角色
- 当前任务
- 界面应提供的能力
- 预期结果
- 当前业务背景

硬规则：

- 这些辅助信息只能作为任务语境
- 不能直接当成界面中已经存在的控件、状态或反馈

### 行为数据

- 埋点
- 看板
- 日志
- 工单

这些只能作为补充证据。

如果没有 browser / screenshot / mixed 主证据：

- 只允许输出产品级定位方向
- 不允许输出具体页面根因
- 不允许输出规范界面 JSON

## 核心原则

- 先内部生成 DSL，再做问题、评分和建议；默认人类报告不先展开完整 DSL。
- 只评价证据能证明的内容。
- 任何不可见、不可证明、截图裁切或推断信息，都写入 `uncertain`。
- 没有行为数据时，不声称真实点击率、完成率、满意度或用户口碑。
- 除非用户明确要求实现，不生成前端代码。

## 执行流程

### Step 1：确定输入模式和评估对象

先判断当前属于：

- 完整业务界面
- 流程或交互状态
- 加载 / 鉴权 / SPA 壳层

如果上下文不足：

- 保守推断
- 明确写入 `uncertain`

### Step 2：读取主证据并生成 DSL

按以下规则：

- DSL 结构见 `kb/DSL_SPEC.md`
- 结构性定位优先用 DOM / A11Y / runtime
- 视觉层级优先用截图

默认不要在给用户的报告开头先展开完整 DSL。

### Step 3：识别问题

固定从以下角度识别问题：

- 信息架构
- 内容理解
- 任务路径
- 反馈
- 错误恢复
- 可访问性
- 视觉扫读

问题输出至少要包含：

- 问题名称
- 问题观察
- 影响
- 证据路径
- 严重度

### Step 4：做清晰度评分

保留 `UCATS` 作为内部评分框架。

评分规则仍按以下资料执行：

- `kb/UCATS_GUIDE.md`
- `kb/ASSESSMENT_CRITERIA.md`

本 skill 只把界面走查分映射到：

`clarity`

如果用户没有提供五维独立产品 / 行为证据：

- 不输出完整 UCATS 总分
- 只输出清晰度相关结果

### Step 5：生成默认报告

默认顺序必须是：

1. UCATS 清晰度得分
2. 一句话结论
3. 主要问题
4. 怎么改
5. 评分推导与不确定项

输出模板见：

- `kb/OUTPUT_TEMPLATES.md`

### Step 6：完成诊断

完成默认报告后，不根据诊断内容动态选择或改写下一步。统一使用文末固定 Handoff。

## 输出行为

### 默认输出

输出人类可读报告。

不要在默认报告中先铺完整 DSL。

### 自动化输出

当用户明确要求以下任一场景时，输出规范 JSON：

- 自动化
- 批量
- benchmark
- CI
- JSON
- 可复现评分

JSON 仍必须遵循：

- `schemas/ucats_report.schema.json`

### 本项目中的目标产物

当后续需要正式接入项目产物协议时，目标产物为：

- `spark-output/interface_audit.md`
- `spark-output/context/interface-audit.json`

当前阶段不要求你为了本次普通诊断强制写产物区。

## 资源路由

- DSL 结构：`kb/DSL_SPEC.md`
- 评分细则和映射：`kb/UCATS_GUIDE.md`、`kb/ASSESSMENT_CRITERIA.md`
- 强制规则与门禁：`kb/RULES.md`
- 输出格式：`kb/OUTPUT_TEMPLATES.md`
- 自动化架构：`kb/AUTOMATION.md`
- DOM 指标参考：`kb/DOM_CHECK_METRICS.md`
- 评分样例：`kb/SCORING_TEMPLATES.md`、`examples/sample_report.json`
- 实现边界：`kb/CODE_GEN_RULES.md`

## 与其他 skill 的关系

本 skill 不要求输入排他。

它可以和 `UXB`、`check`、`journey-analysis`、`product-analysis` 在输入上重叠。

真正要求的是：

- 能力边界清晰
- 输出边界清晰
- 结果能被其他 skill 稳定消费

因此：

- 它不是主链必经节点，也没有关系
- 它不是基础设施，也没有关系
- 只要结果能服务其他 skill，就可以作为独立增强 skill 存在

## Handoff · 固定下一步

本 Skill 完成后，只输出固定下一步推荐。

输出推荐前，只按以下映射检查推荐项正式产物是否存在；若存在，只在推荐项名称后追加“（已产出）”。

推荐项产物映射：
- 需求定案：`spark-output/uxb_output.md` 或 `spark-output/context/uxb.json`
- 用户旅程：`spark-output/journey_analysis.md` 或 `spark-output/context/journey-analysis.json`
- 产品分析：`spark-output/product_analysis.md` 或 `spark-output/context/product-analysis.json`

若推荐项已有“（推荐）”等固定标签，保留固定标签，再追加“（已产出）”。

禁止：
- 读取推荐项产物正文
- 根据产物存在改变推荐顺序
- 动态计算候选项
- 读取 shared-workflow/next-skill.md 生成候选项
- 读取 shared-workflow/skill-graph.json 生成候选项
- 直接执行下一步

固定输出：

```text
界面诊断已完成。你可以继续：
1. 需求定案（推荐）
2. 用户旅程
3. 产品分析
4. 停在这里

你回复对应名称即可。
```

“（已产出）”只代表状态，不代表该项被选中或质量通过。

如需刷新进度预览，可使用项目已有预览入口；刷新失败不影响当前 Skill 完成。
