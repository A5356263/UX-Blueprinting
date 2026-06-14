# UXB Run Orchestrator Contract

## Goal

定义 `python -m packages run <project-id>` 作为面向 `Agent`（智能体）协作的阶段级运行中控入口。

第二期目标不是增强 `uxb run`，而是把它收回到：

- 阶段状态读取
- 阶段产物检查
- 自动工程检查
- 同阶段修复承接
- 同次 `run` 阶段切换

它不是第二个大脑，也不是细粒度任务派发器。

## Positioning

`uxb run` 只负责：

- 读取结构化运行状态
- 判断当前所处阶段
- 判断当前阶段主产物是否已可检查
- 自动执行已有工程命令
- 在同一次 `run` 中完成阶段切换
- 在失败时进入同阶段修复模式

`uxb run` 不负责：

- 重新判断复杂度
- 重新选择知识
- 重新决定 `full / standard / fast` 执行模式
- 读取长正文后做新的语义判断
- 在阶段内继续拆很多小动作
- 生成 `agent_next_task.md` 这类细粒度任务卡

## Runtime Products

第二期运行时核心产物收敛为：

- `projects/<project-id>/runtime/phase_state.json`
- `projects/<project-id>/runtime/stage_context.json`
- `projects/<project-id>/runtime/uxb_run_history.jsonl`
- `projects/<project-id>/runtime/gates/`
- `projects/<project-id>/runtime/remediation/`（仅失败或修复时出现）

必须删除或停写这些第一期往返载体：

- `projects/<project-id>/runtime/current_action.json`
- `projects/<project-id>/runtime/agent_next_task.md`
- `projects/<project-id>/runtime/agent_task_status.json`
- `projects/<project-id>/runtime/uxb_run_report.json`

## State Split

### `uxb_route_decision.json`

`uxb_route_decision.json` 属于 `Skill`（技能分析阶段）真相。

它：

- 由分析阶段写入
- 供正式主链路消费
- 不得被后续 `uxb run` 覆盖

第二期不允许把它并入 `phase_state.json`。

### `phase_state.json`

`phase_state.json` 是运行阶段唯一状态单，只给 `Agent` 看。

至少包含：

- `schema_version`
- `project_id`
- `phase`
- `status`
- `target_artifact`
- `template_refs`
- `rule_refs`
- `preflight_errors`
- `repair_mode`
- `repair_refs`
- `warnings`
- `updated_at`

`phase_state.json` 只表达当前阶段。
它不承载分析阶段真相，也不承载完整上下文装配清单。

### `stage_context.json`

`stage_context.json` 是系统运行上下文单，只给系统看。

至少包含：

- `schema_version`
- `project_id`
- `phase`
- `context`
- `execution_trace`
- `accumulated_warnings`
- `updated_at`

边界：

- `phase_state.json` 负责给 `Agent` 的最小阶段指针
- `stage_context.json` 负责系统上下文与工序流水
- 两者不得重复堆同一批“给 Agent 的模板/规则说明”

## Stage Rules

第二期只允许这些阶段：

- `formal`
- `facts`
- `business`
- `experience`
- `final`

不允许新增：

- 小阶段
- 过渡阶段
- 修复子阶段
- 临时阶段

修复不是新阶段，而是同阶段的 `repair_mode=true`。

## Planner Boundary

`planner.py` 只能做阶段级判断：

- 当前在哪个阶段
- 当前阶段主产物是什么
- 当前阶段是否可进入检查
- 当前阶段是否进入同阶段修复
- 当前阶段通过后应切到哪个下一阶段

`planner.py` 禁止做：

- 阶段内下一步动作判断
- 动态跳步
- 动态改顺序
- 基于正文质量决定放行
- 新的知识选择
- 新的复杂度判断
- warning 主观放行

## Phase Entry Order

进入新阶段时，顺序必须固定：

1. `uxb run` 判断进入哪个阶段
2. `uxb run` 先写 `phase_state.json` 第一笔
3. 第一笔必须写清：
   - 当前阶段
   - 目标产物路径
   - 模板路径
   - 规则路径
4. `Agent` 启动时先读 `phase_state.json`
5. `Agent` 按当前阶段交付主产物
6. 再次运行 `uxb run`

禁止让 `Agent` 自己猜“现在该写什么”。

## Completion Signal

第二期不再依赖 `agent_task_status.json` 回执。

当前阶段“可继续推进”的信号是：

- 当前阶段主产物已写出
- `preflight_check` 通过
- 当前阶段可进入 `gate`

也就是：

`Agent` 不再说“我做完了”，而是系统根据阶段产物和机械检查自动判断。

## Preflight Rules

`executor.py` 在跑任何：

- `gate`
- `validate`
- `coverage`
- `repair-plan`

之前，必须先做机械 `preflight_check`，只允许检查：

- 文件存在
- `JSON` 合法
- 必填章节存在
- 无占位符残留
- `provenance`（工序来源记录）可自动补齐

禁止把 `preflight_check` 做成内容质量判断器。

### Preflight Error Depth

`preflight_errors` 只允许放机械缺项，例如：

- 缺少必填章节
- 存在占位符
- JSON 非法
- 目标产物缺失

如果问题来自深层 `gate / validate / coverage` 结论，不得压扁写进 `preflight_errors`，而应通过 `repair_refs` 指向 `remediation/` 下的详细文件。

## Provenance / Execution Trace

`execution_trace` 的唯一来源是：

- `packages/provenance.py`

第二期禁止在 `uxb run` 中重写一套 hash 计算逻辑。

时机必须固定为：

- `executor.py`
- 在跑 `gate / validate / coverage / repair-plan` 之前
- 先调用 `provenance.py` 现有写入入口
- 再执行 `preflight_check` 后续检查

`execution_trace` 是系统责任，不再由 `Agent` 手写。

## Warnings

如果检查结果是：

- 有 `blocker`（阻断项） -> `needs_revision`
- 无 `blocker` 但有 `warning`（警告） -> `passed_with_warnings`
- 无 `blocker` 且无 `warning` -> `passed`

`warning` 不自动进入修复循环。

持久化规则：

- `phase_state.json.warnings` 只保留当前阶段 warning
- `stage_context.json.accumulated_warnings` 负责跨阶段累计 warning
- `uxb_run_history.jsonl` 保留每次运行的原始 warning 记录

不得依赖 `phase_state.json` 跨阶段保留 warning。

## Repair Mode

修复仍保留：

- `repair-plan`
- `remediation/`
- `retry_scope`

但不再生成新的任务卡。

规则：

- 当前阶段失败时，`phase_state.json` 更新为 `repair_mode=true`
- `repair_refs` 直接指向 `remediation/` 下的修复文件
- `Agent` 继续修同一个阶段主产物
- 修完后再次运行 `uxb run`

修复是同阶段修复，不是新阶段，也不是新一轮细粒度派单。

## Same-Run Phase Switch

当前阶段 `gate` 通过后：

- `uxb run` 必须在同一次调用里直接写入下一阶段 `phase_state.json`
- 写完后就停止

禁止要求 `Agent` 再额外跑一次 `uxb run` 才切下一阶段。

## CLI Responsibility

`cli.py` 必须纳入第二期改造范围。

它负责：

- 阶段级主循环
- 当前阶段自动检查
- 同次 `run` 阶段切换
- 同阶段修复模式承接

它不再负责：

- 任务卡主循环
- 回执文件驱动
- 细粒度 ready/retry 往返

## Relationship With Routed Main

`run-routed-main` 继续保留。

关系是：

- `run-routed-main`：旧批处理主链路入口
- `uxb run`：面向 `Agent` 的阶段级运行调度入口

第二期不把 `uxb run` 写成新的全能主链路。

## Acceptance

必须同时满足：

- `runtime/` 控制文件数明显减少
- 删除第一期任务卡与回执载体
- `uxb_route_decision.json` 保持独立
- `phase_state.json` 成为运行阶段唯一状态单
- `stage_context.json` 承接 `execution_trace + accumulated_warnings`
- `planner.py` 只保留阶段判断
- 自动化只保留机械检查
- 删除任一新增调度逻辑后，不影响主链路语义正确性，只影响流程便利性

如果文件数没降、往返没减、阶段内判断仍然很多，就视为第二期未达标。
