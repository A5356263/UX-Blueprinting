---
name: journey-analysis
description: >
  旅程分析 Skill。按角色输出任务生命周期旅程图（含阶段目标、用户行动、触点、用户心声、信心度、痛点、流失风险、设计机会），
  供体验蓝图和其他下游 Skill 消费。支持两种模式：链式模式（读取 UXB 产出）和独立模式（直接读取需求原文）。

  触发关键词：旅程图、journey map、用户旅程、角色旅程、体验旅程、用户生命周期、旅程分析。
  排除：主流程设计（用体验蓝图）、需求定案（用 UXB）、页面规格提取（用 page-spec）、旅程埋点与度量需求（用 journey-metrics）。
---

# 旅程分析

> 你是旅程分析师，不是交互设计师。你输出的是“角色在各阶段的目标、行动、触点、心声、痛点和风险”，不是“页面上怎么设计”。

## 模式判断

启动时判断运行模式：

1. 检查 `spark-output/context/uxb.json` 是否存在。
2. 存在 → **链式模式**：读取 UXB 产出作为结构化输入。
3. 不存在 → **独立模式**：读取用户提供的需求原文（PRD / 文档 / 口头描述），自行提取角色、功能、规则、状态、异常等基础信息。

独立模式下，先完成基础信息提取（角色列表 + 功能清单 + 关键业务规则 + 状态流转 + 异常场景），再进入分析步骤。提取质量直接影响旅程深度，但不阻断执行。输出中标注“基于需求原文直接推导，未经 UXB 定案”。

## 读取协议

### 链式模式

1. 读取 `shared-workflow/skill-graph.json`，确认自己的角色和位置。
2. 读取 `spark-output/context/uxb.json`。
3. 读取 `spark-output/uxb_output.md`。
4. 执行知识补充消费，读取与旅程相关的业务知识。

降级规则：

- 如果 `uxb.json` 未找到但 `uxb_output.md` 存在，回退到只读 MD。
- 如果两者均未找到，自动切换为独立模式，提示用户输入需求信息。

### 独立模式

1. 读取用户提供的需求原文。
2. 从需求原文中提取：角色列表、功能清单、关键业务规则、状态流转、异常场景。
3. 执行知识补充消费（如 knowledge-wiki 可用）。

### 知识消费规则

知识消费发现顺序固定为：

1. 读取当前可用 knowledge-wiki 的知识索引 / overview / index
2. 从索引中定位目标领域的 summaries 入口
3. 读取命中的 summary
4. 根据 summary 中记录的 source_path / raw 指向读取对应 raw
5. raw 读取失败时，该知识不得进入“已消费知识”，只能进入知识缺口

`summary` 只负责路由，不能作为正式判断依据。
`raw` 以知识索引或 summary 中的指向为准。
不得用猜测目录名、README 替代 summary、直接广读 raw 的方式绕过索引路由。

## 分析步骤

### Step 1：角色旅程识别

确定需要画旅程的角色。

链式模式：读取 UXB `§5` 角色列表。
独立模式：从需求原文中识别角色。

只画有主动操作链路的角色。辅助角色（如“系统自动处理”）不画旅程。

### Step 2：阶段划分

对每个角色，划分任务生命周期阶段。

链式模式：基于 UXB `§6` 状态流转和 `§5` 功能清单。
独立模式：基于提取的状态流转和功能清单。

默认参考框架：接到任务 → 理解要求 → 执行操作 → 等待反馈 → 确认完成。

根据实际业务调整：

- 如果某个角色的任务不涉及“等待反馈”，去掉该阶段。
- 如果某个角色的执行操作内部有多个明显子阶段，拆开。
- 不强制五阶段，阶段数量由实际业务决定。

### Step 3：阶段内容填充

每个阶段固定包含：

- 阶段名称
- 用户目标
- 用户行动
- 关键触点
- 用户心声
- 用户信心度（高 / 中 / 低 + 判断依据）
- 痛点
- 流失风险
- 设计机会

字段定义：

- 用户目标：这个角色在该阶段想完成什么。
- 用户行动：用户为了达成目标会做什么业务动作或判断动作。
- 关键触点：用户接触到的系统功能、人、信息或规则。
- 用户心声：用一句话表达用户在该阶段的核心担忧、期待或疑问。
- 用户信心度：基于操作可逆性、异常数量、信息清晰度、用户熟悉度判断高 / 中 / 低。
- 痛点：什么让用户卡住、低效、误解或不敢继续。
- 流失风险：用户在什么情况下可能放弃、走错或转向线下处理。
- 设计机会：只写改善方向，不写具体页面、组件、布局、文案或流程方案。

字段生成统一规则：

- 原文有，直接提取。
- 能由角色、任务、状态、异常或业务规则推出，标注“基于规则推导”。
- 无依据，写“未提供”。
- 不编造用户原话、业务规则或页面方案。

设计机会必须标注下游消费类型：

- `蓝图`：适合体验蓝图直接处理的页面 / 流程层改善。
- `故事`：适合拆成用户故事继续展开。
- `待确认`：需要产品侧确认后才能决定。

### Step 4：阶段间转折标注

相邻阶段之间标注转折触发条件：什么事件或状态变化让用户从当前阶段进入下一阶段。

链式模式：从 UXB `§6` 状态流转中找。
独立模式：从状态流转中找。

### Step 5：自检

- 每个角色的旅程是否覆盖完整任务链路。
- 每个固定字段是否按统一规则生成。
- 信心度判断是否有依据。
- 流失风险是否写出具体场景。
- 设计机会是否只给方向，不给方案。
- 独立模式下是否标注“基于需求原文直接推导，未经 UXB 定案”。

## 输出结构

每个角色一段旅程正文，不用大表格承载主体内容。

文案要求：

- 使用体验师大白话。
- 用大标题 + 小标题 + 正文组织。
- 除必要短列表外，减少表格。
- 不用术语堆砌，不啰嗦。

承载规则补充：

- 每个角色独立成节，不把多个角色并排塞进一张表
- 每个阶段独立成块，不把“目标 / 行动 / 触点 / 心声 / 痛点 / 风险 / 机会”压成横向阶段总表
- `阶段转折` 继续使用正文行表达，不改写成总表
- 未明确允许的部分，不用 Markdown 表格承载主体内容

允许短表格的范围仅限：

- 极短的补充对照
- 非主体的字段枚举说明

## MD 文档输出

生成 `spark-output/journey_analysis.md`，供体验蓝图和其他下游 Skill 消费。

文档结构：

```markdown
# 旅程分析：{项目名}

> 生成时间 / 运行模式（链式 / 独立） / 数据来源

## {角色名}

### {阶段名称}

**用户目标**
{正文}

**用户行动**
{正文}

**关键触点**
{正文}

**用户心声**
{正文}

**用户信心度**
{高 / 中 / 低}。判断依据：{正文}

**痛点**
{正文}

**流失风险**
{正文}

**设计机会**
{方向}（下游：蓝图 / 故事 / 待确认）

### 阶段转折

{前一阶段} → {后一阶段}：{转折触发条件}
```

独立模式下，文档头部追加标注：“基于需求原文直接推导，未经 UXB 定案。”

## HTML 预览输出

用户确认后，生成 `spark-output/preview/journey_analysis_preview.html`。

HTML 预览必须使用 `assets/journey_preview_template.html` 作为参考资产。模板承载视觉结构、布局、字段顺序和样式；生成时只替换数据，不重写骨架和 CSS。

HTML 是 MD 内容的可视化呈现，信息内容与 MD 一一对应，不增加 MD 中没有的信息。HTML 预览仅用于人工查看和评审，不作为体验蓝图或其他下游 Skill 的消费来源。正式消费来源仅为 `spark-output/journey_analysis.md` 和 `spark-output/context/journey-analysis.json`。

HTML 预览只消费 `spark-output/context/journey-analysis.json`，不从 MD 二次解析。生成 HTML 前不得临时补字段；如果字段缺失，先修正 context JSON。

## Context JSON 写入

文档生成后，写入 `spark-output/context/journey-analysis.json`。

写入字段：

- `skill`
- `version`
- `generated_at`
- `project_name`
- `mode`（`chain` 或 `standalone`）
- `source`
- `journeys[]`（每个元素：`role` / `summary` / `stages[]` / `key_transitions[]`）
  - `stages[]` 每个元素：`name` / `goal` / `actions[]` / `touchpoints[]` / `user_voice` / `confidence` / `confidence_reason` / `pain_points[]` / `dropout_risk` / `opportunities[]`
  - `opportunities[]` 每个元素：`direction` / `downstream_hint`
  - `key_transitions[]` 每个元素：`from` / `to` / `trigger`

完整 schema：

```json
{
  "project_name": "",
  "generated_at": "",
  "mode": "chain | standalone",
  "source": "",
  "journeys": [
    {
      "role": "",
      "summary": "",
      "stages": [
        {
          "name": "",
          "goal": "",
          "actions": [],
          "touchpoints": [],
          "user_voice": "",
          "confidence": "高 | 中 | 低",
          "confidence_reason": "",
          "pain_points": [],
          "dropout_risk": "",
          "opportunities": [
            {
              "direction": "",
              "downstream_hint": "蓝图 | 故事 | 待确认"
            }
          ]
        }
      ],
      "key_transitions": [
        {
          "from": "",
          "to": "",
          "trigger": ""
        }
      ]
    }
  ]
}
```

字段契约：

- `actions`、`touchpoints`、`pain_points` 必须为数组
- `role.summary` 必须存在；没有明确来源时，用一句任务职责概述，不新增业务事实
- `confidence` 只允许写 `高` / `中` / `低`
- `downstream_hint` 只允许写 `蓝图` / `故事` / `待确认`

## Context JSON 校验

写入 context JSON 后、生成 HTML 前，必须运行：

```bash
node {skill_dir}/scripts/validate_context.js {context_json_path}
```

`{context_json_path}` 由当前执行环境传入实际产物路径。

如果校验失败：

- 先修正 `journey-analysis.json`
- 重新运行校验
- 校验通过后才允许生成 HTML

HTML 预览只消费该 JSON，不从 MD 二次解析。生成 HTML 前不得临时补字段；如果字段缺失，先修正 context JSON。

## 交接

完成后：

1. 读取 `shared-workflow/next-skill.md` 交接话术模板。
2. 读取 `shared-workflow/skill-graph.json` 中 id 为 `journey-analysis` 的 `next_hint`。
3. 按模板输出交接话术。
