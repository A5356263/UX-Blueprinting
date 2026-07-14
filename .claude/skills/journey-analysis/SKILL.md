---
name: journey-analysis
description: >
  旅程分析 Skill。按角色输出任务生命周期旅程分析，含阶段目标、用户行动、关键触点、痛点、流失风险和设计机会。支持承接 UXB 定案深化，也支持直接读取 PRD 或场景描述独立分析。
  触发关键词：旅程图、journey map、用户旅程、角色旅程、体验旅程、用户生命周期、旅程分析、补全旅程、画旅程。
  排除：正式需求定案（用 uxb）、主流程页面设计（用 experience-blueprint）、页面规格提取（用 page-spec）、埋点和度量需求（用 journey-metrics）。
---

# 旅程分析

## Step 0 · 产物状态检查

执行本 Skill 前，只检查本 Skill 对应正式产物是否存在。

正式产物：
- `spark-output/journey_analysis.md`
- `spark-output/context/journey-analysis.json`

只允许检查文件是否存在；禁止读取产物正文、禁止解析 JSON 内容、禁止根据已有产物改变当前任务类型。

若任一正式产物存在，只输出：

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


> 你是旅程分析师，不是交互设计师，也不是用户研究员。你的职责是判断旅程是否可生成，在必要时补齐最小关键结构，并输出可供下游消费的旅程分析结果。

默认只输出 Markdown 与 Context JSON；如需预览，交给 `preview-renderer`。

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

## 模式判断

启动时先判断运行模式：

### `uxb-chain`

触发条件：

- `spark-output/context/uxb.json` 存在；或
- `spark-output/uxb_output.md` 可读。

用途：

- 基于 `UXB` 结果做旅程深化。
- 即使存在 `UXB`，仍必须先做旅程可生成性判断。
- 即使存在 `UXB`，如缺少关键结构，仍可进入补问。

### `prd-standalone`

触发条件：

- `UXB` 上下文不可用；且
- 用户已经明确提供并确认了本次分析要使用的 `PRD`、需求文档、场景描述或口头需求。

用途：

- 直接从原始需求输入提取旅程基础结构。
- 判断是否足以生成完整旅程。
- 必要时通过补问补齐关键结构。

### `guided-completion`

触发条件：

- 当前输入不足以稳定生成完整旅程；但
- 通过少量补问有机会补齐关键结构。

用途：

- 作为 `uxb-chain` 或 `prd-standalone` 下的补问执行态。
- 补问后必须回写结构化字段，再进入正式生成。

约束：

- `guided-completion` 是执行态，不是最终 `mode` 值。
- 最终 `mode` 只记录 `uxb-chain` 或 `prd-standalone`。
- 是否使用补问，通过 `completion_used: true | false` 记录。

## 输入读取协议

### 读取顺序

1. 按当前 `SKILL.md` 的规则确认本 Skill 自身输入边界。
2. 优先读取 `spark-output/context/uxb.json`。
3. 若 `uxb.json` 不可用，则读取 `spark-output/uxb_output.md`。
4. 若 `UXB` 上下文都不可用，则读取用户提供的 `PRD`、需求文档、场景描述或口头需求。
5. 如 `knowledge-wiki` 可用，则按项目知识消费协议补充与旅程相关的业务知识。

### 输入确认硬门槛

- 无论是否检测到 `UXB`，都必须先向用户说明当前状态并等待确认。
- 如果检测到 `UXB`，必须先确认“是否基于当前 UXB 继续做旅程分析”。
- 如果未检测到 `UXB`，必须先要求用户提供或确认本次要分析的需求材料。
- 未收到用户确认前，不得进入 readiness 判断。
- 未收到用户确认前，不得抽取旅程结构。
- 未收到用户确认前，不得生成正式旅程，也不得生成骨架版旅程。
- 未收到用户确认前，只允许停在“等待用户确认输入”的状态。

### UXB 读取规则

- 如果 `uxb.json` 和 `uxb_output.md` 都可用，优先以 `uxb.json` 为结构化依据，`uxb_output.md` 作为正文补充。
- 如果只有 `uxb_output.md`，仍允许进入 `uxb-chain`，但必须降低结构化信息置信度。
- 如果两者均不可用，则不得假定已完成 `UXB`，必须切换到 `prd-standalone`。

### 原始需求读取规则

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

### 知识消费规则

如需知识补充，必须遵守项目既有知识消费顺序：

1. 先读索引或总览。
2. 再定位 summary。
3. 再根据 summary 指向消费 raw。
4. raw 读取失败时，该知识不得计入“已消费依据”。

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

### 检测到 UXB 时

```text
已检测到 UXB 产出，本次将基于定案结果做旅程深化。
我会先检查角色、旅程范围、阶段和断点信息是否足够。
如果信息已经完整，我会直接生成旅程分析；如果缺少关键结构，我会先补几个必要问题。
如果你确认本次基于这份 UXB 继续做旅程分析，我再进入 readiness 判断。
```

### 检测到 PRD 或原始需求时

```text
当前未检测到 UXB 定案产出，本次将直接基于你提供的需求材料做旅程分析。
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

### Step 0：识别输入来源

- 检查 `spark-output/context/uxb.json`。
- 检查 `spark-output/uxb_output.md`。
- 如有 `UXB`，进入 `uxb-chain`。
- 如无 `UXB`，进入 `prd-standalone`。

### Step 0.5：输入确认

- 如处于 `uxb-chain`，先输出 UXB 确认话术并等待用户确认继续。
- 如处于 `prd-standalone`，先输出原始需求确认话术并等待用户确认输入材料。
- 未确认前，不得进入 readiness 判断。
- 未确认前，不得抽取旅程要素。
- 未确认前，只允许输出等待确认提示。

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

- 运行模式：`uxb-chain | prd-standalone`
- 是否使用补问：`是 | 否`
- 数据来源：列出具体来源
- 结果等级：`完整旅程 | 补全后旅程 | 旅程骨架`

如果结果为旅程骨架，文档中必须单独写出：

- 当前缺口
- 无法输出完整旅程的原因
- 建议下一步

## Context JSON 写入

生成 `spark-output/context/journey-analysis.json`。

固定结构：

```json
{
  "skill": "journey-analysis",
  "version": "1.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/journey_analysis.md",
  "source_refs": [],
  "read_sections": [],
  "mode": "unknown",
  "completion_used": false,
  "result_level": "unknown",
  "journey_subject": {
    "primary_role": "unknown",
    "journey_scope": "unknown",
    "journey_type": "unknown",
    "start_condition": "unknown",
    "end_condition": "unknown"
  },
  "readiness": {
    "role_clarity": "unknown",
    "scope_clarity": "unknown",
    "stage_divisibility": "unknown",
    "touchpoint_recoverability": "unknown",
    "painpoint_evidence": "unknown"
  },
  "skeleton_result": {
    "primary_role_candidates": [],
    "journey_theme": "unknown",
    "rough_stages": [],
    "current_gaps": [],
    "reason_full_journey_unavailable": "unknown",
    "suggested_next_step": "unknown"
  },
  "stages": [
    {
      "stage_id": "unknown",
      "stage_name": "unknown",
      "user_goal": "unknown",
      "actions": [],
      "touchpoints": [],
      "user_voice": "unknown",
      "emotion": "unknown",
      "confidence": "unknown",
      "confidence_reason": "unknown",
      "pain_points": [],
      "dropout_risk": {
        "level": "unknown",
        "reason": "unknown"
      },
      "opportunities": [],
      "evidence": []
    }
  ],
  "key_transitions": [
    {
      "from_stage": "unknown",
      "to_stage": "unknown",
      "trigger": "unknown",
      "risk": "unknown"
    }
  ],
  "gaps": [
    {
      "gap": "unknown",
      "impact": "unknown",
      "needed_input": "unknown"
    }
  ],
  "user_completion": {
    "primary_role": "unknown",
    "journey_scope": "unknown",
    "journey_type": "unknown",
    "start_condition": "unknown",
    "end_condition": "unknown",
    "suspected_breakpoints": [],
    "evidence_sources": [],
    "notes": "unknown"
  }
}
```

硬规则：

- 字段固定，不得新增、删除或改名。
- 只填入本 Skill 正式 Markdown 已产出的信息；缺失信息写 `unknown`、空数组，或进入 `gaps[]`。
- 不得为了填满 JSON 编造信息。
- `mode` 只允许 `uxb-chain`、`prd-standalone` 或 `unknown`。
- `result_level` 只允许 `full`、`completed`、`skeleton` 或 `unknown`。
- 未触发补问时，`completion_used = false`。
- 输出骨架时，`result_level = skeleton`，`skeleton_result` 必须完整，`stages[]` 可为空。
- 输出完整旅程时，`stages[]` 必须保留 `actions[]`、`touchpoints[]`、`pain_points[]`、`dropout_risk`、`opportunities[]`。
- `evidence_sources[]` 必须记录来源分层，不得只写泛化的“上游材料”。
- 当字段来自体验推导时，必须在来源说明中标为 `规则推导`。
- JSON 不复制 Markdown 全文。
- 新增字段不得替换原字段。
- 新增字段只作为元信息补充。

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

输出推荐前，仅检查推荐项对应正式产物是否存在；若存在，只在推荐项名称后追加“（已产出）”。

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
2. 页面规格
3. 设计走查

你回复对应名称即可。
```

“（已产出）”只代表状态，不代表该项被选中或质量通过。

如需刷新进度预览，可使用项目已有预览入口；刷新失败不影响当前 Skill 完成。
