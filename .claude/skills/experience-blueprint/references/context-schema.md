# Experience Blueprint Context JSON Schema

## 1. 定位与版本

- 产物：`spark-output/context/experience-blueprint.json`
- `skill`：固定为 `experience-blueprint`
- `version`：固定为 `2.0`
- `experience_blueprint.md` 是完整体验设计方案；本 JSON 仅是下游定位流程、载体、状态和异常的结构索引。
- 本 JSON 禁止承担泳道、图节点、关系边、坐标或覆盖清单。

## 2. 完整结构

```json
{
  "skill": "experience-blueprint",
  "version": "2.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/experience_blueprint.md",
  "source_refs": [],
  "source_status": {
    "source_mode": "uxb-mode",
    "expansion_mode": "full",
    "usable": true,
    "missing_inputs": []
  },
  "critical_design_judgments": [
    {
      "judgment_id": "judgment-example",
      "judgment": "示例判断",
      "decision": "示例设计决策",
      "open_question": "unknown",
      "source_anchor": "§0"
    }
  ],
  "main_flow": [
    {
      "node_id": "node-example",
      "node_name": "示例节点",
      "user_action": "示例用户动作",
      "system_feedback": "示例系统反馈",
      "state_change": "示例状态变化",
      "next_step": "明确结果",
      "source_anchor": "§3"
    }
  ],
  "sub_flows": [
    {
      "flow_id": "flow-example",
      "flow_name": "示例次流程",
      "trigger_condition": "示例触发条件",
      "user_action": "示例动作",
      "system_feedback": "示例反馈",
      "next_step": "示例下一步",
      "end_type": "return",
      "end_target": "node-example",
      "source_anchor": "§4"
    }
  ],
  "exceptions": [
    {
      "exception_id": "exception-example",
      "name": "示例异常",
      "timing": "示例发生时机",
      "trigger_condition": "示例触发条件",
      "system_feedback": "示例系统反馈",
      "user_next_step": "示例用户下一步",
      "recovery_path": "示例恢复路径",
      "end_type": "return",
      "end_target": "node-example",
      "source_anchor": "§5"
    }
  ],
  "surfaces": {
    "pages": [
      {
        "surface_id": "page-example",
        "name": "示例页面",
        "goal": "示例目标",
        "entry_condition": "示例入口条件",
        "md_anchor": "§6"
      }
    ],
    "modals": [],
    "drawers": []
  },
  "states": [
    {
      "state_id": "state-example",
      "state": "示例状态",
      "meaning": "示例含义",
      "applies_to": ["node-example"],
      "user_action_available": "示例可用动作",
      "feedback_standard": "示例反馈标准",
      "source_anchor": "§7"
    }
  ],
  "open_questions": [
    {
      "question_id": "question-example",
      "question": "示例问题",
      "impact": "示例影响",
      "owner": "示例确认方",
      "source_anchor": "§8"
    }
  ]
}
```

## 3. 字段来源与约束

- `source_status.source_mode` 只允许 `uxb-mode`、`framing-mode`、`deepened-mode`、`unknown`。
- `source_status.expansion_mode` 只允许 `full`、`limited`、`unknown`。
- `source_status.usable` 必须是布尔值。
- 所有 `*_id` 必须非空，并在对应集合中唯一。
- `main_flow` 必须保留用户动作、系统反馈、状态变化和明确下一步；完整蓝图不得为空。
- `sub_flows.end_type` 只允许 `return`、`result`、`terminate`、`unknown`。
- `exceptions.end_type` 只允许 `return`、`terminate`、`unknown`。
- `end_type=return` 时，`end_target` 必须指向真实主流程节点名称或 `node_id`。
- `end_type=terminate` 时，`end_target` 必须写明确终止结果。
- `surfaces.pages/modals/drawers` 不得合并；每个 `surface_id` 在三类载体的并集中唯一。
- `md_anchor`、`source_anchor` 必须指向正式 Markdown 中真实存在的章节或标题。
- `states.applies_to` 只写真实节点、流程、异常或载体 ID；无法确定时使用空数组，不得猜测。

## 4. 禁止写入

禁止写入 ASCII 结构图、区域、按钮、长文案、知识消费过程、完整上游映射，以及 `lanes`、`nodes`、`edges`、坐标、连线、`coverage_manifest`。

## 5. 最小错误示例

以下结构必须失败，因为主流程为空、版本错误且出现图模型字段：

```json
{
  "skill": "experience-blueprint",
  "version": "1.0",
  "artifact_md": "spark-output/experience_blueprint.md",
  "main_flow": [],
  "lanes": []
}
```

## 6. 校验

```bash
node .claude/skills/experience-blueprint/scripts/validate-context.js spark-output/context/experience-blueprint.json
```

退出码非 `0` 时必须修复并重跑。
