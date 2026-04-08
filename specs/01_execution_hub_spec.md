# 执行中枢规格

## 目标

定义本项目中“执行中枢”应如何按规则执行任务步骤。

本规格面向执行中枢，而不是面向业务推理本身。

执行中枢负责：

- 按规则推进步骤
- 校验输入输出
- 显式暴露失败
- 把结果写入稳定位置

执行中枢不负责：

- 替代业务判断
- 替代体验推导
- 自行发明知识结论

## 定位

执行中枢是本项目中承接固定逻辑的轻量执行层。

它可以由以下任一实现承载：

- 本地脚本
- 包装后的 package
- 后续的 command / hook / policy plugin
- 其他 AI 工具中的自动化入口

只要实现遵守本规格，即视为等价执行中枢。

## 上位依赖

执行中枢必须受以下上位文档约束：

- `specs/03_task_card_contract.md`
- `specs/04_knowledge_reference_contract.md`
- `specs/05_output_contract.md`
- `specs/06_check_contract.md`
- `specs/07_wiki_contract.md`
- `specs/08_fact_extraction_contract.md`
- `specs/09_business_blueprint_contract.md`
- `specs/10_experience_blueprint_contract.md`

其中：

- `docs/sdd/` 只负责解释项目主线与整体理解
- 本文件负责说明执行中枢每一步如何执法

## 执行对象

执行中枢按单个任务执行。

标准项目目录：

```text
projects/<project-id>/
  source/
  workspace/
  runtime/
  exports/
```

## 统一状态模型

执行中枢在任何步骤中都应使用以下最小状态语义：

- `pending`：未开始
- `running`：执行中
- `passed`：执行完成且符合规格
- `warning`：执行完成但存在警告
- `failed`：执行失败，存在 blocker

## 统一失败原则

执行中枢必须遵守：

- 失败不得静默吞掉
- 缺少必需输入时必须显式报错
- 生成结果不完整时必须显式报错
- 允许 warning，但 warning 不能伪装成 passed

## Step 1: Task Bootstrap

### 目标

创建任务工作区，并保证任务目录具有最小结构。

### 输入

- `task_id`
- 可选：`task_name`
- 可选：`domain`

### 输出

- `projects/<project-id>/source/task_card.md`
- `projects/<project-id>/source/requirement.md`
- `projects/<project-id>/source/background.md`
- `projects/<project-id>/source/attachments/`
- `projects/<project-id>/workspace/`
- `projects/<project-id>/runtime/context_bundle/`
- `projects/<project-id>/runtime/run_logs/`
- `projects/<project-id>/runtime/snapshots/`

### 成功条件

- 标准目录全部存在
- `task_card.md` 已生成
- 输入占位文件已生成

### 失败条件

- 目录未创建完整
- 模板渲染失败
- 输出文件缺失

## Step 2: Task Card Resolve

### 目标

把 `task_card.md` 解析为可执法的任务协议，并生成标准化解析结果。

### 输入

- `projects/<project-id>/source/task_card.md`

### 强制协议段

以下段落必须存在且可解析：

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

### 必填协议字段

在 `## Protocol` 中，至少必须解析出：

- `Protocol Name`
- `Protocol Version`
- `Task ID`

如果存在 `Task Name` 与 `Domain`，应一并解析。

### 路径解析规则

- 所有路径必须是仓库相对路径
- 不允许使用绝对路径
- 不允许使用 URL 替代仓库文件路径
- `Required Outputs` 必须全部落在 `projects/<project-id>/workspace/`
- `Result Locations` 必须显式给出 `workspace` 查看位置与最终归档位置
- `Knowledge`、`Wiki`、`Templates`、`Checks` 中的路径必须可被逐条提取

### 解析产物

执行中枢完成本步骤后，必须生成：

- `projects/<project-id>/runtime/task_card_resolved.json`

该文件至少应包含：

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

### 执法顺序

1. 读取并识别所有一级协议段
2. 校验强制协议段是否缺失
3. 解析 `## Protocol` 中的键值
4. 解析 `Required Inputs` 与 `Required Outputs`
5. 解析 `Knowledge`、`Wiki`、`Templates`、`Checks`
6. 校验输出路径是否位于当前任务 `workspace/`
7. 生成 `task_card_resolved.json`
8. 若存在 blocker，则本步骤状态为 `failed`

### 成功条件

- 强制协议段齐全
- 必填协议字段齐全
- 引用路径能够被逐条提取
- 输出路径符合 `workspace/` 约束
- `task_card_resolved.json` 已生成

### Warning 条件

满足以下情况时，可继续执行，但必须记录 warning：

- 缺少 `## Wiki`，但存在 `Knowledge`
- 缺少 `## Read Order`
- `Knowledge` 仅引用目录而未细化到文件或索引页
- `Platform Optimizations` 存在但为空

### 失败条件

- `task_card.md` 缺失
- 任一强制协议段缺失
- `Protocol Name`、`Protocol Version`、`Task ID` 缺失
- `Required Outputs` 为空
- 任一输出路径不位于 `projects/<project-id>/workspace/`
- 任一引用段存在但无法解析为路径列表
- `task_card_resolved.json` 未生成

## Step 3: Context Assembly

### 目标

根据 `task_card.md` 的显式引用，组装最小上下文快照。

### 输入

- `task_card.md`
- `task_card_resolved.json`
- 仓库内显式引用路径

### 输出

- `projects/<project-id>/runtime/context_bundle/`
- `projects/<project-id>/runtime/context_manifest.json`

### 成功条件

- 所有显式引用路径均被解析
- 可复制引用被写入 `context_bundle`
- `context_manifest.json` 正常生成

### 失败条件

- 引用路径不存在
- 引用无法复制
- manifest 未生成

## Step 4: Fact Extraction

### 目标

从输入材料中提炼 `facts.md`。

### 输入

- `task_card.md`
- `inputs/requirement.md`
- `inputs/background.md`
- 必要附件

### 输出

- `workspace/facts.md`
- 必要时 `workspace/gap_list.md`

### 成功条件

- `facts.md` 存在
- 结构符合 `specs/05_output_contract.md`

### 失败条件

- `facts.md` 缺失
- 关键栏目缺失
- 明显越过阶段边界

## Step 5: Blueprint Build

### 目标

基于事实、知识和模板生成业务蓝图与体验蓝图。

### 输入

- `workspace/facts.md`
- `knowledge/wiki/`
- 必要的 `knowledge/business/`
- 必要的 `knowledge/guidelines/`
- 输出模板

### 输出

- `workspace/business_blueprint.md`
- `workspace/experience_blueprint.md`

### 成功条件

- 两个蓝图文件存在
- 输出结构符合合同
- 未越过阶段边界

### 失败条件

- 任一蓝图缺失
- 必需栏目缺失
- 明显把业务判断、体验推导、视觉实现混写

## Step 6: Validation

### 目标

检查输出结构、阶段边界与事实承接情况。

### 输入

- `workspace/facts.md`
- `workspace/business_blueprint.md`
- `workspace/experience_blueprint.md`
- 检查规则

### 输出

- `workspace/check_report.md`
- `workspace/check_status.json`

### 成功条件

- `check_report.md` 已生成
- `check_status.json` 已生成
- 至少表达 `blocker`、`warning`、`info`
- 机器可读状态与 Markdown 报告状态一致

### 失败条件

- 检查报告缺失
- 状态文件缺失
- 存在 blocker 且未显式写出

## Step 7: Archive

### 目标

把任务产物归档到标准位置。

### 输入

- `workspace/`
- `check_report.md`
- `context_bundle/`

### 输出

- `projects/<project-id>/exports/final/`
- `projects/<project-id>/exports/checks/`
- `projects/<project-id>/runtime/archive_snapshot/`

### 成功条件

- 最终产物归档完成
- 检查报告归档完成
- 上下文快照归档完成

### 失败条件

- 任一标准归档目录缺失
- 已完成产物未能复制到归档位置

## 执行中枢与 AI 推理的边界

执行中枢负责：

- 目录
- 协议解析
- 装配
- 校验
- 状态
- 归档

AI 推理负责：

- 事实提炼
- 业务判断
- 体验推导
- `[GAP]` 与 `[CONFLICT]` 的语义处理

## 最小实现要求

只要某实现满足以下条件，即可视为执行中枢：

- 能按上述步骤推进任务
- 能显式报错
- 能稳定落盘
- 能遵守上位 `specs/`

## 后续扩展点

执行中枢未来可以扩展：

- task status summarizer
- wiki sync checker
- export packager
- plugin loader

但这些扩展不得破坏本规格中的最小步骤合同。
