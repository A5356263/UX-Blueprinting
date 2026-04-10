# 从 85% 到 100% 的最终收口任务规范
## 正式规范文档

## 1. 任务名称
**黄金样例重跑、运行时真相刷新与最终验收收口**

## 2. 任务目标
在当前架构层、协议层、执行层已基本完成升级的前提下，完成最后一轮“真相收口”，把仓库状态从约 85% 完成度推进到 100% 可验收状态。

本阶段的核心目标不是再扩写规格，而是：

1. 让仓库内的静态协议真相与运行时真相完全一致
2. 让至少一个活跃项目成为可复跑、可验证、可演示的 golden sample（黄金样例）
3. 清理或重生成所有已过时的 runtime / workspace / gate 产物
4. 完成一轮端到端验收，证明新主线不是“文档已升级”，而是“实际可运行并可交付”

## 3. 当前状态判断
截至当前主分支，以下层已经基本成立：

### 3.1 已基本完成的层
- `templates/task_card.template.md` 已升级到 `v0.2`，并包含三阶段输出要求与边界
- `specs/01_execution_hub_spec.md` 已升级到新主线执行口径
- `packages/task_card_resolve/core.py` 已要求并解析三阶段输出要求
- `packages/context_assemble/core.py` 已消费三阶段输出要求并生成三阶段边界
- `packages/validate/core.py` 已按新标题、新边界、新覆盖逻辑执行检查

### 3.2 当前仍未闭环的层
- 活跃项目的 `runtime/` 中仍存在旧运行结果
- 活跃项目的 `workspace/` 中仍存在旧结构样例产物
- gate/check 的结果仍在基于旧产物给出 warning
- `context_manifest.json` 中仍可能保留本地绝对路径与目录级知识引用

因此，本阶段不再定义新法典，而是完成：

**运行结果、样例产物与验收状态的最终闭环。**

## 4. 本阶段边界

### 4.1 本阶段必须完成
1. 选定 1 个黄金样例项目并全链路重跑
2. 刷新该项目全部 runtime 真相
3. 刷新该项目全部 workspace 真相
4. 刷新 gate/check/coverage 结果
5. 清理或替换所有已过时的生成型产物
6. 输出一份最终验收说明文档

### 4.2 本阶段不做
- 不重写 08/09/10 合同
- 不重写 facts / business / experience 模板
- 不继续扩写 task card 协议
- 不新增新的业务域知识包
- 不在本阶段引入新的 compile engine（编译引擎）能力

## 5. 黄金样例定义

### 5.1 黄金样例项目
优先选择：

- `projects/real-self-apply-v1/`

原因：
- 它已经完成了 `task_card.md` 的 `v0.2` 协议迁移
- 它当前仍是最适合承接新主线验证的权限域样例
- 它暴露出了最典型的“协议升级了，但 runtime / workspace 还未刷新”的问题

### 5.2 黄金样例必须满足
一个样例要被视为黄金样例，至少必须同时满足：

1. `source/` 是当前新协议
2. `runtime/` 全部产物由当前主线重新生成
3. `workspace/` 全部产物符合当前新模板与新合同
4. `runtime/gates/` 反映新输出而不是旧样例残留
5. `check_report.md` 与 `check_status.json` 一致
6. 至少达到：
   - 零 blocker
   - warning 显著减少，最好为零
7. 他人可以按 README / 命令链复跑得到同类型结果

## 6. 本阶段核心任务

### Task 1：黄金样例全链路重跑
对 `projects/real-self-apply-v1/` 重新执行完整主线：

1. `task_card_resolve`
2. `context_assemble`
3. facts 生成
4. `gate-facts`
5. business 生成
6. `gate-business`
7. experience 生成
8. `gate-experience`
9. `validate`
10. `coverage`
11. `archive`

### Task 2：刷新运行时真相
以下文件必须以“当前代码主线”重新生成，不允许继续沿用旧文件：

- `runtime/task_card_resolved.json`
- `runtime/context_manifest.json`
- `runtime/gates/*.json`
- `runtime/gates/*.md`
- `workspace/check_report.md`
- `workspace/check_status.json`

### Task 3：刷新工作区真相
以下样例输出必须以新模板、新合同重生成：

- `workspace/facts.md`
- `workspace/business_blueprint.md`
- `workspace/experience_blueprint.md`
- `workspace/gap_list.md`

目标不是“存在文件”，而是文件结构必须真正符合当前新主线。

### Task 4：解决 facts 阶段残留 warning
重点解决 facts gate 当前暴露出的典型问题：

- 旧结构标题未替换
- 缺少规则标识（R-xx）
- 缺少状态标识（S-xx）
- 缺少动作标识（A-xx）
- 缺少异常标识（EX-xx）
- 缺少依赖标识（D-xx）
- 缺少范围标识（SC-xx）
- 追踪映射不足

目标是让 `facts.md` 真正进入 structured extraction layer（结构化提取层）形态。

### Task 5：解决 business / experience 旧结构残留
当前样例中的 `business_blueprint.md`、`experience_blueprint.md` 仍是旧式结构输出，需要重生成为：

- business review layer（业务审视层）
- experience architecture layer（体验架构层）

重点不是改几行标题，而是让内容结构真正匹配：
- judgment framework（判断框架）
- option comparison（方案比较）
- task flow（任务流）
- page blueprint（页面蓝图）
- state and feedback matrix（状态与反馈矩阵）
- copy contract（文案合同）

### Task 6：清理过时生成型产物
以下内容若已经被新主线重生成，应允许删除旧版本或直接覆盖：

- 旧版本 `runtime/task_card_resolved.json`
- 旧版本 `runtime/context_manifest.json`
- 旧版本 `runtime/gates/*.json`
- 旧版本 `workspace/check_report.md`
- 旧版本 `workspace/check_status.json`
- 旧结构的 `facts.md`
- 旧结构的 `business_blueprint.md`
- 旧结构的 `experience_blueprint.md`

### Task 7：清理运行时不稳定信息
本阶段必须处理以下不稳定信息：

1. `context_manifest.json` 中的本地绝对路径
2. 目录级知识引用过宽问题
3. 旧路径命名或旧引用残留
4. 仓库中“新协议 + 旧运行结果”并存造成的误导

### Task 8：输出最终验收文档
新增一份最终收口说明，建议命名为：

- `docs/acceptance/final-convergence-report.md`

至少说明：
- 哪个项目被用作黄金样例
- 这次重跑刷新了哪些文件
- 哪些历史生成物被清理
- 最终 blocker / warning 状态
- 是否可以将本轮优化视为完成

## 7. 推荐执行顺序

### Phase A：先重跑，不先修报告
先完整重跑黄金样例，让 runtime / workspace 真相先刷新出来。

### Phase B：再处理剩余 warning
在拿到新产物后，逐项修 facts/business/experience 的 warning，而不是先手工改 gate 结果。

### Phase C：再清旧产物
在新结果稳定后，再删除或覆盖旧生成型文件。

### Phase D：最后补最终验收文档
确保仓库最终留下的是“新主线的真相”，不是“历史过渡状态”。

## 8. 正式交付物
本阶段至少应交付：

1. 完整重跑后的 `projects/real-self-apply-v1/`
2. 刷新后的：
   - `runtime/task_card_resolved.json`
   - `runtime/context_manifest.json`
   - `runtime/gates/*.json`
   - `workspace/check_report.md`
   - `workspace/check_status.json`
3. 刷新后的：
   - `workspace/facts.md`
   - `workspace/business_blueprint.md`
   - `workspace/experience_blueprint.md`
4. 一份最终验收说明：
   - `docs/acceptance/final-convergence-report.md`

## 9. 通过标准

### 9.1 通过
满足以下条件视为从 85% 到 100% 完成：

1. 黄金样例已按当前主线完整重跑
2. `runtime/` 中不再保留旧协议残留真相
3. `workspace/` 中不再保留旧结构样例真相
4. `facts / business / experience` 三份输出与当前新合同、新模板一致
5. gate/check/coverage 结果与当前新样例一致
6. `check_report.md` 与 `check_status.json` 状态一致
7. 没有本地绝对路径残留在标准运行时真相中
8. 目录级知识引用问题已被收敛或被明确记录为可接受 warning
9. 最终验收文档已输出

### 9.2 Warning
以下情况可带 warning 完成：

- 尚存在少量非阻断性知识引用过宽
- 某些说明性 runtime 字段仍需后续格式优化
- 黄金样例仍保留极少量不影响主线理解的 warning

### 9.3 失败
以下任一情况视为未完成：

- `source/` 已升级但 `runtime/` 仍是旧协议产物
- `workspace/` 仍是旧结构样例
- `facts gate` / `business gate` / `experience gate` 仍明显暴露旧模板残留
- `check_report.md` 与 `check_status.json` 不一致
- 仍有关键 blocker
- 无法给出一个“当前主线可复跑、可演示、可验收”的黄金样例

## 10. 本阶段完成后的状态
当本阶段完成后，整个优化任务应可正式视为完成，并进入下一类任务：

- compile layer（编译层）能力增强
- 自动生成质量提升
- 跨业务域扩展
- 多样例体系建设

也就是说，只有完成这一轮收口之后，才适合继续往“更高能力”推进。

## 11. 一句话定义
**这一步不是再升级规则，而是把仓库中所有仍然停留在过渡态的旧运行真相刷新为新主线真相，并完成最终验收闭环。**
