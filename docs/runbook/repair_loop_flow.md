# Repair Loop Flow

## 目标

说明何时进入 Repair Loop、如何读取 remediation 产物、如何完成局部补修、如何按范围重跑，以及何时允许继续 `archive`。

## 什么时候必须执行 `repair-plan`

出现以下任一情况时，必须执行：

- 任一 stage gate 状态为 `failed`
- `workspace/check_status.json.status` 为 `failed`
- 存在需要正式记录和追踪的 `warning`
- 需要把问题从“检查结果”转成“可执行修复任务”

执行命令：

```bash
python -m packages repair-plan <project-id>
```

## Repair Loop 产物位置

Repair Loop 统一落盘到：

```text
projects/<project-id>/runtime/remediation/
```

固定产物：

- `issue_index.json`
- `remediation_plan.json`
- `retry_scope.json`
- `repair_run_log.jsonl`
- `repair_summary.md`

其中机器真源以 JSON 为准，当前至少包括：

- `issue_index.json`
- `retry_scope.json`
- 各 gate / validate 状态文件中的 `issue_details`

如需在修复前确认 repair 相关正式能力，可运行：

```bash
python -m packages capabilities-list
python -m packages capability-show repair_plan
python -m packages capability-show repair_close
```

## 如何阅读 `repair_summary.md`

重点看 5 个区域：

1. `当前状态`
2. `问题统计`
3. `本轮修复单元`
4. `推荐重跑`
5. `未关闭问题`

如果 `repair_loop_status` 为：

- `idle`：当前没有 open issue
- `planned`：已有修复计划，待开始修复
- `blocked`：存在 open blocker，不得归档
- `closed`：当前 open blocker 已清零，可进入 archive 判定

## 如何依据 `remediation_plan.json` 做局部补修

原则：

- 优先局部补修，不默认整稿重写
- 只修改 `repair_units[*].target_artifact` 对应的正式产物
- 按 `operator_guidance` 修，不在聊天窗口口头声明“已修复”
- 如 issue 明确指向上游阶段失败，不要跳过回退链直接做下游重跑

建议操作顺序：

1. 先看 `repair_units[*].issue_ids`
2. 再看 `repair_goal`
3. 再看 `required_inputs`
4. 最后按 `operator_guidance` 修改正式文件

## 如何依据 `retry_scope.json` 判断回退范围

读取：

- `retry_scope.json.recommended_commands`
- `retry_scope.json.highest_required_stage`
- `retry_scope.json.backtrack_required`

当前仓库的标准重跑范围是：

- `facts` 问题：`gate-facts -> gate-business -> gate-experience -> validate -> coverage`
- `business` 问题：`gate-business -> gate-experience -> validate -> coverage`
- `experience` 问题：`gate-experience -> validate -> coverage`
- `final/runtime` 问题：`validate -> coverage`

不要凭经验自行缩小或扩大范围。  
如果 `backtrack_required=true`，必须按更高阶段的推荐链路重跑。

## 修完后如何按 `retry_scope.json` 重跑

按 `recommended_commands` 顺序串行执行。例如：

```bash
python -m packages gate-business <project-id>
python -m packages gate-experience <project-id>
python -m packages validate <project-id>
python -m packages coverage <project-id>
```

这里要求串行，不建议并行执行依赖前一步状态文件的命令。

## 如何执行 `repair-close`

在修复已落盘，且 `retry_scope.json` 推荐命令已执行后，运行：

```bash
python -m packages repair-close <project-id>
```

该命令会：

- 重新收集当前问题
- 更新 issue 状态
- 刷新 `repair_summary.md`
- 追加 `repair_run_log.jsonl`

如需快速查看当前是否还能继续归档，执行：

```bash
python -m packages repair-status <project-id>
```

如需正式把 warning 标记为接受或延期，执行：

```bash
python -m packages repair-accept <project-id> <issue-id> --reason "<accepted-reason>"
python -m packages repair-defer <project-id> <issue-id> --reason "<deferred-reason>"
```

## 哪些 warning 可以 accept

允许 `accepted` 的前提：

- 不属于 blocker
- 不影响正式归档安全
- 风险和保留理由已在 remediation 产物中可追溯
- 已完成当前轮次要求的 scoped rerun

不允许 accept 的情况：

- blocker 伪装成 warning
- 需要上游回退却未回退
- 未重跑验证就试图保留

执行方式：

```bash
python -m packages repair-accept <project-id> <issue-id> --reason "<accepted-reason>"
```

## 哪些问题可以 defer

允许 `deferred` 的前提：

- 已明确记录延期原因
- 延期不会让当前归档误判为安全
- 对 blocker 的延期会继续阻断 `archive`

不允许 defer 的情况：

- 以 defer 规避 blocker 清零要求
- 没有记录重新处理条件或下一触发点

执行方式：

```bash
python -m packages repair-defer <project-id> <issue-id> --reason "<deferred-reason>"
```

## 何时允许 `archive`

必须同时满足：

- `workspace/check_status.json.status` 不是 `failed`
- `repair-status` 显示 `open_blocker_count=0`
- 不存在 `deferred` blocker
- 若已进入 Repair Loop，则以当前 remediation 状态为准

执行：

```bash
python -m packages archive <project-id>
```

如存在 open blocker 或 deferred blocker，`archive` 会被正式拦截。

## 已验证的回退样例

`projects/real-self-apply-v1/` 已完成以下专项验证：

- facts 缺陷：临时移除 `facts.md` 的 `## 追踪映射`，验证 `retry_scope` 扩展为全链路重跑
- business 缺陷：临时移除 `business_blueprint.md` 的 `## 判断追踪映射`，验证 `retry_scope` 扩展为中段回退
- experience 缺陷：临时移除 `experience_blueprint.md` 的 `## 状态与反馈矩阵`，验证 `retry_scope` 保持 experience scoped rerun
- warning 样例：临时制造 orphan judgment，验证 `repair-defer` 与 `repair-accept` 能正式落盘状态与理由

这 3 类样例在恢复正式标题并重跑后，最终都回到：

- `check_status.json.status=passed`
- `repair_loop_status=closed`
- `open_blocker_count=0`
