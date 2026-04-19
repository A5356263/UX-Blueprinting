# Final Convergence Report

## 验收范围

- 规范来源：`specs/01_execution_hub_spec.md`、`specs/06_check_contract.md`、`specs/11_repair_loop_contract.md`
- 黄金样例项目：`examples/positive/real-self-apply-v1/`
- 验收目标：完成 P2 Repair Loop 落地，并验证 facts / business / experience 三类失败样例均可进入正式修复闭环

## 当前命令面

```bash
python -m packages bootstrap
python -m packages assemble
python -m packages gate-facts
python -m packages gate-business
python -m packages gate-experience
python -m packages validate
python -m packages coverage
python -m packages repair-plan
python -m packages repair-status
python -m packages repair-close
python -m packages repair-accept
python -m packages repair-defer
python -m packages archive
```

## 已刷新产物

- runtime
  - `examples/positive/real-self-apply-v1/runtime/task_card_resolved.json`
  - `examples/positive/real-self-apply-v1/runtime/context_manifest.json`
  - `examples/positive/real-self-apply-v1/runtime/gates/facts_gate_report.md`
  - `examples/positive/real-self-apply-v1/runtime/gates/facts_gate_status.json`
  - `examples/positive/real-self-apply-v1/runtime/gates/business_gate_report.md`
  - `examples/positive/real-self-apply-v1/runtime/gates/business_gate_status.json`
  - `examples/positive/real-self-apply-v1/runtime/gates/experience_gate_report.md`
  - `examples/positive/real-self-apply-v1/runtime/gates/experience_gate_status.json`
  - `examples/positive/real-self-apply-v1/runtime/trace_index.json`
  - `examples/positive/real-self-apply-v1/runtime/gate_metrics.json`
  - `examples/positive/real-self-apply-v1/runtime/knowledge_usage_report.json`
  - `examples/positive/real-self-apply-v1/runtime/remediation/issue_index.json`
  - `examples/positive/real-self-apply-v1/runtime/remediation/remediation_plan.json`
  - `examples/positive/real-self-apply-v1/runtime/remediation/retry_scope.json`
  - `examples/positive/real-self-apply-v1/runtime/remediation/repair_run_log.jsonl`
  - `examples/positive/real-self-apply-v1/runtime/remediation/repair_summary.md`
- workspace
  - `examples/positive/real-self-apply-v1/workspace/facts.md`
  - `examples/positive/real-self-apply-v1/workspace/business_blueprint.md`
  - `examples/positive/real-self-apply-v1/workspace/experience_blueprint.md`
  - `examples/positive/real-self-apply-v1/workspace/gap_list.md`
  - `examples/positive/real-self-apply-v1/workspace/check_report.md`
  - `examples/positive/real-self-apply-v1/workspace/check_status.json`
- exports
  - `examples/positive/real-self-apply-v1/exports/checks/repair_summary.md`

## Repair Loop 失败样例验证

### 样例 A：facts 回退验证

人工制造缺陷：

- 将 `examples/positive/real-self-apply-v1/workspace/facts.md` 中的 `## 追踪映射`
- 临时改为 `## 追踪补丁（临时缺陷）`

故障期命令链：

```bash
python -m packages gate-facts real-self-apply-v1
python -m packages validate real-self-apply-v1
python -m packages coverage real-self-apply-v1
python -m packages repair-plan real-self-apply-v1
```

故障期观察结果：

- `facts gate` 变为 `failed`
- `check_status.json.status` 变为 `failed`
- `repair-plan` 识别 `facts.md` 缺少 `## 追踪映射`
- `retry_scope.json.recommended_commands` 扩展为：
  - `python -m packages gate-facts real-self-apply-v1`
  - `python -m packages gate-business real-self-apply-v1`
  - `python -m packages gate-experience real-self-apply-v1`
  - `python -m packages validate real-self-apply-v1`
  - `python -m packages coverage real-self-apply-v1`

恢复与关闭：

- 恢复 `## 追踪映射`
- 依次执行完整推荐链路
- 执行 `python -m packages repair-close real-self-apply-v1`

修复后结果：

- `repair_loop_status`：`closed`
- `open_blocker_count`：`0`

### 样例 B：business 回退验证

人工制造缺陷：

- 将 `examples/positive/real-self-apply-v1/workspace/business_blueprint.md` 中的 `## 判断追踪映射`
- 临时改为 `## 判断追踪补丁（临时缺陷）`

故障期命令链：

```bash
python -m packages gate-business real-self-apply-v1
python -m packages gate-experience real-self-apply-v1
python -m packages validate real-self-apply-v1
python -m packages coverage real-self-apply-v1
python -m packages repair-plan real-self-apply-v1
```

故障期观察结果：

- `business gate` 变为 `failed`
- `experience gate` 随之变为 `failed`
- `check_status.json.status` 变为 `failed`
- `repair-plan` 识别 `business_blueprint.md` 缺少 `## 判断追踪映射`
- `retry_scope.json.recommended_commands` 扩展为：
  - `python -m packages gate-business real-self-apply-v1`
  - `python -m packages gate-experience real-self-apply-v1`
  - `python -m packages validate real-self-apply-v1`
  - `python -m packages coverage real-self-apply-v1`

恢复与关闭：

- 恢复 `## 判断追踪映射`
- 依次执行完整推荐链路
- 执行 `python -m packages repair-close real-self-apply-v1`

修复后结果：

- `repair_loop_status`：`closed`
- `open_blocker_count`：`0`

### 样例 C：experience scoped rerun 验证

人工制造缺陷：

- 将 `examples/positive/real-self-apply-v1/workspace/experience_blueprint.md` 中的 `## 状态与反馈矩阵`
- 临时改为 `## 状态矩阵（临时缺陷）`

故障期命令链：

```bash
python -m packages gate-experience real-self-apply-v1
python -m packages validate real-self-apply-v1
python -m packages coverage real-self-apply-v1
python -m packages repair-plan real-self-apply-v1
```

故障期观察结果：

- `experience gate` 变为 `failed`
- `check_status.json.status` 变为 `failed`
- `repair-plan` 正确识别缺失章节：`## 状态与反馈矩阵`
- `retry_scope.json` 给出 scoped rerun：
  - `python -m packages gate-experience real-self-apply-v1`
  - `python -m packages validate real-self-apply-v1`
  - `python -m packages coverage real-self-apply-v1`

archive 前置约束验证：

在缺陷未修复且 `repair-plan` 已生成时，执行：

```bash
python -m packages archive real-self-apply-v1
```

结果：

- 归档被正式阻止
- 阻止原因为：`check_status.json.status=failed`

恢复与关闭：

- 恢复 `## 状态与反馈矩阵`
- 依次执行完整推荐链路
- 执行 `python -m packages repair-close real-self-apply-v1`
- 执行 `python -m packages repair-status real-self-apply-v1`
- 执行 `python -m packages archive real-self-apply-v1`

修复后结果：

- `repair_loop_status`：`closed`
- `open_issue_count`：`0`
- `open_blocker_count`：`0`
- `archive` 恢复可执行

### 样例 D：accepted / deferred warning 验证

人工制造缺陷：

- 临时移除 `examples/positive/real-self-apply-v1/workspace/experience_blueprint.md` 对 `J-09` 的消费
- 使 coverage 产生 warning：`存在未被体验层消费的业务判断：J-09`

故障期命令链：

```bash
python -m packages validate real-self-apply-v1
python -m packages coverage real-self-apply-v1
python -m packages repair-plan real-self-apply-v1
```

故障期观察结果：

- `check_status.json.status` 变为 `warning`
- `issue_index.json` 形成单一 warning issue，而不是文本散点
- `retry_scope.json.recommended_commands` 为：
  - `python -m packages validate real-self-apply-v1`
  - `python -m packages coverage real-self-apply-v1`

状态操作验证：

```bash
python -m packages validate real-self-apply-v1
python -m packages coverage real-self-apply-v1
python -m packages repair-defer real-self-apply-v1 <issue-id> --reason "<deferred-reason>"
python -m packages repair-accept real-self-apply-v1 <issue-id> --reason "<accepted-reason>"
```

观察结果：

- `repair-defer` 会把 warning 正式标记为 `deferred`
- `repair-accept` 会把 warning 正式标记为 `accepted`
- `issue_index.json` 会同步写入 `status_reason` 与 `status_updated_at`
- `repair_run_log.jsonl` 会记录状态变更事件

恢复与关闭：

- 恢复 `J-09` 消费
- 执行 `gate-experience -> validate -> coverage -> repair-close`

修复后结果：

- warning issue 被标记为 `resolved`
- 黄金样例重新回到 `check_status.json.status=passed`
- `repair_loop_status=closed`

## 最终验收状态

- `facts gate`：passed
- `business gate`：passed
- `experience gate`：passed
- `check_status.json`：passed
- `repair_loop_status`：closed
- blocker：0
- warning：0

## 结论

- P2 Repair Loop 已从文档方案落到正式执行入口
- 黄金样例 `real-self-apply-v1` 已验证“facts 回退、business 回退、experience scoped rerun”三类修复路径
- archive 已具备 repair-aware 前置约束
- 当前仓库已具备可暂时收口、不继续深化也可使用的 P2 主闭环
