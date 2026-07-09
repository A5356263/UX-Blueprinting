---
name: interface-audit
description: >
  界面诊断 Skill。基于截图、DOM、Accessibility、runtime 或混合证据，评估现有页面、流程或状态的界面清晰度，输出证据化问题、影响、改进方向与下一步建议。
  当用户想分析已有页面、比较改版前后界面、做截图诊断、做 DOM/A11Y 走查、做批量界面评分，或希望把界面现状问题整理成可供 UXB、journey-analysis、product-analysis、check 消费的输入时触发。
  保留 UCATS 作为内部评分框架；默认输出人类可读报告，明确问题与后续去向；当用户要求自动化、批量、CI、benchmark、JSON 或可复现评分时，再输出规范 JSON。
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

### Step 6：生成建议下一步

诊断结束后，必须补一段：

`建议下一步`

只允许以下结果：

- `UXB`
- `journey-analysis`
- `product-analysis`
- `check`
- `无需继续流转`

## 建议下一步规则

### 去 `UXB`

满足任一条件时推荐：

- 页面问题已经指向需求约束、规则边界或目标不清
- 需要把现状诊断收敛成正式需求定案
- 用户下一步明显是基于诊断继续梳理需求

### 去 `journey-analysis`

满足任一条件时推荐：

- 问题不是单页，而是跨阶段任务断裂
- 用户目标、阶段、转折和流失点不清
- 需要从界面现状上升到角色旅程层

### 去 `product-analysis`

满足任一条件时推荐：

- 页面问题只是表象
- 根因在目标、规则或策略层
- 当前方案看上去像在优化错误问题

### 去 `check`

满足任一条件时推荐：

- 当前页面实际上是某份蓝图或方案的落地版本
- 用户想做方案后走查，而不是现状诊断
- 核心目标是核对一致性、遗漏和覆盖率

### 无需继续流转

满足以下条件时允许：

- 用户只要界面问题诊断本身
- 没有后续正式分析诉求
- 本轮结论停留在界面修正建议即可

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
