---
name: journey-analysis
description: >
  旅程分析 Skill。按角色输出任务生命周期中的阶段、行动、触点、痛点、流失风险和设计机会。
  触发关键词：旅程图、journey map、用户旅程、角色旅程、体验旅程、用户生命周期、旅程分析、补全旅程、画旅程。
  仅在用户明确要求分析角色任务生命周期、旅程阶段或旅程图时使用；不得仅因 UXB、用户故事或问题框定产物存在而自动触发。
  排除：需求定案（用 uxb）、交互方案（用 experience-blueprint）、页面规格（用 page-spec）、埋点度量（用 journey-metrics）。
---

# 旅程分析

> 你是旅程分析师，不是交互设计师，也不是用户研究员。你的职责是判断旅程是否可生成，在必要时补齐最小关键结构，并输出可供下游消费的旅程分析结果。

默认只输出 Markdown 与 Context JSON；如需预览，交给 `preview-renderer`。

## Step 0 · 运行入口

### Step 0.1 · 本 Skill 产物状态

执行本 Skill 前，只检查本 Skill 对应正式产物是否存在。

正式产物：
- `spark-output/journey_analysis.md`
- `spark-output/context/journey-analysis.json`

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

### Step 0.2 · 上游读取

按以下固定优先级检查并读取正式输入：

1. 先确认本 Skill 自身输入边界。
2. 检查 `spark-output/context/stories.json`；有效 `3.0` JSON 存在时作为用户故事正式机器输入。
3. Stories JSON 缺失、旅程必需字段为 `unknown` 或 `[]`、与 Markdown 明显冲突，或需要审计完整任务叙述时，再完整读取 `spark-output/stories.md`。
4. 检查 `spark-output/context/uxb.json`；有效 `5.0` JSON 存在时作为 UXB 正式机器输入。
5. UXB JSON 缺失、旅程必需字段为 `unknown` 或 `[]`、与 Markdown 明显冲突，或需要审计完整论证时，再读取 `spark-output/uxb_output.md`。
6. 检查 `spark-output/context/problem-framing.json`；存在时只用于快速定位问题方向和边界。
7. 检查并完整读取 `spark-output/problem_framing.md`；存在时作为问题框定完整正式语义源。
8. 上述正式上游均不可用时，读取用户明确提供的 `PRD`、需求文档、场景描述或口头需求。
9. 如 `knowledge-wiki` 可用，从其 `knowledge/wiki/index.md` 进入实际入口；业务知识先按领域 README 选择正式文件，index 明确直达的单一设计知识直接进入，再按顶部导航只读与旅程角色、任务、状态、异常或回流直接相关的章节；条件依赖触发时补读后回到主域，不遍历 raw。

- 停止条件：命中局部知识后不得停止；问题涉及的主体、动作、条件、例外、结果及已触发依赖均有正式依据后再输出。
- 封闭枚举：仅以完整正式清单作答；未命中完整清单时，不得把局部事实表述为全集。
- 输出边界：以上仅作内部检查，不展示读取过程或检查项；证据不足影响正确性时，只说明必要边界。

读取约束：

- 除 UXB `5.0` 和 Stories `3.0` 外，JSON 只用于快速定位，不是正式语义源；同类 Markdown 可用时必须实际完整读取，不能只读摘要或重点章节。
- 即使上游刚在同一会话生成、当前上下文仍保留内容，也不得替代本次正式文件读取。
- 重点章节只决定二次核对优先级，不是正文白名单。
- 只有 Markdown 可用时允许直接以 Markdown 作为正式输入；只有结构完整的 UXB `5.0` JSON 时，也可将 UXB 视为正式机器输入。
- UXB JSON 与 Markdown 明显冲突时，停止使用冲突字段，回读 Markdown 核对并将 JSON 记为交接错误；不得自行选择或补齐。
- 未读完当前实际必需的正式输入，不得进入模式判断、旅程可生成性判断或旅程生成。
- 有效 Stories `3.0` JSON 或 `stories.md` 存在时始终作为主要任务单元；同时存在的 `uxb_output.md` 或 `problem-framing` 只补充边界和约束，不替代用户故事。
- 无有效 Stories `3.0` JSON 和 `stories.md`，但有有效 UXB `5.0` JSON 或 `uxb_output.md` 时，以 UXB 为主要输入；`problem-framing` 只作为补充。
- 禁止在读取前判断运行模式。

### Step 0.3 · 模式判断与降级

完成 Step 0.2 后，按以下互斥优先级确定运行模式：

1. 有效 Stories `3.0` JSON 或 `stories.md` 可读：进入 `stories-chain`。
2. 无有效 Stories `3.0` JSON 和 `stories.md`，但有效 UXB `5.0` JSON 或 `uxb_output.md` 可用：进入 `uxb-chain`。
3. 无有效 Stories `3.0` JSON 和 `stories.md`，且有效 UXB `5.0` JSON 与 `uxb_output.md` 均不可用，但 `problem_framing.md` 可读：进入 `framing-chain`。
4. 上述正式上游均不可用：进入 `prd-standalone`，并等待用户提供或确认本次输入。

#### `stories-chain`

触发条件：有效 `spark-output/context/stories.json` `3.0` 或 `spark-output/stories.md` 可读。

用途：

- 基于用户故事结果做旅程深化。
- 如同时存在 `uxb_output.md`，将 UXB Markdown 作为业务边界和约束补充，不替代 `stories` 的任务单元。
- 仍必须先做旅程可生成性判断；如缺少阶段、触点或关键角色，进入补问。

#### `uxb-chain`

触发条件：

- 有效 `spark-output/context/uxb.json` 或 `spark-output/uxb_output.md` 可读。

用途：

- 基于 `UXB` 结果做旅程深化。
- 即使存在 `UXB`，仍必须先做旅程可生成性判断。
- 即使存在 `UXB`，如缺少关键结构，仍可进入补问。

#### `framing-chain`

触发条件：

- 有效 Stories `3.0` JSON、`stories.md`、有效 UXB `5.0` JSON 与 `uxb_output.md` 均不可用；且
- `spark-output/problem_framing.md` 可读。

用途：

- 基于问题框定结果恢复角色、场景、方向和边界。
- 仍必须先做旅程可生成性判断；缺少关键结构时进入补问或输出旅程骨架。

#### `prd-standalone`

触发条件：

- 有效 Stories `3.0` JSON、`stories.md`、有效 UXB `5.0` JSON、`uxb_output.md` 与 `problem_framing.md` 均不可用；且
- 用户已经明确提供并确认了本次分析要使用的 `PRD`、需求文档、场景描述或口头需求。

用途：

- 直接从原始需求输入提取旅程基础结构。
- 判断是否足以生成完整旅程。
- 必要时通过补问补齐关键结构。

#### `guided-completion`

触发条件：

- 当前输入不足以稳定生成完整旅程；但
- 通过少量补问有机会补齐关键结构。

用途：

- 作为 `stories-chain`、`uxb-chain`、`framing-chain` 或 `prd-standalone` 下的补问执行态。
- 补问后必须回写结构化字段，再进入正式生成。

约束：

- `guided-completion` 是执行态，不是最终 `mode` 值。
- 最终 `mode` 只记录 `stories-chain`、`uxb-chain`、`framing-chain` 或 `prd-standalone`。
- 是否使用补问，通过 `completion_used: true | false` 记录。

#### 输入确认硬门槛

- 无论是否检测到上游，都必须先向用户说明当前状态并等待确认。
- 如果检测到有效 Stories `3.0` JSON 或 `stories.md`，必须先确认“是否基于当前用户故事继续做旅程分析”。
- 如果未检测到有效 Stories `3.0` JSON 和 `stories.md`，但检测到有效 UXB `5.0` JSON 或 `uxb_output.md`，必须先确认“是否基于当前 UXB 继续做旅程分析”。
- 如果未检测到有效 Stories `3.0` JSON、`stories.md`、有效 UXB `5.0` JSON 和 `uxb_output.md`，但检测到 `problem-framing`，必须先确认“是否基于当前问题框定继续做旅程分析”。
- 如果未检测到任何正式上游，必须先要求用户提供或确认本次要分析的需求材料。
- 未收到用户确认前，不得进入 readiness 判断。
- 未收到用户确认前，不得抽取旅程结构。
- 未收到用户确认前，不得生成正式旅程，也不得生成骨架版旅程。
- 未收到用户确认前，只允许停在“等待用户确认输入”的状态。

#### UXB 读取规则

- UXB `5.0` JSON 是同一轮定案结论的结构化机器面。重点消费 `roles`、`features`、`business_rules`、`states`、`exceptions`、`experience_handoff_requirements`、`constraints`、`open_questions`。
- JSON 字段为 `unknown`、`[]`，且该字段是当前旅程生成的必需信息时，必须回读 `uxb_output.md`；不得从会话上下文补齐。
- 需要审计完整论证、背景来源或章节语境时，回读 `uxb_output.md`。
- 如果只有 `uxb_output.md`，仍正常进入 `uxb-chain`；如果只有结构完整的 UXB `5.0` JSON，也可进入 `uxb-chain`。
- 检测到非 `5.0` UXB JSON 且 Markdown 可用时，忽略旧 JSON、基于 Markdown 继续并提示重新生成 JSON；不得在本 Skill 内转换旧结构。

#### Stories 读取规则

- Stories JSON 只接受 `3.0`。必须完整消费 `direction_summary`、`stories[]`、`out_of_scope[]` 和 `open_questions[]`，不得只读取标题或功能名。
- `stories[]` 中的角色、场景、目标、用户任务、优先级、来源依据、完成标准、设计触点、风险和明确假设共同构成正式任务语义。
- 结构完整的 Stories `3.0` JSON 可单独作为正式机器输入；字段为 `unknown`、`[]` 且是当前旅程必需信息，或需要审计完整任务叙述时，回读 `stories.md`。
- 如果只有 `stories.md`，正常进入 `stories-chain`，不得因缺少 JSON 降低正式语义置信度。
- 检测到旧 `2.0` Stories JSON 且 Markdown 可用时，忽略旧 JSON 并完整读取 Markdown；只有旧 `2.0` JSON 时，不得据此恢复 Story 详情或进入 `stories-chain`。
- JSON 与 Markdown 冲突时停止使用冲突字段，回读 Markdown 核对并报告交接错误；不得自行选择、补齐或重判。
- 如果同时存在 `uxb_output.md`，只将 UXB Markdown 作为业务边界和约束补充，不替代 Stories 的任务单元。

#### Problem Framing 读取规则

- Problem Framing JSON 只接受 `2.0` 的 `decision_summary`、`problem_statement`、`primary_roles`、`recommended_direction`、`handoff_requirements`、`hard_constraints`、`out_of_scope`、`confirmed_facts`、`working_assumptions`、`open_questions`。
- 如果 `problem-framing.json` 和 `problem_framing.md` 都可用，JSON 只定位核心问题、角色、方向、约束和待确认问题，完整问题论证和承接要求必须从 `problem_framing.md` 获取。
- 如果只有 `problem_framing.md`，正常进入 `framing-chain`，不得因缺少紧凑 JSON 降低正式语义置信度。
- 检测到非 `2.0` Problem Framing JSON 且 Markdown 可用时，忽略旧 JSON 并提示重新生成，不做版本转换。
- 如果同时存在 `stories` 或 `uxb_output.md`，只将 `problem-framing` 作为问题方向和边界补充，不改变主要模式。

#### 原始需求读取规则

在 `prd-standalone` 下，先从输入中提取以下对象：

- 候选角色
- 业务场景
- 起点
- 终点
- 动作链
- 触点
- 业务规则
- 异常场景
- 可疑断点

如果只能提取到少量信息，也不得阻断执行；但前提仍然是用户已经确认当前输入。确认后，再通过 readiness 判断决定直接生成、补问或骨架降级。

#### 知识消费规则

如需知识补充，必须遵守项目既有知识消费顺序：

1. 先读索引或总览。
2. 再定位 summary。
3. 再根据 summary 指向消费 raw。
4. raw 读取失败时，该知识不得计入“已消费依据”。

### Step 0.4 · 固定输入确认

- 如处于 `stories-chain`，先输出用户故事确认话术并等待用户确认继续。
- 如处于 `uxb-chain`，先输出 UXB 确认话术并等待用户确认继续。
- 如处于 `framing-chain`，先输出问题框定确认话术并等待用户确认继续。
- 如处于 `prd-standalone`，先输出原始需求确认话术并等待用户确认输入材料。
- 未确认前，不得进入 readiness 判断。
- 未确认前，不得抽取旅程要素。
- 未确认前，只允许输出等待确认提示。

## 适用场景与排除场景

### 适用场景

- 已有 `UXB` 产出，希望把定案结果深化为角色旅程。
- `PRD` 不完整，希望从旅程视角反向暴露缺口并补齐结构。
- 只有需求描述或场景描述，希望先得到旅程骨架或补全后的正式旅程。

### 排除场景

- 正式需求定案：用 `UXB`。
- 页面交互设计与主流程展开：用 `experience-blueprint`。
- 页面规格提取：用 `page-spec`。
- 埋点、度量和追踪需求：用 `journey-metrics`。
- 访谈方案、研究计划、样本设计和深访洞察：用 `probe`。

## 核心定位

`journey-analysis` 是旅程补全型分析 Skill，不是单纯的旅程产出器。

它有 3 种结果形态：

1. 直接生成完整旅程。
2. 补问后生成完整旅程。
3. 在信息不足时输出旅程骨架。

它的目标不是“无论输入多差都强行生成”，而是在依据充分时生成正式旅程，在依据不足时明确暴露缺口，避免假完整。

## 旅程可生成性判断

在正式生成前，必须对当前输入做 5 项固定检查。每项只允许输出：

- `通过`
- `部分通过`
- `不通过`

### 1. `role_clarity` 角色清晰度

- `通过`：能明确 1 个主行动角色，且该角色是旅程中的主要操作者。
- `部分通过`：存在 2-3 个候选角色，但主角色不稳定。
- `不通过`：无法明确是谁在执行旅程。

### 2. `scope_clarity` 范围清晰度

- `通过`：能明确旅程分析的是哪段业务场景，且存在起点和终点。
- `部分通过`：知道大致主题，但起点或终点缺失其一。
- `不通过`：连分析哪段旅程都不清楚。

### 3. `stage_divisibility` 阶段可划分性

- `通过`：可稳定拆出至少 3 个阶段，且阶段之间有事件、状态或目标转折依据。
- `部分通过`：只能拆出 2-3 个粗阶段，转折依据较弱。
- `不通过`：无法形成稳定的阶段划分。

### 4. `touchpoint_recoverability` 触点/动作可还原性

- `通过`：大多数阶段都能写出具体行动和触点。
- `部分通过`：只有部分阶段能写出具体行动和触点，其他阶段偏抽象。
- `不通过`：基本无法还原动作和触点。

### 5. `painpoint_evidence` 痛点/风险依据度

- `通过`：至少能提取或稳定推导出部分痛点、风险或断点。
- `部分通过`：只能给出弱推导，证据支持较弱。
- `不通过`：没有依据判断哪里会卡住。

## 执行分支规则

根据 readiness 判断结果，必须按以下硬规则执行：

### 直接生成完整旅程

条件：

- `通过` 项数不少于 4；且
- `role_clarity` 不是 `不通过`；且
- `scope_clarity` 不是 `不通过`。

动作：

- 不补问。
- 直接进入完整旅程生成。
- `completion_used = false`。

### 进入补问闭环

条件：

- 不满足“直接生成完整旅程”的全部条件；且
- `通过 + 部分通过` 项数不少于 3；且
- `role_clarity` 至少为 `部分通过`；且
- `scope_clarity` 至少为 `部分通过`。

动作：

- 进入 `guided-completion`。
- 只补问缺口最大的 3-5 个问题。
- 补问结果必须回写结构化字段后，才允许继续生成。

### 输出旅程骨架

条件：

- `通过 + 部分通过` 项数不超过 2；或
- `role_clarity` 为 `不通过`；或
- `scope_clarity` 为 `不通过`。

动作：

- 不生成完整旅程。
- 只输出旅程骨架、缺口清单和下一步建议。

## 固定用户提示模板

这些模板属于用户可见输出约束，不得省略。

### 检测到 Stories 时

```text
已检测到用户故事产出，本次将基于已有任务单元做旅程深化。
我会先检查角色、旅程范围、阶段和断点信息是否足够。
如果信息已经完整，我会直接生成旅程分析；如果缺少关键结构，我会先补几个必要问题。
如果你确认本次基于这份用户故事继续做旅程分析，我再进入 readiness 判断。
```

### 检测到 UXB 时

```text
已检测到 UXB 产出，本次将基于定案结果做旅程深化。
我会先检查角色、旅程范围、阶段和断点信息是否足够。
如果信息已经完整，我会直接生成旅程分析；如果缺少关键结构，我会先补几个必要问题。
如果你确认本次基于这份 UXB 继续做旅程分析，我再进入 readiness 判断。
```

### 检测到 Problem Framing 时

```text
已检测到问题框定产出，本次将基于已有问题方向和边界做旅程分析。
我会先检查角色、旅程范围、阶段和断点信息是否足够。
如果只缺少少量关键结构，我会先补问；如果信息过薄，我会先给出旅程骨架和缺口清单。
如果你确认本次基于这份问题框定继续做旅程分析，我再进入 readiness 判断。
```

### 检测到 PRD 或原始需求时

```text
当前未检测到可用的正式上游产出，本次将直接基于你提供的需求材料做旅程分析。
我会先判断这些材料是否足够支撑完整旅程。
如果只缺少少量关键结构，我会先补问；如果信息过薄，我会先给出旅程骨架和缺口清单。
当前不会自动扫描 input，请你提供或确认本次要分析的需求材料后我再继续。
```

### 进入补问时

```text
我已经识别出本次旅程的主题，但以下关键信息还不够稳定：{缺口列表}。
我只补问最关键的几项，补完后就继续生成，不会把流程拉长。
如果这些问题不补，本次只能输出骨架版旅程。
```

### 补问结束后

```text
已收到你的补充信息，我会把这些内容写回本次旅程分析的结构字段中。
接下来将基于补充后的角色、范围和断点继续生成正式旅程结果。
```

### 输出骨架时

```text
当前信息还不足以稳定生成完整旅程，我先输出骨架版结果，方便你看到缺口和下一步补充方向。
这不代表旅程分析失败，而是避免在依据不足时给出假完整结果。
```

## 补问触发规则

### 补问上限

- 单次调用最多补问 5 个问题。
- 如果补问 5 个问题后仍不足以生成完整旅程，则停止追问，直接输出骨架版。

### 补问优先级

必须按以下顺序补问，不得跳序：

1. 主角色
2. 旅程范围
3. 起点 / 终点
4. 关键断点
5. 证据来源

### 固定问题池

#### A. 主角色

- 这条旅程里，真正执行主要动作的角色是谁？
- 如果有多个角色，这次先聚焦哪一个？

#### B. 旅程范围

- 这次想分析的是完整旅程，还是其中一段关键场景？
- 如果是一段关键场景，请直接说这段场景是什么。

#### C. 起点与终点

- 这条旅程从什么时刻开始？
- 这条旅程到什么结果算结束？

#### D. 关键断点

- 你现在最怀疑用户会卡在哪一段？
- 哪个阶段最容易流失、误解或放弃？

#### E. 证据来源

- 这些判断主要来自哪里：PRD 原文、现有观察、用户反馈，还是你的经验判断？
- 有没有明确提到的规则、限制或异常场景？

### 补问节奏

补问节奏必须压缩为 3 段：

1. 先反馈当前已知信息。
2. 再说明为什么补问、补问对结果有什么价值。
3. 最后一次性提出 3-5 个关键问题。

除非宿主交互能力限制，否则不采用一问一停的慢节奏。

## 补问结果吸收规则

补问结果必须先转成结构化字段，再参与正式生成。禁止边问边写正文。

### 补充对象

```json
{
  "completion_used": true,
  "user_completion": {
    "primary_role": "",
    "journey_scope": "",
    "journey_type": "end-to-end | segment",
    "start_condition": "",
    "end_condition": "",
    "suspected_breakpoints": [],
    "evidence_sources": [],
    "notes": []
  }
}
```

### 字段吸收优先级

#### `primary_role`

- 用户补问明确指定时，优先级高于模糊原文提取。

#### `journey_scope`

- 决定是全旅程还是单段旅程。
- 直接影响阶段数量和阶段命名。

#### `journey_type`

只允许：

- `end-to-end`
- `segment`

#### `start_condition` / `end_condition`

- 用于约束旅程边界。
- 不允许生成超出该边界的阶段。

#### `suspected_breakpoints`

- 必须进入痛点、风险和机会生成逻辑。
- 这些阶段需要优先展开。

#### `evidence_sources`

- 用于记录本次旅程中的判断依据来源。

## 正式执行流程

### Step 1：抽取初始旅程要素

固定抽取：

- 候选角色
- 业务场景
- 起点
- 终点
- 动作链
- 触点
- 规则
- 异常
- 可疑断点

### Step 2：执行旅程可生成性判断

输出 readiness：

- `role_clarity`
- `scope_clarity`
- `stage_divisibility`
- `touchpoint_recoverability`
- `painpoint_evidence`

### Step 3：选择执行分支

- 达标：直接生成完整旅程。
- 中间态：进入补问闭环。
- 不达标：输出旅程骨架。

### Step 4：如需补问，执行最小补问

- 最多 5 问。
- 必须按优先级选问题。
- 必须使用固定提示模板组织用户可见内容。

### Step 5：补问结果回写

- 将用户回答写入 `user_completion`。
- 禁止跳过回写直接生成正文。

### Step 6：补问后复判

补问后只允许复判 1 次：

- 达标：进入正式生成。
- 仍不达标：输出骨架版。

### Step 7：生成旅程内容

每个角色固定生成：

- 角色摘要
- 阶段正文
- 阶段转折
- 来源说明
- 缺口说明

### Step 8：写入 Markdown

生成：

- `spark-output/journey_analysis.md`

### Step 9：写入 Context JSON

生成：

- `spark-output/context/journey-analysis.json`

### Step 10：执行 JSON 校验

运行：

```bash
node {skill_dir}/scripts/validate_context.js {context_json_path}
```

### Step 11：如需预览则交接

`journey-analysis` 自身不再生成 HTML 预览。
如用户明确确认需要预览，则在 JSON 校验通过后交给 `preview-renderer`。

### Step 12：固定收口

- 使用本文末尾 Handoff · 固定下一步。
- 不读取 shared-workflow/next-skill.md 或 shared-workflow/skill-graph.json 生成候选项。
- 收口后等待用户明确选择。

## 阶段生成规则

### 全旅程

- 默认 4-7 个阶段。
- 少于 4 个阶段，视为表达不足。
- 多于 7 个阶段，必须合并相邻弱阶段。

### 单段旅程

- 默认 3-5 个阶段。
- 少于 3 个阶段，不足以构成旅程。
- 多于 5 个阶段，必须检查是否过度拆分。

### 阶段命名红线

- 必须是业务阶段，不是页面名。
- 必须是状态/任务阶段，不是解决方案名。
- 不允许使用“填写表单页”“详情页”“确认页”这类页面化命名。

## 字段生成规则

每个阶段必须固定包含以下字段：

1. `name`
2. `goal`
3. `actions[]`
4. `touchpoints[]`
5. `user_voice`
6. `confidence`
7. `confidence_reason`
8. `pain_points[]`
9. `dropout_risk`
10. `opportunities[]`

### `actions[]`

- 必须是动作短语。
- 不允许写抽象口号。

### `touchpoints[]`

- 必须写用户接触到的系统、信息、人或规则。

### `user_voice`

- 只能写一句核心心声。
- 如果来自原文或用户补充，可以直接表达。
- 如果来自推导，必须在来源说明里标为推导。
- 不允许伪造真实用户原话。

### `confidence`

只允许：

- `高`
- `中`
- `低`

### `confidence_reason`

- 必须写判断依据。
- 不允许只写“根据判断”。

### `pain_points[]`

- 必须写真实阻塞点、误解点、低效点或不敢继续的原因。

### `dropout_risk`

- 必须写出用户在什么情况下会放弃、走错、转线下或终止。

### `opportunities[]`

- 只能写改进方向。
- 不允许写页面、组件、文案或流程方案。

## 来源标注规则

所有关键结论都必须标明来源类型。只允许以下 4 种：

- `原文提取`
- `用户补充`
- `规则推导`
- `未提供`

### 标注规则

- 原文明确给出：标为 `原文提取`。
- 用户通过补问明确给出：标为 `用户补充`。
- 基于角色、任务、规则、异常、状态推导：标为 `规则推导`。
- 无法从任何来源获得：标为 `未提供`。

硬规则：

- 不允许把 `未提供` 伪装成结论。
- 不允许把推导冒充原文。
- 当来源链路包含 `problem-framing` 与 `stories` 时，必须进一步区分：
  - 来自 `problem-framing` 的业务边界、角色、规则、承接契约。
  - 来自 `stories` 的任务单元、验收口径、设计触点。
  - 基于旅程分析方法形成的体验推导。
- 体验推导不得写成上游事实。
- 每个高流失风险、低信心点、关键转折和设计机会，都必须能追溯到上游来源或明确标为规则推导。
- 如果关键角色、阶段目标或主任务不明确，必须先补问；补问后仍不清晰时，只能输出骨架旅程或降级结果。

## 旅程骨架输出规则

当无法稳定输出完整旅程时，必须输出旅程骨架版，而不是硬写完整旅程。

骨架版最少包含：

1. 主角色候选
2. 旅程主题
3. 2-3 个粗阶段
4. 当前缺口清单
5. 无法输出完整旅程的原因
6. 建议下一步

建议下一步只允许：

- 去 `UXB`
- 去 `probe`
- 去 `product-analysis`
- 补充更具体 `PRD`

## 输出结构

正式产物固定为 Markdown 文档与 Context JSON。
如用户确认，可在正式产物完成后追加一份 HTML 预览，由 `preview-renderer` 承接。
## Markdown 输出

生成：

- `spark-output/journey_analysis.md`

文档头部必须包含：

- 运行模式：`stories-chain | uxb-chain | framing-chain | prd-standalone`
- 是否使用补问：`是 | 否`
- 数据来源：列出具体来源
- 结果等级：`完整旅程 | 补全后旅程 | 旅程骨架`

如果结果为旅程骨架，文档中必须单独写出：

- 当前缺口
- 无法输出完整旅程的原因
- 建议下一步

## ⛔ Context JSON 生成门禁

写入 Context JSON 前，必须完整读取：

`references/context-schema.md`

硬规则：

1. 未完整读取该文件，禁止开始生成 Context JSON。
2. 禁止凭记忆重建 schema，禁止沿用旧 `1.0` / `2.0` 结构。
3. JSON 阶段只以已完成并通过自检的 `journey_analysis.md` 为内容来源；禁止回读原始输入、知识库或会话补充、纠正或重判 Markdown。
4. Context JSON 是同一轮旅程分析结论的结构化机器面，不是摘要索引、Markdown 全文镜像或第二次旅程分析；业务文本禁止概括性简写，只能执行 schema 明确允许的格式清理和列表拆分。
5. 只能写入 schema 明确允许的字段；不得新增、删除、改名或改变字段类型。
6. 不得建立阶段 ID、对象引用、章节映射、中间 JSON 或下游专用字段。
7. Markdown 没有明确内容时，按 schema 写 `unknown` 或 `[]`；禁止为了填满字段进行推导。
8. 必须逐角色、逐阶段执行完整覆盖核对；不得遗漏、重复、跨角色合并或只摘取代表性动作、触点、痛点和机会。
9. 阶段转折、来源和缺口只能承接 Markdown 明确内容；禁止根据阶段顺序、上下文或常识自行生成。
10. 写盘前必须逐字段回看 Markdown；任何限定、条件、示例、枚举或阈值被删除，都视为 JSON 投影失败并恢复对应 Markdown 原文。
11. 写盘后必须运行指定校验脚本。
12. 校验失败时必须修复并重跑；校验未通过不得进入 Handoff，不得宣告 Skill 完成。
13. schema 文件缺失或无法读取时，停止 JSON 生成并明确报告，禁止临时自创结构。

## Context JSON 写入

严格按 `references/context-schema.md` 的 `3.0` 合同生成：

`spark-output/context/journey-analysis.json`

## 预览交接

- `journey-analysis` 自身不再生成 HTML 预览。
- 正式产物完成并通过 JSON 校验后，如用户明确确认需要预览，再交给 `preview-renderer`；不得为了预览临时补字段或绕过当前 JSON 校验。
- 预览是附加动作，不改变主链流转，也不进入 `next_hint`。
- 固定提示口径：

```text
附加操作：
如果需要，我可以继续把本次正式产物渲染成 HTML 预览。
这不会改变主链流转。
```

## Context JSON 校验

写入 JSON 后，且在交给 `preview-renderer` 前，必须运行：

```bash
node {skill_dir}/scripts/validate_context.js {context_json_path}
```

如果校验失败：

1. 先修复 `journey-analysis.json`。
2. 重新执行校验。
3. 校验通过后，才允许交给 `preview-renderer`。

## 与 probe 的边界

### `journey-analysis` 自己补问的范围

- 主角色不清
- 旅程边界不清
- 起点终点不清
- 阶段断点不清
- 可疑流失点不清

### 应建议升级到 `probe` 的范围

- 需要验证真实用户声音
- 需要访谈问题设计
- 需要样本计划
- 需要深访后的主题与洞察提炼
- 当前痛点判断缺少可信证据

### 红线

- 不设计研究方案
- 不输出访谈大纲
- 不假装拥有真实研究证据

## 与 shared-workflow 的边界

- shared-workflow 只作为静态关系、进度预览和人工查看数据源。
- 当前 Skill 的启动、输入读取、执行分支和收口，以用户显式意图和本 SKILL.md 为准。
- standalone 能力只表示本 Skill 可在材料足够时独立执行，不改变全局预览面板的展示口径。

## Handoff · 固定下一步

本 Skill 完成后，只输出固定下一步推荐。

输出推荐前，只按以下映射检查推荐项正式产物是否存在；若存在，只在推荐项名称后追加“（已产出）”。

推荐项产物映射：
- 体验蓝图：`spark-output/experience_blueprint.md` 或 `spark-output/context/experience-blueprint.json`

禁止：
- 读取推荐项产物正文
- 根据产物存在改变推荐顺序
- 动态计算候选项
- 读取 shared-workflow/next-skill.md 生成候选项
- 读取 shared-workflow/skill-graph.json 生成候选项
- 直接执行下一步

固定输出：

```text
用户旅程已完成。你可以继续：
1. 体验蓝图

你回复对应名称即可。
```

“（已产出）”只代表状态，不代表该项被选中或质量通过。

**硬规则：正式产物写入并校验通过后，必须执行 `node shared-workflow/generate-progress-preview.js`；失败仅告警，不得阻断 Handoff。**
