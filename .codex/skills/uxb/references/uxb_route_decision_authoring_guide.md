# UXB Route Decision Authoring Guide

## 目的

本文用于指导 UXB 在正式执行前生成：

- `projects/<project-id>/runtime/uxb_route_decision.json`

这个文件是 UXB 的执行判断单和资料选择单。执行中枢只读取它，不替 UXB 做语义判断。

## 生成时机

- 用户已经明确确认正式执行
- 准备调用执行中枢之前

如果这个文件缺失，不得启动主链路。

## 先记住一条原则

这个文件不是业务蓝图，也不是体验方案正文。

这个文件只负责回答：

1. 当前是否允许进入主链路
2. 当前业务输出深度是什么
3. 后续正式生成真正需要读哪些资料
4. 本次必须产出哪些文件
5. 是否存在执行级注意事项

## 语义边界

判断单不承载：

- 体验压力点
- 业务规则细节
- 页面设计策略
- 5 Why 过程
- 风险完整清单
- GAP 完整清单

这些内容应进入 `source/background.md`，再由 `facts.md` 结构化消费。

## 判断阶段做什么

判断阶段只做：

1. 判断是否允许进入主链路
2. 判断当前业务输出深度
3. 选择后续正式生成真正要读的资料
4. 写明选择理由
5. 写明执行级注意事项
6. 判断需要的正式输出

判断阶段不做：

1. 不写完整业务蓝图
2. 不写完整体验方案
3. 不通读整个 `knowledge/`
4. 不为了保险全量选资料
5. 不把知识原文复制进判断单

## 读取顺序

### 必读

1. `references/complexity/00_core_complexity_judgment.md`
2. `references/complexity/01_domain_router.md`
3. `references/knowledge_usage_guide.md`

### 按需读取

- 命中的领域卡片
- 业务 summary 或 README
- 设计指南 summary
- 必要 raw

重点是“读哪些资料来支撑判断单”，不是完整讲解知识体系本身。

## 复杂度判断

按这个顺序判断：

1. 这次改动到底改了什么
2. 是否改动底层业务骨架
3. 更适合落到哪类正式输出

判断时优先看：

- 对象关系
- 业务规则
- 状态变化
- 生效方式
- 数据口径
- 外部回写

不要只靠关键词或领域名自动下结论。

## 不确定项

先在内部分两类：

- 阻断型不确定项：不补清就会让 facts、business 或 experience 明显失真
- 非阻断型不确定项：不影响当前正式执行，但会影响后续细化质量

写法要求：

- `judgment.reason` 里顺手交代当前是否存在阻断型问题
- 如存在阻断型不确定项，优先追问或把 `can_execute_mainline` 设为 `false`
- 不要把完整 GAP 清单写进判断单

## knowledge_selection 写法

`knowledge_selection` 只保留两个正式字段：

```json
{
  "files": [],
  "reasoning": ""
}
```

填写要求：

1. `files` 只列后续正式产物真正需要消费的知识文件，保持最小集合
2. `reasoning` 只说明为什么选这些知识，不写业务方案
3. 不为了“更完整”把整域 summary 或 raw 全量塞进去
4. raw 可以直接进入 `files`，前提是你能说明它为什么必要

## 字段写法

- `business_depth`：写复杂度驱动后的业务输出深度，不写分析过程
- `knowledge_selection.files`：只列后续正式产物真正需要消费的知识文件
- `knowledge_selection.reasoning`：只说明选这些知识的原因，不写业务方案
- `execution.required_outputs`：写本次必须产出的文件
- `execution.notes`：只写执行级约束，比如“某项能力作为 GAP 标注”，不写体验方案
- `experience_output`：如当前 schema 仍存在，按允许值填写，不扩展语义
- `experience_pressure`：如当前 schema 仍存在，保持 `[]`，不写语义压力点

## required_outputs 判断

先想“当前事实能支撑到什么深度”，不要先想“我想跑哪条路径”。

一般判断：

- 只需先收敛边界和承接重点：`business_note.md`
- 需要较稳定的业务方案，但还不到完整 full blueprint：`business_blueprint_lite.md`
- 已明显涉及对象关系、规则系统、状态机重构或完整业务方案：`business_blueprint.md`

## can_execute_mainline 判断

可执行，不代表信息完整；只代表“当前信息足以支撑这次选定的正式输出”。

通常需要满足：

- 需求目标清楚
- 关键对象关系基本清楚
- 输出深度有依据
- 阻断型不确定项没有继续悬空
- 资料选择有清楚原因

## confirmed_by_user 判断

`confirmed_by_user=true` 不是“用户说了一句继续聊”，而是用户已经明确表达以下含义之一：

- 确认执行
- 开始正式任务
- 创建任务
- 走主链路
- 输出正式产物

## judgment.reason 写法

至少覆盖这三点：

1. 为什么当前输出深度是合适的
2. 为什么当前可以执行，或为什么当前不能执行
3. 如用户表述里自带方案前提，你是否接受了这个前提

## JSON 写入要求

写入路径：

- `projects/<project-id>/runtime/uxb_route_decision.json`

使用模板：

- `assets/uxb_route_decision.template.json`

不要把完整业务方案、完整体验方案或知识原文写进这个文件。

## JSON 稳定写法

先复制模板，再只替换值，不要临时改字段结构。

必须遵守：

1. JSON 键名一律保持模板原样
2. `knowledge_selection` 下的正式字段只允许 `files` 和 `reasoning`
3. 不要把旧字段残留写回去
4. `experience_pressure` 如存在，保持 `[]`
5. 不要把修复说明、报错信息、检查结论写进 JSON
