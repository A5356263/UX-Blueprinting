# 语义抽取规则

## 目录

1. 抽取目标
2. 泳道
3. 节点
4. 关系
5. 流程
6. 覆盖处置
7. 不确定性
8. 模型结构

## 1. 抽取目标

把体验蓝图转成“角色任务—系统处理—业务结果”图，不复刻页面点击路径。

优先表达：

- 谁负责发起、处理、决策和恢复
- 系统在何处校验、创建、分配、通知和更新状态
- 正常流程如何推进
- 条件如何分支
- 次流程如何回到主线或结束
- 异常从哪里发生，如何恢复或终止

不要继承参考图片中的已有、一期、二期、功能编号、固定角色或固定颜色语义。

## 2. 泳道

为每个对业务推进承担独立责任的角色、团队或系统建立一条横向泳道。

允许：

- `human`：个人或业务角色
- `team`：组织或处理团队
- `system`：系统自动处理方

角色名称必须来自正式蓝图。不要根据页面名称或行业惯例补角色。

同一角色的别名可以归并，但必须把全部来源项写入 `source_item_ids[]`，并在对应覆盖记录中使用 `merged`。

## 3. 节点

节点只允许：

- `action`：角色主动完成的完整任务
- `system_process`：系统自动处理、校验、分配、通知或状态更新
- `decision`：会改变后续路径的条件判断
- `result`：业务结果或明确终止

节点必须是可宣讲的任务粒度。以下内容默认不单独成节点：

- 单次点击、输入、选择
- 页面、弹窗、抽屉名称
- 字段、按钮、Toast、InlineError
- 纯解释文案
- 旅程情绪、风险等级和分析结论

当页面级动作改变跨角色流转时，可以提升为任务节点，例如“提交申请”“审批决定”“关闭模式”。

同一任务同时包含角色动作和系统处理时必须拆开。例如：

```text
员工提交申请 → 系统校验资格 → 系统创建审批记录
```

不要把三者塞进一个节点。

## 4. 关系

每条关系必须具备：

- `from`：存在的来源节点
- `to`：存在的目标节点
- `label`：触发、条件或业务含义
- `edge_type`：`normal`、`conditional`、`return` 或 `exception`
- `source_item_ids[]`：正式蓝图证据

只有以下依据可以建立关系：

- Markdown 明确的箭头、步骤顺序、触发条件、下一步或恢复路径
- Context JSON 的 `next_step`、`trigger_condition`、`recovery_path` 和状态变化
- 同一正式流程块中可验证的先后顺序

禁止：

- 为了让图闭环而补造关系
- 根据页面清单猜调用关系
- 根据行业惯例补审批人、通知方或恢复目标
- 用无标签跨泳道连线掩盖语义不明

如果能确认节点但无法确认关系端点，将相关源项置为 `blocked`，停止正式生成。

## 5. 流程

每个模型必须至少有一条 `main` 流程，并且只能有一条 `default_visible=true`。

- `main`：从触发到主要业务结果的核心跨角色路径
- `secondary`：编辑、查看、撤销、关闭等非核心任务
- `exception`：阻断、失败、超时、拒绝和恢复路径

`flows[].node_ids[]` 按阅读顺序排列。`edge_ids[]` 必须连接该流程中的节点。

异常流程必须满足一种结束方式：

- 通过 `return` 边恢复到正常流程
- 到达 `result` 节点明确终止

不要只画异常提示而不画用户或系统如何恢复。

## 6. 覆盖处置

源清单中的每个 `source_item_id` 必须且只能有一条覆盖记录。

`disposition`：

- `rendered`：直接进入泳道、节点、关系或流程
- `merged`：与同义来源合并，但仍挂接到图元素
- `detail`：进入节点详情、开放问题或说明区
- `excluded_by_rule`：按稳定规则排除
- `blocked`：无法可靠判断

允许的 `rule_id`：

- `MERGE_DUPLICATE_EVIDENCE`
- `DETAIL_NODE_CONTEXT`
- `DETAIL_OPEN_QUESTION`
- `EXCLUDE_PAGE_DETAIL`
- `EXCLUDE_COPY_DETAIL`
- `EXCLUDE_ANALYSIS_ONLY`
- `EXCLUDE_VISUAL_SKETCH`
- `EXCLUDE_NON_SEMANTIC`
- `EXCLUDE_DUPLICATE_CONTAINER`

`required_in_diagram=true` 时只允许 `rendered` 或 `merged`。

以下通常是必画项：

- 正式角色或系统处理方
- 主流程任务、系统处理、条件和结果
- 次流程的触发、关键处理和结束/回接
- 每个异常的发生点、阻断/处理、恢复或终止
- 明确状态变化所对应的业务关系

以下通常进入详情或按规则排除：

- 页面布局和控件说明
- 示例文案
- 设计准则消费记录
- 旅程分析摘要
- 不改变流转的字段校验细节

## 7. 不确定性

开放问题不应伪装成确定节点或普通实线。

- 只影响局部表达：写入 `open_questions[]`，相关源项使用 `detail`。
- 会改变泳道、主流程、关系端点或异常恢复：使用 `blocked`，停止正式生成。
- 蓝图写有“基于推荐方案推进”时，只能表达蓝图已经采用的推荐方案，并在详情区保留对应开放问题。

## 8. 模型结构

草稿模型允许图元素使用 `source_selectors[]`，由 `materialize-coverage.js` 展开并删除。选择器支持：

```json
{
  "source_ref": "精确来源引用",
  "source_ref_prefix": "来源引用前缀",
  "source_file": "来源文件",
  "source_kind": "源项类型",
  "context": "精确 Markdown 标题路径",
  "context_prefix": "Markdown 标题路径前缀",
  "raw_text_equals": "精确原文",
  "raw_text_includes": "原文包含"
}
```

一个选择器可组合多个条件，所有条件同时满足。选择器匹配零项时脚本必须失败。

对没有映射到图元素、但确实只应进入详情或排除的流程源项，使用草稿模型顶层 `coverage_rules[]`：

```json
{
  "selector": {
    "source_ref_prefix": "spark-output/context/experience-blueprint.json#$.main_flow[0].copy_suggestions"
  },
  "semantic_kind": "detail",
  "required_in_diagram": false,
  "disposition": "excluded_by_rule",
  "rule_id": "EXCLUDE_COPY_DETAIL",
  "reason": "提示文案不提升为主图节点"
}
```

`main_flow`、`sub_flows`、`exceptions`、`states` 以及 Markdown `§2-§5` 中未映射、也没有明确覆盖规则的源项会自动变成 `blocked`。不要用宽泛规则一次排除整个流程章节。

```json
{
  "schema_version": "1.0",
  "title": "项目名称 · 方案协同图",
  "subtitle": "一句话说明图的范围",
  "source_hash": "来自 source-inventory.json",
  "lanes": [
    {
      "id": "lane-kebab-id",
      "name": "角色名称",
      "lane_type": "human",
      "order": 1,
      "source_item_ids": []
    }
  ],
  "nodes": [
    {
      "id": "node-kebab-id",
      "lane_id": "lane-kebab-id",
      "label": "任务名称",
      "node_type": "action",
      "summary": "任务与结果摘要",
      "certainty": "confirmed",
      "source_item_ids": [],
      "flow_ids": []
    }
  ],
  "edges": [
    {
      "id": "edge-kebab-id",
      "from": "node-id",
      "to": "node-id",
      "label": "关系含义",
      "edge_type": "normal",
      "certainty": "confirmed",
      "source_item_ids": [],
      "flow_ids": []
    }
  ],
  "flows": [
    {
      "id": "flow-kebab-id",
      "name": "流程名称",
      "flow_type": "main",
      "node_ids": [],
      "edge_ids": [],
      "default_visible": true,
      "source_item_ids": []
    }
  ],
  "open_questions": [
    {
      "id": "question-kebab-id",
      "question": "待确认问题",
      "impact": "影响范围",
      "source_item_ids": []
    }
  ],
  "coverage_manifest": [
    {
      "source_item_id": "source-id",
      "semantic_kind": "lane|node|edge|flow|detail|excluded",
      "required_in_diagram": true,
      "disposition": "rendered",
      "mapped_lane_ids": [],
      "mapped_node_ids": [],
      "mapped_edge_ids": [],
      "mapped_flow_ids": [],
      "rule_id": "",
      "reason": "简短说明"
    }
  ]
}
```
