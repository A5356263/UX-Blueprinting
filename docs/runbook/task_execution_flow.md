# 任务执行流程

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
python -m packages gate-facts <project-id>
```

## Step 4

生成 `workspace/business_blueprint.md`，再运行：

```bash
python -m packages gate-business <project-id>
```

## Step 5

生成 `workspace/experience_blueprint.md`，再运行：

```bash
python -m packages gate-experience <project-id>
```

## Step 6

运行总检查：

```bash
python -m packages validate <project-id>
python -m packages coverage <project-id>
```

本步骤会额外产出：

- `runtime/trace_index.json`
- `runtime/gate_metrics.json`

## Step 7

如需生成交付镜像，再运行：

```bash
python -m packages archive <project-id>
```

## 执行约束

- 主链路知识消费仅使用 `knowledge/wiki/topics/*.md`（wiki 页）
- wiki 属于独立子系统，执行链不改动 wiki 体系本身
- `check_status.json` 为机器状态真源：`failed / warning / passed`
