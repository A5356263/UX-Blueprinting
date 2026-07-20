# Problem Framing Context JSON Schema

## 1. 定位

- 正式产物：`spark-output/context/problem-framing.json`
- `skill`：固定为 `problem-framing`
- `version`：固定为 `2.0`
- 完整问题框定：`spark-output/problem_framing.md`

本 JSON 只提供核心判断、问题、角色、推荐方向、承接要求和事实层级的紧凑索引。完整论证、机会分析和候选方向只保留在 Markdown。

## 2. 固定结构

```json
{
  "skill": "problem-framing",
  "version": "2.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/problem_framing.md",
  "source_refs": [],
  "decision_summary": "unknown",
  "problem_statement": "unknown",
  "primary_roles": [],
  "recommended_direction": "unknown",
  "handoff_requirements": [],
  "hard_constraints": [],
  "out_of_scope": [],
  "confirmed_facts": [],
  "working_assumptions": [],
  "open_questions": []
}
```

只允许以上字段。

## 3. 字段来源

| 字段 | 唯一内容来源 |
|---|---|
| `decision_summary` | `§0` 核心判断 |
| `problem_statement` | `§2` 正式问题定义 |
| `primary_roles` | `§3` 角色名称 |
| `recommended_direction` | `§7` 推荐方向摘要 |
| `handoff_requirements` | `§7` 明确的承接要求 |
| `hard_constraints` | `§8` 硬约束 |
| `out_of_scope` | `§8` 不做什么 |
| `confirmed_facts` | 正文明示的已确认事实 |
| `working_assumptions` | 正文明示的工作假设 |
| `open_questions` | `§9` 的问题本身 |

## 4. 摘取规则

1. JSON 阶段只读取已完成的 `problem_framing.md`。
2. 每个业务字符串必须能直接指回 Markdown 明确表述。
3. 允许删除不影响原意的连接词，禁止跨段重组或补全。
4. 所有集合都是字符串数组，不允许对象数组。
5. 缺失时单值写 `unknown`，集合写 `[]`。
6. 不得把假设改写为事实，不得把待确认问题改写为约束或方向。

## 5. 禁止字段

禁止旧版 `read_sections`、`key_judgments`、`input_summary`、`problem_definition`、`target_roles`、`target_scenarios`、`current_workarounds`、`opportunities`、`candidate_directions`、`experience_focus`、`handoff_contract`、`constraints`、`not_to_do`、`gaps`、`knowledge_anchoring`。

禁止复杂对象、知识原文、候选方向完整论证和责任人映射。

## 6. 校验

```bash
node .claude/skills/problem-framing/scripts/validate-context.js spark-output/context/problem-framing.json
```
