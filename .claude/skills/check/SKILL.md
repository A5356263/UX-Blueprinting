---
name: check
description: >
  设计走查 Skill。读取已完成的需求定案、体验蓝图和可选异常态产物，按检查清单输出设计完整性与一致性的结构化发现列表。
  仅在用户明确要求设计走查、设计完整性检查或检查正式设计产物时使用；不得因检测到设计产物而自动触发。
  排除：基于截图、DOM 或运行界面的现状诊断（用 interface-audit）、生成体验设计方案（用 experience-blueprint）。
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
7. 如存在，再完整读取 `spark-output/edge_output.md`
8. 如需补读设计准则，从 `knowledge-wiki` 的 `knowledge/wiki/index.md` 按实际入口进入原则集，只读与当前检查项直接相关的章节；不得整份默认读取或遍历 raw

这是链路消费型 skill，默认承接 `spark-output/` 中的上游产物属于正式工作流。

上游读取硬门禁：

- UXB `5.0` 与 Experience Blueprint `3.0` JSON 都是对应 Markdown 结论的结构化机器面；其他 JSON 仍按各自现有定位消费。
- Blueprint `3.0` 必须按结构完整核对流程、载体、异常、状态、反馈和待确认边界；不得因无 ID、anchor 或回接字段而降级为旧索引读取。
- 存在对应 Markdown 时仍必须实际完整读取，用于双视图一致性和完整论证审计。
- 即使上游刚在同一会话生成、当前上下文仍保留内容，也不得替代本次文件读取。
- 重点章节只决定二次核对优先级，不是正文白名单。
- UXB JSON 与 Markdown 明显冲突时，停止使用冲突字段，回读 Markdown 核对并将 JSON 记为交接问题；不得自行选择或重判。
- Blueprint JSON 与 Markdown 明显冲突时，将冲突记录为蓝图交接问题；不得自行选择、补全或重判。
- 只有 JSON 而没有对应 Markdown 时，不得宣称完成该上游的一致性检查。
- 必需 Markdown 未读完前，不得进入检查清单或输出正式 findings。

Experience Blueprint 读取边界：

- `3.0` JSON 用于逐项核对蓝图的结构化设计事实是否被下游承接。
- `experience_blueprint.md` 用于核对 JSON 保真、ASCII 和完整叙述；ASCII 不进入 JSON 不属于遗漏。
- JSON 字段为 `unknown` 或 `[]` 时不得从会话补齐；需要判断是否遗漏时回读 Markdown 对应章节。
- 本段只改变输入读取，不改变现有检查维度、问题判定和输出结构。

UXB 读取边界：

- UXB `5.0` JSON 是同一轮定案结论的结构化机器面。检查时消费完整结构，重点核对角色、功能、规则、状态、异常、体验承接要求、约束和待确认问题是否被下游遗漏。
- `uxb_output.md` 用于检查 JSON 与 Markdown 的语义一致性及审计完整论证；只有 JSON 时仍可检查下游是否承接 JSON，但不得宣称完成 JSON/Markdown 一致性检查。
- JSON 字段为 `unknown` 或 `[]` 时，不得从会话补齐，也不得直接判断 Markdown 缺失；需要核对时回读 Markdown。
- JSON 与 Markdown 冲突时，将冲突记录为 UXB 交接问题；不得从任一侧自行补全或重判事实。

降级规则：

- 只要 `experience_blueprint.md` 可读，就可以按链路模式执行
- Edge Markdown 缺失时，不阻断执行，只是不做基于异常态矩阵的对照加严；只有 `edge.json` 不算完整 Edge
- `uxb_output.md` 缺失但有效 UXB `5.0` JSON 存在时，跳过 JSON/Markdown 一致性对照并说明，仍可执行 UXB 到下游的承接检查
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

**硬规则：正式产物写入并校验通过后，必须执行 `node shared-workflow/generate-progress-preview.js`；失败仅告警，不得阻断 Handoff。**

## 边界

- 不把 Check 写成“再做一版体验蓝图”
- 不用主观审美词替代结构化 finding
- 不在没有依据时把问题升为 blocker
- 不输出 marker、dashboard 或其他已暂缓执行的 chain 机制
