# Stories Context JSON Schema

## 1. 定位

- 正式产物：`spark-output/context/stories.json`
- `skill`：固定为 `stories`
- `version`：固定为 `2.0`
- 完整用户故事：`spark-output/stories.md`

本 JSON 只提供方向、角色和 Story 标题级索引。Story 场景、目标、来源、验收标准、设计触点和风险只保留在 Markdown。

## 2. 固定结构

```json
{
  "skill": "stories",
  "version": "2.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/stories.md",
  "source_refs": [],
  "source_mode": "unknown",
  "direction_summary": "unknown",
  "primary_roles": [],
  "story_titles": [],
  "p0_story_titles": [],
  "critical_assumptions": [],
  "out_of_scope": [],
  "open_questions": []
}
```

只允许以上字段。

## 3. 字段来源

| 字段 | 唯一内容来源 |
|---|---|
| `source_mode` | Markdown 已记录的正式来源模式 |
| `direction_summary` | `1. 来源与方向` |
| `primary_roles` | Story 正文中的主要用户角色 |
| `story_titles` | `2. Story 索引` 的全部标题，按顺序 |
| `p0_story_titles` | 索引中明确标记为 P0 的标题 |
| `critical_assumptions` | 正文明示的关键假设 |
| `out_of_scope` | `4. 不进入 Story 的内容` |
| `open_questions` | `5. 待确认问题` |

## 4. 摘取规则

1. JSON 阶段只读取已完成的 `stories.md`。
2. 每个业务字符串必须能直接指回 Markdown 明确表述。
3. 允许删除不影响原意的连接词，禁止跨段重组或补全。
4. 所有集合都是字符串数组，不允许对象数组。
5. 缺失时单值写 `unknown`，集合写 `[]`。
6. 不得为了填满 JSON 推导新 Story、优先级、假设或问题。

## 5. 禁止字段

禁止旧版 `read_sections`、`source_and_direction`、`direction`、`persona`、`story_index`、`stories`、`excluded_items`、`gaps`。

禁止完整验收标准、设计触点、风险、场景正文、Story ID 和对象引用。

## 6. 校验

```bash
node .claude/skills/stories/scripts/validate-context.js spark-output/context/stories.json
```
