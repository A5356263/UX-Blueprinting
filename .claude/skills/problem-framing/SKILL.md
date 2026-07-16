---
name: problem-framing
description: >
  问题框定 Skill。用于无 PRD、问题未成形、方向尚不清楚的白纸场景，先获取支撑判断所需的必要信息，再通过问题聚焦、机会点收敛和方向判断，输出可供 stories、journey-analysis、experience-blueprint 消费的正式上游结论。
  触发关键词：问题框定、白纸、没有 PRD、无 PRD、方向探索、问题没想清楚、帮我想想方向、从零开始、模糊想法、设计方向、机会点、方向判断。
  排除：用户明确要求需求定案（用 uxb）、现有界面诊断（用 interface-audit）、方向已被否定需重构问题（用 product-analysis）、交互设计方案（用 experience-blueprint）。如果用户明确要求问题框定，即使材料中有 PRD 或详细需求文档，也仍使用本 Skill。
---

# 问题框定

这个 skill 负责在没有 PRD、问题尚未成形时，先尽量获取支撑判断所需的必要信息，再把模糊想法收敛为清楚的问题定义、方向判断和下游承接要求。它与 `uxb` 平级，不是 `uxb` 的前置步骤，也不是轻版 `uxb`。

## Step 0 · 运行入口

### Step 0.1 · 本 Skill 产物状态

执行本 Skill 前，只检查本 Skill 对应正式产物是否存在。

正式产物：
- `spark-output/problem_framing.md`
- `spark-output/context/problem-framing.json`

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

启动后先判断当前输入来源：

1. 读取用户当前对话中的问题描述、目标、想法、约束或背景。
2. 如果用户明确提供文档、URL 或路径，可读取该材料作为背景。
3. 不默认扫描工作区寻找 PRD。
4. 不读取历史产物作为默认输入，除非用户明确要求“基于已有产物继续”。

### Step 0.3 · 输入校准

如果用户输入已经明显属于其他 Skill，必须先说明，但不强制切走：

- 明确 PRD / 需求文档：提示“这更适合 `uxb`，也可以继续在这里做方向框定”。
- 现有界面问题：提示“这更适合 `interface-audit`，也可以继续在这里抽象问题”。
- 方向已被否定：提示“这更适合 `product-analysis`，也可以先在这里重新框问题”。

当用户明确要求“问题框定”时，即使材料中存在完整 PRD、详细需求文档、历史 UXB 产物，也仍按问题框定执行。

这些材料只能作为问题框定输入，不得作为切换到 UXB 的理由。

允许提示：

```text
你提供的材料已经比较完整，后续也可以进入需求定案。本次先按问题框定处理。
```

禁止输出表示已经切换到其他 Skill 的话术。

## 角色定义

问题框定负责：

- 引导用户说清目标用户、真实问题、当前替代做法和成功标准
- 从模糊输入中提炼机会点
- 生成 2-3 个候选方向，并明确推荐一个方向
- 输出下游可消费的承接契约
- 在必要时执行轻量知识锚定，校准正式业务对象与能力边界
- 在关键信息未闭合时主动澄清，而不是直接产出方向

问题框定不负责：

- 正式需求定案
- 业务能力闭环文档
- 用户故事拆解
- 用户旅程分析
- 页面、弹窗、抽屉或组件方案
- 高保真视觉设计或前端实现

## 适用场景与排除场景

### 适用场景

- 用户没有 PRD。
- 用户明确要求基于 PRD、需求文档或历史 UXB 产物先做问题框定。
- 用户只有模糊问题域、方向想法或一句话需求。
- 用户需要先判断“到底在解决什么问题”。
- 用户希望在设计展开前先收敛方向。

### 排除场景

- 用户明确要求需求定案、生成 UXB 或输出 `uxb_output.md`：用 `uxb`。
- 已有截图、DOM、A11Y 或运行态证据，重点是诊断现有界面：用 `interface-audit`。
- 当前方向已经被判断不成立，需要重构问题：用 `product-analysis`。
- 已经要展开交互流程、页面结构和状态文案：用 `experience-blueprint`。
- 需要拆用户任务单元：用 `stories`。
- 需要阶段、触点、流失风险和旅程断点：用 `journey-analysis`。

## 核心判断规则
正式执行前必须先检查 7 个最小必要信息项是否闭合：

1. 主角色是谁。
2. 当前替代做法是什么。
3. 目标结果是什么。
4. 为什么现在值得解决。
5. 正式业务对象是什么。
6. 核心能力边界是什么。
7. 会影响方案成立的关键状态或规则是什么。

每个信息项只允许三种状态：

- `已确认`
- `待确认`
- `无法确认`

任一信息项只要满足以下情况之一，都视为未闭合：

- 表述模糊
- 存在多种可能解释
- 主要依赖 AI 自行补全
- 用户未明确提供
- 经过轻量知识锚定后仍不能确定

规则：

- 只有 `已确认` 的项才能作为稳定判断依据。
- `待确认` 必须主动获取。
- `无法确认` 只能进入保留项，不得伪装成已知事实。

## 执行流程

### Step 1：问题聚焦

固定围绕最小必要信息集收敛问题，优先补当前最关键缺口：

- 谁在遇到问题
- 现在怎么解决
- 什么算成功
- 为什么现在重要
- 正式业务对象是什么
- 边界和不做什么是什么
- 哪些关键状态或规则会影响方向成立

要求：

- 一次只补当前最关键的缺口。
- 每个判断都区分“用户明确提供”和“基于上下文推导”。
- 不把用户给出的方案直接当作问题定义。
- 标准硬，手法软：问题像共同框定，而不是高压盘问。
- 不限制追问次数，但每次追问都必须服务于闭合当前最关键缺口。
- 最低信息集必须覆盖：主角色、当前替代做法、目标结果、正式业务对象、能力边界、关键规则、关键状态。
- 如果缺失项会改变推荐方向或下游蓝图骨架，必须追问。
- 如果缺失项只影响局部页面细节，可以进入 `open_gaps`，不阻断下传。

### Step 1.5：轻量知识锚定

该步骤不是完整 UXB 知识消费，但在命中已有业务域时必须执行。目的只有一个：在进入方向判断前，校准当前问题对应的正式业务对象、既有入口、相邻能力边界、关键角色责任和关键状态规则，防止把用户口述收敛到错误对象。

触发条件满足任一即可：

- 用户描述中出现明确业务对象、系统模块、角色、状态、流程、规则、配置、审批、权限、数据范围、治理、审计等领域线索。
- 当前问题可能落入已有成熟业务域，而不是全新创意。
- 不读知识就无法判断正式业务对象是什么。
- 不读知识就无法区分相邻能力边界。
- 不读知识就可能把已有能力误判成新能力。
- 不读知识就无法判断关键角色责任、状态语义、规则约束或治理边界。

不得使用领域枚举作为触发条件。规则必须通用，不要写成某个具体领域专用。

执行规则：

- 先明确当前要回答的判断问题，再命中知识。
- 判断问题只能围绕正式业务对象、既有能力/入口、相邻边界、角色责任、关键状态/规则/治理约束。
- 先读 `knowledge-wiki` 的 `knowledge/wiki/index.md`。
- 从 index 进入主域的实际入口；下一跳可以是必要的知识集合 README、领域 README 或单一 raw。
- README 存在时必须逐层缩小范围；只读取实际路由命中的 `raw` 文件或章节。条件依赖被触发时按其实际入口补读，读完回到主域闭环。
- `index` 与实际存在的 README 只作为路由层，不得作为正式判断依据；index 直达的 raw 直接作为事实层。
- `raw` 才能进入知识支撑依据。
- raw 读取失败时，该知识不得进入“已消费知识”，只能进入知识缺口。
- 达到当前判断所需的最小充分证据后停止；长 raw 只读导航命中的章节。
- 只允许有 1 个主领域；可补读相邻依赖领域，但只能服务边界判断或依赖判断，不得把相邻领域变成主问题对象。
- 每读取一个 raw，都必须对应一个当前判断问题；不能说明判断用途的 raw，不得读取。
- 不得预设业务集合、目录深度或 README 必然存在，不得猜测目录或遍历 raw。

该步骤只允许回答 5 类问题：

- 当前问题对应的正式业务对象是什么。
- 当前问题更接近哪个既有入口或能力。
- 是否存在必须区分的相邻能力。
- 当前问题涉及哪些关键角色、责任关系或权限关系。
- 当前问题有哪些会影响方向成立的状态、规则、治理约束或审计约束。

禁止在该步骤中：

- 复刻 `uxb` 的完整需求定案流程。
- 输出正式需求定案判断。
- 扩展为页面、流程或交互方案分析。
- 直接 glob `raw/**` 后按文件名猜测读取。
- 把 README 当作正式事实，或因 README 不存在就判断没有知识。
- 只按需求标题、页面名称或单个关键词选知识。
- 为了完整性通读整个领域。

输出中必须轻量记录：

- 命中主领域。
- 补读相邻领域（如有）。
- 已读路由入口。
- 已读 raw / 章节。
- 知识用于校准的判断。
- 仍无法确认的内容。

不要展开完整思考过程，不要复述知识库原文。

如果执行完 Step 1 与 Step 1.5 后，仍存在会影响业务对象、能力边界、主流程骨架或关键状态语义的未闭合项，则这些内容必须进入 `open_gaps`，不得当作方向已稳继续下传。

### Step 2：机会点与方向收敛

基于 Step 1 生成：

- 当前关键矛盾
- 3-5 个机会点
- 2-3 个候选方向
- 1 个推荐方向

候选方向必须包含：

- 解决的问题
- 目标用户价值
- 主要风险
- 成立前提

推荐方向必须明确，不允许只列备选。

如果主角色、目标结果、正式业务对象、核心能力边界、关键状态/规则中任一项仍未闭合，允许输出“带保留的方向收敛结果”，但不得写成“稳定推荐方向已成立”。

### Step 3：承接要求生成

围绕推荐方向输出：

- 推荐方向
- 体验侧关注点
- 承接契约
- 明确不做什么
- 关键待确认前提

承接契约只允许包含：

- 下游不得重判的业务边界
- 下游必须继续展开的判断面
- 业务边界
- 状态边界
- 角色责任

承接契约中禁止出现：

- 页面方案
- 组件方案
- 布局方案
- 具体交互形态建议
- 明显属于蓝图层的行为路径设计

Step 3 完成后停止，不进入用户故事、旅程或页面方案。

## 输出结构

输出到：

- `spark-output/problem_framing.md`
- `spark-output/context/problem-framing.json`

输出规则补充：

- 如果宿主支持文件系统，先检查并创建 `spark-output/` 与 `spark-output/context/`，再写入产物。
- 如果文件写入失败，仍可在对话中输出完整 Markdown，并提示 context JSON 未写入。

Markdown 固定结构：

```markdown
# 问题框定：{项目名}

## §0 关键判断
## §1 输入摘要
## §2 问题定义
## §3 目标用户与场景
## §4 当前替代做法
## §5 机会点
## §6 候选方向
## §7 推荐方向与承接要求
## §8 约束与不做什么
## §9 待确认问题
## §10 知识锚定
```

正文默认用小标题、正文和短列表承载，不整章退化成大表格。

`§0` 到 `§9` 中必须显式区分三层信息：

- `confirmed_facts`
- `working_assumptions`
- `open_gaps`

其中：

- `confirmed_facts` 只记录用户明确提供或经轻量知识锚定后可确认的事实
- `working_assumptions` 只记录当前为继续收敛暂时采用的判断
- `open_gaps` 只记录一旦判断错误就会改写业务对象、能力边界、主流程或关键状态语义的问题

## Context JSON 写入

文档生成后，按固定结构写入 `spark-output/context/problem-framing.json`。

固定结构：

```json
{
  "skill": "problem-framing",
  "version": "1.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/problem_framing.md",
  "source_refs": [],
  "read_sections": [],
  "key_judgments": [
    {
      "judgment": "unknown",
      "impact": "unknown",
      "recommended_approach": "unknown",
      "not_recommended": "unknown",
      "open_question": "unknown"
    }
  ],
  "input_summary": {
    "raw_request": "unknown",
    "confirmed_facts": [],
    "explicit_constraints": [],
    "missing_information": []
  },
  "problem_definition": {
    "problem": "unknown",
    "why_it_matters": "unknown",
    "not_the_problem": []
  },
  "target_roles": [
    {
      "role": "unknown",
      "scenario": "unknown",
      "goal": "unknown",
      "pain": "unknown"
    }
  ],
  "target_scenarios": [
    {
      "scenario": "unknown",
      "trigger": "unknown",
      "current_context": "unknown"
    }
  ],
  "current_workarounds": [
    {
      "workaround": "unknown",
      "limitation": "unknown",
      "evidence": "unknown"
    }
  ],
  "opportunities": [
    {
      "title": "unknown",
      "user_value": "unknown",
      "business_value": "unknown",
      "risk": "unknown"
    }
  ],
  "candidate_directions": [
    {
      "direction": "unknown",
      "solves": "unknown",
      "user_value": "unknown",
      "risk": "unknown",
      "assumption": "unknown"
    }
  ],
  "recommended_direction": {
    "summary": "unknown",
    "reason": "unknown",
    "experience_focus": "unknown",
    "handoff_requirements": []
  },
  "experience_focus": "unknown",
  "handoff_contract": [
    {
      "item": "unknown",
      "requirement": "unknown",
      "reason": "unknown"
    }
  ],
  "constraints": [],
  "not_to_do": [],
  "confirmed_facts": [],
  "working_assumptions": [],
  "gaps": [
    {
      "question": "unknown",
      "impact": "unknown",
      "suggested_owner": "unknown"
    }
  ],
  "knowledge_anchoring": {
    "used_sources": [],
    "supported_conclusions": [],
    "unsupported_parts": []
  }
}
```

硬规则：

- 字段固定，不得新增、删除或改名。
- 只填入本 Skill 正式 Markdown 已产出的信息；缺失信息写 `unknown`、空数组，或进入 `gaps[]`。
- 不得为了填满 JSON 编造信息。
- `recommended_direction` 必须是结构对象，不能只写标题。
- `experience_focus` 与 `handoff_contract[]` 必须保留，用于承接 `§7` 推荐方向与承接要求。
- `not_the_problem`、`not_to_do` 必须保留。
- 未标记为假设的信息，不得进入 `confirmed_facts[]`。
- `knowledge_anchoring` 不得复述知识原文。
- JSON 不复制 Markdown 全文。
- 写入失败不阻断完成，但应在输出中提示。

## 预览交接

- `problem-framing` 自身不生成 HTML 预览。
- 正式产物完成后，如用户明确确认需要预览，再交给 `preview-renderer`。
- 不得为了预览修改当前 Skill 的正式 Markdown、Context JSON 或知识锚定记录。
- 预览是附加动作，不改变主链流转，也不进入 `next_hint`。
- 固定提示口径：

```text
附加操作：
如果需要，我可以继续把本次正式产物渲染成 HTML 预览。
这不会改变主链流转。
```

## Handoff · 固定下一步

本 Skill 完成后，只输出固定下一步推荐。

输出推荐前，只按以下映射检查推荐项正式产物是否存在；若存在，只在推荐项名称后追加“（已产出）”。

推荐项产物映射：
- 用户故事：`spark-output/stories.md` 或 `spark-output/context/stories.json`
- 用户旅程：`spark-output/journey_analysis.md` 或 `spark-output/context/journey-analysis.json`

若推荐项已有“（推荐）”等固定标签，保留固定标签，再追加“（已产出）”。

禁止：
- 读取推荐项产物正文
- 根据产物存在改变推荐顺序
- 动态计算候选项
- 读取 shared-workflow/next-skill.md 生成候选项
- 读取 shared-workflow/skill-graph.json 生成候选项
- 直接执行下一步

固定输出：

```text
问题框定已完成。你可以继续：
1. 用户故事（推荐）
2. 用户旅程
3. 停在这里

你回复对应名称即可。
```

“（已产出）”只代表状态，不代表该项被选中或质量通过。

**硬规则：正式产物写入并校验通过后，必须执行 `node shared-workflow/generate-progress-preview.js`；失败仅告警，不得阻断 Handoff。**

## 边界

### 与 uxb

- `uxb` 处理已有明确需求输入，输出正式需求定案。
- `problem-framing` 处理问题未成形的白纸场景，输出问题结论、方向判断和承接要求。

### 与 product-analysis

- `problem-framing` 处理问题尚未成形。
- `product-analysis` 处理已有方向不成立后的问题重构。

### 与 stories

- `problem-framing` 不写用户故事。
- `stories` 承接本 Skill 的推荐方向和承接契约，拆成任务单元。

### 与 journey-analysis

- `problem-framing` 不写旅程阶段。
- `journey-analysis` 承接角色、场景和方向，分析阶段、触点、断点和流失风险。

## 质量标准

- 问题定义必须明确，不能只是复述用户想法。
- 目标用户或受影响角色必须明确。
- 当前替代做法必须明确；如果未知，必须进入 `§9`。
- 候选方向必须有 2-3 个。
- 推荐方向必须有且只能有 1 个。
- `§7` 必须包含可被下游消费的承接契约。
- 承接契约只写不可重判的边界和必须展开的判断面，不得提前进入方案层。
- 未闭合关键项不得伪装成“这次信息已经够了”。
- 待确认问题不得被改写为方向已定。
- 不得输出页面、组件、流程或文案方案。

## 红线规则

- 不做正式需求定案。
- 不写用户故事。
- 不写旅程阶段。
- 不写页面 / 弹窗 / 抽屉设计。
- 不把用户给出的方案直接改写成问题定义。
- 不把模糊机会点包装成已确认需求。
- 不为了完整性伪造用户、场景、证据或成功标准。
- 不把承接契约写成页面方案、组件方案、布局方案或明显的交互二选一。
- 不把未标记推断冒充事实。
- 不把关键缺口静默抹平。
