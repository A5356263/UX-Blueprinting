# UXB Context JSON Schema

## 1. 定位

- 正式产物：`spark-output/context/uxb.json`
- 人类阅读面：`spark-output/uxb_output.md`
- `skill`：固定为 `uxb`
- `version`：固定为 `6.0`

JSON 只结构化已冻结的体验定案，不重复需求基线中的业务事实。

## 2. 生成红线

- 只从已冻结的 `uxb_output.md` 投影。
- 不回读需求基线补充 JSON。
- 不新增 Markdown 没有的体验结论。
- 不包含业务问题、待确认项或候选主方向。
- 不包含页面、组件、布局和最终文案。
- 不包含 Handoff 推荐。

## 3. 固定结构

```json
{
  "skill": "uxb",
  "version": "6.0",
  "generated_at": "2026-07-28T00:00:00+08:00",
  "project_name": "项目名",
  "artifact_md": "spark-output/uxb_output.md",
  "baseline_ref": {
    "artifact_md": "spark-output/requirements_baseline.md",
    "status": "formal"
  },
  "core_experience_decision": {
    "direction": "核心体验方向",
    "primary_tradeoff": "最重要的体验取舍",
    "blueprint_principle": "蓝图必须守住的原则"
  },
  "experience_impact_scope": {
    "tasks": [],
    "role_perspectives": [],
    "key_nodes": [],
    "unaffected_scope": []
  },
  "experience_goals": [],
  "information_architecture_directions": [],
  "interaction_flow_directions": [],
  "node_explanation_strategies": [],
  "information_reading_strategies": [],
  "state_feedback_and_role_continuity": [],
  "experience_tradeoffs": [],
  "blueprint_handoff_requirements": []
}
```

## 4. 体验目标

```json
{
  "id": "EG-001",
  "goal": "体验目标",
  "priority": "P0",
  "pressure": "对应的理解或任务压力",
  "conflict_principle": "目标冲突时的优先原则"
}
```

`priority` 只允许 `P0`、`P1`、`P2`。

## 5. 信息架构方向

```json
{
  "id": "IA-001",
  "scope": "影响的信息范围",
  "direction": "信息组织方向",
  "rationale": "选择理由",
  "stable_relationships": []
}
```

## 6. 交互流程编排方向

```json
{
  "id": "FL-001",
  "task": "任务",
  "direction": "流程编排方向",
  "sequence_principles": [],
  "exception_continuity": "异常结果如何保持任务连续"
}
```

## 7. 关键节点解释策略

```json
{
  "id": "NE-001",
  "node": "关键节点",
  "before": [],
  "during": [],
  "after": [],
  "purpose": "解释目的"
}
```

没有对应时机内容时使用空数组，不写 `unknown`。

## 8. 信息阅读策略

```json
{
  "id": "IR-001",
  "scope": "信息范围",
  "reading_order": [],
  "clarity_principles": [],
  "concept_distinctions": []
}
```

## 9. 状态反馈与连续性

```json
{
  "id": "SF-001",
  "scenario": "业务结果或连续性场景",
  "feedback_strategy": "反馈方向",
  "action_understanding": "用户应形成的下一步认知",
  "role_continuity": "多角色连续性；不适用时为空字符串",
  "cross_node_or_channel_continuity": "跨节点或跨端连续性；不适用时为空字符串"
}
```

## 10. 体验取舍

```json
{
  "id": "TD-001",
  "topic": "取舍主题",
  "chosen_direction": "已选方向",
  "rejected_directions": [],
  "reason": "选择理由",
  "impact_scope": []
}
```

## 11. 体验蓝图承接要求

```json
{
  "id": "BH-001",
  "requirement": "必须落实的体验策略",
  "purpose": "体验目的",
  "must_preserve": [],
  "solution_space": "蓝图可以自行设计的方案空间"
}
```

## 12. 结构规则

- 所有根字段必须存在。
- 根字段之外不得新增字段。
- 稳定编号在所属数组内唯一。
- 字符串不能为空；明确允许不适用的字段可使用空字符串。
- 字符串数组不得包含空字符串。
- 没有对应内容时使用空数组，不生成虚假占位对象。
- 数组顺序与 Markdown 对应章节顺序一致。
- 不建立业务角色、权限、规则、状态或异常全集字段。

## 13. 结构校验边界

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

这些只能由 Agent 验收。
