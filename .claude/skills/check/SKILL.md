---
name: check
description: 设计走查 Skill。读取需求定案、体验策略和可选的异常态产出，按检查清单输出结构化发现列表，用于独立走查设计完整性和一致性。
---

# Check

这个 skill 负责在体验蓝图完成后，做一轮独立的设计走查。

它不是重新生成方案，而是用固定检查清单和外部基线，找出遗漏、冲突、不一致和需要优先修复的问题。

## Step 0 · 运行入口

### Step 0.1 · 本 Skill 产物状态

执行本 Skill 前，只检查本 Skill 对应正式产物是否存在。

正式产物：
- `spark-output/check_output.md`
- `spark-output/context/check.json`

只允许检查文件是否存在；禁止读取产物正文、禁止解析 JSON 内容、禁止根据已有产物改变当前任务类型。

若任一正式产物存在，先输出以下状态提示，然后继续执行本 Skill 的入口规则：

```text
检测到本 Skill 已有正式产物（已产出）。
```

该提示只表示状态，不代表采取任何处理动作。

禁止：
- 读取产物正文
- 解析 JSON 内容
- 根据已有产物改变当前任务类型
- 根据已有产物执行下游
- 根据已有产物询问处理方式
- 根据已有产物推断用户意图

### Step 0.2 · 上游读取与模式判断

启动后按以下顺序读取：

1. 按当前 `SKILL.md` 的规则确认本 Skill 自身输入边界
2. 读取 `spark-output/context/uxb.json`
3. 读取 `spark-output/uxb_output.md`
4. 读取 `spark-output/context/experience-blueprint.json`
5. 读取 `spark-output/experience_blueprint.md`
6. 如存在，再读取 `spark-output/context/edge.json`
7. 如有需要，补读 `knowledge-wiki` 中相关设计准则

这是链路消费型 skill，默认承接 `spark-output/` 中的上游产物属于正式工作流。

降级规则：

- 只要有 `experience-blueprint` 产出，就可以执行
- `edge.json` 缺失时，不阻断执行，只是不做基于异常态矩阵的对照加严
- `uxb` 缺失时，跳过 `uxb-consistency` 的强对照，并在结果里说明
- 如果只有用户指定的文件或文本，也可以按独立模式执行

### Step 0.3 · 独立模式确认

没有完整上游时，先确认：

1. 走查目标：单页 / 多页 / 整个流程
2. 材料类型：文档 / 页面结构 / HTML / 文字描述
3. 是否有特别关注点

独立模式也要按同一套类别输出 findings，不因为输入简化而省略严重度和建议。

## 角色定义

Check 负责：

- 按固定类别逐项走查
- 结合 UXB、体验蓝图和可选的 Edge 结果做一致性核对
- 输出分严重度的 findings 清单
- 给出修复优先级建议

Check 不负责：

- 重做需求定案
- 重写体验蓝图
- 替代实现验收
- 做主观审美评价

## 检查清单

执行前必须阅读：

- `references/review-checklist.md`

固定覆盖 10 类：

- `flow-continuity`
- `ia`
- `structure-consistency`
- `information-hierarchy`
- `edge-states`
- `copy`
- `responsive`
- `feedback`
- `accessibility`
- `uxb-consistency`

要求：

- 每条 finding 都要有 `severity`
- 每条 finding 都要有出现位置和修复建议
- 没有问题的类别不强行造问题
- 仅蓝图文档时，允许对部分视觉类项目降级检查，但要显式标明降级

## 执行流程

### Step 1：确定走查材料与模式

- 如果上游文件完整，优先走链式模式
- 如果只有蓝图文档，则按“文档走查模式”执行
- 如果用户给的是局部内容，则按目标范围走查，不擅自扩成全项目

### Step 2：建立外部基线

固定优先用三个外部基线：

- UXB `§7` 的体验蓝图承接要求
- 体验蓝图正文里的流程、页面、状态与待确认项
- Edge 的覆盖矩阵（如果存在）

如果知识库中命中了相关设计准则，可以作为补充基线，但不能替代前三项。

### Step 3：按 10 类输出 findings

对 `references/review-checklist.md` 中的每个类别逐项核对，输出：

- `blocker`
- `major`
- `minor`

每条 finding 都要写明：

- 问题描述
- 修复建议
- 出现位置

### Step 4：写入结果

输出到：

- `spark-output/check_output.md`
- `spark-output/context/check.json`

输出规则补充：

- 如果宿主支持文件系统，先检查并创建 `spark-output/` 与 `spark-output/context/`，再写入产物

`check.json` 至少包含：

- `skill`
- `version`
- `generated_at`
- `project_name`
- `target`
- `findings[]`
- `summary`

`summary` 必须根据 `findings` 自动汇总，不允许手写估算。

## 输出要求

Markdown 报告至少包含：

- 走查目标
- 走查依据
- 分严重度的 findings
- 修复优先级建议
- 本次降级项或跳过项

JSON 要求：

- `findings[].category`
- `findings[].severity`
- `findings[].description`
- `findings[].suggestion`
- `findings[].location`
- `summary.blocker`
- `summary.major`
- `summary.minor`
- `summary.pass`

## Context JSON 写入

正式产物生成后，按固定结构写入 `spark-output/context/check.json`。

固定结构：

```json
{
  "skill": "check",
  "version": "1.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/check_report.md",
  "source_refs": [],
  "read_sections": [],
  "target": {
    "artifact": "unknown",
    "scope": "unknown"
  },
  "basis": [
    {
      "source": "unknown",
      "rule_or_section": "unknown"
    }
  ],
  "findings": [
    {
      "id": "unknown",
      "category": "unknown",
      "severity": "unknown",
      "description": "unknown",
      "suggestion": "unknown",
      "location": "unknown",
      "evidence": "unknown"
    }
  ],
  "summary": {
    "total": 0,
    "blocker": 0,
    "major": 0,
    "minor": 0,
    "pass": "unknown"
  },
  "degraded_items": [
    {
      "item": "unknown",
      "reason": "unknown",
      "impact": "unknown"
    }
  ],
  "skipped_items": [
    {
      "item": "unknown",
      "reason": "unknown"
    }
  ]
}
```

硬规则：

- 字段固定，不得新增、删除或改名。
- 只填入本 Skill 正式 Markdown 已产出的信息；缺失信息写 `unknown` 或空数组。
- 不得为了填满 JSON 编造信息。
- `findings[]` 必须保留 `location` 和 `evidence`。
- `basis[]` 必须说明走查依据，不能只写主观判断。
- JSON 不复制 Markdown 全文。
- 写入失败不阻断完成，但应在输出中提示。

## Handoff · 固定下一步

固定输出：

```text
设计走查已完成。当前没有固定下一步推荐。
你可以停在这里。
```

如需刷新进度预览，可使用项目已有预览入口；刷新失败不影响当前 Skill 完成。

## 边界

- 不把 Check 写成“再做一版体验蓝图”
- 不用主观审美词替代结构化 finding
- 不在没有依据时把问题升为 blocker
- 不输出 marker、dashboard 或其他已暂缓执行的 chain 机制
