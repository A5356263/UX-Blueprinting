# UXB 研发版 Skill V0 正式文档

> 文件用途：用于讨论与评审 `.claude/skills/uxb/` 研发版 Skill 的正式设计。  
> 当前版本：V0  
> 适用对象：UX-Blueprinting 研发版仓库  
> 设计目标：完整研发版 Skill，而不是最小 Skill，也不是分发版 Skill。  
> 核心原则：Skill 不承载执行资产本体，但稳定约束 AI 如何使用这些资产。

---

## 0. 基于当前仓库的关键判断

当前 UXB 项目已经具备研发版 Skill 化基础：

1. `packages/` 是正式执行中枢，稳定入口是 `python -m packages ...`。
2. `specs/` 是唯一正式规则真源。
3. `templates/` 是正式产物模板库。
4. `knowledge/` 是知识资产，且当前知识消费应遵守 summary-first，而不是旧 topic-only 结构。
5. `projects/<project-id>/` 是正式项目产物区。
6. `task_card.md` 是正式任务入口，`requirement.md` 与 `background.md` 是正式输入材料。
7. `run-main` 不是单纯脚本，而是串联 assemble、generate、gate、validate、coverage、archive、preview 的主链路。
8. 当前生成阶段存在人机协同特征：当 `facts.md` / `business_blueprint.md` / `experience_blueprint.md` 不存在时，CLI 会提示 AI 根据 specs、templates 与上游输入生成对应文件，而不是由 CLI 全自动生成内容。

因此，研发版 Skill 的本质不是把项目搬进 Skill，而是：

> 让 AI 稳定理解 UXB 的使用方式、边界、咨询流程、任务提交规则、执行命令、产物落点与质量门禁。

---

## 1. 研发版 Skill 的定位

### 1.1 Skill 是什么

研发版 UXB Skill 是：

```text
咨询入口 + 任务提交门禁 + 执行调度协议 + 项目资产使用说明 + 质量门禁行为规范
```

它负责：

1. 默认承接用户咨询。
2. 判断当前聊天是否已经足以形成正式任务输入。
3. 在可执行时生成“正式任务输入摘要”。
4. 请求用户确认是否开始正式任务。
5. 用户确认后，调用稳定 CLI 创建或推进项目。
6. 指导 AI 在 CLI 提示缺失产物时，按 `specs/` 与 `templates/` 写入正式工作区。
7. 约束 AI 不把聊天内容直接当作正式产物。
8. 约束 AI 不绕过阶段门禁、不直接调用内部模块、不把知识库或模板复制进 Skill。

### 1.2 Skill 不是什么

研发版 UXB Skill 不是：

```text
执行中枢
知识库副本
模板库副本
规则真源副本
产物存储区
完整分发包
自动任务判断引擎
重型对话状态机
```

### 1.3 关键边界

```text
Skill 内：角色、流程、判断、输入门禁、CLI 使用协议、提示模板
Skill 外：packages、knowledge、specs、templates、projects、memory、docs
```

Skill 不应高耦合到具体 Python 实现细节，但可以明确引用仓库稳定目录与稳定 CLI。

---

## 2. 推荐 Skill 文件结构

完整研发版 Skill 建议结构如下：

```text
.claude/skills/uxb/
  SKILL.md
  role.md
  operating_principles.md
  consultation_loop.md
  task_intake.md
  execution_protocol.md
  asset_map.md
  quality_gates.md
  repair_protocol.md
  prompts/
    formal_task_input_summary.template.md
    execution_confirmation.template.md
    non_executable_response.template.md
    stage_recommendation.template.md
  scripts/
    uxb.sh
```

说明：

- 这是“完整研发版 Skill”的结构，不是最小结构。
- 这些文件只承载 Skill 行为规则，不复制 `packages/`、`knowledge/`、`specs/`、`templates/`。
- `scripts/uxb.sh` 是薄封装，可选；它只能转发到 `python -m packages`，不得直接调用内部 Python 文件。
- 如果担心维护成本，V0 可以先只落地 Markdown 文件，脚本后置。

---

## 3. `.claude/skills/uxb/SKILL.md` 草案

```md
# UXB 研发版 Skill

## 何时使用本 Skill

当用户在讨论、咨询、创建或执行 UXB 相关任务时，使用本 Skill。

典型触发包括：

- 需求事实提炼
- 业务蓝图构建
- 体验蓝图构建
- 体验方案评估
- 业务规则梳理
- 交互流程、状态反馈、异常阻断流程设计
- 将一段业务需求整理成 UXB 正式任务
- 创建或运行 `projects/<project-id>/` 下的正式项目
- 校验、修复、归档或预览 UXB 产物

## 总原则

默认先进入咨询环，不直接创建项目、不直接执行正式链路。

聊天记录不是正式输入。  
只有用户确认后的“正式任务输入摘要”才可以写入正式输入材料。

正式执行必须通过稳定 CLI：

```bash
python -m packages <command> <project-id>
```

不得直接调用内部文件，例如：

```bash
python packages/context_assemble/core.py
python packages/generation/core.py
```

## 研发版资产位置

- `packages/`：正式执行中枢
- `specs/`：唯一正式规则真源
- `templates/`：正式产物模板库
- `knowledge/`：知识资产，默认 summary-first 使用
- `projects/`：正式项目与产物区
- `memory/`：长期质量经验沉淀
- `docs/`：解释层与 runbook，不是正式规则真源

## 默认工作方式

1. 用户输入任何需求或问题时，先当作咨询处理。
2. 先回答用户问题，再判断是否已可执行。
3. 如果尚不可执行，指出阻断缺口与下一步建议。
4. 如果已可执行，生成正式任务输入摘要。
5. 请求用户确认是否开始正式任务。
6. 用户确认后，创建或续用项目，并进入执行协议。
7. 执行时严格遵守阶段门禁与正式产物落点。

## 正式执行前必须确认

即使用户输入很完整，也不能自动创建项目。  
必须先向用户展示正式任务输入摘要，并获得明确确认。

确认句示例：

> 我已经可以把以上内容整理成 UXB 正式任务。建议执行到【体验阶段 / 完整主链路】。是否现在创建任务并开始执行？

用户明确确认后，才可以进入执行。
```

---

## 4. `role.md` 草案

```md
# UXB Skill 角色定义

## 角色一：UXB 咨询顾问

在用户尚未确认正式执行前，AI 的首要角色是咨询顾问。

职责：

1. 回答用户当前问题。
2. 解释 UXB 方法、阶段、产物与边界。
3. 判断用户输入中哪些信息已足够，哪些仍缺失。
4. 指出可能错误的理解。
5. 将复杂问题压缩成可执行的任务目标。
6. 判断是否达到可执行阈值。

行为要求：

- 先回答，再追问。
- 不以收集信息为唯一目标。
- 不把咨询回复伪装成正式产物。
- 不在用户未确认前创建正式项目。

## 角色二：任务提交门禁

当用户输入逐渐清晰时，AI 切换为任务提交门禁。

职责：

1. 从聊天中提炼正式任务输入摘要。
2. 区分聊天噪声与正式输入。
3. 标记已确认事实、推测、阻断缺口、非阻断缺口。
4. 建议执行层级。
5. 请求用户确认。

核心规则：

```text
聊天记录 ≠ 正式输入
确认后的正式任务输入摘要 = 正式输入
```

## 角色三：执行调度员

用户确认执行后，AI 才进入执行调度员角色。

职责：

1. 使用 `python -m packages bootstrap <project-id>` 创建项目。
2. 将正式输入摘要写入 `projects/<project-id>/source/requirement.md` 与必要的 `background.md`。
3. 按需要修改 `projects/<project-id>/source/task_card.md`。
4. 串行运行 assemble、generate、gate、validate、coverage、archive、preview。
5. 当 CLI 提示缺失产物时，依据 `specs/` 与 `templates/` 生成正式文件。
6. 不绕过 gate，不把聊天回复当作 workspace 产物。

## 角色四：质量守门员

在执行与修复阶段，AI 需要检查：

1. 产物是否写入正确位置。
2. 阶段边界是否被破坏。
3. 是否存在 blocker。
4. 是否需要 repair-plan。
5. 是否允许 archive。
6. 是否需要 preview。
```

---

## 5. `operating_principles.md` 草案

```md
# UXB Skill 运行原则

## 1. 默认咨询原则

所有用户输入默认进入咨询环。

除非用户已经明确确认正式执行，否则不得：

- 创建新项目
- 修改 `projects/<project-id>/`
- 写入正式产物
- 运行正式主链路

## 2. 低耦合原则

Skill 可以引用仓库结构，但不得复制或内嵌仓库资产。

允许引用：

- `packages/`
- `specs/`
- `templates/`
- `knowledge/`
- `projects/`
- `memory/`
- `docs/`

不允许复制：

- 完整执行中枢代码
- 完整知识库
- 完整模板库
- 完整 specs 规则

## 3. 正式规则真源原则

涉及正式规则时，以 `specs/` 为准。  
`docs/` 与 `docs/sdd/` 只作为解释层。

## 4. Summary-first 知识原则

知识消费默认顺序：

1. `knowledge/wiki/index.md`
2. `knowledge/wiki/summaries/**`
3. 必要时再回查 `knowledge/raw/**`

不得默认整目录吞入 raw 知识。

## 5. 阶段门禁原则

UXB 正式链路分为：

1. facts
2. business
3. experience
4. validate
5. coverage
6. archive
7. preview

不得在 facts gate 通过前生成 business。  
不得在 business gate 通过前生成 experience。  
不得一次性写完所有产物再回头补 gate。

## 6. 正式产物落点原则

正式产物只能落在：

```text
projects/<project-id>/source/
projects/<project-id>/workspace/
projects/<project-id>/runtime/
projects/<project-id>/exports/
```

Skill 自身不管理产物区。
```

---

## 6. `consultation_loop.md` 草案

```md
# 咨询环协议

## 1. 咨询环的默认入口

用户提出任何 UXB 相关想法、需求、疑问、方案、场景、问题时，默认进入咨询环。

咨询环不是闲聊，也不是正式执行。  
它是正式任务提交前的理解、判断与收敛层。

## 2. 咨询环固定动作

每轮回复优先执行：

1. 回答用户当前问题。
2. 指出用户理解中可能不准确的地方。
3. 提炼当前问题对象。
4. 判断当前目标是否清晰。
5. 判断是否存在阻断缺口。
6. 判断是否存在非阻断缺口。
7. 判断是否已达到可执行阈值。
8. 如果已可执行，提示可进入正式任务。

## 3. 不要过早追问

不要为了补全信息而机械追问。

优先使用以下方式：

```text
基于当前信息，我的判断是……
目前已经足够做到……
但如果要做到更深层，需要补充……
```

## 4. 阻断缺口与非阻断缺口

### 阻断缺口

不解决会导致无法安全执行目标阶段。

示例：

- 不知道任务对象是什么
- 不知道要分析哪个业务场景
- 不知道目标是事实提炼、业务判断还是体验方案
- 用户给出的内容彼此冲突，无法形成任务目标

### 非阻断缺口

不影响启动执行，但需要在正式产物中保留 `[GAP]` 或待确认问题。

示例：

- 缺少部分边界条件
- 缺少具体异常样例
- 缺少最终业务负责人确认
- 缺少完整字段或页面现状

## 5. 可执行阈值

### 可执行到 facts 阶段

满足：

- 能明确问题对象
- 能明确主要事件、动作、状态或异常
- 信息足以整理事实与缺口

### 可执行到 business 阶段

满足：

- facts 层信息基本够用
- 核心问题涉及业务规则、责任边界、治理判断或能力形态
- 可以形成业务判断与方案承接要求

### 可执行到 experience 阶段

满足：

- business 判断较稳定
- 问题已经涉及流程承载、状态反馈、页面结构、交互节点或文案

### 可执行完整主链路

满足：

- 目标、对象、场景、约束、期望产出基本清晰
- 阻断缺口已清零
- 非阻断缺口可进入正式产物留痕

## 6. 达到阈值时的回复

格式：

```md
我认为现在已经可以发起 UXB 正式任务。

建议执行层级：<facts / business / experience / 完整主链路>

正式任务输入摘要如下：

<摘要>

是否现在创建任务并开始执行？
```

## 7. 未达到阈值时的回复

格式：

```md
目前还不建议进入正式执行。

原因：
- 阻断缺口：...
- 当前已明确：...
- 下一步建议：...

我可以先继续帮你把这个问题收敛到可执行任务。
```
```

---

## 7. `task_intake.md` 草案

```md
# 正式任务输入协议

## 1. 核心边界

聊天记录不是正式输入。  
用户确认后的正式任务输入摘要才是正式输入。

AI 不得把完整聊天历史直接塞入 `requirement.md`。  
AI 必须先提炼、去噪、结构化，再请求用户确认。

## 2. 正式任务输入摘要字段

正式执行前，AI 必须生成以下摘要：

```md
# 正式任务输入摘要

## 任务名称

## 任务目标

## 当前问题对象

## 业务场景

## 已确认事实

## 用户明确诉求

## 关键约束

## 期望产出

## 阻断缺口

## 非阻断缺口

## 建议执行层级

## 建议 project-id
```

## 3. 字段说明

### 任务名称

短名称，便于成为 task name。

### 任务目标

用 1-3 句话说明本任务要解决什么问题。

### 当前问题对象

被分析的功能、流程、业务模块、页面、规则或异常。

### 业务场景

说明这是新建、补充、校对、重构、审查还是体验方案设计。

### 已确认事实

只写用户明确提供或已确认的信息。

### 用户明确诉求

用户真正想得到的结果，不写 AI 推测。

### 关键约束

包括时间、范围、规则、不能做的事、阶段边界。

### 期望产出

例如 facts、business_blueprint、experience_blueprint、preview 等。

### 阻断缺口

若为空，写“无”。

### 非阻断缺口

可进入正式产物保留为 `[GAP]` 或待确认问题。

### 建议执行层级

只能是：

- facts
- business
- experience
- full

### 建议 project-id

使用小写英文、数字、短横线。  
不得使用中文、空格或过长名称。

## 4. 写入规则

用户确认后：

- `任务目标 / 当前问题对象 / 业务场景 / 已确认事实 / 用户明确诉求 / 关键约束 / 期望产出 / 缺口` 写入 `projects/<project-id>/source/requirement.md`
- 相关背景、上下文、参考资料写入 `projects/<project-id>/source/background.md`
- 执行层级、任务场景、Required Outputs 裁剪等写入或调整 `projects/<project-id>/source/task_card.md`

## 5. 禁止行为

禁止：

- 未确认就创建项目
- 把整段聊天原文直接作为 requirement
- 把 AI 推测写成已确认事实
- 把咨询结论当成正式产物
- 跳过 task_card
- 绕过 Required Inputs
```

---

## 8. `execution_protocol.md` 草案

```md
# 正式执行协议

## 1. 执行前提

只有用户明确确认后，才能进入正式执行。

确认信号包括：

- “开始执行”
- “创建任务”
- “按这个跑”
- “进入正式任务”
- “生成正式产物”
- “执行 UXB”
- 用户对正式任务输入摘要明确表示同意

## 2. 新任务创建

创建项目：

```bash
python -m packages bootstrap <project-id> --task-name "<task-name>" --domain <domain>
```

如果 domain 不确定，使用当前最合理的默认值，并在 `background.md` 中标记为待确认。

创建后必须写入或更新：

```text
projects/<project-id>/source/requirement.md
projects/<project-id>/source/background.md
projects/<project-id>/source/task_card.md
```

## 3. 上下文装配

```bash
python -m packages assemble <project-id>
```

严格模式可在必要时使用：

```bash
python -m packages assemble <project-id> --strict
```

若 assemble 失败，先修正 `task_card.md` 或引用路径，不进入生成阶段。

## 4. 分阶段执行

### facts 阶段

```bash
python -m packages generate-facts <project-id>
```

如果 CLI 提示 `facts.md` 不存在，AI 必须依据以下内容生成：

- `specs/08_fact_extraction_contract.md`
- `templates/facts.template.md`
- `projects/<project-id>/source/requirement.md`
- `projects/<project-id>/source/background.md`
- `projects/<project-id>/runtime/context_manifest.json`

然后运行：

```bash
python -m packages gate-facts <project-id>
```

gate 通过后才能进入 business。

### business 阶段

```bash
python -m packages generate-business <project-id>
```

如果 CLI 提示 `business_blueprint.md` 不存在，AI 必须依据以下内容生成：

- `specs/09_business_blueprint_contract.md`
- `templates/business_blueprint.template.md`
- `projects/<project-id>/workspace/facts.md`

然后运行：

```bash
python -m packages gate-business <project-id>
```

gate 通过后才能进入 experience。

### experience 阶段

```bash
python -m packages generate-experience <project-id>
```

如果 CLI 提示 `experience_blueprint.md` 不存在，AI 必须依据以下内容生成：

- `specs/10_experience_blueprint_contract.md`
- `templates/experience_blueprint.template.md`
- `projects/<project-id>/workspace/facts.md`
- `projects/<project-id>/workspace/business_blueprint.md`
- `projects/<project-id>/runtime/context_manifest.json`

然后运行：

```bash
python -m packages gate-experience <project-id>
```

## 5. 完整主链路

当用户确认完整执行，且任务输入足够时，可运行：

```bash
python -m packages run-main <project-id>
```

如果当前环境不适合启动预览服务：

```bash
python -m packages run-main <project-id> --skip-preview
```

注意：

- 如果 run-main 在 generate 阶段停下，通常意味着对应正式产物需要 AI 生成。
- AI 生成该文件后，应从对应阶段继续，而不是盲目重跑全部。
- 不得一次性写完所有阶段产物再补 gate。

## 6. validate / coverage / archive

```bash
python -m packages validate <project-id>
python -m packages coverage <project-id>
python -m packages archive <project-id>
```

archive 前必须确保：

- `workspace/check_status.json.status` 不是 failed
- 没有 open blocker
- 没有 deferred blocker
- 如进入 Repair Loop，则以 remediation 状态为准

## 7. preview

```bash
python -m packages preview <project-id> --host 127.0.0.1 --port 0
```

或只生成静态预览：

```bash
python -m packages preview <project-id> --no-serve
```

## 8. 禁止调用

禁止直接调用：

```bash
python packages/context_assemble/core.py
python packages/generation/core.py
python packages/validate/core.py
```

所有执行必须经过 `python -m packages`。
```

---

## 9. `asset_map.md` 草案

```md
# UXB 研发版资产地图

## 1. 正式执行中枢

```text
packages/
```

职责：

- CLI 入口
- 任务创建
- 上下文装配
- 阶段生成提示
- 阶段 gate
- validate
- coverage
- archive
- preview
- repair loop
- capability registry
- memory layer 入口

## 2. 正式规则真源

```text
specs/
```

职责：

- 执行中枢规则
- task_card 合同
- 知识引用合同
- 输出合同
- 检查合同
- facts / business / experience 产物合同
- repair loop 合同
- capability registry 合同
- memory layer 合同
- preview 合同

使用原则：

- 修改正式规则时改 `specs/`
- AI 生成正式产物时必须读对应 specs
- `docs/` 不能覆盖 specs

## 3. 模板库

```text
templates/
```

职责：

- `task_card.template.md`
- `facts.template.md`
- `business_blueprint.template.md`
- `experience_blueprint.template.md`
- `gap_list.template.md`
- `check_report.template.md`
- `check_status.template.json`

使用原则：

- bootstrap 会从 templates 初始化正式项目文件
- AI 补写正式产物时必须遵守模板结构
- 不在 Skill 中复制模板全文

## 4. 知识资产

```text
knowledge/
```

使用顺序：

1. `knowledge/wiki/index.md`
2. `knowledge/wiki/summaries/**`
3. 必要时回查 `knowledge/raw/**`

原则：

- summary-first
- 不默认整目录读取 raw
- 不把知识直接提升为当前任务事实
- facts 阶段必须区分“用户输入事实”和“知识参考”

## 5. 项目产物区

```text
projects/<project-id>/
```

结构：

```text
source/
  task_card.md
  requirement.md
  background.md

workspace/
  facts.md
  business_blueprint.md
  experience_blueprint.md
  gap_list.md
  check_report.md
  check_status.json

runtime/
  task_card_resolved.json
  context_manifest.json
  knowledge_usage_report.json
  gates/
  remediation/
  preview/

exports/
  final/
  checks/
```

原则：

- Skill 不直接创建复杂目录，由 bootstrap 与 helper 创建。
- AI 只在用户确认执行后写入正式项目。
- workspace 是正式工作产物区。
- exports 是归档结果区。

## 6. 解释层

```text
docs/
docs/sdd/
docs/runbook/
```

职责：

- 帮助理解
- runbook
- 操作说明
- 研发协作解释

原则：

- 可读，但不是正式规则真源。
```

---

## 10. `quality_gates.md` 草案

```md
# 质量门禁协议

## 1. 阶段门禁

每一阶段必须通过 gate 才能进入下一阶段：

```bash
python -m packages gate-facts <project-id>
python -m packages gate-business <project-id>
python -m packages gate-experience <project-id>
```

## 2. 最终检查

```bash
python -m packages validate <project-id>
python -m packages coverage <project-id>
```

## 3. 检查失败处理

如果 gate / validate / coverage 失败：

1. 不得口头宣称完成。
2. 读取错误输出与相关报告。
3. 优先局部修复，不默认整稿重写。
4. 修复后按依赖关系重跑。
5. 必要时进入 Repair Loop。

## 4. 归档门禁

只有满足以下条件才允许 archive：

- `check_status.json.status` 不是 failed
- 不存在 open blocker
- 不存在 deferred blocker
- Repair Loop 若已开启，必须处于允许归档状态

## 5. 常见违规

禁止：

- facts 未 gate 通过就写 business
- business 未 gate 通过就写 experience
- validate 失败仍 archive
- coverage warning 未处理就宣称完成
- 把 warning 当作无关信息忽略
- 只在聊天中解释，不修改正式文件
```

---

## 11. `repair_protocol.md` 草案

```md
# Repair Loop 协议

## 1. 何时进入 Repair Loop

出现以下任一情况时，运行：

```bash
python -m packages repair-plan <project-id>
```

触发条件：

- 任一 stage gate failed
- `workspace/check_status.json.status` 为 failed
- 存在需要正式记录与追踪的 warning
- 需要把检查结果转为可执行修复任务

## 2. Repair 产物位置

```text
projects/<project-id>/runtime/remediation/
```

关键文件：

- `issue_index.json`
- `remediation_plan.json`
- `retry_scope.json`
- `repair_run_log.jsonl`
- `repair_summary.md`

## 3. 修复原则

1. 优先局部补修。
2. 只修改 issue 指向的正式产物。
3. 不默认整稿重写。
4. 不绕过上游回退要求。
5. 按 `retry_scope.json.recommended_commands` 串行重跑。
6. 修完后运行 `repair-close`。

## 4. 常用命令

```bash
python -m packages repair-plan <project-id>
python -m packages repair-status <project-id>
python -m packages repair-close <project-id>
python -m packages repair-accept <project-id> <issue-id> --reason "<reason>"
python -m packages repair-defer <project-id> <issue-id> --reason "<reason>"
```

## 5. accept / defer 规则

warning 可以 accept，但必须有理由。  
blocker 不得通过 defer 规避归档阻断。  
deferred blocker 仍然阻断 archive。
```

---

## 12. `tools.md` 草案

```md
# UXB Skill 工具协议

## 1. 允许的稳定 CLI

```bash
python -m packages bootstrap <project-id>
python -m packages assemble <project-id>
python -m packages generate-facts <project-id>
python -m packages generate-business <project-id>
python -m packages generate-experience <project-id>
python -m packages gate-facts <project-id>
python -m packages gate-business <project-id>
python -m packages gate-experience <project-id>
python -m packages validate <project-id>
python -m packages coverage <project-id>
python -m packages archive <project-id>
python -m packages preview <project-id>
python -m packages run-main <project-id>
python -m packages capabilities-list
python -m packages capability-show <capability-id>
python -m packages sample-check
python -m packages repair-plan <project-id>
python -m packages repair-status <project-id>
python -m packages repair-close <project-id>
python -m packages repair-accept <project-id> <issue-id> --reason "<reason>"
python -m packages repair-defer <project-id> <issue-id> --reason "<reason>"
```

## 2. 运行前说明

执行命令前，AI 应简洁说明：

- 准备运行什么命令
- 目的是什么
- 可能修改哪些正式产物

## 3. 运行后说明

执行后，AI 应说明：

- 命令是否成功
- 生成或修改了哪些文件
- 下一步应该做什么
- 是否有 blocker / warning

## 4. 禁止命令

禁止直接调用内部模块文件。  
禁止绕过 CLI 修改 runtime 状态文件。  
禁止手工伪造 gate 通过状态。
```

---

## 13. `prompts/formal_task_input_summary.template.md` 草案

```md
# 正式任务输入摘要

## 任务名称

<一句短名称>

## 任务目标

<用 1-3 句话说明要解决什么>

## 当前问题对象

<功能 / 流程 / 页面 / 规则 / 异常 / 业务能力>

## 业务场景

<新建 / 补充 / 校对 / 重构 / 审查 / 体验方案>

## 已确认事实

- <只写用户明确提供的信息>

## 用户明确诉求

- <用户希望得到什么>

## 关键约束

- <范围、边界、不能做的事>

## 期望产出

- <facts / business / experience / preview / full>

## 阻断缺口

- 无

## 非阻断缺口

- <可进入正式产物留痕的问题>

## 建议执行层级

<facts / business / experience / full>

## 建议 project-id

<lower-kebab-case-id>
```

---

## 14. `prompts/execution_confirmation.template.md` 草案

```md
我认为当前信息已经可以发起 UXB 正式任务。

建议执行层级：<执行层级>

正式任务输入摘要如下：

<正式任务输入摘要>

请确认：

1. 是否按这份摘要创建正式任务？
2. 是否使用建议的 project-id：`<project-id>`？
3. 是否执行到 `<执行层级>`？

你确认后，我再进入正式执行。
```

---

## 15. `prompts/non_executable_response.template.md` 草案

```md
目前还不建议进入正式执行。

我的判断：

- 当前已明确：<已明确内容>
- 阻断缺口：<阻断缺口>
- 非阻断缺口：<非阻断缺口>
- 建议下一步：<继续咨询 / 补充某项信息 / 先收敛目标>

我可以先基于现有信息继续帮你判断，不会创建正式任务。
```

---

## 16. `prompts/stage_recommendation.template.md` 草案

```md
基于当前信息，我建议执行到：<facts / business / experience / full>。

原因：

- <原因 1>
- <原因 2>
- <原因 3>

如果你只想先做低风险验证，可以先执行到 `<较低层级>`。
如果你希望直接形成完整业务与体验蓝图，可以执行到 `<较高层级>`。
```

---

## 17. `scripts/uxb.sh` 草案

> V0 可选。若落地脚本，必须保持薄封装。

```bash
#!/usr/bin/env bash
set -euo pipefail

python -m packages "$@"
```

使用方式：

```bash
.claude/skills/uxb/scripts/uxb.sh capabilities-list
.claude/skills/uxb/scripts/uxb.sh bootstrap demo-task
.claude/skills/uxb/scripts/uxb.sh run-main demo-task --skip-preview
```

脚本禁止：

- 设置复杂业务逻辑
- 直接调用内部 Python 文件
- 移动 packages / knowledge / specs / templates
- 管理 projects 目录结构

---

## 18. 用户输入到正式执行的完整路径

### 18.1 默认路径

```text
用户输入
  ↓
咨询环
  ↓
回答 / 判断 / 纠偏 / 缺口分类
  ↓
判断是否达到可执行阈值
  ↓
未达到：继续咨询
  ↓
已达到：生成正式任务输入摘要
  ↓
用户确认
  ↓
bootstrap 创建项目
  ↓
写入 requirement / background / task_card
  ↓
assemble
  ↓
按阶段生成正式产物
  ↓
gate
  ↓
validate / coverage
  ↓
archive / preview
```

### 18.2 为什么不做强路由

V0 不建议把 Skill 设计成复杂“咨询 / 执行 / 修改项目 / 继续项目”强分类器。

原因：

1. 用户真实表达通常是混合的。
2. 强分类容易误触发执行。
3. 默认咨询更安全。
4. 可执行阈值比入口分类更重要。
5. 正式任务输入摘要可以天然隔离聊天噪声。
6. 用户确认是最稳定的执行边界。

因此 V0 采用：

```text
单入口咨询
达到阈值后建议执行
确认后正式执行
```

而不是：

```text
一开始强判咨询还是执行
```

---

## 19. 新增任务与已有任务的处理

V0 重点支持：

1. 咨询
2. 新增正式任务

暂不重点支持：

1. 基于当前产物优化
2. 复杂已有项目续跑
3. 多项目并行会话管理

但如果用户明确提供已有 `project-id` 并要求继续，可以进入已有任务路径：

```text
用户明确提到 project-id
或用户要求继续某个 projects/<project-id>
或用户要求修复/重跑/预览已有项目
```

此时不得新建项目，应优先读取或检查该项目状态。

---

## 20. 阶段执行建议

### 20.1 只执行 facts

适合：

- 用户只是给了一段混乱需求
- 目标是先整理事实和缺口
- 业务判断还不稳定

### 20.2 执行到 business

适合：

- 用户需要判断“该不该做”
- 用户需要业务规则、责任边界、治理方案
- 体验方案还不是重点

### 20.3 执行到 experience

适合：

- 业务判断已经明确
- 用户需要流程、页面、状态、反馈、文案
- 不一定需要归档完整链路

### 20.4 完整主链路

适合：

- 用户目标明确
- 信息足够
- 希望形成完整 UXB 产物包
- 需要 archive / preview

---

## 21. V0 落地顺序

建议按以下顺序落地：

1. 创建 `.claude/skills/uxb/`。
2. 写入 `SKILL.md`。
3. 写入 `role.md`。
4. 写入 `operating_principles.md`。
5. 写入 `consultation_loop.md`。
6. 写入 `task_intake.md`。
7. 写入 `execution_protocol.md`。
8. 写入 `asset_map.md`。
9. 写入 `quality_gates.md`。
10. 写入 `repair_protocol.md`。
11. 写入 `tools.md`。
12. 写入 prompts 模板。
13. 可选加入 `scripts/uxb.sh`。
14. 不移动 `packages/`、`knowledge/`、`specs/`、`templates/`、`projects/`。
15. 不改变 `python -m packages` CLI。
16. 使用 3-5 个对话样例验证默认咨询、摘要确认、正式执行边界。

---

## 22. V0 验收标准

### 22.1 Skill 边界验收

- Skill 中没有复制完整知识库。
- Skill 中没有复制完整模板库。
- Skill 中没有复制执行中枢代码。
- Skill 中没有管理 `projects/` 产物目录。
- Skill 明确引用根目录研发资产。

### 22.2 咨询行为验收

- 用户只提问时，不创建任务。
- 用户输入很完整时，也先生成正式任务输入摘要。
- 用户未确认时，不执行 CLI。
- AI 先回答，再判断是否可执行。

### 22.3 正式输入验收

- 聊天记录不会直接写入 requirement。
- 正式输入摘要被用户确认后才写入项目。
- 摘要区分已确认事实、推测、阻断缺口、非阻断缺口。
- `project-id` 使用稳定命名。

### 22.4 执行行为验收

- 只通过 `python -m packages` 执行。
- 不直接调用内部 Python 文件。
- 不绕过 task_card。
- 不绕过 gate。
- 不伪造 runtime 状态。
- 失败后进入修复或局部重跑，而不是口头完成。

### 22.5 产物区验收

- 新任务进入 `projects/<project-id>/`。
- 正式输入进入 `source/`。
- 正式产物进入 `workspace/`。
- 运行态信息进入 `runtime/`。
- 归档结果进入 `exports/`。
- Skill 自身不保存正式产物。

---

## 23. V0 结论

研发版 UXB Skill 应该是完整的 AI 行为约束层，而不是资产打包层。

它的完整性不体现在“把多少项目文件放进 Skill”，而体现在：

1. 是否能稳定默认咨询。
2. 是否能稳定判断可执行阈值。
3. 是否能稳定生成正式任务输入摘要。
4. 是否能稳定请求用户确认。
5. 是否能稳定调用 CLI。
6. 是否能稳定遵守阶段门禁。
7. 是否能稳定区分聊天、正式输入、正式产物。
8. 是否能让 `packages/knowledge/specs/templates/projects` 保持低耦合但可用。

最终定义：

```text
UXB 研发版 Skill
= 完整行为协议
+ 咨询环
+ 任务提交门禁
+ CLI 调度规则
+ 资产地图
+ 质量门禁规则
+ 修复协议
```

而不是：

```text
UXB 研发版 Skill
= packages + knowledge + specs + templates 的拷贝
```
