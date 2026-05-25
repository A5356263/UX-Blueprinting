# 业务蓝图构建合同

## 目标

基于 `facts.md`、已装配知识与 UXB 已确认判断，输出可评审的 `business_blueprint.md`。

## 阶段定位

business 阶段负责：

- 判断需求是否成立、是否值得做
- 推导推荐业务方案
- 明确必须守住的规则边界
- 输出 experience 阶段必须承接的业务要求

business 阶段不负责：

- 页面结构设计
- 交互细节
- 视觉方案
- 前后端实现方案

## 输入

- `projects/<project-id>/workspace/facts.md`
- `projects/<project-id>/runtime/uxb_route_decision.json`
- 已装配进 `runtime/context_bundle/` 的业务知识或复杂度知识

## 写作原则

- 用业务方能直接理解的话写判断，不写内部执行术语
- 判断必须能回到 facts 或已装配知识
- 信息不足时明确写入“待确认问题”
- 不把 UXB 判断文件原样抄进正文
- 不暴露 `route`、`fast`、`standard`、`full` 等内部词

## 关键判断摘要

正文前置的 `## 0. 本次关键设计判断` 可以吸收 UXB 的判断结果，但必须转写成业务语言。

允许表达：

- 这类需求不能只按局部页面修改处理
- 本次需要先讲清业务规则和边界
- 当前仅适合做轻量业务判断

禁止表达：

- `route = full`
- `当前是 standard 路线`
- `route 判断已升级`

## 与 UXB 判断的关系

- UXB 是本次执行判断源
- business 阶段可以参考 `judgment.demand_type`、`judgment.business_depth`、`judgment.reason`
- 如发现现有判断不足以支撑正文，应暴露问题并要求重新判断，不得在正文里自行升级执行口径

## 结构要求

`business_blueprint.md` 必须包含：

- `## 0. 本次关键设计判断`
- `## 1. 一句话结论`
- `## 2. 需求是否成立`
- `## 3. 值不值得做`
- `## 4. 应该做成什么能力形态`
- `## 5. 推荐业务方案`
- `## 6. 必须守住的规则和边界`
- `## 7. 主要风险与保护策略`
- `## 8. 方案承接要求`
- `## 9. 待确认问题`
- `## 附录：事实、知识与判断追踪`

## 合格标准

- 能回答需求是否成立、值不值得做、建议做成什么
- 推荐方案具体、可执行，不是空泛分类
- 规则边界与风险明确
- 承接要求足够具体，experience 可直接展开
- 摘要部分不泄露内部执行术语
- 正文不依赖尚未生成的 `experience_blueprint.md`

## 失败条件

- 大量复述 facts 原文而没有形成判断
- 用 route 术语替代业务结论
- 依赖未装配的知识
- 发现判断不足时直接在文中自行升级，而不是明确要求重新判断

## 同步约束

本合同更新后需与以下文件保持一致：

- `templates/business_blueprint.template.md`
- `specs/10_experience_blueprint_contract.md`
