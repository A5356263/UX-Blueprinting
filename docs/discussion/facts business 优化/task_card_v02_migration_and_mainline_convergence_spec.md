# Task Card v0.2 批量迁移与执行主线收口
## 正式任务规范文档

## 1. 任务名称
**Task Card v0.2 批量迁移与执行主线收口**

## 2. 任务目标
在不改变当前三阶段主链路的前提下，完成以下收口：

1. 将现有活跃 `projects/*/source/task_card.md` 从 `v0.1` 升级到 `v0.2`
2. 将通用 `templates/task_card.template.md` 升级到 `v0.2`
3. 将 `specs/01_execution_hub_spec.md` 升级为与当前 resolver / context assemble / validate 主线一致的执行说明
4. 确保 `task_card.md -> task_card_resolved.json -> context_manifest.json` 在新协议下稳定运行
5. 避免旧任务在 assemble（装配）阶段因协议缺口被新规则拦截

---

## 3. 任务背景
当前仓库已经进入“内容架构已升级，但任务协议入口与执行说明仍需收口”的阶段。

### 当前已完成部分
- `packages/task_card_resolve/core.py` 已把以下三段视为强制协议段：
  - `## Facts Output Requirements`
  - `## Business Output Requirements`
  - `## Experience Output Requirements`
- `packages/task_card_resolve/core.py` 已将三段解析进：
  - `facts_output_requirements`
  - `business_output_requirements`
  - `experience_output_requirements`
- `packages/context_assemble/core.py` 已开始消费这些字段，并写入：
  - `facts_extraction_boundary`
  - `business_judgment_boundary`
  - `experience_translation_boundary`
- `packages/validate/core.py` 已按新架构标题、新覆盖关系和新阶段深度进行检查

### 当前未收口部分
- 历史 task card（任务卡）实例仍有 `v0.1`
- 通用 `templates/task_card.template.md` 仍是旧协议模板
- `specs/01_execution_hub_spec.md` 仍是旧执行口径
- 因此当前存在“解析器已升级，但任务入口和执行说明未完全跟上”的新旧分叉

---

## 4. 本阶段任务边界
### 4.1 本阶段必须完成
- 批量升级活跃 `projects/*/source/task_card.md`
- 升级 `templates/task_card.template.md`
- 升级 `specs/01_execution_hub_spec.md`
- 选择至少一个已有项目进行回归验证
- 输出迁移说明文档

### 4.2 本阶段不做
- 不重写 `08 / 09 / 10` 合同
- 不重写 `facts / business / experience` 模板
- 不重写 `packages/validate/core.py`
- 不改具体业务需求内容
- 不引入新的业务知识包或设计知识包

---

## 5. 任务对象
### 5.1 需要被修改的对象
- `projects/*/source/task_card.md`
- `templates/task_card.template.md`
- `specs/01_execution_hub_spec.md`

### 5.2 需要被验证的链路
- `task_card.md`
- `runtime/task_card_resolved.json`
- `runtime/context_manifest.json`
- `runtime/gates/*.json`
- `workspace/check_report.md`
- `workspace/check_status.json`

---

## 6. 执行原则
### 6.1 协议升级优先兼容
对于历史 task card，只升级协议结构，不应随意改动任务的业务语义。

### 6.2 模板与实例一致
模板、活跃项目实例、执行中枢说明三者必须保持一致，不能继续分叉。

### 6.3 执行主线优先于文档美化
本阶段不是为了“把文档写漂亮”，而是为了确保平台默认执行链能消费新协议。

### 6.4 优先迁移活跃项目
优先升级当前仍在运行、仍会被 assemble / resolve / context assemble 调用的项目。归档项目可晚一步，但需在迁移文档中说明。

---

## 7. v0.2 协议最低要求
所有升级后的 task card 至少必须满足以下要求。

### 7.1 协议版本
- `Protocol Version：v0.2`

### 7.2 新增正式协议段
在既有必需段落之外，必须补齐：

- `## Facts Output Requirements`
- `## Business Output Requirements`
- `## Experience Output Requirements`

### 7.3 Facts Output Requirements（事实层输出要求）
至少包含：

#### Required Sections
- facts 必需章节清单

#### Recommended ID Prefixes
- facts 推荐编号前缀

#### Boundary
- facts 的知识使用边界
- 例如：
  - input-first extraction
  - knowledge only for calibration / conflict / gap identification

### 7.4 Business Output Requirements（业务层输出要求）
至少包含：

#### Required Sections
- business blueprint 必需章节清单

#### Recommended ID Prefixes
- business 推荐编号前缀

#### Boundary
- business judgment 边界
- 例如：
  - facts-first judgment
  - no UI / implementation details

### 7.5 Experience Output Requirements（体验层输出要求）
至少包含：

#### Required Sections
- experience blueprint 必需章节清单

#### Recommended ID Prefixes
- experience 推荐编号前缀

#### Boundary
- experience translation 边界
- 例如：
  - business-first translation
  - no high-fidelity visual or implementation details

---

## 8. `templates/task_card.template.md` 升级要求
升级后的模板必须满足：

1. 默认协议版本为 `v0.2`
2. 默认包含三阶段输出要求段
3. `Read Order` 明确三阶段消费顺序：
   - facts：input-first extraction
   - business：facts-first judgment
   - experience：business-first translation
4. `Constraints` 明确三阶段禁止越权规则
5. 模板结构可被 `packages/task_card_resolve/core.py` 稳定解析

---

## 9. `specs/01_execution_hub_spec.md` 升级要求
升级后的执行中枢规格应与当前主线实现保持一致。

### 9.1 Step 2: Task Card Resolve
必须明确：
- 三阶段输出要求段是正式协议的一部分
- 解析产物必须写入：
  - `facts_output_requirements`
  - `business_output_requirements`
  - `experience_output_requirements`

### 9.2 Step 3: Context Assembly
必须明确：
- 上下文装配不只是复制引用
- 还要生成三阶段边界字段：
  - `facts_extraction_boundary`
  - `business_judgment_boundary`
  - `experience_translation_boundary`

### 9.3 Step 4: Fact Extraction
必须明确：
- facts 是 structured extraction layer（结构化提取层）
- 不是摘要层
- 其输入知识边界受 task card 和 context manifest 约束

### 9.4 Step 5: Business Blueprint Build
必须明确：
- business 是 business review layer（业务审视层）
- 不是普通业务总结
- 它在 facts 之上做评审与归位判断

### 9.5 Step 6: Experience Blueprint Build / Validation
必须明确：
- experience 是 experience architecture layer（体验架构层）
- 输出应达到页面、任务流、信息架构、状态反馈、文案合同粒度
- validation 不只是结构检查，还包括 coverage（覆盖）、trace（追溯）、boundary（边界）和 depth（深度）检查

---

## 10. 推荐执行顺序
### Phase 1：升级平台默认协议入口
先改：
- `templates/task_card.template.md`
- `specs/01_execution_hub_spec.md`

目标：
- 先把平台默认入口和执行说明统一到 v0.2

### Phase 2：批量迁移项目实例
再批量改：
- `projects/*/source/task_card.md`

目标：
- 让历史任务实例和新协议兼容

### Phase 3：回归验证
至少选 1 个项目验证整条链：

推荐优先验证：
- `projects/real-self-apply-v1/`

验证链路：
1. task resolve
2. context assemble
3. facts gate
4. business gate
5. experience gate
6. validate
7. coverage

---

## 11. 正式交付物
本阶段至少应交付：

1. 升级后的 `templates/task_card.template.md`
2. 升级后的 `specs/01_execution_hub_spec.md`
3. 批量升级后的 `projects/*/source/task_card.md`
4. 一份迁移说明文档，建议命名为：
   - `docs/migrations/task-card-v0.2-migration.md`

---

## 12. 迁移说明文档最低要求
迁移说明至少需要记录：

- 哪些字段从 `v0.1` 升级到 `v0.2`
- 哪些项目 task card 被修改
- 哪些字段是新增强制字段
- 哪些字段只影响协议解析，不影响业务语义
- 哪些项目暂缓升级及原因
- 如何判断一个 task card 已完成 v0.2 迁移

---

## 13. 检查标准
### 13.1 通过标准
满足以下条件视为本阶段完成：

1. `templates/task_card.template.md` 已升级为 `v0.2`
2. `specs/01_execution_hub_spec.md` 已与当前新执行链一致
3. 所有活跃 `projects/*/source/task_card.md` 已完成 `v0.2` 升级
4. 至少一个历史项目成功跑通：
   - `task_card_resolve`
   - `context_assemble`
   - `gate/check`
5. 未因协议升级导致大面积 assemble 阶段拦截

### 13.2 Warning 标准
以下情况可带 warning 完成：

- 少量已归档项目仍为 `v0.1`，但已明确不参与执行
- 个别历史任务保留少量兼容字段，但不影响解析
- 迁移说明文档仍需补示例

### 13.3 失败标准
以下任一情况视为失败：

- 模板已升级，但历史任务未迁移，导致旧任务被拦
- 历史任务已迁移，但模板仍是旧协议
- `specs/01_execution_hub_spec.md` 未同步，导致协议与执行主线分叉
- `task_card_resolve` 无法稳定解析三阶段输出要求
- `context_assemble` 无法稳定生成三阶段边界字段

---

## 14. 本阶段完成后的下一步
本阶段完成后，下一阶段应进入：

**Task Card Resolve 与 Context Assembly 的实现细节收口 / 稳定性优化**

重点包括：
- 处理旧任务兼容分支是否仍需保留
- 进一步规范 `context_manifest.json` 的字段表达
- 对多项目批量迁移后的行为做一次统一回归
- 再进入更高阶的 compile layer（编译层）或任务自动生成能力优化

---

## 15. 一句话定义
本阶段的本质不是“补几份文档”，而是：

**把新三阶段架构正式变成平台默认协议入口，并确保旧任务实例继续可运行。**
