# P3 Implementation Backlog
**Project:** UX-Blueprinting  
**Goal:** 在现有执行中枢基础上，落地 Memory Layer（记忆层）  
**原则:** 增强，不重构；memory 与 wiki 解耦；长期 memory 顶层独立；项目级摘要面向用户

---

## 0. 执行前共识（必须遵守）

- 不改变 facts / business / experience 三阶段主链
- 不改变 `source / workspace / runtime / exports` 分层
- 不把 memory 做进 `knowledge/wiki/`
- 不直接复制完整 blueprint 作为长期 memory
- 不让 AI 自动捏造主观偏好
- 先搭 memory 骨架，再做内容补充
- `workspace/memory_summary.md` 必须作为用户可读入口

---

## 1. 基于当前仓库的关键事实（给施工 AI 的上下文）

### 当前主骨架已稳定
- `specs/`：唯一正式规则真源
- `packages/`：执行中枢
- `projects/`：项目真相层
- `docs/`：解释与 runbook

### 当前任务协议支持 Domain
`specs/03_task_card_contract.md` 已明确 `task_card` 中可解析 `Domain` 字段。  
这为 P3 的领域归类提供第一优先证据。

### 当前 `knowledge/wiki/` 是独立子系统
`specs/07_wiki_contract.md` 明确：
- wiki 承担长期知识沉淀与跨任务复用
- 但不替代 facts / business / experience

因此 P3 不应直接写进 wiki。

### 当前项目真相层分工已稳定
`projects/README.md` 已明确：
- `workspace/` 给人看
- `runtime/` 给机器跑

因此：
- `runtime/memory/` 适合机器候选产物
- `workspace/memory_summary.md` 适合用户摘要

### 当前已有 P2 / P4
因此 P3 可以消费：
- repair loop 暴露的 issue / remediation
- capability registry 暴露的 capability 对象

---

## 2. 本轮只做这 7 个任务

## Task 1 — 新增正式合同：`specs/13_memory_layer_contract.md`
### 目标
把 Memory Layer 正式纳入规则真源。

### 输入
- `specs/03_task_card_contract.md`
- `specs/07_wiki_contract.md`
- `specs/11_repair_loop_contract.md`
- `specs/12_capability_registry_contract.md`
- 当前 P3 总方案文档

### 输出
- `specs/13_memory_layer_contract.md`

### 要求
合同必须明确：
- Memory Layer 的定位
- 与 wiki 的边界
- 长期 memory 顶层落点
- 项目级 runtime memory 落点
- `workspace/memory_summary.md` 的作用
- Memory 对象模型
- generic / domain / task_type 分类规则
- preference 骨架要求
- 不允许整篇 blueprint 直接入长期 memory

### 完成标准
- 文件存在
- 风格与现有 `specs/*.md` 一致
- 明确写出“Memory 不耦合 wiki”

---

## Task 2 — 新增顶层 `memory/` 子系统骨架
### 目标
建立独立于 `knowledge/wiki/` 的长期 memory 子系统。

### 新增目录
```text
memory/
  README.md
  index.json
  patterns/
    generic/
    permission/
    organization/
    enterprise_security/
    personal_account/
  failure_modes/
    generic/
    permission/
    organization/
    enterprise_security/
    personal_account/
  preferences/
    quality_preferences.md
    preference_rules.yaml
  capability_insights/
```

### 要求
- `memory/` 位于仓库根目录
- 不放进 `projects/`
- 不放进 `knowledge/wiki/`
- 目录语义清楚、独立

### 完成标准
- 顶层目录存在
- 领域骨架已预建
- 偏好骨架已预建，但正文可为空模板

---

## Task 3 — 新增项目级 `runtime/memory/`
### 目标
让每次任务都能提取本轮候选 memory。

### 新增目录
```text
projects/<project-id>/runtime/memory/
```

### 固定产物
- `extracted_memory_candidates.json`
- `accepted_memory_items.json`
- `memory_trace.json`

### 要求
- 这些文件全部属于 `runtime/`
- 机器真源不写进 `workspace/`
- 先支持结构存在，首轮不要求复杂自动提取

### 完成标准
- 项目运行后可以生成这些文件
- 不影响现有主产物结构

---

## Task 4 — 新增用户摘要：`workspace/memory_summary.md`
### 目标
给用户一个明确的 Memory 查看入口。

### 输出
- `projects/<project-id>/workspace/memory_summary.md`

### 要求
至少包含：
- 本次新增的通用模式
- 本次新增的领域模式
- 本次识别的失败模式
- 本次新增的 capability insight
- 进入长期 memory 的条目
- 仅作为候选的条目
- 当前偏好骨架位置

### 完成标准
- 文件存在
- 用户能直接从 `workspace/` 看见
- 不作为机器真源

---

## Task 5 — 新增 `packages/memory_layer/` 模块
### 目标
提供 P3 的轻执行层。

### 新增目录
```text
packages/
  memory_layer/
    __init__.py
    extract_candidates.py
    classify_memory.py
    accept_memory.py
    write_memory_summary.py
    memory_index.py
```

### 每个文件职责
- `extract_candidates.py`：从任务结果、repair、capability 使用记录提取候选 memory
- `classify_memory.py`：给候选 memory 打 scope / domain / task_type / confidence
- `accept_memory.py`：把 accepted memory 写入长期 `memory/`
- `write_memory_summary.py`：生成 `workspace/memory_summary.md`
- `memory_index.py`：维护 `memory/index.json`

### 要求
- 首轮做轻执行层，不做重型数据库
- 先支持文件系统落盘
- 不直接更改 facts / business / experience 主产物

### 完成标准
- 运行后能产生 candidate、accepted、summary 三类结果
- 可维护长期 memory 索引

---

## Task 6 — 定义 Memory 查询/生成入口（轻量）
### 目标
让 P3 有正式命令入口。

### 推荐新增命令
```bash
python -m packages memory-extract <project-id>
python -m packages memory-accept <project-id>
python -m packages memory-summary <project-id>
```

### 最低要求
- `memory-extract`：生成项目级 candidate
- `memory-accept`：把 accepted 条目写入顶层 `memory/`
- `memory-summary`：生成/刷新 `workspace/memory_summary.md`

### 要求
- 保持现有命令不变
- 命令面风格与当前 `packages` 一致
- 只做 memory 相关工作，不替代主流程执行

### 完成标准
- 命令可见
- 不破坏现有命令链
- 产物可落盘

---

## Task 7 — 补 runbook 与示例验证
### 目标
让 P3 不只是有结构，还能被使用。

### 新增文档
- `docs/runbook/memory_layer_flow.md`

### 至少说明
- Memory Layer 是什么
- 为什么不放进 wiki
- 为什么长期 memory 放顶层 `memory/`
- 如何从项目运行结果中提取 candidate
- 如何接受 memory 进入长期层
- 如何查看 `workspace/memory_summary.md`
- 如何后续人工补充 `preferences/quality_preferences.md`

### 最低验证要求
至少选一个已通过或已修复的样例任务，验证：
1. 能生成 candidate
2. 能把一条 generic pattern 接受到长期 memory
3. 能把一条 domain pattern（permission）接收到长期 memory
4. 能生成 `workspace/memory_summary.md`

### 完成标准
- runbook 存在
- 有一次样例验证记录
- 用户和 AI 都能按文档理解 P3

---

## 3. 开发顺序（不要并行乱改）

### Phase 1：规则层
先做：
1. Task 1

### Phase 2：结构层
再做：
2. Task 2
3. Task 3
4. Task 4

### Phase 3：执行层
再做：
5. Task 5
6. Task 6

### Phase 4：验证层
最后做：
7. Task 7

---

## 4. 明确不做的事

本轮不要做：

- 不做聊天记忆
- 不做向量数据库优先方案
- 不做 AI Bridge
- 不做 wiki memory 融合
- 不把整篇样例直接当长期 memory
- 不自动填充你的主观偏好内容
- 不改变项目真相层与主链路结构

---

## 5. 给 code agent 的执行方式

把下面材料一起喂给 code agent：

1. `P3_memory_layer_formal_upgrade_plan.md`
2. `specs/13_memory_layer_contract.md`
3. 本清单 `P3_implementation_backlog.md`
4. 当前仓库相关文件：
   - `README.md`
   - `packages/README.md`
   - `projects/README.md`
   - `specs/01_execution_hub_spec.md`
   - `specs/03_task_card_contract.md`
   - `specs/07_wiki_contract.md`
   - `specs/11_repair_loop_contract.md`
   - `specs/12_capability_registry_contract.md`
   - `docs/runbook/external_ai_quickstart.md`
   - `docs/runbook/task_execution_flow.md`
   - `docs/runbook/repair_loop_flow.md`

然后要求它：

> 先理解当前项目骨架；严格保持 memory 与 wiki 解耦；按本 backlog 顺序逐项完成；每完成一项只改最少相关文件；每项完成后输出“改了哪些文件、为什么、如何验证”。

---

## 6. 一句话总原则

**长期 memory 顶层独立，项目级 memory 候选留在 runtime，用户只看 workspace/memory_summary；先沉淀可复用模式，再逐步丰富内容。**
