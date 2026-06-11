# Repair Loop Contract

## Goal

定义 repair loop 如何围绕 gate / validate / coverage 暴露的问题组织修复。

## Inputs

至少读取：
- `projects/<project-id>/runtime/context_manifest.json`
- `projects/<project-id>/workspace/check_status.json`
- `projects/<project-id>/runtime/gates/facts_gate_status.json`
- `projects/<project-id>/runtime/gates/business_gate_status.json`
- `projects/<project-id>/runtime/gates/experience_gate_status.json`

如存在，也可读取：
- `projects/<project-id>/workspace/check_report.md`
- `projects/<project-id>/runtime/uxb_route_decision.json`
- `projects/<project-id>/runtime/trace_index.json`
- `projects/<project-id>/runtime/gate_metrics.json`
- `projects/<project-id>/workspace/facts.md`
- `projects/<project-id>/workspace/business_blueprint.md`
- `projects/<project-id>/workspace/experience_blueprint.md`
- `projects/<project-id>/workspace/gap_list.md`

## Outputs

至少输出：
- `projects/<project-id>/runtime/remediation/issue_index.json`
- `projects/<project-id>/runtime/remediation/remediation_plan.json`
- `projects/<project-id>/runtime/remediation/retry_scope.json`
- `projects/<project-id>/runtime/remediation/repair_summary.md`

## Constraints

- repair loop 不是新的业务阶段
- 不得重建 UXB 判断
- 不得把 blocker 伪装成 warning
- open blocker 未清零前，不得进入 archive
