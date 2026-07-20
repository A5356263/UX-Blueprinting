# UXB Context JSON Schema

## 1. 定位

- 正式产物：`spark-output/context/uxb.json`
- `skill`：固定为 `uxb`
- `version`：固定为 `4.0`
- 完整需求定案：`spark-output/uxb_output.md`

本 JSON 只负责向下游提供紧凑上下文摘要。它不是完整 UXB，不是 Markdown 章节目录或一一映射，也不能脱离 `uxb_output.md` 独立承载规则、状态、异常和体验承接语义。

## 2. 固定结构

只允许以下字段：

```json
{
  "skill": "uxb",
  "version": "4.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/uxb_output.md",
  "source_refs": [],
  "decision_summary": "unknown",
  "primary_roles": [],
  "in_scope": [],
  "out_of_scope": [],
  "hard_constraints": [],
  "confirmed_decisions": [],
  "open_questions": []
}
```

## 3. 字段来源

| 字段 | 唯一内容来源 | 写入规则 |
|---|---|---|
| `generated_at` | 生成元数据 | 写实际时间或 `unknown` |
| `project_name` | UXB 已确定项目名 | 未明确时写 `unknown` |
| `artifact_md` | 固定值 | 必须为 `spark-output/uxb_output.md` |
| `source_refs` | 本轮正式输入 | 只写真实文件路径字符串 |
| `decision_summary` | `§0` | 直接摘取核心判断；不得跨章节重新总结 |
| `primary_roles` | `§5` | 只写主要角色名称，不写职责或关系 |
| `in_scope` | `§4` | 只写已明确纳入的业务能力或范围 |
| `out_of_scope` | `§8` | 完整摘取明确不做的事项，不得筛选 |
| `hard_constraints` | `§8` | 只写已明确的硬约束，不写偏好或建议 |
| `confirmed_decisions` | `§3`、`§4`、`§5`、`§8` 的 `[CONFIRMED]` | 只写用户明确确认的决定；确认事实但不是决定的内容不写 |
| `open_questions` | `§9` | 只写问题本身，不附加影响、责任人、答案或方案 |

## 4. 摘取规则

1. JSON 阶段只读取已冻结且已通过自检的 `uxb_output.md`。
2. 每个非元数据业务字符串都必须能直接指回上表规定章节中的明确原意。
3. 允许删除不影响原意的连接词，禁止跨段合并、重新归纳或补全。
4. 所有业务集合都是字符串数组；不允许对象数组或嵌套业务对象。
5. Markdown 没有明确内容时，单值写 `unknown`，集合写 `[]`。
6. 不要求填满数组；禁止为避免空值回读原始需求、知识库或会话。
7. “用户未反对”、Agent 推荐和默认方案均不得写入 `confirmed_decisions`。
8. `[GAP]` 和 `§9` 的内容不得改写为范围、约束或已确认决定。

## 5. 禁止字段与内容

禁止写入：

- 旧版 `summary`、`scope`、`roles`、`features`、`rules`、`states`、`exceptions`、`handoff`；
- 对象形态的 `open_questions`；
- 任意 ID、引用、关系、映射表或中间模型；
- 角色职责、功能输入输出、规则处理、状态行为、异常恢复等详细业务对象；
- 原始需求复述、成立性论证、知识消费过程和 Markdown 长段落；
- JSON 阶段自行推导的事实、边界、因果、状态、异常或处理方式。

## 6. 正确示例

```json
{
  "skill": "uxb",
  "version": "4.0",
  "generated_at": "2026-07-19",
  "project_name": "子管理员权限复制",
  "artifact_md": "spark-output/uxb_output.md",
  "source_refs": ["input/子管理员权限复制/log.MD"],
  "decision_summary": "在现有权限模型内增加受约束的批量复制能力。",
  "primary_roles": ["子管理员"],
  "in_scope": ["复制当前可管理范围内的权限"],
  "out_of_scope": ["修改来源账号的权限配置"],
  "hard_constraints": ["单次最多选择 200 个目标账号"],
  "confirmed_decisions": ["复制操作沿用现有权限范围校验"],
  "open_questions": ["部分目标失败时是否允许只重试失败项？"]
}
```

## 7. 错误示例

以下结构必须校验失败，因为保留了旧版业务对象：

```json
{
  "skill": "uxb",
  "version": "4.0",
  "roles": [
    {
      "name": "子管理员",
      "responsibility": "发起权限复制"
    }
  ],
  "rules": [
    {
      "condition": "提交时",
      "requirement": "最多 200 人"
    }
  ]
}
```

## 8. 校验

写盘后必须运行：

```bash
node .claude/skills/uxb/scripts/validate-context.js spark-output/context/uxb.json
```

退出码非 `0` 时只修正 JSON 结构并重跑；不得反向修改已冻结的 Markdown，校验未通过不得进入 Handoff。
