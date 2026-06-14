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

## 跨平台启动建议

- 标准入口始终是 `python -m packages`
- Windows 优先使用 `python -m packages`，如果本机没有 `python`，再使用 `py -3 -m packages`
- macOS / Linux 优先使用 `python3 -m packages`
- 也可以使用仓库根目录的薄转发脚本：
  - `bash run_packages.sh <command> ...`
  - `powershell -ExecutionPolicy Bypass -File .\\run_packages.ps1 <command> ...`
- `run_packages.sh` 和 `run_packages.ps1` 只是便捷入口，不替代正式主链路

## 最小使用方式

```bash
python -m packages bootstrap demo-task --domain 权限管理
python -m packages project-structure-check demo-task
python -m packages assemble demo-task
python -m packages generate-facts demo-task
python -m packages generate-business demo-task
python -m packages generate-experience demo-task
python -m packages gate-facts demo-task
python -m packages gate-business demo-task
python -m packages gate-experience demo-task
python -m packages validate demo-task
python -m packages coverage demo-task
python -m packages preview demo-task --host 127.0.0.1 --port 0
python -m packages run-main demo-task
```

## UXB run 推荐流程

如果已经通过 `UXB`（业务与体验分析）确认进入正式蓝图任务，推荐使用：

```bash
python -m packages run <project-id> --domain 权限管理 --task-name "<task-name>"
```

后续节奏固定为：

1. 运行 `python -m packages run <project-id>`
2. 读取 `runtime/phase_state.json`
3. 只完成当前阶段主产物
4. 如需修复，只根据 `phase_state.json.preflight_errors` 或 `repair_refs` 继续修同一阶段产物
5. 再次运行 `python -m packages run <project-id>`

`run-routed-main` 继续保留，但它更偏旧的批处理入口。  
`uxb run` 更适合 `Agent` 协作式一步一推进。

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
python -m packages preview <project-id> --host 127.0.0.1 --port 0
python -m packages sample-check
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
