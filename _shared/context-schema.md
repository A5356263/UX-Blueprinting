# Context JSON 字段规范

> 每个 Skill 完成后，将结构化数据写入 `spark-output/context/{skill_id}.json`。
> 下游 Skill 通过读取上游 JSON 获取结构化上下文，避免解析长文本。

## 固定字段（所有 Skill 必须包含）

| 字段 | 类型 | 说明 |
|------|------|------|
| `skill` | string | 当前 Skill 的 ID |
| `version` | string | 输出版本号（如 "V1"） |
| `generated_at` | string | ISO 8601 时间戳 |
| `project_name` | string | 当前项目/需求名称 |

## 业务字段（由各 Skill 自定义）

各 Skill 根据自身输出内容定义业务字段。原则：

- 数组类数据用 JSON array，不用自然语言描述
- 每条数据有明确的 key，方便下游按字段读取
- 不复制 SKILL.md 的 prompt 指令，只存分析结果
- 保留来源引用（如 knowledge 文件路径），便于溯源

## UXB 输出字段

`spark-output/context/uxb.json` 应包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| `product_summary` | string | 产品定位一句话 |
| `goals` | object | `{ business: string[], product: string[] }` |
| `target_users` | array | 角色列表，含业务定义和能力边界 |
| `features` | array | 功能单元列表（name, description, priority, user_role, input, output, result） |
| `constraints` | array | 硬约束列表 |
| `out_of_scope` | array | 明确排除项 |
| `design_implications` | array | 设计 implications（含依据来源） |
| `gaps` | array | 待确认问题（field, why_needed, impact_level, suggested_action） |
| `experience_risks` | array | 体验风险（risk_id, description, mitigation） |
| `applicable_design_principles` | array | 适用设计准则（code, name, application） |

## Experience Blueprint 输出字段

`spark-output/context/experience_blueprint.json` 应包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| `journey` | array | 旅程节点（role, nodes[]） |
| `interaction_overview` | array | 分角色交互流程节点 |
| `main_flow` | array | 主流程节点详细定义 |
| `sub_flows` | array | 次交互流程 |
| `exceptions` | array | 异常与阻断流程 |
| `pages` | array | 页面/弹窗/抽屉设计 |
| `states` | array | 状态与反馈文案 |

## 写入时机

- Skill 完成最终输出时，同步写入对应的 context JSON
- 写入失败不阻断 Skill 完成，但应在输出中提示

## 读取时机

- 下游 Skill 启动时，优先读取上游 context JSON
- 如 JSON 不存在，回退读取上游 MD 文档
