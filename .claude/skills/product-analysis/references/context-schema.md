# Product Analysis Context JSON Schema

## 1. 定位

- 正式产物：`spark-output/context/product-analysis.json`
- `skill`：固定为 `product-analysis`
- `version`：固定为 `2.0`
- 完整产品分析：`spark-output/product_analysis.md`

本 JSON 只提供方向纠偏结论的紧凑索引。完整失败论证、替代方向、风险和假设只保留在 Markdown。

## 2. 固定结构

```json
{
  "skill": "product-analysis",
  "version": "2.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/product_analysis.md",
  "source_refs": [],
  "source_mode": "unknown",
  "decision_summary": "unknown",
  "failure_summary": "unknown",
  "reframed_problem": "unknown",
  "skipped_premises": [],
  "recommended_direction": "unknown",
  "next_step": "unknown",
  "out_of_scope": [],
  "open_questions": []
}
```

只允许以上字段。

## 3. 字段来源

| 字段 | 唯一内容来源 |
|---|---|
| `source_mode` | Markdown 已记录的正式来源模式 |
| `decision_summary` | `§0` 核心判断 |
| `failure_summary` | `§1` 当前方向为什么不成立 |
| `reframed_problem` | `§2` 真问题重定义 |
| `skipped_premises` | `§3` 被跳过的关键前提 |
| `recommended_direction` | `§5` 推荐方向 |
| `next_step` | `§6` 下一步建议 |
| `out_of_scope` | `§7` 不做什么 |
| `open_questions` | `§8` 的问题本身 |

`source_mode` 只允许 `direct-input`、`uxb-inflight`、`unknown`。

## 4. 摘取规则

1. JSON 阶段只读取已完成的 `product_analysis.md`。
2. 每个业务字符串必须能直接指回 Markdown 明确表述。
3. 允许删除不影响原意的连接词，禁止跨段重组或补全。
4. 所有集合都是字符串数组，不允许对象数组。
5. 缺失时单值写 `unknown`，集合写 `[]`。
6. 不得回读原始需求、UXB、知识库或会话填充 JSON。

## 5. 禁止字段

禁止旧版 `read_sections`、`key_judgments`、`input_summary`、`current_direction_failure`、`alternative_directions`、`not_to_do`、`gaps`。

禁止复杂对象、候选方向完整论证、风险、假设和责任映射。

## 6. 校验

```bash
node .claude/skills/product-analysis/scripts/validate-context.js spark-output/context/product-analysis.json
```
