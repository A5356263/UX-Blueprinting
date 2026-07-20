# Journey Analysis Context JSON Schema

## 1. 定位

- 正式产物：`spark-output/context/journey-analysis.json`
- `skill`：固定为 `journey-analysis`
- `version`：固定为 `2.0`
- 完整旅程分析：`spark-output/journey_analysis.md`

本 JSON 只提供紧凑交接摘要。完整阶段正文、动作、触点、痛点、机会、证据、流失风险和补全说明只保留在 Markdown。

## 2. 固定结构

只允许以下字段：

```json
{
  "skill": "journey-analysis",
  "version": "2.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/journey_analysis.md",
  "source_refs": [],
  "mode": "unknown",
  "result_level": "unknown",
  "journey_summary": "unknown",
  "primary_roles": [],
  "stage_names": [],
  "lowest_confidence_stages": [],
  "key_transition_summaries": [],
  "critical_gaps": [],
  "open_questions": []
}
```

## 3. 字段来源

| 字段 | 唯一内容来源 |
|---|---|
| `mode` | Markdown 已记录的正式来源模式 |
| `result_level` | Markdown 已记录的结果等级 |
| `journey_summary` | 角色摘要中的旅程主题或范围结论 |
| `primary_roles` | 角色摘要中的正式角色名称 |
| `stage_names` | 全部阶段标题，按正文顺序 |
| `lowest_confidence_stages` | 正文明示为低信心的阶段名称 |
| `key_transition_summaries` | 阶段转折中的直接短句 |
| `critical_gaps` | 缺口说明中的关键缺口 |
| `open_questions` | 尚需产品、业务或技术确认的问题 |

`mode` 只允许 `stories-chain`、`uxb-chain`、`framing-chain`、`prd-standalone`、`unknown`。

`result_level` 直接摘取 Markdown 已记录的结果等级原文；不得把中文等级转换成另一套枚举。

## 4. 摘取规则

1. JSON 阶段只读取已完成并通过自检的 `journey_analysis.md`。
2. 每个业务字符串必须能直接指回 Markdown 中的明确表述。
3. 允许删除不影响原意的连接词，禁止跨段重组或补全。
4. 所有业务集合都是字符串数组，不允许对象数组。
5. Markdown 没有明确内容时，单值写 `unknown`，集合写 `[]`。
6. 不得回读原始需求、知识库或会话填充 JSON。

## 5. 禁止字段

禁止旧版 `read_sections`、`completion_used`、`journey_subject`、`readiness`、`skeleton_result`、`stages`、`key_transitions`、`gaps`、`user_completion`。

禁止阶段 ID、对象引用、完整阶段详情、下游章节映射和中间模型。

## 6. 校验

```bash
node .claude/skills/journey-analysis/scripts/validate_context.js spark-output/context/journey-analysis.json
```

校验失败时只修 JSON 结构并重跑，不得反向修改 Markdown。
