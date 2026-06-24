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

### 2.1 三层结构

每个 Skill 完成后，按以下 3 层结构输出交接话术。

**第 1 层：完成摘要**

用 1-2 句话说明完成了什么、关键产物是什么。

格式：`✅ {Skill中文名} 已完成，产出 {关键产物简述}。`

**第 2 层：推荐下一步**

优先读取 `skill-graph.json` 中当前 Skill 的 `next_hint.preferred`。

输出规则：

- 只有 1 个可推荐 Skill：`下一步建议进入 {next_skill_zh}，{reason}。`
- 有多个并列可推荐 Skill：`下一步建议进入 {skill_a_zh} / {skill_b_zh} / ...，{reason}。`

**第 3 层：触发语**

给出用户可以直接使用的触发语。

输出规则：

- 只有 1 个可推荐 Skill：`你可以说："{trigger_phrase}"`
- 有多个并列可推荐 Skill：逐条列出，每条一行  
  `你可以说："进入 {trigger_a}"`  
  `你也可以说："进入 {trigger_b}"`

### 2.2 终端节点处理

当 Skill 是链路终端（`next_hint.preferred` 为空数组）时：

- 第 2 层改为：`当前链路已完成，无下游 Skill。`
- 第 3 层省略。

### 2.3 冲突处理

当就绪判定算法算出的可启动 Skill 列表与 `skill-graph.json` 中的 `next_hint.preferred` 不一致时：

- 第 2 层（推荐下一步）：以算法结果为准，只列出算法判定为就绪的 Skill。
- 第 3 层（触发语）：跟随第 2 层变化；如果有多个并列可启动项，可并列列出。
- 如果 `next_hint.preferred[0]` 未就绪，第 2 层改为列出算法结果中的前 3 个候选，并在原因中说明首选 Skill 的前置条件尚未满足。

当用户强制执行一个不就绪的 Skill 并完成时，交接话术正常按 3 层结构输出，不因"该 Skill 在算法中未就绪"而省略或修改任何层。

### 2.4 基础设施型 Skill 交接

`skill-graph.json` 中 `type` 为 `"infrastructure"` 的 Skill 完成时，按 `next_hint.preferred` 是否为空区分交接方式：

**有明确下游指向**（`next_hint.preferred` 非空，如 product-analysis）：使用标准 3 层结构，正常推荐下一步和触发语。

**无明确下游指向**（`next_hint.preferred` 为空，如 knowledge-wiki）：不使用管线交接模板，改为输出：

```text
✅ {Skill中文名} 已完成。如需继续使用管线，请回到之前的流程。
```

不输出第 2 层和第 3 层。

### 2.5 完整示例（UXB 完成时）

```text
✅ 需求定案已完成，产出统一需求定案文档（10 章 + 附录）和结构化数据。

下一步建议进入体验蓝图，基于需求定案生成交互设计方案。

你可以说："进入体验蓝图"
```

### 2.6 并列推荐示例（体验蓝图完成时）

```text
✅ 体验蓝图 已完成，产出完整的交互流程、页面结构和状态反馈方案。

下一步建议进入异常态 / 视觉情绪板，体验蓝图完成后，建议进入异常态穷举补齐状态覆盖，或进入视觉情绪板收敛视觉方向。

你可以说："进入异常态"
你也可以说："进入视觉情绪板"
```
