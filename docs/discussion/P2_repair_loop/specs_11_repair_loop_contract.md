# Repair Loop 合同

## 目标

定义当前项目中 `Repair Loop`（修复闭环层）应如何对 gate（闸门）、validate（正式检查）与 coverage（覆盖检查）暴露的问题进行标准化收集、修复组织、范围化重跑与问题关闭。

本合同的目标不是增加新的业务阶段，也不是替代 facts（事实层）、business（业务层）、experience（体验层）的主链路，而是在现有三阶段主链路与执行中枢之上，正式建立一条 **repair-aware workflow（具备修复意识的工作流）**。

本合同用于解决以下问题：

- 问题被发现后，如何从“失败状态”转译为“可执行修复任务”
- 哪些问题应局部补修，哪些问题必须回退上游阶段
- 修复完成后，应重跑哪些步骤
- 如何记录修复过程与关闭状态
- 在什么条件下，任务可以从修复态重新回到可归档态

## 定位

Repair Loop 是执行中枢的增强层，不是新的业务阶段。

它负责：

- 收集 gate / validate / coverage 暴露的问题
- 将分散问题标准化为统一 issue（问题）模型
- 生成 remediation plan（修复计划）
- 生成 retry scope（重跑范围）
- 协助操作者进行局部补修或阶段回退判断
- 在重跑后关闭已解决问题并更新修复状态

它不负责：

- 替代 facts、business、experience 的内容生成
- 自动重写文档正文
- 决定业务立场或体验立场
- 引入新的外部 AI 调用协议
- 改变当前项目的主架构与主目录语义

## 与现有架构的关系

Repair Loop 必须嵌入以下现有结构中，而不是替代它们：

- `specs/`：唯一正式规则真源
- `packages/`：唯一固定执行入口
- `projects/<project-id>/source/`：人读输入层
- `projects/<project-id>/workspace/`：人读结果层
- `projects/<project-id>/runtime/`：机器运行层
- `projects/<project-id>/exports/`：交付镜像层

Repair Loop 的新增产物原则上位于：

- `projects/<project-id>/runtime/remediation/`

## 上位依赖

Repair Loop 必须受以下文档约束：

- `specs/01_execution_hub_spec.md`
- `specs/03_task_card_contract.md`
- `specs/06_check_contract.md`
- `specs/08_fact_extraction_contract.md`
- `specs/09_business_blueprint_contract.md`
- `specs/10_experience_blueprint_contract.md`

其中：

- facts / business / experience 合同定义“各阶段什么算合格”
- check contract 定义“正式检查如何表达失败 / warning / passed”
- execution hub spec 定义“执行中枢如何推进步骤”
- 本合同定义“问题被发现后，如何进入修复闭环”

## 统一状态模型

Repair Loop 至少使用以下状态：

### 修复问题状态

- `open`：问题已识别，尚未处理
- `accepted`：问题存在，但当前被正式接受为可保留 warning
- `resolved`：问题已修复，且在重跑后确认不再触发
- `deferred`：问题已识别，但当前轮次不处理，明确延期
- `invalid`：问题经确认后属于误报或已失效

### 修复闭环状态

- `idle`：尚未进入 repair loop
- `planned`：修复计划已生成
- `in_repair`：正在执行修复
- `rerun_pending`：修复已落盘，等待按范围重跑
- `verifying`：正在执行重跑验证
- `closed`：当前 open blocker 已清零，修复闭环已完成
- `blocked`：存在 blocker 且尚未修复，不得归档

## 统一失败原则

Repair Loop 必须遵守：

- 问题不得只停留在口头说明，必须进入标准 issue 模型
- blocker 不得伪装为 warning
- 未完成重跑验证的问题不得标记为 `resolved`
- 需要回退上游阶段的问题不得被伪装成当前阶段局部补修
- 修复动作必须落盘，不能只存在聊天窗口
- open blocker 未清零时，不得进入 `archive`

## 输入

Repair Loop 的输入来自当前项目已有机器产物与检查产物。

至少包括：

- `projects/<project-id>/runtime/task_card_resolved.json`
- `projects/<project-id>/runtime/context_manifest.json`
- `projects/<project-id>/runtime/gates/facts_gate_status.json`
- `projects/<project-id>/runtime/gates/facts_gate_report.md`
- `projects/<project-id>/runtime/gates/business_gate_status.json`
- `projects/<project-id>/runtime/gates/business_gate_report.md`
- `projects/<project-id>/runtime/gates/experience_gate_status.json`
- `projects/<project-id>/runtime/gates/experience_gate_report.md`
- `projects/<project-id>/workspace/check_status.json`
- `projects/<project-id>/workspace/check_report.md`

如存在以下文件，也应优先读取：

- `projects/<project-id>/runtime/trace_index.json`
- `projects/<project-id>/runtime/gate_metrics.json`
- `projects/<project-id>/runtime/knowledge_usage_report.json`
- `projects/<project-id>/workspace/facts.md`
- `projects/<project-id>/workspace/business_blueprint.md`
- `projects/<project-id>/workspace/experience_blueprint.md`
- `projects/<project-id>/workspace/gap_list.md`

## 输出

Repair Loop 至少输出以下正式产物：

- `projects/<project-id>/runtime/remediation/issue_index.json`
- `projects/<project-id>/runtime/remediation/remediation_plan.json`
- `projects/<project-id>/runtime/remediation/retry_scope.json`
- `projects/<project-id>/runtime/remediation/repair_summary.md`

如闭环进入执行与关闭阶段，还应输出：

- `projects/<project-id>/runtime/remediation/repair_run_log.jsonl`

## issue_index.json 合同

### 目标

将 gate / validate / coverage 暴露的分散问题，标准化为统一问题索引。

### 最小字段

每个 issue 至少包含：

- `issue_id`
- `source`
- `stage`
- `severity`
- `category`
- `title`
- `description`
- `evidence`
- `violated_contract_refs`
- `target_artifacts`
- `repair_mode`
- `suggested_actions`
- `upstream_backtrack_required`
- `retry_scope_hint`
- `status`

### 字段说明

#### `issue_id`
唯一问题标识。  
建议格式：

- `FACT-*`
- `BIZ-*`
- `EXP-*`
- `CHK-*`
- `COV-*`
- `RUN-*`

#### `source`
问题来源，至少支持：

- `facts_gate`
- `business_gate`
- `experience_gate`
- `validate`
- `coverage`
- `runtime`

#### `stage`
问题归属阶段，至少支持：

- `facts`
- `business`
- `experience`
- `final`
- `runtime`

#### `severity`
严重级别，仅允许：

- `blocker`
- `warning`
- `info`

#### `category`
问题分类，至少支持：

- `structure_missing`
- `boundary_violation`
- `trace_missing`
- `coverage_gap`
- `depth_insufficient`
- `state_model_gap`
- `copy_contract_gap`
- `consistency_conflict`
- `runtime_staleness`
- `placeholder_residue`

#### `evidence`
最小证据集合。  
可包含：

- 报告片段
- 命中的栏目名
- 触发规则名
- 文件路径
- 行号 / 区段名
- 命中的 forbidden term
- 缺失的 expected section

#### `violated_contract_refs`
至少应引用相关合同路径，例如：

- `specs/08_fact_extraction_contract.md`
- `specs/09_business_blueprint_contract.md`
- `specs/10_experience_blueprint_contract.md`
- `specs/06_check_contract.md`

#### `target_artifacts`
至少列出被影响的正式产物路径。

#### `repair_mode`
仅允许以下值之一：

- `patch_current_section`
- `patch_current_artifact`
- `regenerate_current_stage`
- `backtrack_upstream_stage`
- `rerun_checks_only`
- `accept_warning`
- `defer`

#### `upstream_backtrack_required`
布尔值。  
用于表达该问题是否必须回退上游阶段。

#### `retry_scope_hint`
推荐重跑范围提示，不是最终正式命令清单。

#### `status`
仅允许：

- `open`
- `accepted`
- `resolved`
- `deferred`
- `invalid`

## remediation_plan.json 合同

### 目标

把 issue 索引转译为正式修复计划，而不是停留在问题列表。

### 最小字段

- `project_id`
- `plan_version`
- `generated_at`
- `open_issue_count`
- `blocker_count`
- `warning_count`
- `repair_units`

### repair_units 最小字段

每个 repair unit 至少包含：

- `unit_id`
- `stage`
- `target_artifact`
- `issue_ids`
- `repair_mode`
- `repair_goal`
- `required_inputs`
- `operator_guidance`
- `completion_signal`

### 修复单元原则

Repair Loop 不要求一条 issue 对应一个修复动作。  
允许将同阶段、同目标文档、同修复模式的问题聚合为一个 repair unit。

聚合时必须满足：

- 不跨越相互冲突的阶段边界
- 不混合“局部补修”和“必须回退上游”的问题
- 不把 blocker 与纯 info 混成一个无法执行的修复单元

### operator_guidance 约束

`operator_guidance` 必须是明确可执行的修复指导，不得只写抽象口号。  
例如允许：

- “补齐体验追踪映射章节”
- “新增失败态 / 阻断态 / 处理中状态”
- “不要整稿重写，只修正文案合同矩阵”

不允许：

- “优化一下”
- “写得更完整”
- “增强体验”

## retry_scope.json 合同

### 目标

定义修复完成后必须执行的重跑范围。

### 最小字段

- `project_id`
- `scope_version`
- `recommended_commands`
- `backtrack_required`
- `highest_required_stage`
- `rationale`

### recommended_commands 规则

`recommended_commands` 必须是仓库正式执行入口，至少来自：

```bash
python -m packages gate-facts <project-id>
python -m packages gate-business <project-id>
python -m packages gate-experience <project-id>
python -m packages validate <project-id>
python -m packages coverage <project-id>
```

### 标准回退规则

#### 情况 A：facts blocker
若 blocker 位于 facts 阶段，至少应重跑：

- `gate-facts`
- `gate-business`
- `gate-experience`
- `validate`
- `coverage`

#### 情况 B：business blocker
若 blocker 位于 business 阶段，至少应重跑：

- `gate-business`
- `gate-experience`
- `validate`
- `coverage`

#### 情况 C：experience blocker
若 blocker 位于 experience 阶段，至少应重跑：

- `gate-experience`
- `validate`
- `coverage`

#### 情况 D：仅 final check / coverage 问题
若问题不涉及事实 / 业务 / 体验正文重写，只涉及最终检查层，则允许只重跑：

- `validate`
- `coverage`

### highest_required_stage 规则

仅允许：

- `facts`
- `business`
- `experience`
- `final`

用于表达本轮修复至少影响到哪个最高阶段。

## repair_summary.md 合同

### 目标

输出面向人类的修复摘要，便于快速理解：

- 当前有哪些 open issue
- 哪些是 blocker
- 当前应修什么
- 修完后重跑什么
- 哪些 warning 被接受
- 哪些问题延期

### 最小结构

`repair_summary.md` 至少包含：

- `当前状态`
- `问题统计`
- `本轮修复单元`
- `推荐重跑`
- `未关闭问题`
- `已接受 warning`
- `已延期问题`

### 表达要求

摘要必须人类可读，但不得与 JSON 状态相冲突。  
Markdown 只负责解释，不得成为机器正式判断真源。

## repair_run_log.jsonl 合同

### 目标

记录 Repair Loop 每一轮操作与状态变化。

### 最小字段

每条日志至少包含：

- `ts`
- `cycle_id`
- `event`
- `actor`
- `issue_ids`
- `result`

### 允许事件类型

至少支持：

- `plan_generated`
- `repair_started`
- `repair_artifacts_updated`
- `rerun_started`
- `rerun_finished`
- `issue_resolved`
- `issue_accepted`
- `issue_deferred`
- `repair_closed`

## Repair Loop 标准流程

### Step 1：Issue Collect
收集以下来源中的问题：

- facts gate
- business gate
- experience gate
- validate
- coverage
- 必要时 runtime 一致性问题

要求：

- 不遗漏 blocker
- 不伪造问题
- 同一问题可合并去重，但必须保留来源信息

### Step 2：Issue Normalize
将问题标准化为统一 issue 模型，并写入：

- `runtime/remediation/issue_index.json`

### Step 3：Plan Build
根据 issue 索引生成：

- `runtime/remediation/remediation_plan.json`
- `runtime/remediation/retry_scope.json`
- `runtime/remediation/repair_summary.md`

### Step 4：Repair Action
由操作者使用现有工具执行修复。  
修复必须：

- 面向正式产物
- 落盘到 `workspace/` 或其他正式位置
- 对齐 remediation plan
- 不得只在聊天中口头说明已修复

### Step 5：Scoped Rerun
按 `retry_scope.json` 重跑相关命令。  
未完成重跑，不得关闭问题。

### Step 6：Repair Close
重跑后，逐条更新 issue 状态：

- 不再命中 -> `resolved`
- 明确保留且可接受 -> `accepted`
- 暂不处理 -> `deferred`
- 误报或失效 -> `invalid`
- 仍命中 -> 保持 `open`

同时更新：

- `repair_summary.md`
- `repair_run_log.jsonl`

## 与 archive 的关系

Repair Loop 必须对 archive 形成正式约束：

- 如存在 `open` 且 `severity=blocker` 的 issue，不得执行 archive
- 如不存在 open blocker，但存在 accepted warning，可继续 archive
- 如存在 deferred blocker，不得执行 archive
- `archive` 前应以当前修复闭环状态为准，而不只看旧的 gate 结果

## Warning 条件

以下情况可以生成 remediation 产物，但必须带 warning：

- issue 可被识别，但部分 evidence 只能从 Markdown 报告中解析，暂未实现完全结构化
- repair unit 已生成，但 operator guidance 仍偏粗，需后续细化
- retry scope 已成立，但个别命令仍依赖人工确认
- 某些 info 问题仅进入摘要，不进入正式修复单元

## 失败条件

Repair Loop 视为失败，如出现以下任一情况：

- `issue_index.json` 未生成
- `remediation_plan.json` 未生成
- `retry_scope.json` 未生成
- `repair_summary.md` 未生成
- blocker 未进入 issue 模型
- 需要回退上游的问题被错误标记为当前阶段局部补修
- 修复未落盘却被标记为已完成
- 未执行 scoped rerun 就将问题标为 `resolved`
- open blocker 未清零却继续进入 archive

## 合格标准

一个合格的 Repair Loop 至少满足：

- 能从现有 gate / validate / coverage 中提取问题
- 能把问题转为统一 issue 模型
- 能形成正式 remediation plan
- 能形成正式 retry scope
- 能支持局部补修
- 能支持上游回退判断
- 能在重跑后关闭已解决问题
- 能阻止 open blocker 进入 archive
- 不改变当前项目主架构与三阶段主链路

## 阶段完成标准

Repair Loop 可视为落地完成，当以下条件同时满足：

- 相关 specs 已更新
- 相关 packages 命令已实现
- `runtime/remediation/` 产物可稳定生成
- 至少一个失败样例项目可走通：
  - 问题收集
  - 修复计划
  - 局部补修
  - 范围化重跑
  - 问题关闭
- 对现有通过样例不造成兼容性破坏

## 与其他模块的同步要求

本合同引入后，至少应同步检查以下模块：

- `specs/01_execution_hub_spec.md`
- `specs/06_check_contract.md`
- `packages/__main__.py`
- `packages/validate/*`
- `docs/runbook/task_execution_flow.md`
- `docs/runbook/external_ai_quickstart.md`

如果合同已建立，但执行入口、检查产物与 runbook 仍未同步，则 Repair Loop 只能停留在文档层，无法成为正式能力。

## 一句话原则

**先把问题标准化，再组织修复；先局部补修，再判断是否回退；修复后必须按范围重跑，open blocker 清零后才能归档。**
