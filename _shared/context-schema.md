# Context JSON 字段规范

## 固定字段（每个 Skill 的 context JSON 必须包含）

| 字段 | 类型 | 说明 |
|------|------|------|
| `skill` | string | Skill id（如 `uxb`、`experience-blueprint`） |
| `version` | string | 输出格式版本号 |
| `generated_at` | string | ISO 8601 时间戳 |
| `project_name` | string | 项目名称 |

## UXB 输出字段（写入 `spark-output/context/uxb.json`）

| 字段 | 类型 | 说明 |
|------|------|------|
| `product_summary` | string | 一句话结论 |
| `goals` | object | 目标：`{ business: string, product: string }` |
| `target_users` | array | 目标用户列表 |
| `features[]` | array | 功能单元列表，每项含 `id`、`name`、`description`、`priority`（P0/P1）、`roles[]` |
| `constraints[]` | array | 约束列表，每项含 `type`、`description` |
| `states[]` | array | 状态流转列表，每项含 `from`、`to`、`trigger`、`user_action` |
| `exceptions[]` | array | 异常列表，每项含 `name`、`trigger`、`handling` |
| `gaps[]` | array | 待确认问题列表，每项含 `question`、`tier`（1 或 2）、`impact` |
| `experience_risks[]` | array | 体验风险列表，每项含 `risk`、`strategy`、`principle_ref` |
| `applicable_design_principles[]` | array | 适用设计准则列表，每项含 `id`、`name`、`application` |

## 体验蓝图输出字段（写入 `spark-output/context/experience-blueprint.json`）

| 字段 | 类型 | 说明 |
|------|------|------|
| `journey[]` | array | 旅程图，每项含 `role`、`nodes[]`（节点名称数组） |
| `interaction_overview` | object | 交互总览：`{ roles_flow: string, exception_highlights: string[] }` |
| `main_flow[]` | array | 主流程节点列表，每项含 `id`、`name`、`user_action`、`system_feedback`、`next` |
| `sub_flows[]` | array | 次流程列表 |
| `exceptions[]` | array | 异常流程列表 |
| `pages[]` | array | 页面设计列表 |
| `states[]` | array | 状态文案表 |

## 规则

1. 数组型数据用 JSON 数组，不用自然语言罗列。
2. 每条数据有显式 key，便于下游按字段精确读取。
3. 不复制 SKILL.md 中的 prompt 指令，只存分析结果。
4. 写入路径使用 `spark-output/context/{skill-id}.json`。文件名保留 Skill id 原文，不把连字符改成下划线，例如 `uxb.json`、`experience-blueprint.json`。
