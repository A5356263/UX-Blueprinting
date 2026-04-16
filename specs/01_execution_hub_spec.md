# 执行中枢规格（正式替换稿）

## 目标

定义本项目中“执行中枢”应如何按规则执行任务步骤，并使执行中枢与当前升级后的三阶段主链路保持一致。

本规格面向执行中枢，而不是面向业务推理本身。

执行中枢负责：

- 按规则推进步骤
- 校验输入输出
- 显式暴露失败
- 把结果写入稳定位置
- 在 facts / business / experience 三阶段之间维护边界
- 生成可供 gate / check 消费的机器可读状态

执行中枢不负责：

- 替代业务判断
- 替代体验推导
- 自行发明知识结论
- 以实现便利为由跳过阶段边界

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
- `specs/11_repair_loop_contract.md`
- `specs/14_experience_preview_contract.md`

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
- 下游阶段不得绕过上游 blocker 强行继续

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
- `## Facts Output Requirements`
- `## Business Output Requirements`
- `## Experience Output Requirements`

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
- `facts_output_requirements`
- `business_output_requirements`
- `experience_output_requirements`
- `warnings`
- `errors`

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
- 任一阶段输出要求段缺失或不可解析
- `task_card_resolved.json` 未生成

## Step 3: Context Assembly

### 目标

根据 `task_card.md` 的显式引用，组装最小上下文快照，并显式记录三阶段知识使用边界。

### 输入

- `task_card.md`
- `task_card_resolved.json`
- 仓库内显式引用路径

### 输出

- `projects/<project-id>/runtime/context_bundle/`
- `projects/<project-id>/runtime/context_manifest.json`

### context_manifest 最小要求

至少包含：

- 引用资源清单
- 目录 / 文件类型标记
- warnings
- `facts_extraction_boundary`
- `business_judgment_boundary`
- `experience_translation_boundary`

### 成功条件

- 所有显式引用路径均被解析
- 可复制引用被写入 `context_bundle`
- `context_manifest.json` 正常生成
- 三阶段边界均有机器可读记录

### 失败条件

- 引用路径不存在
- 引用无法复制
- manifest 未生成
- 三阶段边界字段缺失

## Step 4: Fact Extraction

### 目标

从输入材料中生成 `facts.md`，并把本阶段正式视为 structured extraction layer（结构化提取层）。

### 输入

- `task_card.md`
- `task_card_resolved.json`
- `context_manifest.json`
- `source/requirement.md`
- `source/background.md`
- 必要附件
- 任务显式引用的 wiki / knowledge（仅作 calibration）

### 输出

- `workspace/facts.md`
- 必要时 `workspace/gap_list.md`

### 成功条件

- `facts.md` 存在
- 结构符合 `specs/08_fact_extraction_contract.md`
- 至少形成可消费的原子事实、规则结构、状态结构、异常结构、依赖结构、缺口结构
- 未越权输出 business judgment（业务判断）或 experience design（体验设计）

### 失败条件

- `facts.md` 缺失
- 关键栏目缺失
- 主要输出仍是高层摘要而非结构化提取
- 明显越过阶段边界
- 将引用知识提升为当前任务已确认事实

## Step 5: Business Blueprint Build

### 目标

基于 facts、业务知识与 wiki 构建 `business_blueprint.md`，并把本阶段正式视为 business review layer（业务审视层）。

### 输入

- `workspace/facts.md`
- 任务显式引用的 wiki
- 任务显式引用的业务知识
- `task_card_resolved.json`
- `context_manifest.json`
- 输出模板

### 输出

- `workspace/business_blueprint.md`

### 成功条件

- `business_blueprint.md` 存在
- 输出结构符合 `specs/09_business_blueprint_contract.md`
- 关键判断能够回溯到 facts 与基线知识
- 形成合理性判断、底层逻辑一致性判断、管理策略一致性判断、能力归位判断、备选路径比较与最终业务立场
- 未输出 UI 方案或实现方案

### 失败条件

- 文件缺失
- 必需栏目缺失
- 主要内容仍只是 facts 的摘要复述
- 使用知识替代 facts 直接下结论
- 越权进入体验层或实现层

## Step 6: Experience Blueprint Build

### 目标

基于 facts、business blueprint、业务知识与设计指南生成 `experience_blueprint.md`，并把本阶段正式视为 experience architecture layer（体验架构层）。

### 输入

- `workspace/facts.md`
- `workspace/business_blueprint.md`
- 任务显式引用的 wiki
- 任务显式引用的业务知识
- 任务显式引用的 guideline knowledge（设计指南）
- Wiki 中保留的页面结构语义
- `task_card_resolved.json`
- `context_manifest.json`
- 输出模板

### 输出

- `workspace/experience_blueprint.md`

### 成功条件

- `experience_blueprint.md` 存在
- 输出结构符合 `specs/10_experience_blueprint_contract.md`
- 已形成可进入 UI 设计讨论的 IA、task flow、page/window inventory、page blueprint、state & feedback matrix、copy contract
- 已判断新增 / 优化信息是否引起结构变化，并显式表达结构变化或结构不变
- 能回溯到 business judgment、facts 与 guideline
- 未输出高保真视觉设计稿或研发实现细节

### 失败条件

- 文件缺失
- 必需栏目缺失
- 仍停留在抽象体验口号
- 改写 business rules
- 跳过页面结构语义判断，导致新增区块或结构不变没有被显式表达
- 越权进入高保真视觉稿或实现稿

## Step 7: Stage Gates

### 目标

对 facts / business / experience 三阶段分别执行 gate 检查，决定是否可进入下一阶段。

### 输入

- 当前阶段输出
- 上游阶段 gate 状态
- `task_card_resolved.json`
- `context_manifest.json`
- gate / validate 规则

### 输出

- `runtime/gates/facts_gate_report.md`
- `runtime/gates/facts_gate_status.json`
- `runtime/gates/business_gate_report.md`
- `runtime/gates/business_gate_status.json`
- `runtime/gates/experience_gate_report.md`
- `runtime/gates/experience_gate_status.json`

### 最小检查范围

- 结构完整性
- 阶段边界
- 追溯关系
- 覆盖关系
- 深度要求
- 上下游承接关系

### 成功条件

- 每个 gate 都生成 report 与 status
- 状态判断与 issue 分级一致
- failed 不得继续推进下一阶段

### 失败条件

- gate 产物缺失
- stage failed 仍被继续推进
- gate 逻辑与当前合同 / 模板不一致

## Step 8: Final Validation and Coverage

### 目标

执行最终的 check / coverage，检查输出结构、阶段边界、追溯关系、覆盖关系与机器状态一致性。

### 输入

- `workspace/facts.md`
- `workspace/business_blueprint.md`
- `workspace/experience_blueprint.md`
- 各阶段 gate 结果
- 检查规则

### 输出

- `workspace/check_report.md`
- `workspace/check_status.json`

### 最小检查范围

- 输出文件存在性
- 关键栏目存在性
- placeholder（占位内容）残留
- forbidden terms（越权词）检查
- facts -> business -> experience 的 coverage
- judgment / trace / principle 引用关系
- Markdown 报告与 JSON 状态一致性

### 成功条件

- `check_report.md` 已生成
- `check_status.json` 已生成
- 至少表达 `blocker`、`warning`、`info`
- 机器可读状态与 Markdown 报告状态一致

### 失败条件

- 检查报告缺失
- 状态文件缺失
- 存在 blocker 且未显式写出
- check 逻辑仍停留在旧标题 / 旧覆盖规则

## Step 8.5: Repair Plan Build

### 目标

在 `validate / coverage` 之后，将 gate 与最终检查暴露的问题转译为正式修复任务。

### 输入

- `runtime/gates/*_gate_status.json`
- `runtime/gates/*_gate_report.md`
- `workspace/check_status.json`
- `workspace/check_report.md`
- `runtime/trace_index.json`
- `runtime/gate_metrics.json`

### 输出

- `runtime/remediation/issue_index.json`
- `runtime/remediation/remediation_plan.json`
- `runtime/remediation/retry_scope.json`
- `runtime/remediation/repair_summary.md`

### 成功条件

- 问题被标准化为 issue 模型
- 修复计划形成 repair unit，而不是停留在口头说明
- 重跑范围被明确给出
- 如无 open issue，允许直接进入归档判定

### 失败条件

- remediation 产物缺失
- blocker 未被纳入 issue 模型
- 需要回退上游的问题被错误判定为当前阶段局部补修

## Step 8.6: Scoped Retry

### 目标

在修复动作落盘后，按正式范围执行最小必要重跑，而不是凭经验临时决定。

### 输入

- `runtime/remediation/retry_scope.json`
- 修复后更新的正式产物

### 输出

- 重跑后的 gate / validate / coverage 状态

### 成功条件

- 推荐命令来自正式 `python -m packages` 执行入口
- 重跑范围与受影响阶段一致
- 未发生无依据的全链路重跑或漏跑

### 失败条件

- 未按 `retry_scope.json` 重跑
- 未完成验证却试图关闭问题
- 重跑范围与修复影响阶段不一致

## Step 8.7: Repair Close

### 目标

在重跑后重新判断 issue 状态，关闭已解决问题，并形成可追溯修复记录。

### 输入

- `runtime/remediation/issue_index.json`
- `runtime/remediation/remediation_plan.json`
- `runtime/remediation/retry_scope.json`
- 重跑后的 gate / validate / coverage 结果

### 输出

- 更新后的 `runtime/remediation/issue_index.json`
- `runtime/remediation/repair_run_log.jsonl`
- 更新后的 `runtime/remediation/repair_summary.md`

### 成功条件

- issue 被更新为 `resolved / accepted / deferred / invalid / open`
- 未完成重跑的问题不会被标记为 `resolved`
- 当前修复闭环状态可被 archive 正式消费

### 失败条件

- 修复状态未更新
- 修复记录未落盘
- open blocker 未清零却被标记为可归档

## Step 9: Archive

### 目标

把任务产物归档到标准位置。

### 输入

- `workspace/`
- `check_report.md`
- `context_bundle/`
- 如存在：`runtime/remediation/repair_summary.md`
- 如存在：`runtime/remediation/issue_index.json`

### 输出

- `projects/<project-id>/exports/final/`
- `projects/<project-id>/exports/checks/`
- `projects/<project-id>/runtime/archive_snapshot/`

### 成功条件

- 最终产物归档完成
- 检查报告归档完成
- 上下文快照归档完成
- 若已进入 Repair Loop，则不存在 open blocker 或 deferred blocker
- archive 判定以当前 repair 状态为准，而不只看旧 gate 结果

### 失败条件

- 任一标准归档目录缺失
- 已完成产物未能复制到归档位置
- 存在 open blocker 却继续归档
- 存在 deferred blocker 却继续归档

## Step 9.5: Experience Preview

### 目标

在主链路正式产物完成后，生成正式体验蓝图的只读浏览器预览层，并向用户交付明确可访问的本地预览地址。

### 输入

- `projects/<project-id>/exports/final/experience_blueprint.md`
- 或降级输入 `projects/<project-id>/workspace/experience_blueprint.md`

### 输出

- `projects/<project-id>/runtime/preview/index.html`
- `projects/<project-id>/runtime/preview/assets/style.css`
- `projects/<project-id>/runtime/preview/preview_model.json`
- `projects/<project-id>/runtime/preview/preview_runtime.json`
- `projects/<project-id>/runtime/preview/preview_build_log.md`

### 成功条件

- 预览运行时文件已写入 `runtime/preview/`
- 本地服务已成功启动，或已显式选择仅构建模式
- 若服务已启动，输出中明确给出完整本地 URL
- 预览层未修改正式蓝图与主链路正式产物

### 失败条件

- 输入体验蓝图不存在
- 预览运行时文件缺失
- 服务已启动但未输出完整 URL
- 预览层失败被误判为主链路失败

## 推荐命令入口

建议至少提供以下命令入口，保证执行中枢既可逐步运行，也可一键跑完整主链路：

- `python -m packages generate-facts <project-id>`
- `python -m packages generate-business <project-id>`
- `python -m packages generate-experience <project-id>`
- `python -m packages run-main <project-id>`
- `python -m packages run-main <project-id> --skip-preview`
- `python -m packages sample-check`

其中：

- `run-main` 负责按固定顺序串联 `assemble -> generate-* -> gate-* -> validate -> coverage -> archive`
- 默认 `run-main` 在 archive 成功后自动执行 preview
- `sample-check` 只消费 benchmark 样例，不参与真实项目默认扫描

## 执行中枢与 AI 推理的边界

执行中枢负责：

- 目录
- 协议解析
- 装配
- gate
- validate
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
- 能消费新的 task 协议字段与三阶段边界

## 后续扩展点

执行中枢未来可以扩展：

- task status summarizer
- memory extractor
- memory acceptor
- memory summary writer
- experience preview generator
- wiki sync checker
- export packager
- plugin loader

但这些扩展不得破坏本规格中的最小步骤合同。
