# 问题与业务方案 Context JSON Schema

## 1. 定位

- 正式产物：`spark-output/context/problem-framing.json`
- `skill`：固定为 `problem-framing`
- `version`：固定为 `3.0`
- 完整语义源：`spark-output/problem_framing.md`

JSON 是 Markdown 的紧凑投影。它提供正式问题、主推荐业务方案、约束和下游承接索引，不镜像候选方案和比较过程。

## 2. 固定结构

```json
{
  "skill": "problem-framing",
  "version": "3.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/problem_framing.md",
  "source_refs": [],
  "mode": "unknown",
  "decision_summary": "unknown",
  "problem_statement": "unknown",
  "primary_roles": [],
  "solution_goal": "unknown",
  "success_signals": [],
  "recommended_solution": "unknown",
  "recommendation_basis": [],
  "business_solution_points": [],
  "handoff_requirements": [],
  "hard_constraints": [],
  "out_of_scope": [],
  "confirmed_facts": [],
  "working_assumptions": [],
  "open_questions": []
}
```

只允许以上字段。

## 3. 字段来源与语义

| 字段 | Markdown 来源 | 语义 |
|---|---|---|
| `mode` | 本次运行模式 | `problem-definition`、`direction-correction` 或 `unknown` |
| `decision_summary` | `§0` | 关键结论 |
| `problem_statement` | `§2` | 正式问题 |
| `primary_roles` | `§3` | 目标角色 |
| `solution_goal` | `§3` | 目标结果 |
| `success_signals` | `§3` | 可观察的成效判断 |
| `recommended_solution` | `§7` | 主推荐方案摘要，属于未来方案 |
| `recommendation_basis` | `§6`、`§7` | 推荐依据 |
| `business_solution_points` | `§8` | 已确定的能力、责任和过程变化，属于未来方案 |
| `handoff_requirements` | `§11` | 下游承接要求 |
| `hard_constraints` | `§4`、`§9` | 已确认约束 |
| `out_of_scope` | `§9` | 本期不做 |
| `confirmed_facts` | 正文明示事实 | 当前已确认事实与约束 |
| `working_assumptions` | 正文明示假设 | 工作假设 |
| `open_questions` | `§10` | 待确认事项 |

## 4. 摘取规则

1. JSON 阶段只读取完成的 `problem_framing.md`。
2. 每个字符串能直接指回 Markdown 明确表述；只允许删除不影响原意的连接词。
3. 单值字段缺失时写 `unknown`，集合字段缺失时写 `[]`。
4. `confirmed_facts` 不收录推荐方案、工作假设或待确认事项。
5. `recommended_solution` 与 `business_solution_points` 不作为当前事实。
6. 数值成效只有输入提供明确依据时才进入 `success_signals`。

## 5. 校验

```bash
node .claude/skills/problem-framing/scripts/validate-context.js spark-output/context/problem-framing.json
```
