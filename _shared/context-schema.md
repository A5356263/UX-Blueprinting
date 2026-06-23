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
| `input_summary` | object | 输入摘要，含 `background`、`target_users[]`、`business_goals`、`product_goals`、`features_in_scope[]`、`explicit_constraints[]`、`prd_gaps[]` |
| `business_scenario_judgment` | object | 业务场景判断，含 `position`、`relationship_to_existing`、`governance_mode_change`、`max_uncertainty`、`impact_if_wrong` |
| `viability_judgment` | object | 可行性判断，含 `viable`、`benefits[]`、`costs[]`、`alternatives[]`、`recommendation` |
| `business_boundary` | object | 业务边界，含 `recommended[]`、`not_recommended[]`、`reuse[]`、`no_new[]`、`new[]` |
| `roles[]` | array | 角色列表，每项含 `id`、`name`、`responsibilities[]` |
| `features[]` | array | 功能单元列表，每项含 `id`、`name`、`description`、`priority`、`roles[]` |
| `business_rules[]` | array | 业务规则列表，每项含 `id`、`name`、`trigger`、`result`、`fallback` |
| `states[]` | array | 状态流转列表，每项含 `from`、`to`、`trigger` |
| `exceptions[]` | array | 异常列表，每项含 `name`、`trigger`、`handling`、`user_next` |
| `experience_handoff_requirements[]` | array | 体验交接要求，每项含 `business_judgment`、`experience_impact`、`must_handle`、`no_rejudge` |
| `gaps[]` | array | 待确认问题列表，每项含 `id`、`question`、`tier`、`impact` |
| `knowledge_trace[]` | array | 知识消费追踪，每项含 `file`、`used_for` |

## 体验蓝图输出字段（写入 `spark-output/context/experience-blueprint.json`）

| 字段 | 类型 | 说明 |
|------|------|------|
| `uxb_mapping[]` | array | UXB 判断映射，每项含 `uxb_judgment`、`experience_impact`、`design_decision`、`landing_sections[]` |
| `journey[]` | array | 旅程图，每项含 `role`；`nodes[]` 为对象数组，每个节点含 `stage`、`goal`、`touchpoint`、`confidence`、`pain` |
| `interaction_overview` | object | 交互总览：`roles_flow`（string）、`exception_highlights`（string[]） |
| `main_flow[]` | array | 主流程，每项含 `name`、`role`；`nodes[]` 为对象数组，每个节点含 `name`、`user_action`、`system_feedback`、`next` |
| `sub_flows[]` | array | 次流程列表，每项含 `name`、`trigger`、`role` |
| `exceptions[]` | array | 异常流程列表，每项含 `name`、`trigger`、`feedback_form`、`user_next` |
| `pages[]` | array | 页面设计列表，每项含 `id`、`name`、`role`、`goal` |
| `states[]` | array | 状态文案表，每项含 `state`、`meaning`、`audience`、`user_action`、`feedback` |
| `open_questions[]` | array | 待确认问题，每项含 `id`、`question`、`tier`、`assumption`（可选）、`affected_sections` |

## 规则

1. 数组型数据用 JSON 数组，不用自然语言罗列。
2. 每条数据有显式 key，便于下游按字段精确读取。
3. 不复制 SKILL.md 中的 prompt 指令，只存分析结果。
4. 写入路径使用 `spark-output/context/{skill-id}.json`。文件名保留 Skill id 原文，不把连字符改成下划线，例如 `uxb.json`、`experience-blueprint.json`。
