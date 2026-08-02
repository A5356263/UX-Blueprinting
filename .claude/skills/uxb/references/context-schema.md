# UXB Context JSON Schema

## 1. 定位

- 正式产物：`spark-output/context/uxb.json`
- 人类阅读面：`spark-output/uxb_output.md`
- `skill`：固定为 `uxb`
- `version`：固定为 `8.0`

JSON 只结构化已冻结的体验定案，不重复需求基线中的业务事实。

## 2. 生成红线

- 只从已冻结的 `uxb_output.md` 投影。
- 不回读需求基线补充 JSON。
- 不新增 Markdown 没有的体验结论。
- 不包含业务问题、待确认项或候选主方向。
- 不包含页面、组件、布局和最终文案。
- 不包含 Handoff 推荐。
- 不使用基线编号、章节号、行号或固定位置建立跨文件关联。
- `id` 只用于 UXB 单个集合内的稳定识别，不得作为下游绑定键。

## 3. 固定结构

```json
{
  "skill": "uxb",
  "version": "8.0",
  "generated_at": "2026-07-28T00:00:00+08:00",
  "project_name": "项目名",
  "artifact_md": "spark-output/uxb_output.md",
  "experience_scope": {
    "tasks": [],
    "roles": [],
    "business_objects": [],
    "key_nodes": [],
    "relevant_states": [],
    "relevant_results": [],
    "unaffected_scope": []
  },
  "task_experience_decisions": [],
  "cross_stage_decisions": [],
  "state_recovery_decisions": [],
  "blueprint_requirements": [],
  "upstream_trace": []
}
```

## 4. 任务体验定案

```json
{
  "id": "TE-001",
  "task": "需求基线中的具体任务",
  "roles": ["涉及角色"],
  "business_objects": ["相关业务对象"],
  "business_nodes": ["该阶段承接的业务节点"],
  "perceived_stage": "用户感知阶段",
  "orchestration_actions": ["merge"],
  "orchestration_reason": "为什么这样编排",
  "experience_breakpoint": "需要解决的具体体验问题",
  "user_must_understand": ["用户必须理解的内容"],
  "experience_decision": "唯一体验决定",
  "information_order": ["用户理解信息的顺序"],
  "explanation_timing": {
    "before": ["操作前需要解释的内容"],
    "during": ["操作中需要反馈的内容"],
    "after": ["操作后需要说明的内容"]
  },
  "state_result_requirements": ["状态和结果要求"],
  "continuity_requirements": ["角色或系统连续性要求"],
  "blueprint_requirements": ["蓝图必须落实的要求"]
}
```

必填字段：

- `id`
- `task`
- `roles`
- `business_objects`
- `business_nodes`
- `perceived_stage`
- `orchestration_actions`
- `orchestration_reason`
- `experience_breakpoint`
- `user_must_understand`
- `experience_decision`
- `blueprint_requirements`

必填数组不得为空。

`orchestration_actions` 只允许：

- `retain`
- `merge`
- `split`
- `reorder`

可选字段：

- `information_order`
- `explanation_timing`
- `state_result_requirements`
- `continuity_requirements`

可选字段没有真实内容时省略。不得使用空字符串、空数组或占位语句。

`explanation_timing` 只允许 `before`、`during`、`after`。没有内容的时机字段省略。

## 5. 跨阶段衔接

```json
{
  "id": "CS-001",
  "task": "对应任务",
  "from_stage": "上一用户感知阶段",
  "to_stage": "下一用户感知阶段",
  "transition_trigger": "阶段转换条件",
  "context_to_preserve": ["必须保留的任务对象和上下文"],
  "transition_decision": "唯一衔接决定",
  "blueprint_requirements": ["蓝图必须落实的要求"]
}
```

以上字段全部必填。数组不得为空。

## 6. 状态与恢复

```json
{
  "id": "SR-001",
  "task": "对应任务",
  "business_states": ["需求基线中的业务状态"],
  "user_visible_meaning": "用户需要理解的状态或结果含义",
  "result_or_next_action": "结果或下一步",
  "experience_decision": "唯一状态或恢复决定",
  "blueprint_requirements": ["蓝图必须落实的要求"]
}
```

以上字段全部必填。数组不得为空。

UXB 可以简化用户感知状态，但不得把不同业务结果错误合并。

## 7. Experience Blueprint 落实要求

```json
{
  "id": "BR-001",
  "task": "落实要求对应的任务",
  "roles": ["涉及角色"],
  "perceived_stage": "对应用户感知阶段",
  "requirement": "必须落实的体验要求",
  "purpose": "用户需要获得的体验结果",
  "must_preserve": ["必须保持的信息、顺序、衔接、反馈或连续性"]
}
```

必填字段：

- `id`
- `task`
- `roles`
- `perceived_stage`
- `requirement`
- `purpose`
- `must_preserve`

必填数组不得为空。

## 8. 来源追溯

`upstream_trace` 使用编号前缀 `UT`。

```json
{
  "id": "UT-001",
  "source_type": "requirements_baseline",
  "source_name": "正式需求基线",
  "status": "formal",
  "source_path": "spark-output/requirements_baseline.md",
  "used_for": ["本次体验定案的用途"]
}
```

`source_type` 只允许：

- `requirements_baseline`
- `business_knowledge`
- `design_guideline`
- `interaction_pattern`

`status` 固定为 `formal`。`source_path` 可省略，只用于来源追溯，不能用于关联某条体验定案。

## 9. 有体验压力与无体验压力

存在真实体验压力时，Agent 必须确认：

- `task_experience_decisions` 非空。
- `blueprint_requirements` 非空。

没有真实体验压力时，Agent 必须确认：

- `task_experience_decisions` 为空。
- `cross_stage_decisions` 为空。
- `state_recovery_decisions` 为空。
- `blueprint_requirements` 只保留“忠实落实需求基线”的要求。

这是语义规则，只能由 Agent 验收，脚本不得推断。

## 10. 结构规则

- 所有根字段必须存在。
- 根字段之外不得新增字段。
- 稳定编号在所属数组内唯一。
- 字符串不能为空。
- 字符串数组不得包含空字符串。
- 没有对应内容时使用空数组，不生成虚假占位对象。
- 数组顺序与 Markdown 对应章节顺序一致。
- 不建立业务角色、权限、规则、状态或异常全集字段。
- 不建立需求基线外键。
- Markdown 与 JSON 通过任务、角色、业务对象、状态和结果的自然语义保持对应。
- 角色、任务、对象和状态名称沿用需求基线。
- 使用用户表达时，必须同时保留对应业务节点。
- 不保存未选择方向、候选方案或内部比较过程。

## 11. 结构校验边界

脚本可以校验：

- JSON 解析。
- 字段存在和未知字段。
- 类型。
- 固定值和枚举。
- 编号格式与数组内唯一性。

脚本不得校验：

- 体验结论是否合理。
- 体验取舍是否充分。
- 是否越界到页面方案。
- Markdown 与 JSON 是否语义一致。
- 是否应该执行 UXB。
- 是否存在真实体验压力。
- 体验定案是否能改变蓝图方案。
- 与需求基线的自然语义对应是否准确。

这些只能由 Agent 验收。
