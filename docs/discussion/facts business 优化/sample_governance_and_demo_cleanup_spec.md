# 活跃样例收口与遗留 Demo 治理
## 正式任务规范文档

## 1. 任务名称
**活跃样例收口与遗留 Demo（演示项目）治理**

## 2. 任务目标
在当前新主线已经基本成型的前提下，对 `projects/` 下的样例项目进行统一治理，完成以下目标：

1. 明确哪些 demo（演示项目）继续保留，哪些进入 archive（归档），哪些可以删除
2. 将保留的活跃样例项目收口为“可复跑、可验证、可演示”的标准样例
3. 清理旧协议、旧命名、旧 runtime（运行时）产物与旧 gate/check（关卡/检查）痕迹
4. 为后续真实项目提供一个稳定的 golden sample（黄金样例）和一个 lightweight smoke sample（轻量冒烟样例）
5. 降低仓库内“新主线已经升级，但样例真相仍然混杂”的认知成本

---

## 3. 当前判断

### 3.1 `demo-permission-v1` 的作用
当前不建议删除。

原因：

- 它的 README 明确写了：该项目用于演示权限域任务在 `projects/` 主线下的完整执行，并给出了完整复跑命令链 fileciteturn58file7L1-L1
- 改造执行文档中也明确写了：`demo-permission-v1` 是 `projects/` 目录下“首个迁移试点” fileciteturn59file2L1-L1

因此，它当前的角色更接近：

- migration pilot（迁移试点）
- end-to-end sample（全链路样例）
- golden demo（黄金演示样例）

结论：
**现在不应删除，应该优先收口成标准样例。**

### 3.2 `demo-smoke-v1` 的作用
当前不建议直接删除，但它更适合被重新定位。

从仓库现状看：

- 它的 `source/task_card.md` 已经升级到 `v0.2`，说明协议层已经迁移 fileciteturn58file0L1-L1
- 但它的 `runtime/task_card_resolved.json` 仍然是 `v0.1` 结构，说明该项目迁移后没有按新主线完整重跑 fileciteturn58file4L1-L1
- 它的 `runtime/context_manifest.json` 也仍是旧知识路径与旧上下文形态 fileciteturn58file5L1-L1
- 它的 facts gate（事实关卡）仍带 warning（警告） fileciteturn58file18L1-L1

因此，它当前的角色更像：

- smoke sample（冒烟样例）
- lightweight validation case（轻量验证用例）
- migration-not-closed sample（迁移未收口样例）

结论：
**不建议现在直接删。更合理的做法是先决定：要么升级为正式 smoke sample，要么归档后删除。**

### 3.3 为什么现在不适合直接删
因为这两个项目目前分别承担了两类不同价值：

- `demo-permission-v1`：证明“完整主线能跑”
- `demo-smoke-v1`：证明“轻量样例能快速验证”

如果在没有替代物之前直接删除，仓库会丢掉：
- 一个迁移试点真相
- 一个轻量回归样例

---

## 4. 本阶段任务边界

### 4.1 本阶段必须完成
1. 给现有 demo 项目明确分类：
   - 保留
   - 归档
   - 删除候选
2. 把 `demo-permission-v1` 收口为标准黄金样例
3. 对 `demo-smoke-v1` 做明确处置：
   - 升级为轻量 smoke sample
   - 或归档后退出活跃项目集合
4. 清理 demo 项目中的旧 runtime / 旧 gate / 旧命名残留
5. 补一份样例索引或治理说明文档

### 4.2 本阶段不做
- 不重写 08/09/10 合同
- 不重写 facts / business / experience 模板
- 不新增全新的业务域知识包
- 不扩写真实业务项目内容
- 不在本阶段引入新的复杂自动化能力

---

## 5. 项目分类原则

### 5.1 保留类
满足以下条件的 demo 应继续保留：
- 能代表当前主线最佳实践
- 能完整复跑 `assemble -> gate -> validate -> coverage -> archive`
- 结构、协议、runtime 与检查链一致
- 对新成员理解主线有明显帮助

### 5.2 归档类
满足以下条件的 demo 应转入 archive（归档）：
- 有历史价值，但不再适合作为当前主线样例
- 保留会增加认知噪音
- 当前内容与主线结构不一致，但仍值得保留作历史参照

### 5.3 删除候选类
满足以下条件才允许删除：
- 不再被文档、README、runbook、playbook 引用
- 已有更好的替代样例
- 不再承担迁移验证或回归验证价值
- 删除后不会让仓库失去“完整样例”或“轻量样例”

---

## 6. 对两个 demo 的建议处置

### 6.1 `demo-permission-v1`
建议：**保留并升级为黄金样例**

目标：
- 成为当前仓库默认展示的 end-to-end sample（全链路样例）
- 成为 README / 文档 / onboarding（上手引导） 默认引用对象
- 清理其旧 runtime 残留，使其完全符合新主线

### 6.2 `demo-smoke-v1`
建议：**二选一处理**
#### 方案 A：保留并升级
把它升级成真正的 smoke sample：
- 输入更轻
- 输出更小
- 跑得更快
- 专门用于主线回归验证

#### 方案 B：归档后删除
前提：
- 已经有新的 smoke sample 替代
- 或 `demo-permission-v1` 加一份 lightweight smoke scenario（轻量冒烟场景）替代其作用

当前更推荐：
**先做方案判断，不要直接删。**

---

## 7. 本阶段核心任务

### Task 1：建立 demo 治理清单
输出一份样例治理清单，至少列出：
- 项目名
- 当前角色
- 当前状态
- 是否活跃
- 处置建议
- 是否可删
- 删除前依赖

建议文件：
- `docs/governance/project-sample-governance.md`

### Task 2：收口 `demo-permission-v1`
至少完成：

1. 重新跑：
   - `python -m packages assemble demo-permission-v1`
   - `python -m packages gate-facts demo-permission-v1`
   - `python -m packages gate-business demo-permission-v1`
   - `python -m packages gate-experience demo-permission-v1`
   - `python -m packages validate demo-permission-v1`
   - `python -m packages coverage demo-permission-v1`
   - `python -m packages archive demo-permission-v1`
2. 清理旧 `01_facts / 02_business / 03_experience` 残留
3. 让 runtime、workspace、exports 与当前命名完全一致
4. 让它成为 README 默认样例

### Task 3：处理 `demo-smoke-v1`
至少完成其中一个结果：

#### 路径 A：升级为正式 smoke sample
- 重跑新主线
- 修复旧 runtime 结果
- 保证它能作为“轻量回归样例”存在
- 补 README 说明它与 `demo-permission-v1` 的区别

#### 路径 B：转归档 / 删除候选
- 先转为 archive 状态
- 删除主文档对它的活跃引用
- 明确说明其历史角色
- 若后续确认无需保留，再删除

### Task 4：清理旧残留
重点清理：
- 旧命名：
  - `01_facts.md`
  - `02_business_blueprint.md`
  - `03_experience_blueprint.md`
- 旧 gate 状态文件：
  - `01_facts_gate_status.json`
  - `03_experience_gate_status.json`
- 旧 runtime 产物中仍为 `v0.1` 的 resolved / manifest

### Task 5：补“样例索引文档”
新增一份样例索引，建议：
- `docs/samples/README.md`

至少说明：
- 哪个是黄金样例
- 哪个是 smoke 样例
- 哪个是历史归档样例
- 各自适合什么时候看

---

## 8. 推荐执行顺序

### Phase A：先分类，不先删
先完成：
- `demo-permission-v1` / `demo-smoke-v1` 的角色定义
- 是否保留 / 归档 / 删除候选 的判断

### Phase B：先把 `demo-permission-v1` 做成黄金样例
原因：
- 它已经被正式文档定义为首个迁移试点 fileciteturn59file2L1-L1
- 它已有 README 和复跑命令，最适合成为展示样例 fileciteturn59file1L1-L1

### Phase C：再决定 `demo-smoke-v1`
原因：
- 它当前协议层已迁移，但 runtime 真相未收口 fileciteturn58file0L1-L1 fileciteturn58file4L1-L1
- 需要先判断它是否值得保留为 smoke sample

### Phase D：最后处理删除
只有在：
- 样例分类完成
- 替代样例明确
- 引用已清理
之后，才允许删除候选项目。

---

## 9. 正式交付物
本阶段至少应产出：

1. `docs/governance/project-sample-governance.md`
2. 收口后的 `projects/demo-permission-v1/`
3. 对 `projects/demo-smoke-v1/` 的处置结果：
   - 升级后的活跃样例
   - 或归档说明
4. `docs/samples/README.md`

---

## 10. 通过标准

### 10.1 通过
满足以下条件可视为本阶段完成：

1. `demo-permission-v1` 成为当前主线下可复跑、可演示的黄金样例
2. `demo-smoke-v1` 的角色已明确，且不再处于“半迁移、半遗留”状态
3. 样例索引文档已补齐
4. 仓库中不再同时存在“旧样例真相”和“新样例真相”混杂引用
5. 删除动作（如果有）已经有替代依据

### 10.2 Warning
以下情况可带 warning 完成：
- `demo-smoke-v1` 先进入 archive，删除动作留到下一轮
- 个别历史 runtime 文件仍保留，但已明确不再被主流程消费

### 10.3 失败
以下任一情况视为失败：
- 直接删除 demo，但没有替代样例
- 保留 demo，但不说明角色差异
- `demo-permission-v1` 仍混有旧命名和旧运行时真相
- `demo-smoke-v1` 继续维持“协议已升级、runtime 未升级”的中间态

---

## 11. 本阶段完成后的下一步
当本阶段完成后，下一阶段再进入：

**更高层的 compile layer（编译层）/ 任务自动生成能力优化**

因为到那时：
- 协议层已收口
- 执行主线已收口
- 样例真相也已收口
- 仓库会更适合继续往“自动化生成与编译质量提升”推进

---

## 12. 一句话结论
**这一步不是删项目，而是先把 demo 项目从“混合遗留状态”治理成“有角色、有边界、有去留策略”的样例体系。**
