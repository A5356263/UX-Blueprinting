# 体验蓝图构建合同

## 目标

基于 `facts.md`、business 产物与 UXB 已确认判断，生成可评审的 `experience_blueprint.md`。

## 阶段定位

experience 阶段负责：

- 按角色组织交互流程
- 写清用户动作、系统反馈、页面文案和下一步
- 展开异常与阻断流程
- 承接业务边界、风险与反馈要求

experience 阶段不负责：

- 高保真视觉设计
- 前端实现方案
- 接口设计
- 重做业务判断

## 输入

- `projects/<project-id>/workspace/facts.md`
- `projects/<project-id>/workspace/business_blueprint.md`
- `projects/<project-id>/runtime/uxb_route_decision.json`
- 已装配进 `runtime/context_bundle/` 的 guideline / business / complexity refs

## 设计参考使用规则

- 只能使用 UXB 已明确选中的 `guideline_refs`
- 不根据关键词自动命中设计指南
- 不根据 guideline summary 自动展开 raw
- 不自动补充额外 guideline
- guideline 只吸收原则，不在正文暴露内部路径或编号

## 与 UXB 判断的关系

- experience 可以参考 `judgment.experience_output`、`judgment.reason`
- 可以参考 `complexity_judgment.experience_pressure`、`uncertainties`
- 这些信息只能转写成业务或体验语言，不得原样暴露执行字段

## 关键判断摘要

`## 0. 本次关键设计判断` 应前置表达本次体验方案的核心处理方式。

允许表达：

- 当前重点不是多做页面，而是先把异常反馈说清楚
- 本次需要重点承接多角色协作和状态变化

禁止表达：

- `route 判断为 full`
- `标准路线下优先写主流程`
- `matched_signals 显示存在 guardrail`

## 结构要求

`experience_blueprint.md` 必须包含：

- `## 0. 本次关键设计判断`
- `## 1. 交互流程总览`
- `## 2. 主交互流程`
- `## 3. 次交互流程`
- `## 4. 异常与阻断流程`
- `## 5. 页面 / 弹窗 / 抽屉设计`
- `## 6. 状态与反馈文案`
- `## 7. 待确认问题`
- `## 附录：设计指南消费说明`

## 附录：设计指南消费说明

该附录只在实际装配并消费了 guideline refs 时填写，可记录：

- 本次重点承接的体验问题
- 实际使用的 guideline 主题
- 这些原则如何转成页面、流程、反馈方案

不得记录：

- 自动命中过程
- `summary -> raw` 链式消费过程
- guideline 原文大段摘录

## 合格标准

- 读完后能清楚知道谁在什么场景下做什么、系统怎么回应
- 每个关键节点都写清用户动作、系统反馈、文案和下一步
- 异常流程说明触发条件、反馈文案和补救路径
- 重点流程和重点异常有明显更高的展开深度
- 正文不暴露内部执行术语

## 失败条件

- 缺少主流程或异常流程
- 把设计参考写成自动路由、自动升级或内部判断说明
- 页面文案是元指令而不是用户可见文本
- 依赖未装配知识或自行补 guideline
