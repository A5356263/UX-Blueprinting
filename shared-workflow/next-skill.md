# 静态关系与预览协调

## 使用边界

本文件只用于说明静态关系、进度面板展示口径和人工维护规则。

低算力稳定模式下，业务 Skill 执行时不得读取本文件来决定：

- 当前应该触发哪个 Skill
- 是否切换到另一个 Skill
- 是否根据 `spark-output/context/*.json` 动态计算 ready set
- 是否覆盖用户显式指定的任务类型

当前 Skill 的启动、执行、输入读取、输出和收口，以用户显式意图和对应 `SKILL.md` 为准。

> **静态参考**：`shared-workflow/skill-graph.json` 只提供静态关系、进度预览和人工查看数据。本文档中的算法只用于进度面板，不作为低算力模式下的运行时执行规则。

---

## 一、进度预览与静态关系

> 本章算法只作为进度面板参考，不作为低算力模式下的运行时执行规则。

### 1.1 done 集合

通常扫描 `spark-output/context/` 目录下的正式 Context JSON 判定完成状态。只输出单文件 HTML 的 `solution-swimlane` 是明确例外：以 `spark-output/solution-swimlane/solution_swimlane.html` 存在作为完成信号。

示例：

- 若目录下存在 `uxb.json`，则 `done = { "uxb" }`
- 若存在 `spark-output/solution-swimlane/solution_swimlane.html`，则 `done` 包含 `"solution-swimlane"`
- 首次运行时，`done` 为空集合

### 1.2 ready 判定

对 `skill-graph.json` 中的每个 Skill，判断是否可启动：

```text
条件 1：该 Skill 不在 done 集合中（不重复执行）
条件 2：该 Skill 的 required 数组中的每一项都在 done 集合中
```

两个条件同时满足，则该 Skill `ready`。

特殊情况：

- `required` 为空数组（如 `uxb`）：条件 2 自动满足，任何时候都就绪。
- `required` 有多项：所有项都必须完成。

### 1.3 语义说明

“不就绪”表示“不推荐启动”，不表示“禁止启动”。

补充说明：

- 除 `solution-swimlane` 的固定 HTML 产物外，`done` 集合只以 `spark-output/context/` 下的 JSON 文件为依据；MD 文件存在与否不影响 `ready` 判定。
- 如果用户在 Skill 不就绪时仍然强制执行，行为由该 Skill 的 `SKILL.md` 降级规则定义，例如回退读取、柔和引导或输出骨架版结果。
- 本文件只负责“推荐什么”，不负责“拦截什么”。

### 1.4 基础设施型 Skill

`skill-graph.json` 中 `type = "infrastructure"` 的 Skill，例如 `knowledge-wiki`、`product-analysis`：

- 不参与 `ready` 判定
- 不出现在主链就绪计算中
- 任何时候都可按需调用

就绪判定算法在扫描候选时应跳过 `type: "infrastructure"` 的条目。

其中 `product-analysis` 还需额外遵守一条承接规则：

- 它虽然是基础设施 Skill，但不是通用查询工具，而是“纠偏型回流节点”
- 它的正式下游固定是 `uxb`，不能被推荐为直接进入 `experience-blueprint`、`page-spec` 或其他正式设计下游
- 若调用来源是独立输入或外部材料，则完成后回到 `uxb`
- 若调用来源是 `uxb` 执行中途的纠偏分支，则完成后回到当前 `uxb` 上下文继续定案，而不是开启一个新的主链分支
- shared-workflow 只负责声明“回到 uxb”，具体是外部承接还是内部回流，由 `product-analysis` 和 `uxb` 各自的 `SKILL.md` 负责执行

### 1.5 多上游主链说明

当前主链允许两个第一梯队正式来源：

```text
uxb -> journey-analysis / stories / experience-blueprint
problem-framing -> stories / journey-analysis
stories -> journey-analysis / experience-blueprint
journey-analysis -> experience-blueprint
experience-blueprint -> solution-swimlane / page-spec / edge / board / journey-metrics
product-analysis -> uxb
interface-audit -> uxb / journey-analysis / product-analysis
```

`uxb` 负责有 PRD 或明确需求材料时的需求定案；`problem-framing` 负责无 PRD、白纸或问题未定清时的问题框定。两者都是第一梯队来源，但不互相替代。

`stories` 和 `journey-analysis` 属于第二梯队深化：

- `stories` 把第一梯队结论转成用户故事、任务单元和验收口径
- `journey-analysis` 把上游输入收拢为阶段、触点、断点和旅程结构
- 二者职责不同，可按项目需要插入或独立调用；`uxb` 完成后固定推荐优先进入 `journey-analysis`，`problem-framing` 完成后固定推荐优先进入 `stories`
- 二者是增强型输入，不是进入 `experience-blueprint` 的必经项

当前终点节点：

- `solution-swimlane`
- `page-spec`
- `edge`
- `board`
- `journey-metrics`
- `design-strategy`
- `check`

硬规则：

- `experience-blueprint` 需要至少一个第一梯队正式来源：`uxb` 或 `problem-framing`
- `stories`、`journey-analysis` 的 standalone 结果不能替代第一梯队正式来源
- 不得因为缺少 `stories` 或 `journey-analysis` 阻止推荐 `experience-blueprint`
- shared-workflow 只做推荐与提示，不拦截用户强制调用；降级、补问和跳转由各 Skill 的 `SKILL.md` 执行

### 1.5A journey-analysis 固定下一步

`journey-analysis` 完成后的固定下一步只有 `experience-blueprint`。

- 不根据第一阶梯来源、Stories 或当前产物状态改变候选项。
- `experience-blueprint` 能否正式执行，由它自己的 Step 0 上游读取、模式判断与降级规则处理。
- Handoff 只负责推荐，不负责替目标 Skill 完成运行条件判断。

### 1.6 推荐项产物状态提示

固定 Handoff 只按当前 `SKILL.md` 中的路径映射检查推荐项正式产物是否存在。

- 不读取产物正文或 JSON 字段。
- 不比较 `project_name`。
- 存在正式产物时，只在对应推荐项后追加“（已产出）”。
- 不因产物存在改变推荐顺序、删除候选项或直接执行下一步。

### 1.7 无文件系统时的降级

当宿主没有文件系统能力时，无法扫描目录。此时各 Skill 依赖自身 `SKILL.md` 中的规则判断上游是否存在。

### 1.8 低算力模式优先级关系

```text
用户显式意图 > 当前 Skill 的 SKILL.md > 用户明确指定的输入材料 > 当前 Skill 内部读取规则
```

当 `shared-workflow/` 与当前 `SKILL.md` 信息不一致时，低算力稳定模式下以用户显式意图和当前 `SKILL.md` 为准。`shared-workflow/` 只用于静态关系、进度预览和人工维护参考。

---

## 二、固定 Handoff 一致性规则

> 低算力稳定模式下，各业务 Skill 使用自身 `SKILL.md` 内的固定 Handoff，不读取本文件动态生成下一步。

### 2.1 运行时权威

- 固定候选项、顺序、标签和完成句以当前 `SKILL.md` 为准。
- `skill-graph.json` 只登记同一组静态关系，不生成运行时文案。
- `next-skill.md` 不保存需要 Agent 套用的完整交接模板。

### 2.2 关系集合

对参与固定流转的 Skill：

```text
SKILL.md 固定推荐项集合
=
skill-graph.json 中 next_hint.preferred + next_hint.alternatives
```

- “停在这里”是交互选项，不写入关系图。
- 终点 Skill 的两个数组都为空，Handoff 不推荐其他 Skill。
- 允许消费某产物不等于固定推荐；只有 Handoff 中出现的 Skill 才登记为下一步。

### 2.3 特殊节点

- `knowledge-wiki`、`preview-renderer` 是公共能力，不参与主链固定 Handoff。
- `solution-swimlane` 是体验蓝图后的可视化终点，只承接正式体验蓝图 Markdown 与 JSON，不固定推荐后续 Skill。
- `product-analysis` 是 UXB 纠偏回流节点，固定下一步只有 `uxb`。
- `design-strategy` 是独立终点，当前无固定下一步。
- `interface-audit` 是独立增强节点，固定关系为 `uxb`、`journey-analysis`、`product-analysis`。
- `check` 是设计走查终点，当前无固定下一步。

### 2.4 进度预览刷新策略

进度预览指 `spark-output/progress-preview.html`，用于展示 Skill 流程完成状态。

执行规则：

- 如需要刷新进度面板，优先执行跨平台入口：`node shared-workflow/generate-progress-preview.js`。
- Windows 环境也可使用 PowerShell 兼容入口：`shared-workflow/generate-progress-preview.ps1`。
- 如果当前环境不支持刷新脚本、脚本缺失或执行失败，直接跳过，不得阻断当前 Skill 完成。
- 不直接修改 `shared-workflow/progress-preview.html` 模板。

---

## 三、人工核对

修改任一 Skill 的固定 Handoff 后，必须同时核对：

1. `skill-graph.json` 的静态候选集合是否一致。
2. 本文件的静态关系说明是否仍然成立。
3. 进度预览是否能正常生成。
4. 是否残留动态路由、旧交接示例或基于产物内容的候选判断。
