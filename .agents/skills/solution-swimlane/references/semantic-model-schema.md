# 最小语义草稿与规范模型

Agent 只写草稿 1.1。`normalize-semantic-model.js` 把草稿确定性转换为语义模型 2.0。Agent 不得直接手写语义模型 2.0。

## 草稿 1.1

### 顶层

```json
{
  "draft_version": "1.1",
  "title": "方案协同图标题",
  "scope": "本图覆盖的业务范围",
  "start_condition": "流程开始条件",
  "end_conditions": ["成功完成", "明确终止"],
  "lanes": [],
  "nodes": [],
  "edges": [],
  "flows": [],
  "open_questions": []
}
```

所有顶层字段必填。`end_conditions` 至少一项；`lanes`、`nodes`、`flows` 非空。未知字段直接失败。

### 泳道 `lanes`

```json
{
  "id": "employee",
  "name": "员工",
  "type": "human",
  "order": 1,
  "responsibility": "发起并跟踪权限申请"
}
```

- `type`：`human`、`team`、`system`
- `order`：从上到下的整数顺序
- `source_refs`：禁止写入；规范模型固定补为 `[]`

### 节点 `nodes`

```json
{
  "id": "submit-request",
  "lane_id": "employee",
  "label": "提交权限申请",
  "type": "action",
  "summary": "选择权限并填写申请原因"
}
```

- `type`：`start`、`action`、`system_process`、`decision`、`result`、`end`、`pending`
- `summary`：可选；没有补充信息时省略，脚本逐字复制 `label`
- `certainty`：可选；省略时补为 `confirmed`，原文无法确认时写 `uncertain`
- `source_refs`、`flow_ids`：禁止写入

主流程首节点必须是 `start`，末节点必须是 `end`。

### 关系 `edges`

```json
{
  "id": "submit-to-check",
  "from": "submit-request",
  "to": "check-request",
  "label": "提交后",
  "type": "handoff"
}
```

- `type`：`normal`、`conditional`、`handoff`、`exception`、`return`、`terminate`
- `conditional` 必须有明确条件标签
- `from`、`to` 必须引用现有节点
- `certainty`：可选；省略时补为 `confirmed`，原文无法确认时写 `uncertain`
- `source_refs`、`flow_ids`：禁止写入

### 流程 `flows`

```json
{
  "id": "main",
  "name": "主流程",
  "type": "main",
  "edge_ids": ["start-submit", "submit-check", "check-done"]
}
```

- `type`：`main`、`secondary`、`exception`
- 必须且只能有一条 `main`
- `edge_ids` 至少一项，按实际行进顺序排列
- 下一条关系的 `from` 必须等于上一条关系的 `to`
- `node_ids`、`default_visible`：禁止写入
- 脚本从有序 `edge_ids` 推导 `node_ids`
- 次流程和异常流程的最后节点必须为 `pending`、`result`、`end`，或最后关系为 `return`、`terminate`
- 只有主流程创建显式 `start` 和 `end`；其他流程复用真实触发与出口节点

正确：

```text
e1: A → B
e2: B → C
生成 node_ids: [A, B, C]
```

错误：

```text
e1: A → B
e2: C → D
```

脚本报告关系不连续，不得排序或补充 `B → C`。

### 待确认项 `open_questions`

```json
{
  "id": "question-timeout",
  "question": "审批超时后是否自动终止？",
  "impact": "影响异常流程出口",
  "related_element_ids": ["approval-timeout"],
  "fallback": "使用 pending 节点表达"
}
```

`related_element_ids` 可引用泳道、节点、关系或流程。待确认项非空不构成校验失败。

### 草稿禁止字段

以下旧字段在任何层级均禁止：

```text
coverage_manifest
coverage_rules
source_inventory
source_item_ids
source_selectors
```

泳道、节点和关系额外禁止 `source_refs`；节点和关系禁止 `flow_ids`；流程禁止 `node_ids` 和 `default_visible`。任何未定义字段均直接失败。

## 规范模型 2.0

脚本输出以下顶层结构：

```json
{
  "schema_version": "2.0",
  "title": "方案协同图标题",
  "scope": "本图覆盖的业务范围",
  "start_condition": "流程开始条件",
  "end_conditions": ["成功完成", "明确终止"],
  "lanes": [],
  "nodes": [],
  "edges": [],
  "flows": [],
  "open_questions": []
}
```

相对于草稿，脚本只增加：

- 所有泳道、节点、关系缺失的 `source_refs: []`
- 节点缺失的 `summary`，逐字复制 `label`
- 所有节点、关系缺失的 `certainty: "confirmed"`
- 流程根据有序 `edge_ids` 生成的 `node_ids`
- 节点、关系根据流程反向生成的 `flow_ids`
- `main` 的 `default_visible: true` 与其他流程的 `default_visible: false`

脚本不得新增、删除、合并、重排或改写业务语义。规范模型必须通过 `validate-semantic-model.js` 后才能写入。
