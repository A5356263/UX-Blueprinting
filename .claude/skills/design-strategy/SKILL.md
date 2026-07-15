---
name: design-strategy
description: >
  设计策略生成 Skill。基于已存在的 PRD 或需求材料形成设计判断，输出带来源分级的设计策略报告。
  仅在用户明确要求设计策略、设计策略报告或策略评审时使用；不得仅因发现 PRD 或需求材料而自动触发。
  排除：问题框定（用 problem-framing）、问题重构（用 product-analysis）、需求定案（用 uxb）、交互方案（用 experience-blueprint）、页面规格（用 page-spec）。
---

# 设计策略生成

读取产品需求材料（PRD、流程图、原型、需求文档等），完成两阶段设计策略生成：Phase 1 从材料中识别用户问题并形成设计判断，Phase 2 基于判断展开结构化策略报告。

## Step 0 · 运行入口

### Step 0.1 · 本 Skill 产物状态

执行本 Skill 前，只检查本 Skill 对应正式产物是否存在。

正式产物：
- `spark-output/phase1_<run_name>.md`
- `spark-output/report_<run_name>.md`

如果无法确定 `run_name`，只允许用 `spark-output/phase1_*.md` 或 `spark-output/report_*.md` 做存在性状态标注，不读取正文，不推断是否同一项目。

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

### Step 0.2 · 默认工作目录

本 skill 当前为独立 Skill，不依赖其他 Skill 产出，也不被其他 Skill 调用。默认行为：

- **默认材料来源**：`spark-output/` 下的 HTML 文件（如 `preview/` 中的原型页面）。HTML 能提供页面结构、表单字段、导航关系、交互流程等丰富信号，优于静态图片作为分析材料。
- **默认输出位置**：`spark-output/`，输出文件直接写入该目录。

用户可显式指定其他材料路径或输出位置来覆盖默认行为。

补充规则：

- 可以默认扫描 `spark-output/`，但这属于默认材料入口，不表示必须依赖某个固定工作区结构才能运行
- 如果宿主不支持文件系统，则不依赖目录扫描，改为仅使用用户当前明确提供的材料

> `shared-workflow/skill-graph.json` 仅作为静态关系和预览参考，不参与本 Skill 的运行时路由。上下游关系待后续 Skill 丰富后再定义。

### Step 0.3 · 材料输入与输出位置

**默认行为**：启动后扫描 `spark-output/` 目录，优先使用其中的 HTML 文件作为分析材料。HTML 原型能提供页面结构、表单字段、导航关系、按钮层级等信号，这些正是 Phase 1 "识别用户行为与任务结构"所需的关键信息。

**用户也可显式指定材料来源**：
- 用户上传的附件（PRD、原型图、流程图、需求文档、HTML 原型）
- 用户指定的文件路径
- 对话上下文中直接提供的需求描述

视觉材料（png/jpg/pdf）优先多模态整体理解，不默认走 OCR。

**默认输出**：Phase 1 和 Phase 2 的产出文件直接写入 `spark-output/`。用户可指定其他输出路径。

输出规则补充：

- 如果宿主支持文件系统，先检查并创建目标输出目录，再写入 Phase 1 与 Phase 2 产物

## 角色定义

本 skill 作为设计策略生成工具，做三件事：

1. 从项目材料中识别用户行为、任务结构和核心体验问题
2. 基于问题形成设计取向判断（含 UX 最优解推导、候选方向比较、取舍决策）
3. 展开为设计策略报告，供设计师评审和决策

不做的事：
- 不做视觉设计或前端实现
- 不替代设计师做最终方向裁决
- 不输出 UI 稿或交互原型
- 不做纯业务分析（那是 UXB 或 product-analysis 的职责）

## 两阶段流程

### 命名约定

每轮生成目录：`run_name = <需求名>_<YYYY-MM-DD>_v###`
输出文件：`spark-output/phase1_<run_name>.md` 和 `spark-output/report_<run_name>.md`（用户指定其他位置时以用户指定为准）

### Phase 1 — 问题识别与设计判断

**目标**：从材料中识别用户问题，形成设计取向判断，为 Phase 2 提供决策基础。

Phase 1 不写设计策略，不生成最终报告，不直接决定落地方案。

**产出**：`spark-output/phase1_<run_name>.md`

**三步执行**（详细指南见 [references/phase1_guide.md](references/phase1_guide.md)）：

1. **识别用户行为与任务结构** — 提取用户任务目标、关键行为节点、任务阶段划分、场景边界。同时捕捉材料中的现状信号：已有入口/流程、重复操作、反馈断点、高风险动作缺少保护等。
2. **提炼核心问题** — 每个问题标注 ID（P1、P2…）、行为锚点、信息类型（材料事实/合理推断/待确认）。问题描述应表达用户遇到的判断困难、信息缺口、风险或路径成本过高，不是功能需求原文改写。
3. **形成设计判断** — 先从核心用户问题独立推导 UX 最优解，再生成 2-4 个候选方向（含来源标注：`material_explicit` / `material_inferred` / `kb_pattern` / `domain_inference` / `design_hypothesis`），选定方向并核算取舍缺口。

**knowledge 读取时机**：Phase 1 只在命中时读取诊断型 knowledge。`containers.md` 和 `ia_patterns.md` 仅在 UX 最优解写定后、生成候选方向时按条件读取——详见 [references/phase1_guide.md](references/phase1_guide.md)。

### Phase 2 — 设计策略报告

**目标**：基于 Phase 1 的判断展开设计策略，生成供设计师评审的策略报告。

Phase 2 不重做设计判断，不新增 Phase 1 没有的问题，不自行决定候选方向。

**产出**：`spark-output/report_<run_name>.md`

**三步执行**（详细指南见 [references/phase2_guide.md](references/phase2_guide.md)）：

1. **承接 Phase 1 判断** — 必须先显式读取 Phase 1 落盘文件（即使刚由当前会话生成），理解已识别的问题、选定方向和待确认前提。不重新推导问题，不更换设计取向。
2. **组织策略单元** — 一个策略单元 = 一个独立设计判断。Phase 1 的每个问题（P1-Pn）都必须被某张策略卡片承接。策略标题是设计判断，不是页面模块名或功能名。
3. **展开策略卡片** — 每张卡包含：解决的问题、策略目标、用户路径、设计要点、前提与降级、验证指标。策略卡面向评审阅读，不承载完整候选裁决。

Phase 1 完成后直接进入 Phase 2，无需中间确认。

## knowledge 使用协议

knowledge 文件位于 `knowledge/`，按需读取，不替代项目材料。核心原则：

- **诊断型**（`behavior_patterns.md` / `state_and_feedback_patterns.md` / `domain_knowledge.md`）：Phase 1 识别问题时按需读取，用于辅助识别行为摩擦、状态断点和领域风险。读取后只能校准问题诊断，不得直接推出方案方向。
- **方案型**（`strategy_directions.md`）：Phase 1 不读。Phase 2 展开落地要点时按需读取，用于校准策略方向的适用条件、落地手段和失败边界。用它补充边界和风险，不产生新主策略方向。
- **结构型**（`containers.md` / `ia_patterns.md`）：Phase 1 在 UX 最优解写定后、候选生成阶段按条件读取（详情见 phase1_guide.md）。Phase 2 可继续读取用于展开落地手段。

knowledge 不是生成边界，也不是候选答案池。knowledge 未覆盖的方向，只要有材料锚点或领域推理依据，可以标 `domain_inference` 提出。

不要为了"读全一点"把所有 knowledge 一次性读完——只在命中对应信号时才读取。

## 核心约束

这些约束来自方法论的要害，每一条都有其为什么重要的理由：

### 1. 问题必须锚定材料

每个问题必须有材料中的具体行为、流程节点、界面区域、角色约束或业务规则作为锚点。可以做推断，但推断的是材料已暴露的问题本质，不是另起一套命题。

**为什么**：没有材料锚点的设计决策脱离了用户现实，会让策略报告变成通用方法论罗列。

### 2. 区分三类信息

每条信息都必须能判断属于哪一类：
- **材料事实**：材料明确写出的
- **合理推断**：可从材料信号推导，需说明推断依据
- **待确认**：材料不足，需要外部确认

**为什么**：下游决策需要知道什么是已建立的、什么是假设的、什么还需要验证。把推断写成事实会导致策略建立在沙地上。

### 3. 每条策略必须标注来源

来源分级（详见 [references/source_grading.md](references/source_grading.md)）：

| source_type | 含义 |
|---|---|
| `material_explicit` | 材料明确写出，可作为较强依据 |
| `material_inferred` | 从材料行为/流程/界面信号推断，可进入主策略但保留推断边界 |
| `kb_pattern` | 与 knowledge 中已有模式对应，可作为复用经验来源 |
| `domain_inference` | 基于领域知识提出，必须写成立前提 |
| `design_hypothesis` | 设计假设，只能作为需验证方向，不应写成已确认方案 |

**为什么**：可追溯性让评审者能够评估每条建议的可信度。domain_inference 和 design_hypothesis 不写成立前提会伪装成已确认方案。

### 4. Phase 2 必须引用 Phase 1 问题 ID

每条策略卡片必须显式标注对应的 Phase 1 问题编号（P1、P2 等）。不得凭空生成与 Phase 1 问题都无关的策略。

**为什么**：策略必须回答已识别的问题，而不是引入新问题。如果策略和问题脱节，说明 Phase 1 有缺口需要回退修正。

### 5. Phase 2 不得重做设计判断

Phase 2 的角色是展开和表达 Phase 1 已建立的判断，不是重新决定方向。如果 Phase 2 发现 Phase 1 的判断不够充分，应回退修正 Phase 1，而不是在报告层静默改写。

**为什么**：分叉的判断会造成内部分歧。Phase 1 的独立判断是质量保证的第一道防线，Phase 2 的职责是精准表达。

### 6. knowledge 按需读取，不预载

只在遇到对应信号时才读取对应 knowledge 文件。不要为"完整了解"把所有 knowledge 一口气读完。

**为什么**：预载所有 knowledge 会让分析偏向已有模式，削弱从材料出发的独立判断。knowledge 是校准工具，不是答案库。

### 7. 不读取历史产出

不要读取之前任何一轮的 output 文件作为当前轮的上下文参考。

**为什么**：每个项目有自己的材料锚点和上下文假设。历史产出携带的是旧判断，会污染当前分析。

## 质量自检

### Phase 1 输出前核心检查
- 每个问题都有材料行为锚点
- 推断和事实已区分
- 候选方向标注了来源类型
- UX 最优解先于候选方向表写定
- 选定方向明确写出了具体判断（Phase 2 无需重新推导结构关系）
- 取舍缺口说明了哪些用户问题未被完整解决

### Phase 2 输出前核心检查
- Phase 1 的每个问题（P1-Pn）都被策略覆盖
- 每条策略卡片引用了问题 ID 和 source_type
- domain_inference / design_hypothesis 类策略写了成立前提
- 策略卡片按「解决的问题 → 策略目标 → 用户路径 → 设计要点 → 前提与降级 → 验证指标」组织
- 设计要点写出了具体的界面结构、交互方式、状态反馈或对象关系变化，不只有模式名称

完整自检清单见 [references/phase1_guide.md](references/phase1_guide.md) 和 [references/phase2_guide.md](references/phase2_guide.md)。

## 参考文件索引

| 文件 | 用途 | 何时读 |
|---|---|---|
| [references/phase1_guide.md](references/phase1_guide.md) | Phase 1 完整执行指南（含输出模板和质量自检） | 执行 Phase 1 时 |
| [references/phase2_guide.md](references/phase2_guide.md) | Phase 2 完整执行指南（含策略卡片格式和质量自检） | 执行 Phase 2 时（Phase 1 落盘后） |
| [references/output_templates.md](references/output_templates.md) | Phase 1 和 Phase 2 的完整输出模板 | 需要完整模板参考时 |
| [references/source_grading.md](references/source_grading.md) | 5 级来源分级的详细定义和使用示例 | Phase 2 标注来源时 |
| [knowledge/README.md](knowledge/README.md) | knowledge 文件索引和用途说明 | 判断是否需要读取 knowledge 时 |


## Handoff · 固定下一步

固定输出：

```text
设计策略已完成。当前没有固定下一步推荐。
你可以停在这里。
```

如需刷新进度预览，可使用项目已有预览入口；刷新失败不影响当前 Skill 完成。
