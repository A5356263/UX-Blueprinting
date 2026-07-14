# 就绪判定与交接话术

## 使用边界

本文件只用于说明历史上的下一步推荐算法、进度面板展示口径和人工维护参考。

低算力稳定模式下，业务 Skill 执行时不得读取本文件来决定：

- 当前应该触发哪个 Skill
- 是否切换到另一个 Skill
- 是否根据 `spark-output/context/*.json` 动态计算 ready set
- 是否覆盖用户显式指定的任务类型

当前 Skill 的启动、执行、输入读取、输出和收口，以用户显式意图和对应 `SKILL.md` 为准。

> **静态参考**：`shared-workflow/skill-graph.json` 只提供静态关系、进度预览和人工查看数据。本文档中的算法只作为历史说明或面板参考，不作为低算力模式下的运行时执行规则。

---

## 一、就绪判定算法

> 本章算法只作为历史说明或进度面板参考，不作为低算力模式下的运行时执行规则。

### 1.1 done 集合

扫描 `spark-output/context/` 目录下的所有 `.json` 文件，取文件名（去掉 `.json` 后缀）组成已完成集合。

示例：

- 若目录下存在 `uxb.json`，则 `done = { "uxb" }`
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

- `done` 集合只以 `spark-output/context/` 下的 JSON 文件为依据，MD 文件存在与否不影响 `ready` 判定。
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
uxb -> experience-blueprint
problem-framing -> experience-blueprint
```

`uxb` 负责有 PRD 或明确需求材料时的需求定案；`problem-framing` 负责无 PRD、白纸或问题未定清时的问题框定。两者都是第一梯队来源，但不互相替代。

`stories` 和 `journey-analysis` 属于第二梯队深化：

- `stories` 把第一梯队结论转成用户故事、任务单元和验收口径
- `journey-analysis` 把上游输入收拢为阶段、触点、断点和旅程结构
- 二者职责不同，可按项目需要插入或独立调用；当二者都需要时，推荐深化顺序是 `stories -> journey-analysis`
- 二者是增强型输入，不是进入 `experience-blueprint` 的必经项

硬规则：

- `experience-blueprint` 需要至少一个第一梯队正式来源：`uxb` 或 `problem-framing`
- `stories`、`journey-analysis` 的 standalone 结果不能替代第一梯队正式来源
- 不得因为缺少 `stories` 或 `journey-analysis` 阻止推荐 `experience-blueprint`
- shared-workflow 只做推荐与提示，不拦截用户强制调用；降级、补问和跳转由各 Skill 的 `SKILL.md` 执行

### 1.5A journey-analysis 完成后的动态推荐说明

`journey-analysis` 完成后的下一步推荐，必须结合当前文件状态判断，不是单纯套用 `skill-graph.json` 的静态 `next_hint`。

执行规则如下：

1. 该动态判断由 `journey-analysis` 自身在收尾阶段执行
2. `shared-workflow/next-skill.md` 只记录规则，不替代 Skill 自己做判断
3. 先检查第一梯队来源：
   - `spark-output/context/uxb.json` 或 `spark-output/uxb_output.md`
   - `spark-output/context/problem-framing.json` 或 `spark-output/problem_framing.md`
4. 再检查 Stories：
   - `spark-output/context/stories.json`
   - `spark-output/stories.md`
5. 若存在第一梯队来源，允许推荐 `experience-blueprint`
6. 若存在第一梯队来源但 Stories 不存在，可把 `stories` 作为可选增强提示，不得把它写成进入体验策略前的必经项
7. 若第一梯队来源不存在，推荐回 `problem-framing` 或 `uxb`，不得推荐 `experience-blueprint`

硬规则：

- 无第一梯队正式来源时不得推荐 `experience-blueprint`
- 有第一梯队正式来源时，不得因为 `stories` 缺失而阻止推荐 `experience-blueprint`
- 不允许把“最直接的下游消费方”等同于“当前一定可执行的下一步”

### 1.6 第一梯队后的 Stories 去重过滤

当当前节点是 `uxb` 或 `problem-framing` 时，在输出下一步推荐前增加一次轻量过滤：

- 检查当前第一梯队 JSON 是否存在：`uxb.json` 或 `problem-framing.json`
- 检查 `spark-output/context/stories.json` 是否存在
- 检查 `spark-output/stories.md` 是否存在
- 读取两者的 `project_name`

只有当以下条件同时满足时，才视为“同一需求已完成用户故事深化”：

1. 第一梯队 JSON 的 `project_name` 存在且非空
2. `stories.json.project_name` 存在且非空
3. 两者 `project_name` 完全一致
4. `spark-output/stories.md` 正式产物存在

满足上述条件时：

- 第一梯队完成后不再重复推荐 `stories`
- 可继续推荐 `journey-analysis`；如旅程也已完成，可推荐 `experience-blueprint`

任一条件不满足时：

- 保持 `skill-graph.json` 中的推荐逻辑，但不得把 `stories` 或 `journey-analysis` 写成 `experience-blueprint` 的前置阻断项

### 1.7 无文件系统时的降级

当宿主没有文件系统能力时，无法扫描目录。此时各 Skill 依赖自身 `SKILL.md` 中的规则判断上游是否存在。

### 1.8 低算力模式优先级关系

```text
用户显式意图 > 当前 Skill 的 SKILL.md > 用户明确指定的输入材料 > 当前 Skill 内部读取规则
```

当 `shared-workflow/` 与当前 `SKILL.md` 信息不一致时，低算力稳定模式下以用户显式意图和当前 `SKILL.md` 为准。`shared-workflow/` 只用于静态关系、进度预览和人工维护参考。

---

## 二、交接话术模板

> 本章模板只作为历史说明或人工维护参考。低算力稳定模式下，各业务 Skill 使用自身 `SKILL.md` 内的固定 Handoff 推荐，不读取本文件动态生成下一步。

### 2.1 完成句

每个 Skill 完成后，先输出完成句：

```text
✅ {name_zh} 完成，{产物简述}
```

`{产物简述}` 由各 Skill 根据实际产物动态生成，1-2 句即可。

### 2.2 下一步推荐

推荐项、回复项和交接话术中的稳定中文名，统一使用 `skill-graph.json` 里的 `name_zh`。

读取当前 Skill 的：

- `next_hint.preferred`
- `next_hint.alternatives`

合并成候选项列表，再按候选项数量决定输出格式。

#### 候选项为空

只保留完成句，不输出推荐。

#### 候选项只有 1 项

输出格式：

```text
你可以选择：{label} - {reason}
你回复“{下游 name_zh}”即可
```

#### 候选项有多项

输出格式：

```text
你可以选择：
- 1.{label_a}
- 2.{label_b}
...
你回复对应数字编号即可
```

### 2.3 基础设施型 Skill 的交接

`type = "infrastructure"` 的 Skill：

- 若有下游推荐：按普通规则输出
- 若无下游推荐：输出

```text
✅ {name_zh} 完成。继续走管线的话，回到上一步就好。
```

`product-analysis` 是例外。它有固定承接目标，因此交接文案不能写成泛化的“回到上一步就好”，而应明确写成“回到 UXB”。

若无法判断是独立进入还是 `uxb` 中途回流，默认仍输出“回到 UXB 继续定案”，不要输出进入正式蓝图或其他下游的建议。

### 2.4 进度预览刷新策略

进度预览指 `spark-output/progress-preview.html`，用于展示 Skill 流程完成状态。

执行规则：

- 如需要刷新进度面板，优先执行跨平台入口：`node shared-workflow/generate-progress-preview.js`。
- Windows 环境也可使用 PowerShell 兼容入口：`shared-workflow/generate-progress-preview.ps1`。
- 如果当前环境不支持刷新脚本、脚本缺失或执行失败，直接跳过，不得阻断当前 Skill 完成。
- 不直接修改 `shared-workflow/progress-preview.html` 模板。

---

## 三、示例

### 3.1 UXB 完成后的单选项

```text
✅ 需求定案完成，需求文档和结构化数据已就位。
你可以选择：用户故事 - 把需求定案转成用户故事、任务单元和验收口径。
你回复“用户故事”即可
```

### 3.1A 问题框定完成后的单选项

```text
✅ 问题框定完成，问题定义、目标用户、场景边界和方向判断已就位。
你可以选择：用户故事 - 把问题框定结果转成用户故事、任务单元和验收口径。
你回复“用户故事”即可
```

### 3.2 体验策略完成后的多选项

```text
✅ 体验策略完成，交互流程、页面结构、状态反馈和文案都已有。
你可以选择：
- 1.设计文档
- 2.异常态
- 3.视觉风格
- 4.旅程埋点与度量需求
你回复对应数字编号即可
```

### 3.3 异常态完成后的单选项

```text
✅ 异常态完成，状态矩阵和异常设计补充已输出。
你可以选择：设计文档 - 把异常态补充吸收到页面规格中。
你回复“设计文档”即可
```

### 3.4 终点节点

```text
✅ 设计文档完成，页面规格层已收口。
```

### 3.5 基础设施型 Skill

```text
✅ 产品分析完成，问题重定义和方向选项已就位。
你可以选择：需求定案 - 回到 UXB 继续正式定案。
你回复“需求定案”即可
```

如果当前是 `uxb` 执行中途触发的纠偏分支，则同样使用“回到 UXB”这一出口语义，但执行含义应理解为：

```text
✅ 产品分析完成，纠偏结论已就位。
你可以选择：需求定案 - 回到当前 UXB 上下文继续定案。
你回复“需求定案”即可
```
