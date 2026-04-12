# External AI Quickstart

本文件面向外部 AI Agent。

目标是让任意能读本地文件、能执行本地命令的 AI Agent，在拿到本仓库后，按统一流程完成一次任务执行，而不是自由发挥。

## 你在这个仓库中的角色

你不是随意写文档的聊天助手，你是在使用这个仓库的任务工作台。

你必须：

- 以本地文件为正式输入输出介质
- 以 `specs/` 作为唯一正式规则真源
- 以 `projects/<project-id>/source/task_card.md` 作为任务入口
- 以 `packages/` 作为固定执行步骤入口
- 把正式结果写回 `projects/<project-id>/workspace/` 与 `projects/<project-id>/exports/`

你不得：

- 只在聊天窗口里给答案而不落盘
- 跳过 `task_card.md` 直接开始生成产物
- 把设计原则替代业务规则
- 在事实不充分时伪造结论

## 先读什么

开始任务前，按以下顺序建立理解：

1. `docs/sdd/README.md`
2. `specs/README.md`
3. `specs/01_execution_hub_spec.md`
4. `projects/<project-id>/source/task_card.md`
5. `task_card.md` 中显式引用的 `Wiki`
6. `task_card.md` 中显式引用的 `Templates`

主链路知识消费仅使用 `knowledge/wiki/topics/*.md`。  
wiki 是独立子系统，执行任务时不要改动 wiki 体系本身。

## 两种任务入口

你可能接到两种输入方式，但都必须落到同一流程里。

### 方式 A：已经有需求文档

如果用户已经提供了需求文档或背景文档：

1. 创建项目目录
2. 把需求写入 `projects/<project-id>/source/requirement.md`
3. 把背景写入 `projects/<project-id>/source/background.md`
4. 补全或确认 `projects/<project-id>/source/task_card.md`

### 方式 B：用户只是在聊天窗口里输入一段话

如果用户只给了一段聊天文本：

1. 先创建项目目录
2. 把这段聊天输入整理成正式任务输入，写入 `projects/<project-id>/source/requirement.md`
3. 如果背景不足，在 `projects/<project-id>/source/background.md` 中写入已知背景、缺失背景和待确认项
4. 补全或确认 `projects/<project-id>/source/task_card.md`

无论入口是哪一种，聊天内容都不等于正式产物。  
聊天输入必须先被整理为 `source/` 下的正式文件，再进入后续步骤。

## 项目初始化

如项目尚不存在，执行：

```bash
python -m packages bootstrap <project-id>
```

然后确认以下目录存在：

```text
projects/<project-id>/
  source/
  workspace/
  runtime/
  exports/
```

## 标准执行流程

### Step 1：确认任务协议

读取并确认：

- `projects/<project-id>/source/task_card.md`

确保至少能明确：

- 任务目标
- 必需输入
- 必需输出
- Wiki 引用
- Templates 引用
- 结果位置

### Step 2：装配上下文

执行：

```bash
python -m packages assemble <project-id>
```

这一步会解析任务卡，并生成：

- `projects/<project-id>/runtime/task_card_resolved.json`
- `projects/<project-id>/runtime/context_manifest.json`
- `projects/<project-id>/runtime/knowledge_usage_report.json`
- `projects/<project-id>/runtime/context_bundle/`

如果这一步失败，不要继续生成蓝图，先修复输入或任务卡。

### Step 3：生成事实文档

基于 `source/` 输入、`Wiki` 和模板，生成：

- `projects/<project-id>/workspace/facts.md`
- 如有必要，生成 `projects/<project-id>/workspace/gap_list.md`

要求：

- 只记录已确认事实、约束和开放问题
- 事实不充分时保留 `[GAP]`
- 不把事实阶段写成业务方案或体验方案

### Step 4：生成业务蓝图

基于 `facts.md` 与 Wiki，生成：

- `projects/<project-id>/workspace/business_blueprint.md`

要求：

- 业务蓝图必须建立在 `facts.md` 基础上
- 必须引用任务所需的 Wiki 页
- 不要提前写体验层方案
- 必须达到 business review layer 深度，而不是摘要式复述
- 至少显式输出：领域基线、合理性判断、底层逻辑一致性判断、管理策略一致性判断、能力归位判断、价值/成本/认知负担评估、备选路径比较、最终业务立场、风险与反模式、判断追踪映射
- 关键判断至少要能说明结论、依据、对比对象与剩余缺口

### Step 5：运行 facts 与 business 阶段闸门

在进入体验蓝图前，执行：

```bash
python -m packages gate-facts <project-id>
python -m packages gate-business <project-id>
```

如果任一 gate 的状态为 `failed`，不要继续写体验蓝图，先回到上一阶段补齐并重新检查。

### Step 6：生成体验蓝图

只有在 `facts` 与 `business` 阶段 gate 通过后，才生成：

- `projects/<project-id>/workspace/experience_blueprint.md`

要求：

- 体验蓝图必须建立在业务蓝图之上
- 体验蓝图必须引用设计原则
- 不得越权写成视觉设计稿、界面稿或前端实现方案
- 体验蓝图必须达到 experience architecture layer 深度，而不是只写“体验要求”
- 至少显式输出：体验目标与任务边界、体验推导依据、信息架构总览、任务流蓝图、页面 / 窗口清单、关键页面蓝图、区块布局示意、内容与信息优先级合同、状态与反馈矩阵、文案合同、风险/疑惑点与保护策略、开放问题与缺口、体验追踪映射
- 必须覆盖关键异常态、阻断态与失败反馈，不能只写 happy path
- 仅有页面清单、没有逐页展开，不视为合格体验蓝图

### Step 7：运行 experience 阶段闸门

生成完体验蓝图后，先执行：

```bash
python -m packages gate-experience <project-id>
```

如果 `experience` gate 失败，先修复体验阶段问题，再进入正式总检查。

### Step 8：运行正式检查

生成完完整输出后，执行：

```bash
python -m packages validate <project-id>
python -m packages coverage <project-id>
```

这一步会生成并更新：

- `projects/<project-id>/workspace/check_report.md`
- `projects/<project-id>/workspace/check_status.json`

状态判断以 `check_status.json` 为准。

### Step 9：根据检查结果处理

如果 `check_status.json.status` 为：

- `failed`：不得归档，必须先执行 `repair-plan`
- `warning`：可以继续，但如需正式追踪、接受或关闭 warning，应执行 `repair-plan`
- `passed`：进入归档

### Step 10：进入 Repair Loop（如需要）

当检查结果需要正式修复闭环时，执行：

```bash
python -m packages repair-plan <project-id>
```

然后：

1. 读取 `runtime/remediation/repair_summary.md`
2. 按 `runtime/remediation/remediation_plan.json` 做局部补修
3. 按 `runtime/remediation/retry_scope.json` 重跑推荐命令
4. 执行 `python -m packages repair-close <project-id>`

快速查看修复状态可运行：

```bash
python -m packages repair-status <project-id>
```

如仍存在 open blocker，不得归档。

### Step 11：归档结果

通过正式检查，且 Repair Loop 无 open blocker 后，执行：

```bash
python -m packages archive <project-id>
```

归档后结果位置为：

- 最终交付：`projects/<project-id>/exports/final/`
- 检查结果：`projects/<project-id>/exports/checks/`

## 结果应该写到哪里

执行中产物：

- `projects/<project-id>/workspace/facts.md`
- `projects/<project-id>/workspace/business_blueprint.md`
- `projects/<project-id>/workspace/experience_blueprint.md`
- `projects/<project-id>/workspace/gap_list.md`
- `projects/<project-id>/workspace/check_report.md`
- `projects/<project-id>/workspace/check_status.json`
- `projects/<project-id>/runtime/remediation/issue_index.json`
- `projects/<project-id>/runtime/remediation/remediation_plan.json`
- `projects/<project-id>/runtime/remediation/retry_scope.json`
- `projects/<project-id>/runtime/remediation/repair_summary.md`

最终查看位置：

- `projects/<project-id>/exports/final/`
- `projects/<project-id>/exports/checks/`

## 外部 Agent 的最短启动语

如果用户只给你一句启动指令，你应按下面的理解执行：

```text
请把这个仓库当作任务工作台使用。
以 specs/ 作为唯一正式规则真源，以 projects/<project-id>/source/task_card.md 作为任务入口。
如果输入只存在于聊天窗口，请先整理写入 source/requirement.md 和 source/background.md。
先运行 packages assemble 完成协议解析与上下文装配。
然后生成 facts.md 并运行 gate-facts。
再生成 business_blueprint.md 并运行 gate-business。
只有 facts 与 business 都放行后，再生成 experience_blueprint.md 并运行 gate-experience。
最后运行 validate、coverage。
如检查失败或需要正式修复闭环，则运行 repair-plan、按 retry_scope 重跑并执行 repair-close。
只有 open blocker 清零后，才能运行 archive，把正式结果写回 workspace/ 与 exports/。
```

## 一句话原则

先把聊天输入变成正式输入文件。  
先把业务阶段做稳并自检。  
正式检查通过，且 open blocker 清零后，再交付最终结果。
