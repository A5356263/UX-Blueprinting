# Task Card 合同

## 目标

定义 `projects/<project-id>/source/task_card.md` 的正式协议字段、路径约束与解析结果。

## 定位

`task_card.md` 是执行中枢的正式入口协议文件，不是业务判断正文。

## 必填段落

以下一级段落必须存在且可解析：

- `## Protocol`
- `## Task Goal`
- `## Required Inputs`
- `## Required Outputs`
- `## Constraints`
- `## Templates`
- `## Checks`
- `## Result Locations`
- `## Completion Criteria`

以下段落为推荐但可选：

- `## Task Scenario`
- `## Read Order`
- `## Knowledge`
- `## Wiki`
- `## Platform Optimizations`
- `## Notes`

## Protocol 字段

在 `## Protocol` 中，至少必须包含：

- `Protocol Name`
- `Protocol Version`
- `Task ID`

如存在以下字段，应一并解析：

- `Task Name`
- `Domain`

## 路径规则

- 所有路径必须使用仓库相对路径
- 不允许使用绝对路径
- 不允许使用 URL 替代仓库文件路径
- `Required Outputs` 必须全部位于 `projects/<project-id>/workspace/`
- `Result Locations` 必须显式给出 `workspace` 与 `exports` 查看位置

## 知识引用规则

- `Knowledge`、`Wiki`、`Templates`、`Checks` 中的路径必须可逐条提取
- 当存在稳定 Wiki 入口时，优先显式引用 Wiki
- `Platform Optimizations` 只作为增强层信息，不得替代主线输入输出合同

## 解析产物

执行中枢解析后必须生成：

- `projects/<project-id>/runtime/task_card_resolved.json`

最小字段包括：

- `task_id`
- `protocol_name`
- `protocol_version`
- `task_name`
- `domain`
- `required_inputs`
- `required_outputs`
- `knowledge_refs`
- `wiki_refs`
- `template_refs`
- `check_refs`
- `result_locations`
- `completion_criteria`
- `warnings`
- `errors`

## Warning 条件

以下情况可继续执行，但必须记录 warning：

- 缺少 `## Wiki`，但存在 `Knowledge`
- 缺少 `## Read Order`
- `Knowledge` 仅引用目录而未细化到文件或索引页
- `Platform Optimizations` 存在但为空

## 失败条件

- `task_card.md` 缺失
- 任一必填段落缺失
- `Protocol Name`、`Protocol Version`、`Task ID` 缺失
- `Required Outputs` 为空
- 任一输出路径不位于 `projects/<project-id>/workspace/`
- 任一路径段存在但无法解析为路径列表
- `task_card_resolved.json` 未生成
