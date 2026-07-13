---
name: stories
description: >
  用户故事 Skill。承接 uxb 或 problem-framing 的正式上游结论，把方向和承接要求拆成可设计、可验证的用户任务单元，输出用户故事文档和结构化 context。
  触发关键词：用户故事、stories、user story、故事拆解、拆任务、任务切片、把需求拆成故事、把方向拆成故事、设计故事、验收标准。
  排除：问题尚未成形（用 problem-framing）、正式需求定案（用 uxb）、旅程阶段分析（用 journey-analysis）、交互流程和页面设计（用 experience-blueprint）。
---

# 用户故事

这个 skill 负责把第一阶梯已经形成的正式上游结论，拆成可承接的用户任务单元。它不重新判断问题是否成立，也不写旅程阶段和页面方案。

来源为 `problem-framing` 时，本 skill 可以执行最小澄清停顿，但该停顿只服务任务拆解，不服务重新判断方向。

## 角色定义

用户故事负责：

- 读取 `uxb` 或 `problem-framing` 的上游结论
- 判断当前方向是主题、Epic 还是单个 Story
- 输出 Story 索引
- 生成每个 Story 的角色、场景、目标、验收标准和设计触点
- 为 `journey-analysis` 和 `experience-blueprint` 提供任务层输入

用户故事不负责：

- 重新做需求定案
- 重新做问题框定
- 输出用户旅程图
- 输出页面流程、页面结构或状态文案方案
- 输出工程 PRD

## 适用场景与排除场景

### 适用场景

- 已有 `uxb` 需求定案，希望拆成用户任务单元。
- 已有 `problem-framing` 问题框定，希望把推荐方向拆成用户故事。
- 设计前需要明确每个任务的完成标准和设计触点。

### 排除场景

- 问题还未成形：用 `problem-framing`。
- 已有明确 PRD 但尚未做需求定案：用 `uxb`。
- 需要旅程阶段、情绪、流失风险：用 `journey-analysis`。
- 需要交互流程、页面设计、状态文案：用 `experience-blueprint`。
- 需要页面生成规格：用 `page-spec`。

## 上游读取协议

启动后先读取 `shared-workflow/skill-graph.json`，再按以下顺序读取上游：

1. `spark-output/context/uxb.json`
2. `spark-output/uxb_output.md`
3. `spark-output/context/problem-framing.json`
4. `spark-output/problem_framing.md`
5. 用户当前对话中明确提供的方向、角色、任务背景

读取规则：

- 如果 `uxb` 与 `problem-framing` 同时存在，优先以 `uxb` 作为正式上游来源。
- 如果只有 `problem-framing`，允许正式运行。
- 如果两者都不存在，但用户在当前对话中已经提供足够明确的方向、角色和任务背景，允许独立运行，并在输出中标注 `source_mode = direct-input`。
- 如果上游没有明确方向、主角色和任务目标，不进入正式 Story 生成。

当正式来源为 `problem-framing` 时，先检查其信息分层：

- `confirmed_facts` 可直接消费
- `working_assumptions` 可有限消费，但必须显式标记
- `open_gaps` 不得直接转写为完成标准、状态规则或硬性交互要求
- 上游明确排除的范围，不得滑入 P0/P1 主线 Story
- 为体验完整性推导出的辅助能力，必须标为辅助能力或 P1/P2，不得抢主链
- 如果某个 Story 来自下游可选增强，而不是上游明确边界，必须在 `source_basis` 中说明

## 核心判断规则

正式生成前必须判断：

1. 是否有明确上游结论或明确方向。
2. 是否有主角色或受影响角色。
3. 是否存在可拆解的任务目标。
4. 当前输入是主题、Epic、Story、Micro 还是 Nano。

颗粒度定义：

- `theme`：一个方向或主题，通常需要拆成多个 Epic 或 Story。
- `epic`：一个较大任务域，通常包含 3-6 个 Story。
- `story`：一个完整用户任务。
- `micro`：一次局部交互。
- `nano`：一个 UI 瞬间。

规则：

- 如果是 `theme` 或 `epic`，先输出 Story 索引，再展开正文。
- 如果是 `story`，直接进入 Story 正文。
- 如果是 `micro` 或 `nano`，必须提示颗粒度偏细，并确认是否仍按 Story 输出。

## 执行流程

### Step 1：确认来源与方向

明确本次 Story 来源：

- `uxb`
- `problem-framing`
- `direct-input`

提取：

- 项目名
- 方向或需求主题
- 主角色
- JTBD 或任务目标
- 约束与不做什么
- 下游承接要求

### Step 1.5：来源澄清停顿

该步骤只在以下条件全部满足时触发：

- 正式来源为 `problem-framing`
- `uxb` 不存在
- 当前输入仍是 `theme` 或 `epic`
- 主角色、核心任务目标、或本轮明确不做什么 这三类关键信息之一缺失或明显不稳定

执行规则：

- 最多补 3 个问题
- 一次只补最关键的 1 个缺口
- 只补任务拆解所必需的信息
- 不回退成问题框定
- 不引入旅程、页面方案或体验诊断内容

允许补问的范围：

- 这组 Story 服务的主角色是谁
- 本轮最优先完成的任务目标是什么
- 哪些内容明确不进入本轮 Story

禁止补问的范围：

- 需求为什么成立
- 是否应该做这个方向
- 应该如何设计页面
- 用户在哪些阶段会流失

### Step 2：颗粒度判断

判断当前输入是：

- 主题
- Epic
- Story
- Micro
- Nano

如果是主题或 Epic，先生成 Story 索引。

Story 索引必须包含：

- 标题
- 颗粒度
- 优先级
- 是否关键假设
- 来源依据

如果来源为 `problem-framing` 且关键缺口仍未闭合，只允许三种结果：

- 仅输出 Story 索引
- 输出带 `critical_assumption` 的 Story
- 明确停止本次 Story 展开，并提示需先补齐问题框定的关键缺口

### Step 3：Story 生成

每个 Story 固定包含：

- 标题
- Persona
- 场景
- 目标
- Story 主体
- 完成标准
- 设计触点
- 优先级
- 风险或待验证点

Story 主体使用用户能理解的自然语言，不写工程字段、接口、表结构或页面布局。

完成标准必须可观察、可验证。来源为 `problem-framing` 时，未确认项不得直接写入完成标准。

来源为 `problem-framing` 时，完成标准还必须满足：

- 只能把 `confirmed_facts` 写成稳定验收标准。
- `working_assumptions` 可进入 Story，但必须在 `critical_assumption` 或 `risk` 中显式标记。
- `open_gaps` 不得写入验收标准。
- 上游明确限定或排除的内容，不得作为 P0/P1 主线验收标准。
- 为体验闭环推导出的辅助能力，必须降级为辅助 Story 或可选增强，不得覆盖上游主任务。

设计触点只写：

- 涉及页面或场景
- 涉及组件类型
- 涉及状态类型
- 涉及交互模式

设计触点不写具体页面结构和文案方案。

### Step 4：Story 自检

每个 Story 生成后必须检查：

- 是否只描述一个任务。
- 是否有明确角色。
- 是否有明确完成标准。
- 是否有设计触点。
- 是否没有写旅程阶段、情绪曲线或流失风险。
- 是否没有写页面布局或组件方案。

不通过则修正后再输出。

## 输出结构

输出到：

- `spark-output/stories.md`
- `spark-output/context/stories.json`

输出规则补充：

- 如果宿主支持文件系统，先检查并创建 `spark-output/` 与 `spark-output/context/`，再写入产物。
- 如果文件写入失败，仍可在对话中输出完整 Markdown，并提示 context JSON 未写入。

Markdown 固定结构：

```markdown
# 用户故事：{项目名}

## 1. 来源与方向
## 2. Story 索引
## 3. Story 详情
## 4. 不进入 Story 的内容
## 5. 待确认问题
```

`Story 详情` 中每个 Story 固定结构：

```markdown
### {story_id}. {title}

- **Persona**：
- **场景**：
- **目标**：
- **优先级**：
- **来源依据**：

**Story 主体**

作为 {persona}，我想 {action}，从而 {outcome}。

**完成标准**

- ...

**设计触点**

- 涉及页面 / 场景：
- 涉及组件类型：
- 涉及状态：
- 涉及交互模式：

**风险或待验证点**

- ...
```

## Context JSON 写入

文档生成后，按下方字段列表写入 `spark-output/context/stories.json`。

写入字段包括：

- `skill`
- `version`
- `generated_at`
- `project_name`
- `source_mode`
- `source_refs[]`
- `direction`
- `persona`
- `stories[]`
- `excluded_items[]`
- `gaps[]`

每个 `stories[]` 元素必须包含：

- `id`
- `title`
- `size`
- `persona`
- `scenario`
- `goal`
- `story_text`
- `acceptance_criteria[]`
- `design_touchpoints[]`
- `priority`
- `source_basis`
- `risk`
- `critical_assumption`

字段规则：

- `stories[]` 不得为空。
- `acceptance_criteria[]` 每个 Story 至少 2 条。
- `design_touchpoints[]` 每个 Story 至少 1 条。
- 若 `critical_assumption` 非空，必须与对应 `risk` 或 `gaps[]` 对齐。
- P0 Story 必须能追溯到 `confirmed_facts`、UXB 定案或 problem-framing 承接契约。
- 辅助能力或可选增强不得伪装成主线 Story。

写入失败不阻断完成，但应在输出中提示。

## 预览交接

- `stories` 自身不生成 HTML 预览。
- 正式产物完成后，如用户明确确认需要预览，再交给 `preview-renderer`。
- 不得为了预览修改当前 Skill 的正式 Markdown、Context JSON、Story 优先级或验收标准。
- 固定提示口径：

```text
用户故事 Markdown 与 Context JSON 已生成。如果需要，我可以继续交给 `preview-renderer` 渲染 HTML 预览。
```

## 交接

当前是否为链路终端，以 `shared-workflow/skill-graph.json` 为准。完成后：

1. 读取 `shared-workflow/next-skill.md` 交接话术模板。
2. 读取 `shared-workflow/skill-graph.json` 中 id 为 `stories` 的 `next_hint`。
3. 根据 `next_hint.preferred` 是否为空，输出标准交接或终端节点交接话术。
4. 如宿主支持文件系统与本地命令执行，写出正式产物后立即刷新一次进度预览，优先执行 `shared-workflow/generate-progress-preview.ps1`。
5. 如刷新失败或宿主不支持，直接跳过，不影响当前 Skill 完成与下游继续。
6. 完成前必须确认已输出预览交接提示。

默认推荐下游：

- `journey-analysis`：需要把任务单元放入阶段、触点和流失风险中。
- `experience-blueprint`：任务已经足够清楚，可以直接展开交互流程和页面设计。

## 边界

### 与 uxb

`stories` 不做需求定案，只消费 `uxb` 的定案结果。

### 与 problem-framing

`stories` 不做问题框定，只消费 `problem-framing` 的方向判断和承接要求。

当来源为 `problem-framing` 时，`stories` 可以执行最小澄清停顿，但该停顿只服务任务拆解，不服务问题成立性判断或方向重构。

### 与 journey-analysis

`stories` 输出任务单元；`journey-analysis` 输出阶段、触点、断点和流失风险。

### 与 experience-blueprint

`stories` 不写页面结构、流程节点、状态文案或异常方案，这些由 `experience-blueprint` 展开。

## 质量标准

- 每个 Story 只能服务一个用户任务。
- 每个 Story 必须有明确 Persona。
- 每个 Story 必须有可观察的完成标准。
- 每个 Story 必须有设计触点。
- Story 标题必须是用户任务，不是页面名或功能模块名。
- 不得把多个任务用“并且 / 同时”塞进一个 Story。
- 来源为 `problem-framing` 时，最小澄清停顿不得超过 3 个问题，且只服务拆解。
- 来源为 `problem-framing` 时，`open_gaps` 不得被写成验收标准。
- 来源为 `problem-framing` 时，若信息仍不稳，允许只输出 Story Index，不强行展开全部 Story。

## 红线规则

- 不重做问题成立性判断。
- 不重做需求定案。
- 不写旅程阶段。
- 不写情绪曲线。
- 不写流失风险。
- 不写页面结构方案。
- 不写具体文案方案。
- 不把工程实现项伪装成用户故事。
- 不得用最小澄清停顿替代 `problem-framing` 或 `uxb`。
- 不得把上游未确认项写成 `acceptance_criteria`。
- 不得把 Story 写成页面规格或蓝图方案。
