# UXB Context 10.0 JSON Schema

## 快速导航

- [1. 定位与生成顺序](#1-定位与生成顺序)
- [2. 根结构](#2-根结构)
- [3. 对象字段](#3-对象字段)
- [4. 引用规则](#4-引用规则)
- [5. 结构校验边界](#5-结构校验边界)

## 1. 定位与生成顺序

- 正式 Markdown：`spark-output/uxb_output.md`
- Context JSON：`spark-output/context/uxb.json`
- skill：固定为 `uxb`
- version：固定为 `10.0`

Markdown 是唯一正式语义源。Markdown 冻结后才能生成 JSON。

生成顺序：

1. 读取冻结 Markdown。
2. 按 Markdown 顺序投影 Context。
3. 运行结构校验。
4. 由 Agent 核对语义一致性。

JSON 不读取正式输入、知识库、聊天记录或内部分析补内容。

## 2. 根结构

```json
{
  "skill": "uxb",
  "version": "10.0",
  "generated_at": "2026-08-16T00:00:00+08:00",
  "project_name": "项目名称",
  "artifact_md": "spark-output/uxb_output.md",
  "result_status": "strategy_ready",
  "strategy_basis": {},
  "key_insights": [],
  "experience_strategies": [],
  "design_criteria": [],
  "strategy_boundaries": [],
  "source_trace": []
}
```

根字段全部必填，不允许其他根字段。

- `result_status`：`strategy_ready` 或 `no_independent_strategy`。
- `strategy_ready`：`key_insights`、`experience_strategies`、`design_criteria` 和 `strategy_boundaries` 均至少一项。
- `no_independent_strategy`：`experience_strategies`、`design_criteria` 和 `strategy_boundaries` 为空数组；`key_insights` 可以为空或记录判断依据。

## 3. 对象字段

### 3.1 `strategy_basis`

| 字段 | 类型 | 规则 |
|---|---|---|
| `source_ref` | 非空字符串 | 引用存在的 `ST-xxx` |
| `problem_or_goal` | 非空字符串 | 正式输入中的问题或目标 |
| `target_users` | 非空字符串数组 | 正式输入中的目标用户 |
| `key_tasks` | 非空字符串数组 | 正式输入中的关键任务 |
| `solution_direction` | 非空字符串 | 已确认的解决方向或能力范围 |
| `scope` | 非空字符串数组 | 本轮范围 |
| `out_of_scope` | 字符串数组 | 明确不做内容；未声明时为空数组 |

### 3.2 `key_insights[]`

| 字段 | 类型 | 规则 |
|---|---|---|
| `id` | 非空字符串 | `KI-001` 格式，数组内唯一 |
| `insight` | 非空字符串 | `§1` 中的关键体验判断 |
| `applies_to` | 非空字符串数组 | 角色、任务或旅程阶段 |
| `evidence_refs` | 非空字符串数组 | 引用存在的 `ST-xxx` |

### 3.3 `experience_strategies[]`

| 字段 | 类型 | 规则 |
|---|---|---|
| `id` | 非空字符串 | `ES-001` 格式，数组内唯一 |
| `title` | 非空字符串 | 策略标题 |
| `thesis` | 非空字符串 | 策略主张 |
| `tension` | 非空字符串 | 需要解决的体验矛盾 |
| `applies_to` | 非空字符串数组 | 角色、任务或旅程阶段 |
| `expected_outcome` | 非空字符串 | 预期体验结果 |
| `handoff_outcome` | 非空字符串 | 后续方案需保留的体验结果 |
| `evidence_refs` | 非空字符串数组 | 引用存在的 `ST-xxx` |
| `confidence` | 枚举字符串 | `high`、`medium` 或 `low` |

### 3.4 `design_criteria[]`

| 字段 | 类型 | 规则 |
|---|---|---|
| `id` | 非空字符串 | `DC-001` 格式，数组内唯一 |
| `criterion` | 非空字符串 | 可观察的体验结果 |
| `strategy_refs` | 非空字符串数组 | 引用存在的 `ES-xxx` |
| `source_refs` | 非空字符串数组 | 引用存在的 `ST-xxx` |

### 3.5 `strategy_boundaries[]`

| 字段 | 类型 | 规则 |
|---|---|---|
| `id` | 非空字符串 | `SB-001` 格式，数组内唯一 |
| `boundary` | 非空字符串 | 策略边界或留给交互方案的内容 |
| `strategy_refs` | 非空字符串数组 | 引用存在的 `ES-xxx` |

### 3.6 `source_trace[]`

| 字段 | 类型 | 规则 |
|---|---|---|
| `id` | 非空字符串 | `ST-001` 格式，数组内唯一 |
| `source_type` | 枚举字符串 | 见下方允许值 |
| `source_name` | 非空字符串 | 来源名称 |
| `used_for` | 非空字符串数组 | 引用已有对象或 `strategy_basis` |
| `source_path` | 可选非空字符串 | 来源存在文件路径时填写 |

`source_type` 允许值：

- `formal_input`
- `stories`
- `journey`
- `business_knowledge`
- `design_principle`
- `interaction_pattern`
- `user_confirmation`

## 4. 引用规则

- `strategy_basis.source_ref` 必须引用 `source_trace[].id`。
- 每个 `evidence_refs` 和 `source_refs` 必须引用 `source_trace[].id`。
- 每个 `strategy_refs` 必须引用 `experience_strategies[].id`。
- `source_trace[].used_for` 只能引用 `strategy_basis`、`KI-xxx`、`ES-xxx`、`DC-xxx` 或 `SB-xxx`，且编号必须存在。
- Context 数组顺序沿用 Markdown 对应内容的顺序。
- JSON 每条非元数据内容都必须能在 Markdown 中找到直接来源。

置信度说明：

- `high`：正式主输入直接明确，或用户明确确认。
- `medium`：正式主输入与体验证据或设计知识共同支持，且没有冲突。
- `low`：主要来自设计推导；写入 Markdown 前已获用户逐条确认。

## 5. 结构校验边界

脚本检查 JSON 可解析性、根字段、对象字段、固定值、字段类型、空值、编号、枚举和引用关系。

脚本不检查策略正确性、业务事实充分性、体验方案是否越界、Markdown 与 JSON 语义一致性或策略遗漏。这些由 Agent 核对。
