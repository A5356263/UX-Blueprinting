# 就绪判定与交接话术

> **单一来源**：`_shared/skill-graph.json` 是依赖关系数据的权威源。本文件定义算法和模板，skill-graph.json 提供数据。

---

## 一、就绪判定算法

### 1.1 done 集合

扫描 `spark-output/context/` 目录下所有 `.json` 文件，取文件名（去掉 `.json` 后缀）组成已完成集合。

示例：目录下有 `uxb.json`，则 done = { "uxb" }。

首次运行时，集合为空。

### 1.2 ready 判定

对 `skill-graph.json` 中的每个 Skill，判断是否可启动：

```text
条件 1：该 Skill 不在 done 集合中（不重复执行）
条件 2：该 Skill 的 required 数组中每一项都在 done 集合中
```

两个条件同时满足 = 该 Skill 就绪。

特殊情况：

- `required` 为空数组（如 UXB）：条件 2 自动满足，任何时候都就绪。
- `required` 有多项：所有项都必须完成。

### 1.3 语义说明

"不就绪"表示不推荐启动，不表示禁止启动。

- done 集合只以 `spark-output/context/` 下的 JSON 文件为依据。MD 文件存在与否不影响 ready 判定。
- 如果用户在 Skill 不就绪时仍然强制执行，行为由各 Skill 的 SKILL.md 降级规则定义（如回退读取、柔和引导等）。
- 本文件只负责"推荐什么"，不负责"拦截什么"。

### 1.4 基础设施型 Skill

`skill-graph.json` 中 `type` 为 `"infrastructure"` 的 Skill（如 knowledge-wiki、product-analysis）不参与 ready 判定。它们没有管线阶段，不出现在交接推荐中，任何时候都按需可用。

就绪判定算法在扫描候选时应跳过 `type: "infrastructure"` 的条目。

### 1.5 无文件系统时的降级

当 agent 没有文件系统时，无法扫描目录。此时各 Skill 依赖自身 SKILL.md 中的硬编码来判断上游是否存在。具体降级逻辑由各 Skill 自行定义。

### 1.6 优先级关系

```text
_shared/skill-graph.json  >  各 Skill 的 SKILL.md 硬编码
```

当两者信息不一致时，以 `_shared/` 文件为准。

各 Skill 的 SKILL.md 中应保留硬编码副本作为降级方案，并标注：

```text
此规则与 _shared/skill-graph.json 保持一致，若冲突以 _shared/ 版本为准。
```

---

## 二、交接话术模板

### 2.1 完成句

每个 Skill 完成后，先输出完成句：

> ✅ {name_zh} 完成，{产物简述}

`{产物简述}` 由各 Skill 根据实际产出动态生成，1-2 句即可。

### 2.2 下一步推荐

读取 `skill-graph.json` 中当前 Skill 的 `next_hint.options`，按选项数量决定格式：

**options 为空（终端节点）**

不输出推荐和触发语。只保留完成句。

**options 有 1 项（单选项）**

```
你可以选择：{label} — {reason}
你回复"{下游 name_zh}"即可
```

- `{label}` 取 `option.label`
- `{reason}` 取 `option.reason`
- `{下游 name_zh}` 取下游 Skill 的 `name_zh`

**options 有多项（多选项）**

```
你可以选择：
- 1.{label_a}
- 2.{label_b}
...
你回复对应数字编号即可
```

各项 `{label}` 取对应 `option.label`，按数组顺序编号。

### 2.3 基础设施型 Skill

`type` 为 `"infrastructure"` 的 Skill：

- `options` 非空：按 2.1 + 2.2 正常输出。
- `options` 为空：输出 `✅ {name_zh} 完成。继续走管线的话，回到上一步就好。`

### 2.4 完整示例

**多选项（体验蓝图完成时）：**

```
✅ 体验方案完成，交互流程、页面结构、状态反馈、文案都有了。
你可以选择：
- 1.输出设计文档，给AI生成原型页面
- 2.输出方案埋点
- 3.深度分析方案异常情况
- 4.视觉情绪板
- 5.设计走查
你回复对应数字编号即可
```

**单选项（异常态完成时）：**

```
✅ 异常态分析完成，状态矩阵和异常设计补充已输出。
你可以选择：设计走查 — 整体过一遍完整性和一致性
你回复"设计走查"即可
```

**终端（视觉情绪板完成时）：**

```
✅ 视觉情绪板完成，视觉方向和设计变量已定。
```

**基础设施无下游（knowledge-wiki 完成时）：**

```
✅ 知识库已更新。继续走管线的话，回到上一步就好。
```
