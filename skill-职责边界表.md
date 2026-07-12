# Skill 职责边界表

## 目的

用于统一以下 4 个 skill 的职责边界，避免在后续优化中出现：

- 上游把下游的活提前做完
- 中游回头重判上游已经定住的事情
- 同一类信息在不同 skill 中语义重复但职责不清
- 链路消费时误把中间层当成最终层

涉及 skill：

- `uxb`
- `problem-framing`
- `stories`
- `journey-analysis`

## 总体链路

```text
uxb / problem-framing
        ↓
     stories
        ↓
journey-analysis
        ↓
experience-blueprint
```

说明：

- `uxb` 与 `problem-framing` 都属于一级正式输入层。
- `stories` 属于任务单元层。
- `journey-analysis` 属于旅程阶段层。
- `experience-blueprint` 属于交互与页面展开层，不在本表详细展开。

## 职责边界总表

| Skill | 核心职责 | 承上输入 | 启下输出 | 必须产出什么 | 不负责什么 | 禁止越界 |
|---|---|---|---|---|---|---|
| `uxb` | 正式需求定案 | PRD、需求文档、业务材料、明确输入 | `stories`、`journey-analysis`、`experience-blueprint` | 业务问题、角色、目标、范围、边界、规则、风险、正式承接要求 | 用户故事、旅程图、页面方案、页面规格 | 不提前写任务切片、不提前写旅程阶段、不提前写页面结构 |
| `problem-framing` | 无 PRD 场景下的问题框定与方向收敛 | 模糊想法、问题描述、口头需求、必要时轻量知识锚定 | `stories`、`journey-analysis`、`experience-blueprint` | 问题定义、角色、目标、业务对象、边界、候选方向、推荐方向、承接契约、缺口分层 | 正式需求定案、用户故事、旅程图、页面方案 | 不长成小 `uxb`，不提前写任务清单、不提前写旅程阶段、不提前写蓝图路径 |
| `stories` | 任务单元拆解 | `uxb` 或 `problem-framing` 的正式结论 | `journey-analysis`、`experience-blueprint` | Story Index、Story 详情、完成标准、设计触点、关键假设 | 需求定案、问题框定、旅程图、页面方案 | 不重判方向是否成立，不修改业务边界，不把 Story 写成页面规格或蓝图 |
| `journey-analysis` | 旅程阶段与风险结构分析 | `uxb`、已确认的需求材料，必要时最小补问 | `experience-blueprint` | 阶段、动作、触点、痛点、流失风险、机会点、来源依据、骨架或完整旅程 | 需求定案、页面交互设计、页面规格、研究计划 | 不重判需求成立性，不输出页面方案，不假装拥有真实研究证据 |

## 按层理解

### 1. `uxb`

定位：

- 正式需求定案 skill
- 负责把“这件事要不要做、为谁做、做到哪、边界在哪”定清

它最重要的输出不是页面信息，而是：

- 业务问题定义
- 主角色与对象
- 能力范围
- 规则边界
- 风险与约束
- 下游正式承接要求

它承上：

- 用户明确提供的需求材料
- PRD
- 业务文档

它启下：

- 给 `stories` 提供任务拆解基础
- 给 `journey-analysis` 提供旅程分析基础
- 给 `experience-blueprint` 提供最稳定的一级正式源

它不应抢的职责：

- 不替 `stories` 写任务单元
- 不替 `journey-analysis` 写阶段结构
- 不替 `experience-blueprint` 写交互与页面方案

### 2. `problem-framing`

定位：

- 无 PRD 场景下的一级正式输入 skill
- 负责先获取必要信息，再收敛问题与方向

它最重要的输出不是“灵感”，而是：

- 问题定义
- 主角色
- 目标结果
- 正式业务对象
- 核心边界
- 推荐方向
- 承接契约
- `confirmed_facts / working_assumptions / open_gaps`

它承上：

- 模糊想法
- 白纸需求
- 口头问题描述
- 轻量知识锚定结果

它启下：

- 给 `stories` 提供任务拆解基础
- 给 `journey-analysis` 提供角色、范围、问题主题
- 在满足门槛时，可作为 `experience-blueprint` 的一级正式源

它不应抢的职责：

- 不做正式需求定案
- 不提前切 Story
- 不提前划旅程阶段
- 不提前写页面流程、页面结构、组件形态

当前最需要警惕的风险：

- 为了抗偏移不断补信息，最后长成“小 `uxb`”
- 承接契约写得过深，滑到方案层

### 3. `stories`

定位：

- 任务单元拆解 skill
- 负责把一级正式输入翻译成“可设计、可验证”的任务单元

它最重要的输出不是更多业务分析，而是：

- Story Index
- Persona
- 场景
- 目标
- 可观察完成标准
- 设计触点
- `critical_assumption`

它承上：

- 优先承接 `uxb`
- 次承接 `problem-framing`
- 极少数情况下接受 `direct-input`

它启下：

- 给 `journey-analysis` 提供任务单元
- 给 `experience-blueprint` 提供任务层输入

它的真实价值：

- 不是重复角色和目标
- 而是把“方向 / 需求”翻译成“任务语义”

它不应抢的职责：

- 不重新判断问题是否成立
- 不修改上游已定边界
- 不写旅程阶段
- 不写页面结构、状态文案、蓝图方案

它需要特别守住的规则：

- `confirmed_facts` 可以直接消费
- `working_assumptions` 只能有限消费
- `open_gaps` 不得进入 `acceptance_criteria`

### 4. `journey-analysis`

定位：

- 旅程阶段与风险结构分析 skill
- 负责把需求或任务翻译成“阶段语义”

它最重要的输出不是“画图”，而是：

- 阶段划分
- actions
- touchpoints
- pain points
- dropout risk
- opportunities
- readiness 判断
- 来源依据

它承上：

- `uxb-chain`
- `prd-standalone`
- 必要时最小补问后的结构补全

它启下：

- 给 `experience-blueprint` 提供旅程消费摘要
- 特别提供：
  - 信心最低点
  - 关键转折
  - 流失风险

它的真实价值：

- 不是重复角色和范围
- 而是把“方向 / 任务”翻译成“阶段与风险语义”

它不应抢的职责：

- 不重判需求是否成立
- 不输出页面流程和页面结构
- 不产出页面规格
- 不假装拥有研究证据

它需要特别守住的规则：

- 先做 readiness 判断
- 不够就补问
- 还不够就输出骨架
- 不允许假完整

## 字段重叠不等于职责重叠

以下字段在多个 skill 中都可能出现：

- 角色
- 目标
- 范围
- 约束
- 风险

这不代表职责冲突。

原因：

- `uxb / problem-framing` 写这些字段，是为了定正式输入。
- `stories` 写这些字段，是为了定任务单元。
- `journey-analysis` 写这些字段，是为了定旅程阶段结构。

所以要区分：

- 字段重叠：允许
- 职责重叠：禁止

## 典型越界模式

### 上游越界

典型表现：

- `uxb` 直接写详细 Story
- `uxb` 直接写旅程阶段
- `problem-framing` 直接写任务清单
- `problem-framing` 直接写页面路径

问题：

- 中间层失去价值
- 链路耦合上升
- 一旦上游偏了，下游会一致错到底

### 中游越界

典型表现：

- `stories` 重新判断这个方向该不该做
- `stories` 修改业务边界
- `journey-analysis` 重判需求成立性
- `journey-analysis` 输出页面方案

问题：

- 回头重判上游
- 职责打架
- 消费关系失稳

## 每个 skill 怎样把上游信息做得更好

### `uxb`

关键不是更多信息，而是更稳定的信息：

- 角色清楚
- 业务对象清楚
- 范围清楚
- 规则边界清楚
- 风险与不做什么清楚

### `problem-framing`

关键不是更快出方向，而是先拿到必要信息：

- 主角色
- 当前替代做法
- 目标结果
- 正式业务对象
- 核心边界
- 关键状态与规则

### `stories`

关键不是展开更多 Story，而是更稳地切任务：

- 只吃稳定输入
- 先判断颗粒度
- Theme / Epic 不强行写成 Story
- 未确认项不固化成完成标准

### `journey-analysis`

关键不是无论如何都画完整旅程，而是稳住生成条件：

- readiness 判断
- 最小补问
- 结构回写
- 骨架降级
- 来源标注

## 每个 skill 怎样让下游消费更有用

### `uxb` 对下游有用的方式

- 给出稳定的一级正式源
- 不把任务、旅程、页面方案提前做掉

### `problem-framing` 对下游有用的方式

- 给出清楚的问题定义与承接契约
- 明确哪些是事实，哪些是假设，哪些是缺口

### `stories` 对下游有用的方式

- 给出少量但高质量的任务单元
- 明确优先级
- 明确完成标准
- 明确设计触点
- 明确关键假设

### `journey-analysis` 对下游有用的方式

- 给出阶段结构
- 给出关键转折
- 给出信心最低点
- 给出流失风险
- 给出不过度方案化的机会点

## 一句话定义

- `uxb`：定正式需求输入
- `problem-framing`：定无 PRD 场景下的正式问题输入
- `stories`：把正式输入压成任务单元
- `journey-analysis`：把正式输入压成旅程阶段结构

## 使用建议

### 什么时候优先用 `stories`

当你最关心的是：

- 任务拆解
- 验收标准
- 设计触点
- 任务优先级

### 什么时候优先用 `journey-analysis`

当你最关心的是：

- 阶段划分
- 关键转折
- 流失风险
- 哪些阶段需要重点设计介入

### 什么时候两者都值得保留

当下游要进入 `experience-blueprint`，而你既希望：

- 任务层清楚
- 又希望阶段风险视角清楚

这时：

- `stories` 提供任务语义
- `journey-analysis` 提供阶段语义

两者不是互相替代，而是互补。
