# 完整性校验规则

## 目录

1. 四层对账
2. 模型约束
3. 覆盖约束
4. 流程约束
5. HTML 约束
6. 完成门禁

## 1. 四层对账

必须对账：

```text
正式 MD + JSON
→ source_inventory
→ diagram_model + coverage_manifest
→ HTML 内嵌 SVG DOM
```

源清单负责证明输入没有被静默跳读；覆盖清单负责证明每个源项有处置；图模型负责表达业务语义；SVG DOM 负责证明渲染没有丢元素。

## 2. 模型约束

- 所有 ID 非空且在各自集合内唯一。
- 每个节点引用存在的泳道。
- 每条关系引用存在的来源和目标节点。
- 每个模型元素至少包含一个有效 `source_item_id`。
- `certainty` 只允许 `confirmed`；不确定内容进入开放问题或阻断。
- 必须至少有一条主流程，且只有一条默认流程。

## 3. 覆盖约束

- 源清单中的每个 ID 在覆盖清单中恰好出现一次。
- 覆盖清单不得引用不存在的源项。
- `required_in_diagram=true` 时只允许 `rendered` 或 `merged`。
- `rendered`、`merged` 必须映射至少一个与 `semantic_kind` 对应的真实元素。
- `excluded_by_rule` 必须使用允许的稳定 `rule_id`。
- `blocked` 必须为零。
- 覆盖映射与模型的 `source_item_ids[]` 必须双向一致。

集合必须相等：

```text
必画角色源项 == lanes 的来源覆盖
必画节点源项 == nodes 的来源覆盖
必画关系源项 == edges 的来源覆盖
必画流程源项 == flows 的来源覆盖
```

## 4. 流程约束

- `flows[].node_ids[]` 和 `edge_ids[]` 全部存在。
- 流程中的每条边两端都属于该流程。
- 主流程从第一个节点可到达所有主流程节点。
- 主流程至少包含一个 `result` 节点。
- 次流程必须回接主流程或到达 `result`。
- 异常流程必须含 `exception` 或 `return` 边，并回到正常流程或到达 `result`。
- 节点和关系声明的 `flow_ids[]` 必须与流程成员列表双向一致。

## 5. HTML 约束

- HTML 自包含，不存在外部 `script src`、`link href`、远程图片或模块导入。
- 模板占位符全部替换。
- 内嵌源清单、模型和校验摘要可解析。
- 输入哈希和模型哈希一致。
- 模型 lane ID 集合等于 SVG `data-lane-id` 集合。
- 模型 node ID 集合等于 SVG `data-node-id` 集合。
- 模型 edge ID 集合等于 SVG `data-edge-id` 集合。
- 流程筛选按钮覆盖全部流程。
- “全部”按钮位于流程选择区首位。
- HTML 包含“全部”视角的关系流程聚焦能力。
- 导出 SVG 控件存在。

## 6. 完成门禁

以下计数必须全部为零：

```text
blocked_total
unmapped_total
dom_missing_lanes_total
dom_missing_nodes_total
dom_missing_edges_total
dom_extra_lanes_total
dom_extra_nodes_total
dom_extra_edges_total
geometry_overlap_total
geometry_out_of_lane_total
geometry_text_risk_total
geometry_edge_through_node_total
geometry_edge_label_overlap_total
geometry_edge_shared_segment_total
geometry_edge_out_of_bounds_total
geometry_return_margin_total
```

`geometry_edge_shared_segment_total` 只统计没有共同端点的关系；共同起点或终点形成的共线路径属于允许的汇聚。

任何失败都必须返回非零退出码，不得用警告替代失败。
