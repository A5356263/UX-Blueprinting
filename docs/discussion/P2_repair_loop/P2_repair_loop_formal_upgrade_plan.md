# P2 正式改造方案：Repair Loop（修复闭环层）增强设计  
**Project:** UX-Blueprinting  
**Document Type:** Formal Enhancement Plan  
**Status:** Proposed  
**Target:** 在不改变现有项目主架构的前提下，将当前项目从“检查型文档驱动工作台”增强为“具备正式修复闭环的 harness runtime”  
**Scope:** P2 only（Repair Loop）  
**Out of Scope:** AI Bridge、外部 API 适配、长期记忆层、能力注册表的完整落地  

---

## 1. 文档目标

本方案用于正式定义 **P2: Repair Loop（修复闭环层）** 在当前仓库中的改造方式。  
目标不是重做项目，也不是引入新的 agent runtime，而是在 **现有执行中枢与三阶段主链路** 的基础上，补齐“发现问题之后如何结构化补修、如何局部返工、如何避免整篇重写”的正式能力。

本方案必须满足以下约束：

1. **不改变现有项目主架构**
2. **不改变现有三阶段主链路**
3. **不把项目改造成重型自治 Agent**
4. **保持文档驱动、合同驱动、落盘驱动**
5. **增强 harness 方法论下的反馈闭环能力**

---

## 2. 当前项目基线判断

当前项目已经具备以下基础：

- `specs/` 作为唯一正式规则真源
- `packages/` 作为唯一固定执行入口
- `projects/<project-id>/` 作为项目真相层
- 明确的 `source/ / workspace/ / runtime/ / exports/` 四层目录
- facts / business / experience 三阶段主链路
- facts / business / experience 三阶段 gate
- validate / coverage / archive 完整交付链
- `task_card_resolved.json`、`context_manifest.json`、gate 状态文件、check 状态文件等机器可读产物

这说明当前项目已经具备：

- 强合同（contract）
- 强边界（boundary）
- 强检查（check/gate）
- 强工件化（artifact persistence）
- 强阶段编排（orchestration）

但当前仍缺少一个正式的 **修复闭环层**，导致系统在失败后主要表现为：

- 能发现问题，但不能正式组织修复
- 能阻止继续推进，但不能明确指导返工路径
- 失败后容易落回“人工整篇重写”
- 缺少“局部补修 vs 全稿回退”的制度化判断
- 缺少“修复后该重跑哪些步骤”的机器可读范围

因此，P2 的核心任务不是增加更多检查，而是：

> **把当前项目从“检查型工作流”升级为“具备正式修复闭环的工作流 harness”。**

---

## 3. P2 设计目标

Repair Loop 需要实现以下 6 个正式目标：

### 3.1 目标一：把失败从“状态”升级为“可修复任务”
当前的 `failed / warning / passed` 只表达结果，不表达修复动作。  
P2 必须把失败、警告和关键信息转换为 **结构化 repair issue（修复问题）**。

### 3.2 目标二：支持局部补修，不默认整稿重写
对于深度不足、追溯缺失、异常态缺失、文案合同缺失等问题，应优先支持局部补修，而不是默认推翻当前阶段产物。

### 3.3 目标三：明确回退边界
不是所有问题都只在当前阶段修复。  
P2 必须能够判断：

- 是当前阶段局部修复即可
- 还是必须回退到上游阶段补齐
- 还是需要全链路重跑

### 3.4 目标四：建立标准化重跑范围
修复完成后，系统必须给出正式的 **retry scope（重跑范围）**，而不是靠操作者凭经验决定。

### 3.5 目标五：形成可追溯的修复记录
每次修复必须留下记录，说明：

- 修复了哪些问题
- 由谁修复
- 修复前状态
- 修复后状态
- 重跑了哪些步骤
- 哪些问题被关闭，哪些保留

### 3.6 目标六：不破坏现有主线
Repair Loop 作为增强层嵌入现有架构，不替代当前：

- `assemble`
- `gate-facts`
- `gate-business`
- `gate-experience`
- `validate`
- `coverage`
- `archive`

---

## 4. 非目标（明确不做）

本次 P2 方案明确不做以下内容：

### 4.1 不做 AI Bridge
不引入 API 代理层，不引入模型调用中间件，不依赖公网或内网模型 API。

### 4.2 不做完全自动修复
Repair Loop 不等于自动把文档修好。  
修复动作仍可以由：

- 人工编辑
- 现有 code agent 工具
- open code 平台
- 项目 skill

来完成。

Repair Loop 负责的是 **组织修复闭环**，不是取代写作本身。

### 4.3 不做新的主阶段
facts / business / experience 仍然是主阶段。  
Repair Loop 是围绕主阶段运转的增强层，不增加“第四业务阶段”。

### 4.4 不改变项目真相层分工
不改变：

- `source/` = 人读输入层
- `workspace/` = 人读结果层
- `runtime/` = 机器运行层
- `exports/` = 交付镜像层

Repair Loop 的新增内容主要进入 `runtime/`，必要时补充少量人读报告。

---

## 5. P2 在整体架构中的定位

P2 不替换当前系统，而是插入在：

- stage gate 之后
- validate / coverage 之后
- archive 之前

它的核心作用是：

> 把 gate / validate / coverage 暴露的问题转译为正式修复任务，  
> 然后将修复工作重新纳入当前工作流，而不是留在聊天层或操作者脑中。

### 当前链路
```text
assemble
  -> facts
  -> gate-facts
  -> business
  -> gate-business
  -> experience
  -> gate-experience
  -> validate
  -> coverage
  -> archive
```

### 引入 P2 之后
```text
assemble
  -> facts
  -> gate-facts
  -> business
  -> gate-business
  -> experience
  -> gate-experience
  -> validate
  -> coverage
  -> repair-plan
  -> human/agent repair action
  -> scoped rerun
  -> repair-close
  -> archive
```

如果 `repair-plan` 判定没有 open issue，可直接进入 archive。

---

## 6. P2 核心设计原则

### 6.1 合同优先
所有 Repair Loop 行为必须受 `specs/` 约束。  
P2 不是临时操作脚本，而是正式规则层的一部分。

### 6.2 局部优先
能局部修补的，不整稿重做；  
能在当前阶段修的，不回退上游；  
必须回退的，才回退。

### 6.3 追溯优先
修复必须能回答：

- 修什么
- 为什么修
- 依据哪个 gate / check / contract 修
- 修完之后如何验证

### 6.4 人机协作，不假装全自动
P2 必须承认现实：当前项目是文档驱动、人工+工具协同系统。  
它组织修复，而不伪装成完全自治系统。

### 6.5 向后兼容
已有项目在不运行 Repair Loop 的情况下仍可工作；  
P2 应增强，而不是强制打断现有链路。

### 6.6 机器可读 + 人类可读双产物
修复闭环既要有 JSON 状态，也要有 Markdown 说明。

---

## 7. 新增正式结构件

## 7.1 新增 runtime 目录

在 `projects/<project-id>/runtime/` 下新增：

```text
runtime/
  remediation/
    issue_index.json
    remediation_plan.json
    retry_scope.json
    repair_run_log.jsonl
    repair_summary.md
```

### 文件职责

#### `issue_index.json`
正式问题索引。  
聚合 gate / validate / coverage 暴露的全部 issue，并进行标准化分类。

#### `remediation_plan.json`
正式修复计划。  
说明哪些问题需要修、在哪修、谁负责修、建议修法、修后应重跑哪些步骤。

#### `retry_scope.json`
正式重跑范围。  
说明当前修复后需要重跑哪些命令，以及是否需要回退上游阶段。

#### `repair_run_log.jsonl`
修复过程日志。  
记录每一次 repair cycle 的执行信息。

#### `repair_summary.md`
人类可读的修复摘要。  
便于操作者、评审者、协作者快速看清楚当前修复状态。

---

## 7.2 新增 specs 文件

新增：

```text
specs/11_repair_loop_contract.md
```

该合同负责定义：

- issue 分类模型
- remediation plan 结构
- retry scope 规则
- 问题关闭规则
- 修复后状态判定规则
- Repair Loop 与主链路的边界

---

## 7.3 更新现有 specs

### `specs/01_execution_hub_spec.md`
增加 Step 8.5 / Step 8.6 / Step 8.7（或等价编号）：

- Repair Plan Build
- Scoped Retry
- Repair Close

### `specs/06_check_contract.md`
扩展检查合同，使其不只输出最终状态，还输出标准化 issue 数据源，供 `issue_index.json` 消费。

### 可选更新
视需要在以下合同追加“修复闭环联动说明”：

- `specs/08_fact_extraction_contract.md`
- `specs/09_business_blueprint_contract.md`
- `specs/10_experience_blueprint_contract.md`

目的不是改其主逻辑，而是补充：
- 常见失败模式
- 可局部修复项
- 必须回退项

---

## 7.4 新增 packages 命令

在 `python -m packages` 中新增以下命令：

```bash
python -m packages repair-plan <project-id>
python -m packages repair-status <project-id>
python -m packages repair-close <project-id>
```

### 命令职责

#### `repair-plan`
读取当前：

- gate 状态
- gate 报告
- `check_status.json`
- `check_report.md`
- `trace_index.json`
- `gate_metrics.json`

并生成：

- `issue_index.json`
- `remediation_plan.json`
- `retry_scope.json`
- `repair_summary.md`

#### `repair-status`
读取当前 remediation 相关产物，输出当前 open / closed / blocked 问题摘要。  
用于快速查看是否仍可继续归档。

#### `repair-close`
在操作者完成修复并按 `retry_scope.json` 重跑相关命令后，重新比对 issue 状态，关闭已解决问题，更新 `repair_summary.md` 与 `repair_run_log.jsonl`。

---

## 8. Issue 模型（正式问题模型）

Repair Loop 不是泛泛记录错误，而是使用统一 issue 模型。

## 8.1 Issue 最小字段

每个 issue 至少包含：

- `issue_id`
- `source`（facts_gate / business_gate / experience_gate / validate / coverage）
- `stage`（facts / business / experience / runtime / final）
- `severity`（blocker / warning / info）
- `category`
- `title`
- `description`
- `evidence`
- `violated_contract_refs`
- `target_artifacts`
- `repair_mode`
- `suggested_actions`
- `upstream_backtrack_required`
- `retry_scope_hint`
- `status`（open / accepted / resolved / deferred）

---

## 8.2 Issue 分类（推荐标准分类）

建议至少支持以下类别：

### A. `structure_missing`
必需结构缺失  
例如：
- 关键栏目缺失
- 页面清单缺失
- 状态矩阵缺失

### B. `boundary_violation`
阶段越权  
例如：
- facts 写成 business judgment
- experience 改写 business rules
- 输出越权进入实现层

### C. `trace_missing`
追溯关系缺失  
例如：
- facts 未被 blueprint 显式消费
- 页面设计无法追溯到 business judgment

### D. `coverage_gap`
覆盖关系不足  
例如：
- 异常态未覆盖
- 风险未落到体验保护
- facts ID 没有在下游显式引用

### E. `depth_insufficient`
深度不足  
例如：
- business 仍是摘要级复述
- experience 仍是抽象口号
- 文案合同只有标题没有语义边界

### F. `state_model_gap`
状态模型缺失  
例如：
- 没有失败态 / 阻断态
- 没有不可操作态
- 没有审批中 / 处理中状态

### G. `copy_contract_gap`
文案合同缺失或过弱

### H. `consistency_conflict`
上下游内容不一致  
例如：
- facts 与 business 立场冲突
- business 与 experience 页面承载冲突

### I. `runtime_staleness`
运行时真相过期  
例如：
- 旧 context bundle 混入新状态
- gate 状态和当前文档内容不同步

### J. `placeholder_residue`
占位内容残留

---

## 8.3 Repair Mode（修复模式）

每个 issue 必须归入以下模式之一：

- `patch_current_section`
- `patch_current_artifact`
- `regenerate_current_stage`
- `backtrack_upstream_stage`
- `rerun_checks_only`
- `accept_warning`
- `defer`

这能防止“发现问题后不知道该怎么修”。

---

## 9. 修复计划模型（Remediation Plan）

`remediation_plan.json` 是 P2 的核心产物。  
它不是问题列表，而是问题到动作的正式映射。

## 9.1 最小字段

```json
{
  "project_id": "real-self-apply-v1",
  "plan_version": "1.0",
  "generated_at": "2026-04-12T12:00:00Z",
  "open_issue_count": 4,
  "blocker_count": 1,
  "warning_count": 3,
  "repair_units": [
    {
      "unit_id": "repair-unit-001",
      "stage": "experience",
      "target_artifact": "examples/positive/real-self-apply-v1/workspace/experience_blueprint.md",
      "issue_ids": ["EXP-TRACE-001", "EXP-STATE-002"],
      "repair_mode": "patch_current_artifact",
      "repair_goal": "补齐体验追踪映射与异常状态矩阵",
      "required_inputs": [
        "workspace/facts.md",
        "workspace/business_blueprint.md",
        "workspace/experience_blueprint.md",
        "runtime/trace_index.json"
      ],
      "operator_guidance": [
        "不要整稿重写",
        "优先补‘体验追踪映射’章节",
        "补充失败态、阻断态、处理中状态"
      ],
      "completion_signal": [
        "experience gate 无相关 blocker",
        "coverage 不再报告状态覆盖缺口"
      ]
    }
  ]
}
```

---

## 9.2 Repair Unit（修复单元）
修复计划不建议按“一个问题一条命令”组织，而应按 **repair unit（修复单元）** 组织。  
一个修复单元可以合并多个同阶段、同目标文档的问题。

这样做的好处：

- 更贴近实际写作操作
- 避免 issue 太碎
- 更适合 code agent / skill / 人工编辑器工作

---

## 10. 重跑范围模型（Retry Scope）

Repair Loop 的关键不是“修完就算完”，而是修完后必须知道该重跑什么。

## 10.1 retry_scope.json 最小字段

```json
{
  "project_id": "real-self-apply-v1",
  "scope_version": "1.0",
  "recommended_commands": [
    "python -m packages gate-experience real-self-apply-v1",
    "python -m packages validate real-self-apply-v1",
    "python -m packages coverage real-self-apply-v1"
  ],
  "backtrack_required": false,
  "highest_required_stage": "experience",
  "rationale": [
    "问题集中在 experience 蓝图自身，不涉及 facts/business 回退"
  ]
}
```

---

## 10.2 标准回退规则

### 情况 A：facts 问题
如果 issue 落在 facts 且是 blocker，则至少应重跑：

```bash
python -m packages gate-facts <project-id>
python -m packages gate-business <project-id>
python -m packages gate-experience <project-id>
python -m packages validate <project-id>
python -m packages coverage <project-id>
```

必要时还应重写 business / experience 文档。

### 情况 B：business 问题
若问题只在 business 层，则至少应重跑：

```bash
python -m packages gate-business <project-id>
python -m packages gate-experience <project-id>
python -m packages validate <project-id>
python -m packages coverage <project-id>
```

必要时体验蓝图也需重构。

### 情况 C：experience 问题
若问题只在 experience 层，则重跑：

```bash
python -m packages gate-experience <project-id>
python -m packages validate <project-id>
python -m packages coverage <project-id>
```

### 情况 D：仅最终检查问题
若只是 placeholder、报告不一致、导出前检查问题，可只重跑：

```bash
python -m packages validate <project-id>
python -m packages coverage <project-id>
```

---

## 11. Repair Flow（正式修复闭环流程）

## 11.1 Phase A：Issue Collect
来源包括：

- `runtime/gates/*_gate_status.json`
- `runtime/gates/*_gate_report.md`
- `workspace/check_status.json`
- `workspace/check_report.md`
- `runtime/trace_index.json`
- `runtime/gate_metrics.json`

此阶段目标：  
把分散问题汇总为统一 `issue_index.json`。

---

## 11.2 Phase B：Issue Normalize
将不同来源的失败和警告标准化为统一 issue 模型，并打上：

- stage
- severity
- category
- repair_mode
- retry_scope_hint

---

## 11.3 Phase C：Repair Plan Build
根据 issue 模型生成：

- 修复单元
- 修复动作建议
- 局部修复 vs 上游回退判断
- 推荐重跑范围

---

## 11.4 Phase D：Human / Tool Repair
操作者使用现有工具执行修复。  
这里可以是：

- 人工编辑
- code agent 工具
- open code 平台
- 项目 skill

Repair Loop 不限定承载器，但要求：
- 修复动作必须落盘
- 不得只在聊天窗口修
- 修复目标必须对齐 remediation_plan

---

## 11.5 Phase E：Scoped Rerun
按 `retry_scope.json` 执行推荐命令，重跑相关 gate / validate / coverage。

---

## 11.6 Phase F：Repair Close
再次比对 issue 状态：

- 已不再出现 -> `resolved`
- 仍存在 -> `open`
- 被明确接受 -> `accepted`
- 暂不处理 -> `deferred`

并更新：

- `repair_run_log.jsonl`
- `repair_summary.md`

---

## 12. 与现有项目结构的融合方式

## 12.1 明确原则：增强，不重构
P2 必须作为增强层融入现有仓库结构，而不是改变现有结构。

### 不改的部分
- `specs/` 仍是唯一规则真源
- `packages/` 仍是唯一固定执行入口
- `projects/<project-id>/` 仍是项目真相层
- `source / workspace / runtime / exports` 四层语义不变
- 三阶段主链路不变

### 新增的部分
- 在 `runtime/` 下新增 `remediation/`
- 在 `packages/` 下新增 repair 相关命令
- 在 `specs/` 下新增 Repair Loop 合同
- 在 `docs/runbook/` 下补充 repair flow 使用说明

---

## 12.2 推荐目录变更

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

### 新增文档
```text
specs/
  11_repair_loop_contract.md

docs/runbook/
  repair_loop_flow.md
```

### 每个项目新增运行时目录
```text
projects/<project-id>/runtime/remediation/
```

---

## 13. 对 packages 的正式改造要求

## 13.1 `packages/__main__.py`
扩展为支持：

- `repair-plan`
- `repair-status`
- `repair-close`

但不得移除现有命令，确保兼容现有 README / runbook / acceptance 文档。

---

## 13.2 `packages.validate`
当前 validate 已具备 gate、coverage、final validation 的职责。  
P2 要求其新增或暴露：

- issue 数据提取能力
- 标准化 issue 输出能力
- 向 remediation 层提供数据源能力

注意：
- validate 仍负责检查
- remediation 层负责修复组织
- 不要把 validate 变成重型 orchestrator

---

## 13.3 `packages.repair_loop`
应保持“轻 orchestrator”定位，不直接重写文档，只做：

- issue 收集
- issue 标准化
- remediation plan 生成
- retry scope 生成
- repair close 状态更新
- 摘要渲染

---

## 14. 对 runbook 的正式改造要求

新增 `docs/runbook/repair_loop_flow.md`，明确：

1. 哪些情况下必须执行 `repair-plan`
2. 如何阅读 `repair_summary.md`
3. 如何依据 `remediation_plan.json` 进行局部补修
4. 修复后如何按 `retry_scope.json` 重跑
5. 如何执行 `repair-close`
6. 哪些 warning 允许 accept，哪些不允许
7. 何时才允许 `archive`

---

## 15. 对 stage gate 的联动改造要求

每个 gate 需要逐步从“只给最终状态”升级为“既给状态，也给结构化 issue”。

### 最低要求
每个 gate 至少应能输出：

- `issue_id`
- `severity`
- `category`
- `evidence`
- `violated_contract_ref`
- `target_artifact`

如果短期内不想改 gate status 的文件格式，允许先由 `repair-plan` 从：
- Markdown report
- JSON status
中解析并标准化。

但中期目标应是：  
让 gate 自身具备更好的结构化 issue 输出。

---

## 16. Repair Summary（人类可读摘要）建议格式

`repair_summary.md` 建议至少包含：

- 当前 open issue 总数
- blocker / warning / info 统计
- 本轮主要修复单元
- 每个修复单元目标文档
- 是否需要回退上游
- 推荐重跑命令
- 尚未关闭的问题
- 已接受 warning 清单

### 示例骨架
```md
# Repair Summary

## 当前状态
- open issues: 4
- blocker: 1
- warning: 3

## 本轮修复单元
### repair-unit-001
- target: workspace/experience_blueprint.md
- goal: 补齐追溯与异常状态
- mode: patch_current_artifact

## 推荐重跑
```bash
python -m packages gate-experience <project-id>
python -m packages validate <project-id>
python -m packages coverage <project-id>
```

## 未关闭问题
- EXP-TRACE-001
- EXP-STATE-002
```

---

## 17. 验收标准（P2 完成标准）

P2 改造可视为完成，当以下条件同时满足：

### 17.1 结构完成
- `specs/11_repair_loop_contract.md` 已建立
- `packages` 新增 repair 相关命令
- `runtime/remediation/` 产物可生成
- runbook 已补齐

### 17.2 功能完成
在一个失败样例任务上，系统可以：

1. 生成标准化 `issue_index.json`
2. 生成 `remediation_plan.json`
3. 生成 `retry_scope.json`
4. 生成人类可读 `repair_summary.md`
5. 在局部修复后，按范围重跑相关检查
6. 执行 `repair-close` 后正确关闭已修复问题

### 17.3 兼容完成
- 原有命令链不被破坏
- 原有样例项目在不运行 Repair Loop 时仍可执行
- `archive` 只在 open blocker 为 0 时继续

### 17.4 治理完成
- 有标准 issue taxonomy
- 有标准修复模式
- 有标准回退规则
- 有标准关闭规则

---

## 18. 风险与应对

## 18.1 风险：issue 过度细碎
### 后果
修复计划碎片化，操作者难以执行。

### 应对
使用 repair unit 聚合问题，而不是逐条 issue 独立修。

---

## 18.2 风险：修复计划过度保守，导致频繁整稿回退
### 后果
破坏“局部修修补补”的效率收益。

### 应对
坚持“局部优先”原则，只有追溯到上游事实/业务判断失真时才回退上游。

---

## 18.3 风险：修复后重跑范围不准
### 后果
造成假通过或重复重跑。

### 应对
将回退规则写进 `specs/11_repair_loop_contract.md`，避免由操作者临场决定。

---

## 18.4 风险：repair loop 变成另一套主流程
### 后果
系统复杂度失控。

### 应对
坚持 Repair Loop 只是增强层，不取代三阶段主链路。

---

## 19. 实施顺序（推荐）

## Phase 1：规则落地
- 编写 `specs/11_repair_loop_contract.md`
- 更新 `specs/01_execution_hub_spec.md`
- 更新 `specs/06_check_contract.md`

## Phase 2：运行时产物落地
- 先实现 `repair-plan`
- 能生成 `issue_index.json`
- 能生成 `remediation_plan.json`
- 能生成 `retry_scope.json`
- 能生成 `repair_summary.md`

## Phase 3：闭环落地
- 实现 `repair-close`
- 实现 `repair_run_log.jsonl`
- 完成 open / resolved / accepted / deferred 状态切换

## Phase 4：样例验证
- 选取一个刻意失败的样例项目
- 验证 repair loop 是否能支持局部补修
- 验证是否能避免整稿重写
- 验证是否能准确建议重跑范围

---

## 20. 最终结论

对于当前 UX-Blueprinting 项目，P2 不应理解为“再加一套 agent 能力”，而应理解为：

> **把现有 gate / validate / coverage 的问题发现能力，升级为正式的修复闭环能力。**

其价值不在于更自动，而在于：

- 返工更结构化
- 修复更局部化
- 重跑更可控
- 过程更可追溯
- 系统更贴近 harness 方法论中的反馈闭环

P2 完成后，项目将从：

> **contract-driven + gate-driven + document-driven 工作台**

进一步增强为：

> **contract-driven + repair-aware + harness-style workflow runtime**

且这一增强是在你现有项目架构基础上完成，不改变主骨架，不改变项目定位，只增强其工程反馈能力。

---

## 21. 附录：推荐新增文件总表

```text
specs/
  11_repair_loop_contract.md

docs/runbook/
  repair_loop_flow.md

packages/
  repair_loop/
    __init__.py
    issue_collect.py
    issue_normalize.py
    plan_build.py
    retry_scope.py
    repair_close.py
    summary_render.py

projects/<project-id>/runtime/
  remediation/
    issue_index.json
    remediation_plan.json
    retry_scope.json
    repair_run_log.jsonl
    repair_summary.md
```

---

## 22. 附录：推荐新增命令总表

```bash
python -m packages repair-plan <project-id>
python -m packages repair-status <project-id>
python -m packages repair-close <project-id>
```

---

## 23. 附录：一句话执行原则

**先标准化问题，再组织修复；先局部补修，再决定是否回退；修完必须按范围重跑，关闭问题后才能归档。**
