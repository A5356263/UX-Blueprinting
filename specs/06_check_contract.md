# 检查合同

## 目标

定义 validate / coverage / stage gate 在当前仓库中的正式检查口径、状态判定方式与问题暴露方式。

## 检查范围

- 产物结构完整性
- 阶段边界是否越权
- 关键信息是否缺失
- business 与 experience 之间的自然语言承接质量
- 机器可读状态输出
- issue 标准化暴露

## 正式输出

- `projects/<project-id>/workspace/check_report.md`
- `projects/<project-id>/workspace/check_status.json`

如为阶段 gate，则对应输出：

- `projects/<project-id>/runtime/gates/*_gate_report.md`
- `projects/<project-id>/runtime/gates/*_gate_status.json`

## 状态层级

- `blocker`
- `warning`
- `info`

## 状态判定规则

- 存在 `blocker` 时，状态必须为 `failed`
- 不存在 `blocker` 但存在 `warning` 时，状态必须为 `warning`
- 同时不存在 `blocker` 和 `warning` 时，状态必须为 `passed`

同一规则适用于 `check_status.json` 与各类 `*_gate_status.json`。

## 双产物分工

- JSON：正式机器状态源
- Markdown：面向人的解释层

Repair Loop 可以引用 Markdown 补充说明，但不得让 Markdown 替代 JSON 成为正式状态来源。

## 面向 Repair Loop 的 Issue 暴露要求

至少应可提取：

- `severity`
- `category`
- `evidence`
- `target_artifact`
- `violated_contract_ref`

当前仓库中的 `*_gate_status.json` 与 `check_status.json` 至少应补充：

- `issue_details_version`
- `issue_details`

其中 `issue_details[*]` 至少包含：

- `source`
- `stage`
- `severity`
- `category`
- `message`
- `target_artifacts`
- `violated_contract_refs`
- `checked_files`
- `evidence`

## 最小机器字段要求

机器状态文件至少应稳定表达：

- `status`
- `blocker_count`
- `warning_count`
- `info_count`
- `issues.blockers`
- `issues.warnings`
- `issues.infos`
- `checked_files`
- `generated_by`
- `updated_at`

可选增强：

- `issue_sources`
- `violated_contract_refs`
- `target_artifacts`
- `metrics`

## 一致性要求

- Markdown 报告中的总状态必须与 JSON 一致
- blocker / warning / info 数量必须与 JSON 计数一致
- 被标记为 `failed` 的阶段不得在文案上伪装成“仅观察”
- JSON 中未出现的问题，不得仅靠 Markdown 被当作正式 blocker

## 失败条件

- `check_report.md` 缺失
- `check_status.json` 缺失
- Markdown 与 JSON 状态不一致
- 存在 blocker 但未显式写出失败状态
- 严重问题无法从状态文件或报告中提取最小证据

## 知识装配专项检查

围绕 01 / 02 阶段收口后，检查口径改为：

- `context_manifest.json.selection_source` 必须指向 `runtime/uxb_route_decision.json`
- `knowledge_usage_report.json.selected_refs` 必须存在
- `knowledge_usage_report.json.assembled_refs` 必须存在
- `knowledge_usage_report.json.missing_refs` 必须存在
- 如 `selected_refs` 中声明了 ref，则对应 ref 必须能在 manifest 或 missing 列表中被解释
- 不再要求 `knowledge_consumption_plan`
- 不再要求 `source_ref_chains`
- 不再要求 `guideline summary -> raw` 自动消费记录

## 执行判断专项检查

- 主链路执行前必须存在 `runtime/uxb_route_decision.json`
- `confirmed_by_user` 必须为 `true`
- `can_execute_mainline` 必须为 `true`
- `execution.required_outputs` 必须存在
- 如果执行期发现判断不完整，应返回 `needs_rejudgment`
- 检查器不得自行升级、替换或补写 UXB 判断
