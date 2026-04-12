# Final Convergence Report

## 验收范围

- 规范来源：`specs/01_execution_hub_spec.md`、`specs/06_check_contract.md`、`specs/11_repair_loop_contract.md`
- 黄金样例项目：`projects/real-self-apply-v1/`
- 验收目标：完成 P2 Repair Loop 落地，并验证失败样例可进入正式修复闭环

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
python -m packages archive
```

## 已刷新产物

- runtime
  - `projects/real-self-apply-v1/runtime/task_card_resolved.json`
  - `projects/real-self-apply-v1/runtime/context_manifest.json`
  - `projects/real-self-apply-v1/runtime/gates/facts_gate_report.md`
  - `projects/real-self-apply-v1/runtime/gates/facts_gate_status.json`
  - `projects/real-self-apply-v1/runtime/gates/business_gate_report.md`
  - `projects/real-self-apply-v1/runtime/gates/business_gate_status.json`
  - `projects/real-self-apply-v1/runtime/gates/experience_gate_report.md`
  - `projects/real-self-apply-v1/runtime/gates/experience_gate_status.json`
  - `projects/real-self-apply-v1/runtime/trace_index.json`
  - `projects/real-self-apply-v1/runtime/gate_metrics.json`
  - `projects/real-self-apply-v1/runtime/knowledge_usage_report.json`
  - `projects/real-self-apply-v1/runtime/remediation/issue_index.json`
  - `projects/real-self-apply-v1/runtime/remediation/remediation_plan.json`
  - `projects/real-self-apply-v1/runtime/remediation/retry_scope.json`
  - `projects/real-self-apply-v1/runtime/remediation/repair_run_log.jsonl`
  - `projects/real-self-apply-v1/runtime/remediation/repair_summary.md`
- workspace
  - `projects/real-self-apply-v1/workspace/facts.md`
  - `projects/real-self-apply-v1/workspace/business_blueprint.md`
  - `projects/real-self-apply-v1/workspace/experience_blueprint.md`
  - `projects/real-self-apply-v1/workspace/gap_list.md`
  - `projects/real-self-apply-v1/workspace/check_report.md`
  - `projects/real-self-apply-v1/workspace/check_status.json`
- exports
  - `projects/real-self-apply-v1/exports/checks/repair_summary.md`

## Repair Loop 失败样例验证

### 人工制造缺陷

在 `projects/real-self-apply-v1/workspace/experience_blueprint.md` 中，将：

- `## 状态与反馈矩阵`

临时改为：

- `## 状态矩阵（临时缺陷）`

### 故障期命令链

```bash
python -m packages gate-experience real-self-apply-v1
python -m packages validate real-self-apply-v1
python -m packages coverage real-self-apply-v1
python -m packages repair-plan real-self-apply-v1
```

### 故障期观察结果

- `experience gate` 变为 `failed`
- `check_status.json.status` 变为 `failed`
- `repair-plan` 生成 remediation 产物
- `repair_summary.md` 正确识别缺失章节：`## 状态与反馈矩阵`
- `retry_scope.json` 给出 scoped rerun：
  - `python -m packages gate-experience real-self-apply-v1`
  - `python -m packages validate real-self-apply-v1`
  - `python -m packages coverage real-self-apply-v1`

### archive 前置约束验证

在缺陷未修复且 `repair-plan` 已生成时，执行：

```bash
python -m packages archive real-self-apply-v1
```

结果：

- 归档被正式阻止
- 阻止原因为：`check_status.json.status=failed`

### 修复与关闭

将标题恢复为：

- `## 状态与反馈矩阵`

然后执行：

```bash
python -m packages gate-experience real-self-apply-v1
python -m packages validate real-self-apply-v1
python -m packages coverage real-self-apply-v1
python -m packages repair-close real-self-apply-v1
python -m packages repair-status real-self-apply-v1
python -m packages archive real-self-apply-v1
```

修复后结果：

- `repair_loop_status`：`closed`
- `open_issue_count`：`0`
- `open_blocker_count`：`0`
- `archive` 恢复可执行

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
- 黄金样例 `real-self-apply-v1` 已验证“失败 -> 计划 -> 局部修复 -> scoped rerun -> 关闭 -> 归档”闭环
- archive 已具备 repair-aware 前置约束
- 当前仓库可视为完成 P2 落地
