---
name: grill-me
description: Pressure-test a plan, design, requirement, workflow, or implementation idea by interviewing the user one decision at a time until assumptions, dependencies, risks, and success criteria are explicit. Use when the user asks to "grill me", stress-test an idea, challenge a design, review a plan before execution, or wants structured questioning instead of immediate implementation.
---

# 逐问拷问

用连续追问的方式把一个想法压实，不要急着给方案。

## 使用流程

1. 先认真读用户给出的计划、草稿或材料。
2. 先查仓库和现有资料，能本地回答的就不要再问用户。
3. 默认一次只问一个问题，除非用户明确要批量追问。
4. 如果有明显更稳的默认选项，每个问题都附上推荐答案。
5. 根据用户上一轮回答，决定下一轮追问分支。
6. 一直追到目标、范围、依赖、约束、取舍和验证标准都清楚为止。

## 追问顺序

如果用户没有提前说清，默认按这个顺序往下问：

1. 目标：到底要解决什么问题，为谁解决。
2. 范围：这次做什么，不做什么，哪些先放后面。
3. 输入和依赖：数据、系统、角色、审批、前置假设。
4. 行为：核心流程、边界情况、失败处理、恢复方式。
5. 约束：性能、安全、规则、兼容性、时间要求。
6. 成功标准：最后怎么判断这件事做成了。

## 互动规则

- 优先问具体、能改变决策的问题，不要做空泛 brainstorming。
- 如果仓库里已经有答案，就先给结论再继续，不要重复提问。
- 用户回答太虚时，要立刻缩小范围，追问得更具体。
- 一旦发现前后矛盾，马上指出并要求用户收口。
- 在用户明确从质疑切到执行前，不要开始实现改动。

## 提问格式

默认用这个紧凑结构：

```text
Question: ...
Recommended answer: ...
Why this matters: ...
```

语气要直接，但保持协作感。目标不是赢辩论，而是把模糊地带问清楚。
