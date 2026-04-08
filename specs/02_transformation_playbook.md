# 仓库改造执行文档

## 目标

本文件定义本项目从“文档驱动仓库”改造成“规则法典 + 执行中枢 + 项目真相”体系的正式执行顺序。

后续优化不再按零散讨论推进，而按本文件的阶段顺序实施。

## 执行原则

- 先固化规则法典，再改实现
- 先收紧任务入口，再收紧输出与状态
- 任何阶段都不得破坏 `facts -> business_blueprint -> experience_blueprint` 主链路
- 任何阶段都不得让 `skills/` 成为唯一依赖
- 新工作一律落在 `specs/`、`packages/`、`projects/`、`knowledge/`、`templates/`、`docs/`

## Phase 0: 规则法典归位

### 目标

把执行法典提升到仓库根级 `specs/`，与解释性文档正式分层。

### 必做项

1. 使用根目录 `specs/` 作为执行法典唯一位置
2. 所有正式引用统一指向根级 `specs/`
3. 在 `README.md` 与项目总览中明确 `specs/`、`packages/`、`projects/` 的职责

### 完成标准

- 存在 `specs/README.md`
- 执行中枢规则位于 `specs/01_execution_hub_spec.md`

### 当前状态

- 已完成

## Phase 1: Task Card 协议硬化

### 目标

把 `task_card.md` 从“任务说明卡”提升为“执行中枢正式入口协议”。

### 必做项

1. 固定协议字段
2. 固定 `Protocol Name / Protocol Version / Task ID`
3. 固定 `Required Inputs / Required Outputs / Result Locations`
4. 明确 `Wiki` 是默认消费入口，`Knowledge` 是回查真源
5. 让执行中枢能把 `task_card.md` 解析为结构化 JSON

### 交付物

- `templates/task_card.template.md`
- `docs/sdd/01_task_card_spec.md`
- `specs/01_execution_hub_spec.md`
- `packages/task_card_resolve/core.py`

### 完成标准

- 任一新任务都能稳定生成符合协议的 `task_card.md`
- 执行中枢能生成 `projects/<project-id>/runtime/task_card_resolved.json`

### 当前状态

- 已完成

## Phase 2: 上下文装配收口

### 目标

让执行中枢而不是聊天记忆，成为任务上下文装配的固定入口。

### 必做项

1. Context Assembly 必须以 `task_card_resolved.json` 为输入
2. `Wiki`、`Knowledge`、`Templates`、`Checks` 的显式引用必须进入 `context_manifest.json`
3. 缺失引用必须显式失败，不允许静默降级
4. `context_bundle/` 只存放任务显式依赖，不复制无关知识

### 交付物

- `packages/context_assemble/core.py`
- `specs/01_execution_hub_spec.md`

### 完成标准

- `projects/<project-id>/runtime/context_bundle/` 可稳定重建
- `projects/<project-id>/runtime/context_manifest.json` 能解释每一个上下文来源

### 当前状态

- 已完成

## Phase 3: 检查状态标准化

### 目标

让 `check_report.md` 与 `check_status.json` 一起成为标准检查双产物。

### 必做项

1. 固定 `blocker / warning / info` 三层级
2. 明确“有 blocker 即任务未完成”
3. 把结构完整性、阶段越权、事实承接纳入标准检查项
4. 机器可读状态文件必须正式产出，不再作为可选项

### 交付物

- `templates/check_report.template.md`
- `templates/check_status.template.json`
- `docs/sdd/05_check_rules_spec.md`
- `packages/validate/core.py`

### 完成标准

- 任一任务结束后都能产出标准 `check_report.md`
- 任一任务结束后都能产出标准 `check_status.json`
- 人和执行中枢都不需要依赖聊天记录判断任务是否完成

### 当前状态

- 已完成

## Phase 4: 项目真相迁移

### 目标

把任务输入、执行中产物、运行时文件和交付结果统一收进 `projects/<project-id>/`。

### 必做项

1. 新任务只允许进入 `projects/`
2. `source/` 只承载任务输入与协议
3. `workspace/` 只承载执行中的正式产物
4. `runtime/` 只承载解析结果、上下文快照与运行时文件
5. `exports/final/` 作为最终交付区
6. `exports/checks/` 作为正式检查区

### 交付物

- `projects/_template/`
- `projects/<project-id>/...`
- `packages/task_bootstrap/core.py`
- `packages/archive/core.py`

### 完成标准

- 设计师只需查看 `projects/<project-id>/workspace/` 与 `projects/<project-id>/exports/`
- 结果不再散落在旧的根级目录

### 当前状态

- 进行中
- `demo-permission-v1` 已完成首个迁移试点

## Phase 5: 执行中枢收敛

### 目标

把固定逻辑全部收敛到 `packages/`，不再保留平行兼容壳。

### 必做项

1. 执行中枢固定能力包括：
   - task bootstrap
   - task card resolve
   - context assemble
   - validate
   - archive
2. AI 推理能力仍只负责：
   - fact extraction
   - blueprint build
3. 旧入口不再继续维护

### 交付物

- `packages/`
- `python -m packages ...` 入口

### 完成标准

- 固定逻辑不再散落在平行目录
- 新工作不再新增平行兼容层

### 当前状态

- 进行中
- 旧兼容入口已删除

## Phase 6: 持续迁移与收尾

### 目标

用真实项目持续验证 `packages + projects` 主线，并逐步消化遗留内容。

### 必做项

1. 逐个把现有任务迁入 `projects/`
2. 修正模板、知识引用和归档内容中的旧路径
3. 保持 `specs/` 与 `packages/` 的同步收紧

### 完成标准

- 所有活跃项目都在 `projects/`
- 规范、模板与试点项目不再引用旧目录

### 当前状态

- 进行中

## 当前立即执行项

当前阶段继续按下面顺序推进：

1. 清理所有活跃规范中的旧目录引用
2. 继续完成 `projects/` 试点迁移
3. 在后续真实项目中只使用 `python -m packages ...`

## 结束判定

当以下条件同时满足时，可认为本轮改造达到可用状态：

- `specs/` 成为唯一正式执行法典入口
- `packages/` 成为唯一固定逻辑实现入口
- `projects/` 成为唯一项目真相入口
- `task_card.md` 已成为稳定协议入口
- `check_report.md` 与 `check_status.json` 已成为稳定完成判断依据
