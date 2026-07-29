# PRD Review Context JSON

## 1. 适用范围

Context JSON 只结构化冻结后的正式需求基线，不结构化问题单或 Handoff 建议。

输出路径：

- `spark-output/context/requirements-baseline.json`

Markdown 是唯一正式语义源。JSON 是给下游稳定读取的结构化投影。

## 2. 根字段顺序

1. `schema_version`
2. `project_name`
3. `baseline_status`
4. `source_trace`
5. `goal_and_scope`
6. `business_objects`
7. `roles_and_permissions`
8. `functions_and_task_closure`
9. `business_rules`
10. `states_and_transitions`
11. `exceptions_and_business_results`
12. `data_system_and_audit`
13. `constraints_and_out_of_scope`
14. `acceptance_criteria`

不得增加 `recommendation`、`next_step`、`uxb`、`blueprint` 等流程推荐字段。

## 3. 根结构

```json
{
  "schema_version": "1.0",
  "project_name": "项目名",
  "baseline_status": "formal",
  "source_trace": {
    "prd": [],
    "formal_knowledge": [],
    "product_responses": []
  },
  "goal_and_scope": {
    "business_problem": [],
    "goals": [],
    "in_scope": [],
    "out_of_scope": [],
    "success_results": []
  },
  "business_objects": [],
  "roles_and_permissions": [],
  "functions_and_task_closure": [],
  "business_rules": [],
  "states_and_transitions": [],
  "exceptions_and_business_results": [],
  "data_system_and_audit": {
    "data_changes": [],
    "system_impacts": [],
    "synchronization_and_failures": [],
    "audit_facts": [],
    "historical_data": []
  },
  "constraints_and_out_of_scope": {
    "business_constraints": [],
    "dependencies": [],
    "explicitly_out_of_scope": [],
    "future_considerations": []
  },
  "acceptance_criteria": []
}
```

## 4. 通用来源结构

需要追溯的对象使用：

```json
{
  "type": "prd",
  "reference": "文件名或问题编号",
  "location": "章节或段落"
}
```

`type` 只允许：

- `prd`
- `formal_knowledge`
- `product_response`

`source_trace` 中：

- `prd` 和 `formal_knowledge` 是来源对象数组。
- `product_responses` 是 `Q-001` 格式的问题编号数组。

## 5. 业务对象

```json
{
  "id": "BO-001",
  "name": "业务对象名",
  "definition": "对象定义",
  "relations": [],
  "entry_conditions": [],
  "exclusion_conditions": [],
  "change_type": "keep",
  "sources": []
}
```

`change_type` 只允许：

- `keep`
- `add`
- `modify`
- `remove`

## 6. 角色与权限

```json
{
  "id": "RP-001",
  "role": "角色名",
  "responsibilities": [],
  "allowed_actions": [],
  "permission_prerequisites": [],
  "business_scope": [],
  "forbidden_actions": [],
  "sources": []
}
```

## 7. 功能与任务闭环

```json
{
  "id": "FN-001",
  "name": "功能名",
  "actor": "执行角色",
  "trigger_conditions": [],
  "main_steps": [],
  "success_results": [],
  "failure_or_rejection_results": [],
  "next_business_nodes": [],
  "sources": []
}
```

## 8. 业务规则

```json
{
  "id": "BR-001",
  "name": "规则名",
  "applicable_objects": [],
  "trigger_conditions": [],
  "decision_conditions": [],
  "business_results": [],
  "priority_or_exclusion": [],
  "sources": []
}
```

## 9. 状态与流转

```json
{
  "id": "ST-001",
  "business_object": "业务对象名",
  "state": "状态名",
  "meaning": "状态含义",
  "entry_conditions": [],
  "allowed_actions": [],
  "forbidden_actions": [],
  "next_states": [],
  "irreversible": false,
  "sources": []
}
```

## 10. 异常与业务结果

```json
{
  "id": "EX-001",
  "scenario": "异常或边界场景",
  "trigger_conditions": [],
  "business_decision": "业务判定",
  "task_result": "任务结果",
  "object_state_result": "对象状态结果",
  "retry_or_recovery": "重试或恢复规则",
  "responsible_party": "责任方；无明确责任方时为空字符串",
  "sources": []
}
```

## 11. 验收条件

```json
{
  "id": "AC-001",
  "related_ids": ["FN-001"],
  "preconditions": [],
  "observable_results": [],
  "sources": []
}
```

## 12. 数组项规则

- 事实列表使用字符串数组。
- 字符串不能为空。
- 对象数组按 Markdown 出现顺序投影。
- `id` 在所属数组内唯一。
- `related_ids` 只能引用基线中已有的稳定编号。
- Markdown 写“本期无”或“不适用”时，对应 JSON 数组使用空数组。
- 不用 `null` 表示缺失事实。

## 13. 投影规则

- Markdown 是正式语义源。
- JSON 不复制问题单。
- JSON 不包含 Handoff 建议。
- JSON 不补充 Markdown 中没有的事实。
- JSON 不进行二次业务推理。
- JSON 与 Markdown 的事实顺序保持一致。
- JSON 生成后，由 Agent 逐节对照 Markdown。

## 14. 结构校验边界

脚本只校验 JSON 解析、字段存在、字段类型、格式和枚举，不判断业务语义。

脚本可以校验：

- 根字段是否存在。
- 未知根字段。
- 对象和数组类型。
- 稳定编号格式与数组内唯一性。
- 枚举值。
- 来源结构。
- `related_ids` 是否引用已存在编号。

脚本不得校验：

- 需求是否完整。
- 问题是否关闭。
- 业务结论是否正确。
- 文本中是否含“待确认”等词。
- 是否应该进入 UXB。
