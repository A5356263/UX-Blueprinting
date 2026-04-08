# 任务执行流程

## Step 1

创建 `projects/<project-id>/`，并把需求与背景写入 `source/`。

## Step 2

读取 `task_card.md`、Wiki、Knowledge 与模板，运行：

```bash
python -m packages assemble <project-id>
```

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

## Step 7

如需生成交付镜像，再运行：

```bash
python -m packages archive <project-id>
```
