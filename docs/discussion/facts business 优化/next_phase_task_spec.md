# 下一步任务正式规范
## 任务名称
**Task Card v0.2（任务卡 v0.2 协议）升级与执行主线收口**

## 任务目标
在不改变当前三阶段主链路的前提下，将仓库中的任务协议入口与执行中枢说明同步升级到新架构版本，确保：

- 旧任务不会因新规则在 assemble（装配）阶段被拦截
- 新任务默认按 v0.2（版本 0.2）协议生成
- 执行中枢说明与当前 `facts（事实层）`、`business blueprint（业务蓝图层）`、`experience blueprint（体验蓝图层）` 的新合同、新模板、新 gate/check（关卡/检查）保持一致

---

## 当前判断
当前仓库已经完成了大部分“阶段内容架构”的升级，但“任务协议入口”和“执行主线说明”仍未完全收口，表现为：

1. 历史任务仍存在 `Protocol Version: v0.1（协议版本 0.1）`
2. 通用 `templates/task_card.template.md` 仍是旧协议结构
3. `specs/01_execution_hub_spec.md` 仍采用旧执行口径
4. `packages/validate/core.py` 已经开始按新架构检查，因此如果协议入口不升级，后续执行链会出现新旧不一致

---

## 本阶段任务范围
本阶段将 **1 和 2 合并执行**，统一视为同一个正式改造任务。

### A. 批量升级现有任务卡
将现有 `projects/*/source/task_card.md` 批量升级到 **v0.2（版本 0.2）协议**。

目标不是改业务内容，而是补齐协议层字段，使历史任务在新执行链下仍可运行。

### B. 升级通用任务卡模板
升级：

- `templates/task_card.template.md`

使新建任务默认生成 v0.2（版本 0.2）协议结构。

### C. 升级执行中枢规格
升级：

- `specs/01_execution_hub_spec.md`

使执行中枢的 Step 2 / Step 3 / Step 4 / Step 5 / Step 6 与当前新架构一致。

---

## 不在本阶段范围
以下内容不作为本阶段主任务：

- 重写 08 / 09 / 10 合同
- 重写 facts / business / experience 三份模板
- 重写 `packages/validate/core.py`
- 重写单个业务项目的需求内容本身
- 引入新的业务知识包或设计知识包

如果执行过程中发现这些内容仍需微调，只允许做最小兼容修正，不应在本阶段扩成新任务。

---

## 改造原则

### 1. 协议升级优先兼容
对于现有 `projects/*/source/task_card.md`，优先补齐 v0.2（版本 0.2）协议结构，不应随意改动任务本身的业务语义。

### 2. 模板与实例一致
`templates/task_card.template.md` 必须与升级后的历史 task card（任务卡）结构一致，不能出现模板和实例协议分叉。

### 3. 执行说明必须承接新架构
`specs/01_execution_hub_spec.md` 必须明确：

- facts = structured extraction layer（结构化提取层）
- business = business review layer（业务审视层）
- experience = experience architecture layer（体验架构层）
- validation = gate/check + coverage（关卡/检查 + 覆盖检查）

### 4. 不做“只改文档不改入口”
本阶段不是纯文档美化，而是执行入口收口。任何升级都必须以“可被执行中枢消费”为准。

---

## v0.2 协议最低要求
升级后的 task card（任务卡）至少应满足以下新增要求：

### 协议版本
- `Protocol Version: v0.2`

### 新增正式段落
除既有强制段外，新增以下正式协议段：

- `## Facts Output Requirements`
- `## Business Output Requirements`
- `## Experience Output Requirements`

### facts（事实层）最低内容
至少应明确：

- required sections（必需章节）
- recommended id prefixes（推荐编号前缀）
- boundary（知识使用边界）

### business（业务层）最低内容
至少应明确：

- required sections（必需章节）
- recommended id prefixes（推荐编号前缀）
- judgment boundary（判断边界）

### experience（体验层）最低内容
至少应明确：

- required sections（必需章节）
- recommended id prefixes（推荐编号前缀）
- translation boundary（转译边界）

---

## `templates/task_card.template.md` 升级要求
升级后的模板必须具备：

1. 默认协议版本为 `v0.2`
2. 显式保留三阶段输出要求段
3. `Read Order（阅读顺序）` 中体现三阶段边界：
   - facts（事实层）先 input-first extraction（输入优先提取）
   - business（业务层）先 facts-first judgment（事实优先判断）
   - experience（体验层）先 business-first translation（业务优先转译）
4. `Constraints（约束）` 中体现三阶段禁止越权规则
5. 模板结构可被 Task Card Resolve（任务卡解析）稳定解析为机器字段

---

## `specs/01_execution_hub_spec.md` 升级要求
升级后的执行中枢规格至少应完成以下同步：

### Step 2: Task Card Resolve（任务卡解析）
应把三阶段输出要求段视为正式协议的一部分，并要求解析进：

- `task_card_resolved.json`

### Step 3: Context Assembly（上下文装配）
应要求生成三阶段边界字段：

- `facts_extraction_boundary`
- `business_judgment_boundary`
- `experience_translation_boundary`

### Step 4: Fact Extraction（事实提炼）
应明确 facts（事实层）是 **structured extraction layer（结构化提取层）**，而非摘要层。

### Step 5: Business Blueprint Build（业务蓝图构建）
应明确 business（业务层）是 **business review layer（业务审视层）**，而非普通业务总结。

### Step 6: Experience Blueprint Build / Validation（体验蓝图构建 / 检查）
应明确 experience（体验层）是 **experience architecture layer（体验架构层）**，输出应达到页面、任务流、信息架构、状态反馈、文案合同粒度。

---

## 推荐执行顺序
本阶段建议按以下顺序执行：

### Phase 1（阶段 1）
先升级：

- `templates/task_card.template.md`
- `specs/01_execution_hub_spec.md`

目的：先把平台默认入口和执行说明定死。

### Phase 2（阶段 2）
再批量升级：

- `projects/*/source/task_card.md`

目的：让历史任务实例与新模板、新执行规则对齐。

### Phase 3（阶段 3）
用至少一个历史项目回归检查：

- `task_card.md`
- `task_card_resolved.json`
- `context_manifest.json`
- gate/check（关卡/检查）链路

推荐优先使用：

- `projects/real-self-apply-v1/`

---

## 正式交付物
本阶段至少应产出：

1. 升级后的 `templates/task_card.template.md`
2. 升级后的 `specs/01_execution_hub_spec.md`
3. 批量升级后的 `projects/*/source/task_card.md`
4. 一份迁移说明文档，建议命名为：
   - `docs/migrations/task-card-v0.2-migration.md`

---

## 迁移说明文档最低内容
迁移说明至少应写清楚：

- 哪些字段从 v0.1（版本 0.1）升级到 v0.2（版本 0.2）
- 哪些历史任务被批量修改
- 哪些字段是新增强制字段
- 哪些字段只影响协议解析，不影响业务含义
- 如何判断一个 task card（任务卡） 已经完成 v0.2 升级

---

## 检查标准

### 通过标准
满足以下条件可视为本阶段完成：

1. 通用 `task_card.template.md` 已升级到 v0.2（版本 0.2）
2. `specs/01_execution_hub_spec.md` 已与新三阶段架构一致
3. 所有活跃 `projects/*/source/task_card.md` 已完成 v0.2 升级
4. 至少一个历史项目能成功跑通：
   - Task Card Resolve（任务卡解析）
   - Context Assembly（上下文装配）
   - gate/check（关卡/检查）
5. 未出现因新协议导致的大面积 assemble（装配）拦截

### 警告标准
以下情况可带 warning（警告）完成：

- 少量归档项目暂未升级，但已明确不参与执行
- 个别历史 task card（任务卡）保留兼容字段，但不影响解析
- 迁移说明文档仍需补充示例

### 失败标准
以下任一情况应视为失败：

- 模板升级了，但历史任务未升级，导致旧任务被阻断
- 历史任务升级了，但模板仍是旧协议
- 执行中枢规格未同步，导致协议与执行链分叉
- Task Card Resolve（任务卡解析）无法稳定产出新字段
- Context Assembly（上下文装配）无法稳定产出三阶段边界

---

## 本阶段完成后的下一步
当本阶段完成后，下一阶段应进入：

**Task Card Resolve（任务卡解析）与 Context Assembly（上下文装配）执行实现收口**

也就是：
- 不再只改协议文本
- 而是把 `task_card.md -> task_card_resolved.json -> context_manifest.json` 真正做成平台默认执行链

---

## 一句话定义
本阶段的本质不是“补文档”，而是：

**把新架构正式变成平台默认协议入口，并确保旧任务能继续运行。**
