# 任务执行流程

如需先确认当前系统正式能力面，可读取 `packages/capability_registry/`，或运行：

```bash
python -m packages capabilities-list
python -m packages capability-show <capability-id>
```

## Step 1

创建 `projects/<project-id>/`，并把需求与背景写入 `source/`。

## Step 2

读取 `task_card.md`、Wiki 与模板，运行：

```bash
python -m packages assemble <project-id>
```

本步骤会产出：

- `runtime/task_card_resolved.json`
- `runtime/context_manifest.json`
- `runtime/knowledge_usage_report.json`
- `runtime/context_bundle/`

## Step 3

生成 `workspace/facts.md`，再运行：

```bash
python -m packages generate-facts <project-id>
python -m packages gate-facts <project-id>
```

## Step 4

生成 `workspace/business_blueprint.md`，再运行：

```bash
python -m packages generate-business <project-id>
python -m packages gate-business <project-id>
```

最小深度要求：

- 必须形成 review 级业务判断，而不是 facts 摘要重写
- 必须显式包含领域基线、合理性判断、能力归位判断、价值/成本/认知负担评估、备选路径比较、风险与反模式、判断追踪映射
- 关键判断至少要能说明结论、依据、对比对象与剩余缺口

## Step 5

生成 `workspace/experience_blueprint.md`，再运行：

```bash
python -m packages generate-experience <project-id>
python -m packages gate-experience <project-id>
```

最小深度要求：

- 必须形成 experience architecture layer，而不是“体验要求”摘要
- 必须显式包含信息架构总览、任务流蓝图、页面 / 窗口清单、关键页面蓝图、区块布局示意、内容与信息优先级合同、状态与反馈矩阵、文案合同、体验追踪映射
- 必须覆盖异常态 / 阻断态，不能只写 happy path
- 仅列页面清单但不逐页展开，视为未达标

## Step 6

运行总检查：

```bash
python -m packages validate <project-id>
python -m packages coverage <project-id>
```

本步骤会额外产出：

- `runtime/trace_index.json`
- `runtime/gate_metrics.json`

## Step 6.5

如 `check_status.json.status` 为 `failed`，或存在需要正式追踪的 warning，运行：

```bash
python -m packages repair-plan <project-id>
```

本步骤会产出：

- `runtime/remediation/issue_index.json`
- `runtime/remediation/remediation_plan.json`
- `runtime/remediation/retry_scope.json`
- `runtime/remediation/repair_summary.md`

## Step 6.6

根据 `remediation_plan.json` 对正式产物做局部补修，不在聊天窗口口头声明“已修复”。

## Step 6.7

按 `retry_scope.json` 重跑推荐命令，然后执行：

```bash
python -m packages repair-close <project-id>
```

只有在 open blocker 清零后，才允许进入归档。

## Step 7

如需生成交付镜像，再运行：

```bash
python -m packages archive <project-id>
```

## Step 8

如需只补做体验蓝图浏览器预览，并向用户交付本地预览地址，运行：

```bash
python -m packages preview <project-id> --host 127.0.0.1 --port 0
```

本步骤会产出：

- `runtime/preview/index.html`
- `runtime/preview/assets/style.css`
- `runtime/preview/preview_model.json`
- `runtime/preview/preview_runtime.json`
- `runtime/preview/preview_build_log.md`

## Step 9

如需按正式主链路一次性执行 `assemble -> generate-* -> gate-* -> validate -> coverage -> archive -> preview`，运行：

```bash
python -m packages run-main <project-id>
```

如只希望主链路执行到归档，不自动补 preview，可运行：

```bash
python -m packages run-main <project-id> --skip-preview
```

## Step 10

如需校验正反样例是否仍满足回归要求，运行：

```bash
python -m packages sample-check
```

## Step 11

如需把本轮结果提炼为 quality memory，再运行：

```bash
python -m packages memory-extract <project-id>
python -m packages memory-accept <project-id>
python -m packages memory-summary <project-id>
```

本步骤会产出：

- `runtime/memory/extracted_memory_candidates.json`
- `runtime/memory/accepted_memory_items.json`
- `runtime/memory/memory_trace.json`
- `workspace/memory_summary.md`

## 执行约束

- 主链路知识消费仅使用 `knowledge/wiki/topics/*.md`（wiki 页）
- wiki 属于独立子系统，执行链不改动 wiki 体系本身
- 长期 memory 顶层独立于 wiki，正式写入 `memory/`
- `check_status.json` 为机器状态真源：`failed / warning / passed`
- 如已进入 Repair Loop，则 `runtime/remediation/issue_index.json` 与 `repair_summary.md` 共同构成 archive 前置约束
