# 业务蓝图 / 体验蓝图项目 v1

这是一个轻量的文档驱动型项目工作台。

它的目标不是搭建重型后端或 App，而是用稳定的本地目录、规则法典和执行中枢，支持三段主链路：

- 需求事实提炼
- 业务蓝图构建
- 体验蓝图构建

## 当前主结构

- `specs/`：唯一正式规则真源
- `packages/`：执行中枢（内含 Capability Registry 与 Memory Layer 入口）
- `projects/`：项目真相
- `memory/`：长期质量经验沉淀层
- `knowledge/`：业务真源、原则真源、Wiki 编译层
- `templates/`：固定模板
- `docs/`：解释、讨论、runbook

## 最小使用方式

```bash
python -m packages bootstrap demo-task
python -m packages assemble demo-task
python -m packages gate-facts demo-task
python -m packages gate-business demo-task
python -m packages gate-experience demo-task
python -m packages validate demo-task
python -m packages coverage demo-task
python -m packages archive demo-task
```

如需查看当前正式能力面，可运行：

```bash
python -m packages capabilities-list
python -m packages capability-show <capability-id>
```

如需提取与沉淀质量经验，可运行：

```bash
python -m packages memory-extract <project-id>
python -m packages memory-accept <project-id>
python -m packages memory-summary <project-id>
```

## 阅读顺序

1. `docs/runbook/external_ai_quickstart.md`
2. `docs/sdd/README.md`
3. `specs/README.md`
4. `projects/<project-id>/source/task_card.md`

## 说明

- `docs/sdd/` 只负责帮助理解
- `specs/` 才是正式规则
- `packages/` 是唯一固定执行入口
- `packages/capability_registry/` 负责正式能力声明，不替代真实执行逻辑
- `memory/` 是独立顶层长期 memory 子系统，不写进 wiki
- 正式产物统一位于 `projects/<project-id>/`
