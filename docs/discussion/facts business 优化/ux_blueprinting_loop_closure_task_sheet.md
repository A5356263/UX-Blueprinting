# UX-Blueprinting 第一次重构后的闭环完善工程任务单

## 1. 文档定位

这不是第二次重构任务，而是**第一次重构后的闭环完善任务**。执行目标是在**不推翻现有主链路、不重命名阶段文件、不改变阶段顺序**的前提下，补齐标准落地闭环，使 contract（合同/规范）、template（模板）、validate（校验）、gate（关卡）、runbook（运行说明）和实际产物重新一致。

## 2. 背景事实（必须作为判断前提）

1. `specs/10_experience_blueprint_contract.md` 已把体验蓝图定义为更深的 blueprint（蓝图）层，明确要求至少覆盖：体验目标与任务边界、体验推导依据、信息架构总览、任务流蓝图、页面/窗口清单、关键页面蓝图、区块布局示意、内容与信息优先级合同、状态与反馈矩阵、文案合同、风险/疑惑点与保护策略、开放问题与缺口、体验追踪映射。
2. `specs/09_business_blueprint_contract.md` 已把业务蓝图定义为 business review layer（业务审视层），要求显式输出：领域基线、合理性判断、底层逻辑一致性判断、管理策略一致性判断、能力归位判断、价值/成本/认知负担评估、备选路径比较、最终业务立场、风险与反模式、判断追踪映射。
3. 当前 `packages/validate/core.py` 中对 `experience_blueprint.md` 的必需栏目检查仍偏旧，仍以“阶段定位、体验目标、体验范围与边界、核心任务流、页面蓝图、原则引用与映射、开放问题、不进入本阶段的内容”等旧栏目为主。
4. 当前 `projects/real-self-apply-v1/runtime/gates/experience_gate_status.json` 已经 `passed`，但其 `state_feedback_pair_count = 0`、`copy_contract_item_count = 0`，说明现有 gate 会在蓝图深度明显不足时放行。

## 3. 本次任务目标

本次只做“闭环完善”，不做第二轮架构级重构。必须完成以下目标：

- 让 spec（规范）成为唯一标准源。
- 让 template（模板）完全对齐 spec，而不是半对齐。
- 让 validate/gate 按新标准拦截，而不是继续放行摘要型产物。
- 让 runbook 与执行说明不再传播旧口径。
- 让至少一个真实项目在修复后表现出“旧产物不过、新产物可过”的闭环效果。

## 4. 严格约束（不可违反）

### 4.1 不允许做的事

- 不允许把本任务升级为“第二次重构”。
- 不允许推翻第一次重构的主链路。
- 不允许更改三阶段顺序。
- 不允许更改主文件命名：`facts.md`、`business_blueprint.md`、`experience_blueprint.md`。
- 不允许绕过现有 validate/gate 体系，另起一套新检查器。
- 不允许为了让现有样例继续通过而继续降低标准。
- 不允许只补文档，不修校验。
- 不允许只修校验，不验证真实项目。

### 4.2 允许做的事

- 允许在现有文件上补齐、收紧、对齐。
- 允许修改模板、校验、关卡、运行说明。
- 允许新增少量辅助函数、测试或说明文档，但必须服务于现有主链路，而不是替代它。
- 允许对历史样例执行回归验证。

## 5. 执行原则

1. **先对齐标准，再收紧拦截，最后验证生成。**
2. **先修闭环，再谈个别项目文档优化。**
3. **所有判断以 `specs/09` 与 `specs/10` 为准，不以历史通过状态为准。**
4. **任何“旧样例还能过”的需求，都不能高于“新标准必须落地”的要求。**

## 6. 目标文件与必须修改项

### 6.1 核心修改表

| 目标文件 | 当前问题 | 必须修改点 | 完成判定 |
|---|---|---|---|
| `packages/validate/core.py` | `experience_blueprint.md` 仍按旧栏目校验；experience gate 对深度不足产物放行；部分 metric 统计方式失真且不参与失败判定 | 1) 将 `STAGE_REQUIRED_HEADINGS` 中的 `experience_blueprint.md` 必需栏目改为与 `specs/10` 同构；2) 收紧 `business_blueprint.md` 的深度检查；3) 把“关键页面蓝图、区块布局示意、内容与信息优先级合同、文案合同、体验追踪映射、异常态覆盖”设为 experience 阶段硬门槛；4) 修正 `state_feedback_pair_count`、`copy_contract_item_count` 等 metric 的真实统计逻辑；5) 让关键 metric 绑定 failed/warning 判定，而不是只记录不裁决；6) 提升最终 validate 的深度检查 | 用旧的 `real-self-apply-v1` 体验蓝图运行时，不能再得到 `passed` |
| `templates/experience_blueprint.template.md` | 模板仍保留旧标题与旧表达习惯，未完全按 `specs/10` 组织 | 改为与 `specs/10` 一致的结构；删除或下沉“阶段定位/不进入本阶段的内容”等旧导向栏目；在模板里强制出现页面级蓝图、区块布局示意、内容与信息优先级合同、文案合同、体验追踪映射 | 模板章节顺序与 `specs/10` 主结构一致 |
| `templates/business_blueprint.template.md` | 虽覆盖大部分章节，但对 judgment（判断）深度、备选路径比较、价值/成本/认知负担评估、追踪映射的约束还不够强 | 在现有基础上加强，不重写体系；要求关键判断至少包含“结论 + 依据 + 对比 + 剩余缺口”；让备选路径比较、价值/成本/认知负担评估、风险与反模式、判断追踪映射成为不可空写部分 | 模板能明确引导出 review 级业务蓝图，而不是摘要级说明 |
| `docs/runbook/external_ai_quickstart.md` | 可能继续传播旧的阶段产物口径 | 与 `specs/09`、`specs/10` 对齐，明确 business/experience 阶段输出的最小深度要求；不得再出现“体验蓝图只写体验要求”的旧说法 | runbook 与 spec 口径一致 |
| `docs/runbook/task_execution_flow.md` 及其他执行说明 | 可能仍沿用旧阶段理解，导致上游 agent 继续生成摘要型产物 | 搜索所有涉及 `business_blueprint` / `experience_blueprint` 输出要求的执行说明；凡是仍按旧标题、旧粒度描述的，全部同步到新口径 | 全仓不再存在明显旧口径执行说明 |
| 所有写死输出标题、阶段要求或 gate 条件的代码/配置 | 可能存在未被 `core.py` 覆盖的旧条件 | 全仓搜索 `experience_blueprint.md`、`business_blueprint.md`、旧标题字符串、旧 gate 指标名；发现后按同口径修正 | 不再存在同一阶段多个冲突口径 |

### 6.2 重点实现要求：`packages/validate/core.py`

必须至少完成以下实现：

1. **Experience 必需栏目更新**
   - 将 `experience_blueprint.md` 的必需栏目改为：
     - `体验目标与任务边界`
     - `体验推导依据`
     - `信息架构总览`
     - `任务流蓝图`
     - `页面 / 窗口清单`
     - `关键页面蓝图`
     - `区块布局示意`
     - `内容与信息优先级合同`
     - `状态与反馈矩阵`
     - `文案合同`
     - `风险、疑惑点与保护策略`
     - `开放问题与缺口`
     - `体验追踪映射`

2. **Experience 硬门槛补齐**
   - 缺少关键页面蓝图 => failed
   - 缺少区块布局示意 => failed
   - 缺少内容与信息优先级合同 => failed
   - 缺少文案合同 => failed
   - 缺少体验追踪映射 => failed
   - 仅有 happy path、未覆盖异常态/阻断态 => failed
   - 只有页面清单、没有逐页展开 => failed

3. **Business 深度补齐**
   - 无显式备选路径比较 => failed
   - 无价值/成本/认知负担评估 => failed
   - 无风险与反模式单列 => failed
   - 无判断追踪映射 => failed 或至少 warning，并在最终 validate 中阻断进入 experience

4. **Metric 修正**
   - 不允许继续用模板占位串来统计真实状态条目。
   - 不允许只数表头来判定文案合同存在。
   - 必须统计真实数据行或真实条目数。
   - 关键 metric 必须绑定 gate 裁决。

5. **Final validate 补强**
   - 不能只检查“文件存在 + 标题存在 + ID 被引用”。
   - 必须增加对蓝图深度的最终检查。

## 7. 搜索与排查任务

Code Agent 必须在仓库内执行一次全局搜索，并给出搜索结果摘要。至少搜索以下内容：

- `experience_blueprint.md`
- `business_blueprint.md`
- `阶段定位`
- `体验范围与边界`
- `核心任务流`
- `原则引用与映射`
- `不进入本阶段的内容`
- `copy_contract_item_count`
- `state_feedback_pair_count`
- `体验蓝图只写体验要求`
- `business judgment`
- `experience architecture layer`

搜索目标不是列结果，而是找出：

1. 哪些文件仍使用旧栏目名；
2. 哪些代码仍按旧口径做检查；
3. 哪些说明文档仍传播旧理解；
4. 是否存在多套冲突口径并存。

## 8. 验收标准

### 8.1 功能性验收

必须同时满足：

1. `templates/experience_blueprint.template.md` 与 `specs/10_experience_blueprint_contract.md` 主结构一致。
2. `templates/business_blueprint.template.md` 能明确引导出 review 级业务蓝图。
3. `packages/validate/core.py` 不再允许缺少关键页面蓝图/区块布局示意/内容与信息优先级合同/文案合同/体验追踪映射的文档通过。
4. 关键 metric 使用真实条目统计，而不是模板占位符统计。
5. `docs/runbook/external_ai_quickstart.md` 等执行说明不再传播旧口径。

### 8.2 闭环验收

必须至少完成以下两组验证：

#### A. 旧产物阻断验证

对当前 `projects/real-self-apply-v1/workspace/experience_blueprint.md` 重新运行 gate / validate：

- 预期：**不得继续 `passed`**。
- 预期：必须明确指出其缺失的蓝图深度项，而不是只给泛化 warning。

#### B. 新产物通过验证

任选一个真实项目，基于修正后的模板和校验逻辑重新生成 `business_blueprint.md` 与 `experience_blueprint.md`，然后重新运行 gate / validate：

- 预期：修正后的新产物可以通过；
- 预期：通过原因来自真实深度达标，而不是标题拼凑达标。

### 8.3 回归验收

至少回归以下对象：

- `real-self-apply-v1`
- 一个 demo 项目（如 `demo-smoke-v1` 或 `demo-permission-v1`）

预期：

- 不应破坏 facts 阶段；
- business 阶段不会因为旧摘要式写法继续误通过；
- experience 阶段不会因为旧模板结构继续误通过；
- 不应引入新的主链路断裂。

## 9. 交付物要求

Code Agent 最终必须提交以下内容：

1. 修改后的代码与文档。
2. 一份简短变更摘要，至少说明：
   - 改了哪些文件；
   - 为什么改；
   - 哪些旧口径被移除；
   - 哪些硬门槛被新增。
3. 一份验证结果摘要，至少说明：
   - 旧的 `real-self-apply-v1` 为什么现在会失败；
   - 新生成产物为什么可以通过；
   - 回归项目结果如何。

## 10. 推荐执行顺序

1. 先读 `specs/09_business_blueprint_contract.md` 与 `specs/10_experience_blueprint_contract.md`。
2. 修改两个模板。
3. 修改 `packages/validate/core.py`。
4. 全局搜索并修正旧执行说明。
5. 跑旧产物阻断验证。
6. 跑新产物通过验证。
7. 跑回归验证。
8. 输出变更摘要与验证结果。

## 11. 一句话任务结论

这次任务的本质不是“再做一次重构”，而是：

**在第一次重构已经建立的新标准基础上，把 template、validate、gate、runbook 和真实产物验收真正闭环。**
