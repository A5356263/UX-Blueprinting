# 就绪判定与交接话术

> **单一来源**：`shared-workflow/skill-graph.json` 是依赖关系数据的权威源。本文档定义算法和模板，`skill-graph.json` 提供数据。

---

## 一、就绪判定算法

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

### 1.5 journey-analysis 的特别说明

`journey-analysis` 在主链中的正式位置仍然是：

```text
uxb -> journey-analysis -> experience-blueprint
```

但当前 `journey-analysis` 已支持在用户显式要求时直接读取 `PRD` 或原始需求运行 `standalone / guided-completion` 能力。

这条能力扩展只属于 `journey-analysis/SKILL.md` 内部执行逻辑，不改变 shared-workflow 的主链 ready 判定规则。

因此：

- `journey-analysis` 在主链推荐中仍然要求 `uxb` 先完成
- 如果用户在 `UXB` 前强制调用它，允许由 `journey-analysis` 自身按降级规则执行
- 此类执行结果不视为替代 `UXB` 的正式定案

### 1.5A journey-analysis 完成后的动态推荐说明

`journey-analysis` 完成后的下一步推荐，不是单纯套用 `skill-graph.json` 里的静态 `next_hint` 文案。

执行规则如下：

1. 该动态判断由 `journey-analysis` 自身在收尾阶段执行
2. `shared-workflow/next-skill.md` 只负责记录这条规则，不替代 Skill 自己做判断
3. 判断顺序固定为：
   - 先检查 `spark-output/context/uxb.json`
   - 若不存在，再检查 `spark-output/uxb_output.md`
4. 若任一存在，视为已有 `UXB`，允许推荐 `experience-blueprint`
5. 若两者都不存在，视为无 `UXB`，必须推荐回 `uxb`

硬规则：

- 无 `UXB` 时不得推荐 `experience-blueprint`
- 不允许把“最直接的下游消费方”等同于“当前一定可执行的下一步”

### 1.6 UXB 后的旅程去重过滤

当当前节点是 `uxb` 时，在输出下一步推荐前增加一次轻量过滤：

- 检查 `spark-output/context/uxb.json` 是否存在
- 检查 `spark-output/context/journey-analysis.json` 是否存在
- 检查 `spark-output/journey_analysis.md` 是否存在
- 读取两者的 `project_name`

只有当以下条件同时满足时，才视为“同一需求已完成旅程分析”：

1. `uxb.json.project_name` 存在且非空
2. `journey-analysis.json.project_name` 存在且非空
3. 两者 `project_name` 完全一致
4. `spark-output/journey_analysis.md` 正式产物存在

满足上述条件时：

- `UXB` 完成后不再重复推荐 `journey-analysis`
- 直接推荐 `experience-blueprint`

任一条件不满足时：

- 保持 `skill-graph.json` 中原有的主链推荐逻辑

### 1.7 无文件系统时的降级

当宿主没有文件系统能力时，无法扫描目录。此时各 Skill 依赖自身 `SKILL.md` 中的规则判断上游是否存在。

### 1.8 优先级关系

```text
shared-workflow/skill-graph.json > 各 Skill 的 SKILL.md 硬编码
```

当两者信息不一致时，以 `shared-workflow/` 文件为准。

---

## 二、交接话术模板

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

---

## 三、示例

### 3.1 UXB 完成后的单选项

```text
✅ 需求定案完成，需求文档和结构化数据已就位。
你可以选择：用户旅程 - 进入用户旅程分析，梳理角色任务生命周期，为体验蓝图补充旅程视角。
你回复“用户旅程”即可
```

### 3.2 体验策略完成后的多选项

```text
✅ 体验策略完成，交互流程、页面结构、状态反馈和文案都已有。
你可以选择：
- 1.设计文档
- 2.异常态
- 3.视觉风格
- 4.旅程埋点与度量需求
- 5.设计走查
你回复对应数字编号即可
```

### 3.3 异常态完成后的单选项

```text
✅ 异常态完成，状态矩阵和异常设计补充已输出。
你可以选择：设计走查 - 整体过一遍完整性和一致性。
你回复“设计走查”即可
```

### 3.4 终点节点

```text
✅ 页面原型完成，正式链路已到终点。
```

### 3.5 基础设施型 Skill

```text
✅ 产品分析完成。
你可以选择：需求定案 - 回到需求侧继续推进。
你回复“需求定案”即可
```
