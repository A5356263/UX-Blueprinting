---
name: product-analysis
description: >
  产品分析 Skill。对需求方向不成立或问题未定义清楚的场景，做问题重构和轻量方案发散，输出 2-3 条可行方向。
  触发关键词：产品分析、问题重构、重新定义问题、需求方向不对、方向不成立、重述问题、打开方案空间、方案发散。
  排除：正式需求定案（用 uxb）、体验诊断（用 uxb）、知识问答（用 knowledge-wiki）。
---

# Product Analysis

这个 skill 用于承接一种特定情况：

```text
已有方向、方案、PRD 或阶段性 UXB 判断
但当前方向不足以继续正式定案
需要先重定义问题，再打开 2-3 条替代方向
```

它不是 UXB 的默认主流程，也不是无条件脑暴工具，更不是白纸场景入口。

## 适用场景

适用于：

- 需求方向明显不成立
- 用户给的是方案，但还没证明真实问题
- 当前更需要重述问题，而不是继续蓝图分析
- 需要打开 2-3 条可行方案方向，再决定是否回到 UXB
- 当前正在 `uxb` 中，且已经判断现有方向需要纠偏

不适用于：

- 问题尚未成形、仍是白纸探索
- 已经可以直接进入 UXB 正式蓝图
- 单纯体验诊断
- 单纯知识问答
- 已经确认只需要做 facts / business / experience 产物

## 目标

先把问题重新定义清楚，再决定是否发散方案。

优先回答：

1. 真问题是什么
2. 当前方案为什么不够成立
3. 还有哪些替代方向值得看
4. 下一步是继续产品分析，还是回到 UXB

## 来源模式

`product-analysis` 必须支持两种正式来源模式：

- `direct-input`
  - 用户直接带 PRD、方案、文档或口述问题进入
  - 当前不在 `uxb` 执行中
- `uxb-inflight`
  - 当前任务正在 `uxb` 中
  - 因方向不成立、用户要求重想或 UXB 判断需开方案空间而切入

## 上游读取协议

### 模式 A：`direct-input`

读取顺序：

1. 当前对话中的问题背景、已有方向、失败点、约束
2. 用户明确提供的文件路径、PRD、文档
3. 如用户明确要求“基于已有产物继续”，再读取对应产物
4. 不默认扫描工作区历史产物

### 模式 B：`uxb-inflight`

读取顺序：

1. 当前对话中的问题背景、当前争议点、用户新补充
2. 当前 `uxb` 已形成的阶段性结论
3. `spark-output/context/uxb.json`
4. `spark-output/uxb_output.md`
5. 如有必要，再读取原始 PRD / 文档

在该模式下，`uxb` 已确认的事实和约束属于有效输入，不重新丢弃。

## 进入门槛

`product-analysis` 不得因为“感觉一般”直接触发。正式执行前必须先判断，满足任一条件才允许进入：

1. 用户给的是方案，不是问题
2. 当前方案跳过了关键前提
3. 当前方案解决的是表象，不是真问题
4. 当前方案与业务约束冲突
5. 当前方案即使实现，也不足以达成成功标准

## 工作方式

### Step 1：判断是否真的需要产品分析

先用一句话判断：

- 当前更像白纸问题
- 当前更像方向重构问题
- 当前已经可以继续正式定案

只有命中“方向重构问题”时，继续后续步骤。

### Step 2：重定义问题

先回答：

- 谁真的有问题
- 现在怎么解决
- 为什么重要
- 什么算成功
- 当前方案跳过了什么前提
- 当前方案为什么不足以继续

要求：

- 区分已确认事实、推断、判断、缺口
- 不把旧方案直接重写成真问题
- 不提前进入页面或交互方案

### Step 3：给出方向选项

只给 2-3 条方向，不追求大规模创意发散。

每条方向至少说明：

- 解决什么问题
- 核心思路是什么
- 主要风险是什么
- 适用前提是什么

必须明确推荐 1 条方向，不允许只列备选。

### Step 4：建议下一步

只保留两类下一步：

1. 继续产品分析
2. 回到 UXB 做正式定案

其中：

- `继续产品分析` 只在推荐方向仍不稳定、关键前提未补齐时允许
- 默认推荐路径应是 `回到 UXB 做正式定案`

## 输出风格

- 大白话
- 先说判断
- 少术语
- 不默认跑完整 SCAMPER
- 不强制 Top 3 创意筛选

## 输出结构

输出到：

- `spark-output/product_analysis.md`
- `spark-output/context/product-analysis.json`

Markdown 固定结构：

```markdown
# 产品分析：{项目名}

## §0 关键判断
## §1 当前方向为什么不成立
## §2 真问题重定义
## §3 被跳过的关键前提
## §4 替代方向
## §5 推荐方向
## §6 下一步建议
## §7 不做什么
## §8 待确认问题
```

## Context JSON 写入

文档生成后，按下方字段列表写入 `spark-output/context/product-analysis.json`。

写入字段包括：

- `skill`
- `version`
- `generated_at`
- `project_name`
- `source_mode`
- `input_summary`
- `current_direction_failure`
- `reframed_problem`
- `skipped_premises[]`
- `alternative_directions[]`
- `recommended_direction`
- `next_step`
- `gaps[]`

字段规则：

- `source_mode` 只允许 `direct-input` 或 `uxb-inflight`
- `alternative_directions[]` 只允许 2-3 条
- `recommended_direction` 必须非空
- `next_step` 只允许：
  - `continue-product-analysis`
  - `return-to-uxb`

## 交接

当前是否为链路终端，以 `shared-workflow/skill-graph.json` 为准。完成后：

1. 读取 `shared-workflow/next-skill.md` 交接话术模板。
2. 读取 `shared-workflow/skill-graph.json` 中 id 为 `product-analysis` 的 `next_hint`。
3. 根据 `next_hint.preferred` 是否为空，输出标准交接或终端节点交接话术。
4. 如宿主支持文件系统与本地命令执行，写出正式产物后立即刷新一次进度预览，优先执行 `shared-workflow/generate-progress-preview.ps1`。
5. 如刷新失败或宿主不支持，直接跳过，不影响当前 Skill 完成与下游继续。

## 边界

- 可以吸收问题聚焦、5 Why、轻量方案发散
- 不把完整脑暴框架强行跑满
- 不替用户做最终决策
- 不直接生成 UXB 正式产物
- 不作为白纸探索入口
- 不直接进入后续主链或正式蓝图
