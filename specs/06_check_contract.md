# 检查合同

## 目标

定义执行中枢如何对输出结果进行正式检查、状态判定与 issue 数据暴露。

本合同既服务于当前 `validate / coverage / stage gate`，也服务于 `Repair Loop` 对问题的标准化消费。

## 检查范围

- 结构完整性
- 阶段边界越权
- 开放问题缺失
- 事实与蓝图的覆盖关系
- 机器可读状态产出
- issue 标准化所需的数据暴露

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

- 存在 `blocker` 时，`check_status.json.status` 必须为 `failed`
- 不存在 `blocker` 但存在 `warning` 时，`status` 必须为 `warning`
- 不存在 `blocker` 与 `warning` 时，`status` 必须为 `passed`

同一规则同样适用于各阶段 gate 的 `*_gate_status.json`。

## 双产物分工

- `check_status.json` 与 `*_gate_status.json`：机器正式判断依据
- `check_report.md` 与 `*_gate_report.md`：人类解释说明依据

Markdown 是解释层，JSON 是机器真源。  
Repair Loop 可以从 Markdown 补充证据，但不得让 Markdown 替代 JSON 成为正式状态来源。

## 面向 Repair Loop 的 issue 暴露要求

检查产物至少应支持提取以下字段：

- `severity`
- `category`
- `evidence`
- `target_artifact`
- `violated_contract_ref`

在短期内，如果检查器尚未直接输出完整结构化 issue，允许由 `repair-plan` 从：

- JSON 状态文件
- Markdown 报告

中做标准化提取。

但中期目标应是：

- gate / validate / coverage 自身具备更稳定的 issue 暴露能力

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

如可行，建议逐步补充：

- `issue_sources`
- `violated_contract_refs`
- `target_artifacts`
- `metrics`

## issue 进入 Repair Loop 的规则

- `blocker`：必须进入 Repair Loop，且不得绕过进入 archive
- `warning`：默认进入 Repair Loop，后续可被 `accepted` 或继续修复
- `info`：可进入 Repair Loop 摘要层；是否进入正式修复单元，由 remediation 规划决定

## 一致性要求

- Markdown 报告中的总状态必须与 JSON 状态一致
- blocker / warning / info 的数量与 JSON 中的计数必须一致
- 被标记为 `failed` 的阶段不得伪装成仅有人类说明的“待观察项”
- JSON 中未出现的问题，不得仅靠 Markdown 文案被当作正式 blocker 归档约束依据

## 失败条件

- `check_report.md` 缺失
- `check_status.json` 缺失
- Markdown 报告与 JSON 状态不一致
- 存在 blocker 但未显式写出失败状态
- 存在严重问题但无法从机器状态或报告中提取最小 issue 证据
