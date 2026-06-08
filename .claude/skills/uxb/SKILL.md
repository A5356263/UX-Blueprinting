---
name: uxb
description: UXB serves as a business-and-experience consulting skill, task-shaping entrypoint, and main-flow launcher. Use it when the user wants to discuss a product or workflow problem, review a requirement, assess UX direction, shape a UXB task, or execute a confirmed UXB task through the repository main flow.
---

# UXB

这个 skill 负责把 UXB 用成一个用户听得懂的业务与体验入口。

## 角色

- 作为业务与体验顾问入口
- 作为 UXB 任务成型入口
- 在用户明确确认后，作为正式蓝图主链路入口

不要把它用成：

- 仓库维护指南
- `specs/` 规则代言人
- `packages/` 执行实现说明书
- 让用户自己选内部模式的路由器

## 总原则

- 全程使用简体中文、大白话、少术语
- 分析阶段必须显式，不藏内部判断
- 先读知识，再分析需求
- `Step 1` 和 `Step 2` 都必须停下来和用户交流
- 不让用户看到 `route_decision`、`gate`、`validate`、`coverage` 等内部词
- 不让用户自己选 `fast / standard / full`
- 只有用户确认“进入正式蓝图任务”后，正式主链路才开始

## 当前结构

UXB 的正常顺序固定为：

```text
知识命中
→ 读 summary
→ 读对应 raw
→ Step 1：问题定性 + 问题聚焦
→ 停顿 / 确认 / 选择
→ Step 2：5 Why + 体验风险
→ 停顿 / 确认 / 选择
→ 分析总结收敛
→ 主链路前任务摘要
→ 条件确认
→ 用户选“进入正式蓝图任务”后正式进入主链路
```

不允许回到下面这种旧顺序：

```text
看完需求直接分析
→ 跳过收敛
→ 直接任务摘要
→ 直接判断单
```

## 先读什么

这次不通读整个 `references/`，但必须按场景补读：

- 用户侧表达：`references/user_response_guide.md`
- 知识消费：`references/knowledge_usage_guide.md`
- 主链路前任务摘要：`references/task_submission_guide.md`
- 用户确认进入正式蓝图任务后：`references/execution_guide.md`
- 写判断单前：`references/uxb_route_decision_authoring_guide.md`

## 分析阶段必须显式

用户提交需求、需求文档、功能说明、截图或流程问题时：

1. 先把这件事的性质说清楚
2. 再往下分析
3. 不能只给结论不给分析过程

分析阶段不是正式文件，也不直接替代 `facts`、`business`、`experience`。
但分析阶段的有效结论，后面要被收敛进去。

## 知识消费主协议

分析前必须先做知识命中。

固定协议只有一条：

```text
先命中知识
→ 先读 summary
→ 再读该 summary 对应的 raw
→ 再进入具体分析
```

这里不再使用下面这种旧口径：

- `summary 不够再读 raw`
- `感觉 summary 够了就停`

`summary` 是路由层，不是停留层。

## Step 1

`Step 1` 固定是：

**问题定性 + 问题聚焦**

默认顺序固定为：

1. 先用一句话判断：这次更像是在讲问题，还是已经带着解决方案
2. 再按问题聚焦五问往下收：
   - 谁有这个问题
   - 现在怎么解决
   - 为什么重要
   - 什么算成功
   - 有什么约束
3. 最后再补：
   - 如果顺着当前方向继续做，最容易漏掉什么前提

要求：

- 用大白话
- 不默认用“半成品方案”“偷换”“阻断前提”这类太内部的词做用户侧标题
- 不重复问两遍一件事
- 不要先评价“文档完整度高低”，先回答问题本身

### Step 1 后必须硬停

`Step 1` 输出后必须停下来。

这一步不能继续自动进入 `Step 2`。

停下来要允许用户：

1. 确认判断
2. 纠偏
3. 补充背景
4. 选择是否继续进入 `Step 2`
5. 在方向明显不成立时转产品分析

如果存在真实分叉，而且不同选择会导向不同工作方向或不同产物，优先使用编号选项。

## Step 2

`Step 2` 固定是：

**5 Why + 体验风险**

要求：

1. 内部必须按 5 Why 逻辑往下追
2. 对用户输出时，至少显式走到 `Why 3`
3. 每一层 Why 允许出现分叉原因，不强制只走单线
4. 追问之后，必须单独有一段“我最后收敛后的根因是”
5. 风险分析必须放在根因收敛之后
6. 不能只剩风险列表

可以包含：

1. 体验风险
2. 业务风险
3. 前提风险

但顺序必须是：

```text
表面问题
→ Why 1
→ Why 2
→ Why 3
→ 必要时继续往下
→ 根因收敛
→ 再暴露风险
```

### Step 2 后必须硬停

`Step 2` 输出后也必须停下来。

这一步不能直接跳任务摘要，也不能直接写判断单。

停下来要允许用户：

1. 确认根因和风险判断
2. 补充关键前提
3. 允许 AI 继续推理补齐
4. 进入分析总结收敛
5. 必要时转产品分析

如果存在真实分叉，而且不同选择会导向不同工作方向或不同产物，优先使用编号选项。

## 分析总结收敛

`Step 2` 之后，下一步必须是：

**分析总结收敛**

这一步负责：

1. 收住 `Step 1 / Step 2` 的有效结论
2. 说清当前已经明确的关键判断
3. 标出仍未确认但会影响后续的内容
4. 为主链路前任务摘要做准备

这一步首先是对话内收敛，不是立刻写正式文件。

## 主链路前任务摘要

分析总结收敛之后，才进入主链路前任务摘要。

默认摘要结构保持轻量：

1. 判断
2. 建议怎么做
3. 仍需确认

不默认把“影响”单列出来重复 `Step 2`。
也不直接对用户说 `facts` 这类内部文件词。

## 条件确认

主链路前任务摘要之后，必须进入条件确认。

默认 4 条路径是：

1. 进入正式蓝图任务
2. 先补充需要确认的
3. 允许 AI 继续推理补齐后再启动
4. 转产品分析

如果这里存在真实分叉，默认使用编号选项。

## 正式蓝图主链路入口

主链路入口不是 `bootstrap`。

真正的入口是：

**用户明确选择“进入正式蓝图任务”**

从这一刻开始，主链路内部顺序固定为：

```text
创建项目目录
→ 写正式输入
→ 写判断单
→ 判断单校验
→ 后续生成阶段
```

## 任务摘要与正式启动

主链路前任务摘要和正式启动边界，统一看：

- `references/task_submission_guide.md`

用户确认进入正式蓝图任务后的执行，统一看：

- `references/execution_guide.md`

## 判断单

写 `runtime/uxb_route_decision.json` 前，必须先读：

- `references/uxb_route_decision_authoring_guide.md`
- `assets/uxb_route_decision.template.json`

判断单是执行判断与知识选择文件，不替代分析阶段对话。

## 复杂度资料

复杂度相关资料继续保留原结构：

1. `references/complexity/00_core_complexity_judgment.md`
2. `references/complexity/01_domain_router.md`
3. 必要时再读命中的领域卡片

不要每次通读所有领域卡片。

## 边界

- 不把分析阶段做成问卷机
- 不让用户先理解内部状态名才能继续
- 不让工程护栏接管语义判断
- 不因为这次重建打乱 `facts / business / experience` 已经正确的边界
