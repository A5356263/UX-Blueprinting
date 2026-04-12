# P2 Implementation Backlog
**Project:** UX-Blueprinting  
**Goal:** 在现有 `specs / packages / projects / runtime / exports` 架构上，完成 P2 Repair Loop 增强  
**原则:** 增强，不重构；复用现有 gate / validate / coverage / archive；不要新增新的主阶段

---

## 0. 执行前共识（必须遵守）

- 不改变三阶段主链路：facts -> business -> experience
- 不改变项目真相层分工：`source/`、`workspace/`、`runtime/`、`exports/`
- 不引入 AI Bridge
- 不新增大批文档文件
- 优先复用现有：
  - `packages` 命令面
  - `runtime/gates/*`
  - `workspace/check_*`
  - `runtime/trace_index.json`
  - `runtime/gate_metrics.json`
- 所有新增能力必须能被现有外部 AI / IDE 工具按文件和命令消费

---

## 1. 基于当前仓库的关键事实（给施工 AI 的上下文）

### 已有命令面
当前 `python -m packages` 已暴露：
- `bootstrap`
- `assemble`
- `validate`
- `coverage`
- `gate-facts`
- `gate-business`
- `gate-experience`
- `archive`

### 已有项目真相层
每个项目以 `projects/<project-id>/` 为唯一正式入口，目录分工已经稳定：
- `source/`：输入
- `workspace/`：主产物
- `runtime/`：机器运行
- `exports/`：交付镜像

### 已有机器状态产物
当前系统已稳定生成：
- `runtime/task_card_resolved.json`
- `runtime/context_manifest.json`
- `runtime/gates/*`
- `runtime/trace_index.json`
- `runtime/gate_metrics.json`
- `workspace/check_report.md`
- `workspace/check_status.json`

### 已有黄金样例
优先以：
- `projects/real-self-apply-v1/`
作为 P2 验证样例

---

## 2. 本轮只做这 7 个任务

## Task 1 — 新增正式合同：`specs/11_repair_loop_contract.md`
### 目标
把 Repair Loop 正式纳入规则真源。

### 输入
- 已有 P2 正式方案
- 现有 `specs/01_execution_hub_spec.md`
- 现有 `specs/06_check_contract.md`

### 输出
- `specs/11_repair_loop_contract.md`

### 要求
合同必须明确：
- Repair Loop 的定位
- 输入来源
- 输出产物
- issue 模型
- remediation plan 结构
- retry scope 规则
- repair close 规则
- open blocker 不得 archive 的约束

### 完成标准
- 文件存在
- 风格与现有 `specs/*.md` 一致
- 没有引入新的主阶段
- 明确写出“增强，不重构”

---

## Task 2 — 增补 `specs/01_execution_hub_spec.md`
### 目标
把 Repair Loop 接到执行中枢主链上，但不改掉现有主链。

### 输入
- `specs/01_execution_hub_spec.md`
- `specs/11_repair_loop_contract.md`

### 输出
- 更新后的 `specs/01_execution_hub_spec.md`

### 要求
增加或更新以下内容：
- 在 validate / coverage 之后增加 Repair Loop 说明
- 新增或补充 3 个步骤：
  - `Repair Plan Build`
  - `Scoped Retry`
  - `Repair Close`
- 明确 archive 前要受 Repair Loop 状态约束

### 完成标准
- execution hub 仍然以现有主链为中心
- Repair Loop 被定义为增强层，不是第四阶段
- 文档中没有破坏现有命令链

---

## Task 3 — 增补 `specs/06_check_contract.md`
### 目标
让 check 产物不仅有“状态”，还更适合被 Repair Loop 消费。

### 输入
- `specs/06_check_contract.md`
- 当前 `workspace/check_status.json`
- 当前 `workspace/check_report.md`
- 当前 `runtime/gate_metrics.json`

### 输出
- 更新后的 `specs/06_check_contract.md`

### 要求
补充：
- check / coverage / gate 输出需要支持 issue 标准化消费
- 至少要能支持提取：
  - severity
  - category
  - evidence
  - target artifact
  - violated contract
- 明确 Markdown 是解释层，JSON 是机器真源
- 明确 blocker / warning / info 如何进入 Repair Loop

### 完成标准
- 不强制重写现有 validate 逻辑
- 但为 `repair-plan` 命令提供正式消费依据

---

## Task 4 — 扩展命令面：新增 repair 命令
### 目标
在不破坏现有命令面的前提下，给 `packages` 加 P2 命令。

### 输入
- 当前 `packages/__main__.py`

### 输出
- 更新后的 `packages/__main__.py`

### 新增命令
- `python -m packages repair-plan <project-id>`
- `python -m packages repair-status <project-id>`
- `python -m packages repair-close <project-id>`

### 要求
- 保持现有命令不变
- repair 命令只做 orchestration，不直接改业务正文
- 参数风格与当前命令面一致

### 完成标准
- 新命令可被 `python -m packages -h` 看见
- 现有命令仍正常可用

---

## Task 5 — 新增 `packages/repair_loop/` 模块
### 目标
实现 Repair Loop 的轻执行层。

### 新增目录
```text
packages/
  repair_loop/
    __init__.py
    issue_collect.py
    issue_normalize.py
    plan_build.py
    retry_scope.py
    repair_close.py
    summary_render.py
```

### 每个文件职责
- `issue_collect.py`：读取 gate/check/coverage 产物，汇总原始问题源
- `issue_normalize.py`：把问题标准化为统一 issue 模型
- `plan_build.py`：生成 `remediation_plan.json`
- `retry_scope.py`：生成 `retry_scope.json`
- `repair_close.py`：重跑后更新问题状态
- `summary_render.py`：生成人类可读摘要

### 要求
- 复用现有 `runtime/gate_metrics.json` 与 gate status/report
- 不再新造一套独立检查器
- 只做 repair orchestration

### 完成标准
运行 `repair-plan` 后至少能生成：
- `runtime/remediation/issue_index.json`
- `runtime/remediation/remediation_plan.json`
- `runtime/remediation/retry_scope.json`
- `runtime/remediation/repair_summary.md`

---

## Task 6 — 新增 runtime 修复产物目录
### 目标
在项目真相层里给 Repair Loop 一个稳定落盘位置。

### 新增目录
```text
projects/<project-id>/runtime/remediation/
```

### 固定产物
- `issue_index.json`
- `remediation_plan.json`
- `retry_scope.json`
- `repair_run_log.jsonl`
- `repair_summary.md`

### 要求
- 这些文件全部属于 `runtime/`，不要写进 `workspace/`
- `repair_summary.md` 是人读摘要
- 其余 JSON/JSONL 是机器真源
- 不改变 `workspace/` 现有主产物定义

### 完成标准
- `repair-plan` 首次运行即可自动创建目录与文件
- `repair-close` 能更新 `repair_run_log.jsonl`

---

## Task 7 — 补 runbook + 样例验证 + archive 前置约束
### 目标
把 P2 从“代码存在”变成“流程可用”。

### 输入
- `docs/runbook/task_execution_flow.md`
- `docs/runbook/external_ai_quickstart.md`
- `docs/acceptance/final-convergence-report.md`
- 黄金样例 `projects/real-self-apply-v1/`

### 输出
- 新增 `docs/runbook/repair_loop_flow.md`
- 必要时增补现有两个 runbook
- 一次完整的 P2 验证记录

### 要求
runbook 至少说明：
- 什么时候必须跑 `repair-plan`
- 如何查看 `repair_summary.md`
- 如何根据 `remediation_plan.json` 做局部补修
- 修完后如何按 `retry_scope.json` 重跑
- 如何执行 `repair-close`
- open blocker 为 0 之前不得 archive

### 验证要求
至少做 1 个失败样例：
- 人工制造一个 experience 缺陷
- 运行 `repair-plan`
- 按计划局部修复
- 运行推荐重跑
- 执行 `repair-close`
- 确认问题被关闭

### 完成标准
- 有文档
- 有验证
- archive 前置约束生效

---

## 3. 开发顺序（不要并行乱改）

### Phase 1：规则层
先做：
1. Task 1
2. Task 2
3. Task 3

### Phase 2：命令与模块层
再做：
4. Task 4
5. Task 5
6. Task 6

### Phase 3：运行与验收层
最后做：
7. Task 7

---

## 4. 明确不做的事

本轮不要做：

- 不做 AI Bridge
- 不做 Memory Layer
- 不做 Capability Registry
- 不做新的大文档体系
- 不改 `source / workspace / runtime / exports` 结构
- 不新增 facts/business/experience 之外的新主阶段
- 不搞“自动修好文档”的重型 agent 逻辑

---

## 5. 给 IDE AI 的执行方式

把下面 4 个文件一起喂给 IDE AI：

1. `P2_repair_loop_formal_upgrade_plan.md`
2. `specs/11_repair_loop_contract.md`
3. 本清单 `P2_implementation_backlog.md`
4. 当前仓库相关文件：
   - `specs/01_execution_hub_spec.md`
   - `specs/06_check_contract.md`
   - `packages/__main__.py`
   - `docs/runbook/task_execution_flow.md`
   - `docs/runbook/external_ai_quickstart.md`

然后要求它：

> 按本 backlog 顺序逐项完成；每完成一项，只改相关最少文件；每项完成后输出“改了哪些文件、为什么、如何验证”。

---

## 6. 一句话总原则

**先把规则补齐，再把命令补齐，再让运行时能落盘，最后做一次失败样例闭环验证。**
