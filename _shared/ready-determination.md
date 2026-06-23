# 就绪判定规则

## 1. 适用范围

本文件定义 Skill 的就绪判定逻辑。

- 有文件系统的 agent（代理）：本文件是权威源。
- 无文件系统的 agent（代理）：以各 Skill 的 SKILL.md 内部硬编码为准，本文件不可用。
- 两者冲突时：以本文件为准。

## 2. 就绪判定

### 2.1 done 集合

扫描 `spark-output/context/` 目录下所有 `.json` 文件，取文件名（去掉 `.json` 后缀）组成已完成集合。

示例：目录下有 `uxb.json`，则 done = { "uxb" }。

首次运行时，集合为空。

### 2.2 ready 判定

对 `skill-graph.json` 中的每个 Skill，判断是否可启动：

```text
条件 1：该 Skill 不在 done 集合中（不重复执行）
条件 2：该 Skill 的 required 数组中每一项都在 done 集合中
```

两个条件同时满足 = 该 Skill 就绪。

特殊情况：

- `required` 为空数组（如 UXB）：条件 2 自动满足，任何时候都就绪。
- `required` 有多项（如 future skill required: ["uxb", "experience-blueprint"]）：所有项都必须完成。

### 2.2.1 语义说明

"不就绪"表示不推荐启动，不表示禁止启动。

- done 集合只以 `spark-output/context/` 下的 JSON 文件为依据。MD 文件存在与否不影响 ready 判定。
- 如果用户在 Skill 不就绪时仍然强制执行，行为由各 Skill 的 SKILL.md 降级规则定义（如回退读取、柔和引导等）。
- 本文件只负责"推荐什么"，不负责"拦截什么"。

### 2.3 基础设施型 Skill

`skill-graph.json` 中 `type` 为 `"infrastructure"` 的 Skill（如 knowledge-wiki）不参与 ready 判定。它们没有管线阶段，不出现在交接推荐中，任何时候都按需可用。

就绪判定算法在扫描候选时应跳过 `type: "infrastructure"` 的条目。

### 2.4 无文件系统时的降级

当 agent 没有文件系统时，无法扫描目录。此时各 Skill 依赖自身 SKILL.md 中的硬编码来判断上游是否存在。具体降级逻辑由各 Skill 自行定义。

## 3. 优先级关系

```text
_shared/skill-graph.json  >  各 Skill 的 SKILL.md 硬编码
```

当两者信息不一致时，以 `_shared/` 文件为准。

各 Skill 的 SKILL.md 中应保留硬编码副本作为降级方案，并标注：

```text
此规则与 _shared/skill-graph.json 保持一致，若冲突以 _shared/ 版本为准。
```

## 4. 与 handoff.md 的关系

`handoff.md` 定义交接话术的格式。本文件定义"什么时候可以启动下一个 Skill"。两者独立，不互相覆盖。
